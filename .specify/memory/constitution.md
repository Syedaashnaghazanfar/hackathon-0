<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.0 (Bronze) → 2.0.0 (Silver)
Rationale: Adding Silver tier principles (HITL approval workflow, external actions via MCP, multi-watcher infrastructure, security & audit logging) while preserving all Bronze tier foundations.

Modified Principles:
  - Core Principle I: Extended scope to include Silver tier MCP servers and external actions
  - Core Principle V: Expanded security requirements for credential management and audit logging
  - Core Principle VI: Added FastMCP, Playwright, PM2/watchdog.py, multi-watcher support

Added Sections:
  - Core Principle VIII: Human-in-the-Loop (HITL) Approval Workflow
  - Core Principle IX: Security and Audit Logging
  - Core Principle X: Graceful Degradation and Error Handling
  - Artifact Conventions: Approval Request Contract (Pending_Approval folder)
  - Artifact Conventions: Audit Log Format (Logs folder)
  - Quality Gates: Silver Tier Acceptance Criteria
  - Vault Structure: Added /Pending_Approval/, /Approved/, /Rejected/, /Failed/, /Logs/

Removed Sections: None (Silver is additive to Bronze)

Template Consistency Status:
  ✅ .specify/templates/plan-template.md - reviewed, aligned with Silver constraints
  ✅ .specify/templates/spec-template.md - reviewed, aligned with Silver constraints
  ✅ .specify/templates/tasks-template.md - reviewed, aligned with Silver constraints
  ✅ .specify/templates/phr-template.prompt.md - no updates needed
  ✅ .specify/templates/adr-template.md - no updates needed

Follow-up TODOs:
  - Create ADRs for MCP server architecture, approval workflow thresholds, credential management strategy
  - Update all existing skills to reference Silver tier principles where applicable
  - Document multi-watcher health monitoring and restart strategies
  - Define auto-approve vs require-approval thresholds in Company_Handbook.md
-->

# My AI Employee (Hackathon Zero) Constitution

## Core Principles

### I. Local-First Personal AI Employee
This project builds a local-first Personal AI Employee using a three-layer architecture:
- **Memory/GUI**: Obsidian markdown vault as the persistent knowledge base and interface
- **Senses**: Python watcher script(s) for perception (filesystem, Gmail, WhatsApp Web, LinkedIn)
- **Reasoning**: Claude Code as the decision-making and planning engine
- **Behavior**: All AI automation expressed as Claude Code Agent Skills stored under `.claude/skills/`

**Bronze Tier Scope (Non-Negotiable)**:
- MUST produce an Obsidian vault containing `Dashboard.md` and `Company_Handbook.md`
- MUST maintain vault folders: `Inbox/`, `Needs_Action/`, `Done/` (optionally `Plans/`)
- MUST have one working watcher (filesystem watcher preferred) writing markdown action items into `Needs_Action/`
- Claude Code MUST read from and write to the vault (plan generation, dashboard updates, archiving to `Done/`)
- NO MCP servers and NO external actions in Bronze (no sending emails, no posting, no payments)

**Silver Tier Additions (Building on Bronze)**:
- MUST implement Human-in-the-Loop (HITL) approval workflow with vault folders: `/Pending_Approval/`, `/Approved/`, `/Rejected/`, `/Failed/`, `/Logs/`
- MUST support external actions via FastMCP servers (email, LinkedIn posting, browser automation)
- MUST implement multi-watcher infrastructure: Gmail (OAuth 2.0), WhatsApp Web (Playwright), LinkedIn, filesystem
- MUST enforce security-first credential management (`.env` only, never in vault/repo)
- MUST provide comprehensive audit logging with credential sanitization
- ALL external actions require human approval before execution (non-negotiable)

**Rationale**: Bronze tier demonstrates the core perception → reasoning → write-back loop without external dependencies. Silver tier extends this with real-world action execution under strict human oversight and security controls. Gold tier (future) may introduce multi-agent coordination and advanced automation.

