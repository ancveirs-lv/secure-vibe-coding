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

ROOT = Path(__file__).resolve().parents[2]
PILOT = Path(__file__).resolve().parent
ASSESS = ROOT / "scripts/assess.py"
VERIFY_EVIDENCE = ROOT / "scripts/verify_evidence.py"
VERIFY_VERIFICATION = ROOT / "scripts/verify_verification.py"
NAMESPACE = "secure-vibe-coding-verification-v1"


def insist(condition, message):
    if not condition:
        raise AssertionError(message)


def run(args, **kwargs):
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=80,
        check=False,
        **kwargs,
    )


def git(repo, *args, env=None):
    proc = run(["git", "-C", str(repo), *args], env=env)
    insist(proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}")
    return proc.stdout.strip()


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256_bytes(raw: bytes):
    return hashlib.sha256(raw).hexdigest()


def assessment_run(path: Path, lang: str, require_ready: bool = False):
    args = [sys.executable, str(ASSESS), str(path), "--lang", lang]
    if require_ready:
        args.append("--require-ready")
    return run(args)


def evidence_run(repo: Path, manifest: Path):
    return run(
        [
            sys.executable,
            str(VERIFY_EVIDENCE),
            "--repo",
            str(repo),
            "--manifest",
            str(manifest),
        ]
    )


def sign_record(record: Path, key: Path):
    sig = Path(str(record) + ".sig")
    if sig.exists():
        sig.unlink()
    proc = run(
        [
            "ssh-keygen",
            "-Y",
            "sign",
            "-f",
            str(key),
            "-n",
            NAMESPACE,
            str(record),
        ]
    )
    insist(proc.returncode == 0 and sig.is_file(), f"record signing failed: {proc.stderr}")
    return sig


def verification_run(record: Path, evidence_report: Path, signature: Path, allowed: Path):
    return run(
        [
            sys.executable,
            str(VERIFY_VERIFICATION),
            "--record",
            str(record),
            "--evidence-report",
            str(evidence_report),
            "--signature",
            str(signature),
            "--allowed-signers",
            str(allowed),
        ]
    )


def build_subject(temp: Path):
    assessment = json.loads((ROOT / "data/assessment.en.json").read_text(encoding="utf-8"))
    control_ids = sorted(item["id"] for item in assessment["items"])
    subject = temp / "subject"
    subject.mkdir()
    git(subject, "init", "-q")
    git(subject, "config", "user.name", "Synthetic PILOT-002")
    git(subject, "config", "user.email", "pilot002@example.invalid")

    answers = {
        "assessment_id": "SVC",
        "version": "0.1.1",
        "answers": {},
    }
    bindings = []
    for control_id in control_ids:
        artifact_rel = f"evidence/{control_id}.txt"
        artifact_raw = f"PILOT-002 synthetic evidence artifact for {control_id}\n".encode("utf-8")
        artifact_path = subject / artifact_rel
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_bytes(artifact_raw)
        answers["answers"][control_id] = {
            "state": "VERIFIED",
            "evidence": f"synthetic committed artifact: {artifact_rel}",
        }
        bindings.append(
            {
                "control_id": control_id,
                "artifacts": [
                    {
                        "path": artifact_rel,
                        "sha256": sha256_bytes(artifact_raw),
                        "kind": "test_report",
                    }
                ],
            }
        )

    answers_path = subject / "assessment/answers.json"
    write_json(answers_path, answers)
    answers_raw = answers_path.read_bytes()

    git(subject, "add", ".")
    env = os.environ.copy()
    env.update(
        GIT_AUTHOR_DATE="2026-09-25T12:00:00+0000",
        GIT_COMMITTER_DATE="2026-09-25T12:00:00+0000",
    )
    git(subject, "commit", "-q", "-m", "synthetic PILOT-002 subject", env=env)
    commit = git(subject, "rev-parse", "HEAD")
    insist(not git(subject, "status", "--porcelain"), "synthetic subject must be clean")

    manifest = {
        "schema_version": 1,
        "assessment_id": "SVC",
        "assessment_version": "0.1.1",
        "subject": {
            "repository_hint": "synthetic-pilot002-subject",
            "commit": commit,
            "answers": {
                "path": "assessment/answers.json",
                "sha256": sha256_bytes(answers_raw),
            },
        },
        "bindings": bindings,
    }
    return subject, answers, answers_path, manifest, control_ids


