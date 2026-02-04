# Silver Tier AI Employee - Quickstart Guide

**Date**: 2026-01-15
**Feature**: Silver Tier AI Employee
**Purpose**: Setup and deployment instructions

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Bronze Tier Complete**: Filesystem watcher + Obsidian vault + Claude Code skills working
- ✅ **Python 3.13+**: Installed and available in PATH
- ✅ **uv**: Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- ✅ **Node.js 18+**: For PM2 process management (`node --version`)
- ✅ **Git**: For version control
- ✅ **Google Account**: For Gmail API access
- ✅ **LinkedIn Account**: For LinkedIn API or Playwright access
- ✅ **WhatsApp**: Mobile app for QR code scanning

---

## Installation

### 1. Install Python Dependencies

```bash
# Navigate to project root
cd /path/to/hackathon-0

# Install dependencies with uv
uv pip install -e .

# Install Playwright browsers
playwright install chromium
```

### 2. Install PM2 (Process Management)

```bash
# Install PM2 globally
npm install -g pm2

# Verify installation
pm2 --version
```

### 3. Create Environment File

```bash
# Copy example environment file
cp My_AI_Employee/.env.example My_AI_Employee/.env

# Edit with your credentials
nano My_AI_Employee/.env
```

**Required Environment Variables**:

```bash
# Gmail API
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# SMTP Fallback
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# LinkedIn API (optional, can use Playwright fallback)
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret

# System Configuration
DRY_RUN=false
VAULT_PATH=My_AI_Employee/AI_Employee_Vault
LOG_LEVEL=INFO

# Orchestrator
ORCHESTRATOR_CHECK_INTERVAL=5
ORCHESTRATOR_MAX_RETRIES=3
ORCHESTRATOR_RETRY_BACKOFF=25

# Watcher Intervals (seconds)
GMAIL_POLL_INTERVAL=60
WHATSAPP_POLL_INTERVAL=30
LINKEDIN_POLL_INTERVAL=60
```

---

## Setup: Gmail API

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "AI Employee"
3. Enable Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 2. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "AI Employee Gmail"
5. Download credentials as `credentials.json`
6. Move to project root: `mv ~/Downloads/credentials.json My_AI_Employee/credentials.json`

### 3. Authenticate

```bash
# Run Gmail watcher once to authenticate
python My_AI_Employee/watchers/gmail_watcher.py

# Browser opens for OAuth consent
# Grant permissions
# Token saved to token.json
```

**Scopes Granted**:
- `https://www.googleapis.com/auth/gmail.send` - Send emails
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails

---

## Setup: SMTP Fallback

### 1. Generate App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification (if not already enabled)
3. Go to "App passwords"
4. Generate password for "Mail" on "Other (Custom name)"
5. Name: "AI Employee SMTP"
6. Copy 16-character password

### 2. Update .env

```bash
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop  # 16-char app password
```

---

## Setup: LinkedIn

### Option A: LinkedIn API (Recommended)

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create new app
3. Get Client ID and Client Secret
4. Set redirect URI: `http://localhost:8000/callback`
5. Request scopes: `w_member_social`, `r_liteprofile`
6. Update `.env`:
   ```bash
   LINKEDIN_CLIENT_ID=your-client-id
   LINKEDIN_CLIENT_SECRET=your-client-secret
   ```

### Option B: Playwright Fallback

If LinkedIn API is unavailable, Playwright will be used automatically.

**First-time setup**:
```bash
# Run LinkedIn watcher once to authenticate
python My_AI_Employee/watchers/linkedin_watcher.py

# Browser opens to LinkedIn
# Log in manually
# Session saved to linkedin_session.json
```

---

## Setup: WhatsApp Web

### 1. Initial QR Code Scan

```bash
# Run WhatsApp watcher once to authenticate
python My_AI_Employee/watchers/whatsapp_watcher.py

# Browser opens to WhatsApp Web
# Scan QR code with your phone:
#   1. Open WhatsApp on phone
#   2. Tap Menu (⋮) > Linked Devices
#   3. Tap "Link a Device"
#   4. Scan QR code on screen
# Session saved to whatsapp_session.json
```

### 2. Session Persistence

- Session lasts ~7 days
- System notifies when session expires
- Re-run watcher to refresh session

---

## Setup: Vault Folders

### 1. Create Silver Tier Folders

```bash
# Navigate to vault
cd My_AI_Employee/AI_Employee_Vault

# Create Silver tier folders
mkdir -p Pending_Approval Approved Rejected Failed Logs

# Verify structure
ls -la
# Should see: Inbox/ Needs_Action/ Pending_Approval/ Approved/ Rejected/ Failed/ Done/ Plans/ Logs/ Dashboard.md Company_Handbook.md
```

