# Watcher Runner Guide

This guide explains how to run the AI Employee watchers for Bronze and Silver tiers.

## Quick Start

### Bronze Tier (Filesystem Watcher Only)

```bash
# Default - runs filesystem watcher
python run_watcher.py

# Explicit filesystem watcher
python run_watcher.py --watcher filesystem

# With custom paths
python run_watcher.py --watcher filesystem \
  --vault-path ./AI_Employee_Vault \
  --watch-folder ./test_watch_folder
```

### Silver Tier (Individual Watchers)

```bash
# Gmail watcher
python run_watcher.py --watcher gmail

# LinkedIn watcher
python run_watcher.py --watcher linkedin

# WhatsApp watcher
python run_watcher.py --watcher whatsapp
```

### Silver Tier (All Watchers with Orchestration)

```bash
# Run all watchers with health monitoring and auto-restart
python run_watcher.py --watcher all
```

## Configuration

### Environment Variables (.env)

```bash
# Vault configuration
VAULT_ROOT=AI_Employee_Vault

# Filesystem watcher (Bronze tier)
WATCH_FOLDER=test_watch_folder
WATCH_MODE=events  # or "polling" for WSL/network drives

# Watcher settings
WATCHER_CHECK_INTERVAL=60  # seconds between checks

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Command-Line Arguments

All environment variables can be overridden via command-line arguments:

```bash
python run_watcher.py \
  --watcher gmail \
  --vault-path ./custom_vault \
  --check-interval 30 \
  --log-level DEBUG
```

## Watcher Types

### 1. Filesystem Watcher (Bronze Tier)
- **Purpose**: Monitors a local folder for new files
- **Creates**: Action items in `/Needs_Action/` for each new file
- **Requirements**: Local filesystem access
- **Use Case**: Drop files into a folder to create tasks

### 2. Gmail Watcher (Silver Tier)
- **Purpose**: Monitors Gmail inbox for new emails
- **Creates**: Action items in `/Needs_Action/` for each new email
- **Requirements**: Gmail OAuth credentials (credentials.json, token.json)
- **Setup**: Run `python setup_gmail_oauth.py` first

### 3. LinkedIn Watcher (Silver Tier)
- **Purpose**: Monitors LinkedIn for messages and notifications
- **Creates**: Action items in `/Needs_Action/` for LinkedIn activity
- **Requirements**: LinkedIn session credentials
- **Setup**: Configure LinkedIn credentials in .env

### 4. WhatsApp Watcher (Silver Tier)
- **Purpose**: Monitors WhatsApp Web for new messages
- **Creates**: Action items in `/Needs_Action/` for WhatsApp messages
- **Requirements**: WhatsApp Web session
- **Setup**: Configure WhatsApp session in .env

### 5. All Watchers (Silver Tier - Orchestrated)
- **Purpose**: Runs all watchers with health monitoring
- **Features**:
  - Auto-restart on crash
  - Health checks every 30 seconds
  - Uptime monitoring
  - Graceful shutdown
- **Use Case**: Production deployment of Silver tier

## Architecture

### Single Watcher Mode
```
run_watcher.py --watcher <type>
    ↓
Imports specific watcher class
    ↓
Runs watcher.run() in main thread
    ↓
Polls for updates every N seconds
    ↓
Creates action items in /Needs_Action/
```

### Orchestrated Mode (--watcher all)
```
run_watcher.py --watcher all
    ↓
Imports MultiWatcherOrchestrator
    ↓
Starts all watchers in separate threads
    ↓
Health check worker monitors all threads
    ↓
Auto-restarts failed watchers
    ↓
Logs status every 30 seconds
```

## Troubleshooting

### Filesystem Watcher Issues

**Problem**: Files not detected on WSL/network drives
**Solution**: Use polling mode
```bash
python run_watcher.py --watcher filesystem --watch-mode polling
```

**Problem**: Vault path not found
**Solution**: Check VAULT_ROOT in .env or use --vault-path
```bash
python run_watcher.py --vault-path ./AI_Employee_Vault
```

### Gmail Watcher Issues

**Problem**: OAuth authentication failed
**Solution**: Run OAuth setup script
```bash
python setup_gmail_oauth.py
```

**Problem**: Token expired
**Solution**: Delete token.json and re-authenticate
```bash
rm token.json
python setup_gmail_oauth.py
```

### All Watchers Issues

**Problem**: Some watchers fail to start
**Solution**: Check logs for specific watcher errors
```bash
tail -f logs/orchestrator.log
```

**Problem**: Watchers keep restarting
**Solution**: Check credentials and configuration for failing watchers

## Logs

### Single Watcher
Logs are written to stdout/stderr. Redirect to file if needed:
```bash
python run_watcher.py --watcher gmail 2>&1 | tee logs/gmail_watcher.log
```

### Orchestrated Mode
Logs are automatically written to:
- `logs/orchestrator.log` - Main orchestrator log
- Console output - Real-time status updates

## Production Deployment

### Using PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Start all watchers
pm2 start ecosystem.config.js

# Check status
pm2 status

# View logs
pm2 logs

# Stop all
pm2 stop all

# Restart all
pm2 restart all
```

### Using systemd

Create `/etc/systemd/system/ai-employee-watchers.service`:
```ini
[Unit]
Description=AI Employee Watchers
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/My_AI_Employee
ExecStart=/usr/bin/python3 run_watcher.py --watcher all
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ai-employee-watchers
sudo systemctl start ai-employee-watchers
sudo systemctl status ai-employee-watchers
```

## Migration from Old Scripts

### Old Script → New Unified Runner

| Old Script | New Command |
|------------|-------------|
| `python watchers/filesystem_watcher.py` | `python run_watcher.py --watcher filesystem` |
| `python watchers/gmail_watcher.py` | `python run_watcher.py --watcher gmail` |
| `python orchestrate_watchers.py` | `python run_watcher.py --watcher all` |

### Backup Files

The following backup files are kept for reference:
- `run_watcher_old_filesystem_only.py` - Original filesystem-only runner
- `orchestrate_watchers_backup.py` - Original multi-watcher orchestrator

These can be deleted once you've verified the unified runner works correctly.

## Examples

### Development (Bronze Tier)
```bash
# Run filesystem watcher with debug logging
python run_watcher.py \
  --watcher filesystem \
  --log-level DEBUG \
  --check-interval 10
```

### Production (Silver Tier)
```bash
# Run all watchers with orchestration
python run_watcher.py --watcher all
```

### Testing Individual Watchers
```bash
# Test Gmail watcher
python run_watcher.py --watcher gmail --check-interval 30

# Test LinkedIn watcher
python run_watcher.py --watcher linkedin --check-interval 60
```
