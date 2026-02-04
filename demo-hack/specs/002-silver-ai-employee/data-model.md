# Data Model: Silver Tier AI Employee

**Date**: 2026-01-15
**Feature**: Silver Tier AI Employee
**Purpose**: Define entities, state transitions, and data contracts

## Overview

This document defines the data model for Silver Tier AI Employee, including all entities that flow through the system from perception (watchers) to reasoning (Claude Code) to action (MCP servers) to completion (audit logs).

---

## Entity Definitions

### 1. Action Item

**Location**: `My_AI_Employee/AI_Employee_Vault/Needs_Action/`
**Lifecycle**: Created by watchers → Processed by needs-action-triage skill → Moved to Pending_Approval or archived to Done
**Format**: Markdown file with YAML frontmatter

#### Schema

```yaml
---
type: email | whatsapp_message | linkedin_notification | file_drop
source: gmail | whatsapp | linkedin | filesystem
source_id: string  # Unique ID from source system (email ID, message ID, etc.)
received: ISO8601 timestamp
status: pending | processed
priority: high | medium | low | auto
from: string  # Sender information (email address, phone number, LinkedIn profile)
subject: string  # Optional: email subject, message preview
content_hash: string  # SHA256 hash for duplicate detection
created_at: ISO8601 timestamp
processed_at: ISO8601 timestamp | null
---

# Action Item: [Brief Description]

## Source Information

**From**: [Sender details]
**Received**: [Timestamp]
**Channel**: [Gmail/WhatsApp/LinkedIn]

## Content

[Full message content or file reference]

## Context

[Any additional context from Company_Handbook.md rules]
```

#### Validation Rules

- `type` MUST be one of: email, whatsapp_message, linkedin_notification, file_drop
- `source` MUST be one of: gmail, whatsapp, linkedin, filesystem
- `source_id` MUST be unique per source (used for duplicate detection)
- `received` MUST be valid ISO8601 timestamp
- `content_hash` MUST be SHA256 hash of content for duplicate detection
- File name format: `YYYYMMDD_HHMMSS_microseconds_brief_description.md`

#### State Transitions

```
Created (pending) → Processed (processed) → Archived to Done or Pending_Approval
```

---

### 2. Approval Request

**Location**: `My_AI_Employee/AI_Employee_Vault/Pending_Approval/`
**Lifecycle**: Created by approval-workflow-manager skill → Human decision → Moved to Approved or Rejected
**Format**: Markdown file with YAML frontmatter

#### Schema

```yaml
---
type: approval_request
source: needs_action_triage
action_type: send_email | send_message | create_post | payment | system_change
requires_approval: true
status: pending | approved | rejected | expired
priority: high | medium | low
created_at: ISO8601 timestamp
expires_at: ISO8601 timestamp  # 24 hours from creation
approved_by: string | null
approved_at: ISO8601 timestamp | null
rejected_by: string | null
rejected_at: ISO8601 timestamp | null
rejection_reason: string | null
original_action_item: string  # Path to original action item in Needs_Action
---

# Approval Request: [Brief Description]

**Action Type**: [send_email/send_message/create_post/payment]
**Priority**: [HIGH/MEDIUM/LOW]
**Created**: [Timestamp]
**Expires**: [Timestamp]

## The Requested Action

[Detailed description of what the AI wants to do]

**Example for send_email**:
- **To**: client@example.com
- **Subject**: Project Update - Completion Confirmed
- **Body**: [Full email text]

## Why Approval is Needed

[Explanation of why this action requires human decision]

**Examples**:
- External communication to client
- Commits to delivery timeline
- Impacts business relationship
- Payment amount exceeds auto-approve threshold

## Approval Rules Applied

[List rules from Company_Handbook.md that triggered approval]

**Examples**:
- External communications require human review
- Commitments > 1 day require approval
- Client-facing emails need tone review
- Payments > $50 require approval

## Company_Handbook.md Context

[Relevant rules that apply to this decision]

## Recommendation

✅ **APPROVE** - Meets all company guidelines
❌ **REJECT** - [Reason if recommending rejection]
⚠️ **MODIFY** - [Suggested changes]

## Decision Required

Human must:
- [ ] Move to /Approved/ folder to approve
- [ ] Move to /Rejected/ folder to reject
- [ ] Edit this file to modify action before approving
```