### 2. Update Company_Handbook.md

Add approval rules to `Company_Handbook.md`:

```markdown
## Approval Thresholds

### Auto-Approve (No Human Review)
- Emails to known contacts (in contact list)
- Recurring payments < $50
- Scheduled LinkedIn posts (pre-approved content)

### Require Approval (Human Review)
- All external communications to new contacts
- Payments > $50
- Any commitments > 1 day
- Policy changes
- Banking/financial actions

### Never Auto-Retry (Always Require Fresh Approval)
- Banking/payment actions
- Legal/compliance actions
- Account deletions
```

---

## Deployment

### Option A: PM2 (Recommended for Production)

#### 1. Create PM2 Configuration

File: `My_AI_Employee/ecosystem.config.js`

```javascript
module.exports = {
  apps: [
    {
      name: 'gmail-watcher',
      script: 'python',
      args: 'My_AI_Employee/watchers/gmail_watcher.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: 'logs/gmail-watcher-error.log',
      out_file: 'logs/gmail-watcher-out.log'
    },
    {
      name: 'whatsapp-watcher',
      script: 'python',
      args: 'My_AI_Employee/watchers/whatsapp_watcher.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'linkedin-watcher',
      script: 'python',
      args: 'My_AI_Employee/watchers/linkedin_watcher.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'orchestrator',
      script: 'python',
      args: 'My_AI_Employee/orchestrator.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
```

#### 2. Start All Processes

```bash
# Start all watchers and orchestrator
pm2 start My_AI_Employee/ecosystem.config.js

# Check status
pm2 status

# View logs
pm2 logs

# Monitor in real-time
pm2 monit
```

#### 3. Configure Startup

```bash
# Save PM2 configuration
pm2 save

# Generate startup script
pm2 startup

# Follow instructions to enable startup on boot
```

### Option B: Unified Runner (Development)

```bash
# Run all watchers with orchestration
uv run python run_watcher.py --watcher all

# Monitors all watchers and handles health checks
# Checks every 30-60 seconds per watcher
```

---

## Testing

### 1. Test Bronze Tier (Baseline)

```bash
# Drop test file in Inbox
echo "Test request" > My_AI_Employee/test_watch_folder/test.txt

# Verify action item created in Needs_Action/
ls My_AI_Employee/AI_Employee_Vault/Needs_Action/

# Process with Claude Code
# Verify item moved to Done/
```

### 2. Test Gmail Watcher

```bash
# Send test email to your Gmail
# Subject: "Test - Project Update Request"
# Body: "Can you provide an update on Project A?"

# Wait 2 minutes
# Check Needs_Action/ for new item
ls -la My_AI_Employee/AI_Employee_Vault/Needs_Action/

# Should see: YYYYMMDD_HHMMSS_microseconds_email_subject.md
```

### 3. Test Approval Workflow

```bash
# Process action item with Claude Code
# Skill: needs-action-triage

# Check Pending_Approval/ for approval request
ls -la My_AI_Employee/AI_Employee_Vault/Pending_Approval/

# Approve by moving to Approved/
mv My_AI_Employee/AI_Employee_Vault/Pending_Approval/YYYYMMDD_*.md \
   My_AI_Employee/AI_Employee_Vault/Approved/

# Wait 10 seconds for orchestrator to execute
# Check Done/ for execution record
ls -la My_AI_Employee/AI_Employee_Vault/Done/

# Check audit log
cat My_AI_Employee/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

### 4. Test WhatsApp Watcher

```bash
# Send WhatsApp message to yourself containing "urgent"
# Example: "Urgent: Need invoice for Project A"

# Wait 2 minutes
# Check Needs_Action/ for new item
ls -la My_AI_Employee/AI_Employee_Vault/Needs_Action/

# Should see: YYYYMMDD_HHMMSS_microseconds_whatsapp_message.md
```

### 5. Test LinkedIn Post

```bash
# Create scheduled post in Company_Handbook.md
# Schedule: Mondays at 9:00 AM

# Wait for scheduled time
# Check Pending_Approval/ for draft post
ls -la My_AI_Employee/AI_Employee_Vault/Pending_Approval/

# Approve and verify post on LinkedIn
```

---

## Monitoring

### PM2 Dashboard

```bash
# Real-time monitoring
pm2 monit

# Process status
pm2 status

