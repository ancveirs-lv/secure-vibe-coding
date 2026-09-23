# Anti-AI-Slop — Secure Vibe Coding Baseline

> This is a release-readiness and evidence-gap instrument, not a certification, penetration test, compliance determination or guarantee of security.

Anti-AI-Slop is a project label for rejecting software changes that are accepted or deployed without sufficient understanding, constraints or evidence. It is not a claim that AI-generated code is inherently insecure.

## Response states

- `UNKNOWN` — Unknown: The current state cannot be established with reliable information or evidence.
- `CLAIMED` — Claimed: The practice is asserted, but there is no durable implementation or test evidence.
- `IMPLEMENTED` — Implemented: The practice is present in the product or workflow and there is observable implementation evidence.
- `VERIFIED` — Verified: A recent direct test, review or reproducible artefact supports the claim; structured input requires an evidence note.
- `NOT_APPLICABLE` — Not applicable: The control genuinely does not apply to this product or workflow; only allowed where the control permits it and a rationale is required.

## Controls

### Ownership and understanding

#### O01

A named human owns the release decision and remains accountable for AI-assisted changes.

**Recommended action:** Name the human release owner and record who can approve or reject security-sensitive changes.

**Release requirement:** `IMPLEMENTED` · blocking=`true` · N/A=no

**Evidence examples:** release owner in CODEOWNERS/change record

**Sources:** `nist_ssdf11`, `openssf_ai_instructions`

#### O02

The team can explain the deployed architecture, trust boundaries, data flows and external services without relying on the AI tool to reconstruct them.

**Recommended action:** Maintain a concise architecture/data-flow record covering entry points, storage, external services and trust boundaries.

**Release requirement:** `IMPLEMENTED` · blocking=`true` · N/A=no

**Evidence examples:** architecture/data-flow diagram or ADR

**Sources:** `nist_ssdf11`

#### O03

Plausible abuse cases and security-relevant trust assumptions have been identified before public release.

**Recommended action:** Write down the most important attacker goals, trust assumptions and failure modes; convert them into checks.

**Release requirement:** `IMPLEMENTED` · blocking=`false` · N/A=no

**Evidence examples:** threat/abuse-case note linked to tests

**Sources:** `nist_ssdf11`, `owasp_asvs_500`

#### O04

AI-assisted edits are reviewed as diffs, including unexpected or out-of-scope changes.

**Recommended action:** Require review of the complete diff and reject unrelated generated changes instead of accepting a large opaque patch.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=no

**Evidence examples:** review record referencing the complete diff

**Sources:** `owasp_secure_coding_ai`, `openssf_ai_instructions`

### Authentication and authorization

#### A01

Authentication uses established mechanisms and security-sensitive identity flows are not improvised by generated code.

**Recommended action:** Use maintained authentication libraries or platform mechanisms and review login, recovery and session flows.

**Release requirement:** `IMPLEMENTED` · blocking=`true` · N/A=no

**Evidence examples:** authentication design/config review

**Sources:** `owasp_asvs_500`, `openssf_ai_instructions`

#### A02

Authorization is enforced server-side for every protected action and object, not only in the UI.

**Recommended action:** Add server-side permission checks at the resource/action boundary and test denied paths.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=no

**Evidence examples:** negative authorization tests

**Sources:** `owasp_asvs_500`

#### A03

Cross-user, cross-tenant and object-level isolation has been tested with negative cases where relevant.

**Recommended action:** Test whether one identity can read or change another identity's objects by modifying identifiers, routes or API calls.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** IDOR/BOLA/tenant-isolation test evidence

**Sources:** `owasp_asvs_500`

#### A04

Administrative, recovery and other high-impact functions have stronger access boundaries and are not protected by obscurity.

**Recommended action:** Inventory privileged functions, require explicit authorization and verify recovery/admin flows separately.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** privileged-route inventory and negative tests

**Sources:** `owasp_asvs_500`

### Data and secrets

#### D01

Secrets are not hard-coded, committed, shipped to clients or pasted into AI prompts/context; production credentials are stored and scoped appropriately.

**Recommended action:** Move secrets to an appropriate secret store, rotate exposed credentials and add repository/context exclusions.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=no

**Evidence examples:** secret scan plus secret-store/config evidence

**Sources:** `owasp_secure_coding_ai`, `openssf_ai_instructions`

#### D02

AI tools receive only the minimum project context needed and sensitive files are excluded from tool context where supported.

**Recommended action:** Configure AI-tool ignore/exclusion rules and avoid exposing keys, private data, production dumps or regulated content to unnecessary context.

