# WhatsApp Web Session Management

## How It Works

WhatsApp Watcher uses Playwright to automate WhatsApp Web browser. The session includes:
- Browser cookies
- Authentication tokens
- Contact list
- Chat history (last 50 messages cached)

## First Run: QR Code Authentication

**First time running whatsapp_watcher.py:**

```bash
python scripts/whatsapp_watcher.py
```

**Expected behavior:**
1. Chromium browser opens showing WhatsApp Web QR code
2. Output: "Waiting for QR code scan..."
3. **You scan QR code with your phone** (WhatsApp app)
4. Browser closes automatically
5. Output: "✅ Authentication successful!"
6. Session saved: `.whatsapp_session`

**Time needed:** 1-2 minutes first run

## Session Persistence

### Session File
- Location: `.whatsapp_session`
- Size: ~1-5MB
- Expires: ~2 weeks (WhatsApp session timeout)
- Backed up: Yes (include in vault backups)

### Session Reuse
After first authentication:
```bash
python scripts/whatsapp_watcher.py
```

- ✅ Chromium opens
- ✅ Session automatically logged in
- ✅ No QR code needed
- ✅ Ready to monitor in ~10 seconds

## Configuration

### In Company_Handbook.md

```markdown
## Monitored WhatsApp Contacts

List contacts you want to monitor:
- Client A (High Priority)
- Client B (High Priority)
- Team Lead (Medium Priority)
- Personal Contact (Low Priority)

## Message Keywords

Messages containing these trigger action items:
- urgent, asap, critical
- meeting, call, video
- invoice, payment, receipt
- contract, agreement, deal
```

### In .env

```bash
# WhatsApp Session
WHATSAPP_SESSION_FILE=.whatsapp_session
WHATSAPP_HEADLESS=false          # true = no UI, false = show browser
WHATSAPP_TIMEOUT_MS=30000        # Wait time for elements to load
WHATSAPP_CHECK_INTERVAL=120      # Check every 2 minutes
```

## Session Recovery

### Session Expired (QR code needed again)

**When:**
- Not used for 2+ weeks
- WhatsApp logged out on phone
- WhatsApp version updated

**Fix:**
```bash
# Delete session
rm .whatsapp_session

# Run watcher - new QR code will appear
python scripts/whatsapp_watcher.py

# Scan QR code with phone
```

### Session File Corrupted

**Symptoms:**
- Error: "Session file invalid"
- "Failed to restore browser state"
- Browser doesn't auto-login

**Fix:**
```bash
# Delete corrupt session
rm .whatsapp_session

# Re-authenticate
python scripts/whatsapp_watcher.py
```

## Message Monitoring

### How It Works

1. Watcher checks each monitored contact's chat
2. Finds unread messages
3. For each message with keyword match:
   - Creates action item in `/Needs_Action/`
   - Marks as read in WhatsApp
   - Logs to `logs/whatsapp_watcher.log`

### Keyword Matching

Action items created only if message contains keyword:

```
Keywords: urgent, asap, meeting, invoice, payment, contract
Search: case-insensitive, partial matches OK

Examples that TRIGGER:
- "URGENT: Please review this"       ✅
- "Let's schedule a meeting"          ✅
- "Invoice due: $5,000"               ✅

Examples that DON'T trigger:
- "Hey, how are you?"                 ❌
- "See you tomorrow"                  ❌
- "Just checking in"                  ❌
```

### Action Item Format

When action item created:

```markdown
---
type: whatsapp
from: Client A
received: 2026-01-14T10:30:00Z
priority: high
status: pending
source_id: WHATSAPP_CLIENT-A_20260114_103000
message_id: wam_20260114_103000_abc123
---

# WhatsApp Message: Client A

**From**: Client A
**Time**: 2026-01-14 10:30:00
**Chat**: Client A (Mobile: Last 4 digits visible)

## Message
URGENT: Please review attached contract asap. Need your feedback by EOD.

## Metadata
- Keywords: urgent, asap, contract
- Attachment: document (PDF)
- Previous context: Last 3 messages from this contact

## Next Steps
- [ ] Review attachment
- [ ] Provide feedback to Client A
- [ ] Send response via WhatsApp or email
```

## Troubleshooting

### "Browser not launching"

**Cause**: Chromium not installed

**Fix**:
```bash
playwright install chromium
```

### "Timeout waiting for QR code"

**Cause**: Browser or network issue

**Fix**:
```bash
# Kill any existing browser
pkill -f chromium

# Try again
python scripts/whatsapp_watcher.py
```

### "Element not found: Chat list"

**Cause**: WhatsApp Web UI changed or not fully loaded

**Fix**:
```bash
# Wait for page load (already has retry logic)
# If persistent, may need to update selectors in script
# Check: references/whatsapp-web-selectors.md for current selectors
```

### "Session lost after 2 weeks"

**Expected behavior** - WhatsApp times out sessions for security

**Solution**: Re-authenticate quarterly manually:
```bash
rm .whatsapp_session
python scripts/whatsapp_watcher.py
# Scan QR code
```

## Security & Privacy

✅ **What's stored**: Browser session (cookies, tokens)
✅ **Encrypted**: Session file contains hashed data
✅ **Access**: Only readable by your user account
✅ **Cleanup**: Delete `.whatsapp_session` to fully logout

⚠️ **Don't share**: Session files contain your authentication
⚠️ **Backup**: Include in encrypted backups only
⚠️ **Multi-device**: One session per device (use separate session files)

## Advanced: Multiple Accounts

For multiple WhatsApp accounts:

```bash
# Session 1
WHATSAPP_SESSION_FILE=.whatsapp_session_1 python scripts/whatsapp_watcher.py

# Session 2
WHATSAPP_SESSION_FILE=.whatsapp_session_2 python scripts/whatsapp_watcher.py
```

Create separate `.whatsapp_session_1`, `.whatsapp_session_2` files.

## See Also

- `scripts/whatsapp_watcher.py` - Implementation
- `references/error-recovery.md` - Error handling
- `Company_Handbook.md` - Monitoring configuration
