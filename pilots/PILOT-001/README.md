# PILOT-001 — Release-gate contract validation

**Status: controlled synthetic pilot, not a real-world product security assessment.**

This pilot tests the published `v0.1.1` Anti-AI-Slop evaluator without changing its scoring-free, evidence-gap model. All 32 controls are present in every fixture. All `VERIFIED` evidence strings are deliberately labelled **SYNTHETIC TEST TOKEN** and do not establish real-world verification.

## Three scenarios

| Case | Synthetic situation | Expected result | Important interpretation |
| --- | --- | --- | --- |
| `blocked` | Gaps in architecture, server-side authorization, cross-user isolation, secrets, dependency review, agent permissions and security tests | `BLOCKED` | Eight blocking control gaps; missing/nonverified evidence prevents an affirmative release decision. |
| `conditional` | Blocking controls appear satisfied, while threat-model documentation, restore evidence and rollback evidence remain incomplete | `CONDITIONAL` | Three non-blocking control gaps remain; not a security approval. |
| `ready` | All 32 answers contain `VERIFIED` and nonempty **fabricated demonstration tokens** | `READY` | Proves only that the CLI accepts structurally complete self-reported answers. It does **not** establish product security or truth of evidence. |

## Run the controlled pilot

```bash
python3 pilots/PILOT-001/run_pilot.py --check
python3 pilots/PILOT-001/run_pilot.py --write
python3 -m unittest discover -s tests -v
```

`--check` validates all expected outcomes and compares the committed deterministic reports. `--write` recomputes the reports after running the same checks. The pilot uses only the Python standard library, makes no network requests and does not deploy a vulnerable application.

## Scope and interpretation

1. Evaluator identity/version, 32-control coverage, domain count and answer-state assumptions are pinned to the published `v0.1.1` model.
2. Every positive scenario runs in **both EN and LV**. The gate, relevant gap IDs and exit behaviour must match across languages; recommendation text remains localised.
3. `--fail-on-blocked` and `--require-ready` exit statuses are verified for all three outcomes.
4. Input contract failures, unsupported fields and attempts to misuse `NOT_APPLICABLE` are exercised. An incomplete answers object must not produce `READY`.
5. The pilot intentionally confirms an **evidence authenticity limitation**: a fabricated but nonempty evidence string can produce `READY`. Likewise, `NOT_APPLICABLE` rationale semantics are not validated and duplicate JSON answer keys currently use last-wins parsing. These are findings for the proposed `v0.2.0` evidence design, not hidden successes.

Outputs: `reports/results.json`, `reports/summary.en.md`, `reports/summary.lv.md`.

## Acceptance boundary

PILOT-001 passes if the implementation reproduces the stated **structural** behaviour exactly and the limitations are disclosed. It cannot justify public deployment of a tested product: no real product or authenticated evidence is included.

The next stage should introduce an evidence manifest tied to actual commits, artefacts, verifier identities and test results, followed by an independently reviewed product-specific pilot.
