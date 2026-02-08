---
action_id: test-email-001
action_type: send_email
created: '2026-01-24T16:39:35.056000'
risk_factors:
- External email
- Test recipient
risk_level: medium
status: pending
type: approval_request
---

# Approval Request: test-email-001

## Action Classification
- **Action Type**: send_email
- **Risk Level**: MEDIUM
- **Status**: pending

## Risk Assessment

### Risk Factors
- External email
- Test recipient

### Impact Analysis
Test email to verify system functionality

### Blast Radius
Single test recipient, no business impact

## Approval Criteria Checklist

☐ Recipient verified
☐ Content reviewed

## Draft Content

```
Subject: Test Email

This is a test email.
```

## Execution Plan

```yaml
mcp_server: email
tool_name: send_email
tool_inputs:
  to: test@example.com
  subject: Test Email
  body: This is a test email.
retry_policy:
  max_retries: 3
  backoff_seconds:
  - 1
  - 2
  - 4

```

---

## Approval Instructions

**To Approve**: Move this file to `/Approved/` folder
**To Reject**: Move this file to `/Rejected/` folder and add rejection reason in a `## Rejection Reason` section

**Created**: 2026-01-24 16:39:35