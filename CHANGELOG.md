# Changelog

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
