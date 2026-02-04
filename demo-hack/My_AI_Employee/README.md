# Bronze Tier AI Employee

A local-first AI employee system that monitors a filesystem folder, creates action items in an Obsidian vault, and enables Claude Code to triage and process them according to Company Handbook rules.

## Overview

The Bronze Tier AI Employee is a **local-first, no-external-actions** system that:

1. **Watches** a local folder for new files (Perception layer)
2. **Creates** action items in an Obsidian vault's `Needs_Action/` folder
3. **Enables** Claude Code to triage items, create plans, and archive to `Done/`
4. **Updates** a Dashboard with system status and recent activity

**Key Constraint**: No MCP servers, no external APIs, no email - purely local filesystem operations.

## Features

- ✅ **Filesystem Watcher**: Monitors a drop folder and creates action items automatically
- ✅ **Obsidian Vault Integration**: Uses Obsidian as the "Memory/GUI" for the AI employee
- ✅ **Duplicate Prevention**: SHA256-based deduplication prevents duplicate action items
- ✅ **Triage Workflow**: Claude Code processes items according to Company Handbook rules
- ✅ **Plan Generation**: Auto-generates plans with checkboxes and done conditions
- ✅ **Dashboard Updates**: Real-time status tracking and activity logging
- ✅ **Vault Validation**: Ensures consistent vault structure for predictable operations
- ✅ **Comprehensive Tests**: 13 pytest tests covering core functionality

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a step-by-step guide to get started in 5 minutes.

## Requirements

- **Python**: 3.13+
- **uv**: Modern Python package manager
- **Obsidian**: (Optional) For viewing the vault as a GUI

### Python Dependencies

- `watchdog>=6.0.0` - Filesystem monitoring
- `python-frontmatter>=1.1.0` - YAML frontmatter parsing
- `python-dotenv>=1.0.0` - Environment variable management
- `pytest>=9.0.2` - Testing framework

## Installation

```bash
# 1. Navigate to project directory
cd My_AI_Employee

# 2. Install dependencies
uv sync

# 3. Configure environment (if needed)
# The .env file is already configured with default paths
# VAULT_PATH=AI_Employee_Vault
# WATCH_FOLDER=test_watch_folder
# WATCH_MODE=polling
```

## Usage

### Complete Workflow

#### Step 1: Start the Watcher

```bash
cd My_AI_Employee
uv run python run_watcher.py
```

The watcher will:
- Monitor `test_watch_folder/` for new files
- Check every 60 seconds (polling mode for WSL compatibility)
- Create action items in `AI_Employee_Vault/Needs_Action/`
- Prevent duplicates using SHA256 file hashing

#### Step 2: Drop a File

Drop any file into the watch folder:

```bash
# Example: Copy a document
cp /path/to/document.txt test_watch_folder/

# Or create a new file
echo "Task description" > test_watch_folder/task.txt
```

**Wait 60 seconds** for the watcher to detect the file. You'll see:
```
File created: task.txt
Created action item: 20260114_XXXXXX_task.md
Successfully processed: task.txt
```

#### Step 3: Process with Claude Code

Open Claude Code in your project and use **either**:

**Option A: Slash Command (Recommended)**
```
/needs-action-triage
```

**Option B: Natural Language**
```
Process the pending action items
```

Claude will:
1. ✅ Read items from `Needs_Action/`
2. ✅ Apply rules from `Company_Handbook.md`
3. ✅ Create plans in `Plans/` with checkboxes
4. ✅ Update `Dashboard.md` with activity
5. ✅ Archive items to `Done/` with metadata

#### Step 4: View Results

**Check the Plan:**
```bash
cat AI_Employee_Vault/Plans/Plan_*.md
```

**Check the Dashboard:**
```bash
cat AI_Employee_Vault/Dashboard.md
```

**Check Done folder:**
```bash
ls AI_Employee_Vault/Done/
```

**Open in Obsidian (Optional):**
1. Open Obsidian app
2. "Open folder as vault"
3. Select: `My_AI_Employee/AI_Employee_Vault/`

### Testing

```bash
cd /path/to/hackathon-0
PYTHONPATH=. My_AI_Employee/.venv/bin/python -m pytest tests/ -v
```

## Project Structure

```
My_AI_Employee/
├── watchers/          # Filesystem monitoring
├── utils/             # Shared utilities
├── vault_ops/         # Vault operations
├── triage/            # Triage logic
└── AI_Employee_Vault/ # Obsidian vault
```

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Step-by-step setup guide
- [specs/](../specs/001-bronze-ai-employee/) - Design specifications

## License

MIT License