### II. Vault Safety and Non-Destructive Operations
All operations on the Obsidian vault MUST follow safety-first principles:
- NEVER delete user content in the vault; prefer append or section updates
- ALWAYS preserve YAML frontmatter when moving or processing markdown items
- When updating existing notes, use section-targeted edits rather than full overwrites
- Archive completed items by moving to `Done/` rather than deletion
- Log all vault modifications for auditability

**Rationale**: The vault is the user's persistent memory. Data loss breaks trust and destroys value. All operations must be reversible or traceable.

### III. Human-as-Tool Principle
Claude Code MUST invoke the user for guidance in ambiguous situations:
- When vault root/path is ambiguous or not configured
- When an action could overwrite user-authored notes or conflict with existing content
- When multiple valid approaches exist for processing an action item
- When watcher detects unexpected file formats or malformed input
- When creating plans that may require user-specific context or preferences

**Rationale**: Automation without oversight creates brittle systems. Users are specialized tools for clarification, preferences, and domain knowledge that cannot be inferred.

### IV. Watcher Resilience and Idempotency
The filesystem watcher (and all future watchers) MUST be production-grade:
- Log errors and continue running; never crash on single malformed input
- Prevent duplicate processing using tracked IDs or content hashes
- Handle file system race conditions gracefully (file locked, deleted mid-read, etc.)
- Support graceful shutdown and resume without lost events
- Write action items atomically to prevent partial/corrupt markdown files

**Rationale**: Watchers are long-running processes. They must handle real-world filesystem chaos without supervision or restarts.

### V. Secret Management and Security
All credentials and sensitive configuration MUST follow secure practices:

**Bronze Tier Requirements**:
- NO secrets committed to repository (use `.env` files excluded via `.gitignore`)
- API keys for LLM providers MUST be environment variables
- Vault path configuration SHOULD be in `.env` with sensible defaults (e.g., `./AI_Employee_Vault/`)
- Personal identifiable information (PII) in dropped files MUST NOT be logged to console or committed
- File content sanitization before logging (redact emails, phone numbers, etc.)

**Silver Tier Additions**:
- ALL credentials (Gmail OAuth tokens, API keys, browser session cookies) MUST be stored in `.env` only
- NEVER store credentials in Obsidian vault or repository (even temporarily)
- Audit logs MUST sanitize credentials before writing (redact tokens, passwords, session IDs)
- MCP servers MUST validate credential presence at startup and fail gracefully if missing
- Dry-run mode (`DRY_RUN=true` in `.env`) for development/testing without executing real actions
- 90-day minimum retention for audit logs in `/Logs/` (YYYY-MM-DD.json format)
- Permission boundaries MUST be documented in `Company_Handbook.md` (auto-approve vs require-approval thresholds)

**Rationale**: Local-first does not mean insecure. Bronze tier handles user-generated content that may contain sensitive data. Silver tier adds external action execution, requiring enterprise-grade credential management and audit trails to prevent unauthorized access and enable compliance.

### VI. Technology Stack and Implementation Constraints

**Bronze Tier Requirements**:
- **Python**: 3.13+ (or latest available)
- **Package Management**: `uv` for dependency management and virtual environments
- **Testing**: `pytest` for all test suites
- **Vault Path Convention**: `hack-zero/AI_Employee_Vault/` (configurable via `.env`)
- **Minimal Dependencies**: Prefer standard library; justify external packages
- **Watcher Framework**: `watchdog` library for filesystem events

**Silver Tier Additions**:
- **MCP Framework**: FastMCP library with Pydantic v2 validation for MCP server tools
- **Browser Automation**: Playwright for WhatsApp Web scraping and browser-based actions (payments, form fills)
- **Process Management**: PM2 for production or custom `watchdog.py` for development (multi-watcher orchestration)
- **Multi-Watcher Support**:
  - Gmail watcher (OAuth 2.0 authentication via `google-auth` library)
  - WhatsApp Web watcher (Playwright browser automation)
  - LinkedIn watcher (API or Playwright, depending on rate limits)
  - Filesystem watcher (existing `watchdog` library)
