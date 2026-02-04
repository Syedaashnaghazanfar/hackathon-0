# Tasks: Bronze Tier AI Employee

**Input**: Design documents from `/specs/001-bronze-ai-employee/`
**Prerequisites**: plan.md, spec.md, data-model.md
**Context7 Libraries**: watchdog (Observer/PollingObserver), python-frontmatter (load/dump/Post)
**Agent Skills**: @obsidian-vault-ops, @watcher-runner-filesystem, @needs-action-triage, @bronze-demo-check

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project root**: `My_AI_Employee/` (Python package)
- **Vault root**: `My_AI_Employee/AI_Employee_Vault/`
- **Tests**: `tests/` at repository root
- **Skills**: `.claude/skills/` (already exist)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Initialize Python project with uv in My_AI_Employee/ directory
- [X] T002 Add dependencies to pyproject.toml: watchdog, python-frontmatter, pytest
- [X] T003 [P] Create .env.example file with VAULT_PATH and WATCH_FOLDER configuration
- [X] T004 [P] Create .gitignore to exclude .env, __pycache__, .pytest_cache, dedupe state files
- [X] T005 Create My_AI_Employee/__init__.py as package marker

**Checkpoint**: ✅ Project structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Use @obsidian-vault-ops skill to create vault structure at My_AI_Employee/AI_Employee_Vault/
- [X] T007 Verify vault contains: Inbox/, Needs_Action/, Done/, Plans/, Dashboard.md, Company_Handbook.md
- [X] T008 [P] Create My_AI_Employee/utils/__init__.py for shared utilities
- [X] T009 [P] Create My_AI_Employee/utils/frontmatter_utils.py with load_action_item() and save_action_item() using frontmatter.load/dump
- [X] T010 [P] Create My_AI_Employee/utils/dedupe_state.py with DedupeTracker class (JSON file outside vault)
- [X] T011 Create My_AI_Employee/watchers/__init__.py for watcher modules
- [X] T012 Create My_AI_Employee/watchers/base_watcher.py with BaseWatcher abstract class pattern

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Watcher creates action items (Priority: P1) 🎯 MVP

**Goal**: Filesystem watcher detects dropped files and creates Markdown action items in Needs_Action/

**Independent Test**: Start watcher, drop file into watch folder, confirm action item appears in Needs_Action/ within 60 seconds

### Implementation for User Story 1

