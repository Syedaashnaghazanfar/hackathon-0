---
name: audit-logger
description: >
  Comprehensive audit logging for all AI Employee external actions: emails sent, posts published,
  payments processed, form submissions, API calls. Records who (user/AI), what (action details),
  when (timestamps), why (approval reason), with credential sanitization and compliance tracking.
  Use when: (1) Logging action execution results, (2) Creating audit trails, (3) Recording approval
  decisions, (4) Tracking financial transactions, (5) Compliance reporting, (6) Security incident
  review. Trigger phrases: "log action", "create audit trail", "record execution", "compliance report",
  "audit history", "action log", "track external actions".
---

# Audit Logger (Compliance & Action Tracking)

Log all external-facing AI actions with full audit trail: what happened, who approved it, when, why, and the result. Sanitize credentials automatically. Generate compliance reports.

## Quick Start

### Logging Actions Automatically

Audit logging happens automatically when actions are executed:

1. **Action created** → Logged to audit trail
2. **Approval requested** → Logged who, when, decision
3. **Action executed** → Logged result, timestamp, MCP server used
4. **Success/Failure** → Logged outcome with error details if failed

### Viewing Audit Logs

```bash
# View recent audit log entries
tail -f logs/audit.log

# Search audit log
grep "email_send" logs/audit.log

# Generate audit report
python scripts/generate_audit_report.py
```

## Audit Trail Structure

### Log Entry Format

All audit entries are JSON structured logs with consistent format:

```json
{
  "timestamp": "2026-01-14T14:30:00Z",
  "event_type": "action_executed",
  "action_id": "email_client_update_20260114",
  "action_type": "send_email",
  "source_system": "approval_workflow",
  "actor": "ai_employee",
  "approval_info": {
    "approved_by": "jane_doe",
    "approved_at": "2026-01-14T14:35:00Z",
    "approval_reason": "Email meets brand guidelines"
  },
  "action_details": {
    "recipient": "client@example.com",
    "subject": "Project Update",
    "status": "success",
    "message_id": "abc123xyz"
  },
  "execution_info": {
    "mcp_server": "email_mcp",
    "execution_time_ms": 2300,
    "status": "success"
  },
  "compliance": {
    "external_action": true,
    "requires_approval": true,
    "approved": true,
    "policy_violations": []
  }
}
```

### Log Entry Types

1. **action_requested** - When approval requested
2. **action_approved** - When human approved
3. **action_rejected** - When human rejected
4. **action_executed** - When action ran
5. **action_failed** - When execution failed
6. **action_retried** - When retry attempted
7. **approval_timeout** - When approval timed out

## Sensitive Data Sanitization

Audit logger automatically sanitizes credentials and sensitive data:

### Email Redaction

**Original**:
```
To: client@example.com
Body: Hi Sarah, your API key is sk_live_abc123xyz...
```

**Logged as**:
```
To: client@*****.com (email sanitized)
Body: Hi Sarah, your API key is sk_live_*** (credential sanitized)
```

### Payment Data Redaction

**Original**:
```
Credit Card: 4532 1234 5678 9010
Amount: $800
```

**Logged as**:
```
Credit Card: 4532 **** **** 9010 (PAN sanitized)
Amount: $800 (safe to log)
```

### API Key Redaction

**Original**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
LinkedIn Token: li_2026_abc123xyz...
```

**Logged as**:
```
Authorization: Bearer *** (token redacted)
LinkedIn Token: li_2026_*** (token redacted)
```

## Audit Report Generation

### Generate Monthly Report

```bash
python scripts/generate_audit_report.py --period month
```

**Output**:
```markdown
# Monthly Audit Report - January 2026

## Summary
- Total Actions: 247
- Approved: 245 (99.2%)
- Rejected: 2 (0.8%)
- Executed Successfully: 243 (98.4%)
- Executed with Errors: 4 (1.6%)

## Action Breakdown
- Emails Sent: 145
- LinkedIn Posts: 32
- Payments Processed: 18
- Form Submissions: 42
- Other Actions: 10

