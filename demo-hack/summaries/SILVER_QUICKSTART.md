# Silver Tier AI Employee - Quick Start Guide

**Time to Complete**: 30-45 minutes
**Prerequisites**: Python 3.13+, Gmail account, WhatsApp account
**Goal**: Get your AI Employee monitoring Gmail and WhatsApp, processing action items, and executing approved actions

---

## Overview

This guide walks you through setting up and testing your Silver Tier AI Employee in three phases:

1. **Setup** (15 minutes): Install dependencies, configure credentials
2. **Test Gmail Workflow** (10 minutes): Send test email, approve, verify sent
3. **Test WhatsApp Workflow** (10 minutes): Send test message, approve, verify sent

---

## Phase 1: Setup (15 minutes)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd hackathon-0/My_AI_Employee

# Install Python dependencies
uv sync

# Verify installation
python --version  # Should be 3.13+
```

### Step 2: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required variables for Gmail**:
```bash
VAULT_PATH=AI_Employee_Vault
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.modify
GMAIL_CHECK_INTERVAL=60
```

**Required variables for WhatsApp**:
```bash
WHATSAPP_SESSION_DIR=.whatsapp_session
WHATSAPP_CDP_PORT=9222
WHATSAPP_CHECK_INTERVAL=30
```

### Step 3: Set Up Gmail OAuth2

```bash
# Run OAuth2 setup script
python scripts/setup/setup_gmail_oauth.py
```

**What happens**:
1. Browser opens to Google OAuth consent screen
2. You log in and grant permissions
3. Script saves `credentials.json` and `token.json`
4. You're ready to use Gmail API

**Troubleshooting**:
- If browser doesn't open, copy the URL from terminal and paste in browser
- If you see "App not verified", click "Advanced" → "Go to [App Name] (unsafe)"
- Token auto-refreshes; if issues persist, re-run: `python scripts/setup/setup_gmail_oauth.py`

### Step 4: Verify Vault Structure

```bash
# Check vault folders exist
ls -la AI_Employee_Vault/

# Expected folders:
# - Needs_Action/
# - Pending_Approval/
# - Approved/
# - Rejected/
# - Failed/
# - Done/
# - Plans/
# - Logs/
```

If folders are missing, create them:
```bash
mkdir -p AI_Employee_Vault/{Needs_Action,Pending_Approval,Approved,Rejected,Failed,Done,Plans,Logs}
```

### Step 5: Configure Company Handbook

Edit `AI_Employee_Vault/Company_Handbook.md` to define your rules:

```markdown
## Section 6.4: Silver Tier Approval Thresholds

- **Email responses**: Low (always approve unless sensitive)
- **LinkedIn posts**: Medium (review content before posting)
- **WhatsApp messages**: Medium (review before sending)
- **Payments**: High (always review carefully)

## Communication Style

- Professional but friendly tone
- Keep emails concise (under 200 words)
- Always include a call-to-action
- Sign emails with "Best regards, [Your Name]"
```

---

## Phase 2: Test Gmail Workflow (10 minutes)

### Step 1: Start Gmail Watcher

```bash
# In terminal 1
cd My_AI_Employee
python run_watcher.py --watcher gmail
```

**Expected output**:
```
2026-01-21 10:00:00 - INFO - Starting Gmail watcher
2026-01-21 10:00:00 - INFO - Authenticated as: your.email@gmail.com
2026-01-21 10:00:00 - INFO - Monitoring inbox every 60 seconds
```

### Step 2: Send Test Email

From another email account, send an email to your monitored Gmail:

```
To: your.email@gmail.com
Subject: Test - Project Update Request
Body: Hi, can you send me an update on the XYZ project? Thanks!
```

### Step 3: Verify Action Item Created

Within 2 minutes, check your vault:

```bash
ls -la AI_Employee_Vault/Needs_Action/

# Expected file:
# 20260121_103000_123456_email_sender_name.md
```

View the action item:
```bash
cat AI_Employee_Vault/Needs_Action/20260121_103000_123456_email_sender_name.md
```

**Expected content**:
```markdown
---
type: action_item
action_type: email
source: gmail
priority: Medium
created_at: 2026-01-21T10:30:00Z
status: pending
---

