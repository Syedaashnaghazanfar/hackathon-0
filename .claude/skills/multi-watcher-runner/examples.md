# Multi-Watcher Examples

## Starting All Watchers

Run the orchestrator to start all watchers (Gmail, WhatsApp, LinkedIn, Filesystem):

```bash
python scripts/orchestrate_watchers.py
```

**Output:**
```
Multi-Watcher Orchestrator Started
=====================================
Gmail Watcher: ✅ Online (check interval: 5m)
WhatsApp Watcher: ⏳ Authenticating (first run, scan QR code)
LinkedIn Watcher: ✅ Online (check interval: 10m)
Filesystem Watcher: ✅ Online (monitoring: My_AI_Employee/test_watch_folder)

Health checks every 30 seconds
Press Ctrl+C to stop gracefully
```

## First Run: WhatsApp QR Code

First time running the orchestrator, WhatsApp watcher shows QR code:

```bash
# Run orchestrator
python scripts/orchestrate_watchers.py

# Expected:
# WhatsApp Watcher: Waiting for QR code scan...
# 1. Browser opens showing QR code
# 2. Scan with your phone's WhatsApp app
# 3. Browser closes automatically after authentication
# 4. WhatsApp Watcher: ✅ Online (session saved)
```

Session is saved to `.whatsapp_session` - no need to scan again.

## Checking Watcher Status

Monitor all watchers in real-time:

```bash
python scripts/monitor_watchers.py
```

**Output:**
```
Multi-Watcher Status Report
Generated: 2026-01-14 14:30:00 UTC

GMAIL WATCHER
  Status: ✅ online
  Last Check: 14:29:45 (15 seconds ago)
  Uptime: 99.8%
  Items Created Today: 3
  Error Count: 0

WHATSAPP WATCHER
  Status: ✅ online
  Last Check: 14:29:50 (10 seconds ago)
  Uptime: 98.5%
  Items Created Today: 1
  Session Active: Yes

LINKEDIN WATCHER
  Status: ✅ online
  Last Check: 14:29:30 (30 seconds ago)
  Uptime: 95.2%
  Items Created Today: 0

FILESYSTEM WATCHER
  Status: ✅ online
  Last Check: 14:29:59 (1 second ago)
  Uptime: 100%
  Items Created Today: 2

OVERALL
  Watchers Online: 4/4
  Average Uptime: 98.4%
  Total Items Created: 6
  Next Health Check: 14:30:30
```

## Restarting a Specific Watcher

If a watcher crashes or becomes unresponsive, restart it:

```bash
# Restart Gmail watcher
python scripts/restart_watcher.py gmail

# Output:
# Gmail Watcher: Restarting...
# Gmail Watcher: ✅ Online (tokens refreshed)
```

Other options:
```bash
python scripts/restart_watcher.py whatsapp
python scripts/restart_watcher.py linkedin
python scripts/restart_watcher.py filesystem
```

## Viewing Watcher Logs

See detailed logs for each watcher:

```bash
# All watcher logs
tail -f logs/*.log

# Specific watcher
tail -f logs/gmail_watcher.log
tail -f logs/whatsapp_watcher.log
tail -f logs/linkedin_watcher.log
tail -f logs/filesystem_watcher.log

# Orchestrator logs
tail -f logs/orchestrator.log
tail -f logs/health_check.log
```

## Handling Gmail OAuth Errors

If you get "Gmail API: 403 Forbidden" error:

```bash
# 1. Delete old token
rm token.json

# 2. Enable Gmail API in Google Cloud Console
# Go to: https://console.cloud.google.com/
# Search "Gmail API" and click Enable

# 3. Restart Gmail watcher
python scripts/restart_watcher.py gmail

# 4. Complete OAuth flow in browser
# Follow the prompts to re-authenticate
```

## Handling WhatsApp Session Expiry

If WhatsApp session expires (after 2+ weeks):

