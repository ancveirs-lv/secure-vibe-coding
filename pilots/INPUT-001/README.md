# INPUT-001 — Fail-closed assessment input

**Status: audited development hardening; not a v0.2.0 release claim.**

INPUT-001 closes the duplicate-key parser weakness identified by PILOT-001 and strengthens the direct `assess.py` input boundary without changing the 32-control model or its `BLOCKED` / `CONDITIONAL` / `READY` semantics.

## Enforced input rules

- JSON object keys must be unique at every nesting level.
- Non-standard JSON constants such as `NaN` and `Infinity` are rejected.
- Input must be valid UTF-8 and no larger than 1 MiB.
- Top-level fields are limited to `assessment_id`, `version` and `answers`.
- Existing control-ID, state, evidence-note, N/A and CI-gate rules remain in force.
- Valid sparse input is still permitted and defaults omitted controls to `UNKNOWN`; it therefore cannot silently become `READY`.

The hardening is syntax- and contract-focused. It does **not** authenticate evidence, validate the factual truth of an N/A rationale or establish product security.

## Run

```bash
python3 pilots/INPUT-001/run_input_pilot.py --check
python3 -m unittest discover -s tests -v
```

The original PILOT-001 duplicate-key finding remains documented as historical context and is now marked remediated by INPUT-001.
