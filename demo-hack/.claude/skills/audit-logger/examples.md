# Audit Logger Examples

## Complete Action Lifecycle - Audit Trail

Showing all audit log entries for one email action from creation through execution.

### Event 1: Action Requested (Created)

```json
{
  "timestamp": "2026-01-14T14:30:00.123456Z",
  "event_type": "action_requested",
  "action_id": "email_send_client_20260114_143000_a1b2c3",
  "action_type": "send_email",
  "source_system": "gmail_watcher",
  "actor": "ai_employee",
  "source_info": {
    "source_watcher": "gmail",
    "source_contact": "client@example.com",
    "source_message_id": "msg_abc123",
    "triggered_by": "inbound_email"
  },
  "action_details": {
    "recipient": "client@*****.com",
    "subject": "Project Update - Phase 1 Complete",
    "has_attachments": false
  },
  "compliance": {
    "external_action": true,
    "requires_approval": true,
    "data_classification": "public"
  },
  "approval_info": {
    "approval_required": true,
    "estimated_approval_time_seconds": 300
  }
}
```

### Event 2: Action Approved

```json
{
  "timestamp": "2026-01-14T14:35:00.234567Z",
  "event_type": "action_approved",
  "action_id": "email_send_client_20260114_143000_a1b2c3",
  "action_type": "send_email",
  "source_system": "approval_workflow",
  "actor": "jane_doe",
  "approval_info": {
    "approved_by": "jane_doe",
    "approval_action": "approved",
    "approved_at": "2026-01-14T14:35:00Z",
    "approval_reason": "Email tone matches brand guidelines, content accurate",
    "approval_duration_seconds": 300,
    "approval_notes": "Good to send"
  },
  "compliance": {
    "external_action": true,
    "requires_approval": true,
    "approved": true
  },
  "audit_chain": {
    "created_event_id": "evt_001",
    "previous_event": "evt_001"
  }
}
```

### Event 3: Action Executed (Success)

```json
{
  "timestamp": "2026-01-14T14:36:00.345678Z",
  "event_type": "action_executed",
  "action_id": "email_send_client_20260114_143000_a1b2c3",
  "action_type": "send_email",
  "source_system": "mcp_executor",
  "actor": "ai_employee",
  "action_details": {
    "recipient": "client@*****.com",
    "subject": "Project Update - Phase 1 Complete"
  },
  "execution_info": {
    "mcp_server": "email_mcp",
    "execution_time_ms": 2300,
    "attempts": 1,
    "status": "success",
    "result": {
      "message_id": "abc123xyz789",
      "external_id": "msg_client_20260114_143600",
      "status_url": "https://mail.google.com/mail/u/0/#inbox/..."
    }
  },
  "compliance": {
    "external_action": true,
    "requires_approval": true,
    "approved": true,
    "audit_required": false
  },
  "audit_chain": {
    "created_event_id": "evt_001",
    "approved_event_id": "evt_002",
    "previous_event": "evt_002"
  }
}
```

---

## Failed Action with Retry

### Event 1: Action Executed - Failed

```json
{
  "timestamp": "2026-01-14T14:36:00.123456Z",
  "event_type": "action_failed",
  "action_id": "email_send_accounting_20260114_143600_x9y8z7",
  "action_type": "send_email",
  "source_system": "mcp_executor",
  "actor": "ai_employee",
  "action_details": {
    "recipient": "accounting@*****.com",
    "subject": "Invoice Payment Confirmation"
  },
  "execution_info": {
    "mcp_server": "email_mcp",
    "execution_time_ms": 523,
    "attempts": 1,
    "status": "failed",
    "error_type": "authentication_error",
    "error_message": "Gmail OAuth token expired - will refresh and retry",
    "will_retry": true,
    "retry_at": "2026-01-14T15:00:00Z"
  },
  "compliance": {
    "external_action": true,
    "approved": true,
    "audit_required": true
  }
}
```

### Event 2: Action Retried - Success

