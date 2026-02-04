# Implementation Plan: Silver Tier AI Employee

**Branch**: `002-silver-ai-employee` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-silver-ai-employee/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build Silver Tier Personal AI Employee that monitors multiple communication channels (Gmail, WhatsApp, LinkedIn), reasons about required actions using Claude Code with existing skills, routes external actions through Human-in-the-Loop (HITL) approval workflow, and executes approved actions via FastMCP servers. Architecture follows HACKATHON-ZERO.md with four layers: Perception (watchers), Reasoning (Claude Code + skills), Action (MCP servers), and Orchestration (orchestrator.py + PM2).

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastMCP (MCP server framework with Pydantic v2), Playwright (browser automation), google-api-python-client (Gmail API), google-auth-oauthlib (OAuth 2.0), watchdog (filesystem monitoring, already in Bronze), python-frontmatter (YAML parsing, already in Bronze)
**Storage**: Obsidian vault (local markdown files), JSONL audit logs (/Logs/YYYY-MM-DD.json), local queue files for offline resilience
**Testing**: pytest (unit tests for MCP servers, integration tests for approval workflow, end-to-end tests for complete user stories)
**Target Platform**: Linux/macOS/WSL2 (local development and production), requires Node.js for PM2 process management
**Project Type**: Single project with multiple components (watchers, MCP servers, orchestrator, skills)
**Performance Goals**: Action items appear within 2 minutes of triggering event, approved actions execute within 10 seconds, watchers poll every 30-60 seconds, orchestrator checks /Approved/ folder every 5 seconds
**Constraints**: All credentials in .env (gitignored), audit logs sanitize sensitive data, retry logic max 3 attempts with exponential backoff (immediate, 25s, 2h), 90-day audit log retention minimum, Bronze tier functionality must remain operational
**Scale/Scope**: Single user, 3 communication channels (Gmail, WhatsApp, LinkedIn), 3 MCP servers (email, LinkedIn, browser), 6 existing Claude Code skills, ~2000 lines of new Python code (watchers + MCP servers + orchestrator)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Bronze-First, Silver-Second Scope
- **Status**: PASS
- **Verification**: Bronze tier (filesystem watcher + vault + skills) is complete and operational. Silver tier is ADDITIVE - adds multiple watchers, MCP servers, HITL workflow, orchestrator.py. Bronze functionality remains unchanged.

### ✅ Principle II: Local-First Vault as Source of Truth
- **Status**: PASS
- **Verification**: All operational state stored in vault markdown. Adding Silver folders: /Pending_Approval/, /Approved/, /Rejected/, /Failed/, /Logs/. Vault path: My_AI_Employee/AI_Employee_Vault/. Bronze folders remain intact.

### ✅ Principle III: Agent Skills for All AI Behavior
- **Status**: PASS
- **Verification**: All AI workflows implemented via existing skills in .claude/skills/ (needs-action-triage, approval-workflow-manager, mcp-executor, multi-watcher-runner, audit-logger, obsidian-vault-ops). No hidden manual steps except starting watchers and MCP servers.

### ✅ Principle IV: Vault Safety and Non-Destructive Operations
- **Status**: PASS
- **Verification**: Watchers and orchestrator preserve YAML frontmatter when moving files. No deletion of user-authored content. Dashboard.md updates use append/section updates.

### ✅ Principle V: Secure Configuration and Secrets Hygiene
- **Status**: PASS
- **Verification**: All credentials in .env (gitignored). Audit logs sanitize: API keys (first 4 chars + ***), passwords (redacted), credit cards (last 4 digits), PII (truncated). DRY_RUN=true mode for testing. 90-day audit log retention.

### ✅ Principle VI: Testable, Minimal, Reliable Implementation
- **Status**: PASS
- **Verification**: Minimal diffs - only adding Silver components. Watchers resilient with error logging and duplicate prevention. Testing: MCP server unit tests, approval workflow integration tests, credential sanitization tests, graceful degradation tests. All Bronze tests continue passing.

### ✅ Principle VII: Human-in-the-Loop (HITL) Approval Workflow
- **Status**: PASS
- **Verification**: All external actions route to /Pending_Approval/. Human moves to /Approved/ before execution. Orchestrator.py watches /Approved/ and executes via MCP servers. Rejection supported via /Rejected/ folder. Approval request format includes YAML frontmatter with type, action_type, requires_approval, status, priority, created_at.

### ✅ Principle VIII: Comprehensive Audit Logging
- **Status**: PASS
- **Verification**: All external actions logged to /Logs/YYYY-MM-DD.json in JSONL format. Log entries include: timestamp (ISO8601), action_type, actor, target, approval_status, approved_by, result. Credentials sanitized. 90-day retention minimum.

