# Implementation Plan: Silver Tier AI Employee

**Branch**: `002-silver-tier-ai-employee` | **Date**: 2026-01-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-silver-tier-ai-employee/spec.md`

## Summary

Transform the Bronze tier AI Employee from a local-only perception-reasoning system into a production-ready autonomous assistant capable of executing real-world external actions (emails, LinkedIn posts, WhatsApp messages) under strict human-in-the-loop (HITL) oversight with comprehensive security and audit logging. This implements a four-layer architecture: **Perception** (multi-channel watchers) → **Reasoning** (Claude Code skills for triage and planning) → **Human Approval** (file-based workflow in Obsidian vault) → **Action** (FastMCP servers for external integrations).

**Core Value Proposition**: Enable trusted automation of external communications and tasks while maintaining complete human control through vault-based approval workflows, comprehensive audit trails, and graceful degradation when components fail.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**:
- **Core**: uv (package management), pytest (testing), python-frontmatter (YAML parsing), python-dotenv (env management)
- **Bronze Tier**: watchdog (filesystem events)
- **Silver Tier Additions**:
  - fastmcp (MCP server framework with Pydantic v2)
  - playwright (browser automation for WhatsApp Web)
  - google-api-python-client, google-auth-oauthlib, google-auth-httplib2 (Gmail OAuth2)
  - requests (LinkedIn API, generic HTTP)

**Storage**:
- **Primary**: Obsidian vault (markdown files with YAML frontmatter) at `AI_Employee_Vault/`
- **Logs**: Daily JSON files (`/Logs/YYYY-MM-DD.json`)
- **State**: Deduplication tracking (`.gmail_dedupe.json`, `.whatsapp_dedupe.json`, `.linkedin_dedupe.json`)
- **Sessions**: OAuth tokens (`token.json`), Browser contexts (`.whatsapp_session/`)

**Testing**:
- pytest with fixtures for temporary vault creation
- Unit tests for watchers, MCP servers, vault operations, credential sanitization
- Integration tests for end-to-end workflows (Needs_Action → Pending_Approval → Approved → Done)
- Security tests for credential leakage, dry-run mode verification

**Target Platform**:
- Development: Windows, macOS, Linux (any OS with Python 3.13+)
- Production: Long-running processes via PM2 (Node.js process manager) or custom watchdog.py

**Project Type**: Single Python project with modular architecture (watchers, MCP servers, vault operations, skills integration)

**Performance Goals**:
- Action item creation: <2 minutes from detection to `/Needs_Action/`
- Triage processing: <30 seconds per action item
- Execution: <5 minutes end-to-end (detection → approval → execution → logging)
- Component restart: <60 seconds via watchdog/PM2

**Constraints**:
- **Security**: Zero credentials in vault/repository (100% in `.env`), mandatory credential sanitization in logs
- **Reliability**: Component failure isolation (watcher crash cannot cascade), exponential backoff retry (1s, 2s, 4s, max 3 attempts)
- **Auditability**: 100% external action logging with 90-day retention
- **Human Control**: All external actions require approval unless explicitly auto-approved in `Company_Handbook.md`
- **Backward Compatibility**: All Bronze tier tests must continue passing

**Scale/Scope**:
- 4 watcher processes (Gmail, WhatsApp, LinkedIn, filesystem)
- 3 MCP servers (email, LinkedIn, browser automation)
- 6 Claude Code skills (triage, approval-manager, mcp-executor, multi-watcher-runner, vault-ops, audit-logger)
- 9 vault folders (Bronze: Inbox, Needs_Action, Plans, Done | Silver: Pending_Approval, Approved, Rejected, Failed, Logs)
- 45 functional requirements across 6 categories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I - Local-First Personal AI Employee ✅ PASS
- **Bronze tier preserved**: Filesystem watcher continues working, all Bronze vault operations functional
- **Silver tier additions**: Multi-watcher infrastructure (Gmail, WhatsApp, LinkedIn), FastMCP servers for external actions
- **Architecture**: Four-layer flow maintained (Perception → Reasoning → Approval → Action)
- **Rationale**: Silver builds on Bronze foundations without breaking existing functionality

### Principle II - Vault Safety and Non-Destructive Operations ✅ PASS
- **No deletions**: All operations use moves to `/Done/`, `/Rejected/`, `/Failed/` for archival
- **YAML preservation**: All file moves must preserve frontmatter exactly (enforced by obsidian-vault-ops skill)
- **Atomic operations**: obsidian-vault-ops implements atomic file writes to prevent corruption
- **Rationale**: Vault remains single source of truth with full audit trail

### Principle III - Human-as-Tool Principle ✅ PASS
- **Clarification points**:
  - Vault path configuration (via `.env` with validation on startup)
  - Permission boundaries (documented in `Company_Handbook.md`, defaults to require-approval)
  - API credential setup (setup scripts guide user through OAuth flow)
- **Implementation**: Skills will use AskUserQuestion for ambiguous scenarios (e.g., "Which email accounts should auto-approve?")
- **Rationale**: HITL approval workflow embodies this principle - humans remain in decision loop

### Principle IV - Watcher Resilience and Idempotency ✅ PASS
- **Production-grade requirements**:
  - Deduplication via source_id hashing (SHA256 content + source prefix)
  - Graceful error handling (log and continue, never crash on single malformed input)
  - Heartbeat logging every 60 seconds for health monitoring
  - Atomic action item creation (write to temp file, then move to `/Needs_Action/`)
- **Rationale**: 24/7 operation demands resilience

### Principle V - Secret Management and Security ✅ PASS (with enforcement mechanisms)
- **Bronze requirements maintained**: No secrets in repo, `.env` gitignored, PII sanitization in logs
- **Silver additions**:
  - All OAuth tokens, API keys, session cookies in `.env` only
  - Startup validation: fail fast if credentials missing or vault has secrets
  - Audit log sanitization: `<REDACTED_TOKEN>`, `<REDACTED_PII>` placeholders
  - Dry-run mode (`DRY_RUN=true`) for safe testing
- **90-day log retention**: Logs in `/Logs/` excluded from git
- **Rationale**: External actions raise security stakes; proactive enforcement prevents leaks

### Principle VI - Technology Stack and Implementation Constraints ✅ PASS
- **Bronze stack preserved**: Python 3.13+, uv, pytest, watchdog
- **Silver additions justified**:
  - **FastMCP**: Industry-standard MCP framework with Pydantic v2 validation
  - **Playwright**: Only reliable option for WhatsApp Web scraping (no official API)
  - **PM2**: Battle-tested process manager for 24/7 operation (10M+ downloads/month)
  - **Google Auth Libraries**: Official OAuth2 implementation for Gmail API
- **Minimal complexity**: No custom authentication, no exotic frameworks
- **Rationale**: Proven tools reduce risk; standard patterns enable maintainability

### Principle VII - Test-Driven Development for Core Logic ✅ PASS
- **Bronze tests maintained**: All existing filesystem watcher, vault operation, plan generation tests continue passing
- **Silver test additions**:
  - MCP server unit tests with mocked credentials
  - Approval workflow integration tests (Needs_Action → Pending_Approval → Approved → execution)
  - Security tests (credential sanitization, dry-run mode, permission boundaries)
  - Graceful degradation tests (component failure scenarios, retry logic)
- **Coverage target**: 80%+ for critical paths (watchers, MCP execution, audit logging)
- **Rationale**: External actions have real-world consequences; tests are safety nets

### Principle VIII - Human-in-the-Loop (HITL) Approval Workflow ✅ PASS (Core Feature)
- **Default behavior**: ALL external actions require approval
- **Approval flow**: Needs_Action → Pending_Approval (with risk assessment) → human moves to Approved/Rejected → execution or archival
- **Permission boundaries**: Optional auto-approve thresholds in `Company_Handbook.md` (e.g., "emails to pre-approved contacts")
- **Rejection handling**: Moves to `/Rejected/` with reason, never executes
- **Rationale**: This principle IS the Silver tier - human oversight prevents catastrophic errors

### Principle IX - Security and Audit Logging ✅ PASS (Core Feature)
- **Mandatory logging**: Every external action logged to `/Logs/YYYY-MM-DD.json` (cannot be disabled)
- **Schema compliance**: timestamp, action_id, action_type, user, ai_agent, mcp_server, tool_name, execution_status, error, retry_count
- **Credential sanitization**: Redact tokens, passwords, PII before writing
- **90-day retention**: Logs older than 90 days archived (not deleted)
- **Rationale**: Audit trail enables compliance, debugging, security incident response

### Principle X - Graceful Degradation and Error Handling ✅ PASS (Core Feature)
- **Component isolation**: Each watcher runs as independent process (crash doesn't cascade)
- **Retry logic**: Exponential backoff (1s, 2s, 4s) with max 3 retries for transient failures
- **Dead letter queue**: Failed executions → `/Failed/` folder for manual intervention
- **Health monitoring**: Heartbeat every 60 seconds, watchdog/PM2 auto-restart within 60 seconds
- **Graceful shutdown**: SIGTERM/SIGINT handlers ensure in-flight operations complete
- **Rationale**: Production systems will fail; degradation strategy prevents total outage

### Constitution Compliance Summary
**Status**: ✅ **ALL GATES PASS**

No violations requiring justification. Silver tier is designed from the ground up to extend Bronze principles with production-grade external action execution under strict human oversight.

## Project Structure

### Documentation (this feature)

```text
specs/002-silver-tier-ai-employee/
├── spec.md              # Feature requirements (COMPLETE)
├── plan.md              # This file (IN PROGRESS - Phase 0/1)
├── research.md          # Phase 0 output (PENDING - technology decisions)
├── data-model.md        # Phase 1 output (PENDING - entity schemas)
├── quickstart.md        # Phase 1 output (PENDING - setup guide)
├── contracts/           # Phase 1 output (PENDING - MCP OpenAPI specs)
│   ├── email-mcp.json
│   ├── linkedin-mcp.json
│   └── browser-mcp.json
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Structure Decision**: Single Python project with modular architecture. Silver tier extends the existing `My_AI_Employee/` structure established in Bronze tier.

