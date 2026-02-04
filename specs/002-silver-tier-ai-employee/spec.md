# Feature Specification: Silver Tier AI Employee

**Feature Branch**: `002-silver-tier-ai-employee`
**Created**: 2026-01-18
**Status**: Draft
**Input**: User description: "Transform the AI Employee from a local-only perception-reasoning system into a production-ready autonomous assistant capable of executing real-world external actions (emails, LinkedIn posts, WhatsApp messages) under strict human-in-the-loop (HITL) oversight with comprehensive security and audit logging."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Channel Monitoring and Action Item Creation (Priority: P1)

As a busy professional, I want my AI Employee to continuously monitor my Gmail, WhatsApp, and LinkedIn accounts for important messages and notifications, automatically creating structured action items in my Obsidian vault so that I never miss critical communications and can review them in one central location.

**Why this priority**: This is the foundation of Silver tier - without multi-channel perception, no other features can function. It delivers immediate value by consolidating all incoming communications into the vault, building on Bronze tier's single-source (filesystem) monitoring.

**Independent Test**: Can be fully tested by sending test emails/messages to monitored accounts and verifying that structured markdown action items with correct YAML frontmatter appear in the /Needs_Action folder within 2 minutes. Delivers standalone value even without triage or execution features.

**Acceptance Scenarios**:

1. **Given** Gmail watcher is running, **When** an important/unread email arrives, **Then** a structured markdown file is created in /Needs_Action with type: email, sender, subject, timestamp, and email content
2. **Given** WhatsApp watcher is monitoring WhatsApp Web, **When** a message containing urgent keywords (invoice, payment, help, urgent, ASAP) is received, **Then** a markdown action item is created in /Needs_Action within 30 seconds
3. **Given** LinkedIn watcher is active, **When** a business-relevant notification occurs, **Then** an action item is created with type: linkedin and notification details
4. **Given** one watcher (e.g., Gmail) crashes, **When** another watcher (e.g., WhatsApp) continues running, **Then** the system continues creating action items from functional watchers without interruption

---

### User Story 2 - Intelligent Triage with Action Classification (Priority: P1)

As a user, I want the AI Employee to analyze incoming action items, understand their context using my Company_Handbook rules, generate detailed execution plans, and classify whether actions require my approval (external actions) or can proceed automatically (internal vault operations), so that I maintain control over sensitive operations while automating routine tasks.

**Why this priority**: Triage is the "brain" of the system - it transforms raw inputs into actionable plans with risk assessment. Without intelligent classification, users would need to manually review every single item, defeating the purpose of automation. P1 because it's essential for HITL workflow.

**Independent Test**: Manually create test action items in /Needs_Action (email reply request, LinkedIn post draft, vault update request), run needs-action-triage skill, verify Plan.md files appear in /Plans folder with correct classification (auto-approve vs require-approval) and step-by-step execution details.

**Acceptance Scenarios**:

1. **Given** a new email action item requesting a reply, **When** needs-action-triage processes /Needs_Action folder, **Then** a Plan.md is created classifying the action as "require-approval" with draft reply content and execution steps
2. **Given** an action item requesting a dashboard update (internal vault operation), **When** triage runs, **Then** the action is classified as "auto-approve" and Plan.md includes vault update steps
3. **Given** Company_Handbook.md specifies "always require approval for LinkedIn posts", **When** a LinkedIn posting action is triaged, **Then** the plan correctly classifies it as "require-approval" regardless of content
4. **Given** multiple action items of varying types, **When** triage processes them, **Then** each receives an appropriate classification and execution plan tailored to the action type

---

### User Story 3 - Human-in-the-Loop Approval Workflow (Priority: P1)

As a user concerned about AI mistakes, I want all external actions (sending emails, posting to LinkedIn, making payments) to require my explicit approval before execution, with clear risk assessments and execution previews presented in my Obsidian vault, so that I can review and approve/reject actions with full context and confidence.

**Why this priority**: HITL approval is the safety net - it prevents catastrophic errors from AI hallucinations or misunderstandings. Non-negotiable for Silver tier (per constitution). P1 because security and trust are foundational requirements.

