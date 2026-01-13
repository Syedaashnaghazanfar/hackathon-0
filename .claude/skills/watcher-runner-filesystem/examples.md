# Watcher Runner (Filesystem) – Examples

These examples demonstrate how to run and validate the Bronze filesystem watcher that creates `Needs_Action/*.md` in the vault.

Vault convention for these examples:
- Vault root: `My_AI_Employee/AI_Employee_Vault/`

---

## Example 1: Start watcher + confirm it writes to Needs_Action

### User prompt

"@watcher-runner-filesystem\nStart the filesystem watcher. Vault is `My_AI_Employee/AI_Employee_Vault/`. Watch folder is `/tmp/ai-employee-drop/`."

### Expected execution

1. Confirm watcher entrypoint path in `MY-AI-EMPLOYEE/` project code.
2. Start watcher in foreground (so logs are visible).
3. Create a test drop file using `scripts/create_test_drop.py /tmp/ai-employee-drop/`.
4. Confirm a new markdown file appears:
   - `My_AI_Employee/AI_Employee_Vault/Needs_Action/FILE_watcher-smoke-test-<timestamp>.txt.md` (or similar)

### Expected output: Action item created

A file like:

```markdown
---
type: file_drop
subject: watcher-smoke-test-20260112-103500.txt
received: 2026-01-12T10:35:00Z
status: pending
priority: auto
---

## Content
New file dropped for processing.

## Metadata
- original_path: /tmp/ai-employee-drop/watcher-smoke-test-20260112-103500.txt
```

---

## Example 2: Debug when no files appear in Needs_Action

### User prompt

"I dropped files but nothing shows up in `My_AI_Employee/AI_Employee_Vault/Needs_Action`. Debug the watcher."

### Expected troubleshooting sequence

1. Verify the watcher process is running.
2. Verify the watcher is pointing at the correct vault path.
3. Verify the vault path is writable.
4. Run the smoke test script and watch logs.
5. If filesystem events are unreliable (common on some WSL/network setups), switch to a polling approach in the watcher (or recommend running the watcher on a native filesystem path).

### Expected result

- Identify the root cause (path, permissions, dependency, event delivery).
- Provide one minimal fix at a time.
