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
   - If the item is missing required info, include a "Questions" section in the plan.
4. Update `Dashboard.md`:
   - Update counts and append a short recent-activity line per processed item.
5. Archive processed input:
   - **Bronze Tier (no external action)**: Move to `Done/` folder with `status: completed`
   - **Silver Tier (external action required)**:
     - KEEP in `Needs_Action/` folder (do NOT move to Done yet!)
     - Update metadata: `status: pending_approval`, `result: pending_approval`
     - Add `related_plan` and `related_approval` references
     - The file will be moved to `Done/` by `@mcp-executor` AFTER the external action completes
   - Add `processed` metadata to frontmatter:
     - `processed: [ISO timestamp]`
     - `result: planned` (Bronze) or `pending_approval` (Silver)
     - `related_plan: Plans/[plan-filename].md`
     - `related_approval: Pending_Approval/[approval-filename].md` (Silver only)
     - `status: completed` (Bronze) or `pending_approval` (Silver)
   - Mark all checkboxes in "Next Steps" section as completed `[x]` ONLY if no external action remains (Bronze only).

## Output rules

- Keep plans actionable: checkboxes + concrete next steps.
- Always link back to the original action item path.
- If the item is malformed, do not move it; instead add a dashboard warning and leave it in `Needs_Action/`.

## Resources

- Reference: `references/action-item-schema.md`
- Reference: `references/triage-rules.md`
- Examples: `examples.md`
- Templates: `templates/PlanTemplate.md`, `templates/ActionItemTemplate.md`
