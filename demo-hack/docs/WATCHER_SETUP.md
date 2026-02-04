# Watcher Setup Documentation

**Silver Tier AI Employee - Perception Layer**

This document describes how to set up and configure all watchers (Gmail, WhatsApp, LinkedIn) for the Silver Tier AI Employee system. Watchers are the Perception Layer that monitors communication channels and creates action items.

---

## Overview

The Silver Tier AI Employee uses three watchers:

1. **Gmail Watcher** (`gmail_watcher.py`) - OAuth2 email monitoring
2. **WhatsApp Watcher** (`whatsapp_watcher.py`) - CDP browser automation
3. **LinkedIn Watcher** (`linkedin_watcher.py`) - REST API v2 monitoring

All watchers follow these principles:
- **Continuous monitoring**: Poll channels at regular intervals
- **Duplicate prevention**: DedupeTracker prevents duplicate action items
- **Graceful degradation**: One watcher fails, others continue
- **Health monitoring**: Status reported to Dashboard.md
- **Audit logging**: All detected events logged

---

## Gmail Watcher Setup

**File**: `My_AI_Employee/watchers/gmail_watcher.py`
**Authentication**: OAuth2 (credentials.json + token.json)
**Polling Interval**: 60 seconds (configurable)

### Prerequisites

1. **Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Gmail API

2. **OAuth2 Credentials**:
   - Go to APIs & Services → Credentials
   - Create OAuth 2.0 Client ID
   - Application type: Desktop app
   - Download credentials as `credentials.json`

### Step 1: Download Credentials

```bash
# Place credentials.json in My_AI_Employee/
cd My_AI_Employee
# Copy your downloaded credentials.json here
```

### Step 2: Configure Environment Variables

Edit `.env`:
```bash
# Gmail Configuration
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.modify
GMAIL_CHECK_INTERVAL=60
```

**Configuration Options**:
- `GMAIL_CREDENTIALS_FILE`: Path to OAuth2 credentials file
- `GMAIL_TOKEN_FILE`: Path to store access/refresh tokens
- `GMAIL_SCOPES`: Gmail API scopes (modify = read + send)
- `GMAIL_CHECK_INTERVAL`: Polling interval in seconds (default: 60)

### Step 3: Run OAuth2 Authentication

```bash
cd My_AI_Employee
python scripts/setup/setup_gmail_oauth.py
```

**What happens**:
1. Browser opens to Google OAuth consent screen
2. You log in with your Gmail account
3. You grant permissions to the app
4. Script saves `token.json` with access/refresh tokens
5. Tokens auto-refresh when expired

**Expected output**:
```
Opening browser for authentication...
Please log in and grant permissions.
Authentication successful!
Token saved to: token.json
User email: your.email@gmail.com
```

### Step 4: Test Gmail API Connection

```bash
python scripts/debug/debug_gmail.py
```

**Expected output**:
```
✅ Gmail API connection successful
User email: your.email@gmail.com
Inbox messages: 42
Unread messages: 5
```

### Step 5: Start Gmail Watcher

```bash
# Start watcher
python run_watcher.py --watcher gmail

# Or with custom check interval
GMAIL_CHECK_INTERVAL=30 python run_watcher.py --watcher gmail
```

**Expected output**:
```
2026-01-21 10:00:00 - INFO - Starting Gmail watcher
2026-01-21 10:00:00 - INFO - Authenticated as: your.email@gmail.com
2026-01-21 10:00:00 - INFO - Monitoring inbox every 60 seconds
2026-01-21 10:00:00 - INFO - Checking for new messages...
2026-01-21 10:00:01 - INFO - Found 0 new messages
```

### Gmail Watcher Configuration

**What it monitors**:
- Unread emails in INBOX
- Emails from known contacts (in Company_Handbook.md)
- Emails with important keywords (configurable)

**What it creates**:
- Action items in `Needs_Action/` folder
- Filename: `YYYYMMDD_HHMMSS_MICROSECONDS_email_sender_name.md`
- Includes: sender, subject, body, timestamp

**Duplicate prevention**:
- Uses Gmail message ID for deduplication
- Stores processed message IDs in `.gmail_dedupe.json`
- Prevents creating duplicate action items

### Troubleshooting Gmail Watcher

**Problem**: `401 Unauthorized`
**Solution**:
```bash
# Re-authenticate
python scripts/setup/setup_gmail_oauth.py
```

