# Watcher Configuration Guide

## Company_Handbook.md Setup

Add these sections to `My_AI_Employee/AI_Employee_Vault/Company_Handbook.md`:

### Gmail Configuration

```markdown
## Gmail Watcher

### Account Settings
- Email: your-email@gmail.com
- API Scopes: gmail.readonly
- OAuth Token: Auto-refreshed (stored in .env)

### Monitoring Rules
- Watch Labels: INBOX, IMPORTANT, [CUSTOM_LABELS]
- Check Frequency: Every 5 minutes
- Include Archived: false
- Max Items Per Check: 10

### Priority Rules
HIGH:
  - Subject contains: urgent, asap, critical, emergency
  - From: ceo@company.com, important_client@domain.com
  - Has attachment with: invoice, contract, legal

MEDIUM:
  - Standard business emails
  - Meetings, updates, requests

LOW:
  - Newsletters
  - Notifications
  - FYI messages
```

### WhatsApp Configuration

```markdown
## WhatsApp Watcher

### Session Management
- Session File: .whatsapp_session (auto-created on first run)
- QR Code: Scan on first run, then persistent
- Browser: Chromium via Playwright

### Monitored Contacts
- Client A (Prime Contact)
- Client B (Prime Contact)
- Team Lead
- Personal Contact

### Message Filters
Keywords to monitor:
  - urgent, asap
  - meeting, call, discussion
  - invoice, payment, deal
  - proposal, contract

Check Frequency: Every 2 minutes
Archive read messages: Yes
Store conversation history: Last 50 messages
```

### LinkedIn Configuration

```markdown
## LinkedIn Watcher

### Account Settings
- Account: your-linkedin-url
- API Token: (stored in .env)
- Token Expiry: Auto-refresh 24 hours before expiry

### Notification Types
Monitor:
  - Connection requests
  - Direct messages
  - Post comments
  - Job opportunities

### Posting Rules
Auto-Post Topics: AI, Automation, Business Innovation
Max Posts Per Day: 3
Business Hours: 9am - 5pm (user timezone)
Rate Limit: 1 post every 4 hours

### Monitoring Rules
Check Frequency: Every 10 minutes
```

### Filesystem Configuration

```markdown
## Filesystem Watcher

### Watch Folder
Path: My_AI_Employee/test_watch_folder (from .env: WATCH_FOLDER)
Extensions: .txt, .pdf, .docx, .xlsx, .jpg, .png
Max File Size: 100MB

### Processing
- Move to Needs_Action: Yes (create action item)
- Keep Original: Yes (in watch folder)
- Auto-cleanup: After 7 days
```

## .env File Settings

```bash
# Gmail
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_EMAIL=your-email@gmail.com
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_token_here
LINKEDIN_API_VERSION=202601

# WhatsApp
WHATSAPP_SESSION_FILE=.whatsapp_session
WHATSAPP_HEADLESS=false    # Set to true for production (no UI)

# Filesystem
WATCH_FOLDER=My_AI_Employee/test_watch_folder

# Watcher General
VAULT_ROOT=My_AI_Employee/AI_Employee_Vault
WATCHER_CHECK_INTERVAL=30  # Seconds between health checks
WATCHER_MAX_RETRIES=5      # Max retries before marking dead
WATCHER_BACKOFF_MAX=300    # Max backoff in seconds (5 minutes)
WATCHER_LOG_LEVEL=INFO     # DEBUG, INFO, WARNING, ERROR
```

## Watcher Status Fields

Each watcher reports:
- `name` - Watcher name (gmail, whatsapp, linkedin, filesystem)
- `status` - online, checking, retrying, offline, dead
- `last_check` - ISO timestamp of last health check
- `checks_ok` - Number of consecutive successful checks
- `checks_fail` - Number of consecutive failed checks
- `uptime_percent` - Percentage uptime (24h rolling window)
- `error_message` - Last error (if any)
- `items_created_today` - Number of action items created
- `session_active` - true/false (WhatsApp specific)

## Logs Location

```
logs/
├── gmail_watcher.log
├── whatsapp_watcher.log
├── linkedin_watcher.log
├── filesystem_watcher.log
├── orchestrator.log
└── health_check.log
```

Each log is rotated daily and kept for 30 days.
