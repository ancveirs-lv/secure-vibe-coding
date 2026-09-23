# EVIDENCE-001 — Five-direction skeptical review

Date: 2026-09-23
Baseline: `v0.1.1` + merged PILOT-001, `3f9b6d0a23085156c50f89ebd2fef9c634b7af22`
Scope: **synthetic offline local-Git binding**, not independent product evidence authentication.

| Direction | Skeptical question | Mitigation and check | Residual limitation |
| --- | --- | --- | --- |
| Evidence claims | Can an invented log be passed off as true merely because its hash matches? | Report explicitly says `evidence_claims_independently_verified: false` and `release_authorized: false`; positive fixture uses synthetic markers. | Independent log authenticity and control effectiveness remain for VERIFICATION-001. |
| Commit provenance | Does the claimed hash identify the remote author/deployed product? | Read blobs from a specific locally resolved Git commit, not working-tree paths; report dirty tree and HEAD drift. | `repository_hint` and commit origin are unverified offline; signed attestations/remote verification are out of scope. |
| Input integrity | Can duplicate JSON keys, missing binding or path traversal conceal unsupported claims? | Strict duplicate-key parsing in this new verifier, exact field schemas, all 32 explicit answers, all IMPLEMENTED/VERIFIED controls bound; negative cases. | Direct v0.1.1 `assess.py` still has duplicate-key parsing vulnerability; INPUT-001 is separate. |
| Filesystem safety | Can an artifact be swapped after commit, symlinked outside, or hashed from the wrong file? | Only exact regular tracked Git blobs at the target commit; SHA-256 from blob bytes; symlinks, reused paths and hash mismatches rejected. | Malicious Git config/large repositories remain an operator trust boundary. |
| EN/LV and reproducibility | Can locale change the gate, and can tests silently drift? | Exact v0.1.1 baseline hashes remain untouched; verifier invokes the baseline evaluator in both languages; CI runs the deterministic synthetic pilot. | No real product and no independent human translation audit in this technical harness. |

**Conclusion:** candidate PASS only for offline hash-to-Git-commit binding and explicit limitations; no claim of security, compliance or release approval.
