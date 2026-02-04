# LinkedIn Migration Guide: Browser Automation → REST API v2

## Overview

This guide helps you migrate from browser automation (Playwright) to the official LinkedIn REST API v2.

**Why migrate?**
- ✅ Complies with LinkedIn Terms of Service
- ✅ More reliable (stable API vs fragile UI)
- ✅ Lower resource usage (no browser needed)
- ✅ Better rate limiting and error handling
- ✅ No risk of account suspension

---

## Prerequisites

### 1. Create LinkedIn Developer App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Click **Create App**
3. Fill in:
   - App name: `AI Employee`
   - LinkedIn Page: Select or create a company page
   - App logo: Upload any logo
   - Legal agreement: Check the box
4. Click **Create app**

### 2. Request API Access

1. Go to **Products** tab
2. Request access to:
   - **Share on LinkedIn** (for posting)
   - **Sign In with LinkedIn using OpenID Connect**
3. Wait for approval (usually instant for basic access)

### 3. Configure OAuth2 Settings

1. Go to **Auth** tab
2. Copy:
   - **Client ID**
   - **Client Secret** (click eye icon to reveal)
3. Add Redirect URL: `http://localhost:8080/linkedin/callback`
4. Click **Update**

---

## Migration Steps

### Step 1: Update Environment Variables

Add to your `.env` file:

```bash
# LinkedIn REST API Configuration (replaces browser automation)
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:8080/linkedin/callback

# These will be populated by the OAuth2 setup script
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_PERSON_URN=
LINKEDIN_API_VERSION=202601
```

### Step 2: Run OAuth2 Authentication

```bash
cd /mnt/d/hackathon-0/My_AI_Employee
python scripts/linkedin_oauth2_setup.py
```

**What happens:**
1. Browser opens for LinkedIn authorization
2. You log in and approve the app
3. Access token and Person URN are saved to `.env`
4. You're ready to use the REST API

### Step 3: Test API Connection

```bash
python scripts/test_linkedin_api.py
```

**Expected output:**
```
✅ All tests passed!
Your LinkedIn REST API is configured correctly.
```

### Step 4: Update Watcher Configuration

Replace the old browser automation watcher with the REST API watcher:

**Old (Browser Automation):**
```python
from watchers.linkedin_watcher import LinkedInWatcher  # Browser automation
```

**New (REST API):**
```python
from watchers.linkedin_watcher_api import LinkedInWatcher  # REST API v2
```

Or rename the files:
```bash
# Backup old implementation
mv watchers/linkedin_watcher.py watchers/linkedin_watcher_browser.py.bak

# Use new REST API implementation
mv watchers/linkedin_watcher_api.py watchers/linkedin_watcher.py
```

### Step 5: Update MCP Server Configuration

Replace the old browser automation MCP server with the REST API version:

**Old (Browser Automation):**
```python
# mcp_servers/linkedin_mcp.py - Browser automation
```

**New (REST API):**
```bash
# Backup old implementation
mv mcp_servers/linkedin_mcp.py mcp_servers/linkedin_mcp_browser.py.bak

# Use new REST API implementation
mv mcp_servers/linkedin_mcp_api.py mcp_servers/linkedin_mcp.py
```

### Step 6: Update MCP Server Registration

Update your `.mcp.json` or MCP configuration to use the new server:

```json
{
  "mcpServers": {
    "linkedin-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/mnt/d/hackathon-0/My_AI_Employee",
        "python",
        "/mnt/d/hackathon-0/My_AI_Employee/mcp_servers/linkedin_mcp.py"
      ]
    }
  }
}
```

### Step 7: Test the Integration

**Test the watcher:**
```bash
python run_watcher.py --watcher linkedin
```

**Test the MCP server:**
```bash
# In Claude Code, restart the MCP server
/mcp restart linkedin-mcp

# Test health check
mcp__linkedin-mcp__health_check()

# Test creating a post (optional)
mcp__linkedin-mcp__create_post(
    text="Hello from AI Employee REST API!",
    visibility="PUBLIC",
    hashtags=["automation", "ai"]
)
```

---

## Comparison: Before vs After

### Before (Browser Automation)

**Watcher:**
- Uses Playwright to open browser
- Navigates to linkedin.com
- Clicks buttons to check for updates
- Session stored in JSON file
- Violates LinkedIn ToS
- High resource usage

**MCP Server:**
- Uses Playwright to open browser
- Navigates to linkedin.com
- Clicks buttons to create posts
- Session stored in JSON file
- Risk of account suspension

### After (REST API v2)

**Watcher:**
- Uses REST API v2 endpoints
- OAuth2 authentication
- Direct API calls (no browser)
- Complies with LinkedIn ToS
- Low resource usage