```json
{
  "timestamp": "2026-01-14T15:00:30.234567Z",
  "event_type": "action_retried",
  "action_id": "email_send_accounting_20260114_143600_x9y8z7",
  "action_type": "send_email",
  "source_system": "mcp_executor",
  "actor": "ai_employee",
  "execution_info": {
    "mcp_server": "email_mcp",
    "retry_attempt": 2,
    "max_retries": 3,
    "previous_error": "Gmail OAuth token expired",
    "recovery_action": "Gmail OAuth token refreshed automatically",
    "execution_time_ms": 1800,
    "status": "success",
    "result": {
      "message_id": "xyz789abc123",
      "external_id": "msg_accounting_20260114_150030"
    }
  },
  "compliance": {
    "external_action": true,
    "approved": true,
    "audit_required": true
  },
  "audit_chain": {
    "previous_event": "evt_004",
    "related_failure": "evt_004"
  }
}
```

---

## Rejected Action - Policy Violation

```json
{
  "timestamp": "2026-01-14T14:05:00.123456Z",
  "event_type": "action_rejected",
  "action_id": "whatsapp_send_client_20260114_140000_r4s5t6",
  "action_type": "send_message",
  "source_system": "approval_workflow",
  "actor": "jane_doe",
  "approval_info": {
    "approved_by": "jane_doe",
    "approval_action": "rejected",
    "approved_at": "2026-01-14T14:05:00Z",
    "approval_reason": "Violates policy: Cannot commit to deadline without manager approval",
    "rejection_notes": "Action commits to Feb 15 deadline which CEO hasn't authorized yet. Please get approval from CEO first.",
    "approval_duration_seconds": 180
  },
  "action_details": {
    "recipient": "Client B (WhatsApp)",
    "message_preview": "We can deliver by Feb 15...",
    "message_type": "commitment"
  },
  "compliance": {
    "external_action": true,
    "requires_approval": true,
    "approved": false,
    "policy_violations": ["unauthorized_commitment"],
    "audit_required": true
  },
  "audit_chain": {
    "created_event_id": "evt_001"
  }
}
```

---

## Payment Action with Full Audit Trail

### Event 1: Payment Requested

```json
{
  "timestamp": "2026-01-14T16:00:00.123456Z",
  "event_type": "action_requested",
  "action_id": "payment_vendor_20260114_160000_p1q2r3",
  "action_type": "payment",
  "source_system": "filesystem_watcher",
  "actor": "ai_employee",
  "source_info": {
    "source_watcher": "filesystem",
    "triggered_by": "invoice_file_upload"
  },
  "action_details": {
    "vendor": "Tech Solutions Inc",
    "amount": 800,
    "currency": "USD",
    "invoice_number": "TS-2026-001",
    "payment_method": "bank_transfer"
  },
  "compliance": {
    "external_action": true,
    "requires_approval": true,
    "data_classification": "confidential",
    "audit_required": true
  }
}
```

### Event 2: Payment Approved

```json
{
  "timestamp": "2026-01-14T16:25:00.234567Z",
  "event_type": "action_approved",
  "action_id": "payment_vendor_20260114_160000_p1q2r3",
  "action_type": "payment",
  "source_system": "approval_workflow",
  "actor": "jane_doe",
  "approval_info": {
    "approved_by": "jane_doe",
    "approval_action": "approved",
    "approved_at": "2026-01-14T16:25:00Z",
    "approval_reason": "Invoice verified, vendor confirmed, amount matches invoice",
    "approval_duration_seconds": 1500,
    "verification_checks": [
      "Invoice matches request",
      "Services already delivered",
      "Vendor is on approved list",
      "Budget available in Dev category"
    ]
  },
  "action_details": {
    "vendor": "Tech Solutions Inc",
    "amount": 800,
    "currency": "USD",
    "invoice_number": "TS-2026-001"
  },
  "compliance": {
    "external_action": true,
    "approved": true,
    "audit_required": true
  }
}
```

### Event 3: Payment Executed