- **Error Handling**: Exponential backoff with max 3 retries for external API calls
- **Health Monitoring**: Heartbeat logging every 60 seconds, auto-restart on crash (via PM2 or watchdog.py)

**Code Quality Standards** (applies to both Bronze and Silver):
- Prefer simple, minimal diffs; no unrelated refactors
- Type hints required for all function signatures
- Docstrings for public functions and classes
- Error messages must be actionable (include context and suggested fix)

**Rationale**: Consistency reduces cognitive load. Simple tools with clear conventions enable rapid iteration and easier debugging. Silver tier introduces production-grade external integrations requiring robust error handling and monitoring.

### VII. Test-Driven Development for Core Logic

**Bronze Tier Requirements**:
All core Bronze tier logic MUST have test coverage:
- **Required Tests**:
  - Watcher core logic (event detection, action item creation, duplicate prevention)
  - Action item markdown formatting (YAML frontmatter + body structure)
  - Vault safety operations (move, append, section update)
  - Plan generation formatting (Plan.md structure compliance)
- **Testing Strategy**:
  - Unit tests for pure functions (parsing, formatting, validation)
  - Integration tests for vault operations (use temporary test vault)
  - End-to-end smoke test (drop file → Needs_Action → process → Done/)
- **Linting/Formatting**:
  - Basic lint/format checks (keep consistent; no heavy tooling unless already in repo)
  - Pre-commit hooks optional but recommended

**Silver Tier Additions**:
- **MCP Server Testing**:
  - MUST test each MCP server independently (email, LinkedIn, browser automation) with mocked credentials
  - MUST verify Pydantic v2 schema validation for all tool inputs/outputs
  - MUST test error responses (invalid inputs, API failures, timeout scenarios)
- **Approval Workflow Testing**:
  - MUST test end-to-end flow: Needs_Action → Pending_Approval → Approved → execution → Done
  - MUST test rejection flow: Pending_Approval → Rejected (no execution)
  - MUST test orchestrator error handling: Approved → execution failure → Failed folder
- **Security Testing**:
  - MUST verify credential sanitization in audit logs (no plaintext tokens/passwords)
  - MUST test dry-run mode (`DRY_RUN=true`) prevents real external actions
  - MUST verify permission boundary enforcement (auto-approve vs require-approval)
- **Graceful Degradation Testing**:
  - MUST test component failure scenarios (watcher crash, MCP server unavailable, network timeout)
  - MUST verify system continues operating when non-critical components fail
  - MUST test retry logic (exponential backoff, max 3 retries)
- **End-to-End Demo**:
  - Silver tier acceptance requires full demo: watcher → Needs_Action → triage → Pending_Approval → approval → execution → audit log → Done
  - All Bronze tier tests MUST continue passing

**Rationale**: Tests are documentation and safety nets. Core watcher and vault operations are critical infrastructure; they must be reliable. Silver tier adds external actions and HITL workflows requiring exhaustive security, error handling, and integration testing.

### VIII. Human-in-the-Loop (HITL) Approval Workflow
ALL external actions (emails, posts, payments, API calls) MUST pass through human approval before execution:

**Approval Flow**:
1. **Triage** (`/needs-action-triage`): Claude processes items in `/Needs_Action/`, creates plans, identifies actions requiring approval
2. **Approval Request** (`/approval-workflow-manager`): Move action items to `/Pending_Approval/` with structured approval request metadata
3. **Human Decision**: User reviews `/Pending_Approval/` folder in Obsidian, moves items to `/Approved/` (execute) or `/Rejected/` (cancel)
4. **Execution** (`/mcp-executor`): Orchestrator watches `/Approved/`, executes via MCP servers, logs results, moves to `/Done/` or `/Failed/`

