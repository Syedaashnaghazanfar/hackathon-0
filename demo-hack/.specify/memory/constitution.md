<!--
Sync Impact Report

- Version change: 1.0.0 → 2.0.0
- Modified principles:
  - Principle I: "Bronze-First Scope" → "Bronze-First, Silver-Second Scope" (expanded)
  - Principle II: "Local-First Vault as Source of Truth" → expanded with Silver folders
  - Principle V: "Secure Configuration and Secrets Hygiene" → expanded with audit logging
- Added sections:
  - Principle VII: Human-in-the-Loop (HITL) Approval Workflow
  - Principle VIII: Comprehensive Audit Logging
  - Principle IX: Graceful Degradation and Error Recovery
  - Technology & Tooling: Added FastMCP, Playwright, PM2
  - Artifact Conventions (Silver): Approval requests, audit logs, orchestrator contract
- Removed sections: None
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (no changes needed - constitution check is generic)
  - ✅ .specify/templates/spec-template.md (no changes needed - requirements remain technology-agnostic)
  - ✅ .specify/templates/tasks-template.md (no changes needed - task structure remains valid)
- Deferred TODOs: None
- Rationale: MAJOR version bump (1.0.0 → 2.0.0) because Silver tier adds new non-negotiable principles (HITL, audit logging, security boundaries) and mandatory vault structure, representing a significant project milestone. Bronze tier principles remain valid and unchanged.
-->

# My AI Employee (Hackathon Zero) Constitution

## Core Principles

### I. Bronze-First, Silver-Second Scope (NON-NEGOTIABLE)
Build Bronze tier first, then extend to Silver tier.

**Bronze Tier (Foundation)**:
- MUST implement only Bronze deliverables initially: Obsidian vault, one watcher, Claude vault I/O, and skills.
- MUST NOT introduce MCP servers or external actions in Bronze (no email sending, posting, payments).
- SHOULD allow a `Plans/` folder even though only `Inbox/`, `Needs_Action/`, and `Done/` are required.

**Silver Tier (Extension)**:
- MUST implement Human-in-the-Loop (HITL) approval workflow for all external actions.
- MUST add multiple watchers: Gmail (OAuth 2.0), WhatsApp Web (Playwright), LinkedIn, filesystem.
- MUST implement MCP servers for external actions: email (Gmail API + SMTP), LinkedIn, browser automation.
- MUST implement orchestrator.py that watches `/Approved/` folder and executes actions via MCP servers.
- Silver tier is ADDITIVE to Bronze; Bronze tier remains valid and operational.

### II. Local-First Vault as Source of Truth (NON-NEGOTIABLE)
Treat the Obsidian vault as the single source of truth.

**Bronze Tier Structure**:
- MUST store operational state and artifacts in local markdown inside the vault.
- MUST keep the required vault structure:
  - `Inbox/`
  - `Needs_Action/`
  - `Done/`
  - `Dashboard.md`
  - `Company_Handbook.md`
- MUST use the repo vault path convention: `My_AI_Employee/AI_Employee_Vault/`.

**Silver Tier Structure (Additions)**:
- MUST add HITL approval folders:
  - `Pending_Approval/` - Actions awaiting human decision
  - `Approved/` - Actions approved for execution
  - `Rejected/` - Actions rejected by human
  - `Failed/` - Actions that failed execution
  - `Logs/` - Audit logs in JSON format (YYYY-MM-DD.json)
- Approval workflow: `Needs_Action` → `Pending_Approval` → `Approved` → execution → `Done` or `Failed`

### III. Agent Skills for All AI Behavior (NON-NEGOTIABLE)
Express all AI behavior as Claude Code Agent Skills.

- MUST implement AI workflows via skills under `.claude/skills/`.
- MUST be able to run all automation via Claude Code prompts invoking skills.
- MUST avoid hidden manual steps other than starting watcher processes and MCP servers.

### IV. Vault Safety and Non-Destructive Operations (NON-NEGOTIABLE)
Prevent accidental data loss in a local-first vault.

- MUST NOT delete user-authored vault content.
- MUST preserve YAML frontmatter when moving/processing markdown action items.
- SHOULD prefer append/section updates over full-file rewrites (especially for `Dashboard.md`).
- MUST ask for clarification when the vault root is ambiguous or when an edit risks overwriting user notes.

### V. Secure Configuration and Secrets Hygiene (NON-NEGOTIABLE)
Keep credentials out of git and out of the vault.