**Problem**: `403 Forbidden`
**Solution**: Check OAuth scopes in Google Cloud Console

**Problem**: No emails detected
**Solution**:
```bash
# Check token validity
python scripts/debug/debug_gmail.py

# Check watcher logs
tail -f logs/gmail_watcher.log

# Verify GMAIL_CHECK_INTERVAL is set
echo $GMAIL_CHECK_INTERVAL
```

**Problem**: Token expired
**Solution**: Tokens auto-refresh, but if issues persist:
```bash
# Delete old token and re-authenticate
rm token.json
python scripts/setup/setup_gmail_oauth.py
```

---

## WhatsApp Watcher Setup

**File**: `My_AI_Employee/watchers/whatsapp_watcher.py`
**Authentication**: QR code scan (WhatsApp Web)
**Polling Interval**: 30 seconds (configurable)
**Architecture**: CDP (Chrome DevTools Protocol)

### Prerequisites

1. **WhatsApp Account**: Active WhatsApp account on your phone
2. **Chromium Browser**: Installed via Playwright
3. **Phone Access**: To scan QR code

### Step 1: Install Playwright Browsers

```bash
cd My_AI_Employee
playwright install chromium
```

### Step 2: Configure Environment Variables

Edit `.env`:
```bash
# WhatsApp Configuration
WHATSAPP_SESSION_DIR=.whatsapp_session
WHATSAPP_CDP_PORT=9222
WHATSAPP_CHECK_INTERVAL=30
```

**Configuration Options**:
- `WHATSAPP_SESSION_DIR`: Directory to store browser session
- `WHATSAPP_CDP_PORT`: CDP remote debugging port (default: 9222)
- `WHATSAPP_CHECK_INTERVAL`: Polling interval in seconds (default: 30)

### Step 3: Start WhatsApp Watcher (First Time)

```bash
cd My_AI_Employee
python run_watcher.py --watcher whatsapp
```

**What happens**:
1. Browser opens to WhatsApp Web
2. QR code appears
3. You scan QR code with your phone:
   - Open WhatsApp on phone
   - Go to Settings → Linked Devices
   - Tap "Link a Device"
   - Scan QR code
4. Session saves to `.whatsapp_session/` directory
5. Watcher starts monitoring messages

**Expected output**:
```
2026-01-21 10:00:00 - INFO - Starting WhatsApp watcher
2026-01-21 10:00:00 - INFO - Launching browser with CDP on port 9222
2026-01-21 10:00:05 - INFO - Waiting for QR code scan...
2026-01-21 10:00:30 - INFO - Session authenticated successfully
2026-01-21 10:00:30 - INFO - Monitoring messages every 30 seconds
2026-01-21 10:00:30 - INFO - Checking for new messages...
2026-01-21 10:00:31 - INFO - Found 0 unread messages
```

### Step 4: Verify Session Persistence

**Important**: Leave the browser window open! The watcher and MCP server share this browser session via CDP.

```bash
# Check session directory exists
ls -la .whatsapp_session/

# Expected contents:
# - Default/ (browser profile)
# - IndexedDB/
# - Service Worker/
# - Cache/
```

### Step 5: Test WhatsApp Detection

Send yourself a test message with urgent keywords:
```
urgent: test message
```

Within 30 seconds, check for action item:
```bash
ls -la AI_Employee_Vault/Needs_Action/
# Should see: YYYYMMDD_HHMMSS_whatsapp_contact.md
```

### WhatsApp Watcher Configuration

**What it monitors**:
- Unread messages only
- Messages with urgent keywords: "urgent", "help", "asap", "invoice", "payment"
- All contacts (no filtering)

**What it creates**:
- Action items in `Needs_Action/` folder
- Filename: `YYYYMMDD_HHMMSS_MICROSECONDS_whatsapp_contact_name.md`
- Includes: contact, message, urgent keywords, timestamp
- Priority: High (if urgent keywords detected)

**Duplicate prevention**:
- Uses message timestamp + contact for deduplication
- Stores processed message IDs in `.whatsapp_dedupe.json`
- Prevents creating duplicate action items

### CDP Architecture

