from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.verify_evidence import verify as verify_local, EvidenceError

ROOT = Path(__file__).resolve().parents[2]
PILOT = Path(__file__).resolve().parent
CLI = ROOT / "scripts/verify_evidence.py"


def insist(condition, message):
    if not condition:
        raise AssertionError(message)


def run(args, **kwargs):
    return subprocess.run(args, capture_output=True, text=True, check=False, timeout=35, **kwargs)


def git(repo, *args, env=None):
    p = run(["git", "-C", str(repo), *args], env=env)
    insist(p.returncode == 0, f"git {' '.join(args)}: {p.stderr}")
    return p.stdout.strip()


def check():
    baseline = json.loads((ROOT / "data/meta.json").read_text(encoding="utf8"))
    insist(baseline["version"] == "0.1.1", "baseline changed: EVIDENCE-001 needs reviewed rebase")
    checks = []
    with tempfile.TemporaryDirectory(prefix="svc-evidence001-pilot-") as tmp:
        temp = Path(tmp)
        subject = temp / "subject"
        subject.mkdir()
        git(subject, "init", "-b", "main")
        git(subject, "config", "user.name", "Synthetic Test")
        git(subject, "config", "user.email", "synthetic@example.invalid")
        git(subject, "config", "core.autocrlf", "false")

        answers = json.loads((ROOT / "pilots/PILOT-001/fixtures/ready.json").read_text(encoding="utf8"))
        del answers["scenario_id"]
        assessment = subject / "assessment"
        assessment.mkdir()
        answer_data = json.dumps(answers, ensure_ascii=False, indent=2).encode("utf8") + b"\n"
        (assessment / "answers.json").write_bytes(answer_data)
        evidence = subject / "evidence"
        evidence.mkdir()
        bindings = []
        for control_id in sorted(answers["answers"]):
            relative = f"evidence/{control_id}.txt"
            raw = f"SYNTHETIC TEST TOKEN {control_id}; this cannot prove control effectiveness.\n".encode("utf8")
            (subject / relative).write_bytes(raw)
            bindings.append({"control_id": control_id, "artifacts": [{"path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "kind": "test_report"}]})
        (evidence / "link.txt").symlink_to("O01.txt")
        git(subject, "add", "-A")
        env = dict(os.environ, GIT_AUTHOR_DATE="2026-09-23T00:00:00+0000", GIT_COMMITTER_DATE="2026-09-23T00:00:00+0000")
        git(subject, "commit", "-m", "synthetic EVIDENCE-001 fixture", env=env)
        commit = git(subject, "rev-parse", "HEAD")
        manifest = {
            "schema_version": 1, "assessment_id": "SVC", "assessment_version": "0.1.1",
            "subject": {"repository_hint": "synthetic-local-only; not authenticated", "commit": commit,
                        "answers": {"path": "assessment/answers.json", "sha256": hashlib.sha256(answer_data).hexdigest()}},
            "bindings": bindings,
        }
        manifest_path = temp / "manifest.json"

        def verify(data, repo=subject, via_cli=False):
            manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
            if via_cli:
                return run([sys.executable, str(CLI), "--repo", str(repo), "--manifest", str(manifest_path)])
            try:
                result = verify_local(repo, manifest_path)
                return SimpleNamespace(returncode=0, stdout=json.dumps(result), stderr="")
            except EvidenceError as exc:
                return SimpleNamespace(returncode=1, stdout="", stderr="EVIDENCE-001 FAIL: " + str(exc))

        p = verify(manifest, via_cli=True)
        insist(p.returncode == 0, f"valid manifest: {p.stderr}")
        report = json.loads(p.stdout)
        insist(report["artifact_binding"] == "PASS" and report["artifact_count"] == 32, "valid binding unexpected")
        insist(report["structural_gates"] == {"en": "READY", "lv": "READY"}, "EN/LV structural mismatch")
        insist(report["release_authorized"] is False and report["evidence_claims_independently_verified"] is False and report["remote_repository_identity_authenticated"] is False, "unsafe assurance claims")
        checks.append("32 synthetic artifacts bound to exact local commit with EN/LV structural parity; no release or authenticity claim")

        invalid = [
            ("tampered_sha", lambda m: m["bindings"][0]["artifacts"][0].update(sha256="0" * 64), "SHA-256 mismatch"),
            ("wrong_commit", lambda m: m["subject"].update(commit="a" * 40), "git validation failed"),
            ("missing_binding", lambda m: m["bindings"].pop(), "control binding coverage mismatch"),
            ("duplicate_binding", lambda m: m["bindings"].__setitem__(1, copy.deepcopy(m["bindings"][0])), "duplicate control binding"),
            ("path_traversal", lambda m: m["bindings"][0]["artifacts"][0].update(path="../secrets.env"), "unsafe artifact path"),
            ("symlink", lambda m: m["bindings"][0]["artifacts"][0].update(path="evidence/link.txt"), "symlink, gitlink or nonregular"),
            ("answers_sha", lambda m: m["subject"]["answers"].update(sha256="0" * 64), "SHA-256 mismatch"),
            ("unknown_control", lambda m: m["bindings"][0].update(control_id="Z99"), "unknown bound control ID"),
            ("unsupported_field", lambda m: m.update(reviewer_approved=True), "manifest field mismatch"),
            ("unsupported_kind", lambda m: m["bindings"][0]["artifacts"][0].update(kind="trust_me"), "unsupported artifact kind"),
            ("path_reuse", lambda m: m["bindings"][1]["artifacts"][0].update(path=m["bindings"][0]["artifacts"][0]["path"]), "artifact path reused"),
        ]
        for name, change, reason in invalid:
            m = copy.deepcopy(manifest)
            change(m)
            p = verify(m)
            insist(p.returncode == 1 and reason in p.stderr, f"{name} unexpectedly accepted or wrong error: {p.stderr}")
            checks.append("fail-closed: " + name)

        # Duplicate JSON keys in manifest itself: the verifier must fail even if legacy assess.py does not.
        normal = json.dumps(manifest, ensure_ascii=False)
        manifest_path.write_text(normal.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1', 1), encoding="utf8")
        p = run([sys.executable, str(CLI), "--repo", str(subject), "--manifest", str(manifest_path)])
        insist(p.returncode == 1 and "duplicate JSON key rejected" in p.stderr, "duplicate manifest key accepted")
        checks.append("fail-closed: duplicate_manifest_key")

        # Duplicate JSON keys within pinned answer data must also be rejected (without changing legacy assess.py yet).
        patched = answer_data.decode("utf8").replace('"O01": {', '"O01": "UNKNOWN",\n    "O01": {', 1)
        (assessment / "answers.json").write_text(patched, encoding="utf8")
        git(subject, "add", "assessment/answers.json")
        git(subject, "commit", "-m", "synthetic duplicate-key answer fixture", env=env)
        dupe_manifest = copy.deepcopy(manifest)
        dupe_manifest["subject"]["commit"] = git(subject, "rev-parse", "HEAD")
        dupe_manifest["subject"]["answers"]["sha256"] = hashlib.sha256(patched.encode("utf8")).hexdigest()
        p = verify(dupe_manifest)
        insist(p.returncode == 1 and "duplicate JSON key rejected" in p.stderr, f"duplicate answer key accepted: {p.stderr}")
        checks.append("fail-closed: duplicate_pinned_answer_key")

        # Uncommitted changes cannot silently substitute evidence from the pinned Git commit.
        (subject / "evidence/O01.txt").write_text("uncommitted, unverified modification", encoding="utf8")
        p = verify(dupe_manifest)
        insist(p.returncode == 1 and "duplicate JSON key rejected" in p.stderr, "dupe answer mode unexpectedly changed")
        p = verify(manifest)
        insist(p.returncode == 0, f"old pinned commit should remain verifiable: {p.stderr}")
        report = json.loads(p.stdout)
        insist(report["target_commit_equals_local_head"] is False and report["working_tree_dirty"] is True and len(report["warnings"]) == 2, "dirty worktree/head drift not disclosed")
        checks.append("pinned historical commit unaffected by dirty working tree; both warnings present")

    return {
        "protocol": "EVIDENCE-001",
        "scope": "local Git commit/blob hash binding only; all artifacts are synthetic; no authenticity, identity, security or release claims",
        "result": "PASS",
        "baseline_version": baseline["version"],
        "bound_controls_in_positive_case": 32,
        "negative_cases_rejected": len([x for x in checks if x.startswith("fail-closed")]),
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        report = check()
        rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        path = PILOT / "reports/synthetic-results.json"
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf8")
        else:
            insist(path.read_text(encoding="utf8") == rendered, "stale EVIDENCE-001 report")
    except (AssertionError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"EVIDENCE-001 PILOT FAIL: {exc}", file=sys.stderr)
        return 1
    print("EVIDENCE-001 PASS: 32 synthetic Git blobs, both languages, 13 fail-closed negative cases and dirty-worktree disclosure. No claim of true evidence or release approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
