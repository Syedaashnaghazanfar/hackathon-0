# Feature Specification: Bronze Tier AI Employee

**Feature Branch**: `001-bronze-ai-employee`
**Created**: 2026-01-13
**Status**: Draft
**Input**: User description: "Build “My AI Employee” (Hackathon Zero) — Bronze Tier only. Build a local-first Personal AI Employee where an Obsidian vault is the single source of truth for tasks and status. A Python filesystem watcher creates action-item Markdown files in `Needs_Action/`. Claude Code processes those items via Agent Skills by reading `Company_Handbook.md`, creating plans (in `Plans/` when present), updating `Dashboard.md`, and moving processed items to `Done/`. Bronze constraints: no MCP servers and no external actions. Require pytest tests for watcher core logic and action-item formatting."

## Scope, Constraints, Non-Goals

### In scope
- Local-first Obsidian vault as the single source of truth.
- Required vault structure and required files.
- One filesystem watcher that converts dropped files into Markdown action items in `Needs_Action/`.
- A Claude Code skill-driven triage workflow that:
  - reads pending action items
  - applies `Company_Handbook.md` rules
  - creates a plan per action item
  - updates `Dashboard.md`
  - archives processed items to `Done/` (non-destructive; preserves YAML)
- Tests for watcher core logic and action-item formatting.

### Out of scope (Bronze)
- MCP servers or any external actions (sending emails, posting, payments).
- Multiple watchers (only one watcher required).
- Always-on process management (cron/pm2/etc.) beyond being able to run the watcher.

### Invariants
- MUST NOT delete user-authored vault content.
- MUST preserve YAML frontmatter when moving/processing Markdown files.
- Vault root convention: `My_AI_Employee/AI_Employee_Vault/`.


## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Watcher creates action items (Priority: P1)

As a user, I want a filesystem watcher to detect new files dropped into a configured folder and create a corresponding Markdown action item in my Obsidian vault’s `Needs_Action/` folder, so I never miss files that require attention.

**Why this priority**: This is the foundational “perception” capability. Without action items landing in `Needs_Action/`, there is nothing for Claude Code to process.

**Independent Test**: Can be tested by starting the watcher, dropping a new file into the watch folder, and confirming exactly one new `.md` action item appears in `My_AI_Employee/AI_Employee_Vault/Needs_Action/`.

**Acceptance Scenarios**:

1. **Given** the watcher is running and monitoring the watch folder, **When** a new file is created in the watch folder, **Then** the watcher creates exactly one Markdown action item file in `Needs_Action/` that includes a `type: file_drop` frontmatter field and references the original file path.
2. **Given** a file has already been processed, **When** the same file event is observed again (duplicate), **Then** no duplicate action item is created.
3. **Given** the watcher encounters a transient filesystem error, **When** it continues running, **Then** it logs the error and continues monitoring for subsequent files.

---

### User Story 2 - Claude triages action items (Priority: P2)

As a user, I want Claude Code to read pending action items from `Needs_Action/`, apply my operating rules from `Company_Handbook.md`, create a structured plan per item, update the vault dashboard, and archive the processed item to `Done/`, so I get actionable next steps and a reliable audit trail inside the vault.

**Why this priority**: This is the “reasoning” capability that turns raw inputs into usable plans and keeps the vault state consistent.

**Independent Test**: Can be tested by placing a valid action item in `Needs_Action/`, running the triage Agent Skill (e.g., `@needs-action-triage`), and confirming that a plan is created, the dashboard is updated, and the item is moved to `Done/` with YAML preserved.

**Acceptance Scenarios**:

1. **Given** a valid pending action item exists in `Needs_Action/`, **When** the triage skill is run, **Then** a plan file is created (in `Plans/` if it exists) and the action item is moved to `Done/` with frontmatter preserved and `status: processed` recorded.
2. **Given** `Company_Handbook.md` defines prioritization or handling rules, **When** a plan is created, **Then** the plan reflects those rules (e.g., priority or recommended next steps).
3. **Given** an action item is malformed (missing/invalid required frontmatter), **When** triage runs, **Then** the file remains in `Needs_Action/`, a dashboard warning is added, and triage continues with other items.

