from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_MANIFEST = 512 * 1024
MAX_ANSWERS = 1024 * 1024
MAX_ARTIFACT = 16 * 1024 * 1024
MAX_ARTIFACTS = 128
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX_COMMIT = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
KINDS = {"test_report", "review_record", "configuration", "design_record", "scan_report", "build_manifest", "other"}


class EvidenceError(Exception):
    pass


def must(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError(f"duplicate JSON key rejected: {key}")
        result[key] = value
    return result


def forbid_nonstandard_constant(value):
    raise EvidenceError(f"nonstandard JSON constant rejected: {value}")


def decode_json(data: bytes, name: str):
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique_pairs, parse_constant=forbid_nonstandard_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"invalid UTF-8/JSON in {name}: {exc}") from exc


def exact_keys(value, required, description):
    must(isinstance(value, dict), f"{description} must be an object")
    must(set(value) == set(required), f"{description} field mismatch: expected {sorted(required)}, got {sorted(value)}")


def safe_git_path(value: str) -> str:
    must(isinstance(value, str) and bool(value), "artifact path must be nonempty string")
    must(not value.startswith("/") and "\\" not in value, f"unsafe artifact path: {value!r}")
    must(not any(ord(c) < 32 or ord(c) == 127 for c in value), "artifact path contains control character")
    parts = value.split("/")
    must(all(p and p not in (".", "..") for p in parts), f"unsafe artifact path: {value!r}")
    must(len(value.encode("utf-8")) <= 512, "artifact path is too long")
    return value


def hex_sha256(value, description):
    must(isinstance(value, str) and bool(HEX64.fullmatch(value)), f"invalid SHA-256: {description}")


def git(repo: Path, *args: str, binary: bool = False):
    cmd = ["git", "-C", str(repo), *args]
    proc = subprocess.run(cmd, capture_output=True, timeout=20, check=False)
    if proc.returncode:
        raise EvidenceError(f"git validation failed ({' '.join(args[:3])}): {proc.stderr.decode('utf-8', errors='replace').strip()[:280]}")
    return proc.stdout if binary else proc.stdout.decode("utf-8").strip()


def git_file_index(repo: Path, commit: str):
    must(bool(HEX_COMMIT.fullmatch(commit)), "subject.commit must be a full lowercase Git commit SHA")
    resolved = git(repo, "rev-parse", "--verify", commit + "^{commit}")
    must(resolved == commit, "subject commit does not resolve to exact specified commit")
    entries = {}
    for entry in git(repo, "ls-tree", "-rz", "--full-tree", commit, binary=True).split(b"\x00"):
        if not entry:
            continue
        try:
            head, raw_path = entry.split(b"\t", 1)
            mode, kind, blob_id = head.decode("ascii").split(" ")
            path = raw_path.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise EvidenceError("invalid UTF-8 Git tree entry") from exc
        entries[path] = (mode, kind, blob_id)
    return entries


def pinned_blob(repo: Path, entries: dict, path: str, expected: str, max_bytes: int) -> bytes:
    safe_git_path(path)
    hex_sha256(expected, path)
    must(path in entries, f"artifact not tracked at pinned commit: {path}")
    mode, kind, blob_id = entries[path]
    must((mode, kind) in (("100644", "blob"), ("100755", "blob")), f"symlink, gitlink or nonregular artifact rejected: {path}")
    size = int(git(repo, "cat-file", "-s", blob_id))
    must(0 < size <= max_bytes, f"artifact is empty or exceeds size cap: {path}")
    raw = git(repo, "cat-file", "blob", blob_id, binary=True)
    digest = hashlib.sha256(raw).hexdigest()
    must(digest == expected, f"SHA-256 mismatch for {path}: actual {digest}")
    return raw


