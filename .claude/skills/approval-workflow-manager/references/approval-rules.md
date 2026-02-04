# Approval Rules Configuration

Add to `My_AI_Employee/AI_Employee_Vault/Company_Handbook.md`:

## Approval Workflow Rules

### Actions Requiring Approval

#### Always Require Approval
- **External Communications**: Any email, message, or post to outside contacts
- **Financial Transactions**: Any payment, transfer, or money movement
- **Policy Changes**: Modifications to company rules or processes
- **System Changes**: Account changes, integrations, or infrastructure modifications
- **Commitments**: Promises to deliver, meet deadlines, or take on obligations

#### Conditional Approval
- **Payments > $500**: High-value transactions need human verification
- **LinkedIn Posts**: Public posts that represent the business
- **Client Meetings**: Scheduling with new or important contacts
- **Contract Modifications**: Any changes to agreed terms

#### Auto-Approved (No Human Review)
- **Internal Notes**: Items only in personal/internal systems
- **Reminders**: Recurring calendar events, task creation
- **Email Drafts**: Draft emails that won't be auto-sent

### Approval Configuration

```yaml
approval_rules:
  external_communication:
    enabled: true
    requires_approval: true
    timeout_hours: 2
    escalate_after: 24
    message: "External communication requires approval"

  payments:
    enabled: true
    requires_approval: true
    threshold: 500  # Approval required if > $500
    timeout_hours: 1
    escalate_after: 4
    message: "Payment requests need human verification"

  linkedin_posts:
    enabled: true
    requires_approval: true
    timeout_hours: 1
    escalate_after: 8
    message: "Public posts require brand review"

  client_commitments:
    enabled: true
    requires_approval: true
    timeout_hours: 2
    escalate_after: 24
    message: "Business commitments need approval"
```

### Priority Indicators

Approval workflow uses these priority indicators to queue requests:

```markdown
## Priority Levels

**🔴 CRITICAL (P0)**: Requires immediate approval
- Urgent payment required
- Critical client communication
- System failure/outage
- Policy violation detected
- Timeout: 15 minutes before escalation

**🟠 HIGH (P1)**: Needs approval within 2 hours
- Important client meetings
- Significant financial transactions ($500+)
- Public posts or announcements
- Contractual commitments
- Timeout: 2 hours before escalation

**🟡 MEDIUM (P2)**: Standard approval needed within 4 hours
- External emails
- LinkedIn posts
- Meeting scheduling
- Standard payments
- Timeout: 4 hours before escalation

**🟢 LOW (P3)**: Informational, can auto-approve after 8 hours
- Internal notes or reminders
- Routine follow-ups
- Status updates
- Timeout: 8 hours then auto-approve
```

### Approval Timeout & Escalation

If approval not provided within timeout period:

```markdown
## Escalation Strategy

1. **Timeout Notification** (at timeout - 15 minutes)
   - Reminder sent to user
   - Item marked as "URGENT - PENDING"
   - Dashboard highlights in red

2. **Escalation** (at timeout + 15 minutes)
   - Item auto-moves to "/Escalated/" folder
   - Creates escalation record
   - For critical items: may auto-approve as safe fallback

3. **Auto-Approval Fallback** (for low-risk items only)
   - LOW priority items auto-approve after timeout
   - Creates audit log entry: "Auto-approved due to timeout"
   - Notifications sent so you're aware

4. **Manual Override**
   - You can approve/reject at any time
   - Even after auto-approval, can modify decision
   - Audit trail preserves both decisions
```

### Custom Approval Rules

Add organization-specific rules to Company_Handbook.md:

```markdown
## Custom Approval Rules

### Client-Specific Rules
- **Client A (Prime Contact)**:
  - Emails require approval
  - Commitments > 1 day need approval
  - Faster timeout: 1 hour

- **Client B (Prime Contact)**:
  - All communications require approval
  - Timeout: 2 hours

### Tone/Voice Requirements
- All external emails checked against brand voice
- LinkedIn posts should be professional/business-focused
- WhatsApp should be friendly but professional

### Financial Rules
- Payments < $100: Auto-approved
- Payments $100-$500: Approval required if after 6pm
- Payments > $500: Always requires approval
```

## Implementing Approval Rules

### 1. Configure Watchers

Tell watchers which items need approval. Update watcher sections:

```markdown
### Gmail Approval Rules

Items requiring approval:
- All replies to external emails
- All new outgoing emails (not drafts)
- Emails with attachments going to external contacts

Items NOT requiring approval:
- Drafts (not sent)
- Internal-only emails
- Forwarding existing messages
```

### 2. Configure Action Processors

When processing action items, check approval requirements:

```python
# In action processor logic
approval_required = check_approval_rules(action_item)
if approval_required:
    move_to_pending_approval(action_item)
else:
    move_to_approved(action_item)
```

### 3. Configure Approval Checker

Script that enforces approval rules and timeouts:

```bash
python scripts/check_approvals.py --enforce-timeouts
```

## Approval Decision Template

When you receive an approval request, use this structure:

```markdown
---
status: approved
approved_by: [Your Name]
approved_at: 2026-01-14T14:30:00Z
decision_time_minutes: 5
---

# Approval Decision

## Action Summary
[Copy the requested action here]

## Your Decision
✅ **APPROVED** (or ❌ **REJECTED** or 🔄 **NEEDS MODIFICATION**)

## Reasoning
Why you approve/reject:
- Matches brand guidelines
- Appropriate commitment level
- Professional communication

## Modifications (if needed)
If changes needed:
- Modify email tone: "softer" or "more professional"
- Reduce commit ment scope
- Add more details

## Notes
Additional context for AI:
- Client prefers email over WhatsApp
- Make sure to follow up next week
- Ask for invoice before sending payment

---
```

## Monitoring Approvals

### Check Pending Approvals
```bash
python scripts/check_approvals.py
```

Output shows:
- Number pending
- Average wait time
- Items nearing timeout
- Recommended actions

### Generate Report
```bash
python scripts/approval_report.py --period month
```

Shows:
- Approval rate
- Average approval time
- Most common rejection reasons
- Bottleneck analysis

### Archive Old Approvals
```bash
python scripts/archive_approvals.py --older-than 30
```

Moves old approved/rejected items to archive after 30 days.
