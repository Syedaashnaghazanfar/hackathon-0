# Implementation Tasks: Silver Tier AI Employee

**Feature**: Silver Tier AI Employee
**Branch**: `002-silver-tier-ai-employee`
**Date**: 2026-01-22
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

## Overview

This tasks document breaks down Silver tier implementation into 8 phases organized by user story priority. Each phase delivers an independently testable increment that builds on Bronze tier foundations.

**Implementation Strategy**: MVP-first approach - User Story 1 (Multi-Channel Monitoring) is the minimum viable product. Subsequent stories add triage, approval, execution, and production polish.

**Total Estimated Tasks**: 95 tasks across 8 phases

---

## Phase 1: Setup & Infrastructure (12 tasks)

**Goal**: Initialize Silver tier project structure, dependencies, and shared utilities

### Dependencies

```bash
uv add fastmcp playwright google-api-python-client google-auth-oauthlib google-auth-httplib2 requests
playwright install chromium
```

### Tasks

- [X] T001 Update pyproject.toml with Silver tier dependencies (fastmcp, playwright, google-api-python-client, google-auth-oauthlib, google-auth-httplib2, requests)
- [X] T002 Create .env.example template with all required Silver tier environment variables (GMAIL_CREDENTIALS_FILE, LINKEDIN_ACCESS_TOKEN, WHATSAPP_SESSION_DIR, DRY_RUN, LOG_LEVEL)
- [X] T003 Update .gitignore to exclude credentials (.env, credentials.json, token.json, *_dedupe.json, .whatsapp_session/, /Logs/)
- [X] T004 [P] Create src/my_ai_employee/models/action_item.py with ActionItemSchema dataclass (Bronze + Silver fields)
- [X] T005 [P] Create src/my_ai_employee/models/approval_request.py with ApprovalRequestSchema dataclass
- [X] T006 [P] Create src/my_ai_employee/models/audit_log.py with AuditLogEntry dataclass
- [X] T007 [P] Create src/my_ai_employee/utils/sanitizer.py with credential redaction functions (redact_api_key, redact_oauth_token, redact_pii)
- [X] T008 [P] Create src/my_ai_employee/utils/dedupe_state.py with WatcherState class for deduplication tracking
- [X] T009 [P] Create src/my_ai_employee/utils/auth_helper.py with OAuth2Helper class for Gmail token management
- [X] T010 [P] Create src/my_ai_employee/config.py with centralized Config dataclass loading from .env
- [X] T011 Create scripts/setup/initialize_vault.py to create Silver tier folders (/Pending_Approval, /Approved, /Rejected, /Failed, /Logs)
- [X] T012 Run initialize_vault.py to set up vault structure for testing

---

## Phase 2: Foundational Components (8 tasks)

**Goal**: Implement shared base classes and vault operations that all user stories depend on

**Blocking Prerequisites**: These must complete before any user story implementation begins.

### Tasks

- [X] T013 Create src/my_ai_employee/watchers/base_watcher.py with abstract BaseWatcher class (run, check_interval, vault_path, heartbeat_logging)
- [X] T014 Implement src/my_ai_employee/vault_ops/vault_validator.py to validate vault structure on startup
- [X] T015 Implement src/my_ai_employee/vault_ops/action_item_reader.py to read action items from /Needs_Action/ with YAML parsing
- [X] T016 Implement src/my_ai_employee/vault_ops/item_archiver.py to move items between folders preserving YAML frontmatter
- [X] T017 Create src/my_ai_employee/utils/frontmatter_utils.py with load_action_item, save_action_item, create_action_item_from_data functions
- [X] T018 Create src/my_ai_employee/utils/audit_logger.py with AuditLogger class for structured JSON logging to /Logs/YYYY-MM-DD.json
- [X] T019 Update Company_Handbook.md with Silver tier approval thresholds section (auto-approve rules, require-approval defaults)
- [X] T020 Verify all Bronze tier tests still pass after foundational changes (run pytest tests/)

---

## Phase 3: User Story 1 - Multi-Channel Monitoring (Priority P1) - 15 tasks

**Story Goal**: Continuously monitor Gmail, WhatsApp, and LinkedIn accounts, automatically creating structured action items in Obsidian vault.

