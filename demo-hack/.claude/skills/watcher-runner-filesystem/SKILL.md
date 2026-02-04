---
name: watcher-runner-filesystem
description: >
  Run and debug the Bronze-tier filesystem watcher that monitors a local drop folder
  and creates markdown action items inside the Obsidian vault's /Needs_Action folder.
  This skill should be used when the user asks to "run the filesystem watcher", "start the Bronze tier watcher",
  "debug why Needs_Action is not updating", "watch a folder for new files", "test the watcher end-to-end",
  or when Claude needs to validate the Perception layer of Hackathon Zero.
  Trigger phrases include: "filesystem watcher", "Bronze tier watcher", "drop folder", "watchdog",
  "watcher logs", "no files appearing in Needs_Action", "run watcher".
---

# Watcher Runner (Filesystem - Bronze Tier)

Start and validate the Bronze-tier filesystem watcher using the unified watcher runner.

## Quick Start

### Run Filesystem Watcher

```bash
# Default - uses .env configuration
uv run python run_watcher.py

# Explicit filesystem watcher
uv run python run_watcher.py --watcher filesystem

# With custom paths
uv run python run_watcher.py --watcher filesystem \
  --vault-path ./AI_Employee_Vault \
  --watch-folder ./test_watch_folder

# Debug mode
uv run python run_watcher.py --watcher filesystem --log-level DEBUG
```

## Configuration

### Environment Variables (.env)

```bash
# Vault configuration
VAULT_ROOT=AI_Employee_Vault

# Filesystem watcher
WATCH_FOLDER=test_watch_folder
WATCH_MODE=events  # or "polling" for WSL/network drives

# Watcher settings
WATCHER_CHECK_INTERVAL=60  # seconds between checks

# Logging
LOG_LEVEL=INFO
```

### Command-Line Override

```bash
uv run python run_watcher.py \
  --watcher filesystem \
  --vault-path ./custom_vault \
  --watch-folder ./custom_watch \
  --watch-mode polling \
  --check-interval 30 \
  --log-level DEBUG
```

## Workflow

1. **Verify Configuration**
   - Check VAULT_ROOT exists
   - Check WATCH_FOLDER exists
   - Verify vault structure (Needs_Action/, Done/, etc.)

2. **Start Watcher**
   - Run `uv run python run_watcher.py --watcher filesystem`
   - Watcher starts monitoring the watch folder
   - Logs show "Filesystem watcher started"

3. **Test File Detection**
   - Drop a test file in watch folder
   - Watcher detects file
   - Creates action item in Needs_Action/
   - Logs show "Created action file: ..."

4. **Verify Action Item**
   - Check Needs_Action/ folder
   - Verify .md file created
   - Check frontmatter (type, received, status)
   - Verify content references source file

## Troubleshooting

### Files Not Detected (WSL/Network Drives)

**Problem**: Files dropped but not detected
**Solution**: Use polling mode
```bash
uv run python run_watcher.py --watcher filesystem --watch-mode polling
```

### Vault Path Not Found

**Problem**: "Vault path does not exist"
**Solution**: Check VAULT_ROOT in .env or use --vault-path
```bash
uv run python run_watcher.py --vault-path ./AI_Employee_Vault
```

### Watch Folder Not Found

**Problem**: "Watch folder does not exist"
**Solution**: Create folder or check path
```bash
mkdir -p test_watch_folder
uv run python run_watcher.py --watch-folder ./test_watch_folder
```

### No Action Items Created

**Problem**: Watcher runs but no .md files in Needs_Action/
**Debugging**:
1. Check watcher logs for errors
2. Verify vault structure exists
3. Check file permissions
4. Try debug mode: `--log-level DEBUG`

## Testing

### Manual Test

```bash
# 1. Start watcher
uv run python run_watcher.py --watcher filesystem --log-level DEBUG

# 2. In another terminal, drop test file
echo "Test request" > test_watch_folder/test_$(date +%s).txt

# 3. Check Needs_Action/ folder
ls -lh AI_Employee_Vault/Needs_Action/

# 4. Verify action item created
cat AI_Employee_Vault/Needs_Action/*.md | head -20
```

### Automated Test

```bash
# Run Bronze tier validation
uv run python scripts/validate/validate_silver_tier.py
```

## Integration with needs-action-triage

After watcher creates action items:

```bash
# Process action items
/needs-action-triage
```

This will:
1. Read items from Needs_Action/
2. Create plans in Plans/
3. Move processed items to Done/
4. Update Dashboard

## Resources

- **Watcher Runner Guide**: `WATCHER_RUNNER_GUIDE.md`
- **Project Organization**: `PROJECT_ORGANIZATION.md`
- **Validation Script**: `scripts/validate/validate_silver_tier.py`
- **Debug Script**: `scripts/debug/debug_gmail.py`

## Architecture

```
run_watcher.py --watcher filesystem
    ↓
Imports FilesystemWatcher
    ↓
Monitors watch folder (events or polling)
    ↓
Detects new files
    ↓
Creates action items in Needs_Action/
    ↓
Logs activity
```

## See Also

- **Silver Tier**: Use `/multi-watcher-runner` for all watchers
- **Triage**: Use `/needs-action-triage` to process action items
- **Vault Ops**: Use `/obsidian-vault-ops` for vault operations
