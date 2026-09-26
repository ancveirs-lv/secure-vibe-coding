# Anti-AI-Slop — Secure Vibe Coding Baseline

[Latviski](README.lv.md) · **English**

**32-control bilingual release gate for AI-assisted software · global English baseline · Latvian localisation**

> AI made it work. What evidence shows that it is safe enough to release?

This repository is for developers, founders and small teams using AI code assistants or coding agents to build software quickly.

**Anti-AI-Slop** is a project label for rejecting software changes that are accepted or deployed without sufficient understanding, constraints or evidence. It is **not** a claim that AI-generated code is inherently insecure.

## Release model

`AI-assisted change → understanding → constraints → implementation → verification → evidence → release decision`

The tool intentionally produces **no overall security score**.

Possible gate results:

- `BLOCKED` — at least one release-blocking control does not meet its required evidence state;
- `CONDITIONAL` — release blockers are satisfied, but non-blocking gaps remain;
- `READY` — all applicable controls meet their required evidence state.

The tool checks that a verification evidence note exists, but **does not authenticate the evidence itself**; the release owner must inspect it. Inputs must declare matching `assessment_id` and `version`; unknown control IDs fail closed. Use `--fail-on-blocked` to make a `BLOCKED` gate fail CI, or `--require-ready` when any gap must fail CI.

`VERIFIED` requires an evidence note. `NOT_APPLICABLE` is allowed only on controls that explicitly permit it and requires a rationale.

## Domains

1. Ownership and understanding
2. Authentication and authorization
3. Data and secrets
4. Dependencies and supply chain
5. Inputs and business logic
6. AI agents, MCP and tool access
7. Deployment and runtime
8. Release evidence

## Anti-AI-Slop indicators

The repository also includes 16 practical warning signals such as blind dependency installation, client-side authorization, unrestricted coding-agent permissions, disabling security checks to make a build pass, and merging large generated diffs without understanding them.

These indicators are diagnostic prompts, not vulnerability classifications.

## Quick start

```bash
python3 scripts/validate.py
python3 scripts/render.py --check
python3 -m unittest discover -s tests -v
python3 scripts/assess.py examples/answers.example.json
```

No assessment answers are transmitted by the repository tooling.

## Source posture

The control wording is original project wording informed by registered sources.

- NIST SSDF 1.1 is the general secure-development backbone.
- OWASP ASVS 5.0.0 provides application-security verification rationale.
- OWASP Secure Coding with AI addresses AI-assisted development-specific risks.
- OWASP Top 10 for Agentic Applications 2026 is used only where agentic/tool-using behaviour is relevant.
- OpenSSF guidance informs secure AI-code-assistant instructions and human-review boundaries.

A source reference indicates rationale/alignment, not copied official wording, certification or publisher endorsement.

## Audit status

`v0.1.1` is an **audited pilot baseline**. Before publication, the candidate was reviewed in five directions: methodology, source fidelity, coverage/duplication, EN/LV localisation, and release-gate/evidence semantics. Findings and incorporated changes are recorded in `audits/2026-09-23-skeptical-audit.md`.

## Author

**Zigmārs Ancveirs** — technology leader, software engineer and independent cybersecurity researcher.

## PILOT-001 — Controlled release-gate validation

The [PILOT-001 reproducibility package](pilots/PILOT-001/README.md) exercises three **synthetic** `BLOCKED`, `CONDITIONAL` and `READY` scenarios in EN/LV, invalid-input rejection and CI exit modes. Its `READY` case demonstrates the tool's formal decision contract, **not** real product security or evidence authenticity.

## EVIDENCE-001 — Offline artifact binding

[EVIDENCE-001 foundation](pilots/EVIDENCE-001/README.md) optionally binds declared control evidence to regular Git blobs at an exact local product commit and verifies SHA-256. Its output reports separate EN/LV **structural** gates. A valid artifact hash is not evidence of the claim's truth, remote repository identity, reviewer approval or a secure product.

## INPUT-001 — Fail-closed assessment input

[INPUT-001 hardening](pilots/INPUT-001/README.md) rejects duplicate JSON keys recursively, non-standard JSON constants, invalid UTF-8, oversized assessment inputs and unknown top-level fields while preserving valid EN/LV gate behaviour. It closes the PILOT-001 `LIM-DUPLICATE-003` parser finding; it does not authenticate evidence or prove product security.

## VERIFICATION-001 — Signed review provenance

[VERIFICATION-001](pilots/VERIFICATION-001/README.md) binds a detached-SSH-signed verification record to the exact EVIDENCE-001 subject commit and manifest hash. It distinguishes signed assurance claims from established facts: even an `INDEPENDENTLY_VERIFIED` record does not by itself prove real-world identity, organizational independence, evidence truth, product security or release authorization.

## Licence

Documentation and assessment data: **CC BY 4.0**. Code and automation: **MIT**.
