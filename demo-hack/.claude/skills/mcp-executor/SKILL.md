---
name: mcp-executor
description: >
  Execute approved actions via custom FastMCP servers (email, LinkedIn, browser automation).
  Processes items from /Approved/ folder in Obsidian vault, routes to appropriate MCP server,
  executes action with error handling, and logs results to /Done/. Supports email sending,
  LinkedIn posting, form filling, file operations, and external API calls. Use when: (1) Executing
  approved email/message actions, (2) Posting to LinkedIn or social media, (3) Performing browser
  automation (payments, forms, clicks), (4) Calling external APIs, (5) Any action requiring
  real-world execution. Trigger phrases: "execute approved action", "send email", "post to LinkedIn",
  "fill out form", "make API call", "run action".
---

# MCP Executor (Action Execution Engine)

Execute approved actions through custom FastMCP servers. Process items from `/Approved/` folder and execute via appropriate MCP server (email, LinkedIn, browser automation, etc.).

## Architecture Note: Orchestrator.py Component

**IMPORTANT**: The `run_executor.py` script implements the **Orchestrator.py (Master Process)** component described in HACKATHON-ZERO.md (Line 1242, Line 495, Line 666-667).

**What it does**:
- Watches the `/Approved/` folder for approved actions
- Routes actions to appropriate MCP servers
- Handles execution timing and folder watching
- Manages retry logic and error handling
- Moves completed items to `/Done/` or `/Failed/`

**Relationship with orchestrate_watchers.py**:
- `run_executor.py` = **Orchestrator.py** (Master Process for approval execution)
- `orchestrate_watchers.py` (from multi-watcher-runner skill) = **Watchdog.py** (Health Monitor for watcher processes)
- These are TWO DIFFERENT components that work together (per HACKATHON-ZERO.md Line 1239-1250)

**For Hackathon Submission**:
- Copy `run_executor.py` to `My_AI_Employee/orchestrator.py` for alignment with hackathon naming conventions
- Keep original in `.claude/skills/mcp-executor/scripts/` as reference
- Both files serve the same purpose: approval workflow execution

## Quick Start

### Starting the Executor

```bash
# Start MCP executor daemon
python scripts/run_executor.py

# Check execution status
python scripts/executor_status.py

# View execution logs
tail -f logs/executor.log
```

The executor:
1. Watches `/Approved/` folder for new items
2. Routes each item to appropriate MCP server
3. Executes the action
4. Captures results and errors
5. Creates execution record in `/Done/` with results
6. **Moves original file from `/Needs_Action/` to `/Done/`** (Silver tier only)

### Execution Workflow

```
Item in /Approved/
       ↓
Executor reads item
       ↓
Determine action type (email, linkedin_post, etc)
       ↓
Load MCP server for that type
       ↓
Call MCP server tool/resource
       ↓
Action executes successfully? YES → Create execution record in /Done/
                             |      Move original file from /Needs_Action/ to /Done/
                             |      Update original file with execution metadata
                              NO  → Move to /Failed/ with error
```

### Original File Movement (Silver Tier)

**IMPORTANT**: After successful execution, the executor MUST move the original action item from `/Needs_Action/` to `/Done/`.

**Why**: In Silver tier, the `/needs-action-triage` skill keeps files in `/Needs_Action/` with `status: pending_approval` until execution completes. The executor is responsible for moving them to `/Done/` after the external action succeeds.

**How**:
1. Read the `original_file` field from the approval's frontmatter
2. Locate the original file in `/Needs_Action/`
3. Update its frontmatter with execution metadata:
   - `status: executed`
   - `executed_at: [timestamp]`
   - `execution_result: success`
   - `message_id: [if applicable]`
4. Move the updated file to `/Done/`

**Example**:
- Approval file: `/Approved/APPROVAL_20260118_email_Sunaina_Gold_Tier.md`
- Original file: `/Needs_Action/20260118_152957_183659_email_Sunaina_Ismail.md`
- After execution: Move original to `/Done/20260118_152957_183659_email_Sunaina_Ismail.md`

**Bronze Tier Note**: Bronze tier files are already in `/Done/` (moved by `/needs-action-triage` after planning), so this step only applies to Silver tier files that require external actions.

## Built-In MCP Servers

### 1. Email MCP Server

**Capabilities**: Send emails, draft emails, search mailbox

```bash
# Start email server
python mcp_servers/email_mcp.py
```

**Actions**:
- `send_email` - Send email via Gmail
- `draft_email` - Create draft without sending
- `search_mail` - Search existing emails

### 2. LinkedIn MCP Server

**Capabilities**: Post content, share updates, create posts

```bash
# Start LinkedIn server
python mcp_servers/linkedin_mcp.py
```

**Actions**:
- `create_post` - Post to LinkedIn timeline
- `share_link` - Share URL with comment
- `schedule_post` - Schedule post for later

### 3. Browser Automation MCP Server

**Capabilities**: Navigate browser, fill forms, click buttons, extract data

```bash
# Start browser server
python mcp_servers/browser_mcp.py
```

**Actions**:
- `navigate_to` - Open URL
- `fill_form` - Enter text in form fields
- `click_button` - Click element
- `extract_text` - Get page content
- `take_screenshot` - Capture page

## Approved Action Format

Actions in `/Approved/` folder should have this structure:

### Frontmatter (YAML)

```yaml
---
type: action
source: approval_workflow
action_type: send_email|create_post|payment|form_fill
mcp_server: email|linkedin|browser|generic
status: approved
approved_by: Jane Doe
approved_at: 2026-01-14T14:30:00Z
---
```

### Body Structure