**Independent Test**: Manually create an approval request file in /Pending_Approval with sample email send action, move it to /Approved folder, verify the approval-workflow-manager skill correctly routes it for execution. Then test rejection by moving a file to /Rejected and verifying no execution occurs.

**Acceptance Scenarios**:

1. **Given** a plan requires approval for sending an email, **When** approval-workflow-manager processes it, **Then** a structured approval request is created in /Pending_Approval folder with risk assessment (impact, reversibility, blast radius) and execution preview
2. **Given** an approval request in /Pending_Approval, **When** I move the file to /Approved folder, **Then** the system queues it for execution by mcp-executor and moves it from /Pending_Approval
3. **Given** an approval request in /Pending_Approval, **When** I move the file to /Rejected folder and add rejection_reason to frontmatter, **Then** the system archives it to /Rejected without execution and logs the rejection reason
4. **Given** permission boundaries in Company_Handbook specify auto-approve thresholds (e.g., emails to known contacts), **When** an action meets auto-approve criteria, **Then** it bypasses /Pending_Approval and proceeds directly to execution (optional advanced feature)

---

### User Story 4 - External Action Execution via MCP Servers (Priority: P2)

As a user who approved an action, I want the AI Employee to reliably execute it through the appropriate external integration (Gmail API for emails, LinkedIn API for posts, Playwright for WhatsApp), handle errors gracefully with retries, and report execution status back to my vault, so that approved actions complete successfully without my manual intervention.

**Why this priority**: Execution is the "hands" of the system - it turns plans into reality. P2 (not P1) because perception, triage, and approval must work first, but execution is critical for delivering end-to-end value. This is what differentiates Silver from Bronze.

**Independent Test**: Create a pre-approved email send request in /Approved folder (in dry-run mode with DRY_RUN=true), run mcp-executor skill, verify it calls the email MCP server (logged but not actually sent), moves the action to /Done, and creates an audit log entry in /Logs.

**Acceptance Scenarios**:

1. **Given** an approved email action in /Approved folder, **When** mcp-executor processes it, **Then** the email is sent via Gmail API (or logged in dry-run mode), execution result is recorded, and the action file is moved to /Done
2. **Given** an approved LinkedIn post action, **When** mcp-executor executes it, **Then** the post is published via LinkedIn API, post URL is logged, and action is archived to /Done
3. **Given** an execution fails due to transient network error, **When** retry logic kicks in, **Then** the system retries with exponential backoff (1s, 2s, 4s) up to 3 attempts before moving to /Failed folder with error details
4. **Given** dry-run mode is enabled (DRY_RUN=true in .env), **When** any action is executed, **Then** no real external API calls occur, but execution is logged as if it succeeded for testing purposes

---

### User Story 5 - Security and Comprehensive Audit Logging (Priority: P1)

As a security-conscious user (or compliance officer), I want every external action execution to be logged in structured JSON format with timestamps, actors, parameters, and results, with all credentials sanitized before logging, and logs retained for at least 90 days, so that I can audit AI behavior, investigate issues, and meet compliance requirements.

**Why this priority**: Security and auditability are non-negotiable (per constitution). Without audit logs, the system is a black box that cannot be trusted in production. P1 because it must be built-in from day one, not retrofitted later.

**Independent Test**: Execute a test action (in dry-run mode), verify /Logs/YYYY-MM-DD.json file is created with correct schema (timestamp, action_type, user, ai_agent, mcp_server, tool_name, sanitized inputs/outputs, execution_status, error), and verify credentials are redacted (e.g., API keys replaced with <REDACTED_TOKEN>).

**Acceptance Scenarios**:

1. **Given** an external action is executed, **When** audit-logger records it, **Then** a JSON entry is appended to /Logs/YYYY-MM-DD.json with all required fields (timestamp, action_id, action_type, user, ai_agent, mcp_server, tool_name, execution_status, error if applicable)
2. **Given** an action includes sensitive credentials in parameters (API key, OAuth token), **When** audit-logger sanitizes inputs, **Then** credentials are replaced with placeholders like <REDACTED_TOKEN> or <REDACTED_PII> before logging
3. **Given** logs accumulate over 90 days, **When** I review the /Logs folder, **Then** all daily log files from the past 90 days are present and queryable for compliance audits
4. **Given** an execution fails with an error, **When** the audit log is written, **Then** the error field contains the sanitized error message and stack trace (if available) for debugging

---

### User Story 6 - Graceful Degradation and Health Monitoring (Priority: P2)

As a user running the AI Employee 24/7, I want the system to automatically recover from component failures (watcher crashes, MCP server downtime, network outages) by isolating failures, retrying transient errors, restarting crashed processes, and continuing to operate with degraded functionality rather than complete failure, so that I don't need to manually intervene every time something goes wrong.

**Why this priority**: Production systems must be resilient - they will fail, and graceful degradation ensures core functionality survives. P2 because basic monitoring/restart is essential, but advanced health monitoring can evolve over time.

**Independent Test**: Manually kill a watcher process (e.g., Gmail watcher), verify watchdog or PM2 automatically restarts it within 60 seconds, and verify other watchers continue operating unaffected. Test retry logic by simulating a transient network timeout in a mock MCP server.

**Acceptance Scenarios**:

1. **Given** Gmail watcher crashes due to an unhandled exception, **When** the watchdog process (or PM2) detects the failure, **Then** the watcher is automatically restarted within 60 seconds and resumes monitoring
2. **Given** an MCP server is temporarily unavailable (network timeout), **When** mcp-executor attempts to call it, **Then** the system retries with exponential backoff (1s, 2s, 4s) for up to 3 attempts before marking the action as failed
3. **Given** one watcher (e.g., LinkedIn) fails permanently, **When** other watchers (Gmail, WhatsApp) continue running, **Then** the system continues creating action items from functional sources without cascading failure
4. **Given** a component logs heartbeat every 60 seconds, **When** I review logs, **Then** I can identify when components were running/crashed by examining heartbeat timestamps for monitoring purposes

---

### User Story 7 - Vault Integration and Dashboard Updates (Priority: P2)

As a user managing all information in Obsidian, I want the AI Employee to maintain the vault structure (Bronze + Silver folders), update Dashboard.md with recent activity summaries and pending approval counts, preserve YAML frontmatter when moving files, and never delete my content (only archive to /Done or /Rejected), so that my vault remains the single source of truth with full history.

**Why this priority**: Vault safety is critical (per constitution Principle II), but it's P2 because basic vault operations work from Bronze tier - Silver tier adds new folders and dashboard enhancements rather than core functionality.

**Independent Test**: Create a test action item with custom YAML frontmatter, move it through the workflow (Needs_Action → Pending_Approval → Approved → Done), verify frontmatter is preserved at each step and Dashboard.md shows updated statistics (pending approvals count, recent activity).

**Acceptance Scenarios**:

1. **Given** Silver tier initializes, **When** obsidian-vault-ops ensures folder structure, **Then** all required folders exist (/Inbox, /Needs_Action, /Plans, /Done, /Pending_Approval, /Approved, /Rejected, /Failed, /Logs)
2. **Given** an action item with custom YAML frontmatter is moved from /Needs_Action to /Pending_Approval, **When** the move occurs, **Then** all YAML fields are preserved exactly as originally written
3. **Given** multiple actions are in /Pending_Approval, **When** Dashboard.md is updated, **Then** it shows the count of pending approvals, recent activity (last 5 actions), and execution statistics (success/failure counts)
4. **Given** a user-authored note in the vault, **When** any AI operation runs, **Then** the note is never deleted (only archival moves to /Done or /Rejected are allowed, per non-destructive principle)

---

### User Story 8 - Multi-Watcher Orchestration and 24/7 Operation (Priority: P2)

As a user who wants hands-off automation, I want to start all watchers simultaneously with a single command (multi-watcher-runner skill), have them run continuously 24/7 via PM2 or a custom watchdog, and automatically restart after system reboots, so that the AI Employee is always monitoring without requiring manual intervention.