**Permission Boundaries**:
- **Auto-Approve** (optional, requires explicit configuration in `Company_Handbook.md`):
  - Read-only operations (fetch emails, list notifications)
  - Internal vault operations (plan generation, dashboard updates)
  - Low-risk actions below defined thresholds (e.g., emails to pre-approved contacts)
- **Require-Approval** (default for all external actions):
  - Sending emails or messages
  - Publishing posts to LinkedIn or social media
  - Financial transactions (payments, transfers)
  - Browser automation (form submissions, clicks)
  - API calls to external systems

**Rejection Handling**:
- Rejected items MUST be moved to `/Rejected/` with reason documented in frontmatter
- Orchestrator MUST NOT execute rejected actions (even if accidentally moved to `/Approved/`)
- Failed executions MUST be moved to `/Failed/` with error details logged

**Rationale**: External actions have real-world consequences (financial, reputational, legal). Human oversight prevents catastrophic errors from AI misunderstandings or hallucinations. HITL approval is non-negotiable in Silver tier.

### IX. Security and Audit Logging
ALL external action executions MUST be logged for compliance, debugging, and security auditing:

**Audit Log Format** (`/Logs/YYYY-MM-DD.json`):
```json
{
  "timestamp": "2026-01-18T14:30:00Z",
  "action_id": "2026-01-18_urgent_quarterly_report",
  "action_type": "send_email",
  "user": "human-approver-id",
  "ai_agent": "claude-code-sonnet-4.5",
  "approval_reason": "Quarterly report deadline",
  "execution_status": "success",
  "mcp_server": "email-server",
  "tool_name": "send_email",
  "tool_inputs_sanitized": {
    "to": "boss@company.com",
    "subject": "Q4 2025 Report",
    "body_preview": "Please find attached..."
  },
  "tool_output_sanitized": {
    "message_id": "msg_abc123",
    "status": "sent"
  },
  "error": null,
  "retry_count": 0
}
```

**Credential Sanitization**:
- MUST redact API keys, OAuth tokens, passwords, session cookies before logging
- MUST redact sensitive PII (credit card numbers, SSNs, medical records) from tool inputs/outputs
- Use placeholder text (e.g., `<REDACTED_TOKEN>`, `<REDACTED_CREDIT_CARD>`) in sanitized logs

**Retention Policy**:
- Minimum 90-day retention for audit logs
- Rotate logs daily (`YYYY-MM-DD.json` format)
- Archive logs older than 90 days (optional compression)

**Access Control**:
- Audit logs MUST NOT be committed to repository (add `/Logs/` to `.gitignore`)
- Logs stored in Obsidian vault `/Logs/` folder for easy access but excluded from git

**Rationale**: Audit logs enable compliance (SOC 2, GDPR), security incident response, and debugging. Credential sanitization prevents leaking secrets in logs. 90-day retention balances compliance needs with storage costs.

### X. Graceful Degradation and Error Handling
Silver tier systems MUST continue operating when non-critical components fail:

**Component Isolation**:
- Each watcher runs as independent process (Gmail, WhatsApp, LinkedIn, filesystem)
- Failure of one watcher MUST NOT crash other watchers or orchestrator
- MCP server failures MUST NOT prevent approval workflow from functioning

**Error Recovery Strategies**:
- **Retry Logic**: Exponential backoff (1s, 2s, 4s) with max 3 retries for transient failures (network timeout, rate limiting)
- **Dead Letter Queue**: Failed executions moved to `/Failed/` folder with error details, manual intervention required
- **Health Monitoring**: Each component logs heartbeat every 60 seconds, watchdog process restarts crashed components
- **Graceful Shutdown**: SIGTERM/SIGINT handlers ensure in-flight operations complete before shutdown

**Failure Modes**:
| Component | Failure Impact | Mitigation |
|-----------|---------------|------------|
| Gmail watcher | No new email action items | Filesystem/WhatsApp/LinkedIn watchers continue; manual email check fallback |
| MCP server (email) | Cannot execute email actions | Approval workflow continues; failed executions logged in `/Failed/` |
| Orchestrator | No execution of approved items | Watchers continue populating `/Needs_Action/`; restart orchestrator |
| Obsidian vault unavailable | Complete system halt | CRITICAL ERROR - vault is single source of truth, system cannot operate |

