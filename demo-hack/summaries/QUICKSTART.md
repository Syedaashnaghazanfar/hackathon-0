# Bronze Tier AI Employee - Quick Start Guide

Get your Bronze Tier AI Employee up and running in 5 minutes!

## Prerequisites

- Python 3.13+ installed
- `uv` package manager installed
- A terminal/command line

## Step 1: Install Dependencies (1 minute)

```bash
cd My_AI_Employee
uv sync
```

This installs all required Python packages: `watchdog`, `python-frontmatter`, `python-dotenv`, and `pytest`.

## Step 2: Configure Environment (1 minute)

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your preferred editor
nano .env  # or vim, code, etc.
```

**Minimal Configuration**:

```env
VAULT_PATH=My_AI_Employee/AI_Employee_Vault
WATCH_FOLDER=My_AI_Employee/test_watch_folder
WATCH_MODE=polling
LOG_LEVEL=INFO
```

**Important**:
- Use `polling` mode for WSL or network drives
- Use `events` mode for native Linux/Mac filesystems (faster)

## Step 3: Create Watch Folder (30 seconds)

```bash
mkdir -p My_AI_Employee/test_watch_folder
```

This creates the folder that the watcher will monitor for new files.

## Step 4: Verify Vault Structure (30 seconds)

The vault should already exist at `My_AI_Employee/AI_Employee_Vault/` with:

```
AI_Employee_Vault/
├── Inbox/
├── Needs_Action/
├── Done/
├── Plans/
├── Dashboard.md
└── Company_Handbook.md
```

If it doesn't exist, the watcher will create it automatically on first run.

## Step 5: Start the Watcher (30 seconds)

```bash
cd /path/to/project
PYTHONPATH=/path/to/project My_AI_Employee/.venv/bin/python My_AI_Employee/run_watcher.py
```

You should see output like:

```
============================================================
Bronze Tier AI Employee - Filesystem Watcher
============================================================
Vault path: /path/to/My_AI_Employee/AI_Employee_Vault
Watch folder: /path/to/My_AI_Employee/test_watch_folder
Watch mode: polling
Check interval: 60s
Log level: INFO
============================================================
FilesystemWatcher initialized
Watching folder: /path/to/My_AI_Employee/test_watch_folder
Press Ctrl+C to stop
```

## Step 6: Test the Watcher (1 minute)

**In a new terminal**, drop a test file into the watch folder:

```bash
echo "This is a test document for the AI Employee.

Please review and process this file.

