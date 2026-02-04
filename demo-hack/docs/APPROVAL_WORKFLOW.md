# Approval Workflow Documentation

**Silver Tier AI Employee - Human-in-the-Loop (HITL) System**

This document describes the complete approval workflow for the Silver Tier AI Employee, including folder structure, file formats, approval process, and integration with Claude Code skills.

---

## Overview

The approval workflow is the core of the Silver Tier AI Employee's Human-in-the-Loop (HITL) architecture. **All external actions require explicit human approval** before execution.

**Key Principles**:
- ✅ **No automatic execution**: Zero external actions without approval
- 📁 **File-based workflow**: Move files between folders to approve/reject
- 🔍 **Complete transparency**: All actions visible in vault
- 📊 **Audit trail**: Every decision logged with timestamp and approver
- ⏱️ **Fast approval**: Approve in under 30 seconds by moving a file

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│  1. PERCEPTION: Watcher detects event                       │
│     → Creates action item in Needs_Action/                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. REASONING: Claude Code processes action item            │
│     → Creates Plan.md in Plans/                             │
│     → Creates approval request in Pending_Approval/         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. HUMAN DECISION: You review and decide                   │
│     → Move to Approved/ (approve)                           │
│     → Move to Rejected/ (reject)                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. EXECUTION: Orchestrator executes approved action        │
│     → Routes to MCP server                                  │
│     → Moves to Done/ (success) or Failed/ (error)           │
└─────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

### Vault Folders

```
AI_Employee_Vault/
├── Needs_Action/         # Unprocessed action items (from watchers)
├── Plans/                # Planning artifacts (reasoning)
├── Pending_Approval/     # Awaiting human decision
├── Approved/             # Approved for execution (watched by orchestrator)
├── Rejected/             # Rejected by human (not executed)
├── Done/                 # Successfully executed actions
├── Failed/               # Failed executions (after 3 retries)
└── Logs/                 # Audit logs (YYYY-MM-DD.json)
```

### Folder Purposes