**MCP Server:**
- Uses REST API v2 endpoints
- OAuth2 authentication
- Direct API calls (no browser)
- Official, supported method
- No account suspension risk

---

## API Endpoints Used

### Authentication
- **Authorization**: `https://www.linkedin.com/oauth/v2/authorization`
- **Token Exchange**: `https://www.linkedin.com/oauth/v2/accessToken`
- **User Info**: `https://api.linkedin.com/v2/userinfo`

### Posting
- **Create Post**: `POST https://api.linkedin.com/rest/posts`
- **Get Posts**: `GET https://api.linkedin.com/rest/posts`

### Rate Limits
- **Posts**: 5 posts per day recommended
- **API Calls**: Exponential backoff on 429 errors
- **Retry Logic**: 1s, 2s, 4s, 8s, 16s (max 5 retries)

---

## Troubleshooting

### "LINKEDIN_ACCESS_TOKEN not found"

**Solution:**
```bash
python scripts/linkedin_oauth2_setup.py
```

### "Authentication failed (401 Unauthorized)"

**Cause:** Access token expired (typically after 60 days)

**Solution:**
```bash
python scripts/linkedin_oauth2_setup.py
```

### "Access forbidden (403 Forbidden)"

**Cause:** Missing API permissions

**Solution:**
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Select your app
3. Go to **Products** tab
4. Ensure **Share on LinkedIn** is approved

### "Rate limit exceeded"

**Cause:** Too many API requests

**Solution:**
- Wait for rate limit window to reset
- The MCP server has built-in exponential backoff
- Reduce posting frequency

### "Redirect URI mismatch"

**Cause:** Redirect URI in app settings doesn't match `.env`

**Solution:**
1. Check your app settings at [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Ensure redirect URI exactly matches: `http://localhost:8080/linkedin/callback`
3. No trailing slash, include `http://` prefix

---

## Token Expiration

LinkedIn access tokens typically expire after **60 days**.

**When token expires:**
1. You'll see "Authentication failed (401)" errors
2. Run: `python scripts/linkedin_oauth2_setup.py`
3. Re-authorize the app
4. New token saved to `.env`

**Automatic refresh:**
- LinkedIn doesn't provide refresh tokens for this flow
- You must manually re-authenticate every 60 days
- Consider setting a calendar reminder

---

## Security Best Practices

1. **Never commit `.env` to git** - Already in `.gitignore`
2. **Rotate tokens periodically** - Every 60 days (when they expire)
3. **Use least privilege** - Only request needed scopes
4. **Monitor API usage** - Check LinkedIn Developer dashboard
5. **Secure your redirect URI** - Use localhost for development

---

## Files Created

### New Files (REST API)
- `scripts/linkedin_oauth2_setup.py` - OAuth2 authentication helper
- `scripts/test_linkedin_api.py` - API connection test
- `watchers/linkedin_watcher_api.py` - REST API watcher
- `mcp_servers/linkedin_mcp_api.py` - REST API MCP server

### Old Files (Browser Automation) - Can be deleted
- `watchers/linkedin_watcher.py` - Browser automation watcher
- `mcp_servers/linkedin_mcp.py` - Browser automation MCP server

### Configuration
- `.env` - Updated with LinkedIn REST API credentials
- `.env.example` - Updated with LinkedIn REST API template

---

## Next Steps

After migration:

1. **Delete old browser automation code:**
   ```bash
   rm watchers/linkedin_watcher_browser.py.bak
   rm mcp_servers/linkedin_mcp_browser.py.bak
   ```

2. **Remove Playwright dependency (if only used for LinkedIn):**
   ```bash
   # Check if Playwright is used elsewhere (WhatsApp)
   # If not, remove from pyproject.toml
   ```

3. **Test the full workflow:**
   - Watcher detects LinkedIn activity
   - Creates action items in vault
   - Approval workflow processes items
   - MCP server posts to LinkedIn

4. **Monitor API usage:**
   - Check LinkedIn Developer dashboard
   - Monitor rate limits
   - Track token expiration

---

## Support

**LinkedIn Developer Documentation:**
- [REST API v2](https://learn.microsoft.com/en-us/linkedin/)
- [OAuth2 Authentication](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [Share on LinkedIn](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)

**Troubleshooting:**
- Check logs: `tail -f logs/linkedin_watcher.log`
- Test API: `python scripts/test_linkedin_api.py`
- Re-authenticate: `python scripts/linkedin_oauth2_setup.py`

---

## Summary

✅ **Migration Complete!**

You've successfully migrated from browser automation to the official LinkedIn REST API v2:

- ✅ Complies with LinkedIn Terms of Service
- ✅ More reliable and maintainable
- ✅ Lower resource usage
- ✅ No account suspension risk
- ✅ Better error handling and rate limiting

**Your LinkedIn integration is now production-ready!**