**Why this priority**: Orchestration enables true 24/7 operation, but it's P2 because individual watchers can run manually in development - production-grade orchestration is a convenience/reliability enhancement rather than a core feature blocker.

**Independent Test**: Run multi-watcher-runner skill, verify all configured watchers (Gmail, WhatsApp, LinkedIn, filesystem) start successfully and log heartbeat messages every 60 seconds. Stop the orchestrator, restart it, verify watchers resume from last state without duplicate processing.

**Acceptance Scenarios**:

1. **Given** multi-watcher-runner is invoked, **When** it starts, **Then** all configured watchers (at least 2: Gmail + one other) launch as independent processes and begin monitoring their respective sources
2. **Given** watchers are managed by PM2, **When** the system reboots, **Then** PM2 automatically restarts all watchers without manual intervention (pm2 startup configuration)
3. **Given** a scheduled task (cron/Task Scheduler) triggers daily at 8 AM, **When** the trigger fires, **Then** the orchestrator runs needs-action-triage to process overnight action items and generates a morning briefing (optional future enhancement)
4. **Given** watchers log heartbeat every 60 seconds, **When** I review logs after 24 hours of operation, **Then** I see continuous heartbeat entries indicating 24/7 uptime (or gaps indicating downtime for investigation)

---

### Edge Cases

- **What happens when the Obsidian vault is locked or inaccessible (file system permissions, disk full, vault path misconfigured)?**
  System should detect vault unavailability on startup, log a CRITICAL ERROR, pause all operations (watchers write to temporary queue, orchestrator pauses execution), and alert the user. Upon vault restoration, queued items are processed. This is the only acceptable complete system halt (vault is single source of truth per constitution).

- **How does the system handle duplicate messages across multiple channels (same content arrives via email AND WhatsApp)?**
  Each watcher creates an action item with a unique source_id (hash of content + source). Triage detects duplicates by comparing content similarity (e.g., >90% text match) and merges them into a single Plan.md with references to both source action items.

- **What if a user manually edits an action item file while it's being processed by the system?**
  Obsidian uses filesystem watchers, so the system detects file changes. If an action item in /Needs_Action is modified after triage starts, the current triage ignores it and picks it up in the next cycle. If an approval request in /Pending_Approval is edited, the system treats it as a new approval request requiring re-review.

- **How does the system handle API rate limits (Gmail API, LinkedIn API) when executing multiple actions?**
  MCP executor implements rate limiting per API (configurable in .env, e.g., MAX_EMAILS_PER_HOUR=50). When limit is reached, actions are queued in /Approved and execution resumes when the rate limit window resets. Audit log records "rate_limited" status.

- **What if credentials expire (OAuth token refresh fails, API key revoked)?**
  MCP server detects authentication failure on startup or during execution, logs ERROR with actionable message ("OAuth token expired - run `uv run python refresh_token.py`"), pauses operations for that integration, and moves affected actions to /Failed with error: "authentication_failure". User must manually refresh credentials and restart the affected MCP server.

- **How does the system behave when a human takes too long to approve/reject (approval request sits in /Pending_Approval for days)?**
  Optional deadline field in approval request YAML (deadline: 2026-01-20T18:00:00Z). If deadline passes without decision, approval-workflow-manager moves the request to /Rejected with rejection_reason: "expired_deadline" to prevent stale actions from executing unexpectedly.

## Requirements *(mandatory)*

### Functional Requirements

**Multi-Channel Perception (Watchers)**

- **FR-001**: System MUST provide a Gmail watcher that monitors Gmail inbox for important/unread emails using Gmail API with OAuth 2.0 authentication
- **FR-002**: System MUST provide a WhatsApp watcher that monitors WhatsApp Web for messages containing urgent keywords (invoice, payment, help, urgent, ASAP) using Playwright browser automation
- **FR-003**: System MUST provide a LinkedIn watcher that monitors LinkedIn for business-relevant notifications (new connections, messages, post engagement)
- **FR-004**: Each watcher MUST run as an independent process that does not crash other watchers when it fails
- **FR-005**: Each watcher MUST create structured markdown action items in /Needs_Action folder with standardized YAML frontmatter (type, received timestamp, status: pending, source_id for duplicate detection)
- **FR-006**: Watchers MUST implement duplicate detection using source_id (content hash + source identifier) to prevent processing the same message multiple times

