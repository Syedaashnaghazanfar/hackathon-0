---
name: needs-action-triage
description: >
  Triage and plan items in an Obsidian vault's /Needs_Action folder for Hackathon Zero (Bronze tier).
  This skill should be used when the user asks to "process Needs_Action", "triage pending items",
  "create a plan for each item", "turn watcher output into tasks", "update the dashboard after new items",
  "summarize what needs attention", or when Claude detects new action-item markdown files created by a watcher.
  Trigger phrases include: "check /Needs_Action", "process action items", "create Plan.md", "prioritize these",
  "archive to Done", "apply Company_Handbook rules", "process tasks", "check pending tasks",
  "handle Needs_Action items", "complete my tasks", "check what needs to be done", "process pending tasks",
  "check Needs_Action folder", "complete task requests", "move finished work to Done folder",
  "update activity dashboard", or when the user mentions the Needs_Action folder, task processing,
  or wants to see completed work moved to Done.
---

# Needs Action Triage

Convert watcher-created inputs into clear next steps **inside the vault**.

**Bronze Tier Scope:**
- Read items in `Needs_Action/`
- Read rules from `Company_Handbook.md`
- Write plans/drafts back into the vault (`Plans/`)
- Update `Dashboard.md`
- Move processed inputs to `Done/`
- Do **not** perform external actions

**Silver Tier Scope (Expanded):**
- **Decision Layer**: Determine if the plan requires external actions (emails, posts, etc.).
- **HITL Routing**: Move items to `Pending_Approval/` if they require human sign-off.
- **Audit Logging**: Ensure actions are logged to `/Logs/` via the `@audit-logger` skill.
- **MCP Integration**: Create drafts that can be picked up by the `@mcp-executor`.

## Workflow (Bronze & Silver)

1. Locate vault root using `@obsidian-vault-ops` workflow.
2. Scan `Needs_Action/` for pending items.
3. For each item:
   - Read file and parse minimal frontmatter (type/received/status/priority).
   - Read `Company_Handbook.md` and apply processing + priority rules.
   - Produce a plan using `templates/PlanTemplate.md`.
   - **Decision Step (Silver)**:
     - If the plan requires an external action (Section 6.4 of Handbook), mark it as `requires_approval: true`.
     - Generate the approval request file in `Pending_Approval/` using `@approval-workflow-manager`.
   - If the item is missing required info, include a “Questions” section in the plan.
4. Update `Dashboard.md`:
   - Update counts and append a short recent-activity line per processed item.
5. Archive processed input:
   - Move the action item to `Done/` folder (Bronze) OR keep in `Pending_Approval/` (Silver).
   - Add `processed` metadata to frontmatter:
     - `processed: [ISO timestamp]`
     - `result: planned|pending_approval`
     - `related_plan: Plans/[plan-filename].md`
     - `status: completed` (if purely internal) or `pending` (if HITL required)
   - Mark all checkboxes in "Next Steps" section as completed `[x]` ONLY if no external action remains.
   - Remove the original from `Needs_Action/`

## Output rules

- Keep plans actionable: checkboxes + concrete next steps.
- Always link back to the original action item path.
- If the item is malformed, do not move it; instead add a dashboard warning and leave it in `Needs_Action/`.

## Resources

- Reference: `references/action-item-schema.md`
- Reference: `references/triage-rules.md`
- Examples: `examples.md`
- Templates: `templates/PlanTemplate.md`, `templates/ActionItemTemplate.md`

---

## Silver Tier Classification Logic

### Action Type Classification

When processing an action item, determine the **action type** based on content analysis:

**External Actions (Require Approval by Default)**:
- `send_email`: Replying to emails, sending new emails
- `publish_linkedin_post`: Publishing posts to LinkedIn
- `send_whatsapp_message`: Sending WhatsApp messages
- `browser_automation`: Form submissions, payments, clicks

**Internal Actions (Auto-Approve)**:
- `vault_update`: Dashboard updates, internal notes
- `create_plan`: Planning and analysis tasks
- `research`: Information gathering tasks

### Company Handbook Parsing

Read `Company_Handbook.md` and extract:
1. **Auto-Approve Rules** (Section: "Auto-Approve Actions")
2. **Require-Approval Rules** (Section: "Require-Approval Actions")
3. **Exceptions** (Section: "Exceptions")
4. **Approval Criteria** (Section: "Approval Criteria")

Use the `permission_boundaries` module to parse these rules:

```python
from my_ai_employee.approval import parse_permission_boundaries, classify_action_risk

boundaries = parse_permission_boundaries()
requires_approval = boundaries.should_require_approval(action_type, context)
risk_level = classify_action_risk(action_type, boundaries, context)
```