**Monitoring Requirements**:
- Log all component start/stop events with timestamps
- Log all retry attempts (reason, retry count, success/failure)
- Alert on repeated failures (3+ consecutive failures suggest systemic issue)

**Rationale**: Production systems experience failures (network outages, API rate limits, crashes). Graceful degradation ensures core functionality (perception, approval workflow) continues operating while isolated failures are contained and logged for manual intervention.

## Artifact Conventions

### Action Item Contract (Needs_Action)
Action items MUST be Markdown files stored under `Needs_Action/`.

**Required YAML Frontmatter** (minimum):
```yaml
type: email|file_drop|manual
received: 2026-01-13T10:30:00Z  # ISO 8601 timestamp
status: pending|processed
priority: high|medium|low|auto  # optional
```

**Optional Frontmatter Fields**:
- `source_id`: Unique identifier from watcher (hash or path)
- `from`: Email sender or file source
- `subject`: Email subject or file name
- `tags`: List of classification tags (e.g., `[invoice, urgent]`)

**Body Structure**:
```markdown
## Summary
[Brief description of what needs action]

## Details
[Full context, extracted content, or reference to source file]

## Suggested Actions
[Optional: watcher-generated suggestions or category]
```

**Rationale**: Consistent structure enables reliable parsing by Claude Code skills and supports future automation extensions.

### Plan Output Location
- Plans MUST be written to `Plans/` when that folder exists (recommended)
- If `Plans/` is not used, the chosen plan output location MUST be consistent and documented in the feature spec
- Plan filenames SHOULD follow format: `YYYY-MM-DD_ActionItemID_Plan.md`

**Rationale**: Centralized plans enable dashboard aggregation and historical tracking.

### Watcher File Handling Default
- **Default Behavior**: The watcher writes a Markdown action item that references the original dropped file path (metadata-only)
- **File Copying**: Copying dropped files into the vault is OPTIONAL and must be an explicit design choice documented in the plan (and ADR if it has long-term impact)

**Rationale**: Metadata-only approach keeps vault lightweight and avoids duplicate storage. Copying files into vault is a design trade-off (portability vs. storage bloat) requiring conscious decision.

### Approval Request Contract (Pending_Approval) - Silver Tier
Approval requests MUST be Markdown files stored under `/Pending_Approval/` following this structure:

**Required YAML Frontmatter**:
```yaml
type: approval_request
action_type: send_email|post_linkedin|browser_automation|api_call
created: 2026-01-18T14:00:00Z
deadline: 2026-01-18T18:00:00Z  # optional
priority: high|medium|low
requires_approval: true
original_item: "2026-01-18_urgent_quarterly_report.md"
mcp_server: "email-server"
tool_name: "send_email"
```

**Body Structure**:
```markdown
## Proposed Action
[Clear description of what will be executed]

## Justification
[Why this action is necessary, context from original request]

## Risk Assessment
- **Impact**: [financial, reputational, operational]
- **Reversibility**: [can this be undone if something goes wrong?]
- **Blast Radius**: [who/what is affected?]

## Execution Details
**MCP Server**: email-server
**Tool**: send_email
**Parameters**:
- to: boss@company.com
- subject: "Q4 2025 Report"
- body: [preview or full content]
- attachments: [list or "none"]

## Approval Decision
**[ ] APPROVE** - Move this file to `/Approved/` folder
**[ ] REJECT** - Move this file to `/Rejected/` folder with reason in frontmatter
```

**Approval Process**:
- User reviews `/Pending_Approval/` folder in Obsidian
- To approve: move file to `/Approved/` (orchestrator executes)
- To reject: move file to `/Rejected/` and add `rejection_reason` to frontmatter

