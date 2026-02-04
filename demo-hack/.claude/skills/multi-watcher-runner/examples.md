# Multi-Watcher Runner – Examples

Run and orchestrate multiple watchers (Gmail, LinkedIn, WhatsApp, Filesystem) using the unified watcher runner.

---

## Example 1: Start All Watchers with Orchestration

### User Prompt

```
Start all Silver tier watchers with health monitoring
```

### Expected Execution

```bash
# Start all watchers with orchestration
uv run python run_watcher.py --watcher all
```

### Expected Output

```
2026-01-18 16:00:00 - INFO - ============================================================
2026-01-18 16:00:00 - INFO - Silver Tier - All Watchers (Orchestrated)
2026-01-18 16:00:00 - INFO - ============================================================
2026-01-18 16:00:00 - INFO - Vault: /path/to/AI_Employee_Vault
2026-01-18 16:00:00 - INFO - Health check interval: 30s
2026-01-18 16:00:00 - INFO - ============================================================
2026-01-18 16:00:00 - INFO - Starting all watchers
2026-01-18 16:00:00 - INFO - Starting gmail watcher
2026-01-18 16:00:00 - INFO - ✅ gmail watcher started successfully
2026-01-18 16:00:00 - INFO - Starting linkedin watcher
2026-01-18 16:00:00 - INFO - ✅ linkedin watcher started successfully
2026-01-18 16:00:00 - INFO - Starting whatsapp watcher
2026-01-18 16:00:00 - INFO - ✅ whatsapp watcher started successfully
2026-01-18 16:00:00 - INFO - Starting filesystem watcher
2026-01-18 16:00:00 - INFO - ✅ filesystem watcher started successfully
2026-01-18 16:00:00 - INFO - All watchers started

# Status updates every 30 seconds
2026-01-18 16:00:30 - INFO - ============================================================
2026-01-18 16:00:30 - INFO - Multi-Watcher Orchestrator Status
2026-01-18 16:00:30 - INFO - Started: 2026-01-18 16:00:00
2026-01-18 16:00:30 - INFO - Uptime: 0:00:30
2026-01-18 16:00:30 - INFO - GMAIL        | Status: online   | OK:   1 | Fail:   0 | Items:  0 | Uptime: 100.0%
2026-01-18 16:00:30 - INFO - LINKEDIN     | Status: online   | OK:   1 | Fail:   0 | Items:  0 | Uptime: 100.0%
2026-01-18 16:00:30 - INFO - WHATSAPP     | Status: online   | OK:   1 | Fail:   0 | Items:  0 | Uptime: 100.0%
2026-01-18 16:00:30 - INFO - FILESYSTEM   | Status: online   | OK:   1 | Fail:   0 | Items:  0 | Uptime: 100.0%
2026-01-18 16:00:30 - INFO - ============================================================
```

---

## Example 2: Run Individual Silver Tier Watcher

### User Prompt

```
Run only the Gmail watcher for testing
```

### Expected Execution

```bash
# Gmail watcher only
uv run python run_watcher.py --watcher gmail --log-level DEBUG

# LinkedIn watcher only
uv run python run_watcher.py --watcher linkedin

# WhatsApp watcher only
uv run python run_watcher.py --watcher whatsapp

# Filesystem watcher only (Bronze tier)
uv run python run_watcher.py --watcher filesystem
```

---

## Example 3: Gmail Watcher - Email Detection

### User Prompt

```
Test Gmail watcher by sending a test email
```

### Expected Execution

```bash
# Terminal 1: Start Gmail watcher
uv run python run_watcher.py --watcher gmail --log-level DEBUG

# Terminal 2: Send test email to yourself
# Subject: URGENT: Test Request
# Body: Please review this test email ASAP
```

### Expected Output

```
2026-01-18 16:01:00 - INFO - Checking for new items...
2026-01-18 16:01:00 - INFO - Found 1 new message(s)
2026-01-18 16:01:00 - INFO - Processing message from: you@gmail.com
2026-01-18 16:01:00 - INFO - Subject: URGENT: Test Request
2026-01-18 16:01:00 - INFO - Priority: High (urgent, asap keywords detected)
2026-01-18 16:01:00 - INFO - Created action file: 20260118_160100_123456_email_you@gmail.com.md
```

### Verify Action Item

```bash
# Check Needs_Action folder
ls -lh AI_Employee_Vault/Needs_Action/ | grep email

# View the created action item
cat AI_Employee_Vault/Needs_Action/20260118_160100_*_email_*.md
```

---

## Example 4: Setup Gmail OAuth (First Time)

### User Prompt

```
Set up Gmail OAuth credentials for the first time
```

### Expected Execution

```bash
# Run OAuth setup script
uv run python scripts/setup/setup_gmail_oauth.py

# Follow prompts:
# 1. Browser opens for Google OAuth
# 2. Select your Google account
# 3. Grant permissions
# 4. Token saved to token.json

# Verify connection
uv run python scripts/debug/debug_gmail.py

# Start Gmail watcher
uv run python run_watcher.py --watcher gmail
```

---

