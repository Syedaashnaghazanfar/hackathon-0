# Multi-Watcher Configuration Section for Company_Handbook.md

Add this section to `My_AI_Employee/AI_Employee_Vault/Company_Handbook.md`:

---

## Watchers Configuration

### Gmail Watcher

**Account Settings**
- Email: your-email@gmail.com
- API Scopes: gmail.readonly (read-only, cannot send/delete)
- OAuth Token: Auto-refreshed (stored in .env)

**Monitoring Rules**
- Watch Labels: INBOX, IMPORTANT, [custom labels if any]
- Check Frequency: Every 5 minutes
- Include Archived: false
- Max Items Per Check: 10

**Priority Rules**
- HIGH: Subject contains urgent, asap, critical, emergency
- HIGH: From important clients or management
- HIGH: Has invoice, contract, or legal documents
- MEDIUM: Standard business emails
- LOW: Newsletters, notifications, FYI messages

---

### WhatsApp Watcher

**Session Management**
- Session File: .whatsapp_session (auto-created on first run)
- QR Code: Scan on first run only, then persistent
- Browser: Chromium via Playwright
- Session Lifetime: ~2 weeks (WhatsApp timeout)

**Monitored Contacts**
- Client A (Prime Contact - HIGH priority)
- Client B (Prime Contact - HIGH priority)
- Team Lead (MEDIUM priority)
- Personal Contact (LOW priority)

**Message Filters**
Keywords to monitor (trigger action items):
- urgent, asap, critical
- meeting, call, discussion, conference
- invoice, payment, receipt, quote
- proposal, contract, deal, agreement
- deadline, overdue, delayed

Check Frequency: Every 2 minutes
Archive read messages: Yes
Store conversation history: Last 50 messages

---

### LinkedIn Watcher

**Account Settings**
- Account: [your LinkedIn profile URL]
- API Token: [stored in .env as LINKEDIN_ACCESS_TOKEN]
- Token Expiry: Auto-refresh 24 hours before expiry

**Notification Types to Monitor**
- Connection requests from industry contacts
- Direct messages from clients/partners
- Post comments on your content
- Job opportunities

**Posting Configuration**
- Auto-Post Topics: AI, Automation, Business Innovation, Entrepreneurship
- Max Posts Per Day: 3
- Business Hours: 9am - 5pm (your timezone)
- Rate Limit: 1 post every 4 hours

Check Frequency: Every 10 minutes

---

### Filesystem Watcher

**Watch Configuration**
- Watch Folder: My_AI_Employee/test_watch_folder
- Supported Types: .txt, .pdf, .docx, .xlsx, .jpg, .png
- Max File Size: 100MB
- Check Frequency: Every 30 seconds

**Processing Rules**
- Create action item in /Needs_Action/: Yes
- Keep original file in watch folder: Yes
- Auto-cleanup processed files: After 7 days

---

## Watcher Status Indicators

✅ **Online** - Watcher is healthy and checking
⏳ **Checking** - Currently performing health check
⚠️ **Retrying** - Encountered error, backing off exponentially
❌ **Offline** - Failed, will attempt recovery
💀 **Dead** - Failed 5+ times, manual intervention required

---

## Logs Location

Watcher logs are stored in `logs/` directory and rotated daily:
- `logs/gmail_watcher.log` - Gmail monitoring logs
- `logs/whatsapp_watcher.log` - WhatsApp session and messages
- `logs/linkedin_watcher.log` - LinkedIn API calls and posts
- `logs/filesystem_watcher.log` - File drop folder monitoring
- `logs/orchestrator.log` - Main orchestrator status
- `logs/health_check.log` - Health check status

Logs are kept for 30 days before auto-deletion.

---