**Rationale**: Structured approval requests provide human reviewers with all context needed for informed decisions. Risk assessment forces AI to consider consequences before requesting approval.

### Audit Log Format (Logs) - Silver Tier
Audit logs MUST be stored as JSON files in `/Logs/` folder with daily rotation (`YYYY-MM-DD.json`):

**Log Entry Schema**:
```json
{
  "timestamp": "ISO 8601 timestamp",
  "action_id": "unique identifier from approval request",
  "action_type": "send_email|post_linkedin|browser_automation|api_call",
  "user": "human approver identifier",
  "ai_agent": "claude-code model version",
  "approval_reason": "reason from approval decision",
  "execution_status": "success|failure|pending",
  "mcp_server": "server name",
  "tool_name": "tool invoked",
  "tool_inputs_sanitized": {},
  "tool_output_sanitized": {},
  "error": "error message if failed, null otherwise",
  "retry_count": 0
}
```

**Sanitization Rules**:
- Redact API keys, OAuth tokens, passwords (`<REDACTED_TOKEN>`)
- Redact credit card numbers, SSNs (`<REDACTED_PII>`)
- Preserve action context (to/from, subject, timestamps) for debugging
- Include error messages and stack traces (sanitized)

**File Organization**:
- `/Logs/2026-01-18.json` - Single JSON array of all executions for that day
- Daily rotation prevents files from growing unbounded
- 90-day retention minimum for compliance

**Rationale**: Structured JSON logs enable automated analysis, compliance reporting, and security auditing. Daily rotation balances performance with queryability.

## Quality Gates

### Bronze Tier Acceptance Criteria
All Bronze tier deliverables MUST pass the end-to-end demo:

1. **Drop File** → Watcher detects file in drop folder
2. **Needs_Action Item** → Watcher creates markdown action item in `Needs_Action/`
3. **Claude Processes** → User invokes Claude Code skill (e.g., `/needs-action-triage`)
4. **Plan Generated** → Claude creates `Plan.md` in `Plans/`
5. **Dashboard Updated** → Claude updates `Dashboard.md` with new pending item
6. **Archive to Done** → After processing, item moved to `Done/` with completion metadata

**Verification**:
- Run `/bronze-demo-check` skill to validate full pipeline
- All steps must complete without manual intervention (beyond initial skill invocation)
- No errors logged by watcher or Claude Code skills
- Vault integrity preserved (no corrupted YAML, no deleted user content)

**Rationale**: The Bronze demo is the product. If this loop doesn't work reliably, nothing else matters.

### Silver Tier Acceptance Criteria
All Silver tier deliverables MUST pass the end-to-end demo while maintaining all Bronze tier functionality:

**Infrastructure Setup**:
1. **Vault Structure** - Folders exist: `/Pending_Approval/`, `/Approved/`, `/Rejected/`, `/Failed/`, `/Logs/`
2. **Multi-Watcher Running** - At least 2 watchers operational (filesystem + one of Gmail/WhatsApp/LinkedIn)
3. **MCP Servers Ready** - At least 1 MCP server functional (email or LinkedIn) with dry-run mode
4. **Orchestrator Active** - Watches `/Approved/` folder and executes via MCP servers

**End-to-End Flow**:
1. **Perception** - Watcher detects new input (email, message, or file) and creates action item in `/Needs_Action/`
2. **Triage** - `/needs-action-triage` processes item, generates plan, identifies external action required
3. **Approval Request** - `/approval-workflow-manager` creates structured request in `/Pending_Approval/`
4. **Human Review** - User moves approval request to `/Approved/` (or `/Rejected/` to cancel)
5. **Execution** - Orchestrator picks up approved item, calls MCP server tool, logs execution
6. **Audit Trail** - Execution logged in `/Logs/YYYY-MM-DD.json` with sanitized credentials
7. **Archival** - Completed action moved to `/Done/`, or `/Failed/` if execution error