**Intelligent Triage and Planning**

- **FR-007**: System MUST provide needs-action-triage skill that processes all items in /Needs_Action folder
- **FR-008**: Triage MUST analyze each action item to determine appropriate actions (reply, forward, schedule, escalate, update vault)
- **FR-009**: Triage MUST generate Plan.md files in /Plans folder with step-by-step execution details for each action item
- **FR-010**: Triage MUST classify actions as "auto-approve" (internal vault operations like dashboard updates) or "require-approval" (external actions like sending emails)
- **FR-011**: Triage MUST extract business context from Company_Handbook.md to apply user-defined rules (e.g., "always require approval for LinkedIn posts", "auto-approve dashboard updates")
- **FR-012**: Triage MUST preserve the original action item in /Needs_Action after creating a plan (do not delete until execution completes)

**Human-in-the-Loop Approval Workflow**

- **FR-013**: System MUST provide approval-workflow-manager skill that routes external actions to /Pending_Approval folder
- **FR-014**: Approval requests MUST include risk assessment with impact (financial, reputational, operational), reversibility (can this be undone?), and blast radius (who/what is affected?)
- **FR-015**: Approval requests MUST include execution preview with MCP server name, tool name, and sanitized parameter values
- **FR-016**: System MUST wait for human decision: user moves file to /Approved (execute) or /Rejected (cancel)
- **FR-017**: System MUST support optional permission boundaries defined in Company_Handbook.md for auto-approve thresholds (e.g., emails to pre-approved contact list, posts under 280 characters)
- **FR-018**: Rejected actions MUST be archived to /Rejected folder with rejection_reason documented in YAML frontmatter, and MUST NOT be executed

**External Action Execution via MCP Servers**

- **FR-019**: System MUST provide mcp-executor skill that watches /Approved folder for approved actions
- **FR-020**: System MUST support email sending via FastMCP email server with Gmail API integration
- **FR-021**: System MUST support LinkedIn posting via FastMCP LinkedIn server for business content generation
- **FR-022**: System MUST support browser automation via Playwright for WhatsApp message sending and web-based form interactions
- **FR-023**: System MUST implement dry-run mode controlled by DRY_RUN environment variable (when true, log actions without executing real API calls)
- **FR-024**: Successfully executed actions MUST be moved to /Done folder; failed executions MUST be moved to /Failed folder with error details in YAML frontmatter

**Security and Audit Logging**

- **FR-025**: System MUST provide audit-logger skill that logs all external action executions
- **FR-026**: Audit logs MUST be stored in /Logs/YYYY-MM-DD.json format with daily rotation
- **FR-027**: Each audit log entry MUST include: timestamp (ISO 8601), action_id, action_type, user (approver), ai_agent (model version), mcp_server, tool_name, sanitized tool inputs/outputs, execution_status (success/failure/pending), error (if applicable), retry_count
- **FR-028**: Audit logger MUST sanitize credentials before logging (redact API keys → <REDACTED_TOKEN>, OAuth tokens → <REDACTED_TOKEN>, passwords → <REDACTED_PASSWORD>, credit card numbers → <REDACTED_PII>)
- **FR-029**: System MUST enforce credential management: all secrets MUST be stored in .env file only, NEVER in vault or repository (violation triggers startup failure)
- **FR-030**: Audit logs MUST be retained for minimum 90 days to support compliance and security review

**Graceful Degradation and Error Recovery**