## Approval Times
- Average: 3.2 minutes
- Median: 2.1 minutes
- Fastest: 0.5 minutes
- Slowest: 47.3 minutes

## Errors Summary
- Gmail auth token expired: 2
- LinkedIn rate limit: 1
- Browser automation timeout: 1

## Compliance Status
✅ All actions approved before execution
✅ No policy violations detected
✅ Credentials properly sanitized
✅ Audit trail complete and immutable
```

### Generate Compliance Report

```bash
python scripts/generate_compliance_report.py
```

Shows:
- Policy compliance percentage
- Approval workflow adherence
- Error rates and types
- Recommendations for improvement

## Audit Log Locations

Logs are stored with daily rotation:

```
logs/
├── audit.log            # Current day's audit log
├── audit.2026-01-14.log # Previous day's log
├── audit.2026-01-13.log
└── ...                  # 90-day retention
```

Each log file is JSON lines format (one JSON object per line).

## Search & Filter

### Search by Action Type

```bash
# Find all emails sent
grep '"action_type": "send_email"' logs/audit.log

# Find all LinkedIn posts
grep '"action_type": "create_post"' logs/audit.log

# Find all payments
grep '"action_type": "payment"' logs/audit.log
```

### Search by Status

```bash
# Find all successful actions
grep '"status": "success"' logs/audit.log

# Find all failed actions
grep '"status": "failed"' logs/audit.log

# Find all pending approvals
grep '"event_type": "action_requested"' logs/audit.log
```

### Search by Actor

```bash
# Find actions by AI Employee
grep '"actor": "ai_employee"' logs/audit.log

# Find approvals by specific person
grep '"approved_by": "jane_doe"' logs/audit.log
```

### Search by Date Range

```bash
# Actions today
grep "2026-01-14" logs/audit.log

# Actions in specific hour
grep "2026-01-14T14:" logs/audit.log
```

## Compliance & Security

### Data Retention

- Audit logs retained for 90 days
- After 90 days: Archived to /archive/audit/
- Archived logs kept for 2 years for compliance
- Deletion happens automatically based on policy

### Data Protection

- Credentials: Automatically redacted/sanitized
- PII: Email addresses truncated (client@*****.com)
- Payment data: Card numbers show last 4 digits only
- All logs: Immutable (write-once, no deletion during retention)

### Immutability

Audit logs are write-only:
- Cannot be modified after creation
- Cannot be deleted during 90-day retention
- Tampering detected via file checksums
- Integrity verified daily

### Compliance Standards

- GDPR: Personal data minimization (credentials redacted)
- SOC 2: Complete audit trail with timestamps
- PCI DSS: Payment data sanitized, no full card logging
- General: Non-repudiation (proof of who did what when)

## Integration Points

### With Approval Workflow

```json
{
  "event_type": "action_approved",
  "actor": "user",
  "approval_info": {
    "approved_by": "jane_doe",
    "approved_at": "2026-01-14T14:35:00Z",
    "approval_reason": "Meets brand guidelines and policy"
  }
}
```

### With MCP Executor

```json
{
  "event_type": "action_executed",
  "execution_info": {
    "mcp_server": "email_mcp",
    "execution_time_ms": 2300,
    "status": "success",
    "result": {
      "message_id": "abc123xyz"
    }
  }
}
```

### With Multi-Watcher

```json
{
  "event_type": "action_requested",
  "source_system": "multi_watcher_runner",
  "action_details": {
    "source_watcher": "gmail",
    "triggered_by": "client_email"
  }
}
```

## References

See `references/audit-fields.md` for complete field definitions.

See `references/sanitization-patterns.md` for credential redaction examples.

See `references/compliance-standards.md` for regulatory requirements.

## Monitoring Audit Log Health

```bash
# Check log file size (should rotate daily)
ls -lh logs/audit*.log

# Verify log integrity
python scripts/verify_audit_logs.py

# Check for anomalies
python scripts/detect_audit_anomalies.py
```