### Risk Assessment Generation

For each action requiring approval, generate a risk assessment with:

**1. Impact Analysis:**
- Who is affected? (recipient, audience size)
- What changes? (data, reputation, relationships)
- Reversibility: Can this be undone?

**2. Blast Radius:**
- Low: Internal-only, easily reversible
- Medium: External contact, recoverable
- High: Public post, financial transaction, irreversible

**3. Approval Criteria Checklist:**
- ☐ Recipient trust verified?
- ☐ Content sensitivity assessed?
- ☐ Reversibility confirmed?
- ☐ Compliance checked?

### Draft Content Generation

For external actions, generate draft content:

**Email Replies:**
```
Subject: Re: [Original Subject]

[Generated draft based on action item content]

---
[Assistant note: This draft requires review and approval]
```

**LinkedIn Posts:**
```
[Generated post content]

---
Visibility: [Public/Connections/Private]
Hashtags: [Suggested hashtags]
```

### Execution Step Generation

For approved actions, generate MCP execution steps:

**Format:**
```yaml
execution_plan:
  mcp_server: email  # or linkedin, browser
  tool_name: send_email
  tool_inputs:
    to: recipient@example.com
    subject: "Re: Original Subject"
    body: "[Draft content]"
  retry_policy:
    max_retries: 3
    backoff_seconds: [1, 2, 4]
```

**MCP Server Mapping:**
- `send_email` → email MCP server (`send_email` tool)
- `publish_linkedin_post` → linkedin MCP server (`publish_post` tool)
- `send_whatsapp_message` → browser MCP server (`send_whatsapp_message` tool)

---

## Implementation Steps (Silver Tier)

For each action item in `/Needs_Action`:

1. **Parse Action Item**:
   - Extract type, sender, subject, content
   - Determine action needed (reply, post, update, etc.)

2. **Classify Action Type**:
   - Use content analysis to determine action type
   - Check `Company_Handbook.md` for specific rules

3. **Assess Risk**:
   - Calculate impact, reversibility, blast radius
   - Assign risk level (low/medium/high)

4. **Generate Draft Content** (if external action):
   - Create email reply draft
   - Create LinkedIn post draft
   - Include assistant notes and suggestions

5. **Create Execution Plan**:
   - Define MCP server and tool
   - Specify tool inputs (sanitized)
   - Include retry policy

6. **Route Based on Classification**:
   - **Auto-Approve**: Write plan to `/Plans/`, mark as auto-approved
   - **Require-Approval**: Call `@approval-workflow-manager` to create approval request in `/Pending_Approval/`

7. **Archive Action Item**:
   - Move to `/Done/` with metadata
   - Update Dashboard.md with processing result

---

## Example Plan Output (Silver Tier)

### Auto-Approve Action (Internal)

```markdown
---
type: plan
created: 2026-01-22T15:00:00Z
status: active
classification: auto-approve
risk_level: low
---

# Plan: Update Dashboard with Metrics

**Source**: [[20260122-email-abc123]]

## Classification
- **Action Type**: vault_update
- **Approval Required**: No (auto-approved)
- **Risk Level**: Low

## Action Items
- [x] Read current dashboard content
- [x] Update activity metrics
- [x] Add recent activity log entry
- [x] Save dashboard

## Done Condition
Dashboard updated successfully with latest metrics.
```

### Require-Approval Action (External)

```markdown
---
type: plan
created: 2026-01-22T15:00:00Z
status: pending_approval
classification: require-approval
risk_level: high
action_type: send_email
---

# Plan: Reply to Quarterly Report Request

**Source**: [[20260122-email-xyz789]]

## Classification
- **Action Type**: send_email
- **Approval Required**: Yes
- **Risk Level**: High (external email with potential business impact)

## Risk Assessment

### Impact
- **Recipient**: john@company.com (known business contact)
- **Content**: Quarterly financial report
- **Reversibility**: Cannot be unsent once delivered
- **Blast Radius**: Medium (single recipient, professional context)

### Approval Criteria
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
- Revenue: [Amount]
- Growth: [Percentage]
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
```

## Next Steps

**Action Required**: Move this plan to `/Approved/` to authorize execution.

## Done Condition
Email sent successfully after human approval.
```

---

## Error Handling

- **Malformed Action Items**: Leave in `/Needs_Action/`, add warning to Dashboard
- **Missing Information**: Create plan with "Questions" section, mark as incomplete
- **Classification Uncertainty**: Default to `require-approval` for safety
- **API Errors**: Log to `/Logs/`, notify in Dashboard
