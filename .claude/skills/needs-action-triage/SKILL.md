---
name: needs-action-triage
description: >
  Triage and plan items in an Obsidian vault's /Needs_Action folder for Hackathon Zero (Bronze tier).
  This skill should be used when the user asks to "process Needs_Action", "triage pending items",
  "create a plan for each item", "turn watcher output into tasks", "update the dashboard after new items",
  "summarize what needs attention", or when Claude detects new action-item markdown files created by a watcher.
  Trigger phrases include: "check /Needs_Action", "process action items", "create Plan.md", "prioritize these",
  "archive to Done", and "apply Company_Handbook rules".
---

# Needs Action Triage

Convert watcher-created inputs into clear next steps **inside the vault**.

Bronze tier scope:
- Read items in `Needs_Action/`
- Read rules from `Company_Handbook.md`
- Write plans/drafts back into the vault
- Update `Dashboard.md`
- Move processed inputs to `Done/`
- Do **not** perform external actions

## Workflow (Bronze)

1. Locate vault root using `@obsidian-vault-ops` workflow.
2. Scan `Needs_Action/` for pending items.
3. For each item:
   - Read file and parse minimal frontmatter (type/received/status/priority).
   - Read `Company_Handbook.md` and apply processing + priority rules.
   - Produce a plan using `templates/PlanTemplate.md`.
   - If the item is missing required info, include a “Questions” section in the plan.
4. Update `Dashboard.md`:
   - Update counts and append a short recent-activity line per processed item.
5. Archive processed input:
   - Move the action item to `Done/` and add `processed` metadata.

## Output rules

- Keep plans actionable: checkboxes + concrete next steps.
- Always link back to the original action item path.
- If the item is malformed, do not move it; instead add a dashboard warning and leave it in `Needs_Action/`.

## Resources

- Reference: `references/action-item-schema.md`
- Reference: `references/triage-rules.md`
- Examples: `examples.md`
- Templates: `templates/PlanTemplate.md`, `templates/ActionItemTemplate.md`