# Logs for specific process
pm2 logs gmail-watcher
pm2 logs orchestrator

# Restart specific process
pm2 restart gmail-watcher

# Stop all processes
pm2 stop all

# Delete all processes
pm2 delete all
```

### Audit Logs

```bash
# View today's audit log
cat My_AI_Employee/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq

# Count actions today
cat My_AI_Employee/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | wc -l

# Filter by action type
cat My_AI_Employee/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq 'select(.action_type == "send_email")'

# Check for failures
cat My_AI_Employee/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq 'select(.execution_status == "failed")'
```

### Dashboard

```bash
# View Dashboard
cat My_AI_Employee/AI_Employee_Vault/Dashboard.md

# Or open in Obsidian
open -a Obsidian My_AI_Employee/AI_Employee_Vault/
```

---

## Troubleshooting

### Gmail API Issues

**Problem**: "Authentication failed"
**Solution**:
```bash
# Delete token and re-authenticate
rm My_AI_Employee/token.json
python My_AI_Employee/watchers/gmail_watcher.py
```

**Problem**: "Rate limit exceeded"
**Solution**: Wait for quota reset (midnight Pacific Time) or upgrade to paid tier

### WhatsApp Session Expired

**Problem**: "WhatsApp session expired"
**Solution**:
```bash
# Delete session and re-scan QR code
rm My_AI_Employee/whatsapp_session.json
python My_AI_Employee/watchers/whatsapp_watcher.py
```

### Orchestrator Not Executing

**Problem**: Approved items not being executed
**Solution**:
```bash
# Check orchestrator logs
pm2 logs orchestrator

# Verify orchestrator is running
pm2 status orchestrator

# Restart orchestrator
pm2 restart orchestrator
```

### Duplicate Action Items

**Problem**: Same email creates multiple action items
**Solution**: Check duplicate detection in watcher logs. Verify `source_id` and `content_hash` are being set correctly.

---

## Security Checklist

- [ ] `.env` file is gitignored
- [ ] `credentials.json` is gitignored
- [ ] `token.json` is gitignored
- [ ] `*_session.json` files are gitignored
- [ ] Audit logs sanitize credentials
- [ ] DRY_RUN mode tested before production
- [ ] PM2 logs don't contain secrets
- [ ] Company_Handbook.md defines approval thresholds
- [ ] Payment actions never auto-retry

---

## Performance Tuning

### Watcher Intervals

Adjust polling intervals in `.env`:

```bash
# More frequent (higher load)
GMAIL_POLL_INTERVAL=30
WHATSAPP_POLL_INTERVAL=15
LINKEDIN_POLL_INTERVAL=30

# Less frequent (lower load)
GMAIL_POLL_INTERVAL=120
WHATSAPP_POLL_INTERVAL=60
LINKEDIN_POLL_INTERVAL=120
```

### Orchestrator Tuning

```bash
# Faster execution (higher load)
ORCHESTRATOR_CHECK_INTERVAL=2

# Slower execution (lower load)
ORCHESTRATOR_CHECK_INTERVAL=10
```

---

## Backup & Recovery

### Backup Vault

```bash
# Create backup
tar -czf vault-backup-$(date +%Y%m%d).tar.gz My_AI_Employee/AI_Employee_Vault/

# Restore backup
tar -xzf vault-backup-YYYYMMDD.tar.gz
```

### Backup Credentials

```bash
# Backup credentials (store securely, NOT in git)
tar -czf credentials-backup-$(date +%Y%m%d).tar.gz \
  My_AI_Employee/.env \
  My_AI_Employee/credentials.json \
  My_AI_Employee/token.json \
  My_AI_Employee/*_session.json
```

---

## Next Steps

After successful setup:

1. **Run End-to-End Test**: Test all three user stories (P1, P2, P3)
2. **Configure Company_Handbook.md**: Add your business rules and preferences
3. **Set Up Monitoring**: Configure alerts for critical errors
4. **Review Audit Logs**: Verify all actions are being logged correctly
5. **Optimize Performance**: Adjust polling intervals based on usage
6. **Document Custom Rules**: Add any custom approval rules to Company_Handbook.md

---

## Support

- **Documentation**: See `specs/002-silver-ai-employee/` for detailed specs
- **Issues**: Check PM2 logs and audit logs for errors
- **Claude Code Skills**: Use existing skills for vault operations
- **Context7 MCP**: Query documentation during implementation

---

**Status**: Ready for deployment
**Estimated Setup Time**: 2-3 hours (including authentication)
**Prerequisites**: Bronze tier complete, all accounts created