**Independent Test**: Send test emails/messages to monitored accounts and verify structured markdown action items with correct YAML frontmatter appear in /Needs_Action within 2 minutes.

### Setup Tasks

- [X] T021 [US1] Create scripts/setup/setup_gmail_oauth.py for interactive OAuth2 flow (opens browser, saves credentials.json and token.json)
- [X] T022 [US1] Create scripts/setup/linkedin_oauth2_setup.py for LinkedIn bearer token acquisition (saves to .env)
- [X] T023 [US1] Create scripts/setup/whatsapp_auth.py for WhatsApp Web QR code authentication (saves session to .whatsapp_session/)

### Gmail Watcher

- [X] T024 [P] [US1] Implement src/my_ai_employee/watchers/gmail_watcher.py extending BaseWatcher with Gmail API monitoring
- [X] T025 [US1] Add OAuth2 token refresh logic in gmail_watcher.py using utils/auth_helper.py
- [X] T026 [US1] Implement deduplication in gmail_watcher.py using SHA256 hashing and .gmail_dedupe.json state file
- [X] T027 [US1] Add action item creation in gmail_watcher.py (write markdown with YAML frontmatter to /Needs_Action/)

### WhatsApp Watcher

- [X] T028 [P] [US1] Implement src/my_ai_employee/watchers/whatsapp_watcher.py extending BaseWatcher with Playwright browser automation
- [X] T029 [US1] Add session persistence in whatsapp_watcher.py (load from .whatsapp_session/, fallback to QR scan)
- [X] T030 [US1] Implement urgent keyword detection in whatsapp_watcher.py (invoice, payment, help, urgent, ASAP regex matching)
- [X] T031 [US1] Add deduplication in whatsapp_watcher.py using .whatsapp_dedupe.json state file

### LinkedIn Watcher

- [X] T032 [P] [US1] Implement src/my_ai_employee/watchers/linkedin_watcher.py extending BaseWatcher with LinkedIn REST API v2
- [X] T033 [US1] Add rate limit handling in linkedin_watcher.py (exponential backoff for 429 responses)
- [X] T034 [US1] Add deduplication in linkedin_watcher.py using .linkedin_dedupe.json state file

### Testing

- [X] T035 [US1] Run Gmail watcher end-to-end: Send test email → verify action item in /Needs_Action/ within 2 minutes (acceptance scenario 1)

---

## Phase 4: User Story 2 - Intelligent Triage (Priority P1) - 10 tasks

**Story Goal**: Analyze incoming action items, generate detailed execution plans, and classify whether actions require approval (external actions) or can proceed automatically (internal vault operations).

**Independent Test**: Manually create test action items in /Needs_Action, run needs-action-triage skill, verify Plan.md files appear in /Plans with correct classification (auto-approve vs require-approval) and step-by-step execution details.

### Tasks

- [X] T036 [P] [US2] Create src/my_ai_employee/approval/permission_boundaries.py to parse auto-approve rules from Company_Handbook.md
- [X] T037 [P] [US2] Implement src/my_ai_employee/vault_ops/plan_writer.py to write Plan.md files to /Plans/ folder
- [X] T038 [US2] Update .claude/skills/needs-action-triage/SKILL.md with Silver tier classification logic (auto-approve vs require-approval)
- [X] T039 [US2] Add Company_Handbook.md parsing in needs-action-triage skill to extract business rules
- [X] T040 [US2] Implement action type classification in needs-action-triage skill (email, linkedin_post, vault_update, etc.)
- [X] T041 [US2] Add risk assessment generation in needs-action-triage skill (impact, reversibility, blast radius)
- [X] T042 [US2] Implement draft content generation in needs-action-triage skill (email replies, LinkedIn post drafts)
- [X] T043 [US2] Add execution step generation in needs-action-triage skill (MCP server, tool name, parameters)
- [X] T044 [US2] Test classification: Create email reply action item → verify Plan.md classifies as "require-approval" (acceptance scenario 1)
- [X] T045 [US2] Test classification: Create dashboard update action item → verify Plan.md classifies as "auto-approve" (acceptance scenario 2)

---

## Phase 5: User Story 3 - HITL Approval Workflow (Priority P1) - 12 tasks

**Story Goal**: All external actions require explicit human approval before execution, with clear risk assessments and execution previews presented in Obsidian vault.

