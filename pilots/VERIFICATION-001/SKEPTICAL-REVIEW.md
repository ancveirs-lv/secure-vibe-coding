# VERIFICATION-001 — Five-direction skeptical review

Date: 2026-09-24
Base: merged INPUT-001 main `f692e76883c5f63ac0bef772646d4c78013168d2`
Scope: signed verification-record provenance and assurance-boundary enforcement.

| Direction | Skeptical question | Acceptance condition | Residual limitation |
| --- | --- | --- | --- |
| Statement integrity | Can a signed review record be changed after signature? | Any byte change causes detached SSH signature verification to fail. | The verifier does not protect copies stored outside the checked signature workflow. |
| Identity attribution | Does a valid signature prove the named real-world human or organisation? | Output states only that the record matches an identity in the operator-supplied `allowed_signers` trust store. | Trust-store enrolment and real-world identity proofing remain external governance. |
| Independence | Can an internal reviewer label a record `INDEPENDENTLY_VERIFIED`? | This class requires `EXTERNAL` relationship plus a valid trusted signature. | The tool does not prove the declared external relationship or absence of conflicts of interest. |
| Evidence provenance | Can a review silently refer to a different commit, manifest or unbound control? | Subject commit, manifest SHA-256 and reviewed control IDs must match a PASS EVIDENCE-001 report. | EVIDENCE-001 binds bytes, not the truth or sufficiency of their content. |
| Assurance escalation | Can a valid signed record imply security certification or deployment permission? | Output hard-codes real-world identity verification, organizational independence verification, evidence truth, product security and release authorization to `false`. | A separate organizational policy may make decisions using these records, but this tool does not. |

## Audit conclusion

**PASS candidate only if CI reproduces the deterministic synthetic report and the full regression suite is green.** VERIFICATION-001 provides cryptographic provenance for the exact review statement and binds it to EVIDENCE-001. It does not establish real-world identity, actual reviewer independence, evidence truth, product security, compliance or release authorization.
