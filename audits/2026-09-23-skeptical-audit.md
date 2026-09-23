# Five-direction skeptical audit — pre-publication v0.1.0

Date: 2026-09-23
Candidate: `secure-vibe-coding`
Decision: **PASS WITH INCORPORATED REMEDIATIONS — audited pilot baseline**

## 1. Methodology

### Skeptical finding
A generic checklist or percentage score would create false confidence. “Vibe coding” is informal and spans simple code completion through highly privileged coding agents.

### Remediation incorporated
- The project is a release gate, not a maturity score.
- Outcomes are `BLOCKED`, `CONDITIONAL`, or `READY`.
- Each control carries an explicit required evidence state.
- `VERIFIED` requires an evidence note.
- `NOT_APPLICABLE` is control-specific and requires a rationale.
- The README explicitly states that the instrument is not a certification, penetration test, compliance determination or guarantee of security.
- “Anti-AI-Slop” is defined as a project label, not a claim that AI-generated code is inherently insecure.

## 2. Source fidelity

### Skeptical finding
The candidate could overstate what individual sources establish:
- NIST SSDF 1.1 is a general SDLC framework, not an AI-coding standard.
- OWASP ASVS 5.0.0 is application-security verification guidance and is not universally applicable to every product.
- OWASP Agentic Top 10 applies to autonomous/tool-using agentic systems, not ordinary non-agentic code completion.
- OpenSSF AI assistant guidance is practical instruction guidance, not a certification standard.
- OpenSSF’s use of “AI-Slop” concerns low-quality AI-generated vulnerability reports and is narrower than this project’s label.

### Remediation incorporated
Every source in `data/sources.json` has explicit `scope` and `use` metadata. Agentic sources are mapped only to agent/tool controls. The OpenSSF AI-Slop reference is terminology context only.

## 3. Coverage and duplication

### Skeptical finding
A pure AI-risk list would miss the main reason weak AI-built products fail: ordinary application-security controls are skipped while attention is focused on “AI risks”.

### Remediation incorporated
The 32 controls deliberately combine:
- ordinary secure-software basics: authz, validation, secrets, dependencies, runtime hardening, testing and rollback;
- AI-development-specific risks: hallucinated packages, context leakage, indirect prompt injection, MCP/tool permissions and destructive auto-approval.

The repository does not duplicate the broader `cybersecurity-readiness-assessment`: this project evaluates evidence for a specific software release.

## 4. EN/LV localisation

### Skeptical finding
A Latvian translation could accidentally become a Latvia-specific standard, or technical English terms could be translated inconsistently.

### Remediation incorporated
- English remains the canonical global baseline.
- Latvian is a semantic localisation, not a separate control set.
- Stable control IDs, source refs, priorities and gate semantics are identical across languages.
- Common engineering terms such as `release gate`, `diff`, `MCP`, `rollback`, `CI/CD` and `NOT_APPLICABLE` remain visible where translation would reduce precision.
- Validation enforces EN/LV parity and blocks Latvia-specific text from the English dataset.

## 5. Release-gate and evidence semantics

### Skeptical finding
A developer could self-select `VERIFIED` or `NOT_APPLICABLE` to make the gate green without meaningful evidence. The same AI that generated code and tests could also “review” itself.

### Remediation incorporated
- `VERIFIED` requires a non-empty evidence note.
- `NOT_APPLICABLE` is rejected unless the control has `na_allowed=true`, and it requires a rationale.
- Release-blocking controls below their required state force `BLOCKED`.
- If blockers pass but non-blocking gaps remain, the result is `CONDITIONAL`, not `READY`.
- Independent review is a dedicated release-blocking control: self-review by the same generation loop is explicitly insufficient as sole assurance.
- The report contains gap details and no aggregate security score.

## Residual limitations

This v0.1.0 baseline is intentionally compact and cross-stack. It does not:
- replace a product-specific threat model, penetration test or architecture review;
- provide framework-specific controls for every cloud, mobile, desktop, embedded or AI runtime;
- prove regulatory compliance;
- quantify exploit likelihood;
- validate evidence automatically.

Future versions may add stack profiles, a machine-readable evidence schema, mappings to selected ASVS requirements, and product-security/CRA extensions without changing the core no-score release-gate model.

## Audit conclusion

The audited v0.1.0 candidate is suitable for public pilot use because its claims are bounded, source scopes are explicit, the release decision is evidence-based rather than score-based, and AI-specific risks are integrated with ordinary software-security fundamentals rather than replacing them.
