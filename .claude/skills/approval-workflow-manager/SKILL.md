---
name: approval-workflow-manager
description: >
  Human-in-the-loop approval workflow for AI Employee actions. Detects external/sensitive actions
  from watchers and action item processing, routes them for human approval via Obsidian vault
  (/Pending_Approval folder), handles approvals/rejections, and manages execution state.
  Use when: (1) Processing new action items that require approval, (2) Updating approval request status,
  (3) Archiving approved/rejected decisions, (4) Checking pending approvals, (5) Configuring approval
  rules in Company_Handbook.md. Trigger phrases: "request approval", "pending approval", "approve action",
  "reject action", "check what needs approval", "approval workflow", "HITL approval".
---

# Approval Workflow Manager

Manages the human-in-the-loop (HITL) approval workflow for Silver Tier AI Employee external actions.

## Purpose

This skill orchestrates the approval process for all external actions requiring human oversight:
- **Email sending** (all recipients)
- **LinkedIn posting** (all posts)
- **WhatsApp messages** (all contacts)
- **Browser automation** (payments, forms, clicks)

## Workflow Overview

```
Action Item (Needs_Action/)
    ↓
[Triage detects external action]
    ↓
Create Approval Request (Pending_Approval/)
    ↓
Human Decision (file move)
    ├─→ Approved/ → Execution Queue
    └─→ Rejected/ → Archive with reason
```

## Scope

**This skill handles:**
- Creating approval requests with risk assessments
- Writing approval request files to `/Pending_Approval/` folder
- Monitoring for human decisions (file moves to `/Approved/` or `/Rejected/`)
- Updating Dashboard.md with approval status
- Enforcing permission boundaries from Company_Handbook.md

**This skill does NOT handle:**
- External action execution (handled by `@mcp-executor`)
- Action item triage (handled by `@needs-action-triage`)
- Audit logging (handled by `@audit-logger`)

## Integration Points

### Input Sources
1. **@needs-action-triage skill**: Calls this skill when triage determines action requires approval
2. **Manual invocation**: User asks to "check pending approvals" or "create approval request for [action-id]"

### Output Destinations
1. **Pending_Approval/ folder**: Approval requests awaiting human decision
2. **Approved/ folder**: Approved actions ready for execution
3. **Rejected/ folder**: Rejected actions with reasoning
4. **Dashboard.md**: Updated with approval metrics

### Dependent Skills
- **@obsidian-vault-ops**: For vault folder operations and file moves
- **@audit-logger**: For logging approval decisions (optional integration)

## Permission Boundaries

Read approval rules from `Company_Handbook.md`:

### Auto-Approve Actions (Section 6.3)
- Dashboard updates and vault operations
- Reading emails/messages (no sending)
- Internal triage and planning

### Require-Approval Actions (Section 6.4)
- **Sending emails to ANY recipient**
- **Publishing LinkedIn posts**
- **Sending WhatsApp messages**
- **All browser automation** (payments, form submissions, clicks)

### Exceptions (Section 6.5)
- Pre-approved contacts (if configured)
- Whitelisted keywords/patterns

Use the `permission_boundaries` module to parse these rules:

```python
from my_ai_employee.approval import parse_permission_boundaries, classify_action_risk

boundaries = parse_permission_boundaries()
requires_approval = boundaries.should_require_approval(action_type, context)
risk_level = classify_action_risk(action_type, boundaries, context)
```

## Risk Assessment

For each approval request, generate a comprehensive risk assessment:

### 1. Impact Analysis
- **Who is affected?** Recipient, audience size, stakeholders
- **What changes?** Data, reputation, relationships, finances
- **Reversibility?** Can this be undone or corrected?

### 2. Blast Radius
- **Low**: Internal-only, easily reversible (vault updates, reading data)
- **Medium**: External contact, recoverable (email to known contact)
- **High**: Public post, financial transaction, irreversible (LinkedIn post, payment)

### 3. Approval Criteria Checklist
Generate a checklist based on `Company_Handbook.md` approval criteria:

```markdown
- ☐ Recipient trust: Is the recipient a known, trusted contact?
- ☐ Content sensitivity: Does the message contain financial info, PII, or confidential data?
- ☐ Impact: What's the blast radius if this action fails or is misinterpreted?
- ☐ Reversibility: Can this action be easily undone or corrected?
```

Use ☐ for unchecked items (human will manually check them before approving).

## Draft Content Generation

For external actions, generate draft content for human review:

### Email Replies
```
Subject: Re: [Original Subject]

[Generated draft based on action item content and email thread context]

---
Assistant note: This draft requires review and approval before sending.
Verify recipient, tone, and content accuracy.
```

### LinkedIn Posts
```
[Generated post content]

---
Visibility: [Public/Connections/Private]
Hashtags: [Suggested hashtags based on content]

Assistant note: Review post for professional tone and brand alignment.
```

### WhatsApp Messages
```
[Generated message text]

---
Recipient: [Contact name/number]
Context: [Conversation summary or trigger]

Assistant note: Verify contact and message appropriateness.
```

## Execution Plan Generation

For each approval request, include a detailed MCP execution plan:

```yaml
execution_plan:
  mcp_server: email                # or linkedin, browser
  tool_name: send_email            # MCP tool to invoke
  tool_inputs:
    to: recipient@example.com
    subject: "Re: Original Subject"
    body: "[Draft content from above]"
    attachments: []
  retry_policy:
    max_retries: 3
    backoff_seconds: [1, 2, 4]
  timeout_seconds: 30
```

### MCP Server Mapping

| Action Type | MCP Server | Tool Name | Key Inputs |
|-------------|------------|-----------|------------|
| `send_email` | `email` | `send_email` | to, subject, body, attachments |
| `publish_linkedin_post` | `linkedin` | `publish_post` | content, visibility |
| `send_whatsapp_message` | `browser` | `send_whatsapp_message` | contact, message |
| `browser_automation` | `browser` | `fill_form`, `click_button` | selector, value |

## Workflow Steps

### 1. Create Approval Request

When `@needs-action-triage` detects an external action:

1. **Classify Action Type**: Determine action type (send_email, publish_linkedin_post, etc.)
2. **Assess Risk**: Calculate risk level (low/medium/high) using `classify_action_risk()`
3. **Generate Draft Content**: Create email body, post text, or message content
4. **Build Execution Plan**: Define MCP server, tool, and inputs
5. **Create Approval Request File**: Write to `/Pending_Approval/` using `write_approval_request_to_vault()`

```python
from my_ai_employee.approval import (
    create_approval_request,
    write_approval_request_to_vault,
    classify_action_risk,
    parse_permission_boundaries,
)

# Create approval request
approval_request = create_approval_request(
    action_id="20260123-email-abc123",
    action_type="send_email",
    risk_level=risk_level,
    risk_factors=["External email", "Contains financial data"],
    draft_content=email_draft,
    execution_plan={
        "mcp_server": "email",
        "tool_name": "send_email",
        "tool_inputs": {
            "to": "john@company.com",
            "subject": "Re: Q4 Report",
            "body": email_draft,
        },
        "retry_policy": {
            "max_retries": 3,
            "backoff_seconds": [1, 2, 4],
        },
    },
    impact_analysis="Sending quarterly financial report to external contact",
    blast_radius="Single recipient (john@company.com), professional context",
    approval_criteria_checklist=[
        "☐ Recipient trust: Known business contact ✓",
        "☐ Content sensitivity: Contains financial data ⚠️",
        "☐ Reversibility: Cannot undo ⚠️",
        "☐ Compliance: Verify data accuracy required ⚠️",
    ],
)

# Write to vault
approval_file_path = write_approval_request_to_vault(approval_request)
```

### 2. Monitor for Human Decisions

Periodically check `/Pending_Approval/` folder for file moves:

```python
import frontmatter
from pathlib import Path
from my_ai_employee.config import get_config
from my_ai_employee.approval import move_to_approved, move_to_rejected

config = get_config()
vault_path = config.vault_root

# Check Approved/ folder for newly approved requests
approved_dir = vault_path / "Approved"
for approved_file in approved_dir.glob("*-approved.md"):
    # Parse frontmatter
    with open(approved_file, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    action_id = post.metadata.get("action_id")
    # Trigger execution via @mcp-executor
    # Log approval via @audit-logger

# Check Rejected/ folder for newly rejected requests
rejected_dir = vault_path / "Rejected"
for rejected_file in rejected_dir.glob("*-rejected.md"):
    # Parse frontmatter
    with open(rejected_file, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    action_id = post.metadata.get("action_id")
    rejection_reason = post.metadata.get("rejection_reason", "No reason provided")
    # Log rejection via @audit-logger
    # Archive original action item to Done/
```

**Alternative (File-based signaling)**: Human moves file from `/Pending_Approval/` to `/Approved/` or `/Rejected/` manually in Obsidian.

### 3. Update Dashboard

After approval/rejection, update Dashboard.md:

```markdown
## Approval Activity

### Pending Approvals
- 2 actions awaiting approval in `/Pending_Approval/`

### Recent Decisions
- ✅ **Approved**: Email to john@company.com (Q4 Report) - 2026-01-23 14:30
- ❌ **Rejected**: LinkedIn post about product launch - 2026-01-23 13:15 (Reason: Premature announcement)
```

## File Structure

### Approval Request File (Pending_Approval/)

```markdown
---
type: approval_request
action_id: 20260123-email-abc123
action_type: send_email
created: 2026-01-23T14:00:00Z
status: pending
risk_level: high
risk_factors:
  - External email
  - Contains financial data
---

# Approval Request: 20260123-email-abc123

## Action Classification
- **Action Type**: send_email
- **Risk Level**: HIGH
- **Status**: pending

## Risk Assessment

### Risk Factors
- External email
- Contains financial data

### Impact Analysis
Sending quarterly financial report to external business contact (john@company.com).

### Blast Radius
Single recipient, professional context. Email cannot be unsent once delivered.

## Approval Criteria Checklist

- ☐ Recipient trust: Known business contact ✓
- ☐ Content sensitivity: Contains financial data ⚠️
- ☐ Reversibility: Cannot undo ⚠️
- ☐ Compliance: Verify data accuracy required ⚠️

## Draft Content

```
To: john@company.com
Subject: Re: Q4 2025 Report Request

Hi John,

Thank you for reaching out. I've attached our Q4 2025 report as requested.

Key highlights:
- Revenue: $X.XM
- Growth: X%
- Outlook: [Summary]

Please let me know if you need any clarification on the figures.

Best regards
```

## Execution Plan

```yaml
mcp_server: email
tool_name: send_email
tool_inputs:
  to: john@company.com
  subject: "Re: Q4 2025 Report Request"
  body: "[See draft above]"
  attachments: []
retry_policy:
  max_retries: 3
  backoff_seconds: [1, 2, 4]
timeout_seconds: 30
```

---

## Approval Instructions

**To Approve**: Move this file to `/Approved/` folder
**To Reject**: Move this file to `/Rejected/` folder and add rejection reason in a `## Rejection Reason` section

