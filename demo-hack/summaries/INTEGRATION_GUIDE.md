# Silver Tier Integration Guide - Your Project

**This guide shows how your existing Bronze tier project integrates with the 4 new Silver tier skills.**

---

## Your Current Project Structure

```
My_AI_Employee/
├── AI_Employee_Vault/
│   ├── Dashboard.md                    ← Updated by audit-logger
│   ├── Company_Handbook.md             ← Extend with watcher configs
│   ├── Needs_Action/                   ← Populated by watchers
│   └── Plans/                          ← Plan.md files (existing)
│
├── test_watch_folder/                  ← Monitored by filesystem watcher
│
└── .env                                ← Add watcher credentials
```

---

## New Folder Structure After Integration

```
My_AI_Employee/
├── AI_Employee_Vault/
│   ├── Dashboard.md                    ← Real-time status
│   ├── Company_Handbook.md             ← Extended with configs
│   │
│   ├── Needs_Action/                   ← Items from watchers
│   │   ├── gmail_urgent_2026-01-14.md
│   │   ├── whatsapp_client_a_2026-01-14.md
│   │   └── linkedin_notification_2026-01-14.md
│   │
│   ├── Pending_Approval/               ← NEW: Awaiting human decision
│   │   ├── email_send_client.md
│   │   └── payment_vendor_200.md
│   │
│   ├── Approved/                       ← NEW: Ready for execution
│   │   ├── email_send_client.md
│   │   └── linkedin_post.md
│   │
│   ├── Done/                           ← NEW: Completed with results
│   │   ├── email_send_client_executed_20260114_143600.md
│   │   └── linkedin_post_executed_20260114_101500.md
│   │
│   ├── Failed/                         ← NEW: Execution failed, awaiting retry
│   │   └── email_accounting_failed_retry1.md
│   │
│   ├── Rejected/                       ← NEW: Rejected items
│   │   └── whatsapp_unauthorized_commitment.md
│   │
│   ├── Plans/                          ← Your existing plans
│   │   ├── Plan_stripe_integration_greenleaf.md
│   │   └── Plan_website_redesign_techstart.md
│   │
│   └── .archived/                      ← NEW: Old items (optional)
│       └── Done items older than 90 days
│
├── test_watch_folder/
│   ├── api_integration_request.txt     ← Watched by filesystem_watcher
│   └── test_request.txt
│
├── logs/                               ← NEW: Skill logs
│   ├── audit.log                       ← All actions with credentials sanitized
│   ├── orchestrator.log                ← Watcher orchestrator status
│   ├── executor.log                    ← Action execution logs
│   ├── health_check.log                ← Watcher health checks
│   └── [watcher logs]
│
└── .env                                ← Update with new credentials
    ├── GMAIL_CREDENTIALS_FILE
    ├── GMAIL_TOKEN_FILE
    ├── LINKEDIN_ACCESS_TOKEN
    ├── WHATSAPP_SESSION_FILE
    └── WATCH_FOLDER
```

---

## Step-by-Step Integration

### Step 1: Backup Your Current Project

```bash
# Backup existing vault
cp -r My_AI_Employee/AI_Employee_Vault My_AI_Employee/AI_Employee_Vault.backup.20260115

# Backup existing Dashboard
cp My_AI_Employee/AI_Employee_Vault/Dashboard.md Dashboard.backup.md
```

### Step 2: Create New Folders

```bash
mkdir -p My_AI_Employee/AI_Employee_Vault/{Pending_Approval,Approved,Done,Failed,Rejected}
mkdir -p logs
```

### Step 3: Update .env File

```bash
# Copy template
cp .claude/skills/multi-watcher-runner/templates/env_template.txt .env

# Edit .env with your credentials
# Required variables:
# - GMAIL_CREDENTIALS_FILE=credentials.json
# - GMAIL_TOKEN_FILE=token.json
# - LINKEDIN_ACCESS_TOKEN=your_token
# - WHATSAPP_SESSION_FILE=.whatsapp_session
# - WATCH_FOLDER=My_AI_Employee/test_watch_folder
# - VAULT_ROOT=My_AI_Employee/AI_Employee_Vault
```

### Step 4: Update Company_Handbook.md

```bash
# Append watcher configuration
cat .claude/skills/multi-watcher-runner/templates/company_handbook_section.md \
    >> My_AI_Employee/AI_Employee_Vault/Company_Handbook.md
```

**Add These Sections**:
1. Gmail Watcher config (which labels to monitor)
2. WhatsApp Watcher config (which contacts to monitor)
3. LinkedIn Watcher config (what notifications to track)
4. Filesystem Watcher config (watch folder settings)
5. Approval rules (which actions need approval)
6. Executor timeouts (per MCP server)

