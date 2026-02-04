# Bronze Demo Check – Examples

These examples demonstrate how to validate (and present) Hackathon Zero Bronze tier end-to-end.

Vault convention for these examples:
- Vault root: `My_AI_Employee/AI_Employee_Vault/`

---

## Example 1: Bronze readiness validation

### User prompt

"@bronze-demo-check\nAm I done with Bronze tier? Validate everything for my vault at `My_AI_Employee/AI_Employee_Vault/` and tell me what’s missing."

### Expected execution

1. Verify required files/folders exist:
   - `Dashboard.md`, `Company_Handbook.md`
   - `Inbox/`, `Needs_Action/`, `Done/`
2. Verify watcher path:
   - confirm at least one `.md` exists in `Needs_Action/` created by the watcher
3. Verify reasoning loop:
   - confirm at least one plan file exists (or provide steps to create it)
   - confirm `Dashboard.md` updated with recent activity
4. Verify archival behavior:
   - confirm at least one item moved to `Done/` (or provide steps)

### Expected output

- A checklist with PASS/FAIL per item
- A short “next steps” list to close gaps

---

## Example 2: 5-minute judge demo script

### User prompt

"Give me a 5-minute demo script for judges for Bronze tier. Use filesystem watcher."

### Expected output

A scripted sequence:
1. Show vault structure
2. Drop a file into watch folder
3. Show new `Needs_Action/*.md`
4. Run `@needs-action-triage` to create a plan + update dashboard
5. Show the item moved to `Done/`

---

## Example 3: Failure-path demo (malformed action item)

### User prompt

"Show how the system behaves if a watcher produces a malformed action item."

### Expected behavior

- Malformed file remains in `Needs_Action/`
- A dashboard warning is added
- A manual-review plan is created (instead of crashing or deleting the file)
