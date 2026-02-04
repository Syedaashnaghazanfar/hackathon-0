# Needs Action Triage – Examples

These examples demonstrate Bronze-tier triage: read `/Needs_Action`, apply `Company_Handbook.md`, create a plan, update `Dashboard.md`, and archive processed items to `/Done`.

Vault convention for these examples:
- Vault root: `My_AI_Employee/AI_Employee_Vault/`

---

## Example 1: Triage one watcher-created email item

### Input: Action item file

**File**: `My_AI_Employee/AI_Employee_Vault/Needs_Action/EMAIL_20260112_12345.md`

```markdown
---
type: email
from: client@example.com
subject: Invoice Request - January 2026
received: 2026-01-12T10:15:00Z
priority: high
status: pending
source_id: EMAIL_20260112_12345
---

## Content
Could you please send me the invoice for January 2026?

## Metadata
- Label: IMPORTANT
```

### User prompt

"@needs-action-triage\nProcess `/Needs_Action` and create a plan for each new item. Update the dashboard and move processed items to Done."

### Expected execution

1. Read the action item file.
2. Read `My_AI_Employee/AI_Employee_Vault/Company_Handbook.md`.
3. Create a plan file using `templates/PlanTemplate.md`:
   - Include source info, analysis, and 3–7 checkboxes.
   - Include a Done Condition.
4. Update `My_AI_Employee/AI_Employee_Vault/Dashboard.md` (counts + recent activity).
5. Move the processed action item to `Done/` and add `processed` metadata.

### Expected outputs

- Plan created:
  - `My_AI_Employee/AI_Employee_Vault/Plans/PLAN_invoice-request_20260112-103000.md` (or your chosen Plans location)
- Dashboard updated (timestamp + counts)
- Archived item:
  - `My_AI_Employee/AI_Employee_Vault/Done/EMAIL_20260112_12345.md`

---

## Example 2: Triage a filesystem file-drop item

### Input: Action item file

**File**: `My_AI_Employee/AI_Employee_Vault/Needs_Action/FILE_expense_report_2026-01-08.csv.md`

```markdown
---
type: file_drop
from: /DropFolder/expense_report_2026-01-08.csv
subject: expense_report_2026-01-08.csv
received: 2026-01-12T08:00:00Z
priority: auto
status: pending
source_id: FILE_expense_report_20260108
---

## Content
New file dropped in watch folder: expense_report_2026-01-08.csv
File type: CSV
```

### User prompt

"Process the new file-drop item and create a plan with concrete next steps."

### Expected outputs

- A plan that includes:
  - validating CSV structure
  - clarifying where the CSV is stored (if not in-vault)
  - what the human should do next in Bronze tier

---

## Example 3: Malformed action item (leave in Needs_Action)

### Input: Malformed file

**File**: `My_AI_Employee/AI_Employee_Vault/Needs_Action/EMAIL_broken.md`

```markdown
---
type: email
received: invalid-date
status: pending
---

## Content
This has malformed frontmatter.
```

### Expected execution

- Detect invalid frontmatter.
- Do NOT move the file to `Done/`.
- Create a "Manual review required" plan that lists what is wrong.
- Add a dashboard warning entry indicating manual review is needed.