### ✅ Principle IX: Graceful Degradation and Error Recovery
- **Status**: PASS
- **Verification**: Retry logic with exponential backoff (max 3 attempts: immediate, 25s, 2h). Gmail API down → queue locally. WhatsApp session expired → stop watcher, notify human. Vault locked → temporary buffer. Watchdog monitoring via PM2 process management. Dead-letter queue for failed actions.

**Overall Assessment**: ✅ ALL GATES PASS - Ready for Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/002-silver-ai-employee/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already created)
├── research.md          # Phase 0 output (technology research)
├── data-model.md        # Phase 1 output (entities and state)
├── quickstart.md        # Phase 1 output (setup instructions)
├── contracts/           # Phase 1 output (MCP server contracts)
│   ├── email_mcp.md     # Email MCP server API contract
│   ├── linkedin_mcp.md  # LinkedIn MCP server API contract
│   └── browser_mcp.md   # Browser automation MCP server API contract
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (already created)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
My_AI_Employee/
├── AI_Employee_Vault/           # Obsidian vault (Bronze + Silver)
│   ├── Inbox/                   # Bronze: manual file drops
│   ├── Needs_Action/            # Bronze + Silver: unprocessed items
│   ├── Pending_Approval/        # Silver: awaiting human decision
│   ├── Approved/                # Silver: approved for execution
│   ├── Rejected/                # Silver: rejected by human
│   ├── Failed/                  # Silver: failed executions
│   ├── Done/                    # Bronze + Silver: completed items
│   ├── Plans/                   # Bronze + Silver: planning artifacts
│   ├── Logs/                    # Silver: audit logs (YYYY-MM-DD.json)
│   ├── Dashboard.md             # Bronze + Silver: status summary
│   └── Company_Handbook.md      # Bronze + Silver: rules and preferences
│
├── watchers/                    # Perception layer
│   ├── __init__.py
│   ├── filesystem_watcher.py   # Bronze: already implemented
│   ├── gmail_watcher.py        # Silver: Gmail OAuth 2.0 watcher
│   ├── whatsapp_watcher.py     # Silver: WhatsApp Web (Playwright)
│   ├── linkedin_watcher.py     # Silver: LinkedIn API/Playwright
│   └── common/                  # Shared watcher utilities
│       ├── __init__.py
│       ├── action_item.py      # Action item creation helpers
│       ├── duplicate_detector.py # Prevent duplicate items
│       └── vault_writer.py     # Safe vault file operations
│
├── mcp_servers/                 # Action layer (FastMCP servers)
│   ├── __init__.py
│   ├── email_mcp.py            # Gmail API + SMTP fallback
│   ├── linkedin_mcp.py         # LinkedIn API integration
│   ├── browser_mcp.py          # Playwright browser automation
│   └── common/                  # Shared MCP utilities
│       ├── __init__.py
│       ├── auth.py             # OAuth/credential management
│       ├── retry.py            # Exponential backoff retry logic
│       └── sanitizer.py        # Credential sanitization for logs
│
├── orchestrator.py              # Orchestration layer (master process)
├── .env.example                 # Example environment variables
├── .env                         # Actual credentials (gitignored)
├── ecosystem.config.js          # PM2 process management config
├── pyproject.toml               # Python dependencies (uv)
└── README.md                    # Silver tier setup instructions

.claude/skills/                  # Reasoning layer (already implemented)
├── needs-action-triage/         # Process items from Needs_Action
├── approval-workflow-manager/   # Create approval requests
├── mcp-executor/                # Execute approved actions (contains run_executor.py)
├── multi-watcher-runner/        # Multi-watcher orchestration (uses run_watcher.py --watcher all)
├── audit-logger/                # Log all external actions
└── obsidian-vault-ops/          # Safe vault operations

tests/                           # Testing infrastructure
├── unit/                        # Unit tests for individual components
│   ├── test_watchers.py        # Watcher logic tests
│   ├── test_mcp_servers.py     # MCP server tests
│   └── test_orchestrator.py    # Orchestrator tests
├── integration/                 # Integration tests
│   ├── test_approval_workflow.py # End-to-end approval workflow
│   ├── test_credential_sanitization.py # Audit log sanitization
│   └── test_graceful_degradation.py # Error recovery tests
└── e2e/                         # End-to-end tests
    ├── test_client_email_response.py # User Story 1 (P1)
    ├── test_linkedin_post.py         # User Story 2 (P2)
    └── test_whatsapp_message.py      # User Story 3 (P3)