**Needs_Action/**:
- Created by: Watchers (gmail_watcher.py, whatsapp_watcher.py, linkedin_watcher.py)
- Contains: Raw action items from detected events
- Processed by: Claude Code skill `needs-action-triage`
- Lifecycle: Stays until processed, then archived to Done/

**Plans/**:
- Created by: Claude Code skill `needs-action-triage`
- Contains: Reasoning, recommendations, context
- Purpose: Explain WHY an action should be taken
- Lifecycle: Permanent (not moved)

**Pending_Approval/**:
- Created by: Claude Code skill `needs-action-triage`
- Contains: Approval requests with complete action details
- Purpose: Human review and decision
- Lifecycle: Moved to Approved/ or Rejected/ by human

**Approved/**:
- Created by: Human (moving file from Pending_Approval/)
- Contains: Actions approved for execution
- Watched by: Orchestrator (orchestrator.py)
- Lifecycle: Moved to Done/ or Failed/ after execution

**Rejected/**:
- Created by: Human (moving file from Pending_Approval/)
- Contains: Actions rejected by human
- Purpose: Audit trail of rejections
- Lifecycle: Permanent (not moved)

**Done/**:
- Created by: Orchestrator after successful execution
- Contains: Execution records with results
- Purpose: Audit trail of completed actions
- Lifecycle: Permanent (not moved)

**Failed/**:
- Created by: Orchestrator after 3 failed retries
- Contains: Failed actions with error details
- Purpose: Manual review and intervention
- Lifecycle: Permanent (not moved)

**Logs/**:
- Created by: AuditLogger utility
- Contains: JSONL audit logs (one file per day)
- Purpose: Complete audit trail with sanitized credentials
- Lifecycle: 90-day minimum retention

---

## File Formats

### Action Item (Needs_Action/)

**Filename**: `YYYYMMDD_HHMMSS_MICROSECONDS_source_identifier.md`

**Example**: `20260121_103000_123456_email_client_name.md`

**Format**:
```markdown
---
type: action_item
action_type: email | whatsapp | linkedin_post
source: gmail | whatsapp | linkedin
priority: Low | Medium | High
created_at: 2026-01-21T10:30:00Z
status: pending
---

# [Title describing the action item]

[Content from the detected event]

**Source Details**:
- From: [sender/contact]
- Subject/Topic: [subject line or topic]
- Timestamp: [when event occurred]

**Context**:
[Any additional context needed for reasoning]
```

### Plan (Plans/)

**Filename**: `Plan_YYYYMMDD_HHMMSS_identifier.md`

**Example**: `Plan_20260121_103000_email_client.md`

**Format**:
```markdown
---
type: plan
action_item_id: 20260121_103000_123456_email_client_name
created_at: 2026-01-21T10:31:00Z
status: completed
---

# Plan: [Action Item Title]

## Context

[Summary of the action item and why it needs attention]

## Analysis

[Analysis based on Company_Handbook.md rules]

## Recommendation

**Action**: [What should be done]
**Priority**: [Low/Medium/High]
**Reasoning**: [Why this action is recommended]

## Draft Action

[Complete draft of the action to be taken]

## Approval Threshold

Based on Company_Handbook.md Section 6.4:
- Action Type: [email/linkedin_post/whatsapp]
- Threshold: [Low/Medium/High]
- Requires Approval: [Yes/No]

## Next Steps

1. Create approval request in Pending_Approval/
2. Wait for human decision
3. Execute if approved
```

### Approval Request (Pending_Approval/)

**Filename**: `APPROVAL_YYYYMMDD_HHMMSS_identifier.md`

**Example**: `APPROVAL_20260121_103000_email_client.md`

**Format**:
```markdown
---
type: approval_request
action_type: email | whatsapp | linkedin_post
requires_approval: true
priority: Low | Medium | High
status: pending
created_at: 2026-01-21T10:31:00Z
action_item_id: 20260121_103000_123456_email_client_name
plan_id: Plan_20260121_103000_email_client
---

# Approval Request: [Action Title]

## Proposed Action

**Type**: [Email/WhatsApp/LinkedIn Post]
**Target**: [Recipient/Contact/Audience]
**Priority**: [Low/Medium/High]

## Complete Draft

[Full text of email/message/post to be sent]

## Reasoning

[Why this action is recommended, based on Plan.md]

## Company Handbook Alignment

- **Rule**: [Relevant rule from Company_Handbook.md]
- **Threshold**: [Low/Medium/High]
- **Justification**: [Why this action aligns with rules]

## Recommendation

**APPROVE** | **REJECT** | **MODIFY**

[Explanation of recommendation]

---

## How to Approve

Move this file to `Approved/` folder:
```bash
mv Pending_Approval/APPROVAL_20260121_103000_email_client.md Approved/
```

## How to Reject

Move this file to `Rejected/` folder:
```bash
mv Pending_Approval/APPROVAL_20260121_103000_email_client.md Rejected/
```

## How to Modify

1. Edit this file with your changes
2. Move to `Approved/` folder when ready
```

### Execution Record (Done/)

**Filename**: `EXECUTED_YYYYMMDD_HHMMSS_identifier.md`

**Example**: `EXECUTED_20260121_103200_email_client.md`

**Format**:
```markdown
---
type: execution_record
action_type: email | whatsapp | linkedin_post
status: completed
executed_at: 2026-01-21T10:32:00Z
approved_by: user
approval_timestamp: 2026-01-21T10:31:30Z
result: success
---

# Executed: [Action Title]

## Action Details

**Type**: [Email/WhatsApp/LinkedIn Post]
**Target**: [Recipient/Contact/Audience]
**Executed At**: 2026-01-21T10:32:00Z

## Result

**Status**: ✅ Success
**Message ID**: [External system message ID]
**Confirmation**: [Delivery/send confirmation details]

## Approval Trail

- **Approved By**: user
- **Approved At**: 2026-01-21T10:31:30Z
- **Approval File**: APPROVAL_20260121_103000_email_client.md

## Audit Log

Logged to: `Logs/2026-01-21.json`
Entry ID: [Audit log entry ID]

## Original Action Item

Source: `Needs_Action/20260121_103000_123456_email_client_name.md`
Plan: `Plans/Plan_20260121_103000_email_client.md`
```

### Failed Execution (Failed/)

**Filename**: `FAILED_YYYYMMDD_HHMMSS_identifier.md`

**Example**: `FAILED_20260121_103200_email_client.md`

**Format**:
```markdown
---
type: execution_record
action_type: email | whatsapp | linkedin_post
status: failed
executed_at: 2026-01-21T10:32:00Z
approved_by: user
result: error
retry_count: 3
---

# Failed: [Action Title]

## Action Details

**Type**: [Email/WhatsApp/LinkedIn Post]
**Target**: [Recipient/Contact/Audience]
**Failed At**: 2026-01-21T10:32:00Z

## Error Details

**Error Type**: [Network timeout/Authentication failed/Rate limited/etc.]
**Error Message**: [Complete error message]
**HTTP Status**: [If applicable]

## Retry History

1. **Attempt 1** (10:32:00): [Error message]
2. **Attempt 2** (10:32:25): [Error message] (waited 25s)
3. **Attempt 3** (12:32:25): [Error message] (waited 2h)

## Next Steps

**Manual Intervention Required**:
1. Review error details above
2. Fix underlying issue (re-authenticate, check network, etc.)
3. Move this file back to `Approved/` to retry
4. Or move to `Rejected/` if no longer relevant

## Approval Trail

- **Approved By**: user
- **Approved At**: 2026-01-21T10:31:30Z
- **Approval File**: APPROVAL_20260121_103000_email_client.md

## Audit Log

Logged to: `Logs/2026-01-21.json`
Entry ID: [Audit log entry ID]
```

---

## Approval Process

### Step 1: Review Approval Request

Open the approval request file in your vault:

```bash
# View approval request
cat AI_Employee_Vault/Pending_Approval/APPROVAL_20260121_103000_email_client.md

# Or open in Obsidian for better formatting
```

**What to check**:
- ✅ Action type and target are correct
- ✅ Draft content is appropriate
- ✅ Reasoning aligns with your rules
- ✅ No sensitive information exposed
- ✅ Timing is appropriate

### Step 2: Make Decision

**Option A: Approve (Execute as-is)**

```bash
mv AI_Employee_Vault/Pending_Approval/APPROVAL_20260121_103000_email_client.md \
   AI_Employee_Vault/Approved/
```

**Option B: Reject (Do not execute)**

```bash
mv AI_Employee_Vault/Pending_Approval/APPROVAL_20260121_103000_email_client.md \
   AI_Employee_Vault/Rejected/
```

**Option C: Modify (Edit then approve)**

```bash
# Edit the file
nano AI_Employee_Vault/Pending_Approval/APPROVAL_20260121_103000_email_client.md

# Make your changes to the draft content

# Move to Approved/
mv AI_Employee_Vault/Pending_Approval/APPROVAL_20260121_103000_email_client.md \
   AI_Employee_Vault/Approved/
```

### Step 3: Orchestrator Executes

The orchestrator watches the `Approved/` folder and executes actions automatically:

```python
# Orchestrator polling loop (every 5 seconds)
while True:
    approved_files = list(Path("Approved/").glob("APPROVAL_*.md"))
    for file in approved_files:
        execute_action(file)
    time.sleep(5)
```

**Execution flow**:
1. Orchestrator detects file in `Approved/`
2. Reads action type and parameters
3. Routes to appropriate MCP server
4. Executes action via MCP server
5. Logs result to `Logs/YYYY-MM-DD.json`
6. Moves file to `Done/` (success) or `Failed/` (error)

### Step 4: Verify Execution

Check the execution record:

```bash
# View execution record
cat AI_Employee_Vault/Done/EXECUTED_20260121_103200_email_client.md

# Or check audit log
cat AI_Employee_Vault/Logs/2026-01-21.json | grep "20260121_103200"
```

---

## Claude Code Skills Integration

### needs-action-triage

**Purpose**: Process action items from `Needs_Action/` folder

**Usage**:
```
/needs-action-triage process the tasks
```

**What it does**:
1. Reads all files in `Needs_Action/`
2. For each action item:
   - Analyzes content against `Company_Handbook.md`
   - Creates `Plan.md` in `Plans/` folder
   - Creates approval request in `Pending_Approval/`
   - Archives original action item to `Done/`
3. Updates `Dashboard.md` with pending approvals count

**Output**:
- `Plans/Plan_YYYYMMDD_identifier.md`
- `Pending_Approval/APPROVAL_YYYYMMDD_identifier.md`

### approval-workflow-manager

**Purpose**: Handle approval/rejection workflow

**Usage**:
```
/approval-workflow-manager check pending approvals
```

**What it does**:
1. Lists all files in `Pending_Approval/`
2. Shows summary of each approval request
3. Checks for expired approvals (>24 hours)
4. Updates `Dashboard.md` with approval status

**Commands**:
- `check pending approvals` - List all pending approvals
- `expire old approvals` - Move expired approvals to separate folder
- `summarize rejections` - Analyze rejection patterns

### mcp-executor

**Purpose**: Execute approved actions via MCP servers

**Usage**:
```
/mcp-executor execute approved actions
```

**What it does**:
1. Reads all files in `Approved/` folder
2. For each approved action:
   - Routes to appropriate MCP server
   - Executes action
   - Logs result to `Logs/`
   - Moves to `Done/` or `Failed/`
3. Updates `Dashboard.md` with execution results

**Note**: This skill is typically called by the orchestrator, not manually.

---

## Approval Thresholds

Defined in `Company_Handbook.md` Section 6.4:

### Low Threshold
- **Actions**: Email responses to known contacts
- **Approval**: Always approve unless sensitive
- **Review Time**: <30 seconds
- **Auto-expire**: 24 hours

### Medium Threshold
- **Actions**: LinkedIn posts, WhatsApp messages
- **Approval**: Review content before approving
- **Review Time**: 1-5 minutes
- **Auto-expire**: 24 hours

### High Threshold
- **Actions**: Payments, contracts, legal documents
- **Approval**: Careful review required
- **Review Time**: 5-30 minutes
- **Auto-expire**: 48 hours

---

## Audit Logging

All approval decisions and executions are logged to `Logs/YYYY-MM-DD.json`:

### Approval Log Entry

```json
{
  "timestamp": "2026-01-21T10:31:30Z",
  "event_type": "approval_granted",
  "action_type": "email",
  "action_id": "APPROVAL_20260121_103000_email_client",
  "approved_by": "user",
  "approval_method": "file_move",
  "source_folder": "Pending_Approval",
  "target_folder": "Approved"
}
```

### Execution Log Entry

```json
{
  "timestamp": "2026-01-21T10:32:00Z",
  "action_type": "email_sent",
  "actor": "orchestrator",
  "target": "client@example.com",
  "approval_status": "approved",
  "approved_by": "user",
  "result": "success",
  "message_id": "abc123",
  "execution_time_ms": 1234
}
```

### Rejection Log Entry

```json
{
  "timestamp": "2026-01-21T10:31:30Z",
  "event_type": "approval_rejected",
  "action_type": "linkedin_post",
  "action_id": "APPROVAL_20260121_103000_linkedin_post",
  "rejected_by": "user",
  "rejection_method": "file_move",
  "source_folder": "Pending_Approval",
  "target_folder": "Rejected",
  "rejection_reason": "Content not aligned with brand voice"
}
```

---

## Error Handling

### Approval Request Expires

**Trigger**: Approval request in `Pending_Approval/` for >24 hours

**Action**:
1. Move to `Expired/` folder (created automatically)
2. Log expiration event
3. Notify user via `Dashboard.md`

**Recovery**:
```bash
# Move back to Pending_Approval/ to re-activate
mv AI_Employee_Vault/Expired/APPROVAL_20260121_103000_email_client.md \
   AI_Employee_Vault/Pending_Approval/
```

### Execution Fails

**Trigger**: MCP server returns error

**Action**:
1. Retry with exponential backoff (0s, 25s, 2h)
2. After 3 failures, move to `Failed/` folder
3. Log all retry attempts
4. Notify user via `Dashboard.md`

**Recovery**:
```bash
# Fix underlying issue (re-authenticate, check network, etc.)

# Move back to Approved/ to retry
mv AI_Employee_Vault/Failed/FAILED_20260121_103200_email_client.md \
   AI_Employee_Vault/Approved/
```

### Orchestrator Crashes

**Trigger**: Orchestrator process dies

**Action**:
1. PM2 automatically restarts orchestrator
2. Orchestrator resumes watching `Approved/` folder
3. No actions lost (files remain in `Approved/`)

**Recovery**:
```bash
# Check orchestrator status
pm2 status

# Restart if needed
pm2 restart orchestrator

# View logs
pm2 logs orchestrator
```

---

## Best Practices

### 1. Review Regularly

Check `Pending_Approval/` folder at least daily:
```bash
ls -la AI_Employee_Vault/Pending_Approval/
```

### 2. Provide Rejection Reasons

When rejecting, add a note in the file before moving:
```markdown
---
rejection_reason: "Content not aligned with brand voice"
---
```

### 3. Monitor Dashboard

Check `Dashboard.md` for system status:
```bash
cat AI_Employee_Vault/Dashboard.md
```

### 4. Review Audit Logs

Periodically review audit logs for patterns:
```bash
# View today's logs
cat AI_Employee_Vault/Logs/2026-01-21.json | jq .

# Count approvals vs rejections
grep "approval_granted" AI_Employee_Vault/Logs/2026-01-21.json | wc -l
grep "approval_rejected" AI_Employee_Vault/Logs/2026-01-21.json | wc -l
```

### 5. Clean Up Old Files

Archive old files periodically (keep 90 days minimum):
```bash
# Archive files older than 90 days
find AI_Employee_Vault/Done/ -name "*.md" -mtime +90 -exec mv {} Archive/ \;
```

---

## Troubleshooting

### Approval Not Executing

**Problem**: File moved to `Approved/` but not executing

**Solutions**:
1. Check orchestrator is running:
   ```bash
   pm2 status orchestrator
   ```

2. Check orchestrator logs:
   ```bash
   tail -f logs/orchestrator.log
   ```

3. Verify MCP servers are running:
   ```
   /mcp list
   ```

4. Check file format is correct (YAML frontmatter valid)

### Approval Request Not Created

**Problem**: Action item in `Needs_Action/` but no approval request

**Solutions**:
1. Run needs-action-triage skill:
   ```
   /needs-action-triage process the tasks
   ```

2. Check action item format is correct

3. Check `Company_Handbook.md` has approval thresholds defined

### Files Stuck in Approved/

**Problem**: Files remain in `Approved/` folder

**Solutions**:
1. Check orchestrator logs for errors
2. Verify MCP server connectivity
3. Check action type is valid (email/whatsapp/linkedin_post)
4. Manually move to `Failed/` and review error details

---

## Summary

**Approval Workflow Overview**:
- ✅ All external actions require human approval
- 📁 File-based workflow (move files between folders)
- 🔍 Complete transparency (all actions visible in vault)
- 📊 Audit trail (every decision logged)
- ⏱️ Fast approval (<30 seconds)

**Key Folders**:
- `Needs_Action/` - Unprocessed action items
- `Pending_Approval/` - Awaiting human decision
- `Approved/` - Approved for execution
- `Rejected/` - Rejected by human
- `Done/` - Successfully executed
- `Failed/` - Failed executions

**Claude Code Skills**:
- `needs-action-triage` - Process action items, create approval requests
- `approval-workflow-manager` - Manage approval workflow
- `mcp-executor` - Execute approved actions

**Next Steps**:
- See `docs/MCP_SERVERS.md` for MCP server details
- See `docs/WATCHER_SETUP.md` for watcher configuration
- See `SILVER_QUICKSTART.md` for end-to-end examples