# Email from sender@example.com

**Subject**: Test - Project Update Request

**From**: sender@example.com

**Body**:
Hi, can you send me an update on the XYZ project? Thanks!
```

### Step 4: Process Action Item with Claude Code

In Claude Code:
```
/needs-action-triage process the tasks
```

**What happens**:
1. Claude Code reads the action item
2. Analyzes against Company_Handbook.md rules
3. Creates `Plans/Plan_20260121_email_sender.md` with reasoning
4. Creates `Pending_Approval/APPROVAL_20260121_email_sender.md` with draft email

### Step 5: Review and Approve

View the approval request:
```bash
cat AI_Employee_Vault/Pending_Approval/APPROVAL_20260121_email_sender.md
```

**Expected content**:
```markdown
---
type: approval_request
action_type: email
requires_approval: true
priority: Medium
status: pending
created_at: 2026-01-21T10:31:00Z
---

# Approval Request: Email Response

**To**: sender@example.com
**Subject**: Re: Test - Project Update Request

**Draft Email**:
Hi [Sender Name],

Thanks for reaching out! Here's an update on the XYZ project:

[Project update details based on your vault content]

Let me know if you need any additional information.

Best regards,
[Your Name]

---

**Reasoning**: This is a client request for a project update. Based on Company_Handbook.md, email responses have Low approval threshold. The draft follows your communication style (professional, concise, includes call-to-action).

**Recommendation**: APPROVE
```

**Approve the email**:
```bash
mv AI_Employee_Vault/Pending_Approval/APPROVAL_20260121_email_sender.md \
   AI_Employee_Vault/Approved/
```

### Step 6: Start Orchestrator and Execute

In terminal 2:
```bash
cd My_AI_Employee
python orchestrator.py
```

**Expected output**:
```
2026-01-21 10:32:00 - INFO - Starting orchestrator
2026-01-21 10:32:00 - INFO - Watching Approved/ folder
2026-01-21 10:32:05 - INFO - Detected approved action: APPROVAL_20260121_email_sender.md
2026-01-21 10:32:05 - INFO - Routing to email_mcp
2026-01-21 10:32:06 - INFO - Email sent successfully: message_id=abc123
2026-01-21 10:32:06 - INFO - Moved to Done/EXECUTED_20260121_email_sender.md
```

### Step 7: Verify Email Sent

Check your Gmail sent folder - the email should be there!

View execution record:
```bash
cat AI_Employee_Vault/Done/EXECUTED_20260121_email_sender.md
```

**Expected content**:
```markdown
---
type: execution_record
action_type: email
status: completed
executed_at: 2026-01-21T10:32:06Z
approved_by: user
result: success
---

# Executed: Email Response

**To**: sender@example.com
**Subject**: Re: Test - Project Update Request
**Message ID**: abc123
**Sent At**: 2026-01-21T10:32:06Z

**Status**: ✅ Successfully sent

**Audit Log**: Logged to Logs/2026-01-21.json
```

**🎉 Gmail workflow complete!**

---

## Phase 3: Test WhatsApp Workflow (10 minutes)

### Step 1: Set Up WhatsApp Session

```bash
# In terminal 1 (stop Gmail watcher with Ctrl+C first)
cd My_AI_Employee
python run_watcher.py --watcher whatsapp
```

**What happens**:
1. Browser opens to WhatsApp Web
2. QR code appears
3. Scan QR code with your phone (WhatsApp → Settings → Linked Devices)
4. Session saves to `.whatsapp_session/` directory

**Expected output**:
```
2026-01-21 10:35:00 - INFO - Starting WhatsApp watcher
2026-01-21 10:35:00 - INFO - Launching browser with CDP on port 9222
2026-01-21 10:35:05 - INFO - Waiting for QR code scan...
2026-01-21 10:35:30 - INFO - Session authenticated successfully
2026-01-21 10:35:30 - INFO - Monitoring messages every 30 seconds
```

**Important**: Leave this browser window open! The watcher and MCP server share this browser session via CDP.

### Step 2: Send Test WhatsApp Message

From your phone or another WhatsApp account, send a message to yourself:

```
urgent: need help with invoice payment
```

### Step 3: Verify Action Item Created

Within 2 minutes, check your vault:

```bash
ls -la AI_Employee_Vault/Needs_Action/