def verify_artifact_batch(repo: Path, entries: dict, references: list) -> None:
    if not references:
        return
    identifiers = []
    for path, expected in references:
        must(path in entries, f"artifact not tracked at pinned commit: {path}")
        mode, kind, blob_id = entries[path]
        must((mode, kind) in (("100644", "blob"), ("100755", "blob")), f"symlink, gitlink or nonregular artifact rejected: {path}")
        identifiers.append(blob_id)
    stdin = ("\n".join(identifiers) + "\n").encode("ascii")
    sizes = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch-check"],
                           input=stdin, capture_output=True, timeout=25, check=False)
    must(sizes.returncode == 0, "Git batch size query failed")
    parsed = sizes.stdout.decode("ascii").splitlines()
    must(len(parsed) == len(references), "Git batch size reply count mismatch")
    total = 0
    for (path, _), blob_id, line in zip(references, identifiers, parsed):
        parts = line.split()
        must(len(parts) == 3 and parts[0] == blob_id and parts[1] == "blob", "unexpected Git blob size reply")
        size = int(parts[2])
        must(0 < size <= MAX_ARTIFACT, f"artifact is empty or exceeds size cap: {path}")
        total += size
    must(total <= 64 * 1024 * 1024, "total artifact bytes exceed 64 MiB")
    batch = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"],
                           input=stdin, capture_output=True, timeout=35, check=False)
    must(batch.returncode == 0, "Git batch blob read failed")
    output = batch.stdout
    pos = 0
    for (path, expected), blob_id, line in zip(references, identifiers, parsed):
        end = output.find(b"\n", pos)
        must(end >= 0, "truncated Git batch header")
        header = output[pos:end].decode("ascii")
        must(header == line, "Git batch header mismatch")
        size = int(line.split()[2])
        start = end + 1
        raw = output[start:start + size]
        must(len(raw) == size and output[start + size:start + size + 1] == b"\n", "truncated Git blob")
        digest = hashlib.sha256(raw).hexdigest()
        must(digest == expected, f"SHA-256 mismatch for {path}: actual {digest}")
        pos = start + size + 1
    must(pos == len(output), "unexpected trailing Git batch bytes")


def evaluate_answers(data: bytes):
    with tempfile.TemporaryDirectory(prefix="svc-evidence001-") as tmp:
        fp = Path(tmp) / "answers.json"
        fp.write_bytes(data)
        outputs = {}
        for lang in ("en", "lv"):
            process = subprocess.run(
                [sys.executable, str(ROOT / "scripts/assess.py"), str(fp), "--lang", lang],
                capture_output=True, text=True, timeout=15, check=False,
            )
            must(process.returncode == 0, f"baseline assessment rejected pinned answers for {lang}: {(process.stderr + process.stdout).strip()[:220]}")
            outputs[lang] = json.loads(process.stdout)
        en, lv = outputs["en"], outputs["lv"]
        must(en["gate"] == lv["gate"], "EN/LV gate mismatch")
        for field in ("all_gaps", "blocking_gaps"):
            must([x["id"] for x in en[field]] == [x["id"] for x in lv[field]], f"EN/LV {field} ID mismatch")
        return outputs


