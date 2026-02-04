# Silver Tier AI Employee: Quickstart Guide

**Feature**: Silver Tier AI Employee
**Date**: 2026-01-22
**Audience**: Users setting up production Silver tier deployment

This guide walks you through setting up the Silver tier AI Employee from scratch, including credential configuration, vault initialization, and production deployment.

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Bronze tier fully functional** - All Bronze tests passing, filesystem watcher working
- ✅ **Python 3.13+** installed and accessible (`python --version`)
- ✅ **UV package manager** installed globally (`uv --version`)
- ✅ **Node.js 16+** (for PM2 process manager) - `node --version`
- ✅ **Obsidian vault** exists at configured path with Dashboard.md and Company_Handbook.md
- ✅ **Git repository** with `.gitignore` configured (see Step 1)

---

## Step 1: Initial Setup

### 1.1 Clone Repository and Install Dependencies

```bash
cd My_AI_Employee
uv sync  # Install all Python dependencies from pyproject.toml
```

### 1.2 Configure .gitignore

Ensure the following are in `.gitignore` to prevent credential leaks:

```gitignore
# Credentials and secrets
.env
*.env
credentials.json
token.json

# Session persistence
.whatsapp_session/
.gmail_dedupe.json
.whatsapp_dedupe.json
.linkedin_dedupe.json

# Obsidian vault (contains sensitive logs)
AI_Employee_Vault/

# PM2 logs
.pm2/
pm2.log
```

### 1.3 Create .env File

Copy the template and fill in your credentials:

```bash
cp .env.example .env
```

`.env` structure (fill in `<PLACEHOLDER>` values later):

```bash
# Vault Configuration
VAULT_ROOT=AI_Employee_Vault

# Gmail MCP Server
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.modify

# LinkedIn MCP Server
LINKEDIN_ACCESS_TOKEN=<WILL_BE_FILLED_IN_STEP_3>
LINKEDIN_PERSON_URN=<WILL_BE_FILLED_IN_STEP_3>

# WhatsApp Browser Automation
WHATSAPP_SESSION_DIR=.whatsapp_session
WHATSAPP_CDP_PORT=9222

# Global Settings
DRY_RUN=true  # Start in dry-run mode for testing
LOG_LEVEL=INFO
CHECK_INTERVAL=60  # Watcher polling interval (seconds)

# MCP Executor
ORCHESTRATOR_CHECK_INTERVAL=10  # How often to check /Approved/ folder
```

---

## Step 2: Initialize Obsidian Vault Structure

### 2.1 Create Silver Tier Folders

Run the vault initialization script:

```bash
uv run python scripts/setup/initialize_vault.py
```

This creates:
- `/Pending_Approval/` - Approval requests awaiting human decision
- `/Approved/` - Approved actions ready for execution
- `/Rejected/` - Rejected actions (archived)
- `/Failed/` - Failed executions (dead letter queue)
- `/Logs/` - Daily audit logs (YYYY-MM-DD.json)

### 2.2 Update Company_Handbook.md

Add permission boundaries section:

```markdown
## Approval Thresholds (Silver Tier)

### Auto-Approve Actions
- Dashboard updates and vault operations
- Reading emails/messages (no sending)

### Require-Approval Actions (Default)
- Sending emails to ANY recipient
- Publishing LinkedIn posts
- Sending WhatsApp messages
- All browser automation (payments, form submissions)

### Exceptions
- Emails to pre-approved contacts: none (approve all)
- LinkedIn posts: always require approval
```

---

## Step 3: Gmail API Credentials

### 3.1 Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Create new project: "AI Employee Gmail Integration"
3. Enable Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search "Gmail API" → Enable

### 3.2 Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: **Desktop app**
4. Name: "AI Employee Local Client"
5. Download JSON → Save as `credentials.json` in project root

### 3.3 Run OAuth Setup Script

```bash
uv run python scripts/setup/setup_gmail_oauth.py
```

**What happens**:
- Script opens browser for Google consent screen
- Grant permission to "Read, send, and modify Gmail"
- OAuth callback saves `token.json` with refresh token
- Credentials automatically loaded by Gmail watcher and email MCP server

**Verify**:
```bash
uv run python scripts/debug/debug_gmail.py
# Should output: "Gmail API connection successful!"
```

---

## Step 4: LinkedIn API Credentials

### 4.1 Create LinkedIn Developer App

1. Go to https://www.linkedin.com/developers/apps
2. Click "Create app"
3. Fill in details:
   - App name: "AI Employee LinkedIn Integration"
   - LinkedIn Page: (select your page or create one)
   - App logo: Upload any image
4. Click "Create app"

