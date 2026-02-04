---
id: 0002
title: Silver Tier Technical Planning
stage: plan
date: 2026-01-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-silver-ai-employee
branch: 002-silver-ai-employee
user: uneezaismail
command: /sp.plan
labels: ["planning", "silver-tier", "architecture", "fastmcp", "playwright", "gmail-api", "mcp-servers", "hitl", "audit-logging"]
links:
  spec: specs/002-silver-ai-employee/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-silver-ai-employee/plan.md
 - specs/002-silver-ai-employee/research.md
 - specs/002-silver-ai-employee/data-model.md
 - specs/002-silver-ai-employee/contracts/email_mcp.md
 - specs/002-silver-ai-employee/contracts/linkedin_mcp.md
 - specs/002-silver-ai-employee/contracts/browser_mcp.md
 - specs/002-silver-ai-employee/quickstart.md
 - CLAUDE.md (updated with Silver tier technologies)
tests:
 - none (planning phase)
---

## Prompt

Implement Silver Tier using Python 3.13+ with FastMCP for MCP servers, Playwright for browser automation (WhatsApp Web, payments), and PM2 for process management. Architecture follows HACKATHON-ZERO.md (Lines 1200-1250):

**Perception Layer**: Multiple watchers - Gmail (OAuth 2.0 via Google API), WhatsApp Web (Playwright), LinkedIn (API/Playwright), filesystem (watchdog library, already in Bronze).

**Reasoning Layer**: Claude Code with existing skills in .claude/skills/ (needs-action-triage, approval-workflow-manager, mcp-executor, multi-watcher-runner, audit-logger, obsidian-vault-ops).

**Action Layer**: Three FastMCP servers - email_mcp.py (Gmail API + SMTP fallback), linkedin_mcp.py (LinkedIn API), browser_mcp.py (Playwright for forms/payments).

**Orchestration Layer**: orchestrator.py (watches /Approved/ folder, routes to MCP servers, handles retry logic with exponential backoff). Use PM2 for process management (pm2 start ecosystem.config.js) as recommended in HACKATHON-ZERO.md Lines 1297-1315.

**HITL Workflow**: /Needs_Action → /Pending_Approval → human decision → /Approved → orchestrator.py executes → /Done or /Failed.

**Audit Logging**: /Logs/YYYY-MM-DD.json in JSONL format with credential sanitization (API keys show first 4 chars, passwords redacted, credit cards show last 4 digits).

**Graceful Degradation**: Retry logic (max 3 attempts: immediate, 25s, 2h), local queuing when APIs down, watchdog monitoring for crashed processes.

**Security**: All credentials in .env (gitignored), dry-run mode (DRY_RUN=true), permission boundaries in Company_Handbook.md.

**During planning and implementation**: Use Context7 MCP to query FastMCP, Playwright, Gmail API, and LinkedIn API documentation. Leverage existing Claude Code skills for vault operations and workflow management. Reference constitution v2.0.0 for all architectural decisions.

**Testing Strategy**: Independent MCP server tests, end-to-end approval workflow tests, credential sanitization tests, graceful degradation tests. All Bronze tier tests must continue passing.

## Response snapshot

Created comprehensive technical plan for Silver Tier AI Employee with complete architecture, technology research, data model, MCP server contracts, and deployment guide.

**Phase 0: Research & Technology Decisions** (research.md):
- FastMCP: Selected `/jlowin/fastmcp` for MCP server framework with Pydantic v2 validation, tool/resource decorators, production-ready features
- Playwright: Selected `/microsoft/playwright-python` for browser automation with session persistence, cross-browser support, reliable automation
- Gmail API: Selected official Google API with OAuth 2.0, push notifications via watch API, SMTP fallback for reliability
- LinkedIn API: Selected official API with Playwright fallback for unsupported features
- PM2: Recommended for process management with auto-restart, log management, startup persistence
- All technology choices verified via Context7 MCP queries with code examples and best practices

**Phase 1: Design Artifacts**:

1. **plan.md**: Complete technical plan with:
   - Technical Context: Python 3.13+, FastMCP, Playwright, Gmail API, OAuth 2.0, PM2
   - Constitution Check: ✅ ALL 9 PRINCIPLES PASS (Bronze-First, Local-First Vault, Agent Skills, Vault Safety, Secure Configuration, Testable Implementation, HITL, Audit Logging, Graceful Degradation)
   - Project Structure: Four-layer architecture (Perception, Reasoning, Action, Orchestration) with clear separation of concerns
   - Implementation Notes: Critical path components, integration points with existing skills, security considerations, performance targets, deployment strategy

2. **data-model.md**: Complete entity definitions with:
   - 8 core entities: Action Item, Approval Request, Approved Action, Execution Record (Done), Execution Record (Failed), Audit Log Entry, Company Handbook, Dashboard
   - YAML frontmatter schemas for all entities with validation rules
   - State transition diagram showing complete lifecycle from watcher to audit log
   - Relationship mapping between entities
   - Integrity checks: duplicate detection, YAML preservation, audit log sanitization

