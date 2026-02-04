# Watcher Runner (Filesystem) – Examples

Run and validate the Bronze filesystem watcher using the unified watcher runner.

---

## Example 1: Start Filesystem Watcher (Default Configuration)

### User Prompt

```
Start the filesystem watcher using default configuration from .env
```

### Expected Execution

```bash
# Start watcher with default settings
uv run python run_watcher.py

# Or explicitly specify filesystem
uv run python run_watcher.py --watcher filesystem
```

### Expected Output

```
2026-01-18 16:00:00 - INFO - ============================================================
2026-01-18 16:00:00 - INFO - Bronze Tier - Filesystem Watcher
2026-01-18 16:00:00 - INFO - ============================================================
2026-01-18 16:00:00 - INFO - Vault: /path/to/AI_Employee_Vault
2026-01-18 16:00:00 - INFO - Watch folder: /path/to/test_watch_folder
2026-01-18 16:00:00 - INFO - Watch mode: events
2026-01-18 16:00:00 - INFO - Check interval: 60s
2026-01-18 16:00:00 - INFO - ============================================================
2026-01-18 16:00:00 - INFO - Starting FilesystemWatcher
2026-01-18 16:00:00 - INFO - Vault: /path/to/AI_Employee_Vault
2026-01-18 16:00:00 - INFO - Check interval: 60s
2026-01-18 16:00:00 - INFO - Checking for new items...
```

---

## Example 2: Test File Detection

### User Prompt

```
Test the filesystem watcher by dropping a test file
```

### Expected Execution

```bash
# Terminal 1: Start watcher
uv run python run_watcher.py --watcher filesystem --log-level DEBUG

# Terminal 2: Create test file
echo "Test request: Please review this document" > test_watch_folder/test_$(date +%s).txt

# Or use the test script
uv run python .claude/skills/watcher-runner-filesystem/scripts/create_test_drop.py test_watch_folder
```

### Expected Output

```
# Watcher detects file
2026-01-18 16:01:00 - INFO - Checking for new items...
2026-01-18 16:01:00 - INFO - Found 1 new items
2026-01-18 16:01:00 - INFO - Created action file: 20260118_160100_123456_test_1234567890.md

# Action item created in Needs_Action/
AI_Employee_Vault/Needs_Action/20260118_160100_123456_test_1234567890.md
```

### Verify Action Item

```bash
# Check Needs_Action folder
ls -lh AI_Employee_Vault/Needs_Action/

# View the created action item
cat AI_Employee_Vault/Needs_Action/20260118_160100_*.md
```

**Expected Content:**

```markdown
---
type: file
source: filesystem_watcher
received: 2026-01-18T16:01:00Z
priority: Medium
status: pending
source_path: /path/to/test_watch_folder/test_1234567890.txt
---

# File Drop: test_1234567890.txt

**Source**: test_watch_folder/test_1234567890.txt
**Detected**: 2026-01-18 16:01:00
**Size**: 45 bytes

## Content Preview

Test request: Please review this document

## Next Steps

- [ ] Review file content
- [ ] Determine action needed
- [ ] Process with /needs-action-triage
```

---

## Example 3: Custom Paths (Override .env)

### User Prompt

```
Run filesystem watcher with custom vault and watch folder paths
```

### Expected Execution

```bash
uv run python run_watcher.py --watcher filesystem \
  --vault-path ./custom_vault \
  --watch-folder ./custom_watch \
  --log-level DEBUG
```

---

## Example 4: Polling Mode (WSL/Network Drives)

### User Prompt

```
Files aren't being detected on WSL. Use polling mode instead of events.
```

### Expected Execution

```bash
# Use polling mode for WSL/network drives
uv run python run_watcher.py --watcher filesystem \
  --watch-mode polling \
  --check-interval 30
```

### Why Polling Mode?

- **Events mode**: Uses OS filesystem events (fast, but doesn't work on WSL/network drives)
- **Polling mode**: Checks folder periodically (slower, but works everywhere)

---

## Example 5: Debug Mode

### User Prompt

```
Watcher is running but no action items are created. Debug the issue.
```

### Expected Execution

```bash
# Run with debug logging
uv run python run_watcher.py --watcher filesystem --log-level DEBUG

# Check for errors in output:
# - Vault path not found
# - Watch folder not found
# - Permission denied
# - File already processed (dedupe)
```

### Common Issues

**Issue 1: Vault path not found**
```
ERROR - Vault path does not exist: /path/to/vault
```
**Solution**: Check VAULT_ROOT in .env or use --vault-path

**Issue 2: Watch folder not found**
```
ERROR - Watch folder does not exist: /path/to/watch
```
**Solution**: Create folder or check WATCH_FOLDER in .env

**Issue 3: Files already processed**
```
DEBUG - File already processed: test.txt (ID: abc123)
```
**Solution**: Watcher uses deduplication. Delete `.filesystem_dedupe.json` to reset.

---

## Example 6: Integration with needs-action-triage

### User Prompt

```
Process the action items created by the filesystem watcher
```

### Expected Execution

```bash
# 1. Watcher creates action items
uv run python run_watcher.py --watcher filesystem

# 2. Process with needs-action-triage skill
# In Claude Code:
/needs-action-triage
```

### Expected Workflow

```
Filesystem Watcher
    ↓ Creates action items
Needs_Action/
    ↓ Process with /needs-action-triage
Plans/ + Dashboard updated
    ↓ Move to Done/
Done/
```

---

## Example 7: Validation Script

### User Prompt

```
Validate the filesystem watcher setup before running
```

### Expected Execution

```bash
# Run validation script
uv run python scripts/validate/validate_silver_tier.py

# This checks:
# ✅ Vault structure exists
# ✅ Watch folder exists
# ✅ Watcher can create action items
# ✅ Dashboard updates work
```

---

## See Also

- **Watcher Runner Guide**: `WATCHER_RUNNER_GUIDE.md`
- **Project Organization**: `PROJECT_ORGANIZATION.md`
- **Silver Tier**: Use `/multi-watcher-runner` for all watchers
- **Triage**: Use `/needs-action-triage` to process action items
