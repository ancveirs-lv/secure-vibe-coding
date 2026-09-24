# INPUT-001 — Five-direction skeptical review

Date: 2026-09-24
Base: merged EVIDENCE-001 main `c29c53c11c18a3bf3bf5fb3669ceacd0e4ba690b`
Scope: direct assessment-input parsing and fail-closed contract behaviour.

| Direction | Skeptical question | Acceptance condition | Residual limitation |
| --- | --- | --- | --- |
| Parser ambiguity | Can duplicate JSON keys hide an earlier state or metadata value? | Duplicate keys are rejected recursively at root, `answers`, and nested answer objects in EN/LV paths. | This does not validate semantic truth of unique values. |
| JSON strictness | Can Python-specific permissive JSON (`NaN`, `Infinity`) or invalid UTF-8 cross the boundary? | Non-standard constants and invalid UTF-8 are rejected before evaluation. | JSON canonicalisation/signing is outside INPUT-001. |
| Schema drift | Can unknown top-level metadata be silently ignored? | Only `assessment_id`, `version`, and `answers` are accepted at the top level; existing nested-field restrictions remain. | A future schema change must explicitly revise the contract. |
| Availability / resource bound | Can an arbitrarily large answer document be parsed? | Direct assessment input is capped at 1 MiB before JSON decoding. | This is a local CLI bound, not a general DoS guarantee for every integration. |
| Compatibility / evidence boundary | Does hardening alter valid EN/LV gates or falsely upgrade evidence assurance? | Existing valid `READY` remains `READY`, sparse input remains `BLOCKED` under strict CI, and output still states evidence is self-reported. | Evidence authenticity and factual N/A review remain separate work. |

## Pilot-fixture boundary

PILOT-001 retains `scenario_id` only as harness metadata. Before invoking the hardened `assess.py`, the harness constructs an assessment document containing only `assessment_id`, `version`, and `answers`. INPUT-001 separately verifies that a direct assessment carrying `scenario_id` is rejected.

## Audit conclusion

**PASS candidate for INPUT-001 if the repository CI reproduces the committed INPUT-001 report and the full regression suite remains green.** `LIM-DUPLICATE-003` is then considered remediated at the direct `assess.py` input boundary. No product-security, evidence-authenticity, compliance or deployment-authorization claim follows from this result.