```text
My_AI_Employee/
├── src/my_ai_employee/
│   ├── watchers/                    # Perception layer
│   │   ├── base_watcher.py          # Abstract base class for all watchers
│   │   ├── filesystem_watcher.py    # Bronze tier (existing)
│   │   ├── gmail_watcher.py         # NEW: Gmail OAuth2 + API monitoring
│   │   ├── whatsapp_watcher.py      # NEW: Playwright-based WhatsApp Web scraping
│   │   └── linkedin_watcher.py      # NEW: LinkedIn API/Playwright monitoring
│   │
│   ├── mcp_servers/                 # Action layer (NEW)
│   │   ├── email_mcp.py             # FastMCP server for Gmail sending
│   │   ├── linkedin_mcp.py          # FastMCP server for LinkedIn posting
│   │   └── browser_mcp.py           # FastMCP server for WhatsApp/browser automation
│   │
│   ├── vault_ops/                   # Vault integration (Bronze + Silver)
│   │   ├── action_item_reader.py    # Read action items from /Needs_Action/
│   │   ├── plan_writer.py           # Write plans to /Plans/
│   │   ├── dashboard_updater.py     # Update Dashboard.md with statistics
│   │   ├── item_archiver.py         # Move items to /Done/, /Rejected/, /Failed/
│   │   └── vault_validator.py       # Validate vault structure on startup
│   │
│   ├── approval/                    # HITL workflow (NEW)
│   │   ├── approval_request.py      # Create/validate approval request files
│   │   └── permission_boundaries.py # Parse auto-approve rules from Company_Handbook.md
│   │
│   ├── models/                      # Data schemas
│   │   ├── action_item.py           # ActionItemSchema dataclass (Bronze + Silver fields)
│   │   ├── approval_request.py      # ApprovalRequestSchema dataclass
│   │   └── audit_log.py             # AuditLogEntry dataclass
│   │
│   ├── utils/                       # Shared utilities
│   │   ├── frontmatter_utils.py     # YAML frontmatter parsing (Bronze)
│   │   ├── auth_helper.py           # NEW: OAuth2 token management for Gmail
│   │   ├── sanitizer.py             # NEW: Credential redaction for audit logs
│   │   ├── dedupe_state.py          # NEW: Deduplication state persistence
│   │   └── audit_logger.py          # NEW: Structured JSON logging to /Logs/
│   │
│   ├── orchestrator.py              # NEW: Central orchestration (watches /Approved/, triggers execution)
│   ├── run_watcher.py               # NEW: Unified watcher launcher (CLI entry point)
│   └── config.py                    # NEW: Centralized configuration loading from .env
│
├── tests/
│   ├── unit/
│   │   ├── test_action_item_format.py
│   │   ├── test_approval_workflow.py
│   │   ├── test_audit_logger.py
│   │   ├── test_sanitizer.py
│   │   └── test_watcher_core.py
│   │
│   ├── integration/
│   │   ├── test_gmail_watcher.py
│   │   ├── test_whatsapp_watcher.py
│   │   ├── test_linkedin_watcher.py
│   │   ├── test_email_mcp.py
│   │   ├── test_linkedin_mcp.py
│   │   ├── test_browser_mcp.py
│   │   └── test_orchestrator.py
│   │
│   └── e2e/
│       ├── test_bronze_compatibility.py  # Ensure Bronze tests still pass
│       └── test_silver_workflow.py       # Needs_Action → Pending_Approval → Approved → Done
│
├── scripts/
│   ├── setup/
│   │   ├── setup_gmail_oauth.py      # NEW: Interactive OAuth2 flow for Gmail
│   │   ├── complete_oauth.py         # NEW: OAuth callback handler
│   │   └── linkedin_oauth2_setup.py  # NEW: LinkedIn token acquisition
│   │
│   ├── debug/
│   │   ├── debug_gmail.py            # NEW: Test Gmail connection
│   │   ├── debug_gmail_send.py       # NEW: Test email sending
│   │   └── debug_pm2_dashboard.py    # NEW: PM2 health monitoring
│   │
│   └── validate/
│       └── validate_silver_tier.py   # NEW: Pre-deployment validation checks
│
├── .claude/
│   └── skills/
│       ├── approval-workflow-manager/  # NEW: HITL approval skill
│       ├── audit-logger/               # NEW: Logging skill
│       ├── mcp-executor/               # NEW: Execution skill
│       ├── multi-watcher-runner/       # NEW: Orchestration skill
│       ├── needs-action-triage/        # Updated: Bronze + Silver classification
│       ├── obsidian-vault-ops/         # Updated: Bronze + Silver folders
│       └── bronze-demo-check/          # Existing: Bronze validation
│
├── AI_Employee_Vault/               # Obsidian vault (NOT in repo)
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Inbox/                       # Bronze
│   ├── Needs_Action/                # Bronze
│   ├── Plans/                       # Bronze
│   ├── Done/                        # Bronze
│   ├── Pending_Approval/            # NEW: Silver
│   ├── Approved/                    # NEW: Silver
│   ├── Rejected/                    # NEW: Silver
│   ├── Failed/                      # NEW: Silver (dead letter queue)
│   └── Logs/                        # NEW: Silver (YYYY-MM-DD.json)
│
├── ecosystem.config.js              # NEW: PM2 process configuration
├── pyproject.toml                   # Updated: Bronze + Silver dependencies
├── .env.example                     # NEW: Template for credentials
├── .gitignore                       # Updated: Add .env, /Logs/, *_dedupe.json, token.json, .whatsapp_session/
└── README.md                        # Updated: Silver tier setup instructions
```