def verify(repo: Path, manifest_path: Path):
    must(manifest_path.is_file() and manifest_path.stat().st_size <= MAX_MANIFEST, "manifest missing or exceeds size cap")
    manifest_bytes = manifest_path.read_bytes()
    manifest = decode_json(manifest_bytes, "manifest")
    exact_keys(manifest, ("schema_version", "assessment_id", "assessment_version", "subject", "bindings"), "manifest")
    must(manifest["schema_version"] == 1 and type(manifest["schema_version"]) is int, "unsupported manifest schema version")
    meta = decode_json((ROOT / "data/meta.json").read_bytes(), "baseline meta")
    must(manifest["assessment_id"] == meta["assessment_id"], "manifest assessment_id mismatch")
    must(manifest["assessment_version"] == meta["version"], "manifest assessment_version mismatch")
    subject = manifest["subject"]
    exact_keys(subject, ("repository_hint", "commit", "answers"), "subject")
    must(isinstance(subject["repository_hint"], str) and 1 <= len(subject["repository_hint"]) <= 200, "repository_hint must be a nonempty label")
    answers_ref = subject["answers"]
    exact_keys(answers_ref, ("path", "sha256"), "subject.answers")
    commit = subject["commit"]
    must(isinstance(commit, str), "subject.commit must be a string")
    repo = repo.expanduser().resolve(strict=True)
    must(Path(git(repo, "rev-parse", "--show-toplevel")).resolve() == repo, "--repo must be the Git worktree root")
    entries = git_file_index(repo, commit)
    answers_bytes = pinned_blob(repo, entries, answers_ref["path"], answers_ref["sha256"], MAX_ANSWERS)
    answers = decode_json(answers_bytes, "pinned answers")
    exact_keys(answers, ("assessment_id", "version", "answers"), "pinned answers")
    must(answers["assessment_id"] == meta["assessment_id"] and answers["version"] == meta["version"], "pinned answer identity/version mismatch")
    must(isinstance(answers["answers"], dict), "pinned answers must contain an object")
    item_ids = {x["id"] for x in decode_json((ROOT / "data/assessment.en.json").read_bytes(), "baseline controls")["items"]}
    must(set(answers["answers"]) == item_ids, "evidence mode requires all 32 control answers explicitly present")
    expected_bindings = set()
    for control_id, raw in answers["answers"].items():
        state = raw.get("state", "UNKNOWN") if isinstance(raw, dict) else raw
        if state in ("VERIFIED", "IMPLEMENTED"):
            expected_bindings.add(control_id)
    supplied = manifest["bindings"]
    must(isinstance(supplied, list) and len(supplied) <= len(item_ids), "bindings must be bounded array")
    bound, used_paths, artifacts, pending = set(), set(), [], []
    for row in supplied:
        exact_keys(row, ("control_id", "artifacts"), "control binding")
        control_id = row["control_id"]
        must(isinstance(control_id, str) and control_id in item_ids, "unknown bound control ID")
        must(control_id not in bound, f"duplicate control binding: {control_id}")
        bound.add(control_id)
        refs = row["artifacts"]
        must(isinstance(refs, list) and 1 <= len(refs) <= 8, f"invalid artifact count for {control_id}")
        for ref in refs:
            exact_keys(ref, ("path", "sha256", "kind"), "artifact reference")
            path = safe_git_path(ref["path"])
            must(path not in used_paths, f"artifact path reused across controls: {path}")
            must(path != answers_ref["path"], "assessment answers cannot serve as control evidence")
            must(isinstance(ref["kind"], str) and ref["kind"] in KINDS, f"unsupported artifact kind for {path}")
            used_paths.add(path)
            hex_sha256(ref["sha256"], path)
            pending.append((path, ref["sha256"]))
            artifacts.append({"control_id": control_id, "path": path, "kind": ref["kind"], "sha256": ref["sha256"]})
            must(len(artifacts) <= MAX_ARTIFACTS, "artifact count exceeds cap")
    must(bound == expected_bindings, f"control binding coverage mismatch; missing {sorted(expected_bindings - bound)}, extra {sorted(bound - expected_bindings)}")
    verify_artifact_batch(repo, entries, pending)
    outputs = evaluate_answers(answers_bytes)
    head = git(repo, "rev-parse", "HEAD")
    dirty = bool(git(repo, "status", "--porcelain", "--untracked-files=no"))
    na_controls = [x["id"] for x in outputs["en"]["not_applicable_items"]]
    warnings = []
    if head != commit:
        warnings.append("Local HEAD differs from target commit; only the pinned commit was inspected.")
    if dirty:
        warnings.append("Working tree has uncommitted changes; they were ignored. Only pinned Git blobs were inspected.")
    if na_controls:
        warnings.append("NOT_APPLICABLE rationales were not verified for factual truth.")
    return {
        "protocol": "EVIDENCE-001", "schema_version": 1,
        "artifact_binding": "PASS", "structural_gates": {lang: outputs[lang]["gate"] for lang in ("en", "lv")},
        "subject": {"repository_hint": subject["repository_hint"], "commit": commit, "answers_path": answers_ref["path"], "answers_sha256": answers_ref["sha256"]},
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "bound_control_ids": sorted(bound), "artifact_count": len(artifacts), "artifacts": artifacts,
        "not_applicable_ids_unreviewed": na_controls,
        "target_commit_equals_local_head": head == commit, "working_tree_dirty": dirty,
        "source": "tracked Git blobs at the exact pinned local commit, not working-tree files",
        "remote_repository_identity_authenticated": False,
        "evidence_claims_independently_verified": False,
        "release_authorized": False,
        "interpretation": "Hash and local Git-commit binding only. No evidence truth, reviewer identity, remote provenance, software security or deployment authorization is established.",
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Offline manifest and local Git object hash binding. NOT independent evidence verification.")
    parser.add_argument("--repo", type=Path, required=True, help="Local Git worktree root of the subject product")
    parser.add_argument("--manifest", type=Path, required=True, help="External JSON manifest; not required to be committed to subject repo")
    args = parser.parse_args()
    try:
        result = verify(args.repo, args.manifest)
    except (EvidenceError, FileNotFoundError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"EVIDENCE-001 FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
