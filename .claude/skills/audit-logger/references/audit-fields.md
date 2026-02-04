# Audit Log Fields Reference

## Complete Field Definitions

### Core Audit Fields

#### `timestamp` (ISO 8601)
When the event occurred.
- Format: `2026-01-14T14:30:00.123456Z`
- Timezone: Always UTC
- Precision: Microseconds (for accurate sequencing)

#### `event_type` (string)
What type of event this is.
- Values: `action_requested`, `action_approved`, `action_rejected`, `action_executed`, `action_failed`, `action_retried`, `approval_timeout`, `system_error`

#### `action_id` (string)
Unique identifier for the action.
- Format: `{action_type}_{vault_timestamp}_{hash}`
- Example: `email_send_20260114_143000_abc123`
- Immutable throughout action lifecycle

#### `action_type` (string)
Category of action.
- Values: `send_email`, `create_post`, `send_message`, `payment`, `form_fill`, `api_call`, `calendar_event`, `document_create`

#### `source_system` (string)
Which system initiated the action.
- Values: `multi_watcher_runner`, `approval_workflow`, `mcp_executor`, `user_action`, `scheduled_task`

#### `actor` (string)
Who is performing/involved in this event.
- Values: `ai_employee`, `user`, `system`, `audit_logger`
- Examples: `ai_employee` (AI made decision), `jane_doe` (human approved)

### Approval Information

#### `approval_info` (object)
Details about approval decision.

```json
{
  "approved_by": "jane_doe",           // Who approved (null if rejected/no approval needed)
  "approval_action": "approved",       // "approved", "rejected", "needs_info", "needs_modification"
  "approved_at": "2026-01-14T14:35:00Z",
  "approval_reason": "Meets brand guidelines",
  "approval_duration_seconds": 300,    // How long approval took
  "modifications_requested": null,     // If changes needed before approval
  "approval_notes": "Good to send"
}
```

### Action Details

#### `action_details` (object)
Specific information about what action is being performed.

**For email actions**:
```json
{
  "recipient": "client@*****.com",      // Email sanitized
  "subject": "[truncated - 50 chars]",
  "body_preview": "[truncated - 100 chars]",
  "has_attachments": false,
  "recipients_count": 1
}
```

**For LinkedIn actions**:
```json
{
  "post_type": "text_post",             // "text_post", "link_share", "article"
  "character_count": 245,
  "hashtag_count": 3,
  "scheduled": false
}
```

**For payments**:
```json
{
  "vendor": "Tech Solutions Inc",
  "amount": 800,
  "currency": "USD",
  "invoice_number": "TS-2026-001",
  "payment_method": "bank_transfer"     // Never log full payment details
}
```

**For form submissions**:
```json
{
  "form_url": "https://example.com/form",
  "form_fields_count": 5,
  "fields_filled": 5
}
```

### Execution Information

#### `execution_info` (object)
How the action was executed and what resulted.

```json
{
  "mcp_server": "email_mcp",            // Which MCP server executed it
  "execution_time_ms": 2300,            // Total execution time
  "attempts": 1,                        // Number of retry attempts
  "status": "success",                  // "success", "failed", "partial"
  "error_type": null,                   // Error category if failed
  "error_message": null,                // Error details (sanitized)
  "result": {
    "message_id": "abc123xyz",          // Service-provided identifier
    "external_id": "msg_12345",         // ID in external system
    "status_url": "https://..."         // Where to check status
  }
}
```

### Compliance Information

#### `compliance` (object)
Regulatory and policy compliance status.

```json
{
  "external_action": true,              // Is this external-facing?
  "requires_approval": true,            // Did it need approval?
  "approved": true,                     // Was it approved (if needed)?
  "policy_violations": [],              // Any policy breaches?
  "data_classification": "public",      // "public", "internal", "confidential", "restricted"
  "audit_required": false,              // Needs compliance review?
  "retention_days": 90                  // How long to keep this log
}
```

### Source Tracking

#### `source_info` (object)
Where this action originated from.

```json
{
  "source_watcher": "gmail",            // "gmail", "whatsapp", "linkedin", "filesystem"
  "source_contact": "client@example.com",
  "source_message_id": "msg_12345",
  "triggered_by": "client_email"        // What triggered the action
}
```

### Audit Trail Chain