### 4.2 Request API Access

1. Navigate to "Products" tab
2. Request access to: **"Share on LinkedIn"**
3. Wait for approval (usually instant for personal accounts)

### 4.3 Generate Access Token

1. Go to "Auth" tab
2. Copy **Client ID** and **Client Secret**
3. Run setup script:

```bash
uv run python scripts/setup/linkedin_oauth2_setup.py
```

**What happens**:
- Script opens browser for LinkedIn authorization
- Grant permission to post on your behalf
- Script exchanges code for access token
- Saves `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_PERSON_URN` to `.env`

**Verify**:
```bash
uv run python scripts/debug/debug_linkedin.py
# Should output: "LinkedIn API connection successful!"
```

---

## Step 5: WhatsApp Web Authentication

### 5.1 Install Playwright Browsers

```bash
uv run playwright install chromium
```

### 5.2 Authenticate WhatsApp Session

```bash
uv run python scripts/setup/whatsapp_auth.py
```

**What happens**:
- Script launches headless Chrome with WhatsApp Web
- QR code displayed in terminal
- Scan with WhatsApp mobile app (Settings > Linked Devices > Link a Device)
- Session saved to `.whatsapp_session/` directory
- Future runs reuse session (no QR scan needed)

**Verify**:
```bash
uv run python scripts/debug/debug_whatsapp.py
# Should output: "WhatsApp Web authenticated successfully!"
```

---

## Step 6: Test in Dry-Run Mode

### 6.1 Verify .env Configuration

Ensure `DRY_RUN=true` in `.env` file.

### 6.2 Start Individual Watchers (Terminal Testing)

Open 4 terminal windows:

**Terminal 1: Gmail Watcher**
```bash
uv run python -m my_ai_employee.watchers.gmail_watcher
# Should log: "Gmail watcher started, checking every 60 seconds..."
```

**Terminal 2: WhatsApp Watcher**
```bash
uv run python -m my_ai_employee.watchers.whatsapp_watcher
# Should log: "WhatsApp watcher started, monitoring WhatsApp Web..."
```

**Terminal 3: LinkedIn Watcher**
```bash
uv run python -m my_ai_employee.watchers.linkedin_watcher
# Should log: "LinkedIn watcher started, checking every 300 seconds..."
```

**Terminal 4: Orchestrator**
```bash
uv run python -m my_ai_employee.orchestrator
# Should log: "Orchestrator started, watching /Approved/ folder..."
```

### 6.3 Test End-to-End Flow

1. **Send test email** to your Gmail account with subject "TEST: Silver Tier"
2. **Wait 60 seconds** (or less) for Gmail watcher to detect
3. **Check vault**: `AI_Employee_Vault/Needs_Action/` should have new markdown file
4. **Run triage** (from Claude Code):
   ```
   /needs-action-triage
   ```
5. **Check Plans**: `AI_Employee_Vault/Plans/` should have Plan.md
6. **Check Pending_Approval**: Approval request created
7. **Approve action**: Move approval file to `/Approved/`
8. **Check logs**: `/Logs/YYYY-MM-DD.json` should have entry with `"execution_status": "success"` (dry-run logged but not sent)
9. **Check Done**: Action moved to `/Done/`

**Expected outcome**: Full workflow completes in <5 minutes, no actual email sent (dry-run mode).

---

## Step 7: Production Deployment with PM2

### 7.1 Install PM2

```bash
npm install -g pm2
```

### 7.2 Disable Dry-Run Mode

Edit `.env`:
```bash
DRY_RUN=false  # IMPORTANT: Actions will now execute for real!
```

### 7.3 Start All Processes

```bash
pm2 start ecosystem.config.js
```

**What happens**:
- PM2 starts 5 processes:
  1. `gmail-watcher`
  2. `whatsapp-watcher`
  3. `linkedin-watcher`
  4. `filesystem-watcher` (Bronze tier compatibility)
  5. `orchestrator`
- Auto-restart on crash
- Logs written to `.pm2/logs/`

### 7.4 Monitor Processes

```bash
pm2 status  # Show all process statuses
pm2 logs    # Tail all logs
pm2 logs gmail-watcher  # Tail specific process
pm2 monit   # Real-time dashboard
```

### 7.5 Configure Auto-Start on Reboot

```bash
pm2 startup
# Follow on-screen instructions to configure system service
pm2 save  # Save current process list
```

---

## Step 8: Verify Production Operations

### 8.1 Send Real Test Email

Send an email with subject "URGENT: Test Payment Invoice" to your Gmail.

