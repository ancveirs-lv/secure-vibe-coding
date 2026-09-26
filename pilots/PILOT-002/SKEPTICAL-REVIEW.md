# PILOT-002 — Five-direction skeptical review

Date: 2026-09-26
Base: merged VERIFICATION-001 main `81966f5aefda06696d7971e6c65f668ca754e970`
Scope: end-to-end composition of assessment, EVIDENCE-001 and VERIFICATION-001 in one synthetic subject chain.

| Direction | Skeptical question | Acceptance condition | Residual limitation |
| --- | --- | --- | --- |
| Cross-stage identity | Can assessment, evidence and signed verification silently refer to different subjects? | The positive path carries one exact subject commit through EVIDENCE-001 and VERIFICATION-001; changed commit/manifest bindings fail closed. | `repository_hint` remains a label and does not authenticate a remote repository owner. |
| Artifact integrity | Can answers or evidence artifacts be substituted while keeping the chain green? | Pinned answer and artifact SHA-256 substitutions fail EVIDENCE-001. | Matching bytes do not establish truth, adequacy or security relevance. |
| Signed provenance | Can a record be edited after signing or verified under an unrelated trust-store identity? | Post-signature byte changes and wrong `allowed_signers` identities fail verification. | Trust-store enrolment and real-world identity proofing remain external governance. |
| Assurance escalation | Can a composed PASS become a security or release-authorization claim? | Final report and underlying verifiers keep identity, independence, evidence truth, product security and release authorization false; a forged release-authorization field is rejected. | An external organization may make a later release decision using this evidence, outside this tool. |
| Reproducibility | Can the same synthetic chain be regenerated deterministically across local and CI runs? | The committed report must match a fresh `--check`, including deterministic subject commit and cross-stage hashes. | The cryptographic signing key is ephemeral and intentionally not preserved; the report records no claim about key provenance. |

## Audit conclusion

**PASS candidate only if the committed report reproduces, all earlier pilots remain green, the full unit-test suite passes, and CI executes PILOT-002.** This pilot validates protocol composition only. It does not convert structural or cryptographic provenance into factual evidence truth, real-world identity, product security, compliance or permission to release.
