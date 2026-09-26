# Changelog

## 2026-09-26 — v0.2.0 assurance-chain release

### Pre-release audit hardening

- refreshed official source-verification dates after the 2026-09-26 source-fidelity review;
- made assessment-contract version scope explicit instead of conflating it with the repository release tag;
- removed the hard-coded VERIFICATION-001 assessment version in favor of `data/meta.json`;
- required signed verification records and EVIDENCE-001 reports to use the same descriptive `repository_hint`, while preserving the explicit non-authentication boundary.

### PILOT-002 end-to-end assurance-chain integration

- composed READY assessment, EVIDENCE-001 and VERIFICATION-001 over one deterministic synthetic subject commit;
- required all 32 control bindings and preserved exact commit/manifest hashes across stages;
- rejected valid-but-different evidence-report substitution, signed subject rebinding, post-signature tampering and trust-store identity mismatch;
- rejected release-authorization escalation while preserving explicit no-security/no-certification boundaries.

### VERIFICATION-001 signed review provenance

- added strict signed verification records bound to EVIDENCE-001 subject commit and manifest SHA-256;
- verified detached OpenSSH signatures against an explicit operator-supplied `allowed_signers` trust store;
- constrained claimed assurance classes and prevented internal reviewers from claiming `INDEPENDENTLY_VERIFIED`;
- preserved hard boundaries: no automatic real-world identity, independence, evidence-truth, product-security or release-authorization conclusion.

### INPUT-001 fail-closed input hardening

- rejected duplicate JSON keys recursively in direct assessment input;
- rejected `NaN`/`Infinity`, invalid UTF-8, inputs above 1 MiB and unknown top-level fields;
- preserved valid EN/LV gate and CI semantics while retaining sparse-input fail-closed behaviour;
- marked PILOT-001 `LIM-DUPLICATE-003` as remediated without upgrading evidence-authenticity claims.

### EVIDENCE-001 offline Git binding foundation

- added an optional local Git blob SHA-256 verifier and strict manifest/pinned-answer parser;
- bound all declared IMPLEMENTED/VERIFIED controls to committed artifacts without upgrading self-reported security claims;
- added synthetic Git-commit tampering, path-hardening, EN/LV parity, and known-limitations regression tests;
- preserved the published `v0.1.1` baseline and PILOT-001 results without rewriting them.

### PILOT-001 structural validation

- introduced deterministic synthetic `BLOCKED`, `CONDITIONAL` and `READY` scenarios with EN/LV parity checks;
- exercised CI exit codes and rejected malformed/self-inconsistent assessment inputs;
- documented that structurally valid `READY` does not authenticate evidence or prove production security;
- added deterministic pilot reports to the primary CI workflow.

## 2026-09-23 — v0.1.1 release-contract hardening

- completed the full MIT code licence and linked the full CC BY 4.0 terms;
- required exact assessment ID and version in assessment input;
- rejected unknown or duplicate-like malformed answer IDs and unsupported answer fields;
- added explicit CI exit modes `--fail-on-blocked` and `--require-ready`;
- documented that an evidence note is not independently verified by the tool;
- expanded regression coverage for malformed input and CI gate modes.

## 2026-09-23 — v0.1.0 audited pilot baseline

- 32 bilingual controls across eight release-safety domains;
- evidence-state release gate with `BLOCKED`, `CONDITIONAL`, and `READY`;
- `VERIFIED` evidence-note requirement and constrained `NOT_APPLICABLE`;
- 16 bilingual Anti-AI-Slop diagnostic indicators;
- NIST, OWASP and OpenSSF source registry with explicit scope metadata;
- five-direction skeptical audit incorporated before publication;
- deterministic rendering, local assessment, regression tests and CI.