**Rationale**:
- **Modular separation**: Watchers, MCP servers, vault ops, approval logic cleanly separated for independent testing
- **Bronze compatibility**: Existing `src/my_ai_employee/watchers/filesystem_watcher.py` and vault ops preserved
- **Testability**: Unit, integration, and E2E tests mirror source structure
- **Production ops**: Scripts for setup, debug, validation support real-world deployment

## Complexity Tracking

> **No complexity violations - all design choices align with constitution principles**

Silver tier introduces production-grade features (multi-watcher, MCP servers, HITL approval, audit logging) that are explicitly mandated by the constitution's Silver tier principles (VIII, IX, X). All technology choices (FastMCP, Playwright, PM2, Google Auth) are industry-standard tools that minimize implementation risk.

---

## Post-Design Constitution Re-Evaluation

**Date**: 2026-01-22 (After Phase 0 research + Phase 1 design)

### Verification Summary

✅ **All constitution principles remain satisfied** after completing Phase 1 design artifacts:
- `research.md` - Technology decisions documented with alternatives considered
- `data-model.md` - Entity schemas with validation rules and state transitions
- `contracts/` - MCP server OpenAPI specs (email, LinkedIn, browser)
- `quickstart.md` - Production deployment guide with security checklist

### Design Compliance Review