#### `audit_chain` (object)
Complete history of this action's lifecycle.

```json
{
  "created_event_id": "evt_001",        // When first created
  "approved_event_id": "evt_003",       // When approved
  "executed_event_id": "evt_005",       // When executed
  "previous_event": "evt_004",          // Link to previous log entry
  "next_event": "evt_006"               // Link to next log entry (when complete)
}
```

## Event Type Specific Fields

### action_requested

When action is first created (goes to approval).

```json
{
  "event_type": "action_requested",
  "source_system": "multi_watcher_runner",
  "action_details": {
    "recipient": "client@*****.com",
    "priority": "high"
  },
  "approval_info": {
    "approval_required": true,
    "estimated_approval_time_seconds": 120
  }
}
```

### action_approved

When human approves action.

```json
{
  "event_type": "action_approved",
  "actor": "jane_doe",
  "approval_info": {
    "approved_by": "jane_doe",
    "approved_at": "2026-01-14T14:35:00Z",
    "approval_reason": "Meets brand guidelines"
  }
}
```

### action_rejected

When human rejects action.

```json
{
  "event_type": "action_rejected",
  "actor": "jane_doe",
  "approval_info": {
    "approved_by": "jane_doe",
    "approval_action": "rejected",
    "approval_reason": "Violates policy on external commitments"
  }
}
```

### action_executed

When action successfully runs.

```json
{
  "event_type": "action_executed",
  "source_system": "mcp_executor",
  "execution_info": {
    "status": "success",
    "execution_time_ms": 2300,
    "result": {
      "message_id": "abc123xyz",
      "external_id": "msg_12345"
    }
  }
}
```

### action_failed

When action execution fails.

```json
{
  "event_type": "action_failed",
  "source_system": "mcp_executor",
  "execution_info": {
    "status": "failed",
    "error_type": "authentication_error",
    "error_message": "Gmail OAuth token expired",
    "execution_time_ms": 1200,
    "will_retry": true,
    "retry_at": "2026-01-14T15:00:00Z"
  }
}
```

### action_retried

When a failed action is retried.

```json
{
  "event_type": "action_retried",
  "source_system": "mcp_executor",
  "execution_info": {
    "retry_attempt": 2,
    "max_retries": 3,
    "previous_error": "Gmail OAuth token expired",
    "recovery_action": "Token refreshed",
    "status": "success"
  }
}
```

## Credential Sanitization Patterns

### Email Addresses

- **Input**: `client@example.com`
- **Output**: `client@*****.com`

### Phone Numbers

- **Input**: `+1-555-123-4567`
- **Output**: `+1-555-***-4567`

### Credit Card Numbers (PAN)

- **Input**: `4532 1234 5678 9010`
- **Output**: `4532 **** **** 9010`

### API Keys & Tokens

- **Input**: `sk_live_abc123xyz456789`
- **Output**: `sk_live_*** (token redacted)`

### OAuth Access Tokens

- **Input**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **Output**: `*** (token redacted)`

### Passwords

- **Input**: (never logged)
- **Output**: (never logged)

### Social Security Numbers

- **Input**: `123-45-6789`
- **Output**: `***-**-6789`

### Full Names (if PII)

- **Input**: `Jane Doe Smith`
- **Output**: `Jane D*** (name partially redacted)` (only if PII context)

## Log File Naming Convention

```
logs/audit.log                # Current active log
logs/audit.2026-01-14.log     # Daily rotation
logs/audit.2026-01-13.log
logs/audit.2026-01-12.log
```

Daily rotation happens at midnight UTC.
Each file kept for 90 days, then archived.

## Query Examples

### Get all approved actions
```bash
grep '"approval_action": "approved"' logs/audit.log
```

### Get all failed executions
```bash
grep '"status": "failed"' logs/audit.log
```

### Get specific action by ID
```bash
grep '"action_id": "email_send_20260114_143000_abc123"' logs/audit.log
```

### Get actions requiring external approval
```bash
grep '"external_action": true' logs/audit.log
```

### Get actions by actor
```bash
grep '"approved_by": "jane_doe"' logs/audit.log
```

### Timeline of specific action
```bash
# Get all events for one action
grep '"action_id": "email_send_20260114_143000_abc123"' logs/audit*.log | sort
```