#### Validation Rules

- `action_type` MUST be one of: send_email, send_message, create_post, payment, system_change
- `requires_approval` MUST be true (by definition)
- `status` MUST be one of: pending, approved, rejected, expired
- `expires_at` MUST be 24 hours from `created_at`
- `approved_by` and `approved_at` MUST be filled when status is approved
- `rejected_by` and `rejected_at` MUST be filled when status is rejected
- File name format: `YYYYMMDD_HHMMSS_action_type_brief_description.md`

#### State Transitions

```
Created (pending) → Human Decision:
  ├─ Approved (approved) → Moved to /Approved/
  ├─ Rejected (rejected) → Moved to /Rejected/
  └─ Expired (expired) → Moved to /Rejected/ with expiration note
```

---

### 3. Approved Action

**Location**: `My_AI_Employee/AI_Employee_Vault/Approved/`
**Lifecycle**: Moved from Pending_Approval → Picked up by orchestrator.py → Executed via MCP server → Moved to Done or Failed
**Format**: Markdown file with YAML frontmatter (same as Approval Request with status=approved)

#### Additional Fields for Execution

```yaml
---
# ... all fields from Approval Request ...
execution_status: queued | executing | completed | failed
execution_started_at: ISO8601 timestamp | null
execution_completed_at: ISO8601 timestamp | null
execution_attempts: integer  # Retry counter (max 3)
execution_error: string | null
mcp_server: email | linkedin | browser  # Which MCP server to use
---
```

#### State Transitions

```
Queued (queued) → Executing (executing) → Result:
  ├─ Completed (completed) → Moved to /Done/
  └─ Failed (failed) → Retry or Move to /Failed/
```

---

### 4. Execution Record (Done)

**Location**: `My_AI_Employee/AI_Employee_Vault/Done/`
**Lifecycle**: Final state after successful execution
**Format**: Markdown file with YAML frontmatter

#### Schema

```yaml
---
type: execution_record
original_action_type: send_email | send_message | create_post | payment | system_change
status: completed
approved_by: string
approved_at: ISO8601 timestamp
executed_at: ISO8601 timestamp
execution_duration_ms: integer
mcp_server: email | linkedin | browser
result: object  # Execution result from MCP server
audit_log_entry: string  # Path to audit log entry
---

# Execution Record: [Brief Description]

**Action**: [What was done]
**Approved By**: [Human name]
**Executed**: [Timestamp]
**Duration**: [X seconds]

## Execution Result

[Details of what happened]

**Example for send_email**:
- **Status**: Sent successfully
- **Message ID**: <abc123@gmail.com>
- **Sent At**: 2026-01-15T14:30:00Z
- **Confirmation**: Email delivered to recipient

## Audit Trail

See audit log: `/Logs/2026-01-15.json` (entry at 14:30:00)
```

#### Validation Rules

- `status` MUST be "completed"
- `approved_by` MUST match the human who approved
- `executed_at` MUST be after `approved_at`
- `execution_duration_ms` MUST be positive integer
- `result` MUST contain MCP server response

---

### 5. Execution Record (Failed)

**Location**: `My_AI_Employee/AI_Employee_Vault/Failed/`
**Lifecycle**: Final state after max retries exhausted
**Format**: Markdown file with YAML frontmatter

#### Schema

