# Gmail API OAuth Setup

## Prerequisites

- Google Cloud Project created
- Gmail API enabled
- OAuth 2.0 consent screen configured

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Personal AI Employee"
3. Enable Gmail API:
   - Search "Gmail API"
   - Click "Enable"

## Step 2: Create OAuth 2.0 Credentials

1. Go to **Credentials** → **Create Credentials**
2. Choose: "OAuth 2.0 Client ID"
3. Application type: "Desktop application"
4. Download JSON → save as `credentials.json` in project root

## Step 3: Configure OAuth Consent Screen

1. Go to **OAuth consent screen**
2. User type: "External"
3. Fill required fields:
   - App name: "Personal AI Employee"
   - User support email: your@email.com
   - Developer contact: your@email.com
4. Scopes → Add scope:
   - Search: "gmail.readonly"
   - Select: `https://www.googleapis.com/auth/gmail.readonly`
5. Save

## Step 4: First Run - OAuth Flow

First time you run the Gmail watcher:

```bash
uv run python run_watcher.py --watcher gmail
```

**Output:**
```
Opening browser for Gmail authentication...
Please authorize the app in your browser.
✅ Authentication successful!
Token saved to: .env (GMAIL_TOKEN_FILE)
```

The browser opens automatically. Sign in with your Gmail account and grant permission.

## Token Management

### Token File Location
- Stored in: `.env` → `GMAIL_TOKEN_FILE=token.json`
- Contains: Access token + refresh token

### Auto-Refresh
- Tokens auto-refresh 1 hour before expiry
- No manual intervention needed
- Watcher handles all refresh logic

### Token Expiry & Issues

**If token expires (24+ hours):**
```bash
# Delete old token and re-authenticate
rm token.json
uv run python scripts/setup/setup_gmail_oauth.py
# Follow OAuth flow again
```

**Common Issues:**
- `PERMISSION_DENIED` → Re-run OAuth flow
- `INVALID_GRANT` → Token revoked, delete and re-auth
- `RATE_LIMIT` → Wait 1 hour, watcher will retry

## Scopes Explained

### `gmail.readonly` (Current)
- ✅ Read emails
- ✅ Read labels, threads, messages
- ❌ Send emails (use Email MCP instead)
- ❌ Modify labels
- ❌ Trash/delete

### Alternative Scopes (Not Used)
- `gmail.modify` - Full email control (too permissive)
- `gmail.send` - Send emails (use Email MCP)

### Why Read-Only?
✅ Security: Watcher can only READ, not modify
✅ Safety: Can't accidentally delete emails
✅ Simplicity: Sending handled by MCP servers
✅ Least privilege: Only what's needed

## Troubleshooting

### "googleapis.error: 403 Forbidden"

**Cause**: Gmail API not enabled or scope mismatch

**Fix**:
1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Search "Gmail API"
3. Click **Enable**
4. Wait 5-10 minutes for propagation
5. Re-run watcher

### "Failed to fetch access token"

**Cause**: Invalid credentials.json or token file corrupted

**Fix**:
```bash
# Delete both and re-authenticate
rm credentials.json token.json
# Place new credentials.json from Google Cloud Console
uv run python scripts/setup/setup_gmail_oauth.py
```

### "ECONNREFUSED during OAuth flow"

**Cause**: Browser can't reach localhost callback

**Fix**:
```bash
# Ensure port 8080 is free
lsof -i :8080  # Check what's using port 8080

# Or use environment variable
GMAIL_OAUTH_PORT=8081 uv run python scripts/setup/setup_gmail_oauth.py
```

## Security Notes

⚠️ **Never commit credentials.json or token.json to git**

✅ Add to `.gitignore`:
```
credentials.json
token.json
.env
```

✅ Store in `.env` securely:
```bash
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
```

✅ Use environment variables only

## Advanced: Service Account (Optional)

For fully automated setup without OAuth popup:

1. Create Service Account in Google Cloud Console
2. Download service account JSON
3. Share Gmail with service account email
4. Use service account JSON instead of OAuth

Note: This adds complexity. OAuth flow recommended for personal use.