```bash
# 1. Delete expired session
rm .whatsapp_session

# 2. Run orchestrator
python scripts/orchestrate_watchers.py

# 3. WhatsApp watcher will show new QR code
# Scan with your phone to re-authenticate
```

## Handling LinkedIn Rate Limits

If you see "Rate limit: Try again in 1 hour":

```bash
# This is automatic! LinkedIn watcher will:
# 1. Detect rate limit error
# 2. Back off for 1 hour
# 3. Auto-retry after cooldown
# 4. Resume normal operation

# View LinkedIn logs to see retry schedule
tail -f logs/linkedin_watcher.log
```

## Creating Action Items from Email

Gmail watcher monitors inbox for priority keywords and creates action items:

**Email arrives:**
```
From: client@example.com
Subject: URGENT: Contract review needed
Body: Please review the attached contract ASAP. Need feedback by EOD.
```

**Action item automatically created** in `/Needs_Action/`:
```markdown
---
type: gmail
from: client@example.com
received: 2026-01-14T14:30:00Z
priority: high
status: pending
---

# Gmail: URGENT: Contract review needed

**From**: client@example.com
**Date**: 2026-01-14 14:30:00
**Priority**: HIGH (urgent, asap, contract keywords detected)

## Email Body
Please review the attached contract ASAP. Need feedback by EOD.

## Attachments
- contract.pdf

## Next Steps
- [ ] Review contract attachment
- [ ] Provide feedback to client@example.com
- [ ] Send response by EOD
```

## Creating Action Items from WhatsApp

WhatsApp watcher creates action items for monitored contacts with keyword matches:

**WhatsApp message from "Client A":**
```
"URGENT: Please review attached document. Need your feedback ASAP."
```

**Action item automatically created** in `/Needs_Action/`:
```markdown
---
type: whatsapp
from: Client A
received: 2026-01-14T14:30:00Z
priority: high
status: pending
---

# WhatsApp Message: Client A

**From**: Client A
**Time**: 2026-01-14 14:30:00
**Chat**: Client A (Mobile: Last 4 digits visible)

## Message
URGENT: Please review attached document. Need your feedback ASAP.

## Metadata
- Keywords: urgent, asap
- Attachment: document (PDF)
- Previous context: Last 3 messages from this contact

## Next Steps
- [ ] Review attachment
- [ ] Provide feedback to Client A
- [ ] Send response via WhatsApp or email
```

## 24/7 Operation with PM2

Run watchers continuously with PM2:

```bash
# Start with PM2
pm2 start scripts/orchestrate_watchers.py --name "multi-watchers" --interpreter python3

# View status
pm2 status

# View logs
pm2 logs multi-watchers

# Restart if needed
pm2 restart multi-watchers

# Auto-start on system boot
pm2 startup
pm2 save
```

## Graceful Shutdown

Stop all watchers cleanly:

```bash
# Keyboard interrupt (Ctrl+C) during orchestrator run
# Watchers will:
# 1. Finish current health check
# 2. Flush logs
# 3. Clean up resources
# 4. Exit gracefully

# Or with orchestrator flag
python scripts/orchestrate_watchers.py --stop
```

## Monitoring Check Frequency

Adjust how often watchers check for new items. Edit `Company_Handbook.md`:

```markdown
## Watcher Check Frequencies

### Gmail
- Check Frequency: Every 5 minutes
- (Adjust based on email volume)

### WhatsApp
- Check Frequency: Every 2 minutes
- (Real-time messaging needs frequent checks)

### LinkedIn
- Check Frequency: Every 10 minutes
- (Less frequent to respect API rate limits)

### Filesystem
- Check Frequency: Every 30 seconds
- (Local filesystem is fast, can check frequently)
```

Then edit `.env`:
```bash
GMAIL_CHECK_INTERVAL=300        # 5 minutes
WHATSAPP_CHECK_INTERVAL=120     # 2 minutes
LINKEDIN_CHECK_INTERVAL=600     # 10 minutes
FILESYSTEM_CHECK_INTERVAL=30    # 30 seconds
```

Restart watchers for changes to take effect.
