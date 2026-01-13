<!--
SYNC IMPACT REPORT
==================
Version Change: None (initial creation) → 1.0.0
Rationale: Initial constitution for Hackathon Zero Bronze tier project.

Modified Principles: N/A (new constitution)
Added Sections:
  - Core Principles (7 principles)
  - Artifact Conventions
  - Quality Gates
  - Governance

Removed Sections: N/A (initial creation)

Template Consistency Status:
  ✅ .specify/templates/plan-template.md - reviewed, aligned with Bronze constraints
  ✅ .specify/templates/spec-template.md - reviewed, aligned with Bronze constraints
  ✅ .specify/templates/tasks-template.md - reviewed, aligned with Bronze constraints
  ✅ .specify/templates/phr-template.prompt.md - no updates needed
  ✅ .specify/templates/adr-template.md - no updates needed

Follow-up TODOs: None
-->

# My AI Employee (Hackathon Zero) Constitution

## Core Principles

### I. Local-First Personal AI Employee
This project builds a local-first Personal AI Employee using a three-layer architecture:
- **Memory/GUI**: Obsidian markdown vault as the persistent knowledge base and interface
- **Senses**: Python watcher script(s) for perception (starting with filesystem watcher)
- **Reasoning**: Claude Code as the decision-making and planning engine
- **Behavior**: All AI automation expressed as Claude Code Agent Skills stored under `.claude/skills/`

**Bronze Tier Scope (Non-Negotiable)**:
- MUST produce an Obsidian vault containing `Dashboard.md` and `Company_Handbook.md`
- MUST maintain vault folders: `Inbox/`, `Needs_Action/`, `Done/` (optionally `Plans/`)
- MUST have one working watcher (filesystem watcher preferred) writing markdown action items into `Needs_Action/`
- Claude Code MUST read from and write to the vault (plan generation, dashboard updates, archiving to `Done/`)
- NO MCP servers and NO external actions in Bronze (no sending emails, no posting, no payments)

**Rationale**: Bronze tier demonstrates the core perception → reasoning → write-back loop without external dependencies. External actions and integrations are deferred to Silver/Gold tiers.

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
- NO secrets committed to repository (use `.env` files excluded via `.gitignore`)
- API keys for LLM providers MUST be environment variables
- Vault path configuration SHOULD be in `.env` with sensible defaults (e.g., `./AI_Employee_Vault/`)
- Personal identifiable information (PII) in dropped files MUST NOT be logged to console or committed
- File content sanitization before logging (redact emails, phone numbers, etc.)

**Rationale**: Local-first does not mean insecure. Bronze tier handles user-generated content that may contain sensitive data. Protect it.

### VI. Technology Stack and Implementation Constraints
Bronze tier implementation MUST use:
- **Python**: 3.13+ (or latest available)
- **Package Management**: `uv` for dependency management and virtual environments
- **Testing**: `pytest` for all test suites
- **Vault Path Convention**: `hack-zero/AI_Employee_Vault/` (configurable via `.env`)
- **Minimal Dependencies**: Prefer standard library; justify external packages
- **Watcher Framework**: `watchdog` library for filesystem events

**Code Quality Standards**:
- Prefer simple, minimal diffs; no unrelated refactors
- Type hints required for all function signatures
- Docstrings for public functions and classes
- Error messages must be actionable (include context and suggested fix)

**Rationale**: Consistency reduces cognitive load. Simple tools with clear conventions enable rapid iteration and easier debugging.

### VII. Test-Driven Development for Core Logic
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

**Rationale**: Tests are documentation and safety nets. Core watcher and vault operations are critical infrastructure; they must be reliable.

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
This constitution governs the "My AI Employee" project for **Hackathon Zero Bronze Tier**. The project demonstrates AI-native task management using Obsidian + Claude Code + Python watchers. Silver and Gold tiers (external actions, MCP integrations, advanced workflows) are out of scope and may require constitutional amendments.

**Vault Path Convention**: `hack-zero/AI_Employee_Vault/`

---

**Version**: 1.0.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-01-13
