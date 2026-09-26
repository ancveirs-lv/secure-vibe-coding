from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAX_RECORD = 512 * 1024
MAX_EVIDENCE_REPORT = 2 * 1024 * 1024
MAX_SIGNATURE = 128 * 1024
MAX_ALLOWED_SIGNERS = 256 * 1024
HEX40_64 = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
IDENTITY = re.compile(r"[A-Za-z0-9._@:+-]{1,128}\Z")
NAMESPACE = "secure-vibe-coding-verification-v1"
ASSURANCE_CLASSES = {"SELF_REPORTED", "TOOL_VERIFIED", "HUMAN_REVIEWED", "INDEPENDENTLY_VERIFIED"}
RELATIONSHIPS = {"SUBJECT", "INTERNAL", "EXTERNAL", "TOOL"}
METHODS = {"MANUAL_REVIEW", "AUTOMATED_TOOL", "HYBRID_REVIEW"}
RESULTS = {"PASS", "FAIL", "INCONCLUSIVE"}


class VerificationError(Exception):
    pass


def must(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError(f"duplicate JSON key rejected: {key}")
        result[key] = value
    return result


def reject_nonstandard(value):
    raise VerificationError(f"nonstandard JSON constant rejected: {value}")


def decode_json(raw: bytes, label: str):
    try:
        return json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=unique_pairs,
            parse_constant=reject_nonstandard,
        )
    except UnicodeDecodeError as exc:
        raise VerificationError(f"{label} must be valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise VerificationError(f"invalid JSON in {label}: {exc}") from exc


def bounded_file(path: Path, maximum: int, label: str) -> bytes:
    must(path.is_file(), f"{label} not found")
    size = path.stat().st_size
    must(0 < size <= maximum, f"{label} is empty or exceeds size cap")
    return path.read_bytes()


def exact_keys(value, required, label):
    must(isinstance(value, dict), f"{label} must be an object")
    must(set(value) == set(required), f"{label} field mismatch: expected {sorted(required)}, got {sorted(value)}")


def valid_sha256(value, label):
    must(isinstance(value, str) and bool(HEX64.fullmatch(value)), f"invalid SHA-256 for {label}")


def valid_commit(value):
    must(isinstance(value, str) and bool(HEX40_64.fullmatch(value)), "invalid subject commit")


def valid_text(value, label, maximum=500):
    must(isinstance(value, str) and 1 <= len(value.strip()) <= maximum, f"{label} must be a nonempty string")
    must(not any(ord(c) < 32 and c not in "\t" for c in value), f"{label} contains control characters")


def parse_timestamp(value):
    must(isinstance(value, str) and value.endswith("Z"), "performed_at must be RFC3339 UTC ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise VerificationError("invalid performed_at timestamp") from exc
    must(parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0, "performed_at must be UTC")
    must(parsed <= datetime.now(timezone.utc), "performed_at cannot be in the future")
    return parsed


def verify_signature(record_bytes: bytes, identity: str, signature: Path, allowed_signers: Path):
    must(shutil.which("ssh-keygen") is not None, "ssh-keygen is required")
    must(bool(IDENTITY.fullmatch(identity)), "invalid verifier identity")
    bounded_file(signature, MAX_SIGNATURE, "signature")
    bounded_file(allowed_signers, MAX_ALLOWED_SIGNERS, "allowed signers file")
    proc = subprocess.run(
        [
            "ssh-keygen", "-Y", "verify",
            "-f", str(allowed_signers),
            "-I", identity,
            "-n", NAMESPACE,
            "-s", str(signature),
        ],
        input=record_bytes,
        capture_output=True,
        timeout=20,
        check=False,
    )
    must(proc.returncode == 0, "detached SSH signature verification failed")


def verify(record_path: Path, evidence_report_path: Path, signature: Path, allowed_signers: Path):
    record_bytes = bounded_file(record_path, MAX_RECORD, "verification record")
    evidence_bytes = bounded_file(evidence_report_path, MAX_EVIDENCE_REPORT, "evidence report")
    record = decode_json(record_bytes, "verification record")
    evidence = decode_json(evidence_bytes, "evidence report")

    meta = decode_json((ROOT / "data/meta.json").read_bytes(), "baseline meta")
    exact_keys(
        record,
        ("schema_version", "assessment_id", "assessment_version", "subject", "verification", "verifier"),
        "verification record",
    )
    must(type(record["schema_version"]) is int and record["schema_version"] == 1, "unsupported verification schema version")
    must(record["assessment_id"] == meta["assessment_id"], "verification assessment_id mismatch")
    must(record["assessment_version"] == meta["version"], "verification assessment_version mismatch")

    subject = record["subject"]
    exact_keys(subject, ("repository_hint", "commit", "evidence_manifest_sha256"), "subject")
    valid_text(subject["repository_hint"], "repository_hint", 200)
    valid_commit(subject["commit"])
    valid_sha256(subject["evidence_manifest_sha256"], "evidence manifest")

    verification = record["verification"]
    exact_keys(
        verification,
        ("claimed_assurance_class", "performed_at", "method", "result", "control_ids", "statement"),
        "verification",
    )
    assurance = verification["claimed_assurance_class"]
    must(assurance in ASSURANCE_CLASSES, "unsupported claimed assurance class")
    method = verification["method"]
    must(method in METHODS, "unsupported verification method")
    result = verification["result"]
    must(result in RESULTS, "unsupported verification result")
    parse_timestamp(verification["performed_at"])
    valid_text(verification["statement"], "verification statement", 2000)
    control_ids = verification["control_ids"]
    must(isinstance(control_ids, list) and 1 <= len(control_ids) <= 32, "control_ids must contain 1..32 entries")
    must(all(isinstance(x, str) and re.fullmatch(r"[A-Z][0-9]{2}", x) for x in control_ids), "invalid control ID in verification")
    must(len(set(control_ids)) == len(control_ids), "duplicate control ID in verification")

    verifier = record["verifier"]
    exact_keys(verifier, ("identity", "display_name", "role", "organization", "relationship"), "verifier")
    identity = verifier["identity"]
    must(isinstance(identity, str) and bool(IDENTITY.fullmatch(identity)), "invalid verifier identity")
    valid_text(verifier["display_name"], "verifier display_name", 200)
    valid_text(verifier["role"], "verifier role", 200)
    valid_text(verifier["organization"], "verifier organization", 200)
    relationship = verifier["relationship"]
    must(relationship in RELATIONSHIPS, "unsupported verifier relationship")

    if assurance == "SELF_REPORTED":
        must(relationship == "SUBJECT", "SELF_REPORTED requires SUBJECT relationship")
        must(method in {"MANUAL_REVIEW", "HYBRID_REVIEW"}, "SELF_REPORTED requires a human statement")
    elif assurance == "TOOL_VERIFIED":
        must(relationship == "TOOL" and method == "AUTOMATED_TOOL", "TOOL_VERIFIED requires TOOL relationship and AUTOMATED_TOOL method")
    elif assurance == "HUMAN_REVIEWED":
        must(relationship in {"SUBJECT", "INTERNAL", "EXTERNAL"}, "HUMAN_REVIEWED requires a human relationship")
        must(method in {"MANUAL_REVIEW", "HYBRID_REVIEW"}, "HUMAN_REVIEWED requires human review component")
    elif assurance == "INDEPENDENTLY_VERIFIED":
        must(relationship == "EXTERNAL", "INDEPENDENTLY_VERIFIED requires EXTERNAL relationship")
        must(method in {"MANUAL_REVIEW", "HYBRID_REVIEW"}, "INDEPENDENTLY_VERIFIED requires human review component")

    verify_signature(record_bytes, identity, signature, allowed_signers)

    must(isinstance(evidence, dict), "evidence report must be an object")
    must(evidence.get("protocol") == "EVIDENCE-001", "evidence report protocol mismatch")
    must(evidence.get("artifact_binding") == "PASS", "evidence artifact binding is not PASS")
    must(evidence.get("release_authorized") is False, "evidence report must not authorize release")
    must(evidence.get("evidence_claims_independently_verified") is False, "unexpected evidence assurance claim")
    evidence_subject = evidence.get("subject")
    must(isinstance(evidence_subject, dict), "evidence report subject missing")
    must(evidence_subject.get("repository_hint") == subject["repository_hint"], "repository_hint mismatch with evidence report")
    must(evidence_subject.get("commit") == subject["commit"], "subject commit mismatch with evidence report")
    must(evidence.get("manifest_sha256") == subject["evidence_manifest_sha256"], "evidence manifest SHA-256 mismatch")
    bound = evidence.get("bound_control_ids")
    must(isinstance(bound, list) and all(isinstance(x, str) for x in bound), "evidence report bound_control_ids invalid")
    missing = sorted(set(control_ids) - set(bound))
    must(not missing, "verification references controls without evidence bindings: " + ", ".join(missing))

    signed_external_claim = assurance == "INDEPENDENTLY_VERIFIED" and relationship == "EXTERNAL"
    return {
        "protocol": "VERIFICATION-001",
        "record_signature": "PASS",
        "signature_namespace": NAMESPACE,
        "signed_identity": identity,
        "claimed_assurance_class": assurance,
        "verification_method": method,
        "verification_result": result,
        "performed_at": verification["performed_at"],
        "subject_commit": subject["commit"],
        "evidence_manifest_sha256": subject["evidence_manifest_sha256"],
        "verified_control_ids": control_ids,
        "verified_control_count": len(control_ids),
        "identity_bound_to_allowed_signers": True,
        "signed_external_independence_claim": signed_external_claim,
        "real_world_identity_verified_by_tool": False,
        "organizational_independence_verified_by_tool": False,
        "evidence_truth_verified_by_tool": False,
        "product_security_established": False,
        "release_authorized": False,
        "record_sha256": hashlib.sha256(record_bytes).hexdigest(),
        "evidence_report_sha256": hashlib.sha256(evidence_bytes).hexdigest(),
        "interpretation": (
            "The detached SSH signature authenticates the exact verification record to an identity present "
            "in the operator-supplied allowed_signers trust store and the record is bound to the EVIDENCE-001 "
            "subject commit and manifest hash. The tool does not independently establish the real-world identity, "
            "organizational independence, truth of the evidence, product security or deployment authorization."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="Verify signed VERIFICATION-001 records against EVIDENCE-001 output.")
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--evidence-report", type=Path, required=True)
    parser.add_argument("--signature", type=Path, required=True)
    parser.add_argument("--allowed-signers", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify(args.record, args.evidence_report, args.signature, args.allowed_signers)
    except (VerificationError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"VERIFICATION-001 FAIL: {exc}", file=__import__("sys").stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
