# PILOT-001 — Synthetic release-gate results

**Outcome: PASS for structural CLI behaviour only.** No real product was assessed.

Baseline: `v0.1.1` at `94f4a47ad8c6400d9b6fd15b9d7d6f904f0cc519`; 32 controls, eight domains, 16 diagnostic indicators.

| Scenario | Expected | Observed EN | Observed LV | Blocking gaps | Total gaps |
| --- | --- | --- | --- | ---: | ---: |
| `blocked` | `BLOCKED` | `BLOCKED` | `BLOCKED` | 8 | 9 |
| `conditional` | `CONDITIONAL` | `CONDITIONAL` | `CONDITIONAL` | 0 | 3 |
| `ready` | `READY` | `READY` | `READY` | 0 | 0 |

Invalid input contracts rejected: **14** vectors in both languages.
CI exit contracts verified: **12** combinations.
Incomplete answers fail the release-blocking gate (`BLOCKED`).

## Deliberately exposed limitations

- **LIM-EVIDENCE-001:** fabricated nonempty evidence strings can produce `READY`. The tool checks presence, **not evidence authenticity**.
- **LIM-APPLICABILITY-002:** when N/A is allowed, a nonempty reason is accepted without verifying its factual basis.
- **LIM-DUPLICATE-003 — REMEDIATED by INPUT-001:** the original last-wins finding remains historical; the current evaluator rejects duplicate JSON keys.
- **LIM-SYNTHETIC-004:** fixture scenarios do not test or establish the security of any real product.

**Interpretation:** `READY` here demonstrates the evaluator’s formal decision contract, not permission to deploy software.
