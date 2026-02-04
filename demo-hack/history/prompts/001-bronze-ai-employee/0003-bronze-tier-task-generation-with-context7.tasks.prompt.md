---
id: 0003
title: Bronze Tier Task Generation with Context7
stage: tasks
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5
feature: 001-bronze-ai-employee
branch: 001-bronze-ai-employee
user: uneezaismail
command: /sp.tasks
labels: ["tasks", "bronze-tier", "context7", "watchdog", "python-frontmatter", "agent-skills", "obsidian", "watcher"]
links:
  spec: specs/001-bronze-ai-employee/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-bronze-ai-employee/tasks.md
tests:
  - null
---

## Prompt

Generate implementation tasks for Bronze Tier AI Employee (Hackathon Zero) based on specs/001-bronze-ai-employee/spec.md and specs/001-bronze-ai-employee/plan.md.

**Context7 MCP Usage (MANDATORY)**:
Before generating tasks, use the Context7 MCP server to query up-to-date documentation for:
- /gorakhargosh/watchdog - For filesystem watcher implementation (Observer, PollingObserver, FileSystemEventHandler patterns)
- /eyeseast/python-frontmatter - For YAML frontmatter parsing/writing (load, loads, dump, dumps, Post object preservation)

Use Context7 queries to inform task descriptions with correct API patterns and best practices.

**Agent Skills Integration (CRITICAL)**:
The implementation MUST use these four Agent Skills located in .claude/skills/:

1. **@obsidian-vault-ops** - For all vault operations
2. **@watcher-runner-filesystem** - For watcher operations
3. **@needs-action-triage** - For processing workflow
4. **@bronze-demo-check** - For end-to-end validation

**Task Organization Requirements**:
- Organize by user story priority from spec.md (P1: Watcher creates action items, P2: Claude triages, P3: Dashboard shows status, P4: Vault setup, P5: Action item format)
- Each user story phase must be independently testable
- Include pytest test tasks per FR-017 requirement (watcher core logic + action-item formatting)
- Mark parallelizable tasks with [P]
- Include exact file paths under My_AI_Employee/ directory

**Bronze Tier Constraints**:
- No MCP servers or external actions (Bronze only)
- Single filesystem watcher only (no Gmail/WhatsApp)
- Vault path convention: My_AI_Employee/AI_Employee_Vault/
- Python 3.13+ with uv package manager
- Dependencies: watchdog, python-frontmatter, pytest
- Non-destructive vault operations (preserve YAML frontmatter)
- Duplicate prevention via external state file (not in vault)

**Technical Implementation Notes from Context7**:
- Use PollingObserver for WSL/CIFS reliability (fallback from native Observer)
- Use frontmatter.load() and frontmatter.dump() to preserve YAML when moving files
- Implement dedupe tracking outside vault (JSON file in project directory)
- Action items must include type, received (ISO timestamp), status in frontmatter

## Response snapshot

Generated comprehensive tasks.md with 60 tasks organized by user story priority:

**Phase Summary**:
| Phase | Tasks | Parallel | Description |
|-------|-------|----------|-------------|
| Setup | 5 | 2 | Project structure and dependencies |
| Foundational | 7 | 3 | Core infrastructure (vault, utilities, base watcher) |
| US1 (P1) | 10 | 1 | Filesystem watcher implementation |
| US5 (P5) | 8 | 7 | Action item format tests (pytest) |
| US2 (P2) | 10 | 3 | Triage workflow (vault I/O, plan generation, archiving) |
| US3 (P3) | 6 | 1 | Dashboard updates |
| US4 (P4) | 5 | 1 | Vault validation |
| Polish | 9 | 4 | Documentation, end-to-end validation, final tests |

**Key Tasks per User Story**:
- **US1 (Watcher)**: T013-T022 - FilesystemWatcher with Observer/PollingObserver, dedupe prevention, error handling
- **US5 (Format Tests)**: T023-T030 - pytest tests for action item format and watcher core logic (FR-017)
- **US2 (Triage)**: T031-T040 - Vault I/O, plan generation, frontmatter preservation, archiving to Done/
- **US3 (Dashboard)**: T041-T046 - DashboardUpdater with pending counts, activity log, warnings
- **US4 (Vault)**: T047-T051 - VaultValidator for structure consistency

**Context7 Integration**:
- watchdog patterns: Observer/PollingObserver, FileSystemEventHandler.on_created(), error handling
- python-frontmatter patterns: frontmatter.load(), frontmatter.dump(), Post object metadata access

**Agent Skills Integration**:
- @obsidian-vault-ops: T006, T007, T050, T051
- @watcher-runner-filesystem: T022
- @needs-action-triage: T040
- @bronze-demo-check: T056

**Dependency Graph**:
```
Phase 1 (Setup) → Phase 2 (Foundational) → US1 (P1) → US5 (P5 Tests)
                                          → US2 (P2) → US3 (P3)
                                          → US4 (P4)
                                          → Phase 8 (Polish)
```

**MVP Scope**: Phases 1-4 (Setup + Foundational + US1 Watcher + US5 Tests)

**All tasks follow strict checklist format**:
`- [ ] T### [P?] [US#?] Description with file/path.py`

## Outcome

- ✅ Impact: High - 60 executable tasks ready for implementation with Context7 patterns and Agent Skills integration
- 🧪 Tests: pytest tests included per FR-017 (T023-T030: watcher core logic + action-item formatting)
- 📁 Files: specs/001-bronze-ai-employee/tasks.md
- 🔁 Next prompts: Start implementation with Phase 1 Setup tasks (T001-T005)
- 🧠 Reflection: Tasks organized by user story priority with Context7 API patterns (watchdog Observer/PollingObserver, python-frontmatter load/dump) and Agent Skills integration for validation workflows

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Format validation PASS - all 60 tasks follow checklist format with [P] markers and [US#] labels
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