**Expected behavior**:
1. Gmail watcher detects within 60 seconds
2. Action item created in `/Needs_Action/`
3. Triage classifies as `require-approval` (external action)
4. Approval request appears in `/Pending_Approval/`
5. Review risk assessment in Obsidian
6. Move to `/Approved/` to approve
7. Orchestrator executes via email MCP server
8. **Real email sent!** (verify in Gmail Sent folder)
9. Audit log entry created with sanitized credentials
10. Action archived to `/Done/`

### 8.2 Verify Audit Log

Check `/Logs/YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-01-22T15:00:00Z",
  "action_type": "send_email",
  "execution_status": "success",
  "tool_inputs_sanitized": {
    "to": "recipient@example.com",
    "subject": "Test Email",
    "body_preview": "This is a test..."
  },
  "error": null
}
```

**Verify**:
- ✅ No plaintext API keys or OAuth tokens
- ✅ Email addresses preserved (for debugging)
- ✅ Execution status is "success"

### 8.3 Test Graceful Degradation

Kill Gmail watcher:
```bash
pm2 stop gmail-watcher
```

**Expected behavior**:
- WhatsApp and LinkedIn watchers continue running
- Orchestrator continues processing approved items
- PM2 auto-restarts gmail-watcher within 60 seconds

**Verify**:
```bash
pm2 status  # gmail-watcher should show "online" again
```

---

## Step 9: Daily Operations

### 9.1 Morning Routine

1. Open Obsidian vault
2. Check `/Pending_Approval/` folder for overnight items
3. Review risk assessments
4. Move approved items to `/Approved/`
5. Move rejected items to `/Rejected/` (add `rejection_reason` to frontmatter)
6. Check Dashboard.md for statistics

### 9.2 Monitoring Commands

```bash
# Check process health
pm2 status

# View recent logs
pm2 logs --lines 50

# Check heartbeat entries (should see every 60 seconds)
grep "heartbeat" .pm2/logs/gmail-watcher-out.log

# View audit logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.'
```

### 9.3 Troubleshooting

**Gmail watcher not detecting emails**:
```bash
# Check OAuth token
uv run python scripts/debug/debug_gmail.py
# If expired, re-run: uv run python scripts/setup/setup_gmail_oauth.py
```

**WhatsApp session expired**:
```bash
# Re-authenticate
rm -rf .whatsapp_session/
uv run python scripts/setup/whatsapp_auth.py
```

**MCP server failures**:
```bash
# Check /Failed/ folder for error details
cat AI_Employee_Vault/Failed/*.md
# Review error logs
pm2 logs orchestrator --err
```

---

## Step 10: Security Checklist

Before going fully operational, verify:

- [ ] `.env` file is in `.gitignore` (run `git status` - `.env` should NOT appear)
- [ ] No credentials in vault or repository (`grep -r "sk-" AI_Employee_Vault/` returns nothing)
- [ ] Audit logs sanitize credentials (search `/Logs/*.json` for "REDACTED")
- [ ] `DRY_RUN=false` only after testing approval workflow
- [ ] Company_Handbook.md defines clear permission boundaries
- [ ] /Pending_Approval/ folder is checked daily

---

## Common Issues

### Issue: "GMAIL_CREDENTIALS_FILE not found"
**Solution**: Ensure `credentials.json` exists in project root and `.env` has correct path.

### Issue: "LinkedIn API permission denied (403)"
**Solution**: Request "Share on LinkedIn" product in LinkedIn Developer Portal, wait for approval.

### Issue: "WhatsApp Web session expired"
**Solution**: Delete `.whatsapp_session/` and re-run `uv run python scripts/setup/whatsapp_auth.py`.

### Issue: "PM2 command not found"
**Solution**: Install Node.js 16+ and run `npm install -g pm2`.

### Issue: "All actions going to /Failed/"
**Solution**: Check orchestrator logs (`pm2 logs orchestrator`), verify MCP servers are healthy (`uv run python scripts/debug/debug_mcp_health.py`).

---

## Next Steps

After successful deployment:

1. **Customize Company_Handbook.md** with your approval preferences
2. **Set up cron jobs** for daily triage (optional):
   ```bash
   # Add to crontab: Run triage every morning at 8 AM
   0 8 * * * cd /path/to/My_AI_Employee && uv run claude -p "/needs-action-triage"
   ```
3. **Monitor for 48 hours** to ensure stability
4. **Review audit logs weekly** for compliance
5. **Consider Gold tier** for advanced features (multi-agent, proactive suggestions)

---

## Support

- **Documentation**: `docs/SILVER_TIER.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **Architecture**: `specs/002-silver-tier-ai-employee/plan.md`
- **GitHub Issues**: https://github.com/your-repo/issues