```yaml
---
type: execution_record
original_action_type: send_email | send_message | create_post | payment | system_change
status: failed
approved_by: string
approved_at: ISO8601 timestamp
first_attempt_at: ISO8601 timestamp
last_attempt_at: ISO8601 timestamp
total_attempts: integer  # Should be 3 (max retries)
mcp_server: email | linkedin | browser
error: string  # Final error message
error_history: array  # All error messages from retries
retry_delays: array  # Actual delays used: [0s, 25s, 2h]
audit_log_entry: string  # Path to audit log entry
---

# Failed Execution: [Brief Description]

**Action**: [What was attempted]
**Approved By**: [Human name]
**First Attempt**: [Timestamp]
**Last Attempt**: [Timestamp]
**Total Attempts**: 3

## Error Details

[Final error message]

## Retry History

1. **Attempt 1** (immediate): [Error message]
2. **Attempt 2** (after 25s): [Error message]
3. **Attempt 3** (after 2h): [Error message]

## Debugging Information

- **MCP Server**: [email/linkedin/browser]
- **Error Type**: [Authentication/Network/Validation/etc.]
- **Suggested Fix**: [What human should do to resolve]

## Audit Trail

See audit log: `/Logs/2026-01-15.json` (entries at multiple timestamps)
```

#### Validation Rules

- `status` MUST be "failed"
- `total_attempts` MUST be 3 (max retries)
- `error_history` MUST contain 3 error messages
- `retry_delays` MUST be [0, 25, 7200] (seconds)

---

### 6. Audit Log Entry

**Location**: `My_AI_Employee/AI_Employee_Vault/Logs/YYYY-MM-DD.json`
**Lifecycle**: Append-only, immutable during 90-day retention
**Format**: JSONL (one JSON object per line)

#### Schema

```json
{
  "timestamp": "2026-01-15T14:30:00.123456Z",
  "action_type": "send_email",
  "actor": "orchestrator.py",
  "target": "client@example.com",
  "approval_status": "approved",
  "approved_by": "Jane Doe",
  "approved_at": "2026-01-15T14:25:00Z",
  "execution_status": "completed",
  "execution_duration_ms": 1234,
  "mcp_server": "email",
  "result": {
    "status": "sent",
    "message_id": "abc123",
    "sanitized": true
  },
  "error": null,
  "retry_attempt": 1,
  "credentials_sanitized": true,
  "metadata": {
    "original_action_item": "Needs_Action/20260115_142000_client_email.md",
    "approval_request": "Pending_Approval/20260115_142500_send_email_client.md"
  }
}
```

#### Sanitization Rules

- **API Keys**: Show first 4 characters + "***" (e.g., "sk-a***")
- **Passwords**: Redact entirely ("[REDACTED]")
- **Tokens**: Redact entirely ("[REDACTED]")
- **Credit Cards**: Show last 4 digits (e.g., "****1234")
- **PII (emails)**: Truncate domain (e.g., "user@*****.com")
- **Phone Numbers**: Show last 4 digits (e.g., "***-***-1234")

#### Validation Rules

- `timestamp` MUST be ISO8601 with microseconds
- `action_type` MUST match approval request action_type
- `approval_status` MUST be "approved" (only approved actions are executed)
- `approved_by` MUST be non-empty string
- `credentials_sanitized` MUST be true
- File name format: `YYYY-MM-DD.json` (one file per day)
- Each line MUST be valid JSON object

#### Retention Policy

- **Minimum**: 90 days in active logs
- **Archive**: 2 years for compliance
- **Immutable**: No edits during retention period
- **Queries**: Support filtering by action_type, status, actor, date range

---

### 7. Company Handbook

**Location**: `My_AI_Employee/AI_Employee_Vault/Company_Handbook.md`
**Lifecycle**: User-maintained, read by all skills
**Format**: Markdown with structured sections

#### Schema

