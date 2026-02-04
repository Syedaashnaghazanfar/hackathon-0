# Silver Tier AI Employee - Production Deployment Guide

**Version**: 1.0.0
**Status**: Production-ready with dry-run mode
**Prerequisites**: Bronze Tier functional, Python 3.10+, UV package manager

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Credential Setup](#credential-setup)
6. [Configuration](#configuration)
7. [Running the System](#running-the-system)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)
10. [Production Checklist](#production-checklist)

---

## Quick Start

**5-Minute Setup (Dry-Run Mode)**:

```bash
# 1. Install dependencies
cd My_AI_Employee
uv sync

# 2. Copy environment template
cp .env.example .env

# 3. Ensure DRY_RUN=true in .env (safe testing)

# 4. Initialize vault structure
uv run python scripts/setup/initialize_vault.py

# 5. Run security validation
uv run python scripts/validate/validate_silver_tier.py

# 6. Start all services with PM2
npm install pm2 -g
pm2 start ecosystem.config.js

# 7. Monitor logs
pm2 logs

# 8. Check dashboard
cat AI_Employee_Vault/Dashboard.md
```

---

## Architecture Overview

Silver Tier implements a **multi-channel AI employee** with human-in-the-loop approval workflow:

```
┌─────────────────────────────────────────────────────────────┐
│  PERCEPTION (Watchers)                                      │
│  - Gmail: Monitors inbox for important/unread emails        │
│  - WhatsApp: Monitors WhatsApp Web for messages             │
│  - LinkedIn: Monitors notifications and messages            │
│  - Filesystem: Bronze tier file drop folder                 │
│  → Creates action items in /Needs_Action/                   │
└─────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│  REASONING (Triage)                                          │
│  - Claude Code skill: needs-action-triage                   │
│  - Classifies actions: auto-approve vs require-approval     │
│  - Generates execution plans with risk assessment           │
│  → Routes to /Pending_Approval/ or /Approved/               │
└─────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│  APPROVAL (Human-in-the-Loop)                                │
│  - Claude Code skill: approval-workflow-manager             │
│  - Human reviews risk assessment in Obsidian vault          │
│  - Manual file move to /Approved/ or /Rejected/             │
│  → Approved actions queued for execution                    │
└─────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│  ACTION (Orchestrator + MCP Servers)                         │
│  - Orchestrator watches /Approved/ folder                   │
│  - MCP servers: email (Gmail), LinkedIn, WhatsApp           │
│  - Retry logic with exponential backoff (1s, 2s, 4s)        │
│  → Moves to /Done/ (success) or /Failed/ (error)            │
└─────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│  AUDIT & MONITORING                                          │
│  - Audit logs: /Logs/YYYY-MM-DD.json (credential-sanitized) │
│  - Dashboard: Real-time stats in Dashboard.md               │
│  - PM2: Auto-restart, heartbeat logging, health monitoring  │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### System Requirements

- **OS**: Linux, macOS, Windows (WSL2 recommended)
- **Python**: 3.10 or higher
- **Node.js**: 16+ (for PM2 process manager)
- **UV**: Python package manager ([install guide](https://github.com/astral-sh/uv))
- **PM2**: Process manager (`npm install pm2 -g`)

### External Accounts

- **Gmail Account**: For email monitoring and sending
- **LinkedIn Account**: For LinkedIn post monitoring and publishing
- **WhatsApp Account**: For WhatsApp Web message monitoring

### Bronze Tier

Silver Tier builds on Bronze Tier foundations. Ensure Bronze Tier is functional:

```bash
# Test Bronze tier
uv run python -m pytest tests/
```

---

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd My_AI_Employee
```

### 2. Install Python Dependencies

```bash
cd My_AI_Employee
uv sync
```

This installs:
- `fastmcp` - MCP server framework
- `playwright` - WhatsApp Web automation
- `google-api-python-client` - Gmail API
- `google-auth-oauthlib` - Gmail OAuth2
- `requests` - LinkedIn API
- All Bronze tier dependencies

### 3. Install Playwright Browsers

```bash
playwright install chromium
```

### 4. Install PM2 (Process Manager)

```bash
npm install pm2 -g
```

---

## Credential Setup

### Gmail (Email Sending)

**Steps**:

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create new project or select existing
   - Enable Gmail API

2. **Create OAuth2 Credentials**:
   - Create OAuth 2.0 Client ID
   - Application type: **Desktop application**
   - Download JSON as `credentials.json`
   - Save to `My_AI_Employee/credentials.json`

3. **Run OAuth Setup**:
   ```bash
   uv run python scripts/setup/setup_gmail_oauth.py
   ```
   - Browser opens for OAuth consent
   - Grant permissions to Gmail API
   - `token.json` saved automatically

4. **Verify Connection**:
   ```bash
   uv run python scripts/debug/debug_gmail.py
   ```

### LinkedIn (Post Publishing)

**Steps**:

1. **Create LinkedIn App**:
   - Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
   - Create app with appropriate permissions
   - Add redirect URL: `http://localhost:8000/callback`
   - Note Client ID and Client Secret

2. **Run OAuth Setup**:
   ```bash
   uv run python scripts/setup/linkedin_oauth2_setup.py
   ```
   - Follow prompts to authorize
   - Access token and Person URN saved to `.env`

3. **Verify Connection**:
   ```bash
   uv run python scripts/debug/debug_linkedin.py
   ```

⚠️ **Note**: LinkedIn tokens expire after 60 days. Re-run setup before expiration.

### WhatsApp (Message Monitoring)

**Steps**:

1. **Run QR Code Setup**:
   ```bash
   uv run python scripts/setup/whatsapp_auth.py
   ```
   - Browser opens with WhatsApp Web QR code
   - Scan QR with WhatsApp mobile app
   - Session saved to `.whatsapp_session/`

2. **Verify Session**:
   ```bash
   uv run python scripts/debug/debug_whatsapp.py
   ```

⚠️ **Note**: Session expires every ~2 weeks. Re-run setup before expiration.

---

## Configuration

### Environment Variables (.env)

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Critical Settings**:

```bash
# Vault Configuration
VAULT_ROOT=AI_Employee_Vault

# Gmail MCP Server
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.modify

# LinkedIn MCP Server
LINKEDIN_ACCESS_TOKEN=<filled-by-setup-script>
LINKEDIN_PERSON_URN=<filled-by-setup-script>

# WhatsApp Browser Automation
WHATSAPP_SESSION_DIR=.whatsapp_session
WHATSAPP_CDP_PORT=9222

# Global Settings
DRY_RUN=true              # HIGHLY RECOMMENDED for testing
LOG_LEVEL=INFO            # DEBUG | INFO | WARNING | ERROR
CHECK_INTERVAL=60         # Watcher polling interval (seconds)
ORCHESTRATOR_CHECK_INTERVAL=10  # Orchestrator polling (seconds)
```

### Company Handbook (Approval Rules)

Edit `AI_Employee_Vault/Company_Handbook.md` to configure approval thresholds:

```markdown
## 6. Approval Thresholds

### 6.3 Auto-Approve Actions
- Dashboard updates and vault operations
- Reading emails/messages (no sending)
- Internal triage and planning

### 6.4 Require-Approval Actions
- Sending emails to ANY recipient
- Publishing LinkedIn posts
- Sending WhatsApp messages
- All browser automation (payments, forms, clicks)

### 6.5 Exceptions
- Pre-approved contacts (configure list)
- Whitelisted keywords/patterns
```

---

## Running the System

### Option 1: PM2 Orchestration (Recommended)

Start all services with auto-restart and monitoring:

```bash
# Start all watchers + orchestrator
pm2 start ecosystem.config.js

# Monitor logs
pm2 logs

# Check process status
pm2 status

# Stop all services
pm2 stop ecosystem.config.js

# Restart all services
pm2 restart ecosystem.config.js
```

**Configure system startup** (optional):

```bash
# Generate startup script
pm2 startup

# Save process list
pm2 save

# Now services auto-start on system reboot
```

### Option 2: Manual Start (Development)

Start components individually:

```bash
# Terminal 1: Gmail Watcher
uv run python src/my_ai_employee/run_gmail_watcher.py

# Terminal 2: WhatsApp Watcher
uv run python src/my_ai_employee/watchers/whatsapp_watcher.py

# Terminal 3: LinkedIn Watcher
uv run python src/my_ai_employee/watchers/linkedin_watcher.py

# Terminal 4: Filesystem Watcher (Bronze tier)
uv run python -m my_ai_employee.run_watcher

# Terminal 5: Orchestrator
uv run python src/my_ai_employee/orchestrator.py
```

### Option 3: Multi-Watcher CLI

Run specific watchers or all at once:

```bash
# Run all watchers (no orchestrator)
uv run python src/my_ai_employee/run_multi_watcher.py all

# Run Gmail watcher only
uv run python src/my_ai_employee/run_multi_watcher.py gmail

# Run with custom interval
uv run python src/my_ai_employee/run_multi_watcher.py all --check-interval 30
```

---

## Monitoring

### Dashboard (Real-Time Stats)

Check `AI_Employee_Vault/Dashboard.md` for real-time system status:

```bash
cat AI_Employee_Vault/Dashboard.md
```

**Dashboard sections**:
- **System Status**: Running/stopped, uptime
- **Pending Actions**: Counts for /Needs_Action/ and /Pending_Approval/
- **Recent Activity**: Last 10 actions with status emoji
- **Statistics**: Actions processed, success rate, failure count

### PM2 Monitoring

```bash
# Process status
pm2 status

# Live logs
pm2 logs

# Individual component logs
pm2 logs gmail-watcher
pm2 logs orchestrator

# Monitor resource usage
pm2 monit
```

### Audit Logs

Structured JSON logs in `/Logs/`:

```bash
# Today's logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq

# Search for specific action
cat AI_Employee_Vault/Logs/*.json | jq '.[] | select(.action_type == "send_email")'

# Count actions by type
cat AI_Employee_Vault/Logs/*.json | jq -r '.[].action_type' | sort | uniq -c
```

### Heartbeat Logs

All watchers and orchestrator log heartbeats every 60 seconds:

```bash
# Check for stale watchers (no heartbeat in 5 minutes)
pm2 logs | grep "heartbeat" | tail -20
```

---

## Troubleshooting

### Debug Scripts

Run diagnostic scripts before filing issues:

```bash
# Gmail API connection test
uv run python scripts/debug/debug_gmail.py

# LinkedIn API connection test
uv run python scripts/debug/debug_linkedin.py

# WhatsApp Web session test
uv run python scripts/debug/debug_whatsapp.py
```

### Common Issues

See `TROUBLESHOOTING.md` for detailed solutions to:

- Gmail OAuth token expired
- LinkedIn token expired (60-day limit)
- WhatsApp session expired (2-week limit)
- PM2 auto-restart loops
- Network timeout errors
- Rate limiting from APIs

### Security Validation

Check for exposed credentials:

```bash
# Scan vault and repo for API keys/tokens
uv run python scripts/validate/validate_silver_tier.py

# Expected output: "✅ No credentials found"
```

---

## Production Checklist

### Pre-Deployment

- [ ] All Bronze tier tests pass: `uv run pytest tests/`
- [ ] Security scan passes: `uv run python scripts/validate/validate_silver_tier.py`
- [ ] Gmail debug passes: `uv run python scripts/debug/debug_gmail.py`
- [ ] LinkedIn debug passes: `uv run python scripts/debug/debug_linkedin.py`
- [ ] WhatsApp debug passes: `uv run python scripts/debug/debug_whatsapp.py`
- [ ] `.env` file configured and **not committed to git**
- [ ] `credentials.json` and `token.json` **not committed to git**
- [ ] `.whatsapp_session/` **not committed to git**

### Deployment

- [ ] Install PM2 globally: `npm install pm2 -g`
- [ ] Start services: `pm2 start ecosystem.config.js`
- [ ] Configure system startup: `pm2 startup && pm2 save`
- [ ] Verify all processes running: `pm2 status`
- [ ] Check logs for errors: `pm2 logs`
- [ ] Verify dashboard updates: `cat AI_Employee_Vault/Dashboard.md`

### Post-Deployment

- [ ] Monitor logs for 24 hours: `pm2 logs`
- [ ] Verify heartbeat every 60 seconds
- [ ] Test approval flow: Create test email → approve → verify execution
- [ ] Check audit logs: `cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq`
- [ ] Verify auto-restart: `pm2 stop gmail-watcher && sleep 15 && pm2 status`

### Maintenance

- [ ] Review audit logs weekly: `cat AI_Employee_Vault/Logs/*.json | jq`
- [ ] Archive old logs (>90 days): Move to `/Logs/archive/`
- [ ] Check token expiration:
  - LinkedIn: Refresh before 60 days
  - WhatsApp: Refresh before 14 days
- [ ] Update dependencies: `uv sync --upgrade`
- [ ] Security scan monthly: `uv run python scripts/validate/validate_silver_tier.py`

---

## Support

### Documentation

- **Bronze Tier**: `README.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`
- **API Docs**: `.claude/skills/*/SKILL.md`

### Getting Help

1. Check `TROUBLESHOOTING.md` for common issues
2. Run debug scripts: `scripts/debug/debug_*.py`
3. Check audit logs: `AI_Employee_Vault/Logs/*.json`
4. Review PM2 logs: `pm2 logs`

---

## License

[Your License Here]
