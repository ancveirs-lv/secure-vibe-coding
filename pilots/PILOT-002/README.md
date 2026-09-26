# PILOT-002 — End-to-end assurance-chain integration

**Status: synthetic integration pilot for the v0.2.0 candidate path. It is not a security certification, penetration test, compliance determination or release authorization.**

PILOT-002 exercises the current baseline as one connected chain instead of testing each layer in isolation:

`assessment input -> READY gate -> EVIDENCE-001 Git/SHA-256 binding -> signed VERIFICATION-001 record -> final bounded assurance output`

The pilot creates a temporary synthetic product repository, commits one assessment input plus 32 synthetic evidence artifacts, and uses that exact commit through every later stage.

## Acceptance conditions

- the same committed assessment input produces `READY` in EN and LV;
- EVIDENCE-001 binds all 32 controls to regular Git blobs at the exact subject commit;
- the signed VERIFICATION-001 record refers to that same commit and exact evidence-manifest SHA-256;
- the detached signature verifies only through the explicit `allowed_signers` mapping;
- valid-but-different evidence reports, changed hashes, changed signed subject bindings, post-signature tampering and a forged `release_authorized=true` report fail closed;
- the final report keeps real-world identity, organizational independence, evidence truth, product security and release authorization explicitly false.

## Reproduce

```bash
python3 pilots/PILOT-002/run_pilot.py --check
```

To regenerate the committed deterministic report:

```bash
python3 pilots/PILOT-002/run_pilot.py --write
```

## Interpretation

A `PASS` means the current local protocols compose without losing their binding semantics in this synthetic scenario. It does **not** mean the synthetic evidence is truthful, that a real reviewer identity was established, that an organization is actually independent, that a product is secure, or that deployment is authorized.
