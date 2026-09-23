# PILOT-001 — Five-direction skeptical review

**Scope:** review of a **synthetic evaluation harness**, not a security audit of a product. Baseline `v0.1.1`, pinned commit `94f4a47ad8c6400d9b6fd15b9d7d6f904f0cc519`.

| Direction | Adversarial question | Verifiable acceptance condition | Residual limitation |
| --- | --- | --- | --- |
| Decision methodology | Can `BLOCKED` become `CONDITIONAL` merely because blocking controls are omitted? | Every fixture supplies all 32 IDs. Sparse input is tested and remains `BLOCKED`. | Unsupported truth claims cannot be disproven by the CLI. |
| EN/LV parity | Does changing `--lang` change the gate? | All three cases run in both languages. Gate, gap IDs, control semantics and CI exit codes are compared. | Human technical-translation review remains separate. |
| Input contract | Can incorrect version, unknown control ID, missing evidence or illegal N/A be accepted? | Thirteen negative payload types are rejected in both languages. | Unsupported *top-level* metadata is not rejected by `assess.py`; duplicate JSON keys are currently last-wins and separately disclosed. |
| Exit codes / reproducibility | Can blocked or conditional assessments silently pass a strict CI release gate? | Twelve explicit exit-contract combinations, deterministic committed reports and CI execution. | Users must actually select the appropriate gate flag in their own pipeline. |
| Evidence integrity | Can `READY` be reached with fabricated evidence labels or unverified N/A reasons? | Yes; test intentionally records the behaviour as `LIM-EVIDENCE-001` and `LIM-APPLICABILITY-002` and duplicate-key issue `LIM-DUPLICATE-003`. | Requires new evidence provenance and human or automated independent verification design in `v0.2.0`. |

**Conclusion:** pass for *offline structural behaviour* only when reproducible runner returns PASS. No real-world security, compliance or product-release conclusion may be drawn.