| Principle | Status | Post-Design Notes |
|-----------|--------|-------------------|
| I - Local-First AI Employee | ✅ PASS | Four-layer architecture (Perception → Reasoning → Approval → Action) preserved in all design docs |
| II - Vault Safety | ✅ PASS | data-model.md enforces non-destructive operations, state transitions only move files (never delete) |
| III - Human-as-Tool | ✅ PASS | quickstart.md guides user through OAuth setup, Company_Handbook configuration |
| IV - Watcher Resilience | ✅ PASS | research.md documents deduplication strategy (SHA256 hashing), heartbeat logging every 60s |
| V - Secret Management | ✅ PASS | data-model.md shows all credentials in .env, quickstart.md has security checklist preventing leaks |
| VI - Technology Stack | ✅ PASS | research.md justifies all dependencies (FastMCP, Playwright, PM2, Google Auth) with alternatives considered |
| VII - Test-Driven Development | ✅ PASS | project structure includes tests/ directory with unit/integration/e2e tests planned |
| VIII - HITL Approval Workflow | ✅ PASS | data-model.md defines ApprovalRequest schema, contracts/ show execution preview in approval requests |
| IX - Security & Audit Logging | ✅ PASS | data-model.md defines AuditLogEntry schema with credential sanitization requirements |
| X - Graceful Degradation | ✅ PASS | research.md documents exponential backoff retry logic, MCP contracts define error handling |