**How it works**:
```
Watcher (Host)
  ↓ Launches browser with --remote-debugging-port=9222
  ↓ Session saved to .whatsapp_session/ directory
  ↓
MCP Server (Guest)
  ↓ Connects via CDP to watcher's browser
  ↓ Uses existing session (no second QR code scan)
  ↓ Sends messages through shared browser
```

**Benefits**:
- ✅ Scan QR code once (not every time)
- ✅ Full browser profile persistence
- ✅ No file lock issues
- ✅ More reliable than JSON storage_state

### Troubleshooting WhatsApp Watcher

**Problem**: Session expired
**Solution**:
```bash
# Restart watcher and scan QR code again
python run_watcher.py --watcher whatsapp
# Scan QR code in browser
```

**Problem**: Browser crashes
**Solution**:
```bash
# Kill any hanging browser processes
pkill -f chromium

# Delete session and restart
rm -rf .whatsapp_session/
python run_watcher.py --watcher whatsapp
```

**Problem**: No messages detected
**Solution**:
```bash
# Check watcher logs
tail -f logs/whatsapp_watcher.log

# Verify browser is open
ps aux | grep chromium

# Check CDP port
lsof -i :9222
```

**Problem**: MCP server can't connect
**Solution**:
```bash
# Ensure watcher is running first
python run_watcher.py --watcher whatsapp

# Then start orchestrator
python orchestrator.py

# Check CDP connection
curl http://localhost:9222/json
```

---

## LinkedIn Watcher Setup

**File**: `My_AI_Employee/watchers/linkedin_watcher.py`
**Authentication**: OAuth2 (REST API v2)
**Polling Interval**: 300 seconds (5 minutes, configurable)

### Prerequisites

