# SMTP Quick Start Guide

## Use Gmail API (Default - Recommended for Security)

```bash
# .env
EMAIL_BACKEND=gmail
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
```

**Setup**:
1. Download credentials.json from Google Cloud Console
2. Run executor once (will prompt for OAuth)
3. Done! Token auto-refreshes

---

## Use SMTP (Universal - Works with Any Email Provider)

### Gmail with SMTP

```bash
# .env
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@gmail.com
SMTP_PASSWORD=your-app-specific-password
```

**Setup**:
1. Get app-specific password: https://myaccount.google.com/apppasswords
2. Copy password to SMTP_PASSWORD
3. Done!

### Outlook

```bash
# .env
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your@outlook.com
SMTP_PASSWORD=your-password
```

### Custom SMTP Server

```bash
# .env
EMAIL_BACKEND=smtp
SMTP_HOST=mail.yourcompany.com
SMTP_PORT=587
SMTP_USERNAME=user@yourcompany.com
SMTP_PASSWORD=your-password
SMTP_FROM_ADDRESS=noreply@yourcompany.com
```

---

## How It Works

**Same tool, different backend**:

```python
send_email(
    to="user@example.com",
    subject="Hello",
    body="Message here"
)
```

**What changes**: Only which backend sends the email
- `EMAIL_BACKEND=gmail` → Uses Gmail API (OAuth)
- `EMAIL_BACKEND=smtp` → Uses SMTP server (TLS)

**Result includes backend used**:
```json
{
  "success": true,
  "message_id": "...",
  "backend_used": "gmail"  // or "smtp"
}
```

---

## Switching Backends

1. Change `EMAIL_BACKEND` in .env
2. Set backend credentials
3. Restart executor
4. Next email uses new backend ✅

**No code changes needed!**

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Gmail: "credentials.json not found" | Download from Google Cloud Console |
| Gmail: OAuth prompt doesn't appear | Check if running headless server |
| SMTP: "Authentication failed" | Check username/password (Gmail needs app password) |
| SMTP: "Connection timeout" | Check SMTP_HOST and SMTP_PORT |
| SMTP: "TLS error" | Make sure SMTP_PORT=587 (not 465 for TLS) |

---

## Test Your Configuration

```python
# In Python shell:
from scripts.email_mcp import get_email_backend, EmailRequest

backend = get_email_backend()
print(f"Backend type: {type(backend).__name__}")

# Should print:
# Backend type: GmailBackend  (if EMAIL_BACKEND=gmail)
# Backend type: SMTPBackend   (if EMAIL_BACKEND=smtp)
```

---

## Full Configuration Reference

See `templates/env_template.txt` for complete configuration options.

See `references/fastmcp-servers.md` for detailed documentation.

See `examples.md` for real usage examples.