Priority: Medium
Category: General" > My_AI_Employee/test_watch_folder/test_document.txt
```

**Wait 5-10 seconds** (depending on your `CHECK_INTERVAL`), then check the Needs_Action folder:

```bash
ls -la My_AI_Employee/AI_Employee_Vault/Needs_Action/
```

You should see a new markdown file like `20260113_134636_123456_test_document.md`.

**View the action item**:

```bash
cat My_AI_Employee/AI_Employee_Vault/Needs_Action/*.md
```

You should see:

```markdown
---
detected: '2026-01-13T13:46:36.553836'
file_id: f841ebce2935aa31da86559aead005cb622f7c3730606c758911fa958409dcaf
received: '2026-01-13T13:46:36.553854'
source_path: /path/to/test_document.txt
status: pending
type: file_drop
---

# Action Required: test_document.txt

## Source File
- **Path**: `/path/to/test_document.txt`
- **Size**: 196 bytes
- **Modified**: 2026-01-13T13:46:31.214957

## Description
New file detected in watch folder. Review and determine appropriate action.

## Next Steps
- [ ] Review file contents
- [ ] Determine priority and category
- [ ] Create plan if needed
- [ ] Archive to Done when complete
```

✅ **Success!** Your watcher is working correctly.

## Step 7: (Optional) Open in Obsidian (1 minute)

1. Open Obsidian application
2. Click "Open folder as vault"
3. Select `My_AI_Employee/AI_Employee_Vault/`
4. Browse the vault in Obsidian's GUI

You'll see:
- Action items in `Needs_Action/` folder
- Dashboard with system status
- Company Handbook with processing rules

## Step 8: Triage Action Items with Claude Code

Use the `@needs-action-triage` skill in Claude Code to process pending items:

```bash
# In Claude Code CLI
@needs-action-triage
```

This will:
1. Read all pending items from `Needs_Action/`
2. Apply Company Handbook rules
3. Generate plans in `Plans/` folder
4. Archive processed items to `Done/`
5. Update Dashboard with status

## Common Issues & Solutions

### Issue: Watcher not detecting files

**Solution 1**: Use polling mode
```env
WATCH_MODE=polling
CHECK_INTERVAL=5
```

**Solution 2**: Check watch folder path
```bash
ls -la My_AI_Employee/test_watch_folder/
```

**Solution 3**: Check watcher logs for errors

### Issue: Permission denied errors

**Solution**: Ensure vault folders are writable
```bash
chmod -R u+w My_AI_Employee/AI_Employee_Vault/
```

### Issue: Module not found errors

**Solution**: Use PYTHONPATH
```bash
PYTHONPATH=/path/to/project My_AI_Employee/.venv/bin/python My_AI_Employee/run_watcher.py
```

### Issue: Duplicate action items

**Solution**: Clear dedupe state if needed
```bash
rm dedupe_state.json
```

## Next Steps

### 1. Customize Company Handbook

Edit `AI_Employee_Vault/Company_Handbook.md` to define:
- Priority classification rules
- Communication tone preferences
- Permission boundaries
- Output format preferences

### 2. Run Tests

Verify everything works:

```bash
cd /path/to/project
PYTHONPATH=. My_AI_Employee/.venv/bin/python -m pytest tests/ -v
```

All 13 tests should pass.

### 3. Set Up Real Watch Folder

Update `.env` to point to your actual watch folder:

```env
WATCH_FOLDER=/home/user/Documents/AI_Employee_Inbox
```

### 4. Automate Watcher Startup

Create a systemd service (Linux) or launchd service (Mac) to start the watcher automatically.

**Example systemd service** (`/etc/systemd/system/ai-employee-watcher.service`):

```ini
[Unit]
Description=Bronze Tier AI Employee Watcher
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/project
Environment="PYTHONPATH=/path/to/project"
ExecStart=/path/to/My_AI_Employee/.venv/bin/python My_AI_Employee/run_watcher.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable ai-employee-watcher
sudo systemctl start ai-employee-watcher
sudo systemctl status ai-employee-watcher
```

## Tips & Best Practices

### 1. Use Polling Mode on WSL

WSL filesystem events can be unreliable. Always use `WATCH_MODE=polling` on WSL.

### 2. Adjust Check Interval

- Fast response: `CHECK_INTERVAL=5` (5 seconds)
- Balanced: `CHECK_INTERVAL=60` (1 minute, default)
- Low resource: `CHECK_INTERVAL=300` (5 minutes)

### 3. Monitor Dashboard

Check `Dashboard.md` regularly for:
- Pending item counts
- Recent activity
- System warnings

### 4. Archive Regularly

Move old items from `Done/` to an archive folder to keep the vault clean.

### 5. Backup Dedupe State

The `dedupe_state.json` file prevents duplicates. Back it up periodically:

```bash
cp dedupe_state.json dedupe_state.json.backup
```

## Troubleshooting Commands

```bash
# Check watcher is running
ps aux | grep run_watcher

# View recent logs (if logging to file)
tail -f logs/watcher.log

# Count pending items
ls -1 My_AI_Employee/AI_Employee_Vault/Needs_Action/*.md | wc -l

# Count archived items
ls -1 My_AI_Employee/AI_Employee_Vault/Done/*.md | wc -l

# Validate vault structure
# (Use @obsidian-vault-ops skill in Claude Code)

# Run tests
PYTHONPATH=. My_AI_Employee/.venv/bin/python -m pytest tests/ -v
```

## Getting Help

- **Documentation**: See [README.md](README.md) for full documentation
- **Specifications**: See `specs/001-bronze-ai-employee/` for design details
- **Issues**: Check GitHub issues or create a new one

## What's Next?

You now have a working Bronze Tier AI Employee! 🎉

**Experiment with**:
- Dropping different file types
- Customizing the Company Handbook
- Creating custom triage workflows
- Integrating with your existing tools

**Future Enhancements** (Silver/Gold Tiers):
- Email integration
- External API calls
- Automated execution
- Advanced analytics

Happy automating! 🚀