```json
{
  "timestamp": "2026-01-14T16:30:00.345678Z",
  "event_type": "action_executed",
  "action_id": "payment_vendor_20260114_160000_p1q2r3",
  "action_type": "payment",
  "source_system": "mcp_executor",
  "actor": "ai_employee",
  "action_details": {
    "vendor": "Tech Solutions Inc",
    "amount": 800,
    "currency": "USD",
    "invoice_number": "TS-2026-001"
  },
  "execution_info": {
    "mcp_server": "browser_mcp",
    "execution_time_ms": 45200,
    "attempts": 1,
    "status": "success",
    "result": {
      "message_id": "PAY-20260114-12345",
      "external_id": "payment_12345",
      "confirmation_url": "https://techsolutions.example.com/payments/confirm/12345",
      "confirmation_screenshot": "saved_to_done_folder"
    }
  },
  "compliance": {
    "external_action": true,
    "approved": true,
    "financial_transaction": true,
    "audit_required": true,
    "pci_compliant": true,
    "retention_days": 2555
  },
  "audit_chain": {
    "created_event_id": "evt_001",
    "approved_event_id": "evt_002"
  }
}
```

---

## Generating Reports from Audit Logs

### Query: All approved actions today

```bash
grep '"event_type": "action_approved"' logs/audit.log | grep '2026-01-14' | wc -l
```

Output: `24 approved actions today`

### Query: Payment transactions this week

```bash
grep '"action_type": "payment"' logs/audit.log | grep -E '2026-01-0[8-14]' | \
  grep '"event_type": "action_executed"'
```

Shows all executed payments with approval info and results.

### Query: Failed actions needing retry

```bash
grep '"event_type": "action_failed"' logs/audit.log | \
  grep '"will_retry": true'
```

Shows actions that will be automatically retried.

### Query: Policy violations

```bash
grep '"policy_violations"' logs/audit.log | grep -v '\[\]'
```

Shows all actions that violated policies (non-empty violations array).

### Query: Approval timeline

```bash
grep '"approved_by": "jane_doe"' logs/audit.log | \
  jq '.approval_duration_seconds' | \
  awk '{sum+=$1; n++} END {print "Average approval time: " sum/n " seconds"}'
```

Output: `Average approval time: 245.3 seconds`

---

## Compliance Report Example

```markdown
# Monthly Compliance Report - January 2026

## Executive Summary
- **Total Actions**: 247
- **Approval Rate**: 99.2% (244/247)
- **Execution Success Rate**: 98.4% (240/244)
- **Policy Violations Detected**: 2
- **Audit Status**: ✅ FULLY COMPLIANT

## Action Classification

| Category | Count | Approved | Executed | Success |
|----------|-------|----------|----------|---------|
| Emails   | 145   | 145      | 143      | 98.6%   |
| Posts    | 32    | 32       | 32       | 100%    |
| Payments | 18    | 18       | 18       | 100%    |
| Forms    | 42    | 42       | 42       | 100%    |
| Other    | 10    | 7        | 7        | 100%    |

## Approval Workflow
- **Average Approval Time**: 3.2 minutes
- **Fastest**: 0.5 minutes (routine email)
- **Slowest**: 47.3 minutes (large commitment)
- **Rejections**: 2 (policy violations)
- **Needs Info**: 1 (required clarification)

## External Actions
- **Total External**: 167 (67.6%)
- **Approved Before Execution**: 167 (100%)
- **No Unauthorized External Actions**: ✅

## Financial Transactions
- **Total Payments**: $12,450
- **Transactions**: 18
- **All Approved**: ✅
- **All Executed Successfully**: ✅
- **PCI Compliance**: ✅

## Data Security
- **Credentials Sanitized**: 247/247 (100%)
- **PII Redacted**: 98/98 instances
- **Payment Data Protected**: 18/18 transactions
- **Token Redactions**: 156/156 instances

## Audit Trail Integrity
- **Log Files**: Immutable ✅
- **Timestamps**: Accurate (UTC) ✅
- **Chain of Custody**: Complete ✅
- **No Gaps**: Verified ✅

## Recommendations
1. Continue current approval workflow (highly effective)
2. Review 2 policy violations to prevent recurrence
3. Consider automated approval for routine low-risk actions
4. Archive 60-day-old logs to separate retention system

---
```
