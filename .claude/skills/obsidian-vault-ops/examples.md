# Obsidian Vault Ops – Examples

These examples demonstrate safe, local-first file operations in the Obsidian vault for Hackathon Zero (Bronze tier).

Vault convention for these examples:
- Vault root: `My_AI_Employee/AI_Employee_Vault/`
- Required folders: `Inbox/`, `Needs_Action/`, `Done/`

---

## Example 1: Initialize Bronze vault structure

### User prompt

"Create the Bronze-tier Obsidian vault under `My_AI_Employee/AI_Employee_Vault/` with `Dashboard.md`, `Company_Handbook.md`, and the `Inbox/`, `Needs_Action/`, `Done/` folders. Use your templates."

### Expected actions

1. Ensure the vault root exists at `My_AI_Employee/AI_Employee_Vault/`.
2. Create folders:
   - `My_AI_Employee/AI_Employee_Vault/Inbox/`
   - `My_AI_Employee/AI_Employee_Vault/Needs_Action/`
   - `My_AI_Employee/AI_Employee_Vault/Done/`
3. Create files from templates:
   - `My_AI_Employee/AI_Employee_Vault/Dashboard.md` (from `templates/DashboardTemplate.md`)
   - `My_AI_Employee/AI_Employee_Vault/Company_Handbook.md` (from `templates/CompanyHandbookTemplate.md`)

### Expected outputs

- A vault tree containing the required artifacts.
- `Dashboard.md` includes an auto-generated section and a clear separator to preserve user notes.

---

## Example 2: Update Dashboard without clobbering user notes

### Starting state

`My_AI_Employee/AI_Employee_Vault/Dashboard.md` contains a separator like:

```markdown
---
*Auto-generated above. User notes below.*
```

…and the user has written custom notes below the separator.

### User prompt

"Update `Dashboard.md` with the current counts of pending items and the most recent activity, but do not overwrite my notes."

### Expected actions

1. Read `Dashboard.md`.
2. Update only the auto-generated section above the separator:
   - Last Updated timestamp
   - counts (Pending Action Items, Active Plans)
   - recent activity list
3. Preserve everything below the separator exactly.

### Expected outputs

- `Dashboard.md` updated above the separator, user content unchanged below it.

---

## Example 3: Archive a processed action item safely

### Input file

`My_AI_Employee/AI_Employee_Vault/Needs_Action/ACTION_invoice-request_20260112-101500.md`

```markdown
---
type: email
from: client@example.com
subject: Invoice request
received: 2026-01-12T10:15:00Z
priority: high
status: pending
---

## Content
Please send the January invoice.
```

### User prompt

"Move the processed item to Done and preserve its frontmatter. Add processed metadata and link the plan."

### Expected actions

1. Move the file within the vault only:
   - From: `Needs_Action/...`
   - To: `Done/...`
2. Preserve the existing frontmatter fields.
3. Add minimal archive metadata (without deleting original fields):
   - `processed: 2026-01-12T...Z`
   - `result: planned`
   - `related_plan: Plans/PLAN_invoice-request_20260112-103000.md`

### Expected output (Done file)

A file like:

`My_AI_Employee/AI_Employee_Vault/Done/ACTION_invoice-request_20260112-101500.md`

```yaml
processed: 2026-01-12T10:30:00Z
result: planned
related_plan: Plans/PLAN_invoice-request_20260112-103000.md
```

(Original content preserved.)
