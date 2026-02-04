# WhatsApp Watcher Setup Guide

Complete guide to set up and run the WhatsApp watcher with all 5 new features.

## Prerequisites

- Python 3.10+
- WhatsApp account with phone
- Internet connection

---

## Step 1: Install Dependencies

```bash
cd My_AI_Employee

# Install Python dependencies
pip install -r requirements.txt

# Or if using uv (recommended)
uv pip install -r requirements.txt

# Install Playwright browsers (REQUIRED for WhatsApp Web)
playwright install chromium
```

---

## Step 2: Configure .env File

Create or update `My_AI_Employee/.env` with the following:

```bash
# ============================================================================
# WhatsApp Watcher Configuration
# ============================================================================

# Obsidian vault path (absolute or relative)
VAULT_PATH=My_AI_Employee/AI_Employee_Vault

# WhatsApp session file (stores authentication after QR code scan)
WHATSAPP_SESSION_FILE=My_AI_Employee/.whatsapp_session.json

# WhatsApp deduplication tracker (prevents duplicate action items)
WHATSAPP_DEDUPE_FILE=My_AI_Employee/.whatsapp_dedupe.json

# WhatsApp check interval in seconds (default: 60)
WHATSAPP_WATCHER_INTERVAL=60

# Dashboard update interval in seconds (default: 60)
DASHBOARD_UPDATE_INTERVAL=60

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

**Note**: The session and dedupe files will be created automatically. Don't create them manually.

---

## Step 3: Configure Monitored Contacts (Optional)

Edit `My_AI_Employee/AI_Employee_Vault/Company_Handbook.md` and add:

```markdown
## Monitored WhatsApp Contacts
- John Smith
- Sarah Johnson
- Tech Support Team
- Client Services
```

**If you skip this step**: The watcher will monitor ALL WhatsApp contacts (default behavior).

---

## Step 4: Initialize WhatsApp Session (QR Code Scan)

This is a **ONE-TIME setup** to authenticate with WhatsApp Web.

```bash
cd My_AI_Employee

# Method 1: Using the watcher directly
python -m watchers.whatsapp_watcher --init --vault-path AI_Employee_Vault

# Method 2: Using run_watcher.py (if it supports --init)
python run_watcher.py --watcher whatsapp --init
```

**What happens:**
1. A browser window will open showing WhatsApp Web
2. You'll see a QR code
3. Open WhatsApp on your phone
4. Go to: **Settings → Linked Devices → Link a Device**
5. Scan the QR code with your phone
6. Wait for "QR code scanned successfully!" message
7. Session is saved to `.whatsapp_session.json`

**Troubleshooting:**
- If QR code doesn't appear: Check internet connection
- If timeout occurs: Run the command again (you have 2 minutes to scan)
- If browser doesn't open: Make sure Playwright is installed (`playwright install chromium`)

---

## Step 5: Run the WhatsApp Watcher

After initializing the session, run the watcher:

### Option A: Run Watcher Directly

```bash
cd My_AI_Employee

# Run with default settings
python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault

# Run with custom interval (check every 30 seconds)
python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault --interval 30

# Run in headless mode (no visible browser)
python -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault --headless
```

### Option B: Run via run_watcher.py

```bash
cd My_AI_Employee

# Run WhatsApp watcher only
python run_watcher.py --watcher whatsapp

# Run all watchers (Gmail, WhatsApp, LinkedIn)
python run_watcher.py --watcher all
```

### Option C: Run with PM2 (Production)

```bash
cd My_AI_Employee

# Start with PM2
pm2 start ecosystem.config.js --only whatsapp-watcher

# View logs
pm2 logs whatsapp-watcher

# Stop watcher
pm2 stop whatsapp-watcher
```

---

## Step 6: Verify It's Working

### Check 1: Watcher is Running

You should see log output like:
```
2026-01-19 10:30:00 - watchers.whatsapp_watcher - INFO - WhatsApp watcher initialized
2026-01-19 10:30:00 - watchers.whatsapp_watcher - INFO - Monitoring 3 specific contacts
2026-01-19 10:30:05 - watchers.whatsapp_watcher - INFO - WhatsApp session is active
2026-01-19 10:30:05 - watchers.whatsapp_watcher - INFO - Fetched 0 unread message previews from WhatsApp Web
```

### Check 2: Send Test Message

1. Send yourself a WhatsApp message with "URGENT: Test message"
2. Wait 60 seconds (or your configured interval)
3. Check `AI_Employee_Vault/Needs_Action/` folder
4. You should see a new file: `YYYYMMDD_HHMMSS_whatsapp_YourName.md`

### Check 3: Verify Features

**Feature 1: Preview-based reading**
- ✅ Browser should NOT click into chats
- ✅ Messages should be read from chat list only

**Feature 2: Session expiration notification**
- ✅ If session expires, a notification file is created in `/Needs_Action/`
- ✅ File contains re-authentication instructions

**Feature 3: CLI --init flag**
- ✅ `python -m watchers.whatsapp_watcher --init` works
- ✅ `python -m watchers.whatsapp_watcher --help` shows all options

**Feature 4: Monitored contacts filter**
- ✅ Only contacts in Company_Handbook.md are monitored
- ✅ Other contacts are skipped (check logs for "Skipping non-monitored contact")

**Feature 5: Improved priority logic**
- ✅ Messages with "urgent", "help", "payment" → High priority
- ✅ 5+ unread messages → High priority
- ✅ 3-4 unread messages → Medium priority
- ✅ Normal messages → Medium priority

---

## Step 7: Run Automated Tests

```bash
cd My_AI_Employee