```

**Structure Decision**: Single project structure with clear separation of concerns across four layers (Perception, Reasoning, Action, Orchestration) as defined in HACKATHON-ZERO.md Lines 1200-1250. Bronze tier components (filesystem_watcher.py, existing skills, Bronze vault folders) remain unchanged. Silver tier adds new components without modifying Bronze functionality, ensuring additive architecture per Constitution Principle I.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All constitution principles pass without exceptions.

---

## Phase 0: Research & Technology Decisions

See [research.md](./research.md) for detailed technology research and decisions.

## Phase 1: Design Artifacts

See the following files for detailed design:
- [data-model.md](./data-model.md) - Entity definitions and state management
- [contracts/](./contracts/) - MCP server API contracts
- [quickstart.md](./quickstart.md) - Development setup instructions

## Implementation Notes

### Critical Path Components

1. **Watchers (Perception Layer)** - Priority: HIGH
   - Gmail watcher with OAuth 2.0 (google-api-python-client, google-auth-oauthlib)
   - WhatsApp watcher with Playwright (session persistence, QR code auth)
   - LinkedIn watcher (API or Playwright fallback)
   - Shared utilities: duplicate detection, action item creation, vault writing

2. **MCP Servers (Action Layer)** - Priority: HIGH
   - Email MCP: Gmail API primary, SMTP fallback
   - LinkedIn MCP: LinkedIn API integration
   - Browser MCP: Playwright for forms/payments
   - Shared utilities: OAuth management, retry logic, credential sanitization

3. **Orchestrator (Orchestration Layer)** - Priority: HIGH
   - Watch /Approved/ folder (5-second polling)
   - Route to appropriate MCP server based on action_type
   - Retry logic with exponential backoff (immediate, 25s, 2h)
   - Move results to /Done/ or /Failed/
   - Integrate with audit-logger skill

4. **Process Management** - Priority: MEDIUM
   - PM2 configuration (ecosystem.config.js)
   - run_watcher.py with --watcher all for multi-watcher orchestration
   - Auto-restart on crash, log management

5. **Testing Infrastructure** - Priority: MEDIUM
   - Unit tests for watchers, MCP servers, orchestrator
   - Integration tests for approval workflow, credential sanitization
   - E2E tests for three user stories (P1, P2, P3)

### Integration Points with Existing Skills

- **needs-action-triage**: Processes items from /Needs_Action/, determines if approval needed
- **approval-workflow-manager**: Creates approval requests in /Pending_Approval/
- **mcp-executor**: Contains run_executor.py (copy to My_AI_Employee/orchestrator.py)
- **multi-watcher-runner**: Multi-watcher orchestration via run_watcher.py --watcher all
- **audit-logger**: Logs all external actions with credential sanitization
- **obsidian-vault-ops**: Safe vault file operations preserving YAML frontmatter

### Security Considerations

1. **Credential Management**
   - All credentials in .env (gitignored)
   - OAuth tokens stored in OS-specific secure locations
   - Never log credentials (sanitize in audit logs)
   - DRY_RUN=true mode for testing without real actions

2. **Audit Trail**
   - JSONL format: one JSON object per line
   - Immutable during 90-day retention period
   - Sanitization rules: API keys (first 4 chars), passwords (redacted), credit cards (last 4 digits)
   - Support queries by action_type, status, actor, date range

3. **Permission Boundaries**
   - Define in Company_Handbook.md which actions auto-approve vs require approval
   - Examples: emails to known contacts (auto), payments >$50 (require approval)
   - Banking/payment actions NEVER auto-retry on failure

### Performance Targets

- **Watcher polling**: 30-60 seconds per channel
- **Action item creation**: Within 2 minutes of triggering event
- **Orchestrator polling**: 5 seconds for /Approved/ folder
- **Action execution**: Within 10 seconds of approval
- **Retry delays**: Immediate, 25s, 2h (exponential backoff)

### Deployment Strategy

1. **Development**: Local with DRY_RUN=true, test credentials
2. **Staging**: Real credentials, limited scope (test email addresses only)
3. **Production**: Full credentials, PM2 process management, monitoring enabled

---

## Next Steps

After `/sp.plan` completion:
1. Run `/sp.tasks` to generate actionable task breakdown
2. Review and approve tasks.md
3. Run `/sp.implement` to begin implementation
4. Use Context7 MCP during implementation for FastMCP, Playwright, Gmail API documentation
5. Leverage existing Claude Code skills for vault operations and workflow management
