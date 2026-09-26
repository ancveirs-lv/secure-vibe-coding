# VERIFICATION-001 — Signed verification-record provenance

**Status: audited development foundation; not a v0.2.0 release claim and not an independent security certification.**

VERIFICATION-001 adds a signed verification record on top of EVIDENCE-001. The exact JSON record is detached-SSH-signed and checked against an operator-supplied OpenSSH `allowed_signers` trust store. The record is also bound to the same descriptive `repository_hint`, exact subject commit and EVIDENCE-001 manifest SHA-256. The hint remains an untrusted label; equality prevents cross-stage label drift but does not authenticate a repository owner.

## Claimed assurance classes

The record may state one of four **claimed** classes:

- `SELF_REPORTED`
- `TOOL_VERIFIED`
- `HUMAN_REVIEWED`
- `INDEPENDENTLY_VERIFIED`

The word **claimed** is intentional. For `INDEPENDENTLY_VERIFIED`, the verifier must declare an `EXTERNAL` relationship and the signed record must verify against the trust store. This cryptographically attributes the exact statement to a key accepted for the configured identity.

It still does **not** prove that the identity belongs to the named real-world person or organisation, that the reviewer is actually independent, that the underlying evidence is truthful, that the product is secure, or that release is authorised. Those facts require governance outside this local verifier.

## Command

```bash
python3 scripts/verify_verification.py   --record /path/to/verification-record.json   --evidence-report /path/to/evidence-report.json   --signature /path/to/verification-record.json.sig   --allowed-signers /path/to/allowed_signers
```

Sign the exact record with the fixed namespace:

```bash
ssh-keygen -Y sign   -f /path/to/private_key   -n secure-vibe-coding-verification-v1   /path/to/verification-record.json
```

The trust-store mapping is an operator responsibility. Keep the verification record, signature, allowed-signers policy/version, EVIDENCE-001 report and evidence manifest together when preserving assurance history.