**Verification Checklist**:
- [ ] All Bronze tier tests pass (filesystem watcher, vault operations, triage)
- [ ] Multi-watcher infrastructure running (2+ watchers operational)
- [ ] At least 1 MCP server tested independently (mocked credentials)
- [ ] Approval workflow end-to-end (Needs_Action → Pending_Approval → Approved → execution → Done)
- [ ] Rejection flow tested (Pending_Approval → Rejected, no execution)
- [ ] Audit logging verified (credentials sanitized, JSON schema valid)
- [ ] Dry-run mode tested (`DRY_RUN=true` prevents real external actions)
- [ ] Error handling tested (MCP server failure → `/Failed/` folder, retry logic)
- [ ] Graceful degradation verified (one watcher crash doesn't affect others)
- [ ] Security audit passed (no credentials in vault/repo, `.env` gitignored)

**Silver Tier Demo Scenario**:
Run `/multi-watcher-runner` to start watchers → Simulate email/message arrival → `/needs-action-triage` creates plan → `/approval-workflow-manager` requests approval → Move to `/Approved/` → Orchestrator executes (dry-run) → Verify audit log → Check `/Done/` folder

**Rationale**: Silver tier builds on Bronze with production-grade external action execution. HITL approval, security, and audit logging are non-negotiable. All Bronze functionality must continue working.

### Code Review Checklist
Before considering any implementation complete:
- [ ] Tests pass (`pytest` in backend, if applicable)
- [ ] No secrets or PII committed
- [ ] YAML frontmatter preserved in all vault operations
- [ ] Error handling includes actionable messages
- [ ] Changes align with constitution principles
- [ ] ADR created for significant architectural decisions
- [ ] PHR (Prompt History Record) created for implementation session

## Governance

### Amendment Process
- Constitution supersedes specs, plans, and tasks when there is conflict
- Amendments require:
  1. Documented rationale for change
  2. Version bump (MAJOR.MINOR.PATCH semantic versioning)
  3. Update to dependent templates and documentation
  4. Sync Impact Report (prepended as HTML comment)
- Version bump rules:
  - **MAJOR**: Backward-incompatible principle removals or redefinitions
  - **MINOR**: New principle/section added or materially expanded guidance
  - **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Architectural Decision Records
Significant architecture choices MUST be documented via ADR when:
- Multiple viable alternatives exist with meaningful trade-offs
- Decision has long-term impact on system structure or user experience
- Decision affects core Bronze tier deliverables (e.g., watcher file handling, vault organization)

**Examples requiring ADR**:
- Whether watcher copies dropped files into vault vs. metadata-only links
- Choice of watcher framework (watchdog vs. polling vs. inotify)
- Vault folder structure changes (e.g., adding new top-level folders)
- Authentication/encryption approach for future tiers

### Compliance and Enforcement
- All Claude Code skills MUST reference constitution principles in their documentation
- PRs and reviews MUST verify compliance with safety principles (II) and security standards (V)
- Complexity MUST be justified against YAGNI principles; prefer simple solutions
- Runtime development guidance for Bronze tier lives in `.claude/skills/` SKILL.md files

### Project Context
This constitution governs the "My AI Employee" project for **Hackathon Zero Bronze and Silver Tiers**. The project demonstrates AI-native task management using Obsidian + Claude Code + Python watchers, progressing from local perception-reasoning loops (Bronze) to production-ready external action execution with human oversight (Silver). Gold tier (future) may introduce multi-agent coordination, advanced automation, and proactive task initiation.

**Vault Path Convention**: `hack-zero/AI_Employee_Vault/`

**Tier Progression**:
- **Bronze (v1.0.0)**: Filesystem watcher → Needs_Action → triage → Plans → Done (no external actions)
- **Silver (v2.0.0)**: Multi-watcher (Gmail/WhatsApp/LinkedIn/filesystem) → HITL approval workflow → MCP execution → audit logging
- **Gold (future)**: Multi-agent orchestration, proactive task suggestions, advanced automation (TBD)

---

**Version**: 2.0.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-01-18
