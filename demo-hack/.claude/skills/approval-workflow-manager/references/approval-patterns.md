# Common Approval Workflow Patterns

## Pattern 1: Simple External Email

**When to use**: Standard client communication

**Flow**:
1. Email detected as external in Gmail
2. Routed to `/Pending_Approval/` with approval template
3. Human reviews tone and content (2 min)
4. Approved → Moved to `/Approved/`
5. MCP executor sends via email
6. Result logged in audit trail

**Approval decision template**:
```markdown
✅ **APPROVED**

Verified:
- [ ] Tone matches brand voice
- [ ] Information is accurate
- [ ] No sensitive data exposed
- [ ] Professional formatting

Ready to send.
```

---

## Pattern 2: Financial Transaction with Verification

**When to use**: Payments, transfers, money movement

**Flow**:
1. Payment action created (amount, recipient, invoice)
2. Routed to `/Pending_Approval/` for HIGH priority review
3. Human verification (5-10 min):
   - Is recipient legitimate?
   - Does invoice match services?
   - Is budget available?
   - Any red flags?
4. Approved → `/Approved/` with verified status
5. MCP executor processes payment
6. Receipt saved and logged

**Verification checklist**:
```markdown
🔍 **PAYMENT VERIFICATION**

Vendor Check:
- [ ] Vendor on approved list
- [ ] Invoice number matches
- [ ] Amount matches invoice
- [ ] Services already delivered

Budget Check:
- [ ] Budget category available
- [ ] No unusual vendor
- [ ] Payment terms match agreement

Red Flags:
- [ ] Requesting wire to new account? ⚠️
- [ ] Price significantly different? ⚠️
- [ ] Urgent payment request? ⚠️

Decision: ✅ APPROVE
```

---

## Pattern 3: Public Post with Brand Review

**When to use**: LinkedIn posts, public announcements, social media

**Flow**:
1. AI drafts post (tone, message, hashtags)
2. Routed to `/Pending_Approval/` for brand review
3. Human checks (3-5 min):
   - Does post represent brand well?
   - Tone appropriate for audience?
   - Any controversial statements?
   - Hashtags relevant?
4. Approved (optionally with minor edits) → `/Approved/`
5. MCP executor posts to platform
6. Posted content archived

**Brand review template**:
```markdown
🎯 **BRAND REVIEW**

Content Check:
- [ ] Matches brand voice
- [ ] Value to audience
- [ ] Professional tone
- [ ] No typos or grammar issues

Audience Check:
- [ ] Appropriate for LinkedIn?
- [ ] Will it generate good engagement?
- [ ] Any controversial elements?

Hashtags:
- [ ] Relevant to content
- [ ] Not overused
- [ ] Trending value

Decision: ✅ APPROVE
Optional edits: [none]
```

---

## Pattern 4: Commitment with Timeline

**When to use**: Promises to deliver, meet deadlines, or take on obligations

**Flow**:
1. AI drafts communication with commitment
2. Routed to `/Pending_Approval/` for commitment review
3. Human verifies (5-10 min):
   - Can we actually meet this deadline?
   - Is team available?
   - Any resource conflicts?
   - Is commitment realistic?
4. Approved (or modified with realistic timeline) → `/Approved/`
5. MCP executor sends commitment
6. Calendar event created automatically

**Commitment verification**:
```markdown
⏰ **COMMITMENT VERIFICATION**

Proposed Commitment:
- Deliver Phase 1 by: January 31, 2026
- Start Phase 2 by: February 3, 2026

Feasibility Check:
- [ ] Team confirmed availability
- [ ] No resource conflicts
- [ ] Dependencies tracked
- [ ] Buffer time included?

Risk Assessment:
- High risk: 0
- Medium risk: 0
- Low risk: 0

Decision: ✅ APPROVE (or suggest new date)
```

---

## Pattern 5: Request for More Information

**When to use**: When human needs clarification before approving

**Flow**:
1. Approval request created
2. Human identifies missing info
3. Marks as "NEEDS_INFO" with questions
4. AI system reruns analysis with additional context
5. Resubmits with more info
6. Human can then approve/reject

**Request more info template**:
```markdown
❓ **NEED MORE INFORMATION**

I can't decide on this yet because:
- [ ] Missing invoice PDF
- [ ] Unclear pricing breakdown
- [ ] No confirmation from team

Please provide:
1. Actual invoice file (PDF)
2. Breakdown of costs
3. Email confirmation from manager

Resend when ready: [date/time]
```

---

## Pattern 6: Modification Before Approval

**When to use**: Content/commitment needs adjustment before approval

**Flow**:
1. Approval request reviewed
2. Human identifies changes needed
3. Marks as "NEEDS_MODIFICATION" with specific changes
4. AI system modifies the action
5. Resubmits for approval
6. Human verifies changes and approves