- [X] T013 [P] [US1] Create My_AI_Employee/watchers/filesystem_watcher.py with FilesystemWatcher class
- [X] T014 [US1] Implement FilesystemWatcher.__init__() with vault_path, watch_folder, watch_mode (events/polling) config
- [X] T015 [US1] Implement FilesystemWatcher.on_created() handler using watchdog FileSystemEventHandler.on_created()
- [X] T016 [US1] Implement FilesystemWatcher._create_action_item() to generate Needs_Action/*.md with frontmatter (type, received, status)
- [X] T017 [US1] Implement FilesystemWatcher._generate_stable_id() for duplicate prevention using file path + stat info
- [X] T018 [US1] Integrate DedupeTracker in FilesystemWatcher to prevent duplicate action items (FR-007)
- [X] T019 [US1] Implement FilesystemWatcher.run() with Observer (native events) and PollingObserver fallback for WSL
- [X] T020 [US1] Add error handling in FilesystemWatcher: log errors, continue running (FR-008)
- [X] T021 [US1] Create My_AI_Employee/run_watcher.py entrypoint script with argparse for vault_path and watch_folder
- [X] T022 [US1] Test watcher manually using @watcher-runner-filesystem skill

**Checkpoint**: At this point, User Story 1 should be fully functional - files dropped create action items

---

## Phase 4: User Story 5 - Action item format is standardized (Priority: P5)

**Goal**: Action items follow consistent frontmatter contract for reliable triage

**Independent Test**: Generate action item and validate YAML fields are present and parseable

### Tests for User Story 5 (FR-017 requirement)

- [X] T023 [P] [US5] Create tests/test_action_item_format.py with test_action_item_has_required_frontmatter()
- [X] T024 [P] [US5] Add test_action_item_received_is_iso_timestamp() to validate ISO 8601 format
- [X] T025 [P] [US5] Add test_file_drop_references_original_path() to validate FR-006
- [X] T026 [P] [US5] Add test_frontmatter_preservation_on_load_dump() using frontmatter.load() and frontmatter.dump()

### Tests for User Story 1 (FR-017 requirement)

- [X] T027 [P] [US1] Create tests/test_watcher_core.py with test_watcher_creates_action_item()
- [X] T028 [P] [US1] Add test_watcher_prevents_duplicates() to validate dedupe logic
- [X] T029 [P] [US1] Add test_watcher_continues_after_error() to validate FR-008 resilience
- [X] T030 [US1] Run pytest and ensure all US1 and US5 tests pass

**Checkpoint**: Watcher and action item format are tested and validated

---

## Phase 5: User Story 2 - Claude triages action items (Priority: P2)

**Goal**: Claude Code reads Needs_Action/, applies Company_Handbook.md rules, creates plans, updates dashboard, archives to Done/

**Independent Test**: Place action item in Needs_Action/, run @needs-action-triage, confirm plan created and item moved to Done/

### Implementation for User Story 2

- [X] T031 [P] [US2] Create My_AI_Employee/vault_ops/__init__.py for vault operations
- [X] T032 [P] [US2] Create My_AI_Employee/vault_ops/action_item_reader.py with read_pending_items() function
- [X] T033 [P] [US2] Create My_AI_Employee/vault_ops/plan_writer.py with create_plan() function for Plans/ folder
- [X] T034 [US2] Create My_AI_Employee/vault_ops/item_archiver.py with archive_to_done() using frontmatter.load/dump (FR-014)
- [X] T035 [US2] Implement archive_to_done() to preserve YAML frontmatter and add status: processed
- [X] T036 [US2] Create My_AI_Employee/triage/__init__.py for triage logic
- [X] T037 [US2] Create My_AI_Employee/triage/handbook_reader.py with read_handbook_rules() for Company_Handbook.md
- [X] T038 [US2] Create My_AI_Employee/triage/plan_generator.py with generate_plan_content() (checkboxes, done condition)
- [X] T039 [US2] Implement malformed item detection in triage: leave in Needs_Action/, add dashboard warning (FR-015)
- [X] T040 [US2] Test triage workflow manually using @needs-action-triage skill

**Checkpoint**: Triage workflow creates plans and archives items to Done/ with frontmatter preserved

---

## Phase 6: User Story 3 - Dashboard shows system status (Priority: P3)

**Goal**: Dashboard.md displays pending counts, recent activity, and warnings

**Independent Test**: Process action items and confirm Dashboard.md shows correct counts and activity

### Implementation for User Story 3

- [X] T041 [P] [US3] Create My_AI_Employee/vault_ops/dashboard_updater.py with DashboardUpdater class
- [X] T042 [US3] Implement DashboardUpdater.update_pending_count() to count files in Needs_Action/
- [X] T043 [US3] Implement DashboardUpdater.add_recent_activity() with timestamp and item reference
- [X] T044 [US3] Implement DashboardUpdater.add_warning() for malformed items
- [X] T045 [US3] Implement DashboardUpdater._update_section() for non-destructive dashboard updates (preserve user notes)
- [X] T046 [US3] Integrate DashboardUpdater into triage workflow in My_AI_Employee/triage/

**Checkpoint**: Dashboard accurately reflects system status after triage runs

---

## Phase 7: User Story 4 - Vault setup is consistent (Priority: P4)

**Goal**: Vault structure is validated and consistent for predictable operations

**Independent Test**: Run vault validation and confirm all required paths exist

### Implementation for User Story 4

- [X] T047 [P] [US4] Create My_AI_Employee/vault_ops/vault_validator.py with VaultValidator class
- [X] T048 [US4] Implement VaultValidator.validate_structure() to check required folders and files (FR-001)
- [X] T049 [US4] Implement VaultValidator.validate_plans_folder() to check Plans/ behavior (FR-002)
- [X] T050 [US4] Add vault validation to @obsidian-vault-ops skill workflow
- [X] T051 [US4] Test vault validation using @obsidian-vault-ops skill

**Checkpoint**: Vault structure is validated and consistent

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation, documentation, and final improvements

- [X] T052 [P] Create README.md with setup instructions, dependencies, and usage examples
- [X] T053 [P] Create My_AI_Employee/config.py for centralized configuration management
- [X] T054 [P] Add logging configuration in My_AI_Employee/utils/logger.py
- [X] T055 Add comprehensive docstrings to all modules following Google style
- [X] T056 Run @bronze-demo-check skill to validate end-to-end Bronze tier acceptance
- [X] T057 Verify all acceptance scenarios from spec.md are satisfied
- [X] T058 [P] Create QUICKSTART.md with step-by-step demo instructions
- [X] T059 Run final pytest suite and ensure 100% pass rate
- [X] T060 Verify no secrets committed and .env.example is complete

**Checkpoint**: Bronze tier is complete and demo-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Phase 3): Can start after Foundational - No dependencies on other stories
  - US5 (Phase 4): Can start after US1 - Tests US1 output format
  - US2 (Phase 5): Depends on US1 output existing - Can run after US1
  - US3 (Phase 6): Depends on US2 triage workflow - Can run after US2
  - US4 (Phase 7): Can start after Foundational - Independent validation
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P5)**: Depends on US1 - Tests action item format from watcher
- **User Story 2 (P2)**: Depends on US1 - Processes action items created by watcher
- **User Story 3 (P3)**: Depends on US2 - Dashboard updates are part of triage workflow
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent validation

### Within Each User Story

- Tests (US5) should validate US1 output before proceeding to US2
- Vault operations before triage logic
- Dashboard updates integrate into triage workflow
- Validation runs after implementation

### Parallel Opportunities

- Phase 1: T003, T004 can run in parallel
- Phase 2: T008, T009, T010 can run in parallel after T007
- Phase 3: T013 can start independently
- Phase 4: All test tasks (T023-T029) can run in parallel
- Phase 5: T031, T032, T033 can run in parallel
- Phase 6: T041 can start independently
- Phase 7: T047 can start independently
- Phase 8: T052, T053, T054, T058 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch foundational utilities in parallel:
Task: "Create My_AI_Employee/utils/frontmatter_utils.py" (T009)
Task: "Create My_AI_Employee/utils/dedupe_state.py" (T010)

# Launch all tests for US1 and US5 together:
Task: "Create tests/test_action_item_format.py" (T023)
Task: "Add test_action_item_received_is_iso_timestamp()" (T024)
Task: "Add test_file_drop_references_original_path()" (T025)
Task: "Add test_frontmatter_preservation_on_load_dump()" (T026)
Task: "Create tests/test_watcher_core.py" (T027)
Task: "Add test_watcher_prevents_duplicates()" (T028)
Task: "Add test_watcher_continues_after_error()" (T029)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Watcher creates action items)
4. Complete Phase 4: User Story 5 (Test action item format)
5. **STOP and VALIDATE**: Test US1 independently - drop file, confirm action item created
6. Demo watcher functionality

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + US5 tests → Test independently → Demo watcher (MVP!)
3. Add User Story 2 → Test independently → Demo triage workflow
4. Add User Story 3 → Test independently → Demo dashboard updates
5. Add User Story 4 → Test independently → Demo vault validation
6. Complete Phase 8 → Run @bronze-demo-check → Full Bronze tier demo

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Watcher) + US5 (Tests)
   - Developer B: User Story 2 (Triage) - waits for US1 output
   - Developer C: User Story 4 (Vault validation) - can start immediately
3. After US2 complete:
   - Developer B: User Story 3 (Dashboard)
4. Stories complete and integrate independently

---

## Context7 Implementation Notes

### watchdog (Observer/PollingObserver)

From Context7 documentation:

```python
# Native events (default)
from watchdog.observers import Observer
observer = Observer()

# Polling fallback for WSL/CIFS
from watchdog.observers.polling import PollingObserver
observer = PollingObserver()

# Event handler pattern
class FilesystemWatcher(FileSystemEventHandler):
    def on_created(self, event: FileSystemEvent) -> None:
        # Handle file creation
        pass

# Observer lifecycle
observer.schedule(event_handler, path, recursive=False)
observer.start()
try:
    while True:
        time.sleep(1)
finally:
    observer.stop()
    observer.join()
```

### python-frontmatter (load/dump/Post)

From Context7 documentation:

```python
import frontmatter

# Load and preserve frontmatter
post = frontmatter.load('Needs_Action/item.md')

# Access and modify metadata
print(post['type'])  # Access frontmatter field
post['status'] = 'processed'  # Modify field
post['processed'] = datetime.now().isoformat()  # Add new field

# Content access
print(post.content)  # Markdown content without frontmatter

# Write back preserving all frontmatter
with open('Done/item.md', 'w') as f:
    frontmatter.dump(post, f)

# Or serialize to string
text = frontmatter.dumps(post)
```

---

## Agent Skills Integration

### @obsidian-vault-ops
- **Used in**: T006, T007, T050, T051
- **Purpose**: Create and validate vault structure, ensure required files exist

### @watcher-runner-filesystem
- **Used in**: T022
- **Purpose**: Run and smoke-test the filesystem watcher

### @needs-action-triage
- **Used in**: T040
- **Purpose**: Test triage workflow end-to-end

### @bronze-demo-check
- **Used in**: T056
- **Purpose**: Validate complete Bronze tier acceptance criteria

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Use Context7 patterns for watchdog and python-frontmatter implementations
- Reference Agent Skills for validation and testing workflows
- FR-017 requires pytest tests for watcher core logic and action-item formatting
