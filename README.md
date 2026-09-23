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

## Licence

Documentation and assessment data: **CC BY 4.0**. Code and automation: **MIT**.