# Run WhatsApp watcher tests
pytest tests/integration/test_whatsapp_watcher.py -v

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/integration/test_whatsapp_watcher.py --cov=watchers.whatsapp_watcher --cov-report=html
```

**Expected output:**
```
test_whatsapp_watcher_initialization PASSED
test_whatsapp_watcher_loads_monitored_contacts PASSED
test_whatsapp_watcher_urgent_keyword_detection PASSED
test_whatsapp_watcher_priority_logic_keywords PASSED
test_whatsapp_watcher_priority_logic_unread_count PASSED
test_whatsapp_watcher_session_check_active PASSED
test_whatsapp_watcher_session_expired_creates_notification PASSED
test_whatsapp_watcher_preview_based_reading PASSED
test_whatsapp_watcher_monitored_contacts_filter PASSED
test_whatsapp_watcher_creates_action_item PASSED
test_whatsapp_watcher_deduplication PASSED
test_whatsapp_watcher_initialize_session PASSED
test_whatsapp_watcher_message_format_includes_notes PASSED

========================= 13 passed in 2.5s =========================
```

---

## Step 8: Manual End-to-End Test

### Test Scenario 1: Urgent Message Detection

1. **Send message**: "URGENT: Need help with invoice"
2. **Wait**: 60 seconds
3. **Check**: `AI_Employee_Vault/Needs_Action/` for new file
4. **Verify**: Priority is "High" in frontmatter
5. **Verify**: Message preview is correct
6. **Verify**: Formatting notes are included

### Test Scenario 2: Multiple Unread Messages

1. **Send**: 5 messages to yourself quickly
2. **Wait**: 60 seconds
3. **Check**: Action item created
4. **Verify**: Priority is "High" (5+ unread)
5. **Verify**: Unread count is shown

### Test Scenario 3: Monitored Contacts Filter

1. **Add contact**: "Test Contact" to Company_Handbook.md
2. **Restart watcher**
3. **Send message**: From monitored contact → Should be detected
4. **Send message**: From non-monitored contact → Should be skipped
5. **Check logs**: "Skipping non-monitored contact: [Name]"

### Test Scenario 4: Session Expiration

1. **Delete session file**: `rm My_AI_Employee/.whatsapp_session.json`
2. **Run watcher**: It should detect expired session
3. **Check**: Notification file created in `/Needs_Action/`
4. **Verify**: File contains re-authentication instructions

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'dotenv'"

**Solution:**
```bash
pip install python-dotenv
```

### Issue: "ModuleNotFoundError: No module named 'playwright'"

**Solution:**
```bash
pip install playwright
playwright install chromium
```

### Issue: "WhatsApp session not found"

**Solution:**
```bash
# Re-initialize session
python -m watchers.whatsapp_watcher --init --vault-path AI_Employee_Vault
```

### Issue: "QR code scan timeout"

**Solution:**
- You have 2 minutes to scan the QR code
- Make sure your phone has internet connection
- Try again: `python -m watchers.whatsapp_watcher --init`

### Issue: "Browser doesn't open"

**Solution:**
```bash
# Reinstall Playwright browsers
playwright install chromium --force
```

### Issue: "No messages detected"

**Solution:**
1. Check if watcher is running: Look for log output
2. Check interval: Default is 60 seconds
3. Check monitored contacts: Make sure sender is in the list (or remove the list to monitor all)
4. Check deduplication: Delete `.whatsapp_dedupe.json` and restart

### Issue: "Session expires frequently"

**Solution:**
- WhatsApp Web sessions can expire if:
  - Phone is offline for extended period
  - WhatsApp app is uninstalled/reinstalled
  - Phone number changes
- Re-initialize session when this happens

---

## Production Deployment

### Using PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Start watcher
pm2 start ecosystem.config.js --only whatsapp-watcher

# Save PM2 configuration
pm2 save

# Setup auto-restart on system reboot
pm2 startup

# Monitor
pm2 monit
```

### Using systemd (Linux)

Create `/etc/systemd/system/whatsapp-watcher.service`:

```ini
[Unit]
Description=WhatsApp Watcher for AI Employee
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/My_AI_Employee
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 -m watchers.whatsapp_watcher --vault-path AI_Employee_Vault
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable whatsapp-watcher
sudo systemctl start whatsapp-watcher
sudo systemctl status whatsapp-watcher
```

---

## Performance Tips

1. **Adjust check interval**: Increase to 120-300 seconds for lower resource usage
2. **Use headless mode**: Add `--headless` flag to reduce memory usage
3. **Limit monitored contacts**: Only monitor important contacts to reduce processing
4. **Clean dedupe file**: Periodically delete old entries from `.whatsapp_dedupe.json`

---

## Security Best Practices

1. **Never commit session files**: `.whatsapp_session.json` contains authentication tokens
2. **Secure .env file**: Contains sensitive configuration
3. **Use OS credential manager**: For production, use system keyring instead of .env
4. **Regular session refresh**: Re-initialize session every 30 days
5. **Monitor audit logs**: Check `/Logs/` folder for suspicious activity

---

## Next Steps

After WhatsApp watcher is running:

1. **Set up Gmail watcher**: For email monitoring
2. **Set up LinkedIn watcher**: For LinkedIn notifications
3. **Configure approval workflow**: For Silver tier external actions
4. **Set up MCP servers**: For executing approved actions
5. **Configure dashboard**: For system monitoring

---

## Support

If you encounter issues:

1. Check logs: `tail -f My_AI_Employee/logs/whatsapp_watcher.log`
2. Run tests: `pytest tests/integration/test_whatsapp_watcher.py -v`
3. Check GitHub issues: https://github.com/your-repo/issues
4. Review documentation: `CLAUDE.md` and `WATCHER_RUNNER_GUIDE.md`

---

**Last Updated**: 2026-01-19
**Version**: Silver Tier with 5 WhatsApp improvements
