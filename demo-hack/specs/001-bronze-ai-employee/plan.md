# Implementation Plan: Bronze Tier AI Employee

**Branch**: `001-bronze-ai-employee` | **Date**: 2026-01-13 | **Spec**: `specs/001-bronze-ai-employee/spec.md`
**Input**: Feature specification from `specs/001-bronze-ai-employee/spec.md`

## Summary

Implement the Bronze-tier “My AI Employee” loop using a local Obsidian vault as the source of truth: a filesystem watcher creates Markdown action items in `Needs_Action/`, and Claude Code processes those items via Agent Skills to create per-item plans, update `Dashboard.md`, and archive processed items to `Done/`.

Key design decisions (see `specs/001-bronze-ai-employee/research.md`):
- Filesystem watching via `watchdog` with a polling fallback observer when native events are unreliable.
- Action-item YAML frontmatter parsing/writing via `python-frontmatter`.
- Duplicate prevention via stable IDs/hashes stored outside the vault.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: `watchdog`, `python-frontmatter` (plus existing repo deps)
**Storage**: Local files (Obsidian vault + a local non-vault state file for dedupe)
**Testing**: pytest
**Target Platform**: Local Linux/WSL filesystem
**Project Type**: single (Python project)
**Performance Goals**: Create `Needs_Action/*.md` within 60 seconds of a file drop (best-effort; depends on watcher mode).
**Constraints**: Bronze-only; no MCP servers; no external actions; non-destructive vault operations; avoid duplicates.
**Scale/Scope**: Personal-scale usage; correctness and safety over throughput.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Bronze-only scope (no MCP, no external actions)
- [x] Vault is source of truth; uses `My_AI_Employee/AI_Employee_Vault/` convention
- [x] AI behavior expressed as Claude Code Agent Skills under `.claude/skills/`
- [x] Vault safety: do not delete user-authored content; preserve YAML frontmatter
- [x] Secrets hygiene: `.env`/OS store only; do not commit secrets
- [x] Tests required: watcher core logic + action-item formatting

## Project Structure

### Documentation (this feature)

```text
specs/001-bronze-ai-employee/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
My_AI_Employee/

# NOTE: Implementation code will be placed under My_AI_Employee/ as requested.
# The exact package layout will be created during implementation (via /sp.tasks and coding).

tests/
```

**Structure Decision**: Single Python project with Bronze watcher + vault I/O logic under `My_AI_Employee/`. Tests live under `tests/`.

## Architecture Overview

### Components

1) **Filesystem watcher**
- Watches a configured drop folder.
- Emits Markdown action items into `My_AI_Employee/AI_Employee_Vault/Needs_Action/`.

2) **Vault I/O layer**
- Creates/updates action items (frontmatter + content).
- Updates dashboard via append/section update strategy (non-destructive).
- Moves processed items to `Done/` preserving YAML.

3) **Claude Code skills**
- `@watcher-runner-filesystem`: run / smoke test watcher.
- `@needs-action-triage`: process items, create plans, update dashboard, archive to Done.
- `@obsidian-vault-ops`: create/validate vault structure and templates.
- `@bronze-demo-check`: validate end-to-end readiness.

### End-to-end data flow

```text
(drop file into watch folder)
  → watcher detects create event
  → watcher writes Needs_Action/<FILE_...>.md
  → user runs @needs-action-triage
  → triage reads Company_Handbook.md + action item
  → triage writes Plans/<PLAN_...>.md (if Plans/ exists)
  → triage updates Dashboard.md
  → triage moves action item to Done/<...>.md (preserving YAML)
```

## Watcher Design

### Configuration inputs
- `VAULT_PATH`: path to vault root (default: `My_AI_Employee/AI_Employee_Vault/`).
- `WATCH_FOLDER`: path to drop folder (user-provided).
- `WATCH_MODE`: `events` (default) or `polling` (fallback mode).

### Event handling
- React to file creation events.
- Ignore directories and common temporary patterns (implementation detail to be finalized during /sp.tasks).

### Duplicate prevention
- Derive a stable identifier from the dropped file (e.g., absolute path + stat info).
- Store dedupe state outside the vault (e.g., a local JSON file under the project directory).

### Resilience
- Log errors and continue running.
- If vault paths are missing/unwritable, log and continue rather than crashing.

## Vault I/O Contracts

### Action item format
- Stored as Markdown under `Needs_Action/`.
- YAML frontmatter should include (minimum):
  - `type: file_drop|email|manual`
  - `received: <ISO timestamp>`
  - `status: pending|processed`
  - optional: `priority`, `source_id`, `from`, `subject`
- For `file_drop`, content must reference original file path (metadata-only).

### Plan output
- If `Plans/` exists, plans are written to `Plans/`.
- Plans include actionable checkbox steps and a clear done condition.

### Dashboard update
- Update `Dashboard.md` non-destructively (append/section update rather than full rewrite).
- Include:
  - pending count (files in `Needs_Action/`)
  - recent activity (last processed item)
  - warnings (malformed items)

### Archiving
- Move processed action items to `Done/`.
- Preserve YAML frontmatter; record `status: processed`.

## Testing Strategy

- Unit tests for watcher core logic:
  - given a simulated “file drop”, it produces exactly one action item path and content
  - dedupe prevents duplicates
- Unit tests for action-item formatting:
  - frontmatter contains required keys and valid ISO timestamp formatting
  - file_drop items include original path reference
- Integration-ish smoke test:
  - start watcher in a controlled temp directory, create a file, assert a `Needs_Action/*.md` appears

## Implementation Steps (file-by-file)

1) Create Python project scaffolding under `My_AI_Employee/` (uv).
2) Implement filesystem watcher using `watchdog` (events + polling mode).
3) Implement action-item writer using `python-frontmatter`.
4) Implement dedupe state store outside vault.
5) Implement/extend vault ops and triage scripts as needed to satisfy skill workflows.
6) Add pytest tests for watcher core logic + formatting.
7) Run `@bronze-demo-check` validation steps.

## Risks & Mitigations

1) **Filesystem events unreliable in WSL/network mounts**
- Mitigation: support polling observer mode.

2) **Accidental vault data loss**
- Mitigation: non-destructive updates; never delete user-authored content; preserve YAML frontmatter.

3) **Duplicate processing**
- Mitigation: stable IDs/hashes + external state file.

## Done When

- Watcher creates `Needs_Action/*.md` for file drops with correct frontmatter.
- Triage skill creates plans, updates dashboard, and archives to Done preserving YAML.
- Malformed items remain in `Needs_Action/` and generate dashboard warnings.
- Pytest passes for watcher core logic and action-item formatting.
- Bronze end-to-end demo can be executed with the documented skills.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) |  |  |


📋 Architectural decision detected: **Watcher mode strategy (native events vs polling fallback) and where dedupe state is stored (outside-vault local state)** — Document reasoning and tradeoffs? Run `/sp.adr watcher-mode-and-dedupe-state`.