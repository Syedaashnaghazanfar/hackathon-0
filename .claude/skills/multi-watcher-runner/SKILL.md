---
name: multi-watcher-runner
description: >
  Orchestrate and manage multiple watchers for Silver tier: Gmail, WhatsApp Web, LinkedIn, and filesystem monitoring.
  Monitors all sources for new emails, messages, and notifications. Creates action items in /Needs_Action/ folder.
  Manages watcher authentication, session persistence, health monitoring, and automatic restart on crash.
  Use when: (1) Setting up Silver tier watcher infrastructure, (2) Starting all watchers simultaneously,
  (3) Checking watcher health and status, (4) Debugging watcher issues, (5) Managing watcher sessions and credentials.
  Trigger phrases: "start Silver watchers", "run multi-watcher system", "monitor Gmail WhatsApp LinkedIn",
  "check watcher status", "setup multi-watcher infrastructure", "manage watchers 24/7".
---

# Multi-Watcher Runner (Silver Tier)

Orchestrate multiple watchers (Gmail, WhatsApp Web, LinkedIn, filesystem) running simultaneously to monitor diverse information sources and create action items in the Obsidian vault.

## Quick Start

### Prerequisites

- All watchers configured in `Company_Handbook.md`
- `.env` file with credentials (Gmail OAuth, LinkedIn token)
- Playwright browsers installed: `playwright install chromium`
- Watchdog installed: `pip install watchdog`

## Two Approaches for Process Management (Choose One)

### Approach A: PM2 Process Manager (Recommended by HACKATHON-ZERO.md)

**What it is**: Industry-standard Node.js process manager that handles auto-restart, logging, and monitoring.

**Advantages**:
- ✅ Recommended by HACKATHON-ZERO.md (Line 1091-1315)
- ✅ Auto-restart on crash
- ✅ Built-in logging and monitoring
- ✅ Easy to use: `pm2 monit`, `pm2 logs`
- ✅ Startup on system reboot

**Setup**:
```bash
# Install PM2 globally
npm install -g pm2

# Start all watchers via PM2 config
cd My_AI_Employee
pm2 start ecosystem.config.js

# Monitor all processes
pm2 monit

# View logs
pm2 logs

# Save configuration for reboot
pm2 save
pm2 startup
```

**Required file**: `My_AI_Employee/ecosystem.config.js` (see templates/)

### Approach B: Python Health Monitor (Custom Watchdog)

**What it is**: Custom Python script that monitors watcher health and auto-restarts failed processes.

**Advantages**:
- ✅ No Node.js dependency
- ✅ Custom health checks (token validity, API connectivity)
- ✅ Python-native solution
- ✅ Detailed uptime metrics

**Setup**:
```bash
# Run the Python health monitor
python scripts/orchestrate_watchers.py
```

**Note**: This is equivalent to `watchdog.py` in HACKATHON-ZERO.md (Line 809-836). It monitors watcher processes and restarts them on failure.

### Which Approach to Use?

- **For hackathon submission**: Use PM2 (Approach A) - it's explicitly recommended in HACKATHON-ZERO.md
- **For development/testing**: Either approach works
- **For production**: PM2 is more battle-tested

**You can use BOTH**: PM2 manages processes, orchestrate_watchers.py provides additional health monitoring

## Watcher Types

### 1. Gmail Watcher
- **Source**: Gmail API v1 via OAuth 2.0
- **Trigger**: New emails in monitored inbox/labels
- **Action**: Create action item in `/Needs_Action/`
- **Config**: `Company_Handbook.md` → Gmail section

### 2. WhatsApp Watcher
- **Source**: WhatsApp Web via Playwright (browser automation)
- **Trigger**: New messages from monitored contacts
- **Action**: Create action item in `/Needs_Action/`
- **Config**: `Company_Handbook.md` → Monitored Contacts section
- **Note**: Requires QR code scan on first run (session persisted in `.whatsapp_session`)

### 3. LinkedIn Watcher
- **Source**: LinkedIn notifications (via requests/LinkedIn API)
- **Trigger**: New notifications, connection requests, messages
- **Action**: Create action item in `/Needs_Action/`
- **Config**: `Company_Handbook.md` → LinkedIn section

### 4. Filesystem Watcher
- **Source**: Local drop folder (from Bronze tier)
- **Trigger**: New files created in watch folder
- **Action**: Create action item in `/Needs_Action/`
- **Config**: `.env` → WATCH_FOLDER

## Watcher Health & Recovery

### Automatic Features
- ✅ Health checks every 30 seconds (configurable)
- ✅ Auto-restart if watcher crashes
- ✅ Session persistence (WhatsApp QR code not re-scanned)
- ✅ Credential refresh (Gmail OAuth token refresh)
- ✅ Exponential backoff retry (1s → 5s → 10s → 30s)
- ✅ Dead-letter logging for failed watchers

### Manual Operations

**Check watcher status:**
```bash
python scripts/monitor_watchers.py
```

**Restart a specific watcher:**
```bash
python scripts/restart_watcher.py gmail
python scripts/restart_watcher.py whatsapp
python scripts/restart_watcher.py linkedin
```

**View watcher logs:**
```bash
tail -f logs/gmail_watcher.log
tail -f logs/whatsapp_watcher.log
tail -f logs/linkedin_watcher.log
```

## Configuration Reference

See `references/watcher-configuration.md` for detailed configuration options.

See `references/gmail-api-setup.md` for Gmail OAuth setup steps.

See `references/whatsapp-web-session.md` for WhatsApp Web authentication details.

See `references/error-recovery.md` for troubleshooting and recovery procedures.

## Integration with Approval Workflow

When watchers create action items in `/Needs_Action/`:

1. **needs-action-triage** skill processes them
2. **approval-workflow-manager** skill detects external actions
3. Creates approval request in `/Pending_Approval/`
4. Human approves → moves to `/Approved/`
5. **mcp-executor** skill executes via MCP servers

## Key Files & Scripts

- `scripts/gmail_watcher.py` - Gmail watcher implementation
- `scripts/whatsapp_watcher.py` - WhatsApp Web watcher (Playwright)
- `scripts/linkedin_watcher.py` - LinkedIn watcher implementation
- `scripts/orchestrate_watchers.py` - Main orchestrator (start this)
- `scripts/monitor_watchers.py` - Health check and status
- `scripts/restart_watcher.py` - Restart specific watcher
- `references/watcher-configuration.md` - Configuration details
- `references/gmail-api-setup.md` - Gmail OAuth setup
- `references/whatsapp-web-session.md` - WhatsApp session management
- `references/error-recovery.md` - Troubleshooting

## Important Notes

⚠️ **First Run**: WhatsApp watcher will show QR code on first run. Scan with your phone. Session is saved and won't re-ask.

⚠️ **Gmail OAuth**: Must complete OAuth flow once. Token is stored in `.env` and auto-refreshed.

⚠️ **Rate Limiting**: All watchers respect API rate limits and will back off gracefully.

✅ **24/7 Operation**: Use PM2 for production. Watchers auto-restart on crash.