3. **contracts/** (3 MCP server contracts):
   - **email_mcp.md**: Gmail API + SMTP fallback, tools (send_email, draft_email, search_mail), OAuth 2.0 authentication, retry logic, audit logging
   - **linkedin_mcp.md**: LinkedIn API + Playwright fallback, tools (create_post, schedule_post, get_post_analytics), rate limit handling, session management
   - **browser_mcp.md**: Playwright automation, tools (navigate_to, fill_form, click_element, send_whatsapp_message, extract_text, take_screenshot), WhatsApp Web session persistence, payment form automation

4. **quickstart.md**: Complete setup and deployment guide with:
   - Prerequisites checklist (Bronze tier complete, Python 3.13+, Node.js, accounts)
   - Installation steps (uv, PM2, dependencies, Playwright browsers)
   - Authentication setup for Gmail API (OAuth 2.0), SMTP (app passwords), LinkedIn API, WhatsApp Web (QR code)
   - Vault folder creation and Company_Handbook.md configuration
   - PM2 deployment with ecosystem.config.js
   - Testing procedures for all three user stories (P1, P2, P3)
   - Monitoring, troubleshooting, security checklist, backup/recovery

**Agent Context Update**:
- Updated CLAUDE.md with Silver tier technologies: FastMCP, Playwright, Gmail API, OAuth 2.0, JSONL audit logs
- Preserved Bronze tier technologies (watchdog, python-frontmatter)
- Added project type: Single project with multiple components

**Constitution Alignment**:
- ✅ Principle I: Silver tier is ADDITIVE to Bronze (Bronze remains operational)
- ✅ Principle II: All state in vault markdown with Silver folders added
- ✅ Principle III: All AI behavior via existing Claude Code skills
- ✅ Principle IV: YAML frontmatter preserved, no destructive operations
- ✅ Principle V: Credentials in .env, audit logs sanitized, DRY_RUN mode
- ✅ Principle VI: Minimal diffs, resilient watchers, comprehensive testing
- ✅ Principle VII: HITL approval workflow for all external actions
- ✅ Principle VIII: Comprehensive audit logging with credential sanitization
- ✅ Principle IX: Graceful degradation with retry logic and error recovery

## Outcome

- ✅ Impact: Created production-ready technical architecture for Silver Tier AI Employee with four-layer design (Perception, Reasoning, Action, Orchestration), three FastMCP servers (email, LinkedIn, browser), multiple watchers (Gmail, WhatsApp, LinkedIn, filesystem), HITL approval workflow, comprehensive audit logging, and graceful degradation. All design decisions verified via Context7 MCP queries and aligned with constitution v2.0.0 principles. Architecture follows HACKATHON-ZERO.md specification (Lines 1200-1250) with clear separation of concerns and additive approach preserving Bronze tier functionality.

- 🧪 Tests: Not applicable (planning phase). Testing strategy defined: unit tests for watchers/MCP servers/orchestrator, integration tests for approval workflow/credential sanitization/graceful degradation, E2E tests for three user stories (P1: Client Email Response, P2: LinkedIn Business Post, P3: WhatsApp Client Message). All Bronze tier tests must continue passing.

- 📁 Files: Created plan.md (technical architecture), research.md (technology decisions with Context7 research), data-model.md (8 entities with schemas and state transitions), contracts/ (3 MCP server API contracts), quickstart.md (setup and deployment guide). Updated CLAUDE.md with Silver tier technologies.

- 🔁 Next prompts: Run `/sp.tasks` to generate actionable task breakdown from plan.md. Tasks will include: (1) Create vault folders, (2) Implement watchers (Gmail, WhatsApp, LinkedIn), (3) Implement MCP servers (email, LinkedIn, browser), (4) Implement orchestrator.py, (5) Configure PM2, (6) Write tests, (7) End-to-end validation. Use Context7 MCP during implementation for FastMCP, Playwright, Gmail API documentation.

- 🧠 Reflection: Planning phase successfully completed with comprehensive architecture covering all Silver tier requirements. Key decisions: (1) FastMCP for MCP servers provides Pythonic framework with Pydantic validation, (2) Playwright for browser automation enables WhatsApp Web and payment forms with session persistence, (3) Gmail API with SMTP fallback ensures email reliability, (4) PM2 for process management provides production-grade auto-restart and monitoring, (5) Four-layer architecture (Perception/Reasoning/Action/Orchestration) provides clear separation of concerns. All technology choices verified via Context7 MCP with code examples. Constitution v2.0.0 principles fully satisfied with no violations. Ready for task generation and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning phase completed successfully with all artifacts generated and constitution checks passing.
- Graders run and results (PASS/FAIL): Constitution Check: PASS (all 9 principles satisfied). Technology research: PASS (all libraries verified via Context7 MCP). Data model: PASS (complete entity definitions with validation rules). MCP contracts: PASS (comprehensive API specifications with examples).
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Proceed with `/sp.tasks` to generate actionable task breakdown. During implementation, use Context7 MCP to query FastMCP, Playwright, and Gmail API documentation for code examples and best practices. Leverage existing Claude Code skills (needs-action-triage, approval-workflow-manager, mcp-executor, multi-watcher-runner, audit-logger, obsidian-vault-ops) for vault operations and workflow management.