**Independent Test**: Manually create approval request file in /Pending_Approval with sample email send action, move to /Approved, verify approval-workflow-manager correctly routes for execution. Test rejection by moving to /Rejected and verify no execution.

### Tasks

- [x] T046 [P] [US3] Create src/my_ai_employee/approval/approval_request.py with ApprovalRequest class (create, validate, move functions)
- [x] T047 [US3] Create .claude/skills/approval-workflow-manager/SKILL.md with approval routing logic
- [x] T048 [US3] Implement approval request creation in approval-workflow-manager skill (read Plan.md, create /Pending_Approval/ file with risk assessment)
- [x] T049 [US3] Add risk assessment formatting in approval-workflow-manager skill (impact, reversibility, blast radius sections)
- [x] T050 [US3] Add execution preview formatting in approval-workflow-manager skill (MCP server, tool, sanitized parameters)
- [x] T051 [US3] Implement approval decision monitoring in approval-workflow-manager skill (detect file moves to /Approved/ or /Rejected/)
- [x] T052 [US3] Add rejection handling in approval-workflow-manager skill (move to /Rejected/, log rejection_reason from frontmatter)
- [x] T053 [US3] Implement permission boundary enforcement in approval-workflow-manager skill (auto-approve if criteria met in Company_Handbook.md)
- [ ] T054 [US3] Test approval flow: Create approval request → move to /Approved/ → verify queued for execution (acceptance scenario 2)
- [ ] T055 [US3] Test rejection flow: Create approval request → move to /Rejected/ with rejection_reason → verify no execution (acceptance scenario 3)
- [ ] T056 [US3] Test risk assessment: Verify approval request includes impact, reversibility, blast radius sections (acceptance scenario 1)
- [ ] T057 [US3] Test auto-approve: Configure Company_Handbook rule → verify eligible actions bypass /Pending_Approval/ (acceptance scenario 4 - optional)

---

## Phase 6: User Story 5 - Security & Audit Logging (Priority P1) - 10 tasks

**Story Goal**: Every external action execution logged in structured JSON format with timestamps, actors, parameters, results, with all credentials sanitized before logging, 90-day retention.

**Independent Test**: Execute test action in dry-run mode, verify /Logs/YYYY-MM-DD.json file created with correct schema (timestamp, action_type, user, ai_agent, mcp_server, tool_name, sanitized inputs/outputs, execution_status, error), verify credentials redacted.

**Note**: Implementing before US4 (Execution) because audit logging is foundational security requirement and simpler to test independently.

### Tasks