**Release requirement:** `IMPLEMENTED` · blocking=`true` · N/A=yes

**Evidence examples:** AI context exclusion configuration

**Sources:** `owasp_secure_coding_ai`

#### D03

Sensitive data is minimized, protected in transit and storage, and excluded or redacted from logs where appropriate.

**Recommended action:** Document sensitive data, remove unnecessary collection and verify encryption, access and logging behaviour.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** data inventory plus storage/log verification

**Sources:** `owasp_asvs_500`, `openssf_ai_instructions`

#### D04

Important persistent data has a recovery path that has been tested, and destructive operations have defined safeguards.

**Recommended action:** Test restoration of important data and define confirmation/rollback or equivalent safeguards for destructive actions.

**Release requirement:** `VERIFIED` · blocking=`false` · N/A=yes

**Evidence examples:** restore test or destructive-action recovery evidence

**Sources:** `nist_ssdf11`

### Dependencies and supply chain

#### S01

Every AI-suggested external package is verified to exist in the intended registry and is reviewed before installation.

**Recommended action:** Verify package name, registry, maintainer/history and project relevance before adding it.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** dependency-review record or allowlist entry

**Sources:** `owasp_secure_coding_ai`

#### S02

Dependency versions are reproducibly resolved and known-vulnerability checks run before release.

**Recommended action:** Commit lockfiles or equivalent resolution data and run ecosystem-appropriate vulnerability checks in CI.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** lockfile plus dependency-audit result

**Sources:** `owasp_secure_coding_ai`, `nist_ssdf11`

#### S03

Dependencies are minimized and material new dependencies have a recorded purpose, licence and maintenance/provenance check.

**Recommended action:** Remove unnecessary packages and record why material dependencies are trusted and needed.

**Release requirement:** `IMPLEMENTED` · blocking=`false` · N/A=yes

**Evidence examples:** dependency inventory/review note

**Sources:** `nist_ssdf11`, `openssf_ai_instructions`

#### S04

CI/CD actions, build plugins and automation dependencies are pinned or otherwise controlled, and their privileges are minimized.

**Recommended action:** Review pipeline dependencies and permissions; pin immutable versions where practical and restrict tokens.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** CI configuration and permission review

**Sources:** `nist_ssdf11`, `owasp_secure_coding_ai`

### Inputs and business logic

#### I01

Untrusted input is validated to expected shape and length, and output/query contexts use safe encoding or parameterization.

**Recommended action:** Define input contracts and use framework-safe rendering, parameterized queries and context-appropriate encoding.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** injection/validation tests

**Sources:** `owasp_asvs_500`, `openssf_ai_instructions`

#### I02

High-risk parsers and sinks such as URLs, files, shell commands and server-side fetches have explicit validation and isolation.

**Recommended action:** Review file upload, SSRF, command execution and parser boundaries; remove unsafe generic execution paths.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** SSRF/file/command negative tests

**Sources:** `owasp_asvs_500`

#### I03

Security- and money-relevant business invariants are enforced on the server and tested against replay, concurrency or identifier tampering where relevant.

**Recommended action:** Encode critical invariants in server-side logic and add negative/idempotency/concurrency tests for high-impact state transitions.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** business-logic negative tests

**Sources:** `owasp_asvs_500`

#### I04

Externally reachable operations have appropriate resource limits, rate controls, timeouts and fail-safe behaviour.

**Recommended action:** Set bounded request/body/job limits, rate controls and timeouts for abuse-prone or expensive operations.

**Release requirement:** `IMPLEMENTED` · blocking=`false` · N/A=yes

**Evidence examples:** runtime limit configuration

**Sources:** `owasp_asvs_500`

### AI agents, MCP and tool access

#### G01

AI coding agents run with the minimum filesystem, shell, network, cloud and repository privileges needed for the task.

**Recommended action:** Separate development from production credentials and sandbox or scope agent access to the current task.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** agent permission/sandbox configuration

**Sources:** `owasp_secure_coding_ai`, `owasp_agentic_top10_2026`

#### G02

Destructive, credential-sensitive and security-boundary changes require deliberate human approval rather than blanket auto-accept.

**Recommended action:** Disable unrestricted auto-approval and define operations that always require human confirmation.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** agent approval-policy configuration

**Sources:** `owasp_secure_coding_ai`, `owasp_agentic_top10_2026`

#### G03

MCP servers and other connected tools are explicitly trusted, minimally permissioned and use scoped credentials.

**Recommended action:** Maintain a tool allowlist, review each tool's capabilities and restrict credentials and network reach.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** MCP/tool inventory and permission review