**Created**: 2026-01-23 14:00:00
```

## Error Handling

### Malformed Approval Requests
- **Issue**: Missing required fields (action_id, risk_level, draft_content, execution_plan)
- **Action**: Use `validate_approval_request()` before writing to vault
- **Fallback**: Log error to `/Logs/`, add warning to Dashboard.md, notify user

### Missing Action Item Reference
- **Issue**: Approval request references non-existent action item
- **Action**: Verify action item exists in `/Needs_Action/` or `/Done/` before creating approval request
- **Fallback**: Include action item path in approval request for traceability

### Human Decision Ambiguity
- **Issue**: File moved to unknown location or incomplete rejection reason
- **Action**: Check for files in `/Approved/` and `/Rejected/` only
- **Fallback**: If file disappears from `/Pending_Approval/` without appearing in expected locations, log warning

### Permission Boundary Conflicts
- **Issue**: Company_Handbook.md has conflicting rules (action in both auto-approve and require-approval)
- **Action**: Default to require-approval for safety
- **Fallback**: Log warning about conflicting rules, prompt user to clarify handbook

## Testing Checklist

### T054: Approval Request Creation
- [ ] Create approval request for email action
- [ ] Verify file written to `/Pending_Approval/` with correct frontmatter
- [ ] Verify risk assessment includes impact analysis, blast radius, checklist
- [ ] Verify draft content is human-readable and accurate
- [ ] Verify execution plan includes MCP server, tool, inputs, retry policy

### T055: Approval Decision Monitoring
- [ ] Move approval request from `/Pending_Approval/` to `/Approved/`
- [ ] Verify approval is detected and logged
- [ ] Verify Dashboard.md updated with approval
- [ ] Verify approved action is ready for execution (appears in queue)

### T056: Rejection Handling
- [ ] Move approval request from `/Pending_Approval/` to `/Rejected/`
- [ ] Add rejection reason to file
- [ ] Verify rejection is detected and logged
- [ ] Verify Dashboard.md updated with rejection
- [ ] Verify original action item archived to `/Done/` with rejection metadata

### T057: Permission Boundary Enforcement
- [ ] Verify auto-approve actions bypass approval (vault_update, create_plan)
- [ ] Verify require-approval actions create approval requests (send_email, publish_linkedin_post)
- [ ] Verify exceptions are applied (pre-approved contacts, if configured)
- [ ] Verify conflicting rules default to require-approval

## Resources

- **Code**: `src/my_ai_employee/approval/approval_request.py`
- **Code**: `src/my_ai_employee/approval/permission_boundaries.py`
- **Handbook**: `AI_Employee_Vault/Company_Handbook.md` (Section 6: Approval Thresholds)
- **Templates**: `.claude/skills/needs-action-triage/templates/PlanTemplate.md`
- **Related Skills**: `@needs-action-triage`, `@mcp-executor`, `@audit-logger`

---

## Usage Examples

### Example 1: Create Approval Request for Email

```python
from my_ai_employee.approval import (
    create_approval_request,
    write_approval_request_to_vault,
    validate_approval_request,
)

# Create approval request
request = create_approval_request(
    action_id="20260123-email-xyz",
    action_type="send_email",
    risk_level="medium",
    risk_factors=["External email"],
    draft_content="Subject: Re: Meeting Request\n\nHi Sarah, happy to meet...",
    execution_plan={
        "mcp_server": "email",
        "tool_name": "send_email",
        "tool_inputs": {"to": "sarah@company.com", "subject": "Re: Meeting Request", "body": "..."},
        "retry_policy": {"max_retries": 3, "backoff_seconds": [1, 2, 4]},
    },
    impact_analysis="Scheduling meeting with external contact",
    blast_radius="Single recipient, low business impact",
    approval_criteria_checklist=["☐ Recipient trust verified", "☐ Calendar availability checked"],
)

# Validate before writing
is_valid, errors = validate_approval_request(request)
if not is_valid:
    print(f"Validation errors: {errors}")
else:
    # Write to vault
    path = write_approval_request_to_vault(request)
    print(f"Approval request created: {path}")
```

### Example 2: Check Pending Approvals

```python
from pathlib import Path
from my_ai_employee.config import get_config
import frontmatter

config = get_config()
vault_path = config.vault_root
pending_dir = vault_path / "Pending_Approval"

pending_requests = []
for request_file in pending_dir.glob("*-approval.md"):
    with open(request_file, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

    pending_requests.append({
        "action_id": post.metadata.get("action_id"),
        "action_type": post.metadata.get("action_type"),
        "risk_level": post.metadata.get("risk_level"),
        "created": post.metadata.get("created"),
    })

print(f"Pending approvals: {len(pending_requests)}")
for req in pending_requests:
    print(f"  - {req['action_id']} ({req['action_type']}, {req['risk_level']} risk)")
```

### Example 3: Process Approved Action

```python
from my_ai_employee.approval import move_to_approved

# Human moved file to /Approved/ manually, now process it
request = ...  # Load from approved file
approved_path = move_to_approved(request, approved_by="user@example.com")
print(f"Action approved and ready for execution: {approved_path}")

# Next: @mcp-executor picks up approved action and executes
```
