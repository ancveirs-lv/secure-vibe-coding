from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT = Path(__file__).resolve().parent
VERIFY_EVIDENCE = ROOT / "scripts/verify_evidence.py"
VERIFY_REVIEW = ROOT / "scripts/verify_verification.py"
NAMESPACE = "secure-vibe-coding-verification-v1"


def insist(condition, message):
    if not condition:
        raise AssertionError(message)


def run(args, **kwargs):
    return subprocess.run(args, capture_output=True, text=True, check=False, timeout=40, **kwargs)


def git(repo, *args, env=None):
    p = run(["git", "-C", str(repo), *args], env=env)
    insist(p.returncode == 0, f"git {' '.join(args)}: {p.stderr}")
    return p.stdout.strip()


def sign_record(record: Path, key: Path):
    sig = Path(str(record) + ".sig")
    if sig.exists():
        sig.unlink()
    p = run(["ssh-keygen", "-Y", "sign", "-f", str(key), "-n", NAMESPACE, str(record)])
    insist(p.returncode == 0 and sig.is_file(), f"signing failed: {p.stderr}")
    return sig


def write_record(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def verify_cli(record_path, evidence_report, signature, allowed):
    return run([
        sys.executable, str(VERIFY_REVIEW),
        "--record", str(record_path),
        "--evidence-report", str(evidence_report),
        "--signature", str(signature),
        "--allowed-signers", str(allowed),
    ])


def check():
    insist(shutil.which("ssh-keygen") is not None, "ssh-keygen unavailable")
    checks = []
    with tempfile.TemporaryDirectory(prefix="svc-verification001-") as tmp:
        temp = Path(tmp)
        subject = temp / "subject"
        subject.mkdir()
        git(subject, "init", "-b", "main")
        git(subject, "config", "user.name", "Synthetic Test")
        git(subject, "config", "user.email", "synthetic@example.invalid")
        git(subject, "config", "core.autocrlf", "false")

        ready = json.loads((ROOT / "pilots/PILOT-001/fixtures/ready.json").read_text(encoding="utf-8"))
        ready.pop("scenario_id", None)
        assessment = subject / "assessment"
        evidence_dir = subject / "evidence"
        assessment.mkdir()
        evidence_dir.mkdir()
        answers_raw = json.dumps(ready, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
        (assessment / "answers.json").write_bytes(answers_raw)

        bindings = []
        for control_id in sorted(ready["answers"]):
            rel = f"evidence/{control_id}.txt"
            raw = f"SYNTHETIC VERIFICATION-001 EVIDENCE {control_id}; not real security evidence.\n".encode("utf-8")
            (subject / rel).write_bytes(raw)
            bindings.append({
                "control_id": control_id,
                "artifacts": [{"path": rel, "sha256": hashlib.sha256(raw).hexdigest(), "kind": "review_record"}],
            })

        git(subject, "add", "-A")
        env = dict(os.environ, GIT_AUTHOR_DATE="2026-09-24T08:00:00+0000", GIT_COMMITTER_DATE="2026-09-24T08:00:00+0000")
        git(subject, "commit", "-m", "synthetic VERIFICATION-001 subject", env=env)
        commit = git(subject, "rev-parse", "HEAD")

        manifest = {
            "schema_version": 1,
            "assessment_id": "SVC",
            "assessment_version": "0.1.1",
            "subject": {
                "repository_hint": "synthetic-verification001-subject",
                "commit": commit,
                "answers": {"path": "assessment/answers.json", "sha256": hashlib.sha256(answers_raw).hexdigest()},
            },
            "bindings": bindings,
        }
        manifest_path = temp / "evidence-manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        evidence_run = run([sys.executable, str(VERIFY_EVIDENCE), "--repo", str(subject), "--manifest", str(manifest_path)])
        insist(evidence_run.returncode == 0, f"EVIDENCE-001 integration failed: {evidence_run.stderr}")
        evidence_report = temp / "evidence-report.json"
        evidence_report.write_text(evidence_run.stdout, encoding="utf-8")
        evidence = json.loads(evidence_run.stdout)
        insist(evidence["artifact_binding"] == "PASS" and evidence["release_authorized"] is False, "unsafe evidence report")

        key = temp / "reviewer_key"
        keygen = run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "synthetic-reviewer", "-f", str(key)])
        insist(keygen.returncode == 0, f"key generation failed: {keygen.stderr}")
        pub = key.with_suffix(".pub").read_text(encoding="utf-8").strip().split()
        insist(len(pub) >= 2, "invalid generated public key")
        identity = "synthetic-reviewer@example.invalid"
        allowed = temp / "allowed_signers"
        allowed.write_text(f"{identity} {pub[0]} {pub[1]}\n", encoding="utf-8")

        controls = sorted(ready["answers"])
        record = {
            "schema_version": 1,
            "assessment_id": "SVC",
            "assessment_version": "0.1.1",
            "subject": {
                "repository_hint": "synthetic-verification001-subject",
                "commit": commit,
                "evidence_manifest_sha256": evidence["manifest_sha256"],
            },
            "verification": {
                "claimed_assurance_class": "INDEPENDENTLY_VERIFIED",
                "performed_at": "2026-09-24T08:15:00Z",
                "method": "HYBRID_REVIEW",
                "result": "PASS",
                "control_ids": controls,
                "statement": "SYNTHETIC signed external-review claim for protocol testing only; not a real independent security assessment.",
            },
            "verifier": {
                "identity": identity,
                "display_name": "Synthetic External Reviewer",
                "role": "security reviewer",
                "organization": "Example External Lab",
                "relationship": "EXTERNAL",
            },
        }
        record_path = temp / "verification-record.json"
        write_record(record_path, record)
        signature = sign_record(record_path, key)

        positive = verify_cli(record_path, evidence_report, signature, allowed)
        insist(positive.returncode == 0, f"valid signed record rejected: {positive.stderr}")
        report = json.loads(positive.stdout)
        insist(report["record_signature"] == "PASS", "signature not reported PASS")
        insist(report["claimed_assurance_class"] == "INDEPENDENTLY_VERIFIED", "assurance class drift")
        insist(report["signed_external_independence_claim"] is True, "external signed claim missing")
        insist(report["real_world_identity_verified_by_tool"] is False, "unsafe identity claim")
        insist(report["organizational_independence_verified_by_tool"] is False, "unsafe independence claim")
        insist(report["evidence_truth_verified_by_tool"] is False, "unsafe evidence truth claim")
        insist(report["product_security_established"] is False and report["release_authorized"] is False, "unsafe security/release claim")
        checks.append("signed external review claim bound to exact EVIDENCE-001 commit/manifest; no real-world independence or security escalation")

        write_record(record_path, record)
        signature = sign_record(record_path, key)
        raw = record_path.read_text(encoding="utf-8")
        record_path.write_text(raw.replace("HYBRID_REVIEW", "MANUAL_REVIEW", 1), encoding="utf-8")
        p = verify_cli(record_path, evidence_report, signature, allowed)
        insist(p.returncode != 0 and "detached SSH signature verification failed" in p.stderr, "tampered signed bytes accepted")
        checks.append("fail-closed: tampered_signed_record")

        def semantic_negative(name, mutate, expected):
            data = copy.deepcopy(record)
            mutate(data)
            write_record(record_path, data)
            sig = sign_record(record_path, key)
            p = verify_cli(record_path, evidence_report, sig, allowed)
            insist(p.returncode != 0 and expected in (p.stderr + p.stdout), f"{name} unexpectedly accepted: {p.stdout} {p.stderr}")
            checks.append("fail-closed: " + name)

        semantic_negative("wrong_manifest_hash", lambda r: r["subject"].update(evidence_manifest_sha256="0" * 64), "evidence manifest SHA-256 mismatch")
        semantic_negative("repository_hint_mismatch", lambda r: r["subject"].update(repository_hint="different-synthetic-label"), "repository_hint mismatch with evidence report")
        semantic_negative("wrong_commit", lambda r: r["subject"].update(commit="a" * 40), "subject commit mismatch")
        semantic_negative("internal_independent_claim", lambda r: r["verifier"].update(relationship="INTERNAL"), "INDEPENDENTLY_VERIFIED requires EXTERNAL")
        semantic_negative("duplicate_control", lambda r: r["verification"]["control_ids"].__setitem__(-1, r["verification"]["control_ids"][0]), "duplicate control ID")
        semantic_negative("unknown_control", lambda r: r["verification"].update(control_ids=["Z99"]), "controls without evidence bindings")
        semantic_negative("future_timestamp", lambda r: r["verification"].update(performed_at="2999-01-01T00:00:00Z"), "performed_at cannot be in the future")
        semantic_negative("unsupported_field", lambda r: r.update(certified=True), "verification record field mismatch")

        def bad_tool(r):
            r["verification"].update(claimed_assurance_class="TOOL_VERIFIED", method="AUTOMATED_TOOL")
            r["verifier"].update(relationship="EXTERNAL")
        semantic_negative("tool_class_wrong_relationship", bad_tool, "TOOL_VERIFIED requires TOOL")

        write_record(record_path, record)
        wrong_allowed = temp / "wrong_allowed_signers"
        wrong_allowed.write_text(f"other@example.invalid {pub[0]} {pub[1]}\n", encoding="utf-8")
        signature = sign_record(record_path, key)
        p = verify_cli(record_path, evidence_report, signature, wrong_allowed)
        insist(p.returncode != 0 and "detached SSH signature verification failed" in p.stderr, "wrong trust-store identity accepted")
        checks.append("fail-closed: wrong_allowed_signer_identity")

        duplicate = json.dumps(record, ensure_ascii=False, sort_keys=True).replace(
            '"schema_version": 1', '"schema_version": 1, "schema_version": 1', 1
        )
        record_path.write_text(duplicate, encoding="utf-8")
        signature = sign_record(record_path, key)
        p = verify_cli(record_path, evidence_report, signature, allowed)
        insist(p.returncode != 0 and "duplicate JSON key rejected" in p.stderr, "duplicate record key accepted")
        checks.append("fail-closed: duplicate_record_key")

    negatives = [x for x in checks if x.startswith("fail-closed")]
    return {
        "protocol": "VERIFICATION-001",
        "result": "PASS",
        "scope": "signed verification-record provenance bound to EVIDENCE-001 output; synthetic only",
        "positive_case": "signed external INDEPENDENTLY_VERIFIED claim is cryptographically attributed to operator trust-store identity without claiming real-world independence",
        "negative_cases_rejected": len(negatives),
        "checks": checks,
        "assurance_boundary": {
            "identity_bound_to_allowed_signers": True,
            "real_world_identity_verified_by_tool": False,
            "organizational_independence_verified_by_tool": False,
            "evidence_truth_verified_by_tool": False,
            "product_security_established": False,
            "release_authorized": False,
        },
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
            path.write_text(rendered, encoding="utf-8")
        else:
            insist(path.is_file() and path.read_text(encoding="utf-8") == rendered, "stale VERIFICATION-001 report")
    except (AssertionError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"VERIFICATION-001 PILOT FAIL: {exc}", file=sys.stderr)
        return 1
    print("VERIFICATION-001 PASS: signed review provenance bound to EVIDENCE-001; fail-closed trust-store/signature checks; no real-world independence or security claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