```markdown
# Company Handbook

## Communication Rules

### Email Guidelines
- Always be professional with clients
- Confirm delivery dates with management first
- Follow brand voice guidelines
- Response time: within 24 hours for clients

### WhatsApp Guidelines
- Urgent keywords: "urgent", "help", "asap", "invoice", "payment"
- Response time: within 2 hours for urgent messages
- Always acknowledge receipt

### LinkedIn Guidelines
- Post schedule: Mondays and Thursdays at 9:00 AM
- Tone: Professional, informative, engaging
- Hashtags: #automation #business #innovation
- Engagement: Like and comment on relevant posts

## Approval Thresholds

### Auto-Approve (No Human Review)
- Emails to known contacts (in contact list)
- Recurring payments < $50
- Scheduled LinkedIn posts (pre-approved content)

### Require Approval (Human Review)
- All external communications to new contacts
- Payments > $50
- Any commitments > 1 day
- Policy changes
- Banking/financial actions

### Never Auto-Retry (Always Require Fresh Approval)
- Banking/payment actions
- Legal/compliance actions
- Account deletions

## Business Context

### Current Projects
- Project A: Client XYZ, deadline 2026-02-01
- Project B: Internal tool, ongoing

### Key Contacts
- Client A: client-a@example.com (high priority)
- Vendor B: vendor-b@example.com (payment terms: Net 30)

### Financial Rules
- Payment approval: Manager approval for > $500
- Invoice processing: Within 7 days of receipt
- Expense tracking: All expenses logged in vault
```

#### Validation Rules

- MUST be valid Markdown
- MUST contain sections: Communication Rules, Approval Thresholds, Business Context
- SHOULD be updated by user as business needs change
- READ by: needs-action-triage, approval-workflow-manager skills

---

### 8. Dashboard

**Location**: `My_AI_Employee/AI_Employee_Vault/Dashboard.md`
**Lifecycle**: Updated by obsidian-vault-ops skill after each action
**Format**: Markdown with structured sections

#### Schema

```markdown
# AI Employee Dashboard

**Last Updated**: 2026-01-15 14:30:00

## System Status

- **Watchers**: ✅ All running (Gmail, WhatsApp, LinkedIn, Filesystem)
- **Orchestrator**: ✅ Running
- **MCP Servers**: ✅ All healthy (Email, LinkedIn, Browser)

## Pending Actions

### Needs Action (3 items)
- [Client email from client-a@example.com](Needs_Action/20260115_142000_client_email.md)
- [WhatsApp message from +1234567890](Needs_Action/20260115_143000_whatsapp_urgent.md)
- [LinkedIn connection request](Needs_Action/20260115_144000_linkedin_connection.md)

### Pending Approval (2 items)
- [Send email to client-a@example.com](Pending_Approval/20260115_142500_send_email_client.md) - Expires in 23h
- [LinkedIn post about automation](Pending_Approval/20260115_143500_create_post_linkedin.md) - Expires in 22h

### Approved (1 item)
- [Send email to vendor-b@example.com](Approved/20260115_141500_send_email_vendor.md) - Queued for execution

## Recent Activity (Last 24 Hours)

### Completed (5 items)
- ✅ Sent email to client-a@example.com (14:30)
- ✅ Posted to LinkedIn (09:00)
- ✅ Replied to WhatsApp message (13:15)
- ✅ Processed invoice from vendor-b (11:00)
- ✅ Updated project status (10:30)

### Failed (1 item)
- ❌ Send email to client-c@example.com (Gmail API timeout, retrying)

### Rejected (0 items)

## Statistics

- **Actions Today**: 8 total (5 completed, 1 failed, 2 pending)
- **Approval Rate**: 100% (all approved actions executed)
- **Average Response Time**: 15 minutes (from action item to approval)
- **Average Execution Time**: 3 seconds (from approval to completion)

## Alerts

- ⚠️ WhatsApp session expires in 7 days - re-scan QR code soon
- ⚠️ Gmail API quota: 80% used today (reset at midnight)
```

#### Update Rules

- MUST update after each action item processed
- MUST update after each approval decision
- MUST update after each execution completion
- SHOULD use append/section updates (not full rewrites)
- MUST preserve user-added notes

---

## State Transition Diagram