```markdown
# Action: [Description]

## Action Details

**Type**: send_email
**Server**: email_mcp
**Action**: send_email

## Parameters

**To**: client@example.com
**Subject**: Project Update
**Body**: Email content here

---
```

## Execution Examples

### Email Execution

**Approved item** in `/Approved/email_send_client.md`:
```markdown
---
type: action
action_type: send_email
mcp_server: email
approved_by: Jane Doe
---

# Send Email: Project Update

**To**: client@example.com
**Subject**: Project Update - Completion Confirmed
**Body**: [full email text]
```

**Executor processes**:
1. Reads item from `/Approved/`
2. Routes to email_mcp server
3. Calls `send_email(to, subject, body)`
4. Result: Email sent
5. Moves to `/Done/executed_email_send.md` with confirmation

### LinkedIn Post Execution

**Approved item** in `/Approved/linkedin_post.md`:
```markdown
---
type: action
action_type: create_post
mcp_server: linkedin
approved_by: Jane Doe
---

# LinkedIn Post: Automation Insights

**Post Text**: [full post content]
**Hashtags**: #automation #business #innovation
```

**Executor processes**:
1. Reads item from `/Approved/`
2. Routes to linkedin_mcp server
3. Calls `create_post(text, hashtags)`
4. Result: Post published with URL
5. Moves to `/Done/` with post URL

### Browser Automation Execution

**Approved item** in `/Approved/payment_form.md`:
```markdown
---
type: action
action_type: payment
mcp_server: browser
approved_by: Jane Doe
---

# Payment Form Submission

**URL**: https://vendor.example.com/pay
**Amount**: $800
**Vendor**: Tech Solutions Inc

**Steps**:
1. Navigate to https://vendor.example.com/pay
2. Fill "amount" field: 800
3. Fill "vendor" field: Tech Solutions Inc
4. Click "Submit Payment" button
5. Extract confirmation number
```

**Executor processes**:
1. Reads item from `/Approved/`
2. Routes to playwright_mcp server
3. Executes steps in sequence
4. Captures screenshot and confirmation
5. Moves to `/Done/` with result

## Error Handling

### Execution Fails

If action execution fails:

**Result in `/Failed/`**:
```markdown
---
type: action
status: failed
error: Email send failed - authentication error
retry_count: 1
next_retry: 2026-01-14T15:00:00Z
---

# FAILED: Send Email to Client

## Original Request
[original action details]

## Error Details
```
Authentication failed: Invalid OAuth token
Gmail API returned 401 Unauthorized
```

## Debugging Info
- Timestamp: 2026-01-14 14:35:00
- Server: email_mcp
- Attempt: 1/3
- Next retry: 2026-01-14 15:00:00 (25 minutes)

---
```

### Auto-Retry Logic

Failed actions automatically retry:
1. First attempt: Immediate
2. Retry 1: After 25 minutes
3. Retry 2: After 2 hours
4. Retry 3: After 8 hours
5. After 3 retries: Marked as dead, requires manual intervention

## Execution Logs

View what executor is doing:

```bash
# Real-time execution log
tail -f logs/executor.log

# Execution history
grep "EXECUTED" logs/executor.log

# Errors/failures
grep "FAILED\|ERROR" logs/executor.log

# Specific action
grep "email_send_client" logs/executor.log
```

## Configuration

### In Company_Handbook.md

```markdown
## Executor Configuration

### Execution Rules
- Execute all approved actions immediately
- If execution fails, retry up to 3 times
- Wait 30 seconds between retries
- Log all executions to audit trail

### Timeout Handling
- Email send: 30 seconds timeout
- LinkedIn post: 60 seconds timeout
- Browser automation: 120 seconds timeout
- Payment forms: 90 seconds timeout

### Error Notifications
- Critical errors: Notify immediately
- Retry failures: Log and hold for manual review
- Partial success: Proceed with caution
```

### In .env

```bash
# MCP Executor
EXECUTOR_CHECK_INTERVAL=5          # Check for new approved items every 5 seconds
EXECUTOR_MAX_RETRIES=3             # Max retry attempts
EXECUTOR_RETRY_BACKOFF=25          # Initial retry delay in seconds
EXECUTOR_TIMEOUT_DEFAULT=60        # Default execution timeout

# Email MCP
EMAIL_MCP_HOST=localhost
EMAIL_MCP_PORT=3001

# LinkedIn MCP
LINKEDIN_MCP_HOST=localhost
LINKEDIN_MCP_PORT=3002

# Browser MCP
BROWSER_MCP_HOST=localhost
BROWSER_MCP_PORT=3003
```

## MCP Servers Reference

See `references/fastmcp-servers.md` for:
- Email MCP server implementation
- LinkedIn MCP server implementation
- Browser automation MCP server implementation
- Custom MCP server creation
- MCP server deployment

See `references/execution-patterns.md` for:
- Common execution workflows
- Error handling patterns
- Retry strategies
- Timeout handling
- Logging patterns

## Monitoring Execution

```bash
# Check executor health
python scripts/executor_status.py

# Output shows:
# - Items pending execution
# - Success rate today
# - Average execution time
# - Failed items needing retry
# - MCP servers health status
```

## Integration

### With Approval Workflow

1. Approval workflow creates item in `/Pending_Approval/`
2. Human approves → moves to `/Approved/`
3. Executor sees item in `/Approved/`
4. Executes action via MCP server
5. Result → `/Done/`

### With Audit Logger

- All execution attempts logged
- Success/failure recorded
- Error details captured
- Credentials NOT logged (sanitized)
- Full audit trail maintained

### With Multi-Watcher

- Watchers create action items
- Goes through approval workflow
- Executor processes approved items
- Results available for next watcher cycle