- [x] T058 [P] [US5] Implement credential sanitization in src/my_ai_employee/utils/sanitizer.py (redact API keys, OAuth tokens, passwords, credit cards, emails)
- [x] T059 [P] [US5] Add AuditLogger.log_execution method in src/my_ai_employee/utils/audit_logger.py (accepts action_id, action_type, user, ai_agent, mcp_server, tool_name, inputs, outputs, status, error)
- [x] T060 [US5] Implement daily log rotation in AuditLogger (create YYYY-MM-DD.json files in /Logs/)
- [x] T061 [US5] Add JSON schema validation in AuditLogger (timestamp, action_id, action_type, user, ai_agent, mcp_server, tool_name, execution_status, error, retry_count)
- [x] T062 [US5] Create .claude/skills/audit-logger/SKILL.md with logging workflow (called by mcp-executor after each action)
- [ ] T063 [US5] Implement credential sanitization in audit-logger skill (apply sanitizer.py functions before logging)
- [ ] T064 [US5] Add 90-day retention policy in audit-logger skill (archive old logs, don't delete)
- [ ] T065 [US5] Test audit logging: Execute dry-run action → verify /Logs/YYYY-MM-DD.json created with all required fields (acceptance scenario 1)
- [ ] T066 [US5] Test credential sanitization: Log action with API key → verify replaced with <REDACTED_TOKEN> (acceptance scenario 2)
- [ ] T067 [US5] Test error logging: Log failed action → verify error field contains sanitized error message (acceptance scenario 4)

---

## Phase 7: User Story 4 - External Action Execution (Priority P2) - 18 tasks

**Story Goal**: Reliably execute approved actions through appropriate external integration (Gmail API, LinkedIn API, Playwright), handle errors gracefully with retries, report execution status back to vault.

**Independent Test**: Create pre-approved email send request in /Approved (dry-run mode), run mcp-executor skill, verify calls email MCP server (logged but not sent), moves action to /Done, creates audit log entry in /Logs.

### MCP Servers

- [x] T068 [P] [US4] Create src/my_ai_employee/mcp_servers/email_mcp.py with FastMCP server implementing send_email tool (Gmail API integration)
- [x] T069 [US4] Add OAuth2 authentication in email_mcp.py (load credentials from .env, use auth_helper.py for token refresh)
- [x] T070 [US4] Add dry-run mode in email_mcp.py (check DRY_RUN env var, log but don't send if true)
- [x] T071 [US4] Implement error handling in email_mcp.py (401 auth failure, 429 rate limit, network errors)
- [x] T072 [P] [US4] Create src/my_ai_employee/mcp_servers/linkedin_mcp.py with FastMCP server implementing publish_post tool (LinkedIn REST API v2)
- [x] T073 [US4] Add bearer token authentication in linkedin_mcp.py (load LINKEDIN_ACCESS_TOKEN from .env)
- [x] T074 [US4] Add rate limit handling in linkedin_mcp.py (exponential backoff for 429, max 3 retries)
- [x] T075 [US4] Add dry-run mode in linkedin_mcp.py (log but don't post if DRY_RUN=true)
- [x] T076 [P] [US4] Create src/my_ai_employee/mcp_servers/browser_mcp.py with FastMCP server implementing send_whatsapp_message tool (Playwright automation)
- [x] T077 [US4] Add session persistence in browser_mcp.py (load from .whatsapp_session/, fallback to QR scan)
- [x] T078 [US4] Add dry-run mode in browser_mcp.py (log but don't send if DRY_RUN=true)

### Executor

- [x] T079 [US4] Create src/my_ai_employee/orchestrator.py to watch /Approved/ folder and route actions to MCP servers
- [x] T080 [US4] Implement action routing in orchestrator.py (parse action_type, call appropriate MCP server tool)
- [x] T081 [US4] Add retry logic in orchestrator.py (exponential backoff 1s, 2s, 4s, max 3 retries for transient failures)
- [x] T082 [US4] Implement result handling in orchestrator.py (success → move to /Done/, failure → move to /Failed/ with error details)
- [x] T083 [US4] Integrate audit logger in orchestrator.py (call audit-logger skill after each execution)
- [ ] T084 [US4] Test email execution: Approve email send action in dry-run mode → verify logged but not sent, moved to /Done/ (acceptance scenario 1)
- [ ] T085 [US4] Test retry logic: Simulate network error → verify exponential backoff (1s, 2s, 4s) up to 3 attempts, then /Failed/ (acceptance scenario 3)

---

## Phase 8: User Story 6 - Graceful Degradation (Priority P2) - 6 tasks

**Story Goal**: System automatically recovers from component failures (watcher crashes, MCP server downtime, network outages) by isolating failures, retrying transient errors, restarting crashed processes, operating with degraded functionality.

**Independent Test**: Manually kill watcher process (e.g., Gmail), verify watchdog/PM2 automatically restarts within 60 seconds, verify other watchers continue operating unaffected. Test retry logic by simulating transient network timeout.

### Tasks

- [x] T086 [P] [US6] Create ecosystem.config.js with PM2 configuration for all watchers (gmail, whatsapp, linkedin, filesystem) and orchestrator
- [x] T087 [US6] Add auto-restart policy in ecosystem.config.js (max 10 restarts, 10s min uptime before restart)
- [x] T088 [US6] Implement heartbeat logging in all watchers (log heartbeat every 60 seconds with timestamp, component name, status, items_processed, uptime)
- [x] T089 [US6] Add graceful shutdown handlers in all watchers (SIGTERM/SIGINT handling, complete in-flight operations before exit)
- [ ] T090 [US6] Test component isolation: Kill Gmail watcher → verify WhatsApp/LinkedIn watchers continue running (acceptance scenario 3)
- [ ] T091 [US6] Test auto-restart: Kill Gmail watcher → verify PM2 restarts within 60 seconds (acceptance scenario 1)

---

## Phase 9: User Story 7 - Vault Integration (Priority P2) - 4 tasks

**Story Goal**: Maintain vault structure (Bronze + Silver folders), update Dashboard.md with recent activity summaries and pending approval counts, preserve YAML frontmatter when moving files, never delete user content.

**Independent Test**: Create test action item with custom YAML frontmatter, move through workflow (Needs_Action → Pending_Approval → Approved → Done), verify frontmatter preserved at each step and Dashboard.md shows updated statistics.

### Tasks

- [x] T092 [P] [US7] Implement src/my_ai_employee/vault_ops/dashboard_updater.py to update Dashboard.md with statistics (pending approvals count, recent activity, success/failure counts)
- [x] T093 [US7] Update .claude/skills/obsidian-vault-ops/SKILL.md with Silver tier folder operations (/Pending_Approval, /Approved, /Rejected, /Failed, /Logs)
- [ ] T094 [US7] Test YAML preservation: Move action item through workflow → verify frontmatter preserved exactly (acceptance scenario 2)
- [ ] T095 [US7] Test dashboard updates: Approve action → verify Dashboard.md shows updated pending approval count within 10 seconds (acceptance scenario 3)

---

## Phase 10: User Story 8 - Multi-Watcher Orchestration (Priority P2) - 6 tasks

**Story Goal**: Start all watchers simultaneously with single command (multi-watcher-runner skill), run continuously 24/7 via PM2/watchdog, automatically restart after system reboots.

**Independent Test**: Run multi-watcher-runner skill, verify all configured watchers (Gmail, WhatsApp, LinkedIn, filesystem) start successfully and log heartbeat messages every 60 seconds. Stop orchestrator, restart, verify watchers resume from last state without duplicate processing.

### Tasks

- [x] T096 [P] [US8] Create src/my_ai_employee/run_watcher.py as unified watcher launcher CLI (accepts watcher type: gmail|whatsapp|linkedin|filesystem|all)
- [x] T097 [US8] Update .claude/skills/multi-watcher-runner/SKILL.md with orchestration logic (start all watchers, monitor health, auto-restart)
- [x] T098 [US8] Implement multi-watcher startup in multi-watcher-runner skill (spawn all configured watchers as subprocesses)
- [x] T099 [US8] Add health monitoring in multi-watcher-runner skill (check heartbeat logs, restart if no heartbeat in 120 seconds)
- [x] T100 [US8] Configure PM2 startup script for system reboot recovery (pm2 startup command, pm2 save)
- [ ] T101 [US8] Test multi-watcher startup: Run multi-watcher-runner → verify all watchers start and log heartbeats every 60 seconds (acceptance scenario 1)

---

## Phase 11: Polish & Cross-Cutting Concerns (10 tasks)

**Goal**: Production-ready polish, security hardening, testing, documentation

### Security & Validation

- [x] T102 [P] Create scripts/validate/validate_silver_tier.py to check credentials not in vault/repo (grep for API keys, tokens)
- [x] T103 [P] Create scripts/debug/debug_gmail.py to test Gmail API connection and token validity
- [x] T104 [P] Create scripts/debug/debug_linkedin.py to test LinkedIn API connection
- [x] T105 [P] Create scripts/debug/debug_whatsapp.py to test WhatsApp Web session authentication
- [ ] T106 Run validate_silver_tier.py security scan → verify zero credentials in vault/repo (success criterion SC-003)

### Documentation

- [x] T107 [P] Create README_SILVER.md with production deployment instructions (quickstart.md content)
- [ ] T108 [P] Update main README.md with Silver tier overview section
- [x] T109 Create TROUBLESHOOTING.md with common issues and solutions

### End-to-End Testing

- [ ] T110 Run end-to-end Silver tier test: Gmail email → Needs_Action → triage → Pending_Approval → approve → execution (dry-run) → audit log → Done (success criterion SC-002 - complete within 5 minutes)
- [ ] T111 Verify all Bronze tier tests still pass after Silver tier implementation (success criterion SC-007)

---

## Dependency Graph

```
Phase 1 (Setup) → Phase 2 (Foundational)
                     ↓
  ┌─────────────────┴────────────────────┬─────────────────┬─────────────────┐
  ↓                                      ↓                 ↓                 ↓
US1 (Monitoring)                    US2 (Triage)      US5 (Audit Log)   US6 (Degradation)
  ↓                                      ↓                 ↓                 ↓
US1 complete → US2 → US3 (Approval) → US5 complete → US4 (Execution) → US6 (Degradation)
                                                            ↓
                                                     US7 (Vault) → US8 (Orchestration)
                                                            ↓
                                                      Polish Phase
```

**Critical Path**: Setup → Foundational → US1 → US2 → US3 → US5 → US4 → Polish

**Parallel Opportunities**:
- US5 (Audit Logging) can be implemented in parallel with US3 (Approval)
- US6 (Graceful Degradation) infrastructure can be implemented alongside US1-US4
- US7 (Vault) can be implemented alongside US4 (Execution)

---

## Independent Test Criteria Per Story

| User Story | Independent Test | Success Indicator |
|------------|------------------|-------------------|
| US1 - Multi-Channel Monitoring | Send test email/WhatsApp/LinkedIn message | Action item appears in /Needs_Action/ within 2 minutes with correct YAML frontmatter |
| US2 - Intelligent Triage | Create test action items in /Needs_Action, run needs-action-triage skill | Plan.md files appear in /Plans/ with correct classification (auto-approve vs require-approval) |
| US3 - HITL Approval Workflow | Create approval request in /Pending_Approval, move to /Approved/ or /Rejected/ | Approved items queued for execution, rejected items archived with reason, no execution |
| US4 - External Action Execution | Create pre-approved email action in /Approved/ (dry-run mode), run mcp-executor | Email logged (not sent), action moved to /Done/, audit log entry created |
| US5 - Security & Audit Logging | Execute test action in dry-run mode | /Logs/YYYY-MM-DD.json created with correct schema, credentials redacted |
| US6 - Graceful Degradation | Kill watcher process, simulate network timeout | Watcher auto-restarts within 60 seconds, retry logic kicks in with exponential backoff |
| US7 - Vault Integration | Move action item through workflow with custom YAML frontmatter | Frontmatter preserved at each step, Dashboard.md updated with statistics |
| US8 - Multi-Watcher Orchestration | Run multi-watcher-runner skill | All watchers start successfully, log heartbeats every 60 seconds, resume from last state on restart |

---

## Suggested MVP Scope

**MVP = User Story 1 (Multi-Channel Monitoring) + Foundational Components**

This delivers immediate value by consolidating all incoming communications (Gmail, WhatsApp, LinkedIn) into the Obsidian vault, building on Bronze tier's filesystem watcher. The MVP is independently testable and provides standalone value without triage, approval, or execution features.

**MVP Tasks**: T001-T035 (47 tasks total)
**Estimated MVP Duration**: 3-5 days for experienced developer

**Post-MVP Increments**:
- Increment 2: Add US2 (Triage) + US3 (Approval) for HITL workflow
- Increment 3: Add US5 (Audit) + US4 (Execution) for external actions
- Increment 4: Add US6-US8 for production polish (degradation, vault integration, orchestration)

---

## Validation Checklist

- ✅ All tasks follow checklist format (`- [ ] [TaskID] [P?] [Story?] Description with file path`)
- ✅ Tasks organized by user story priority (P1 stories before P2)
- ✅ Each user story phase has independent test criteria
- ✅ Setup and Foundational phases have no story labels (blocking prerequisites)
- ✅ User story phase tasks have story labels ([US1], [US2], etc.)
- ✅ Parallelizable tasks marked with [P]
- ✅ File paths included in all implementation tasks
- ✅ Dependency graph shows story completion order
- ✅ MVP scope clearly defined (US1 + Foundational)
- ✅ Independent test criteria documented for each story

---

## Next Steps

1. **Review & Prioritize**: Confirm MVP scope and user story priorities
2. **Execute MVP**: Complete Phase 1, Phase 2, and Phase 3 (US1) - 35 tasks
3. **Test MVP**: Verify multi-channel monitoring works end-to-end
4. **Iterate**: Add US2-US8 incrementally, testing after each increment
5. **Production Deploy**: Complete Phase 11 (Polish) and deploy with PM2

**Total Implementation Estimate**: 10-15 days for full Silver tier (95 tasks)

