# EVIDENCE-001 — Offline artifact-to-commit binding

**Status: audited development foundation; no v0.2.0 release claim.**

This optional verifier binds *declared* `IMPLEMENTED` and `VERIFIED` self-assessment answers to files that exist as regular Git blobs at one exact local product commit. It verifies SHA-256 hashes, rejects duplicate JSON keys in its manifest and pinned answers, checks EN/LV structural gate parity, and reports local working-tree drift. It does **not** modify the existing `v0.1.1` release evaluator.

## Trust boundaries

- Hash match proves that specific bytes are present in the specified **local Git commit**. It does not establish who created the repository or whether a public remote has that commit.
- The `repository_hint` is an untrusted descriptive label. A Git commit SHA is not a digital signature.
- A fabricated test log may have a valid hash. `artifact_binding: PASS` means **bytes were bound**, not that the control works, evidence is genuine or an independent reviewer approved it.
- `NOT_APPLICABLE` rationales remain unverified. The legacy direct `assess.py` parser is **not** fixed by this optional verifier; `INPUT-001` will address it separately.
- The tool always emits `release_authorized: false` and `evidence_claims_independently_verified: false`. Its `structural_gates` are only the existing self-reported `v0.1.1` gates.
- Only explicitly committed Git blobs are assessed. Changes in the working tree do not substitute for the pinned commit.

## Manifest and command

Manifest structure (illustrative placeholders, not runnable evidence):

```json
{
  "schema_version": 1,
  "assessment_id": "SVC",
  "assessment_version": "0.1.1",
  "subject": {
    "repository_hint": "example-local-product (identity not authenticated)",
    "commit": "<full Git commit SHA>",
    "answers": {"path": "assessment/answers.json", "sha256": "<64 lowercase hex>"}
  },
  "bindings": [
    {
      "control_id": "O04",
      "artifacts": [{"path": "evidence/review.txt", "sha256": "<64 lowercase hex>", "kind": "review_record"}]
    }
  ]
}
```

A real manifest must bind **every** `IMPLEMENTED` and `VERIFIED` response; `UNKNOWN`, `CLAIMED` and `NOT_APPLICABLE` may not be represented as verified artifact bindings. Every one of the 32 control responses must be explicitly present in the pinned answers file. `VERIFIED` still requires a self-reported evidence note in the underlying assessment; its accuracy is not authenticated here.

```bash
python3 scripts/verify_evidence.py --repo /path/to/product-git-repository --manifest /path/to/external-manifest.json
python3 pilots/EVIDENCE-001/run_evidence_pilot.py --check
python3 -m unittest discover -s tests -v
```

The manifest is held **outside the assessed product commit**, avoiding circular self-reference. It may be archived or reviewed independently. Hash the manifest itself (`manifest_sha256` is included in output); retaining and attributing it is a separate assurance task.

**Scope:** offline local Git object and SHA-256 validation only. No network, signatures, reviewer authentication, attestation, penetration testing, vulnerability scanning, or permission to deploy. Run the verifier only on repositories you trust to inspect.