**Request modifications template**:
```markdown
🔄 **NEEDS MODIFICATION**

I approve the general direction but need changes:

**Change 1: Tone softening**
- Current: "We will deliver..."
- Revised: "We can deliver..."
- Reason: Less aggressive for this client

**Change 2: Timeline adjustment**
- Current: "January 31"
- Revised: "Early February"
- Reason: More realistic with current load

Please modify and resubmit.
```

---

## Pattern 7: Timeout & Escalation

**When to use**: Human doesn't respond within approval timeout

**Flow**:
1. Approval request created with timeout (e.g., 2 hours)
2. At timeout - 15 min: Reminder notification
3. At timeout + 15 min: Item escalated to `/Escalated/` folder
4. Escalation decision:
   - **Auto-approve** for low-risk items
   - **Hold** for high-risk items (requires manual approval)
   - **Reject** if policy requires it

**Timeout rules in Company_Handbook.md**:
```markdown
## Approval Timeout & Escalation

### LOW Priority (P3)
- Timeout: 8 hours
- Escalation action: Auto-approve
- Rationale: Low risk, safe to proceed

### MEDIUM Priority (P2)
- Timeout: 4 hours
- Escalation action: Escalate (require manual)
- Rationale: Need human review

### HIGH Priority (P1)
- Timeout: 2 hours
- Escalation action: Escalate (require manual)
- Rationale: Important decisions

### CRITICAL Priority (P0)
- Timeout: 30 minutes
- Escalation action: Escalate (require manual)
- Rationale: Urgent and important
```

---

## Pattern 8: Rejection with Clear Explanation

**When to use**: Action violates policy, best practices, or budget

**Flow**:
1. Approval request reviewed
2. Human identifies violation or issue
3. Marks as "REJECTED" with detailed reason
4. Moved to `/Rejected/` for record-keeping
5. AI system gets feedback about why
6. System can improve future submissions

**Rejection template**:
```markdown
❌ **REJECTED**

**Reason**: Violates policy

**Policy Violated**:
- "No external commitments without manager approval"

**What happened**:
- You committed to deliver by Jan 31
- Need manager sign-off first

**What to do**:
1. Get manager approval for Jan 31 deadline
2. Resubmit with approval attached
3. Then send commitment to client

**Next steps**: [Contact manager today]
```

---

## Pattern 9: Audit Trail & Decision Documentation

**When to use**: Recording all approval decisions for compliance

**Frontmatter preserved**:
```yaml
---
type: approval_request
source: gmail
action_type: send_email
status: approved
created_at: 2026-01-14T10:00:00Z
approved_by: Jane Doe
approved_at: 2026-01-14T10:05:00Z
approval_duration_minutes: 5
decision_reasoning: >
  Email tone matches brand guidelines,
  content is accurate, ready to send
audit_log:
  - timestamp: 2026-01-14T10:00:00Z
    event: created
    creator: whatsapp_watcher
  - timestamp: 2026-01-14T10:02:00Z
    event: routed_to_approval
    reason: external_communication
  - timestamp: 2026-01-14T10:05:00Z
    event: approved
    approver: Jane Doe
    reasoning: brand_compliant
  - timestamp: 2026-01-14T10:10:00Z
    event: executed
    executor: mcp_email_server
    result: success
---
```

---

## Pattern 10: Recurring Approvals

**When to use**: Same type of action needs regular approval (e.g., monthly reports, weekly meetings)

**Setup in Company_Handbook.md**:
```markdown
## Recurring Approvals

### Weekly Status Report
- Frequency: Every Friday at 5pm
- Approval required: Yes
- Timeout: 30 minutes
- Auto-action: Reject if not approved by 5:30pm
- Reason: Report must be sent same day

### Monthly Team Standup
- Frequency: First Monday of month
- Approval required: Yes
- Timeout: 2 hours
- Auto-action: Proceed if not approved (informational only)
- Reason: Team meeting is informational

### Vendor Payments
- Frequency: As needed
- Approval required: Yes (if > $500)
- Timeout: 4 hours
- Auto-action: Escalate if not approved
- Reason: Financial decision
```

**Recurring approval workflow**:
1. Recurring task triggered (e.g., Friday at 5pm)
2. Standard approval request created
3. Human reviews (should be familiar pattern)
4. Approved → executes
5. Rejected → holds until resolved
6. Next occurrence scheduled

---

## Implementation: Which Pattern to Use?

**Use Simple External Email** → Basic client communications, status updates
**Use Financial** → Any money movement or transaction
**Use Public Post** → LinkedIn, Twitter, public announcements
**Use Commitment** → Promises, deadlines, obligations
**Use Request Info** → When you need clarification
**Use Modification** → When close but needs tweaks
**Use Timeout/Escalation** → Automatic handling for busy times
**Use Rejection** → Policy violations or safety concerns
**Use Audit Trail** → Compliance and record-keeping
**Use Recurring** → Repeated actions with pattern

---