```
┌─────────────────┐
│  Watcher        │
│  (Perception)   │
└────────┬────────┘
         │ Creates
         ▼
┌─────────────────┐
│  Action Item    │
│  /Needs_Action/ │
└────────┬────────┘
         │ Processed by needs-action-triage
         ▼
    ┌────┴────┐
    │ Decision│
    └────┬────┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
┌─────────────┐    ┌──────────────────┐
│  Archive    │    │ Approval Request │
│  /Done/     │    │ /Pending_Approval/│
└─────────────┘    └────────┬─────────┘
                            │ Human Decision
                       ┌────┴────┐
                       │         │
                       ▼         ▼
                  ┌─────────┐ ┌──────────┐
                  │Approved │ │ Rejected │
                  │/Approved/│ │/Rejected/│
                  └────┬────┘ └──────────┘
                       │ Orchestrator picks up
                       ▼
                  ┌─────────────┐
                  │  Execution  │
                  │  (MCP Server)│
                  └────┬────────┘
                       │
                  ┌────┴────┐
                  │         │
                  ▼         ▼
            ┌─────────┐ ┌────────┐
            │ Success │ │ Failed │
            │ /Done/  │ │/Failed/│
            └─────────┘ └────────┘
                  │         │
                  └────┬────┘
                       │ Audit Logger
                       ▼
                  ┌─────────────┐
                  │  Audit Log  │
                  │  /Logs/     │
                  └─────────────┘
```

---

## Relationships

### Action Item → Approval Request
- **Type**: One-to-One (optional)
- **Link**: `original_action_item` field in Approval Request
- **Condition**: Only if approval needed

### Approval Request → Approved Action
- **Type**: One-to-One
- **Link**: Same file moved between folders
- **Condition**: Human approves

### Approved Action → Execution Record
- **Type**: One-to-One
- **Link**: Same file moved to Done or Failed
- **Condition**: After execution attempt

### Execution Record → Audit Log Entry
- **Type**: One-to-Many (one record, multiple log entries if retries)
- **Link**: `audit_log_entry` field in Execution Record
- **Condition**: Always created

### Company Handbook → All Entities
- **Type**: Many-to-One (read-only reference)
- **Link**: Rules applied during processing
- **Condition**: Always consulted

### Dashboard → All Entities
- **Type**: One-to-Many (aggregation)
- **Link**: Summary of all entities
- **Condition**: Updated after each state change

---

## Validation & Integrity

### Duplicate Detection

```python
def is_duplicate(action_item: dict) -> bool:
    """Check if action item is duplicate."""
    content_hash = action_item['content_hash']
    source_id = action_item['source_id']

    # Check by source_id first (exact match)
    existing = find_by_source_id(source_id)
    if existing:
        return True

    # Check by content_hash (fuzzy match)
    existing = find_by_content_hash(content_hash)
    if existing:
        return True

    return False
```

### YAML Frontmatter Preservation

```python
import frontmatter

def move_file_safely(src: Path, dst: Path):
    """Move file while preserving YAML frontmatter."""
    # Read with frontmatter
    post = frontmatter.load(src)

    # Update metadata
    post.metadata['moved_at'] = datetime.now().isoformat()
    post.metadata['moved_from'] = str(src)

    # Write to destination
    with open(dst, 'w') as f:
        f.write(frontmatter.dumps(post))

    # Remove source
    src.unlink()
```

### Audit Log Integrity

```python
def append_audit_log(entry: dict):
    """Append to audit log with integrity check."""
    log_file = Path(f"Logs/{datetime.now().strftime('%Y-%m-%d')}.json")

    # Sanitize credentials
    entry = sanitize_credentials(entry)

    # Validate schema
    validate_audit_entry(entry)

    # Append as JSONL
    with open(log_file, 'a') as f:
        f.write(json.dumps(entry) + '\n')
```

---

## Conclusion

This data model provides:
- ✅ Clear entity definitions with validation rules
- ✅ State transition diagram for lifecycle management
- ✅ Relationship mapping between entities
- ✅ Integrity checks for duplicate detection and YAML preservation
- ✅ Audit trail with credential sanitization
- ✅ Alignment with Constitution v2.0.0 principles

**Ready for Phase 1: Contract Generation**