def check():
    checks = []
    negatives = []

    with tempfile.TemporaryDirectory(prefix="svc-pilot002-") as tmp:
        temp = Path(tmp)
        subject, answers, answers_path, manifest, control_ids = build_subject(temp)

        assessment_outputs = {}
        for lang in ("en", "lv"):
            proc = assessment_run(answers_path, lang)
            insist(proc.returncode == 0, f"assessment {lang} failed: {proc.stderr}")
            result = json.loads(proc.stdout)
            insist(result["gate"] == "READY", f"assessment {lang} gate drift: {result['gate']}")
            insist(not result["all_gaps"], f"assessment {lang} unexpectedly has gaps")
            assessment_outputs[lang] = result
        checks.append("assessment: same committed input is READY in EN and LV")

        degraded = copy.deepcopy(answers)
        degraded["answers"][control_ids[0]]["state"] = "UNKNOWN"
        degraded_path = temp / "degraded-answers.json"
        write_json(degraded_path, degraded)
        degraded_run = assessment_run(degraded_path, "en", require_ready=True)
        insist(degraded_run.returncode == 2, "degraded assessment did not fail --require-ready")
        degraded_report = json.loads(degraded_run.stdout)
        insist(degraded_report["gate"] != "READY", "degraded assessment remained READY")
        negatives.append("assessment_not_ready_rejected")

        manifest_path = temp / "evidence-manifest.json"
        write_json(manifest_path, manifest)
        ev_proc = evidence_run(subject, manifest_path)
        insist(ev_proc.returncode == 0, f"EVIDENCE-001 failed: {ev_proc.stderr}")
        evidence_report = json.loads(ev_proc.stdout)
        insist(evidence_report["protocol"] == "EVIDENCE-001", "evidence protocol drift")
        insist(evidence_report["artifact_binding"] == "PASS", "artifact binding not PASS")
        insist(evidence_report["structural_gates"] == {"en": "READY", "lv": "READY"}, "evidence structural gates drift")
        insist(evidence_report["artifact_count"] == 32, "expected 32 evidence artifacts")
        insist(len(evidence_report["bound_control_ids"]) == 32, "expected 32 bound controls")
        insist(evidence_report["subject"]["commit"] == manifest["subject"]["commit"], "evidence subject commit drift")
        insist(evidence_report["release_authorized"] is False, "EVIDENCE-001 must not authorize release")
        insist(evidence_report["evidence_claims_independently_verified"] is False, "EVIDENCE-001 assurance escalated")
        checks.append("evidence: all 32 controls bound to exact Git blobs at the same subject commit")

        evidence_report_path = temp / "evidence-report.json"
        evidence_report_path.write_text(ev_proc.stdout, encoding="utf-8")

        bad_answers_manifest = copy.deepcopy(manifest)
        bad_answers_manifest["subject"]["answers"]["sha256"] = "0" * 64
        bad_answers_manifest_path = temp / "bad-answers-manifest.json"
        write_json(bad_answers_manifest_path, bad_answers_manifest)
        proc = evidence_run(subject, bad_answers_manifest_path)
        insist(proc.returncode != 0 and "SHA-256 mismatch for assessment/answers.json" in proc.stderr, "answers hash substitution accepted")
        negatives.append("answers_hash_substitution_rejected")

        bad_artifact_manifest = copy.deepcopy(manifest)
        bad_artifact_manifest["bindings"][0]["artifacts"][0]["sha256"] = "0" * 64
        bad_artifact_manifest_path = temp / "bad-artifact-manifest.json"
        write_json(bad_artifact_manifest_path, bad_artifact_manifest)
        proc = evidence_run(subject, bad_artifact_manifest_path)
        insist(proc.returncode != 0 and "SHA-256 mismatch for evidence/" in proc.stderr, "artifact hash substitution accepted")
        negatives.append("artifact_hash_substitution_rejected")

        key = temp / "reviewer_key"
        keygen = run(
            [
                "ssh-keygen",
                "-q",
                "-t",
                "ed25519",
                "-N",
                "",
                "-C",
                "synthetic-pilot002-reviewer",
                "-f",
                str(key),
            ]
        )
        insist(keygen.returncode == 0, f"key generation failed: {keygen.stderr}")
        pub = key.with_suffix(".pub").read_text(encoding="utf-8").strip().split()
        insist(len(pub) >= 2, "generated public key is invalid")
        identity = "synthetic-pilot002-reviewer@example.invalid"
        allowed = temp / "allowed_signers"
        allowed.write_text(f"{identity} {pub[0]} {pub[1]}\n", encoding="utf-8")

        record = {
            "schema_version": 1,
            "assessment_id": "SVC",
            "assessment_version": "0.1.1",
            "subject": {
                "repository_hint": "synthetic-pilot002-subject",
                "commit": manifest["subject"]["commit"],
                "evidence_manifest_sha256": evidence_report["manifest_sha256"],
            },
            "verification": {
                "claimed_assurance_class": "INDEPENDENTLY_VERIFIED",
                "performed_at": "2026-09-25T12:15:00Z",
                "method": "HYBRID_REVIEW",
                "result": "PASS",
                "control_ids": control_ids,
                "statement": "SYNTHETIC PILOT-002 end-to-end review claim for integration testing only; not a real independent security assessment.",
            },
            "verifier": {
                "identity": identity,
                "display_name": "Synthetic PILOT-002 External Reviewer",
                "role": "security reviewer",
                "organization": "Example External Lab",
                "relationship": "EXTERNAL",
            },
        }
        record_path = temp / "verification-record.json"
        write_json(record_path, record)
        signature = sign_record(record_path, key)
        ver_proc = verification_run(record_path, evidence_report_path, signature, allowed)
        insist(ver_proc.returncode == 0, f"VERIFICATION-001 failed: {ver_proc.stderr}")
        verification_report = json.loads(ver_proc.stdout)
        insist(verification_report["protocol"] == "VERIFICATION-001", "verification protocol drift")
        insist(verification_report["record_signature"] == "PASS", "record signature not PASS")
        insist(verification_report["subject_commit"] == manifest["subject"]["commit"], "verification subject commit drift")
        insist(verification_report["evidence_manifest_sha256"] == evidence_report["manifest_sha256"], "verification manifest binding drift")
        insist(verification_report["verified_control_count"] == 32, "verification control coverage drift")
        insist(verification_report["signed_external_independence_claim"] is True, "signed external claim missing")
        insist(verification_report["real_world_identity_verified_by_tool"] is False, "identity assurance escalated")
        insist(verification_report["organizational_independence_verified_by_tool"] is False, "independence assurance escalated")
        insist(verification_report["evidence_truth_verified_by_tool"] is False, "evidence truth assurance escalated")
        insist(verification_report["product_security_established"] is False, "product security assurance escalated")
        insist(verification_report["release_authorized"] is False, "verification authorized release")
        checks.append("verification: signed record binds the same subject commit and evidence manifest without assurance escalation")

        alternate_manifest = copy.deepcopy(manifest)
        alternate_manifest["bindings"] = list(reversed(alternate_manifest["bindings"]))
        alternate_manifest_path = temp / "alternate-evidence-manifest.json"
        write_json(alternate_manifest_path, alternate_manifest)
        alternate_ev = evidence_run(subject, alternate_manifest_path)
        insist(alternate_ev.returncode == 0, f"alternate valid EVIDENCE-001 report failed: {alternate_ev.stderr}")
        alternate_report = temp / "alternate-evidence-report.json"
        alternate_report.write_text(alternate_ev.stdout, encoding="utf-8")
        write_json(record_path, record)
        signature = sign_record(record_path, key)
        proc = verification_run(record_path, alternate_report, signature, allowed)
        insist(proc.returncode != 0 and "evidence manifest SHA-256 mismatch" in proc.stderr, "valid but different evidence report substitution accepted")
        negatives.append("valid_evidence_report_substitution_rejected")

        wrong_commit = copy.deepcopy(record)
        wrong_commit["subject"]["commit"] = "a" * 40
        write_json(record_path, wrong_commit)
        signature = sign_record(record_path, key)
        proc = verification_run(record_path, evidence_report_path, signature, allowed)
        insist(proc.returncode != 0 and "subject commit mismatch with evidence report" in proc.stderr, "signed commit rebind accepted")
        negatives.append("signed_subject_commit_rebind_rejected")

        wrong_manifest = copy.deepcopy(record)
        wrong_manifest["subject"]["evidence_manifest_sha256"] = "0" * 64
        write_json(record_path, wrong_manifest)
        signature = sign_record(record_path, key)
        proc = verification_run(record_path, evidence_report_path, signature, allowed)
        insist(proc.returncode != 0 and "evidence manifest SHA-256 mismatch" in proc.stderr, "signed manifest rebind accepted")
        negatives.append("signed_manifest_rebind_rejected")

        wrong_hint = copy.deepcopy(record)
        wrong_hint["subject"]["repository_hint"] = "different-synthetic-label"
        write_json(record_path, wrong_hint)
        signature = sign_record(record_path, key)
        proc = verification_run(record_path, evidence_report_path, signature, allowed)
        insist(proc.returncode != 0 and "repository_hint mismatch with evidence report" in proc.stderr, "signed repository_hint drift accepted")
        negatives.append("signed_repository_hint_drift_rejected")

        write_json(record_path, record)
        signature = sign_record(record_path, key)
        record_path.write_text(
            record_path.read_text(encoding="utf-8").replace(
                "SYNTHETIC PILOT-002 end-to-end review claim",
                "TAMPERED PILOT-002 end-to-end review claim",
                1,
            ),
            encoding="utf-8",
        )
        proc = verification_run(record_path, evidence_report_path, signature, allowed)
        insist(proc.returncode != 0 and "detached SSH signature verification failed" in proc.stderr, "post-signature record tampering accepted")
        negatives.append("post_signature_record_tamper_rejected")

        write_json(record_path, record)
        signature = sign_record(record_path, key)
        wrong_allowed = temp / "wrong_allowed_signers"
        wrong_allowed.write_text(f"other@example.invalid {pub[0]} {pub[1]}\n", encoding="utf-8")
        proc = verification_run(record_path, evidence_report_path, signature, wrong_allowed)
        insist(proc.returncode != 0 and "detached SSH signature verification failed" in proc.stderr, "wrong trust-store identity accepted")
        negatives.append("wrong_trust_store_identity_rejected")

        escalated_evidence = copy.deepcopy(evidence_report)
        escalated_evidence["release_authorized"] = True
        escalated_evidence_path = temp / "escalated-evidence-report.json"
        write_json(escalated_evidence_path, escalated_evidence)
        write_json(record_path, record)
        signature = sign_record(record_path, key)
        proc = verification_run(record_path, escalated_evidence_path, signature, allowed)
        insist(proc.returncode != 0 and "evidence report must not authorize release" in proc.stderr, "release authorization escalation accepted")
        negatives.append("release_authorization_escalation_rejected")

        checks.append("fail-closed: cross-stage substitutions, rebindings, signature tampering and release escalation rejected")

        answers_sha256 = manifest["subject"]["answers"]["sha256"]
        evidence_report_sha256 = sha256_bytes(evidence_report_path.read_bytes())
        verification_record_sha256 = sha256_bytes(json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n")
        insist(verification_report["evidence_report_sha256"] == evidence_report_sha256, "verification evidence-report hash drift")
        insist(verification_report["record_sha256"] == verification_record_sha256, "verification record hash drift")

        return {
            "protocol": "PILOT-002",
            "result": "PASS",
            "scope": "synthetic end-to-end assurance-chain integration only",
            "stages": {
                "assessment": {
                    "en_gate": assessment_outputs["en"]["gate"],
                    "lv_gate": assessment_outputs["lv"]["gate"],
                    "control_count": len(control_ids),
                },
                "evidence": {
                    "protocol": evidence_report["protocol"],
                    "artifact_binding": evidence_report["artifact_binding"],
                    "bound_control_count": len(evidence_report["bound_control_ids"]),
                    "artifact_count": evidence_report["artifact_count"],
                },
                "verification": {
                    "protocol": verification_report["protocol"],
                    "record_signature": verification_report["record_signature"],
                    "claimed_assurance_class": verification_report["claimed_assurance_class"],
                    "verified_control_count": verification_report["verified_control_count"],
                },
            },
            "chain": {
                "subject_commit": manifest["subject"]["commit"],
                "answers_sha256": answers_sha256,
                "evidence_manifest_sha256": evidence_report["manifest_sha256"],
                "evidence_report_sha256": evidence_report_sha256,
                "verification_record_sha256": verification_record_sha256,
            },
            "negative_cases_rejected": len(negatives),
            "negative_cases": negatives,
            "checks": checks,
            "assurance_boundary": {
                "synthetic_only": True,
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
        report_path = PILOT / "reports/synthetic-results.json"
        if args.write:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(rendered, encoding="utf-8")
        else:
            insist(
                report_path.is_file() and report_path.read_text(encoding="utf-8") == rendered,
                "stale PILOT-002 report",
            )
    except (AssertionError, OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(f"PILOT-002 FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        "PILOT-002 PASS: READY assessment -> EVIDENCE-001 -> signed VERIFICATION-001 chain reproduced; "
        "cross-stage substitutions fail closed; no real-world identity, evidence-truth, product-security or release claim."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