---

### User Story 3 - Dashboard shows system status (Priority: P3)

As a user, I want `Dashboard.md` to show current system status (counts of pending items, recent processing activity, and any warnings), so I can quickly see what needs attention and whether the AI employee loop is working.

**Why this priority**: Visibility is critical for trust and demoability, but it depends on having watcher output and triage output.

**Independent Test**: Can be tested by creating (or processing) a small number of action items and confirming `Dashboard.md` shows correct counts and a “recent activity” entry.

**Acceptance Scenarios**:

1. **Given** there are N markdown files in `Needs_Action/`, **When** the dashboard is updated, **Then** `Dashboard.md` displays the same pending count N.
2. **Given** at least one action item has been processed, **When** the dashboard is updated, **Then** it lists recent activity (e.g., latest processed item and timestamp).
3. **Given** a malformed action item is detected, **When** triage runs, **Then** the dashboard includes a warning entry referencing the malformed file.

---

### User Story 4 - Vault setup is consistent (Priority: P4)

As a user, I want the Obsidian vault to have a consistent required structure (`Inbox/`, `Needs_Action/`, `Done/`, plus `Dashboard.md` and `Company_Handbook.md`, and optionally `Plans/`), so that both the watcher and Claude Code can operate predictably.

**Why this priority**: This is essential setup, but it is a one-time step and depends on the overall feature being defined.

**Independent Test**: Can be tested by creating the vault at `My_AI_Employee/AI_Employee_Vault/` and verifying required paths exist.

**Acceptance Scenarios**:

1. **Given** a new vault is created at `My_AI_Employee/AI_Employee_Vault/`, **When** vault setup is complete, **Then** required folders and files exist and are readable.
2. **Given** a `Plans/` folder exists, **When** triage creates plans, **Then** plans are written under `Plans/`.

---

### User Story 5 - Action item format is standardized (Priority: P5)

As a user, I want action items produced by the watcher to follow a consistent frontmatter contract, so that triage can be reliable and non-destructive.

**Why this priority**: This reduces brittleness and makes the loop testable.

**Independent Test**: Can be tested by generating an action item and validating required YAML fields are present and parseable.

**Acceptance Scenarios**:

1. **Given** the watcher creates an action item, **When** the file is opened, **Then** it contains YAML frontmatter including `type`, `received`, and `status`.
2. **Given** `type: file_drop`, **When** the file is opened, **Then** it references the original file path (metadata-only link).


### Edge Cases

- **Vault path missing or unwritable**: Watcher and triage must log an error and continue running without deleting or overwriting user content.
- **`Needs_Action/` empty**: Triage should exit cleanly and optionally record “no pending items” in dashboard activity.
- **Malformed frontmatter**: Malformed items remain in `Needs_Action/`, a dashboard warning is added, and other items continue to be processed.
- **Duplicate events**: A previously processed dropped file must not generate a second action item.
- **Filename collisions**: Plan filenames must not overwrite existing plans; the system should generate unique plan filenames.
- **WSL / filesystem event flakiness**: If filesystem events are unreliable, watcher should still be able to operate via a polling fallback strategy (as a requirement outcome, not an implementation mandate).


## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Vault layout)**: System MUST use the vault root convention `My_AI_Employee/AI_Employee_Vault/` and support the required vault structure: `Inbox/`, `Needs_Action/`, `Done/`, plus `Dashboard.md` and `Company_Handbook.md`.
- **FR-002 (Plans folder behavior)**: If a `Plans/` folder exists in the vault, the system MUST write plan outputs under `Plans/`.
- **FR-003 (Single watcher)**: System MUST provide exactly one Bronze watcher: a filesystem watcher.
- **FR-004 (Action item creation)**: When a new file is dropped into the configured watch folder, the watcher MUST create exactly one Markdown action item under `Needs_Action/`.
- **FR-005 (Action item contract)**: Action items SHOULD include YAML frontmatter including `type`, `received` (ISO timestamp), and `status`.
- **FR-006 (File-drop metadata link)**: For file-drop items, the action item MUST reference the original dropped file path (metadata-only by default).
- **FR-007 (Duplicate prevention)**: The watcher MUST prevent duplicate action items for the same dropped file (e.g., by tracking IDs/hashes).
- **FR-008 (Watcher resilience)**: The watcher MUST log errors and continue running after recoverable failures.
- **FR-009 (Skills-driven processing)**: The action-item processing workflow MUST be implemented as a Claude Code Agent Skill stored under `.claude/skills/` (e.g., `@needs-action-triage`).
- **FR-010 (Triage read-set)**: The triage workflow MUST read pending items from `Needs_Action/` and MUST read `Company_Handbook.md` as operating rules when creating plans.
- **FR-011 (Plan structure)**: Each generated plan MUST include actionable checkbox steps and a clear done condition.
- **FR-012 (Dashboard updates)**: The triage workflow MUST update `Dashboard.md` to reflect counts, recent activity, and warnings.
- **FR-013 (Non-destructive archiving)**: For successfully processed items, the system MUST move the original action item to `Done/` without deleting user-authored content.
- **FR-014 (Frontmatter preservation)**: When moving/processing action items, the system MUST preserve YAML frontmatter.
- **FR-015 (Failure path for malformed items)**: If an action item is malformed (missing/invalid required frontmatter), the system MUST leave it in `Needs_Action/`, MUST add a dashboard warning, and MUST continue processing other items.
- **FR-016 (Secrets hygiene)**: The system MUST NOT commit secrets and MUST support configuration via `.env` (gitignored) when needed.
- **FR-017 (Testing)**: The project MUST include pytest tests that cover watcher core logic and action-item formatting.

### Key Entities

- **Vault**: The local Obsidian vault at `My_AI_Employee/AI_Employee_Vault/` containing folders and Markdown files used as the system’s source of truth.
- **Action Item**: A Markdown file in `Needs_Action/` representing work to be triaged, with frontmatter describing `type`, `received`, and `status` (at minimum).
- **Plan**: A Markdown file representing a concrete response to an action item, containing actionable checkbox steps and a done condition.
- **Dashboard**: A Markdown file (`Dashboard.md`) summarizing system status (counts, recent activity, warnings).
- **Company Handbook**: A Markdown file (`Company_Handbook.md`) containing rules that guide triage decisions.
- **Watcher**: A long-running process that detects new files in a watch folder and emits action items.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (Watcher output)**: Dropping a file into the watch folder results in a new `Needs_Action/*.md` action item being created within 60 seconds.
- **SC-002 (No duplicates)**: Re-processing the same dropped file does not create duplicate action items.
- **SC-003 (Triage produces artifacts)**: For a valid action item, triage creates a plan and updates `Dashboard.md`, and archives the item to `Done/`.
- **SC-004 (Malformed safety)**: For a malformed action item, triage does not delete or archive it; instead it remains in `Needs_Action/` and a dashboard warning is recorded.
- **SC-005 (Dashboard correctness)**: `Dashboard.md` pending count matches the number of Markdown files currently in `Needs_Action/`.
- **SC-006 (Demo loop)**: The end-to-end Bronze demo can be performed using: drop file → action item appears → triage run → plan + dashboard update → item in `Done/`.
- **SC-007 (Test gate)**: Pytest passes for watcher core logic and action-item formatting.
- **SC-008 (No external actions)**: During Bronze operation, the system does not perform external actions and does not require MCP servers.

## Assumptions

1. **Filesystem watcher only**: Bronze implementation uses only the filesystem watcher (not Gmail).
2. **Manual triage invocation**: The user triggers triage manually via Claude Code skill invocation.
3. **Plans folder is optional**: If `Plans/` does not exist, plans are written to a consistent alternative location defined in the spec (default to creating `Plans/`).
4. **Local-first vault**: The vault is stored locally and is writable by the watcher and triage.

## Non-Functional Requirements

- **Reliability**: Watcher and triage must handle errors without crashing and without creating duplicate processing.
- **Safety**: Operations within the vault must be non-destructive; do not delete user-authored content.
- **Security**: No secrets committed to git; redact sensitive values from logs.