**Sources:** `owasp_secure_coding_ai`, `owasp_agentic_top10_2026`

#### G04

Issues, pull requests, repository files, logs and fetched web content are treated as untrusted instructions when consumed by an AI agent.

**Recommended action:** Review untrusted context before agent use, limit context/egress and inspect resulting changes for indirect prompt injection effects.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** agent-context review or constrained-context evidence

**Sources:** `owasp_secure_coding_ai`, `owasp_agentic_top10_2026`

### Deployment and runtime

#### P01

Production configuration is hardened: debug/test features and default credentials are disabled or removed.

**Recommended action:** Create a repeatable production-hardening checklist and verify effective runtime configuration.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** effective production configuration check

**Sources:** `owasp_asvs_500`

#### P02

External exposure is intentional: TLS, cookies, CORS, security headers, origins and public endpoints are configured to the product's needs.

**Recommended action:** Inventory internet-facing endpoints and verify transport/browser/security-boundary settings instead of accepting generated defaults.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** external endpoint and security-header/config verification

**Sources:** `owasp_asvs_500`

#### P03

Databases, object storage, queues and administrative services are not publicly exposed unless explicitly required and protected.

**Recommended action:** Verify network exposure, cloud IAM and service credentials from the deployed environment.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=yes

**Evidence examples:** deployed network/IAM exposure evidence

**Sources:** `owasp_asvs_500`, `nist_ssdf11`

#### P04

Operational logging, alerting, rollback and incident ownership exist for material failures after release.

**Recommended action:** Define what will be monitored, who receives alerts, how a bad release is rolled back and who owns incident decisions.

**Release requirement:** `VERIFIED` · blocking=`false` · N/A=no

**Evidence examples:** monitor/alert/rollback runbook or test

**Sources:** `nist_ssdf11`, `owasp_asvs_500`

### Release evidence

#### R01

Security-critical paths have automated positive and negative tests, including denial cases rather than only happy paths.

**Recommended action:** Add tests that prove unauthorized, malformed and unsafe actions fail as intended.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=no

**Evidence examples:** CI test run with named negative security tests

**Sources:** `openssf_ai_instructions`, `owasp_asvs_500`

#### R02

Security-sensitive AI-generated changes receive review that is independent of the same generation step.

**Recommended action:** Use a human reviewer and/or deterministic security tooling; do not treat the generating model's self-review as sole assurance.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=no

**Evidence examples:** human review plus tool output

**Sources:** `openssf_ai_instructions`, `nist_ssdf11`

#### R03

Secret, dependency and code/configuration security checks run before release, and suppressions have an owner and rationale.

**Recommended action:** Run appropriate automated checks in CI and record why any security finding is suppressed or accepted.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=no

**Evidence examples:** CI security-check results and exception record

**Sources:** `nist_ssdf11`, `openssf_ai_instructions`

#### R04

The release can be tied to a commit, build/configuration state, dependency set, known gaps and a reproducible gate result.

**Recommended action:** Produce a small release evidence bundle so a later reviewer can reconstruct what was shipped and why it passed the gate.

**Release requirement:** `VERIFIED` · blocking=`true` · N/A=no

**Evidence examples:** release manifest with commit/build/gate evidence

**Sources:** `nist_ssdf11`


## Anti-AI-Slop indicators

- `SLOP01` — AI approval is treated as proof that the code is secure.
- `SLOP02` — Nobody can explain the authentication or authorization flow without asking the AI again.
- `SLOP03` — Tests cover generated happy paths but not denied or malicious cases.
- `SLOP04` — A package was installed because the AI named it, without registry or maintainer verification.
- `SLOP05` — A security warning was removed by disabling the check rather than fixing or accepting the risk explicitly.
- `SLOP06` — Client-side hiding or route secrecy is used as authorization.
- `SLOP07` — Production secrets or dumps are exposed to the coding agent's context.
- `SLOP08` — The coding agent has blanket shell, network, cloud or production privileges for routine tasks.
- `SLOP09` — Untrusted issue, PR, log or web content is fed directly to an agent that can act on the repository.
- `SLOP10` — CORS, storage, database or network exposure was widened until the application started working.
- `SLOP11` — A large AI-generated diff is merged without understanding unrelated changes.
- `SLOP12` — The same AI generation loop is the only reviewer and test author for security-critical code.
- `SLOP13` — No one knows which version/configuration was actually deployed.
- `SLOP14` — There is no tested rollback or recovery path for a bad release or destructive data change.
- `SLOP15` — Security findings are suppressed without a named owner and rationale.
- `SLOP16` — The product is public even though critical controls remain UNKNOWN or merely CLAIMED.