- **FR-031**: System MUST isolate watcher processes so failure of one watcher does not crash other watchers or the orchestrator
- **FR-032**: System MUST implement retry logic for transient failures (network timeout, API rate limiting) with exponential backoff (1s, 2s, 4s) and maximum 3 retries
- **FR-033**: Failed executions after max retries MUST be moved to /Failed folder as dead letter queue for manual intervention
- **FR-034**: Each component MUST log heartbeat messages every 60 seconds to enable health monitoring
- **FR-035**: System MUST use watchdog process (or PM2) to automatically restart crashed components within 60 seconds
- **FR-036**: When MCP servers are unavailable, orchestrator MUST pause execution of affected actions and resume when services are restored (watchers continue creating action items)

**Obsidian Vault Integration**

- **FR-037**: System MUST provide obsidian-vault-ops skill for safe vault operations
- **FR-038**: System MUST maintain Bronze tier folders (/Inbox, /Needs_Action, /Plans, /Done) plus Silver tier folders (/Pending_Approval, /Approved, /Rejected, /Failed, /Logs)
- **FR-039**: System MUST update Dashboard.md with recent activity (last 5 actions), pending approvals count, and execution statistics (success/failure counts)
- **FR-040**: System MUST preserve YAML frontmatter exactly when moving files between folders (no data loss or corruption)
- **FR-041**: System MUST follow non-destructive operations principle: never delete user content, only archive to /Done or /Rejected folders

**Process Orchestration and Scheduling**

- **FR-042**: System MUST provide multi-watcher-runner skill that starts and monitors all watchers simultaneously
- **FR-043**: System MUST support 24/7 continuous operation via PM2 process manager (Node.js) or custom watchdog.py (Python)
- **FR-044**: System MUST enable scheduled tasks via cron (Unix/Mac) or Task Scheduler (Windows) for periodic operations (e.g., daily morning briefing at 8 AM)
- **FR-045**: System MUST support automatic recovery from system reboots without manual intervention (PM2 startup configuration or systemd service)

### Key Entities

- **Action Item**: Represents an incoming request or notification requiring attention. Stored as markdown file in /Needs_Action with YAML frontmatter (type: email|whatsapp|linkedin|file_drop, received: timestamp, status: pending|processed, priority: high|medium|low|auto, source_id: unique hash for duplicate detection). Body contains summary, details, and suggested actions.

- **Execution Plan**: Represents the AI's proposed execution strategy for an action item. Stored as markdown file in /Plans with YAML frontmatter (created: timestamp, status: pending_approval|approved|rejected|completed, classification: auto-approve|require-approval). Body contains objective, step-by-step execution details, required MCP servers/tools, and approval requirements.

- **Approval Request**: Represents a request for human approval of a sensitive external action. Stored in /Pending_Approval with YAML frontmatter (type: approval_request, action_type: send_email|post_linkedin|browser_automation|api_call, created: timestamp, deadline: optional timestamp, priority, original_item: link to source action item, mcp_server, tool_name). Body contains proposed action, justification, risk assessment (impact, reversibility, blast radius), execution details with parameter preview.

- **Audit Log Entry**: Represents a record of an executed external action. Stored as JSON object in /Logs/YYYY-MM-DD.json with fields: timestamp, action_id, action_type, user (human approver), ai_agent (Claude model version), approval_reason, execution_status, mcp_server, tool_name, tool_inputs_sanitized (with credentials redacted), tool_output_sanitized, error (if failed), retry_count.

- **Watcher Process**: Represents a long-running background process monitoring a specific communication channel. Each watcher has: name (gmail|whatsapp|linkedin|filesystem), status (running|stopped|crashed), last_heartbeat (timestamp), processed_ids (set of source_ids to prevent duplicate processing), configuration (credentials path, polling interval, keywords for filtering).