**Bronze Tier**:
- MUST NOT commit secrets.
- MUST store credentials/configuration in `.env` (gitignored) or OS secret stores.
- SHOULD redact sensitive values from logs and example files.

**Silver Tier (Additions)**:
- MUST sanitize credentials in audit logs (redact API keys, tokens, passwords, credit card numbers, PII).
- MUST implement dry-run mode (DRY_RUN=true) for development and testing.
- MUST define permission boundaries: which actions auto-approve vs require human approval.
- MUST retain audit logs for minimum 90 days.

### VI. Testable, Minimal, Reliable Implementation
Keep changes small, verifiable, and resilient.

**Bronze Tier**:
- MUST prefer minimal diffs and avoid unrelated refactors.
- MUST make the watcher resilient: log errors, continue running, and prevent duplicates (tracked IDs/hashes).
- SHOULD provide deterministic end-to-end validation steps for Bronze.

**Silver Tier (Additions)**:
- MUST test all MCP servers independently (email, LinkedIn, browser automation).
- MUST test approval workflow end-to-end (Needs_Action → Pending_Approval → Approved → execution → Done).
- MUST test error handling and retry logic (exponential backoff, max 3 retries).
- MUST test credential sanitization in audit logs.
- MUST test graceful degradation when components fail.
- All Bronze tier tests must continue passing.

### VII. Human-in-the-Loop (HITL) Approval Workflow (NON-NEGOTIABLE - Silver Tier)
All external actions require human approval before execution.

- MUST route external/sensitive actions to `/Pending_Approval/` folder.
- MUST wait for human to move file to `/Approved/` before execution.
- MUST support rejection by moving to `/Rejected/` folder.
- Approval request format MUST include:
  - YAML frontmatter: type, action_type, requires_approval, status, priority, created_at
  - Body: requested action, why approval needed, rules applied from Company_Handbook.md, recommendation
- Orchestrator.py MUST watch `/Approved/` folder and execute via MCP servers.
- MUST move executed items to `/Done/` (success) or `/Failed/` (error) with execution results.
- Permission boundaries define auto-approve thresholds (e.g., emails to known contacts, payments < $50 recurring).

### VIII. Comprehensive Audit Logging (NON-NEGOTIABLE - Silver Tier)
Log all external actions with who/what/when/why/result.

- MUST log ALL external actions to `/Logs/YYYY-MM-DD.json` in JSONL format (one JSON object per line).
- Log entry MUST include: timestamp (ISO8601), action_type, actor, target, approval_status, approved_by, result.
- MUST sanitize credentials: API keys, tokens, passwords, credit card numbers (show last 4 digits only), PII.
- MUST retain audit logs for minimum 90 days.
- Logs are write-only and immutable during retention period.
- MUST support audit trail queries: by action type, by status, by actor, by date range.

### IX. Graceful Degradation and Error Recovery (NON-NEGOTIABLE - Silver Tier)
System continues operating when components fail.

- MUST implement retry logic with exponential backoff (max 3 retries: 1s → 5s → 10s → 30s).
- MUST implement graceful degradation:
  - Gmail API down: queue emails locally, process when restored
  - Banking API timeout: NEVER auto-retry payments, require fresh approval
  - Claude Code unavailable: watchers continue collecting, queue grows for later processing
  - Obsidian vault locked: write to temporary folder, sync when available
- MUST implement watchdog process to monitor and restart critical processes (or use PM2).
- MUST implement dead-letter queue for failed actions after max retries.
- MUST notify human on critical errors (authentication failures, system crashes).

## Project Guardrails

### Technology & Tooling

**Bronze Tier**:
- Python: 3.13+ (or latest available)
- Package manager: uv
- Tests: pytest
- Obsidian: vault of markdown files
- Claude Code: used as the terminal-based reasoning and write-back engine

**Silver Tier (Additions)**:
- FastMCP: library for MCP servers with Pydantic v2 validation
- Playwright: browser automation for WhatsApp Web and payment forms
- PM2: process management (recommended) OR custom watchdog.py for health monitoring
- Multiple watchers: Gmail (OAuth 2.0), WhatsApp Web, LinkedIn, filesystem

### Constraints

**Bronze Tier**:
- Bronze tier only: no MCP servers and no external actions.
- Path convention: `My_AI_Employee/AI_Employee_Vault/` is the default vault root.

