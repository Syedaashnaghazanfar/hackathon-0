# Watcher Error Recovery & Troubleshooting

## Automatic Recovery Mechanisms

All watchers have built-in recovery:

1. **Health Checks** - Every 30 seconds
2. **Exponential Backoff** - 1s → 5s → 10s → 30s
3. **Auto-Restart** - Up to 5 retries
4. **Session Persistence** - WhatsApp doesn't need re-scan
5. **Token Refresh** - Gmail OAuth auto-refresh
6. **Dead-Letter Logging** - Failed items logged separately

## Common Errors & Fixes

### 1. Gmail Watcher

#### Error: "Gmail API: 403 Forbidden"
```
Cause: API not enabled or invalid scopes
Fix:   1. Enable Gmail API in Google Cloud Console
      2. Delete token.json
      3. Re-authenticate: python scripts/gmail_watcher.py
```

#### Error: "Invalid OAuth token"
```
Cause: Token revoked or expired > 24hrs
Fix:   1. rm credentials.json token.json
      2. Download new credentials.json from Google Cloud
      3. python scripts/gmail_watcher.py
```

#### Error: "Rate limit exceeded"
```
Cause: Gmail API rate limit (500 requests/second)
Fix:   Automatic - watcher backs off 5 minutes
      Normal for < 100 emails/day
```

### 2. WhatsApp Watcher

#### Error: "Browser not launching"
```
Cause: Chromium not installed
Fix:   playwright install chromium
```

#### Error: "Timeout: Element not found"
```
Cause: WhatsApp Web UI changed or network slow
Fix:   1. Wait 30s (watcher auto-retries)
      2. Check internet connection
      3. If persistent: rm .whatsapp_session && re-authenticate
```

#### Error: "Session expired - scan QR code"
```
Cause: Session timeout (after 2+ weeks)
Fix:   1. rm .whatsapp_session
      2. python scripts/whatsapp_watcher.py
      3. Scan QR code when browser opens
```

#### Error: "Cannot connect to Chromium"
```
Cause: Port already in use or Chromium crashed
Fix:   1. pkill -f chromium
      2. ps aux | grep chromium (verify killed)
      3. python scripts/whatsapp_watcher.py
```

### 3. LinkedIn Watcher

#### Error: "LinkedIn token expired"
```
Cause: API token > 90 days old
Fix:   1. Generate new token: https://www.linkedin.com/developers/apps
      2. Update .env: LINKEDIN_ACCESS_TOKEN=new_token
      3. Restart watcher
```

#### Error: "Rate limit: Try again in 1 hour"
```
Cause: LinkedIn API rate limit (500 requests/hour)
Fix:   Automatic - watcher waits 1 hour then retries
      Reduce check frequency in Company_Handbook.md
```

#### Error: "Unauthorized - invalid token format"
```
Cause: Token invalid or truncated in .env
Fix:   1. Verify token in .env (no spaces, full length)
      2. Generate new token if needed
      3. LINKEDIN_ACCESS_TOKEN="exact_token_from_linkedin"
```

### 4. Filesystem Watcher

#### Error: "Watch folder does not exist"
```
Cause: WATCH_FOLDER path wrong or deleted
Fix:   1. Check .env: WATCH_FOLDER=My_AI_Employee/test_watch_folder
      2. Create folder if missing: mkdir -p "My_AI_Employee/test_watch_folder"
      3. Verify path permissions: ls -la "My_AI_Employee/test_watch_folder"
```

#### Error: "Permission denied writing to Needs_Action"
```
Cause: Vault folder permissions issue
Fix:   1. Check vault permissions: ls -la "My_AI_Employee/AI_Employee_Vault"
      2. Add write permission: chmod 755 "My_AI_Employee/AI_Employee_Vault"
      3. Check disk space: df -h
```

#### Error: "File too large to process"
```
Cause: File > 100MB (or configured limit)
Fix:   1. Move large file from watch folder
      2. Increase limit: WATCHER_MAX_FILE_SIZE=500MB
      3. Split large files into smaller parts
```

## Watcher Status Monitoring

### Check All Watchers

```bash
python scripts/monitor_watchers.py
```