### Architectural Decisions Requiring ADR

Based on Phase 1 design, the following decisions meet ADR significance criteria (Impact + Alternatives + Cross-cutting scope):

1. **MCP Server Framework Selection** (FastMCP vs Custom JSON-RPC)
   - **Impact**: All external actions depend on MCP server reliability
   - **Alternatives**: FastMCP, mcp-python SDK, custom implementation
   - **Scope**: Cross-cutting for all 3 MCP servers (email, LinkedIn, browser)
   - **📋 Suggested ADR**: "ADR-001: FastMCP Framework for External Action Execution"

2. **Browser Automation Strategy** (Playwright vs Selenium vs WhatsApp Business API)
   - **Impact**: Long-term WhatsApp integration maintainability
   - **Alternatives**: Playwright, Selenium, WhatsApp Business API (rejected - requires business account)
   - **Scope**: Affects WhatsApp watcher reliability and session management
   - **📋 Suggested ADR**: "ADR-002: Playwright for WhatsApp Web Automation"

3. **Process Management** (PM2 vs Supervisor vs systemd)
   - **Impact**: 24/7 production reliability and auto-restart behavior
   - **Alternatives**: PM2, Supervisor, systemd, Docker Compose
   - **Scope**: Cross-platform deployment strategy
   - **📋 Suggested ADR**: "ADR-003: PM2 for Multi-Watcher Process Orchestration"

**User Action Required**: After tasks phase, run `/sp.adr` for each decision above to document rationale and trade-offs.

### Design Artifacts Status

| Artifact | Status | Lines | Key Content |
|----------|--------|-------|-------------|
| plan.md | ✅ Complete | ~400 | Technical context, constitution check, project structure |
| research.md | ✅ Complete | ~550 | 10 technology decisions with alternatives and justifications |
| data-model.md | ✅ Complete | ~650 | 6 entity schemas (Action Item, Plan, Approval, Audit, Watcher State, Config) |
| contracts/email-mcp.json | ✅ Complete | ~150 | send_email + health_check tools, OAuth2 auth, dry-run mode |
| contracts/linkedin-mcp.json | ✅ Complete | ~140 | publish_post + health_check tools, rate limits, visibility control |
| contracts/browser-mcp.json | ✅ Complete | ~130 | send_whatsapp_message + health_check tools, session persistence |
| quickstart.md | ✅ Complete | ~450 | 10-step setup guide, OAuth flows, PM2 deployment, security checklist |

**Total Design Documentation**: ~2470 lines across 7 files

### Ready for Phase 2 (Tasks)

✅ All prerequisites for `/sp.tasks` command satisfied:
- Technical context complete with all dependencies identified
- Data model defined with validation rules
- MCP server contracts specify all tools and error codes
- Quickstart guide provides production deployment steps
- Constitution compliance verified post-design

**Next Command**: `/sp.tasks` to generate implementation tasks from this plan