1. **LinkedIn Account**: Active LinkedIn account
2. **LinkedIn Developer App**: Create app at [LinkedIn Developers](https://www.linkedin.com/developers/)
3. **API Access**: Request "Share on LinkedIn" product

### Step 1: Create LinkedIn Developer App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Click **Create App**
3. Fill in:
   - App name: `AI Employee`
   - LinkedIn Page: Select or create a company page
   - App logo: Upload any logo
   - Legal agreement: Check the box
4. Click **Create app**

### Step 2: Request API Access

1. Go to **Products** tab
2. Request access to:
   - **Share on LinkedIn** (for posting)
   - **Sign In with LinkedIn using OpenID Connect**
3. Wait for approval (usually instant for basic access)

### Step 3: Configure OAuth2 Settings

1. Go to **Auth** tab
2. Copy:
   - **Client ID**
   - **Client Secret** (click eye icon to reveal)
3. Add Redirect URL: `http://localhost:8080/linkedin/callback`
4. Click **Update**

### Step 4: Configure Environment Variables

Edit `.env`:
```bash
# LinkedIn REST API Configuration
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:8080/linkedin/callback
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_PERSON_URN=
LINKEDIN_API_VERSION=202601
LINKEDIN_CHECK_INTERVAL=300
```

**Configuration Options**:
- `LINKEDIN_CLIENT_ID`: OAuth2 client ID from LinkedIn app
- `LINKEDIN_CLIENT_SECRET`: OAuth2 client secret
- `LINKEDIN_REDIRECT_URI`: OAuth2 redirect URI (must match app settings)
- `LINKEDIN_ACCESS_TOKEN`: Access token (populated by setup script)
- `LINKEDIN_PERSON_URN`: Person URN (populated by setup script)
- `LINKEDIN_API_VERSION`: API version (default: 202601)
- `LINKEDIN_CHECK_INTERVAL`: Polling interval in seconds (default: 300)

### Step 5: Run OAuth2 Authentication

```bash
cd My_AI_Employee
python scripts/linkedin_oauth2_setup.py
```

**What happens**:
1. Browser opens to LinkedIn authorization page
2. You log in and approve the app
3. Script exchanges authorization code for access token
4. Script retrieves your person URN
5. Credentials saved to `.env`

**Expected output**:
```
Opening browser for LinkedIn authorization...
Please log in and approve the app.
Authorization successful!
Access token saved to .env
Person URN: urn:li:person:abc123
```

### Step 6: Test LinkedIn API Connection

```bash
python scripts/test_linkedin_api.py
```

**Expected output**:
```
✅ All tests passed!
Your LinkedIn REST API is configured correctly.
User ID: abc123
Name: Your Name
Email: your.email@example.com
```

### Step 7: Start LinkedIn Watcher

```bash
# Start watcher
python run_watcher.py --watcher linkedin

# Or with custom check interval
LINKEDIN_CHECK_INTERVAL=600 python run_watcher.py --watcher linkedin
```

**Expected output**:
```
2026-01-21 10:00:00 - INFO - Starting LinkedIn watcher
2026-01-21 10:00:00 - INFO - Authenticated as: Your Name
2026-01-21 10:00:00 - INFO - Monitoring LinkedIn every 300 seconds
2026-01-21 10:00:00 - INFO - Checking for scheduled posts...
2026-01-21 10:00:01 - INFO - No posts scheduled for today
```

### LinkedIn Watcher Configuration

**What it monitors**:
- Scheduled post times (defined in Company_Handbook.md)
- LinkedIn notifications (optional)
- Connection requests (optional)

**What it creates**:
- Draft LinkedIn posts in `Needs_Action/` folder
- Filename: `YYYYMMDD_HHMMSS_linkedin_post.md`
- Includes: post text, hashtags, visibility, timestamp

**Scheduling**:
Define posting schedule in `Company_Handbook.md`:
```markdown
## LinkedIn Posting Schedule

- **Days**: Monday, Thursday
- **Time**: 9:00 AM
- **Content**: Recent business activities from vault
- **Hashtags**: #business #technology #innovation
```

### Token Expiration

LinkedIn access tokens expire after **60 days**.

**When token expires**:
1. You'll see `401 Unauthorized` errors
2. Run: `python scripts/linkedin_oauth2_setup.py`
3. Re-authorize the app
4. New token saved to `.env`

**Set a reminder**: Add calendar reminder to refresh tokens every 60 days.

### Troubleshooting LinkedIn Watcher

**Problem**: `401 Unauthorized`
**Solution**:
```bash
# Re-authenticate
python scripts/linkedin_oauth2_setup.py
```

**Problem**: `403 Forbidden`
**Solution**: Check app permissions at [LinkedIn Developers](https://www.linkedin.com/developers/)

**Problem**: `429 Rate Limited`
**Solution**: Wait for rate limit window to reset (automatic retry)

**Problem**: No posts created
**Solution**:
```bash
# Check watcher logs
tail -f logs/linkedin_watcher.log

# Verify schedule in Company_Handbook.md
cat AI_Employee_Vault/Company_Handbook.md | grep -A 5 "LinkedIn"

# Check current day/time matches schedule
date
```

---

## Multi-Watcher Orchestration

### Running All Watchers Simultaneously

```bash
cd My_AI_Employee
python run_watcher.py --watcher all
```

**What happens**:
1. Launches Gmail watcher in thread 1
2. Launches WhatsApp watcher in thread 2
3. Launches LinkedIn watcher in thread 3
4. Health monitoring enabled
5. Graceful shutdown on Ctrl+C

**Expected output**:
```
2026-01-21 10:00:00 - INFO - Starting multi-watcher orchestration
2026-01-21 10:00:00 - INFO - Launching Gmail watcher (thread 1)
2026-01-21 10:00:00 - INFO - Launching WhatsApp watcher (thread 2)
2026-01-21 10:00:00 - INFO - Launching LinkedIn watcher (thread 3)
2026-01-21 10:00:05 - INFO - All watchers started successfully
2026-01-21 10:00:05 - INFO - Health monitoring enabled
2026-01-21 10:00:05 - INFO - Press Ctrl+C to stop all watchers
```

### Health Monitoring

The multi-watcher runner monitors watcher health:

**Health checks**:
- Every 60 seconds
- Checks if watcher thread is alive
- Checks if watcher is responding
- Updates Dashboard.md with status

**Auto-restart**:
- If watcher crashes, automatically restarts
- Max 3 restart attempts
- After 3 failures, stops and notifies user

### Graceful Shutdown

Press Ctrl+C to stop all watchers:

```
^C
2026-01-21 10:30:00 - INFO - Shutdown signal received
2026-01-21 10:30:00 - INFO - Stopping Gmail watcher...
2026-01-21 10:30:01 - INFO - Gmail watcher stopped
2026-01-21 10:30:01 - INFO - Stopping WhatsApp watcher...
2026-01-21 10:30:02 - INFO - WhatsApp watcher stopped
2026-01-21 10:30:02 - INFO - Stopping LinkedIn watcher...
2026-01-21 10:30:03 - INFO - LinkedIn watcher stopped
2026-01-21 10:30:03 - INFO - All watchers stopped gracefully
```

---

## PM2 Process Management

### Setup PM2

```bash
# Install PM2 globally
npm install -g pm2

# Start all watchers and orchestrator
cd My_AI_Employee
pm2 start ecosystem.config.js
```

### PM2 Configuration

`ecosystem.config.js`:
```javascript
module.exports = {
  apps: [
    {
      name: 'watchers',
      script: 'run_watcher.py',
      args: '--watcher all',
      interpreter: 'python',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M'
    },
    {
      name: 'orchestrator',
      script: 'orchestrator.py',
      interpreter: 'python',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M'
    }
  ]
};
```

### PM2 Commands

```bash
# Start all processes
pm2 start ecosystem.config.js

# View status
pm2 status

# View logs
pm2 logs

# View logs for specific process
pm2 logs watchers
pm2 logs orchestrator

# Restart all
pm2 restart all

# Restart specific process
pm2 restart watchers

# Stop all
pm2 stop all

# Delete all
pm2 delete all

# Monitor in real-time
pm2 monit
```

---

## Monitoring and Maintenance

### Check Dashboard

View real-time watcher status:
```bash
cat AI_Employee_Vault/Dashboard.md
```

**Expected content**:
```markdown
## Watcher Health

- **Gmail**: ✅ Running (last check: 10:29:55)
- **WhatsApp**: ✅ Running (last check: 10:29:58)
- **LinkedIn**: ✅ Running (last check: 10:25:00)
```

### View Watcher Logs

```bash
# Gmail watcher logs
tail -f logs/gmail_watcher.log

# WhatsApp watcher logs
tail -f logs/whatsapp_watcher.log

# LinkedIn watcher logs
tail -f logs/linkedin_watcher.log

# All watcher logs
tail -f logs/*.log
```

### Check Deduplication

```bash
# View processed message IDs
cat .gmail_dedupe.json
cat .whatsapp_dedupe.json
cat .linkedin_dedupe.json
```

### Clean Up Old Deduplication Data

```bash
# Deduplication files can grow large over time
# Clean up entries older than 30 days

# Backup first
cp .gmail_dedupe.json .gmail_dedupe.json.bak

# Clean up (manual process - review before deleting)
# Or let the system handle it automatically (30-day retention)
```

---

## Best Practices

### 1. Monitor Regularly

Check watcher status daily:
```bash
pm2 status
cat AI_Employee_Vault/Dashboard.md
```

### 2. Rotate Credentials

- **Gmail**: Tokens auto-refresh (no action needed)
- **LinkedIn**: Refresh every 60 days (set calendar reminder)
- **WhatsApp**: Session persists until manually logged out

### 3. Review Logs

Check logs for errors:
```bash
tail -f logs/*.log | grep ERROR
```

### 4. Test After Changes

After updating configuration:
```bash
# Stop watchers
pm2 stop all

# Test each watcher individually
python run_watcher.py --watcher gmail
python run_watcher.py --watcher whatsapp
python run_watcher.py --watcher linkedin

# If all work, restart with PM2
pm2 restart all
```

### 5. Backup Session Data

```bash
# Backup WhatsApp session
tar -czf whatsapp_session_backup.tar.gz .whatsapp_session/

# Backup credentials
cp .env .env.backup
cp credentials.json credentials.json.backup
cp token.json token.json.backup
```

---

## Summary

**Watcher Setup Overview**:
- ✅ **Gmail Watcher**: OAuth2 authentication, 60s polling
- ✅ **WhatsApp Watcher**: QR code scan, CDP architecture, 30s polling
- ✅ **LinkedIn Watcher**: OAuth2 authentication, 300s polling

**Key Features**:
- Continuous monitoring (24/7)
- Duplicate prevention
- Graceful degradation
- Health monitoring
- Auto-restart on crash

**Management**:
- PM2 for process management
- Dashboard.md for status
- Logs for debugging
- Multi-watcher orchestration

**Next Steps**:
- See `docs/MCP_SERVERS.md` for MCP server setup
- See `docs/APPROVAL_WORKFLOW.md` for approval workflow
- See `SILVER_QUICKSTART.md` for end-to-end examples