**Silver Tier (Additions)**:
- All external actions MUST go through HITL approval workflow (no exceptions without explicit ADR).
- Orchestrator.py location: `My_AI_Employee/orchestrator.py`
- Watchers location: `My_AI_Employee/watchers/`
- MCP servers location: `My_AI_Employee/mcp_servers/` or `.claude/skills/mcp-executor/scripts/`
- Security and audit logging requirements are NON-NEGOTIABLE.

## Workflow & Quality Gates

**Bronze Tier**:
- MUST keep the workflow demonstrable end-to-end:
  - drop file → `Needs_Action` item → Claude processes → plan + dashboard update → item moved to `Done/`
- MUST add tests for watcher core logic and action-item formatting.
- SHOULD keep formatting consistent; avoid heavy tooling unless already present in the repo.

**Silver Tier (Additions)**:
- MUST demonstrate Silver tier end-to-end workflow:
  - Watcher detects external action → creates item in `Needs_Action/`
  - Triage skill determines approval needed → creates request in `Pending_Approval/`
  - Human approves → moves to `Approved/`
  - Orchestrator.py executes via MCP server → moves to `Done/` with result
  - Audit log entry created in `/Logs/YYYY-MM-DD.json`
- All Bronze tier workflows must continue functioning.

### Artifact Conventions (Bronze)

#### Action Item Contract (Needs_Action)

- Action items MUST be Markdown files stored under `Needs_Action/`.
- Action items SHOULD include YAML frontmatter with (at minimum):
  - `type`: `email|file_drop|manual`
  - `received`: ISO timestamp
  - `status`: `pending|processed`
  - `priority`: `high|medium|low|auto` (optional)
  - optional: `source_id`, `from`, `subject`

#### Plan Output Location

- Plans MUST be written to `Plans/` when that folder exists (recommended).
- If `Plans/` is not used, the chosen plan output location MUST be consistent and documented in the feature spec.

#### Watcher File Handling Default

- Default behavior: the watcher writes a Markdown action item that references the original dropped file path (metadata-only).
- Copying dropped files into the vault is OPTIONAL and must be an explicit design choice documented in the plan (and ADR if it has long-term impact).

### Artifact Conventions (Silver)

#### Approval Request Contract (Pending_Approval)

- Approval requests MUST be Markdown files stored under `Pending_Approval/`.
- YAML frontmatter MUST include:
  - `type`: `approval_request`
  - `action_type`: `send_email|send_message|create_post|payment|system_change`
  - `requires_approval`: `true`
  - `status`: `pending|approved|rejected`
  - `priority`: `high|medium|low`
  - `created_at`: ISO timestamp
  - `approved_by`: null (filled by human)
  - `approved_at`: null (filled by human)
- Body MUST include: requested action, why approval needed, rules applied from Company_Handbook.md, recommendation.

#### Audit Log Entry Contract (Logs/)

- Audit logs MUST be stored as `/Logs/YYYY-MM-DD.json` in JSONL format (one JSON object per line).
- Each entry MUST include: timestamp, action_type, actor, target, approval_status, approved_by, result.
- MUST sanitize: API keys (show first 4 chars + ***), tokens (redact entirely), passwords (redact entirely), credit card numbers (show last 4 digits only), PII (truncate emails as user@*****.com).
- Retention: 90 days minimum, then archive for 2 years for compliance.

#### Orchestrator.py Contract

- MUST watch `/Approved/` folder with configurable check interval (default 5 seconds).
- MUST route actions to appropriate MCP server based on action_type field.
- MUST implement retry logic (max 3 attempts with exponential backoff: 25s, 2h, 8h).
- MUST move successful executions to `/Done/` with results in frontmatter.
- MUST move failed executions to `/Failed/` with error details in frontmatter.
- MUST log all executions to audit trail via audit-logger skill.

## Governance

- This constitution supersedes feature specs, plans, and tasks when there is conflict.
- Amendments MUST update the version and record the rationale.
- Significant architecture choices with multiple viable options and long-term impact SHOULD be documented with an ADR.
  - Example: whether the watcher copies dropped files into the vault vs storing metadata-only links.
- Silver tier principles are ADDITIVE to Bronze tier; Bronze tier remains valid and operational.
- All external actions MUST go through HITL approval workflow (no exceptions without explicit ADR).
- Security and audit logging requirements are NON-NEGOTIABLE.

**Version**: 2.0.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-01-15
