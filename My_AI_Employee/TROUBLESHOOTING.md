# Silver Tier AI Employee - Troubleshooting Guide

Common issues and solutions for Silver Tier deployment.

---

## Table of Contents

1. [Credential Issues](#credential-issues)
2. [Watcher Issues](#watcher-issues)
3. [Orchestrator Issues](#orchestrator-issues)
4. [PM2 Issues](#pm2-issues)
5. [Network & API Issues](#network--api-issues)
6. [Vault & File Issues](#vault--file-issues)

---

## Credential Issues

### Gmail: "401 Unauthorized" Error

**Symptom**: Gmail watcher crashes with `401 Unauthorized`

**Cause**: OAuth token expired or invalid

**Solution**:
```bash
# Re-run OAuth setup
uv run python scripts/setup/setup_gmail_oauth.py

# Verify token
uv run python scripts/debug/debug_gmail.py
```

**Prevention**: Google OAuth tokens refresh automatically if `refresh_token` is present in `token.json`

---

### LinkedIn: "401 Unauthorized" Error

**Symptom**: LinkedIn watcher crashes with `401 Unauthorized`

**Cause**: Access token expired (LinkedIn tokens expire after 60 days)

**Solution**:
```bash
# Re-run OAuth setup
uv run python scripts/setup/linkedin_oauth2_setup.py

# Verify new token
uv run python scripts/debug/debug_linkedin.py

# Update .env with new token
```

**Prevention**: Set calendar reminder to refresh token every 50 days

---

### WhatsApp: QR Code Appears

**Symptom**: WhatsApp watcher shows QR code instead of chat list

**Cause**: Session expired (expires every ~2 weeks)

**Solution**:
```bash
# Re-scan QR code
uv run python scripts/setup/whatsapp_auth.py

# Verify session
uv run python scripts/debug/debug_whatsapp.py
```

**Prevention**: Set calendar reminder to refresh session every 10 days

---

### Credentials Found in Vault/Repo

**Symptom**: Security scan fails with "Credentials detected"

**Cause**: API keys or tokens committed to git or saved in vault

**Solution**:
```bash
# Run security scan to identify files
uv run python scripts/validate/validate_silver_tier.py

# Move credentials to .env
# Update code to use: os.getenv('API_KEY')

# Remove from git history (if committed)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/file" \
  --prune-empty --tag-name-filter cat -- --all

# Verify .env in .gitignore
grep "^\.env$" .gitignore

# Re-run security scan
uv run python scripts/validate/validate_silver_tier.py
```

**Prevention**: Always use `.env` for credentials, never hardcode

---

## Watcher Issues

### Watcher Not Processing New Items

**Symptom**: New emails/messages arrive but no action items created

**Diagnostic Steps**:
```bash
# 1. Check watcher is running
pm2 status

# 2. Check watcher logs
pm2 logs gmail-watcher

# 3. Check for errors
pm2 logs gmail-watcher --err

# 4. Check deduplication state
cat .gmail_dedupe.json | jq
cat .whatsapp_dedupe.json | jq
cat .linkedin_dedupe.json | jq

# 5. Verify vault writable
ls -la AI_Employee_Vault/Needs_Action/
```

**Common Causes**:

1. **Deduplication preventing processing**:
   - Solution: Delete dedupe state file: `rm .gmail_dedupe.json`

2. **Vault permissions**:
   - Solution: `chmod -R u+w AI_Employee_Vault/`

3. **Watcher crashed silently**:
   - Solution: `pm2 restart ecosystem.config.js`

---

### Gmail Watcher: "Insufficient Permissions"

**Symptom**: Gmail API returns 403 Forbidden

**Cause**: OAuth scopes missing

**Solution**:
```bash
# Check current scopes
cat token.json | jq .scopes

# Required scope: "https://www.googleapis.com/auth/gmail.modify"

# If missing, re-run setup
rm token.json
uv run python scripts/setup/setup_gmail_oauth.py

# Ensure GMAIL_SCOPES in .env includes gmail.modify
```

---

### WhatsApp Watcher: Browser Crashes

**Symptom**: Playwright browser crashes with "Target closed"

**Cause**: WhatsApp Web timeout or session expired

**Solution**:
```bash
# 1. Check session validity
uv run python scripts/debug/debug_whatsapp.py

# 2. If expired, re-authenticate
uv run python scripts/setup/whatsapp_auth.py

# 3. Increase timeout in .env (optional)
# Add to .env:
WHATSAPP_TIMEOUT=60000  # 60 seconds
```

**Prevention**: Keep WhatsApp mobile app online and connected to internet

---

## Orchestrator Issues

### Actions Not Executing

**Symptom**: Approval requests in /Approved/ but not executed

**Diagnostic Steps**:
```bash
# 1. Check orchestrator running
pm2 status orchestrator

# 2. Check orchestrator logs
pm2 logs orchestrator

# 3. Check /Approved/ folder
ls -la AI_Employee_Vault/Approved/

# 4. Verify orchestrator polling interval
grep ORCHESTRATOR_CHECK_INTERVAL .env
```

**Common Causes**:

1. **Orchestrator not running**:
   - Solution: `pm2 restart orchestrator`

2. **File naming incorrect**:
   - Requires: `*-approved.md` suffix
   - Solution: Rename file to match pattern

3. **Execution plan missing**:
   - Approval request must have YAML execution plan
   - Solution: Re-create approval request with proper format

---

### Orchestrator Retry Loop

**Symptom**: Orchestrator retries action indefinitely

**Cause**: Transient error with retry logic

**Solution**:
```bash
# 1. Check logs for error type
pm2 logs orchestrator | grep "error_type"

# 2. If non-transient error, manually move to /Failed/
mv AI_Employee_Vault/Approved/ACTION_ID-approved.md \
   AI_Employee_Vault/Failed/ACTION_ID-failed.md

# 3. Add failure reason to frontmatter
# Edit file and add:
# error_message: "Manual intervention required"
```

**Non-retryable errors**:
- `authentication_failure` - Fix credentials
- `unknown_mcp_server` - Fix execution plan
- `validation_error` - Fix input parameters

---

## PM2 Issues

### PM2 Auto-Restart Loop

**Symptom**: Process restarts continuously, never stays up

**Cause**: Process crashes immediately on startup

**Diagnostic Steps**:
```bash
# 1. Check error logs
pm2 logs <process-name> --err

# 2. Check restart count
pm2 status

# 3. Stop auto-restart temporarily
pm2 stop <process-name>

# 4. Run process manually to see error
uv run python src/my_ai_employee/<script>.py
```

**Common Causes**:

1. **Missing dependencies**:
   - Solution: `uv sync`

2. **Invalid configuration**:
   - Solution: Check `.env` file for typos

3. **Permission errors**:
   - Solution: `chmod -R u+w AI_Employee_Vault/`

---

### PM2 Processes Not Starting

**Symptom**: `pm2 start ecosystem.config.js` fails

**Cause**: PM2 configuration error or missing PM2

**Solution**:
```bash
# 1. Verify PM2 installed
pm2 --version

# If not installed:
npm install pm2 -g

# 2. Validate ecosystem.config.js syntax
node -c ecosystem.config.js

# 3. Check logs for specific error
pm2 logs

# 4. Start processes individually
pm2 start "uv run python src/my_ai_employee/run_gmail_watcher.py" --name gmail-watcher
```

---

## Network & API Issues

### Rate Limiting

**Symptom**: "429 Too Many Requests" errors

**Cause**: Exceeded API rate limits

**Solution (Gmail)**:
```bash
# Check quota usage in Google Cloud Console
# Increase CHECK_INTERVAL in .env to reduce requests
CHECK_INTERVAL=120  # Check every 2 minutes instead of 60

# Restart watchers
pm2 restart ecosystem.config.js
```

**Solution (LinkedIn)**:
```bash
# LinkedIn has strict rate limits
# Increase CHECK_INTERVAL to 300+ seconds
CHECK_INTERVAL=300  # Check every 5 minutes

# MCP servers have built-in exponential backoff
# Check logs for retry behavior
pm2 logs linkedin-watcher | grep "retry"
```

---

### Network Timeout Errors

**Symptom**: "Connection timeout" or "Network unreachable"

**Cause**: Slow or unstable internet connection

**Solution**:
```bash
# 1. Check internet connection
ping 8.8.8.8

# 2. Increase timeouts in code (if needed)
# MCP servers have 30s default timeout

# 3. Check firewall/proxy settings
# Ensure HTTPS outbound allowed

# 4. Verify API endpoints accessible
curl -I https://www.googleapis.com/gmail/v1/users/me/profile
curl -I https://api.linkedin.com/v2/me
curl -I https://web.whatsapp.com
```

---

## Vault & File Issues

### YAML Frontmatter Corruption

**Symptom**: Action items can't be parsed, errors mentioning YAML

**Cause**: Manual edits broke YAML syntax

**Diagnostic Steps**:
```bash
# 1. Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('AI_Employee_Vault/Needs_Action/ITEM.md').read())"

# 2. Check for common issues:
# - Missing closing quotes
# - Incorrect indentation
# - Special characters not escaped
```

**Solution**:
```bash
# Fix YAML manually or recreate file
# Use frontmatter library in Python:
python -c "
import frontmatter
post = frontmatter.load('FILE.md')
post.metadata['field'] = 'value'
with open('FILE.md', 'w') as f:
    frontmatter.dump(post, f)
"
```

---

### Dashboard Not Updating

**Symptom**: Dashboard.md shows stale data

**Cause**: Orchestrator not calling dashboard updater

**Solution**:
```bash
# 1. Check orchestrator logs
pm2 logs orchestrator | grep "dashboard"

# 2. Manually trigger update
# Execute an action and verify Dashboard.md timestamp changes

# 3. Check Dashboard.md permissions
ls -la AI_Employee_Vault/Dashboard.md
chmod u+w AI_Employee_Vault/Dashboard.md
```

---

### Lost Files During Workflow

**Symptom**: Action items disappear between folders

**Cause**: File move operation failed

**Diagnostic Steps**:
```bash
# 1. Check all workflow folders
ls AI_Employee_Vault/Needs_Action/
ls AI_Employee_Vault/Pending_Approval/
ls AI_Employee_Vault/Approved/
ls AI_Employee_Vault/Done/
ls AI_Employee_Vault/Failed/
ls AI_Employee_Vault/Rejected/

# 2. Search by action_id
grep -r "ACTION_ID" AI_Employee_Vault/

# 3. Check orchestrator logs for move operations
pm2 logs orchestrator | grep "move"
```

**Prevention**: Dashboard.md tracks recent activity - check there first

---

## Still Having Issues?

### Debug Workflow

1. **Run all debug scripts**:
   ```bash
   uv run python scripts/debug/debug_gmail.py
   uv run python scripts/debug/debug_linkedin.py
   uv run python scripts/debug/debug_whatsapp.py
   ```

2. **Check security scan**:
   ```bash
   uv run python scripts/validate/validate_silver_tier.py
   ```

3. **Review all logs**:
   ```bash
   pm2 logs --lines 100
   ```

4. **Check audit trail**:
   ```bash
   cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq
   ```

### Getting Help

Include the following in your bug report:

- **Environment**: OS, Python version, UV version
- **Logs**: `pm2 logs` output (sanitize credentials!)
- **Configuration**: `.env` contents (sanitize credentials!)
- **Steps to reproduce**: Exact commands that trigger issue
- **Expected vs actual behavior**

---

## Appendix: Log Formats

### Audit Log Format

```json
{
  "timestamp": "2026-01-24T10:30:00",
  "action_type": "send_email",
  "execution_status": "success",
  "executor": "ai_employee",
  "executor_id": "orchestrator",
  "tool_name": "send_email",
  "tool_inputs_sanitized": {
    "to": "[EMAIL_REDACTED]",
    "subject": "Re: Meeting Request"
  },
  "mcp_server": "email",
  "error": null,
  "retry_count": 0
}
```

### PM2 Log Format

```
2026-01-24 10:30:00: [gmail-watcher] INFO - Heartbeat: gmail_watcher running
2026-01-24 10:30:05: [gmail-watcher] INFO - Found 3 unread email(s)
2026-01-24 10:30:05: [gmail-watcher] INFO - Created action item: 20260124-103005-email-abc123.md
```

### Dashboard Format

```markdown
# AI Employee Dashboard

Last updated: 2026-01-24 10:30:00

## System Status

- **Status**: 🟢 Running
- **Mode**: Production
- **Uptime**: 2 hours

## Pending Actions

### Awaiting Approval
- **Pending Approvals**: 2 action(s) in `/Pending_Approval/`

### In Progress
- **Needs Action**: 5 item(s) in `/Needs_Action/`

## Recent Activity

### Last 10 Actions
- ✅ **send_email** (20260124-email-001) - success - 2026-01-24 10:25:00
- ❌ **publish_linkedin_post** (20260124-linkedin-001) - failed - 2026-01-24 10:20:00
```