**Output:**
```
Multi-Watcher Status Report
Generated: 2026-01-14 10:30:00 UTC

GMAIL WATCHER
  Status: ✅ online
  Last Check: 2026-01-14 10:29:45 (15 seconds ago)
  Uptime: 99.8% (24h)
  Items Created Today: 3
  Error Count: 0

WHATSAPP WATCHER
  Status: ✅ online
  Last Check: 2026-01-14 10:29:50 (10 seconds ago)
  Uptime: 98.5% (24h)
  Items Created Today: 1
  Session Active: Yes
  Error Count: 1 (recovered)

LINKEDIN WATCHER
  Status: ⚠️  retrying (attempt 2/5)
  Last Check: 2026-01-14 10:29:30 (30 seconds ago)
  Uptime: 95.2% (24h)
  Items Created Today: 0
  Error: Rate limit - retry at 10:45

FILESYSTEM WATCHER
  Status: ✅ online
  Last Check: 2026-01-14 10:29:59 (1 second ago)
  Uptime: 100% (24h)
  Items Created Today: 2
  Error Count: 0

OVERALL
  Watchers Online: 3/4
  Average Uptime: 98.4%
  Total Items Created: 6
  Next Health Check: 2026-01-14 10:30:30
```

### View Logs

```bash
# All watchers
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

## Restart Operations

### Restart All Watchers

```bash
python scripts/orchestrate_watchers.py --restart-all
```

### Restart Specific Watcher

```bash
python scripts/restart_watcher.py gmail
python scripts/restart_watcher.py whatsapp
python scripts/restart_watcher.py linkedin
python scripts/restart_watcher.py filesystem
```

### Graceful Shutdown

```bash
python scripts/orchestrate_watchers.py --stop
```

Waits for watchers to finish current checks, then stops cleanly.

## PM2 Management (24/7 Operation)

### Start with PM2

```bash
pm2 start scripts/orchestrate_watchers.py --name "multi-watchers" --interpreter python3

# Logs
pm2 logs multi-watchers

# Status
pm2 status

# Restart
pm2 restart multi-watchers

# Stop
pm2 stop multi-watchers

# Delete
pm2 delete multi-watchers
```

### PM2 Auto-Start on Boot

```bash
pm2 startup
pm2 save
```

Now PM2 watchers start automatically on system reboot.

## Performance Tuning

### Check Frequency (vs. Resource Usage)

| Setting | CPU | Memory | Latency | Recommendation |
|---------|-----|--------|---------|---|
| Every 1 min | High | High | Fast | Not recommended |
| Every 5 min | Medium | Medium | Medium | Good balance |
| Every 10 min | Low | Low | Slower | Battery-friendly |

Adjust in Company_Handbook.md watcher sections.

### Parallel Execution

Watchers run in parallel threads (not sequential):
- ✅ Gmail + WhatsApp + LinkedIn checks happen simultaneously
- ✅ No waiting for one watcher before starting next
- ✅ Faster response to new messages

## Dead-Letter Queue

When a watcher fails 5 times and goes offline:

- Logged to: `logs/dead-letter.log`
- Manual recovery: `python scripts/restart_watcher.py <name>`
- Alert: Dashboard shows red indicator

Example dead-letter entry:
```
2026-01-14 14:32:10 - LinkedIn Watcher
Reason: Persistent rate limit after 5 retries
Last Error: Rate limit: Try again in 1 hour
Attempts: 5
Time: 2 hours
Status: Dead (manual intervention required)
```

## Backup & Recovery

### Session Files to Backup

```
.whatsapp_session      (Backup encrypted)
token.json             (Backup encrypted)
credentials.json       (Backup encrypted)
```

### Disaster Recovery

```bash
# If all watchers crash:
rm logs/*
python scripts/orchestrate_watchers.py

# If you lose .whatsapp_session:
# No data loss - just need to re-scan QR code

# If you lose token.json:
# Need Gmail OAuth re-authentication (2 minutes)
```

## Performance Metrics

Monitor health dashboard:

```bash
python scripts/monitor_watchers.py --interval 10
```

Shows real-time metrics:
- Items/hour rate
- Error rate
- Response time
- Uptime %
- Memory usage
- CPU usage