# Expected file:
# 20260121_103600_whatsapp_contact_name.md
```

View the action item:
```bash
cat AI_Employee_Vault/Needs_Action/20260121_103600_whatsapp_contact_name.md
```

**Expected content**:
```markdown
---
type: action_item
action_type: whatsapp
source: whatsapp
priority: High
urgent_keywords: ["urgent", "invoice", "payment"]
created_at: 2026-01-21T10:36:00Z
status: pending
---

# WhatsApp from Contact Name

**Message**: urgent: need help with invoice payment

**Detected Keywords**: urgent, invoice, payment
**Priority**: High (urgent keywords detected)
```

### Step 4: Process Action Item with Claude Code

In Claude Code:
```
/needs-action-triage process the tasks
```

**What happens**:
1. Claude Code reads the WhatsApp action item
2. Analyzes urgency and content
3. Creates `Plans/Plan_20260121_whatsapp_contact.md`
4. Creates `Pending_Approval/APPROVAL_20260121_whatsapp_contact.md` with draft reply

### Step 5: Review and Approve

View the approval request:
```bash
cat AI_Employee_Vault/Pending_Approval/APPROVAL_20260121_whatsapp_contact.md
```

**Approve the message**:
```bash
mv AI_Employee_Vault/Pending_Approval/APPROVAL_20260121_whatsapp_contact.md \
   AI_Employee_Vault/Approved/
```

### Step 6: Execute via Orchestrator

The orchestrator (still running in terminal 2) will detect and execute:

**Expected output**:
```
2026-01-21 10:37:05 - INFO - Detected approved action: APPROVAL_20260121_whatsapp_contact.md
2026-01-21 10:37:05 - INFO - Routing to browser_mcp
2026-01-21 10:37:06 - INFO - Connecting to watcher's browser via CDP (port 9222)
2026-01-21 10:37:07 - INFO - WhatsApp message sent successfully
2026-01-21 10:37:07 - INFO - Moved to Done/EXECUTED_20260121_whatsapp_contact.md
```

### Step 7: Verify Message Sent

Check WhatsApp on your phone - the reply should be there!

View execution record:
```bash
cat AI_Employee_Vault/Done/EXECUTED_20260121_whatsapp_contact.md
```

**🎉 WhatsApp workflow complete!**

---

## Phase 4: Production Setup (Optional)

### Run All Watchers Simultaneously

```bash
# Stop individual watchers (Ctrl+C in terminals)

# Start all watchers in one command
cd My_AI_Employee
python run_watcher.py --watcher all
```

**Expected output**:
```
2026-01-21 10:40:00 - INFO - Starting multi-watcher orchestration
2026-01-21 10:40:00 - INFO - Launching Gmail watcher (thread 1)
2026-01-21 10:40:00 - INFO - Launching WhatsApp watcher (thread 2)
2026-01-21 10:40:00 - INFO - Launching LinkedIn watcher (thread 3)
2026-01-21 10:40:05 - INFO - All watchers started successfully
2026-01-21 10:40:05 - INFO - Health monitoring enabled
```

### Use PM2 for Process Management

```bash
# Install PM2 globally
npm install -g pm2

# Start all processes
cd My_AI_Employee
pm2 start ecosystem.config.js

# View status
pm2 status

# View logs
pm2 logs

# Stop all
pm2 stop all

# Restart all
pm2 restart all
```

---

## Monitoring and Maintenance

### Check Dashboard

View real-time status:
```bash
cat AI_Employee_Vault/Dashboard.md
```

**Expected content**:
```markdown
# AI Employee Dashboard

**Last Updated**: 2026-01-21 10:40:00

## Status Summary