### Step 5: Install Python Dependencies

```bash
pip install \
  FastMCP \
  Pydantic \
  python-dotenv \
  google-auth-oauthlib \
  google-auth-httplib2 \
  google-api-python-client \
  playwright \
  watchdog \
  requests \
  aiohttp
```

### Step 6: Set Up Gmail OAuth

```bash
# 1. Create Google Cloud project
# 2. Enable Gmail API
# 3. Create OAuth 2.0 credentials (Desktop app)
# 4. Download credentials.json to project root

# Verify:
ls -l credentials.json
```

### Step 7: Set Up WhatsApp (First Run Only)

```bash
# First run will show QR code
python .claude/skills/multi-watcher-runner/scripts/orchestrate_watchers.py

# Expected:
# 1. Chromium browser opens with WhatsApp Web QR code
# 2. Scan with your phone
# 3. Session saved to .whatsapp_session
# 4. Ctrl+C to stop, then proceed with other setup
```

### Step 8: Verify Your Existing Data

Your existing action items from Bronze tier should be in:
```
My_AI_Employee/AI_Employee_Vault/Needs_Action/
├── 20260114_154044_684205_test_request.md
├── 20260114_171103_550678_api_integration_request.md
└── ... (other existing items)
```

These will be processed by the new approval workflow.

---

## Integration Flow: How Your Existing Items Get Processed

### Your Existing Items

From your Dashboard.md, you have:
1. **GreenLeaf Stripe integration** (HIGH priority)
2. **TechStart website redesign** (HIGH priority)

### With Silver Tier Skills, They Will:

1. **Stage 1: Detection (Multi-Watcher)**
   - Watchers scan your existing items
   - Create action items if not already present
   - Gmail: New emails from clients
   - Filesystem: New files dropped

2. **Stage 2: Approval (Approval-Workflow-Manager)**
   - Items routed to `/Pending_Approval/`
   - You review: Does this need action?
   - Approve → `/Approved/`
   - Reject → `/Rejected/`

3. **Stage 3: Execution (MCP-Executor)**
   - For approved items, execute via MCP
   - Email: Send responses
   - LinkedIn: Post updates
   - Browser: Fill forms, make payments

4. **Stage 4: Audit (Audit-Logger)**
   - All actions logged
   - Credentials sanitized
   - Complete audit trail

---

## Testing the Integration

### Test 1: Filesystem Watcher

```bash
# Drop a test file
echo "Test action request" > My_AI_Employee/test_watch_folder/test_action.txt

# Run orchestrator
python .claude/skills/multi-watcher-runner/scripts/orchestrate_watchers.py

# Check logs
tail -f logs/orchestrator.log

# Verify action created
ls -la My_AI_Employee/AI_Employee_Vault/Needs_Action/
```

**Expected**: File appears in `Needs_Action/` with metadata

### Test 2: Approval Workflow

```bash
# Check pending approvals
python .claude/skills/approval-workflow-manager/scripts/check_approvals.py

# Expected output shows items awaiting approval
```

### Test 3: Executor Status

```bash
# Check what's queued for execution
python .claude/skills/mcp-executor/scripts/executor_status.py

# Expected: Shows pending, executed, and failed counts
```

### Test 4: Audit Log

```bash
# View recent audit entries
tail -f logs/audit.log

# Check sanitization (should NOT show credentials)
grep "token" logs/audit.log  # Should show "token redacted"
```

---

## Monitoring Your Integration

### Daily Checks

1. **Dashboard Update**
   ```bash
   # Check status
   cat My_AI_Employee/AI_Employee_Vault/Dashboard.md
   ```

2. **Pending Approvals**
   ```bash
   python .claude/skills/approval-workflow-manager/scripts/check_approvals.py
   ```

3. **Watcher Health**
   ```bash
   python .claude/skills/multi-watcher-runner/scripts/monitor_watchers.py
   ```

### Weekly Reports

1. **Audit Report**
   ```bash
   python .claude/skills/audit-logger/scripts/generate_audit_report.py --period week
   ```

2. **Execution Summary**
   ```bash
   # Count completed actions
   find My_AI_Employee/AI_Employee_Vault/Done -type f -mtime -7 | wc -l
   ```

### Configuration Updates

To change watcher behavior, edit `Company_Handbook.md`:

```markdown
## Gmail Watcher Config
Check Frequency: Every 5 minutes
Priority Rules:
- HIGH: urgent, asap, payment
- MEDIUM: standard emails
- LOW: newsletters

## Approval Rules
- External communications require approval
- Payments > $500 require approval
- LinkedIn posts require brand review
```

---

## Troubleshooting Integration

### Watcher Not Starting

```bash
# Check .env is set up
cat .env | grep VAULT_ROOT

# Verify folders exist
ls -la My_AI_Employee/AI_Employee_Vault/Needs_Action/

# Check logs
tail -f logs/orchestrator.log
```

### Gmail Authentication Failed

```bash
# Delete old token and re-authenticate
rm token.json

# Restart watcher - will prompt for OAuth
python .claude/skills/multi-watcher-runner/scripts/orchestrate_watchers.py
```

### WhatsApp Session Expired

```bash
# After 2 weeks, session expires
rm .whatsapp_session

# Restart - will show new QR code
python .claude/skills/multi-watcher-runner/scripts/orchestrate_watchers.py
```

### Items Not Being Approved

```bash
# Check pending approvals
ls -la My_AI_Employee/AI_Employee_Vault/Pending_Approval/

# Manually approve by editing file and moving to Approved/
mv My_AI_Employee/AI_Employee_Vault/Pending_Approval/item.md \
   My_AI_Employee/AI_Employee_Vault/Approved/item.md
```

---

## Migration from Bronze to Silver

### What Stays the Same

✅ Dashboard.md - Your existing dashboard (updated automatically)
✅ Company_Handbook.md - Your rules (extended with new sections)
✅ Plans/ - Your plans stay in place
✅ Needs_Action/ - Existing items move through new workflow

### What Changes

- ⚠️ Permission boundaries: NOW allows external actions (with approval)
- ⚠️ Action items: NOW flow through approval → execution
- ⚠️ Logging: NOW comprehensive audit trail

### What's New

✅ Pending_Approval/ - Items awaiting your decision
✅ Approved/ - Items ready to execute
✅ Done/ - Completed items with results
✅ Failed/ - Failed items awaiting retry
✅ Rejected/ - Rejected items
✅ logs/audit.log - Complete action log

---

## Extending Beyond Silver Tier

### For Gold Tier, You Can Add

1. **Finance Watcher** (Bank transaction monitoring)
2. **Xero Integration** (Accounting)
3. **Social Media** (Facebook, Instagram, Twitter)
4. **Advanced Scheduling** (Cron + Task Scheduler)

The skill architecture supports these extensions:

```bash
# Add new watcher following same pattern
python scripts/create_watcher.py finance
```

---

## Support & Reference

| Need | Location |
|------|----------|
| Watcher setup | `references/watcher-configuration.md` |
| Gmail OAuth | `references/gmail-api-setup.md` |
| WhatsApp session | `references/whatsapp-web-session.md` |
| Approval patterns | `references/approval-patterns.md` |
| Audit fields | `references/audit-fields.md` |
| MCP servers | `references/fastmcp-servers.md` |
| Examples | `examples.md` in each skill |

---

## Quick Reference

### Start All Watchers
```bash
python .claude/skills/multi-watcher-runner/scripts/orchestrate_watchers.py
```

### Check Pending Approvals
```bash
python .claude/skills/approval-workflow-manager/scripts/check_approvals.py
```

### Start Executor
```bash
python .claude/skills/mcp-executor/scripts/run_executor.py
```

### Generate Audit Report
```bash
python .claude/skills/audit-logger/scripts/generate_audit_report.py
```

### Check Watcher Status
```bash
python .claude/skills/multi-watcher-runner/scripts/monitor_watchers.py
```

---

## Approval Decision Template

When you see an item in `/Pending_Approval/`, edit the YAML frontmatter:

```markdown
---
status: approved          ← Change from "pending" to "approved"
approved_by: Your Name
approved_at: 2026-01-15T10:00:00Z
---

# Your Decision

✅ APPROVED - [reason]

Or use rejection template:

❌ REJECTED - [reason]
```

Then move to appropriate folder:

```bash
# Approved items
mv Pending_Approval/item.md Approved/item.md

# Rejected items
mv Pending_Approval/item.md Rejected/item.md
```

---

## Success Indicators

**Your integration is working when**:

1. ✅ Filesystem watcher creates action items
2. ✅ Approval workflow routes items correctly
3. ✅ You can approve/reject items
4. ✅ Executor processes approved items
5. ✅ Audit log records all actions
6. ✅ Results appear in Done/ folder

---

**Status**: ✅ Ready to Deploy
**Version**: 1.0
**Date**: 2026-01-15
