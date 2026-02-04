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

# Approval Workflow Manager (Human-in-the-Loop)

Manage human approval for sensitive or external-facing AI actions. Route decisions through Obsidian vault using `/Pending_Approval/` folder with structured approval requests.

## Architecture Note: Integration with Orchestrator.py

**IMPORTANT**: This skill creates the approval requests that feed into the **Orchestrator.py (Master Process)** for execution.

**Workflow Integration**:
1. **This skill** (approval-workflow-manager): Detects external/sensitive actions and creates approval requests in `/Pending_Approval/`
2. **Human**: Reviews and moves approved items to `/Approved/` folder
3. **Orchestrator.py** (implemented as `run_executor.py` in mcp-executor skill): Watches `/Approved/` folder and executes actions via MCP servers
4. **Audit Logger**: Records all approval decisions and execution results

**Key Components**:
- `needs-action-triage` skill → Processes items from `/Needs_Action/`, determines if approval needed
- `approval-workflow-manager` skill (THIS) → Creates approval requests in `/Pending_Approval/`
- Human decision → Moves to `/Approved/` or `/Rejected/`
- `mcp-executor` skill (orchestrator.py) → Executes approved actions
- `audit-logger` skill → Logs all decisions and actions

**Per HACKATHON-ZERO.md**:
- Line 495: "The Orchestrator watches the /Approved folder and triggers the actual MCP action"
- Line 666-667: "A master Python Orchestrator.py that handles the timing and folder watching"
- This skill implements the HITL (Human-in-the-Loop) approval layer before orchestrator execution

## Quick Start

### Setting Up Approval Workflow

1. Extend `Company_Handbook.md` with approval rules (see `references/approval-rules.md`)
2. Define which actions require human approval (external communications, payments, policy violations)
3. Create approval request template in Company_Handbook.md
4. Watchers and action processors will automatically route flagged items to `/Pending_Approval/`

### Checking Pending Approvals

View all items awaiting approval:

```bash
# List pending approvals
ls -la My_AI_Employee/AI_Employee_Vault/Pending_Approval/

# Or use the approval checker script
python scripts/check_approvals.py
```

Each pending item shows:
- What action is requested
- Why it needs approval (e.g., payment > $500, external communication, policy boundary)
- Required fields for approval decision
- Recommendation (approve/reject/modify)

### Approving an Action

Approve an action by editing the markdown file:

```markdown
---
status: approved
approved_by: [your name]
approved_at: 2026-01-14T14:30:00Z
---

# Approval Decision

## Action
Send email to client@example.com about project proposal

## Approval
✅ **APPROVED** - Matches company brand guidelines

## Notes
- Email tone is professional
- Proposal terms are reasonable
- Ready to send

---
```

Move approved item to `/Approved/` folder:

```bash
mv My_AI_Employee/AI_Employee_Vault/Pending_Approval/item.md \
   My_AI_Employee/AI_Employee_Vault/Approved/item.md
```

### Rejecting an Action

Reject an action with explanation:

```markdown
---
status: rejected
rejected_by: [your name]
rejected_at: 2026-01-14T14:30:00Z
---

# Rejection Decision

## Action
Transfer $5,000 to vendor account

## Rejection Reason
❌ **REJECTED** - Needs additional documentation

## Notes
- Vendor invoice not attached
- Please ask for invoice before approving transfer
- Once received, resubmit for approval

---
```

Move rejected item to `/Rejected/` folder for record-keeping.

## Workflow Structure

### Folder Organization

```
My_AI_Employee/AI_Employee_Vault/
├── Needs_Action/          # New items from watchers (unprocessed)
├── Pending_Approval/      # Items awaiting human decision
├── Approved/              # Approved items ready for execution
├── Rejected/              # Rejected items (archive)
└── Done/                  # Completed/executed items
```

### Action Item Lifecycle

1. **Watcher/Processor** → Creates item in `/Needs_Action/`
2. **Classifier** → Checks if approval needed
   - If YES: Move to `/Pending_Approval/` with approval request format
   - If NO: Move to `/Approved/` for immediate execution
3. **Human** → Reviews and updates status in `/Pending_Approval/`
4. **Executor** → Processes approved items from `/Approved/`
5. **Archiver** → Moves completed items to `/Done/`

## Approval Request Format

### Frontmatter (YAML)

```yaml
---
type: approval_request
source: whatsapp|gmail|linkedin|filesystem
action_type: send_email|send_message|create_post|payment|system_change
requires_approval: true
approved: false
status: pending|approved|rejected
priority: high|medium|low
created_at: 2026-01-14T14:30:00Z
approved_by: null
approved_at: null
approval_reason: null
---
```

### Body Structure

```markdown
# Action Request: [Brief Description]

**Source**: WhatsApp from Client A
**Type**: Send email to external contact
**Priority**: HIGH
**Created**: 2026-01-14 14:30:00

## The Requested Action

Clearly state what the AI wants to do:
- Send email to: client@example.com
- Subject: Project Update
- Body: [Full email text]

## Why Approval is Needed

Explain why this action requires human decision:
- External communication to client
- Commits to delivery timeline
- Impacts business relationship

## Approval Rules Applied

List rules from Company_Handbook.md that triggered approval:
- External communications require human review
- Commitments > 1 day require approval
- Client-facing emails need tone review

## Company_Handbook.md Context

Relevant rules that apply:
- "Always be professional with clients"
- "Confirm delivery dates with management first"
- "Follow brand voice guidelines"

## Recommendation

AI's recommendation (not binding):
✅ **APPROVE** - Meets all company guidelines

## Decision Required

Human must fill in:
- [ ] Approved or Rejected
- [ ] Approval notes (why you agree/disagree)
- [ ] Any modifications needed

---
```

## Configuration: Company_Handbook.md

See `references/approval-rules.md` for complete approval configuration including:
- Which actions require approval
- Who can approve (should default to user)
- Approval timeout (how long before escalation)
- Fallback rules (what happens if no response)

## Scripts

**Check pending approvals:**
```bash
python scripts/check_approvals.py
```

**Auto-archive old approvals:**
```bash
python scripts/archive_approvals.py --older-than 30
```

**Generate approval report:**
```bash
python scripts/approval_report.py
```

## Integration with Other Skills

### Multi-Watcher-Runner
- Watchers create action items in `/Needs_Action/`
- Approval workflow routes external/sensitive items to `/Pending_Approval/`
- Other items go directly to `/Approved/` for execution

### MCP-Executor
- Processes items from `/Approved/` folder
- Executes approved actions via MCP servers
- Moves completed items to `/Done/` with execution results

### Audit-Logger
- Records all approval decisions
- Logs who approved/rejected and when
- Maintains audit trail of actions

## Reference Files

- `references/approval-rules.md` - Configure which actions require approval
- `references/approval-patterns.md` - Common approval workflows and examples
- `references/hitl-best-practices.md` - Human-in-the-loop workflow design patterns