- **Pending Approvals**: 0
- **Approved (Queued)**: 0
- **Completed Today**: 2
- **Failed Today**: 0

## Watcher Health

- **Gmail**: ✅ Running (last check: 10:39:55)
- **WhatsApp**: ✅ Running (last check: 10:39:58)
- **LinkedIn**: ⚠️ Not configured (OAuth2 setup required)

## Recent Activity

1. ✅ Email sent to sender@example.com (10:32:06)
2. ✅ WhatsApp message sent to Contact Name (10:37:07)
```

### View Audit Logs

```bash
# View today's audit log
cat AI_Employee_Vault/Logs/2026-01-21.json
```

**Expected content**:
```json
{"timestamp":"2026-01-21T10:32:06Z","action_type":"email_sent","actor":"orchestrator","target":"sender@example.com","approval_status":"approved","approved_by":"user","result":"success","message_id":"abc123"}
{"timestamp":"2026-01-21T10:37:07Z","action_type":"whatsapp_sent","actor":"orchestrator","target":"Contact Name","approval_status":"approved","approved_by":"user","result":"success"}
```

### Troubleshooting

**Gmail watcher not detecting emails**:
```bash
# Check token validity
python scripts/debug/debug_gmail.py

# Re-authenticate if needed
python scripts/setup/setup_gmail_oauth.py
```

**WhatsApp session expired**:
```bash
# Restart watcher and scan QR code again
python run_watcher.py --watcher whatsapp
# Scan QR code in browser
```

**Orchestrator not executing**:
```bash
# Check orchestrator logs
tail -f logs/orchestrator.log

# Verify MCP servers are running
# In Claude Code:
/mcp list

# Restart orchestrator
python orchestrator.py
```

---

## Next Steps

### 1. Set Up LinkedIn (Optional)

Follow the LinkedIn OAuth2 setup guide:
```bash
# See My_AI_Employee/LINKEDIN_MIGRATION_GUIDE.md for complete instructions
python scripts/linkedin_oauth2_setup.py
```

### 2. Customize Company Handbook

Edit `AI_Employee_Vault/Company_Handbook.md` to define:
- Your communication style
- Approval thresholds
- Business rules
- LinkedIn posting schedule

### 3. Run 24-Hour Stability Test

```bash
# Start all watchers and orchestrator
pm2 start ecosystem.config.js

# Monitor for 24 hours
pm2 logs

# Check dashboard periodically
cat AI_Employee_Vault/Dashboard.md
```

### 4. Explore Advanced Features

- **Duplicate Detection**: System automatically merges duplicate action items
- **Retry Logic**: Failed actions retry 3 times with exponential backoff
- **Graceful Degradation**: One watcher fails, others continue
- **Credential Sanitization**: Audit logs sanitize sensitive data

---

## Summary

**What You've Accomplished**:
- ✅ Installed and configured Silver Tier AI Employee
- ✅ Set up Gmail OAuth2 authentication
- ✅ Set up WhatsApp CDP session
- ✅ Tested complete Gmail workflow (detect → plan → approve → execute)
- ✅ Tested complete WhatsApp workflow (detect → plan → approve → execute)
- ✅ Verified audit logging and execution records

**Your AI Employee is now**:
- 📧 Monitoring your Gmail inbox
- 💬 Monitoring your WhatsApp messages
- ✅ Routing all external actions through approval workflow
- 📊 Logging all actions with complete audit trail
- 🔄 Retrying failed actions automatically

**Time Invested**: 30-45 minutes
**Value Delivered**: Automated communication monitoring and response preparation

---

## Support

For more information:
- **Full Documentation**: See `README.md`
- **MCP Server API**: See `docs/MCP_SERVERS.md`
- **Approval Workflow**: See `docs/APPROVAL_WORKFLOW.md`
- **Watcher Setup**: See `docs/WATCHER_SETUP.md`
- **Status Report**: See `SILVER_TIER_STATUS_REPORT.md`

**Questions or Issues?**
- Check the troubleshooting section above
- Review the documentation files
- Check the audit logs for error details

---

**Congratulations! Your Silver Tier AI Employee is operational.** 🎉
