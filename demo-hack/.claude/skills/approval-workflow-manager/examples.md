# Approval Workflow Examples

## Example 1: Email Approval Request

### Pending Approval Item

**File**: `Pending_Approval/20260114_143000_email_to_client.md`

```markdown
---
type: approval_request
source: gmail
action_type: send_email
requires_approval: true
status: pending
priority: high
created_at: 2026-01-14T14:30:00Z
---

# Approval Request: Email to Client

**Source**: Gmail processing system
**Type**: Send email to external contact
**Priority**: HIGH
**Created**: 2026-01-14 14:30:00

## The Requested Action

Send email to: client@example.com
Subject: Project Update & Next Steps

Body:
```
Hi Sarah,

Following up on our conversation last week regarding the project timeline.

I wanted to confirm that we can deliver the first phase by end of month as discussed. I've coordinated with the team and we're confident in this timeline.

Here's what to expect:
1. Phase 1 delivery: January 31, 2026
2. Phase 2 starts: February 3, 2026
3. Final review: February 28, 2026

Could you confirm this works on your end? Happy to adjust if needed.

Best regards,
[AI Employee]
```

## Why Approval is Needed

- External communication to client
- Makes commitment to delivery date
- Impacts business relationship
- Needs tone and timeline verification

## Approval Rules Applied

- "External communications require human review"
- "Commitments > 1 day require approval"
- "Follow professional email tone"

## Company_Handbook Context

**Relevant Rules:**
- "Always maintain professional tone with clients"
- "Confirm aggressive timelines with team first"
- "No commitments past end of quarter without explicit approval"

## Recommendation

AI recommends: ✅ **APPROVE**
- Tone is professional
- Timeline was pre-agreed
- Ready to send

## Your Decision

Modify the email status below:

```
Decision: [APPROVE / REJECT / NEEDS_CHANGE]
Notes:
```

---
```

### You Approve

**Action**: Edit file and move to Approved folder

```markdown
---
type: approval_request
source: gmail
action_type: send_email
requires_approval: true
status: approved
priority: high
created_at: 2026-01-14T14:30:00Z
approved_by: Jane Doe
approved_at: 2026-01-14T14:35:00Z
---

# Approval Request: Email to Client

[... same content ...]

## Your Decision

✅ **APPROVED**

**Reasoning**: Email tone is professional and timeline was confirmed in our meeting. Good to send.

**Notes**: Follow up with Sarah on Feb 28 to ensure delivery on track.

---
```

Then move to approved folder:
```bash
mv Pending_Approval/20260114_143000_email_to_client.md Approved/
```

### MCP Executor Processes It

The mcp-executor skill:
1. Sees item in `/Approved/` folder
2. Reads approval decision
3. Extracts email details
4. Calls email MCP server to send
5. Moves item to `/Done/` with result

---

## Example 2: Payment Approval Request

### Pending Approval Item

**File**: `Pending_Approval/20260114_160000_payment_request.md`

```markdown
---
type: approval_request
source: filesystem
action_type: payment
requires_approval: true
status: pending
priority: high
created_at: 2026-01-14T16:00:00Z
---

# Approval Request: Payment to Vendor

**Source**: Email from vendor with invoice
**Type**: Financial transaction (payment)
**Priority**: HIGH ($800 > $500 threshold)
**Created**: 2026-01-14 16:00:00

## The Requested Action

**Payment Details:**
- Recipient: Tech Solutions Inc.
- Amount: $800 USD
- Description: Development services for Jan 2026
- Invoice #: TS-2026-001

## Why Approval is Needed

- Amount exceeds $500 threshold
- Financial transaction (critical for accuracy)
- Needs invoice verification
- Need to confirm budget

## Approval Rules Applied

- "Payments > $500 require human verification"
- "All financial transactions need approval"

## Company_Handbook Context

**Financial Rules:**
- Verify invoice matches services rendered
- Check that vendor is on approved vendor list
- Confirm budget category
- Keep receipt for accounting

## Recommendation

AI recommends: ✅ **APPROVE**
- Invoice matches requested services
- Vendor is on approved list
- Budget available in Dev category

## Your Decision

[CHECK INVOICE / APPROVE / REJECT]

---
```

### You Request More Information

```markdown
---
type: approval_request
source: filesystem
action_type: payment
requires_approval: true
status: needs_info
priority: high
created_at: 2026-01-14T16:00:00Z
needs_info_from: user
info_requested:
  - invoice_copy
  - services_verification
---

# Approval Request: Payment to Vendor

[... same content ...]

## Your Decision

🔄 **NEEDS MORE INFORMATION**

**Questions:**
1. Can you attach the actual invoice PDF?
2. Did they complete all the work on the scope?
3. Is this the final payment or partial?

**Status**: Waiting for your response
**Resend by**: 2026-01-14 16:30:00

---
```

User provides information, then you approve:

```markdown
---
status: approved
approved_by: Jane Doe
approved_at: 2026-01-14T16:25:00Z
---

# Approval Decision

[... original content ...]

## Your Decision

✅ **APPROVED**

**Verification Done:**
- Invoice PDF matches request
- All development work completed
- Services match invoice scope
- This is final payment

**Notes**: Payment approved. Process immediately.

---
```

---

## Example 3: LinkedIn Post Approval Request

### Pending Approval Item

**File**: `Pending_Approval/20260114_100000_linkedin_post.md`

```markdown
---
type: approval_request
source: linkedin
action_type: create_post
requires_approval: true
status: pending
priority: medium
created_at: 2026-01-14T10:00:00Z
---

# Approval Request: LinkedIn Post

**Source**: LinkedIn watcher
**Type**: Public post (represents business)
**Priority**: MEDIUM
**Created**: 2026-01-14 10:00:00

## The Requested Action

**Post Text:**
```
Just shipped a new automation feature that saves our clients 5+ hours per week!

The journey from idea to production took 6 weeks, and here's what we learned:

1. Start with customer pain point (not cool tech)
2. Simple MVP wins over perfect features
3. Real feedback matters more than assumptions

If you're building automation, what's your #1 biggest challenge? Would love to hear.

#automation #productmanagement #startups
```

## Why Approval is Needed

- Public post (represents business brand)
- LinkedIn is professional audience
- Need tone/voice verification

## Approval Rules Applied

- "LinkedIn posts require brand review"
- "Public posts need human approval"

## Company_Handbook Context

**Brand Voice:**
- Professional but approachable
- Focus on business value
- Share learnings and lessons
- Encourage community engagement

## Recommendation

AI recommends: ✅ **APPROVE**
- Matches brand voice
- Adds value to audience
- Engagement opportunity

---
```

### You Make Minor Edit and Approve

```markdown
---
status: approved
approved_by: Jane Doe
approved_at: 2026-01-14T10:10:00Z
modifications_made: title_softened
---

# Approval Decision

## Original Text
[... original ...]

## Modified Text
```
Just launched a new automation feature that helps clients save 5+ hours per week!

Building this taught us a lot. Here's what we learned:
...
```

## Changes Made
- Softer language: "launched" vs "shipped" (more formal)
- Better for professional audience

## Decision
✅ **APPROVED with modifications**

Ready to post!

---
```

---

## Example 4: Rejection - Policy Violation

### Pending Approval Item

```markdown
---
type: approval_request
source: whatsapp
action_type: send_message
requires_approval: true
status: pending
priority: high
created_at: 2026-01-14T14:00:00Z
---

# Approval Request: WhatsApp to Client

**Source**: WhatsApp watcher
**Type**: Send message
**Priority**: HIGH
**Created**: 2026-01-14 14:00:00

## The Requested Action

Send to: Client B (WhatsApp)

Message:
```
Hi! Quick note - our CEO just told me he's moving the project deadline up 2 weeks to help your cash flow situation. We can deliver by Feb 15 instead of March 1. Let me know if this works!
```

[... approval rules and context ...]

---
```

### You Reject - Not Authorized to Commit

```markdown
---
status: rejected
rejected_by: Jane Doe
rejected_at: 2026-01-14T14:05:00Z
rejection_reason: unauthorized_commitment
---

# Rejection Decision

## Requested Action
Send WhatsApp message committing to Feb 15 deadline

## Decision
❌ **REJECTED** - Unauthorized commitment

## Reasoning

This violates our approval rules:
- **Rule Violated**: "No commitments without explicit approval"
- **Issue**: You cannot commit to new deadlines on behalf of CEO
- **Risk**: Creates expectation CEO didn't authorize

## What to Do Instead

1. First: Get explicit approval from CEO on new deadline
2. Then: Resubmit with CEO approval attached
3. Send message once approved

## Follow-up Actions
- Contact CEO to confirm Feb 15 deadline is acceptable
- Get written approval
- Resubmit for approval
- Then send message

---
```

---

## Typical Approval Workflow

```
1. Watcher creates action item
   ↓
2. Item moved to /Needs_Action/
   ↓
3. Approval checker reviews
   ↓
4. Requires approval? YES → Move to /Pending_Approval/
                     NO  → Move to /Approved/
   ↓
5. [If pending] Human reviews and decides
   ↓
6. Approved? YES → Move to /Approved/
             NO  → Move to /Rejected/ with notes
   ↓
7. MCP Executor processes /Approved/ items
   ↓
8. Executes action or marks failed
   ↓
9. Result → Move to /Done/
```

## Checking Your Approvals

Monitor pending approvals:

```bash
# See what's pending
python scripts/check_approvals.py

# See approval history
python scripts/approval_report.py --period week
```

Dashboard shows:
- Items waiting for you
- How long each has been pending
- Priority indicators
- Time until escalation