- **MCP Server**: Represents an external integration server implementing Model Context Protocol. Each server has: name (email-server|linkedin-server|browser-automation-server), tools (list of available functions like send_email, post_to_linkedin), status (available|unavailable|rate_limited), credentials (loaded from .env), dry_run_mode (boolean flag).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 2 watchers (Gmail + one of WhatsApp/LinkedIn/filesystem) operate simultaneously for 24 hours without manual intervention or crashes
- **SC-002**: End-to-end flow completes within 5 minutes: watcher detects input → needs-action-triage creates plan → approval-workflow-manager requests approval → human approves → mcp-executor executes → audit-logger logs result → obsidian-vault-ops archives to /Done
- **SC-003**: Zero credentials are stored in vault or repository (100% of secrets in .env file only, verified by automated security scan)
- **SC-004**: 100% of external actions are logged in /Logs with sanitized credentials (verified by audit log review - no plaintext API keys, tokens, or passwords)
- **SC-005**: System continues operating when one watcher fails (verified by killing one watcher process and confirming other watchers continue creating action items within 2 minutes)
- **SC-006**: Dry-run mode prevents real external actions while testing approval workflow (verified by executing 10 test actions in dry-run mode and confirming zero actual API calls via network monitoring)
- **SC-007**: All Bronze tier functionality remains operational (verified by running Bronze tier acceptance tests - filesystem watcher, vault operations, basic triage all pass)
- **SC-008**: Human approves an action in under 30 seconds from request creation to execution completion (measures workflow efficiency)
- **SC-009**: 95% of transient errors (network timeouts, rate limits) recover automatically via retry logic without human intervention (measures resilience)
- **SC-010**: Dashboard.md updates within 10 seconds of any action state change (Needs_Action → Pending_Approval → Approved → Done) to provide real-time visibility

## Assumptions

- Bronze tier is fully functional and tested (filesystem watcher creates action items, vault operations preserve frontmatter, needs-action-triage generates plans, all tests passing)
- Obsidian vault exists at configured VAULT_PATH in .env with required Bronze tier files (Dashboard.md, Company_Handbook.md)
- User has obtained necessary API credentials before starting Silver tier setup:
  - Gmail API: OAuth 2.0 client credentials (client_id, client_secret, refresh_token) from Google Cloud Console
  - WhatsApp Web: Playwright browser session persistence configured (session stored in secure location)
  - LinkedIn API: Access token or session cookies for LinkedIn posting (or manual approval for browser automation approach)
- System environment includes required dependencies:
  - Python 3.13 or higher installed and accessible
  - UV package manager for Python dependency management (uv installed globally)
  - Playwright browser automation library installed (npx playwright install for Chromium)
  - FastMCP library with Pydantic v2 validation for building MCP servers
  - PM2 process manager (npm install -g pm2) or custom watchdog.py for process orchestration
- User reviews /Pending_Approval folder regularly (at least daily, ideally multiple times per day) to approve/reject actions - system cannot execute external actions without human approval
- User understands basic Obsidian markdown and YAML frontmatter syntax to manually review/edit approval requests if needed
- Network connectivity is stable for API calls (Gmail, LinkedIn) - system handles transient failures with retries but requires eventual network access
- User's operating system supports long-running background processes (Windows Task Scheduler, macOS/Linux cron, or PM2 daemon mode)

## Out of Scope (Deferred to Gold Tier or Future Phases)

- Cross-platform integrations beyond Gmail/WhatsApp/LinkedIn: Facebook, Instagram, Twitter/X, Slack, Discord, Telegram (requires additional MCP servers and authentication flows)
- Accounting system integration: Xero MCP server for business expense tracking, invoice generation, financial reporting (Gold tier feature per hackathon spec)
- Weekly business audit and CEO briefing generation: Automated analysis of completed tasks, revenue tracking, bottleneck identification, proactive suggestions (Gold tier "Monday Morning CEO Briefing")
- Multi-agent orchestration: Multiple specialized AI agents (finance agent, communications agent, project management agent) working in parallel with task delegation (Gold tier advanced automation)
- Proactive task suggestions without user input: AI initiating actions based on patterns (e.g., "I noticed you haven't posted on LinkedIn in 2 weeks, should I draft a post?") - requires advanced context awareness beyond Silver tier scope
- Natural language query interface for audit logs: User asks "Show me all failed email sends last week" and AI queries /Logs to generate report (future enhancement, Silver tier provides raw JSON logs only)
- Automatic credential refresh: OAuth token auto-renewal without manual intervention when tokens expire (Silver tier requires manual refresh, Gold tier could automate)
- Machine learning for triage optimization: Learning from user approval/rejection patterns to improve classification accuracy over time (future AI enhancement)
- Mobile app or web dashboard: Silver tier uses Obsidian vault as sole interface, no separate UI beyond markdown files (potential future feature)