## Example 5: WhatsApp Watcher - First Run (QR Code)

### User Prompt

```
Set up WhatsApp watcher for the first time
```

### Expected Execution

```bash
# Start WhatsApp watcher (first run)
uv run python run_watcher.py --watcher whatsapp

# Expected:
# 1. Browser opens showing WhatsApp Web
# 2. QR code displayed
# 3. Scan QR code with your phone's WhatsApp app
# 4. Browser closes after authentication
# 5. Session saved to .whatsapp_session
# 6. Watcher starts monitoring
```

### Subsequent Runs

```bash
# After first setup, no QR code needed
uv run python run_watcher.py --watcher whatsapp

# Session is loaded from .whatsapp_session
# Watcher starts immediately
```

---

## Example 6: Production Deployment with PM2

### User Prompt

```
Deploy all watchers to production with PM2
```

### Expected Execution

```bash
# Install PM2 globally
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'ai-employee-watchers',
    script: 'run_watcher.py',
    args: '--watcher all',
    interpreter: 'uv',
    interpreter_args: 'run python',
    cwd: '/path/to/My_AI_Employee',
    autorestart: true,
    max_restarts: 10,
    min_uptime: '10s',
    error_file: 'logs/pm2-error.log',
    out_file: 'logs/pm2-out.log'
  }]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js

# Monitor
pm2 monit

# View logs
pm2 logs ai-employee-watchers

# Auto-start on system reboot
pm2 startup
pm2 save
```

---

## Example 7: Troubleshooting Gmail OAuth Errors

### User Prompt

```
Gmail watcher fails with "OAuth authentication failed"
```

### Expected Execution

```bash
# 1. Delete expired token
rm token.json

# 2. Re-run OAuth setup
uv run python scripts/setup/setup_gmail_oauth.py

# 3. Verify connection
uv run python scripts/debug/debug_gmail.py

# 4. Start watcher
uv run python run_watcher.py --watcher gmail
```

---

## Example 8: Troubleshooting WhatsApp Session Expiry

### User Prompt

```
WhatsApp watcher fails with "Session expired"
```

### Expected Execution

```bash
# 1. Delete expired session
rm .whatsapp_session

# 2. Restart watcher (will show QR code)
uv run python run_watcher.py --watcher whatsapp

# 3. Scan QR code with phone
# 4. New session saved automatically
```

---

## Example 9: Complete Silver Tier Workflow

### User Prompt

```
Demonstrate complete Silver tier workflow from email to execution
```

### Expected Execution

```bash
# Step 1: Start all watchers
uv run python run_watcher.py --watcher all

# Step 2: Send test email to yourself
# Subject: URGENT: Client Request
# Body: Please send proposal to client@example.com ASAP

# Step 3: Watcher detects email and creates action item
# AI_Employee_Vault/Needs_Action/20260118_*_email_*.md

# Step 4: Process with needs-action-triage
# In Claude Code:
/needs-action-triage

# Step 5: Approve action in Pending_Approval/
# Manually move file to Approved/

# Step 6: Execute approved action
# In Claude Code:
/mcp-executor

# Step 7: Email sent via Gmail API
# Original file moved to Done/
```

---

## Example 10: Validation Before Deployment

### User Prompt

```
Validate Silver tier setup before deploying to production
```

### Expected Execution

```bash
# Run validation script
uv run python scripts/validate/validate_silver_tier.py

# Checks:
# ✅ Vault structure exists
# ✅ .env configuration valid
# ✅ Gmail OAuth credentials present
# ✅ Watch folder exists
# ✅ Dashboard updates work
# ✅ Audit logging works

# If all pass, deploy to production
pm2 start ecosystem.config.js
```

---

## Example 11: Monitoring Watcher Health

### User Prompt

```
Monitor health of all running watchers
```

### Expected Execution

```bash
# Watchers log status every 30 seconds when running with --watcher all
# Watch the logs in real-time:
tail -f logs/orchestrator.log

# Or check PM2 status
pm2 status

# Or check PM2 logs
pm2 logs ai-employee-watchers
```

---

## Example 12: Graceful Shutdown

### User Prompt

```
Stop all watchers gracefully
```

### Expected Execution

```bash
# If running in terminal: Press Ctrl+C
# Orchestrator will:
# 1. Stop all watcher threads
# 2. Print final status report
# 3. Exit cleanly

# If running with PM2:
pm2 stop ai-employee-watchers

# Or restart:
pm2 restart ai-employee-watchers
```

---

## See Also

- **Watcher Runner Guide**: `WATCHER_RUNNER_GUIDE.md`
- **Setup Scripts**: `scripts/setup/` (OAuth, credentials)
- **Debug Scripts**: `scripts/debug/` (Connection testing)
- **Validation**: `scripts/validate/validate_silver_tier.py`
- **Bronze Tier**: Use `/watcher-runner-filesystem` for filesystem only
- **Triage**: Use `/needs-action-triage` to process action items
- **Approval**: Use `/approval-workflow-manager` for HITL workflow
- **Execution**: Use `/mcp-executor` to execute approved actions