## Skills Integration Requirements

This feature MUST utilize the following existing Claude Code skills throughout implementation. These skills are non-negotiable and central to Silver tier architecture:

- **approval-workflow-manager**: Routes external actions requiring human oversight to /Pending_Approval folder, creates structured approval request markdown files with risk assessment and execution preview, handles approval/rejection decisions by monitoring folder moves to /Approved or /Rejected, enforces permission boundaries defined in Company_Handbook.md for auto-approve vs require-approval classification.

- **audit-logger**: Logs all external action executions to /Logs/YYYY-MM-DD.json in structured JSON format, sanitizes credentials and PII before writing to logs (redacts API keys, OAuth tokens, passwords, credit card numbers), ensures 90-day minimum retention policy, implements daily log rotation, validates log schema compliance (timestamp, action_id, action_type, user, ai_agent, mcp_server, tool_name, execution_status, error).

- **mcp-executor**: Watches /Approved folder for approved actions awaiting execution, routes actions to appropriate MCP servers (email-server for Gmail, linkedin-server for posts, browser-automation-server for WhatsApp/web interactions), handles execution results (success → /Done, failure → /Failed with error details), implements dry-run mode when DRY_RUN=true environment variable is set (logs execution without real API calls), enforces retry logic with exponential backoff for transient failures.

- **multi-watcher-runner**: Orchestrates simultaneous startup of all configured watchers (Gmail, WhatsApp, LinkedIn, filesystem), monitors watcher health via heartbeat logging (expected every 60 seconds), restarts crashed watchers automatically via watchdog pattern or PM2 integration, manages process lifecycle (start, stop, restart, status reporting), enables 24/7 continuous operation with system reboot recovery.

- **needs-action-triage**: Processes all items in /Needs_Action folder to analyze content and determine appropriate actions, generates Plan.md files in /Plans folder with step-by-step execution details, classifies actions as "auto-approve" (internal vault operations) or "require-approval" (external actions), extracts business rules from Company_Handbook.md to apply user-defined policies, detects duplicate action items via content similarity analysis, preserves original action items for audit trail.

- **obsidian-vault-ops**: Safely operates on Obsidian vault with non-destructive principles (never delete user content), creates and maintains folder structure (/Inbox, /Needs_Action, /Plans, /Done, /Pending_Approval, /Approved, /Rejected, /Failed, /Logs), moves files between folders while preserving YAML frontmatter exactly, updates Dashboard.md with recent activity summaries and statistics (pending approvals count, success/failure rates), validates vault integrity (checks for corrupted files, missing frontmatter), implements atomic file operations to prevent partial writes.

## Constraints

- Human approval required for ALL external actions by default (non-negotiable security requirement per constitution Principle VIII) - system MUST NOT send emails, post to LinkedIn, or perform browser automation without explicit human approval unless user explicitly configures auto-approve thresholds in Company_Handbook.md
- No credentials in vault or repository (security violation triggers immediate startup failure) - API keys, OAuth tokens, passwords, session cookies MUST be stored exclusively in .env file and .env MUST be in .gitignore
- Bronze tier tests must continue passing (backward compatibility required per constitution versioning policy) - all filesystem watcher tests, vault operations tests, and basic triage tests from Bronze tier remain valid and executable
- Audit logs mandatory for compliance (cannot be disabled even in development) - every external action execution MUST be logged to /Logs with credential sanitization, no configuration option to bypass logging
- Component failures must not cascade (each watcher/MCP server isolated per constitution Principle X) - Gmail watcher crash MUST NOT affect WhatsApp or LinkedIn watchers, MCP server unavailability MUST NOT prevent approval workflow from functioning
