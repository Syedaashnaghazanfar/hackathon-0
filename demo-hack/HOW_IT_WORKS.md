# How the AI Employee Works (Bronze + Silver Tier)

## 🎯 Overview

The AI Employee is an autonomous system that monitors multiple channels, detects new information, creates action items, gets human approval, and executes actions through MCP servers.

**Two Tiers:**
- **Bronze Tier**: Filesystem watcher only (local file drops)
- **Silver Tier**: Gmail, WhatsApp, LinkedIn watchers + MCP execution

This guide covers both tiers and how to run/test each component.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Gmail Watcher │  │WhatsApp      │  │LinkedIn      │          │
│  │(OAuth 2.0)   │  │Watcher       │  │Watcher       │          │
│  │              │  │(Playwright)  │  │(API/Scrape)  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            │                                     │
│                            ▼                                     │
│                  ┌─────────────────────┐                         │
│                  │  Obsidian Vault     │                         │
│                  │  /Needs_Action/     │                         │
│                  └─────────┬───────────┘                         │
└────────────────────────────┼─────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                    REASONING LAYER                               │
│                            ▼                                     │
│                  ┌─────────────────────┐                         │
│                  │ Claude Code +       │                         │
│                  │ Skills:             │                         │
│                  │ - needs-action-     │                         │
│                  │   triage            │                         │
│                  │ - approval-workflow-│                         │
│                  │   manager           │                         │
│                  └─────────┬───────────┘                         │
│                            │                                     │
│         ┌──────────────────┼──────────────────┐                 │
│         ▼                  ▼                  ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  /Plans/     │  │/Pending_     │  │ /Approved/   │          │
│  │              │  │ Approval/    │  │              │          │
│  └──────────────┘  └──────────────┘  └──────┬───────┘          │
└────────────────────────────────────────────┼─────────────────────┘
                                             │
┌────────────────────────────────────────────┼─────────────────────┐
│                    ACTION LAYER                                  │
│                                             ▼                    │
│                                   ┌─────────────────┐            │
│                                   │  Orchestrator   │            │
│                                   │  (MCP Executor) │            │
│                                   └────────┬────────┘            │
│                                            │                     │
│         ┌──────────────────────────────────┼──────────┐          │
│         ▼                  ▼               ▼          ▼          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Email MCP    │  │LinkedIn MCP  │  │Browser MCP   │          │
│  │(Gmail API)   │  │(API/Scrape)  │  │(Playwright)  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         ▼                  ▼                  ▼                  │
│    Send Email        Post to LinkedIn   Fill Forms/Click        │
│                                                                  │
│                            │                                     │
│                            ▼                                     │
│                  ┌─────────────────────┐                         │
│                  │  Audit Logger       │                         │
│                  │  /Logs/YYYY-MM-DD   │                         │
│                  │  .json              │                         │
│                  └─────────────────────┘                         │
└──────────────────────────────────────────────────────────────────┘
```

## 📋 Complete Workflow: Email Response Example

### Step 1: Start the Gmail Watcher

**You run:**
```bash
cd My_AI_Employee
uv run python watchers/gmail_watcher.py
```

**What happens:**
- Watcher connects to Gmail using OAuth token
- Polls inbox every 60 seconds for unread emails
- Runs continuously in background

### Step 2: New Email Arrives

**Scenario:** Client sends email: "Can you send me the Q4 report?"

**What the watcher does:**
1. Detects new unread email via Gmail API
2. Extracts: sender, subject, body, timestamp
3. Checks deduplication (prevents processing same email twice)
4. Analyzes content for:
   - Urgent keywords (urgent, asap, emergency, critical)
   - Risk level (Low/Medium/High)
   - Priority (Low/Medium/High)
5. Creates action item file in `/Needs_Action/`

**File created:** `AI_Employee_Vault/Needs_Action/20260115_143022_email_client.md`

```yaml
---
type: email
received: 2026-01-15T14:30:22Z
status: pending
approval_required: true
priority: Medium
risk_level: Medium
action_type: send_email
sender: client@example.com
subject: Can you send me the Q4 report?
---

# Email from client@example.com

## Details
**From**: client@example.com
**Subject**: Can you send me the Q4 report?
**Priority**: Medium
**Risk Level**: Medium

## Message Body
Can you send me the Q4 report?

---

## Next Steps
- [ ] Read Company_Handbook.md for email response guidelines
- [ ] Draft response based on handbook rules
- [ ] Create approval request in Pending_Approval/
- [ ] Wait for human approval
- [ ] Send email via email_mcp server
```

### Step 3: Process Action Items (Manual or Automated)

**Option A: Manual Processing (You trigger)**
```bash
# Open Claude Code and run:
/needs-action-triage
```

**Option B: Automated Processing (Future enhancement)**
- Cron job or PM2 scheduler runs triage every 5 minutes
- Automatically processes new items in /Needs_Action/

**What the needs-action-triage skill does:**
1. Reads all files in `/Needs_Action/`
2. For each action item:
   - Reads `Company_Handbook.md` for rules
   - Analyzes the request
   - Creates a plan in `/Plans/`
   - Determines if approval is needed
3. Moves items to appropriate folders

**File created:** `AI_Employee_Vault/Plans/Plan_email_client_q4_report.md`

```markdown
# Plan: Respond to Q4 Report Request

## Analysis
- Client: client@example.com
- Request: Q4 report
- Handbook rule: "Q4 reports require CFO approval before sharing"

## Proposed Action
1. Draft email response: "Thank you for your request. I'm preparing the Q4 report and will send it after internal approval."
2. Attach Q4 report PDF
3. CC: cfo@company.com

## Risk Assessment
- Risk Level: Medium (financial data)
- Approval Required: Yes (per handbook)

## Next Steps
- Create approval request
- Wait for human approval
- Execute via email_mcp
```

### Step 4: Approval Workflow (Human-in-the-Loop)

**What the approval-workflow-manager skill does:**
1. Detects external actions (send_email, post_linkedin, etc.)
2. Creates approval request in `/Pending_Approval/`

**File created:** `AI_Employee_Vault/Pending_Approval/Approval_email_client_q4_report.md`

```yaml
---
approval_id: APR-20260115-001
action_type: send_email
risk_level: Medium
requested_at: 2026-01-15T14:35:00Z
status: pending
---

# Approval Request: Send Q4 Report Email

## Action Details
**To**: client@example.com
**Subject**: Re: Q4 Report Request
**Risk Level**: Medium

## Draft Email
Thank you for your request. I'm preparing the Q4 report and will send it after internal approval.

## Approval Options
- [ ] ✅ Approve (move to /Approved/)
- [ ] ❌ Reject (move to /Rejected/)
- [ ] ✏️ Edit and Approve (modify draft, then approve)

## Handbook Reference
Rule 4.2: "Q4 reports require CFO approval before sharing"
```

**You (human) review and approve:**
1. Open the file in Obsidian
2. Review the draft email
3. Move file to `/Approved/` folder (or edit and then move)

### Step 5: Execute Approved Action

**You run the orchestrator:**
```bash
cd My_AI_Employee
uv run python orchestrator.py
```

**What the orchestrator does:**
1. Monitors `/Approved/` folder every 5 seconds
2. Detects new approved action
3. Routes to appropriate MCP server based on `action_type`
4. For `send_email`:
   - Calls `email_mcp.send_email()`
   - Passes: to, subject, body
   - Email MCP uses Gmail API to send
5. Logs execution to audit log
6. Moves file to `/Done/` with execution results

**File moved:** `AI_Employee_Vault/Done/20260115_143022_email_client_executed.md`

```yaml
---
type: email
status: executed
executed_at: 2026-01-15T14:40:00Z
success: true
message_id: <abc123@gmail.com>
execution_time_seconds: 1.2
---

# Email Sent Successfully

✅ Email sent to client@example.com
📧 Message ID: <abc123@gmail.com>
⏱️ Execution time: 1.2 seconds
```

**Audit log created:** `AI_Employee_Vault/Logs/2026-01-15.json`

```json
{
  "timestamp": "2026-01-15T14:40:00Z",
  "action_type": "send_email",
  "mcp_server": "email_mcp",
  "success": true,
  "to": "client@example.com",
  "subject": "Re: Q4 Report Request",
  "approved_by": "human",
  "approved_at": "2026-01-15T14:38:00Z",
  "entry_id": "20260115_143022_email_client"
}
```

## 🔄 Continuous Operation

### Running All Components Together

**Option 1: Manual (Development/Testing)**
```bash
# Terminal 1: Gmail Watcher
cd My_AI_Employee
uv run python watchers/gmail_watcher.py

# Terminal 2: Orchestrator (MCP Executor)
cd My_AI_Employee
uv run python orchestrator.py

# Terminal 3: Claude Code (for triage and approval)
# Run /needs-action-triage when needed
# Review and approve items in Obsidian
```

**Option 2: PM2 (Production - Recommended)**
```bash
# Install PM2
npm install -g pm2

# Start all watchers and orchestrator
cd My_AI_Employee
pm2 start ecosystem.config.js

# Monitor all processes
pm2 monit

# View logs
pm2 logs

# Stop all
pm2 stop all
```

## 🎯 Key Points

### What Requires Human Action:
1. ✅ **Approval** - Review and approve actions in `/Pending_Approval/`
2. ✅ **Triage** - Run `/needs-action-triage` skill (can be automated)
3. ✅ **Monitoring** - Check dashboard and logs periodically

### What Runs Automatically:
1. ✅ **Watchers** - Continuously monitor Gmail/WhatsApp/LinkedIn
2. ✅ **Deduplication** - Prevents duplicate action items
3. ✅ **Orchestrator** - Executes approved actions automatically
4. ✅ **Audit Logging** - Records all actions automatically

### Security & Safety:
1. ✅ **Human-in-the-Loop** - All external actions require approval
2. ✅ **Risk Assessment** - Automatic risk level detection
3. ✅ **Audit Trail** - Complete log of all actions
4. ✅ **Credential Safety** - OAuth tokens, no passwords in code
5. ✅ **Rollback** - Failed actions moved to `/Failed/` for retry

## 🚀 Quick Start Commands

### First Time Setup
```bash
# 1. Complete OAuth (already done!)
# token.json exists

# 2. Test Gmail watcher
cd My_AI_Employee
uv run python test_gmail_process.py

# 3. Process action items
# Open Claude Code and run:
/needs-action-triage

# 4. Approve an action
# Open Obsidian, review /Pending_Approval/, move to /Approved/

# 5. Execute approved actions
uv run python orchestrator.py
```

### Daily Operation
```bash
# Start watchers (runs continuously)
pm2 start ecosystem.config.js

# Check status
pm2 status

# View logs
pm2 logs gmail_watcher
pm2 logs orchestrator

# Stop when done
pm2 stop all
```

## 📊 Monitoring & Debugging

### Check System Status
```bash
# View dashboard
cat AI_Employee_Vault/Dashboard.md

# Check pending actions
ls AI_Employee_Vault/Needs_Action/

# Check pending approvals
ls AI_Employee_Vault/Pending_Approval/

# View audit logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

### Troubleshooting

**Problem: Watcher not detecting emails**
```bash
# Check OAuth token
ls -la My_AI_Employee/token.json

# Test Gmail connection
uv run python debug_gmail.py

# Reset deduplication
rm My_AI_Employee/My_AI_Employee/.gmail_dedupe.json
```

**Problem: Actions not executing**
```bash
# Check orchestrator logs
tail -f logs/executor.log

# Verify MCP server
uv run python -c "from mcp_servers.email_mcp import send_email; print('✅ Email MCP loaded')"

# Check approved folder
ls AI_Employee_Vault/Approved/
```

**Problem: Approval workflow not working**
```bash
# Run approval workflow manager
/approval-workflow-manager

# Check pending approvals
ls AI_Employee_Vault/Pending_Approval/
```

## 🎓 Example Scenarios

### Scenario 1: Client Email Response
1. Client emails: "Send me the invoice"
2. Gmail watcher creates action item
3. You run `/needs-action-triage`
4. Plan created with draft email
5. You approve in Obsidian
6. Orchestrator sends email via Gmail API
7. Audit log records action

### Scenario 2: LinkedIn Connection Request
1. Someone sends LinkedIn connection request
2. LinkedIn watcher creates action item
3. You run `/needs-action-triage`
4. Plan created: "Accept connection + send thank you message"
5. You approve
6. Orchestrator accepts connection via LinkedIn MCP
7. Audit log records action

### Scenario 3: Form Submission
1. Client requests: "Fill out the vendor form"
2. Email watcher creates action item
3. You run `/needs-action-triage`
4. Plan created with form data
5. You approve
6. Orchestrator fills form via Browser MCP (Playwright)
7. Audit log records action

## 📝 Summary

**The workflow is:**
1. **Watcher detects** → Creates action item in `/Needs_Action/`
2. **You run triage** → Creates plan in `/Plans/` and approval request in `/Pending_Approval/`
3. **You approve** → Move file to `/Approved/`
4. **Orchestrator executes** → Calls MCP server, logs result, moves to `/Done/`

**You control:**
- When to run triage (manual or scheduled)
- Which actions to approve (human-in-the-loop)
- System monitoring and oversight

**System handles:**
- Continuous monitoring (watchers)
- Automatic execution (orchestrator)
- Audit logging (all actions)
- Error handling and retries

---

**Next Steps:**
1. Test the workflow with the 5 action items we created
2. Run `/needs-action-triage` to process them
3. Approve one action and test execution
4. Set up PM2 for continuous operation

---

## 🧪 COMPLETE TESTING GUIDE

### Prerequisites Check

Before testing, verify you have:
```bash
cd /mnt/d/hackathon-0/My_AI_Employee

# Check Python environment
uv --version

# Check vault structure
ls AI_Employee_Vault/
# Should see: Needs_Action/, Plans/, Pending_Approval/, Approved/, Done/, Logs/

# Check credentials (for Silver tier)
ls -la credentials.json token.json 2>/dev/null || echo "⚠️ OAuth not set up yet"
```

---

## 🔵 BRONZE TIER TESTING

### Test 1: Filesystem Watcher

**What it does:** Monitors a local folder for new files (.txt, .md, .pdf) and creates action items in vault.

**Setup:**
```bash
cd /mnt/d/hackathon-0/My_AI_Employee

# Create watch folder if it doesn't exist
mkdir -p test_watch_folder

# Check configuration
cat .env | grep WATCH_FOLDER
# Should show: WATCH_FOLDER=test_watch_folder
```

**Run the watcher:**
```bash
# Terminal 1: Start filesystem watcher
uv run python run_watcher.py --watcher filesystem

# Expected output:
# INFO - Starting filesystem watcher...
# INFO - Watching: /path/to/test_watch_folder
# INFO - Vault: /path/to/AI_Employee_Vault
# INFO - Watcher started successfully
```

**Test it:**
```bash
# Terminal 2: Drop a test file
echo "Please review the Q1 budget proposal and send feedback by Friday." > test_watch_folder/budget_request.txt

# Check Terminal 1 - should see:
# INFO - New file detected: budget_request.txt
# INFO - Created action item: AI_Employee_Vault/Needs_Action/20260121_XXXXXX_budget_request.md

# Verify action item was created
ls AI_Employee_Vault/Needs_Action/
```

**Expected result:**
- New markdown file in `Needs_Action/` with:
  - YAML frontmatter (type, status, priority, risk_level)
  - File content extracted
  - Next steps listed

**Stop the watcher:** Press `Ctrl+C` in Terminal 1

---

### Test 2: Process Action Items (Bronze Tier)

**What it does:** Claude Code reads action items, creates plans, and moves to Done.

**Run triage:**
```bash
# In Claude Code terminal:
/needs-action-triage

# Or manually trigger:
# "Process all items in Needs_Action folder"
```

**What happens:**
1. Claude reads all files in `Needs_Action/`
2. Reads `Company_Handbook.md` for rules
3. Creates plan in `Plans/` folder
4. Moves original file to `Done/` (Bronze tier - no approval needed)
5. Updates `Dashboard.md`

**Verify:**
```bash
# Check Plans folder
ls AI_Employee_Vault/Plans/
cat AI_Employee_Vault/Plans/Plan_budget_request.md

# Check Done folder
ls AI_Employee_Vault/Done/

# Check Dashboard
cat AI_Employee_Vault/Dashboard.md
```

---

## 🥈 SILVER TIER TESTING

### Test 3: Gmail Watcher

**What it does:** Monitors Gmail inbox for new unread emails, creates action items.

**Prerequisites:**
```bash
cd /mnt/d/hackathon-0/My_AI_Employee

# Verify OAuth token exists
ls -la token.json credentials.json

# If missing, run OAuth setup:
uv run python scripts/setup/setup_gmail_oauth.py
```

**Test Gmail connection:**
```bash
# Quick test
uv run python scripts/debug/debug_gmail.py

# Expected output:
# ✅ Gmail API connection successful
# 📧 Found X unread emails
# [List of recent emails]
```

**Run Gmail watcher:**
```bash
# Terminal 1: Start Gmail watcher
uv run python run_watcher.py --watcher gmail

# Expected output:
# INFO - Starting Gmail watcher...
# INFO - OAuth token loaded successfully
# INFO - Connected to Gmail API
# INFO - Polling inbox every 60 seconds
# INFO - Watcher started successfully
```

**Test it:**
```bash
# Send yourself a test email:
# To: your-gmail@gmail.com
# Subject: Test AI Employee
# Body: Please send me the project status report.

# Wait 60 seconds (or check Terminal 1 immediately)

# Terminal 1 should show:
# INFO - New email detected: Test AI Employee
# INFO - From: your-gmail@gmail.com
# INFO - Created action item: AI_Employee_Vault/Needs_Action/20260121_XXXXXX_email_your_gmail.md

# Verify
ls AI_Employee_Vault/Needs_Action/
```

**Expected result:**
- Action item created with:
  - `type: email`
  - `sender: your-gmail@gmail.com`
  - `subject: Test AI Employee`
  - `approval_required: true` (Silver tier)
  - Email body content

**Stop the watcher:** Press `Ctrl+C`

---

### Test 4: WhatsApp Watcher

**What it does:** Monitors WhatsApp Web for new messages, creates action items.

**Prerequisites:**
```bash
cd /mnt/d/hackathon-0/My_AI_Employee

# Check WhatsApp configuration
cat .env | grep WHATSAPP

# Install Playwright browsers (first time only)
uv run playwright install chromium
```

**Run WhatsApp watcher:**
```bash
# Terminal 1: Start WhatsApp watcher
uv run python run_watcher.py --watcher whatsapp

# Expected output:
# INFO - Starting WhatsApp watcher...
# INFO - Launching browser...
# INFO - Opening WhatsApp Web...
#
# 🔐 SCAN QR CODE IN BROWSER WINDOW
#
# INFO - Waiting for QR code scan...
```

**First time setup:**
1. Browser window opens with WhatsApp Web
2. Scan QR code with your phone
3. Session saved to `.whatsapp_session/`
4. Next time, auto-login (no QR scan needed)

**Test it:**
```bash
# Send yourself a WhatsApp message from another device:
# "Can you schedule a meeting with the team for next week?"

# Terminal 1 should show:
# INFO - New message detected from: Your Name
# INFO - Created action item: AI_Employee_Vault/Needs_Action/20260121_XXXXXX_whatsapp_Your_Name.md

# Verify
ls AI_Employee_Vault/Needs_Action/
```

**Expected result:**
- Action item with:
  - `type: whatsapp`
  - `sender: Your Name`
  - `approval_required: true`
  - Message content

**Stop the watcher:** Press `Ctrl+C`

---

### Test 5: LinkedIn Watcher

**What it does:** Monitors LinkedIn for new messages and connection requests.

**Prerequisites:**
```bash
cd /mnt/d/hackathon-0/My_AI_Employee

# Check LinkedIn configuration
cat .env | grep LINKEDIN

# Run OAuth setup (if not done)
uv run python scripts/linkedin_oauth2_setup.py
```

**Run LinkedIn watcher:**
```bash
# Terminal 1: Start LinkedIn watcher
uv run python run_watcher.py --watcher linkedin

# Expected output:
# INFO - Starting LinkedIn watcher...
# INFO - Authenticating with LinkedIn...
# INFO - Connected to LinkedIn API
# INFO - Polling for new messages every 120 seconds
```

**Test it:**
- Send yourself a LinkedIn message or connection request
- Wait for polling interval (120 seconds)
- Check `Needs_Action/` for new item

**Stop the watcher:** Press `Ctrl+C`

---

### Test 6: Process Action Items (Silver Tier)

**What it does:** Claude Code reads action items, creates plans, and routes to approval workflow.

**Run triage:**
```bash
# In Claude Code:
/needs-action-triage

# Or:
# "Process all items in Needs_Action folder"
```

**What happens (Silver tier):**
1. Claude reads all files in `Needs_Action/`
2. Reads `Company_Handbook.md` for rules
3. Creates plan in `Plans/` folder
4. Detects external action (send_email, etc.)
5. Creates approval request in `Pending_Approval/`
6. Keeps original file in `Needs_Action/` with `status: pending_approval`

**Verify:**
```bash
# Check Plans
ls AI_Employee_Vault/Plans/
cat AI_Employee_Vault/Plans/Plan_email_test.md

# Check Pending Approval
ls AI_Employee_Vault/Pending_Approval/
cat AI_Employee_Vault/Pending_Approval/APPROVAL_email_test.md

# Original file still in Needs_Action (Silver tier)
ls AI_Employee_Vault/Needs_Action/
```

---

### Test 7: Approval Workflow

**What it does:** Human reviews and approves/rejects actions.

**Review approval request:**
```bash
# Open in Obsidian or any text editor
cat AI_Employee_Vault/Pending_Approval/APPROVAL_email_test.md
```

**Approve an action:**
```bash
# Option 1: Move file to Approved folder
mv AI_Employee_Vault/Pending_Approval/APPROVAL_email_test.md \
   AI_Employee_Vault/Approved/

# Option 2: Edit frontmatter and move
# Edit file: status: approved, approved_by: Your Name
# Then move to Approved/
```

**Reject an action:**
```bash
# Move to Rejected folder (create if needed)
mkdir -p AI_Employee_Vault/Rejected
mv AI_Employee_Vault/Pending_Approval/APPROVAL_email_test.md \
   AI_Employee_Vault/Rejected/
```

---

### Test 8: Orchestrator (MCP Executor)

**What it does:** Watches `Approved/` folder, executes actions via MCP servers, logs results.

**Prerequisites:**
```bash
cd /mnt/d/hackathon-0/My_AI_Employee

# Verify MCP servers exist
ls mcp_servers/
# Should see: email_mcp.py, linkedin_mcp.py, browser_mcp.py

# Check email backend configuration
cat .env | grep EMAIL_BACKEND
# Should be: EMAIL_BACKEND=gmail or EMAIL_BACKEND=smtp
```

**Run orchestrator:**
```bash
# Terminal 1: Start orchestrator
uv run python orchestrator.py

# Expected output:
# INFO - Starting Orchestrator...
# INFO - Watching folders:
# INFO -   Approved: AI_Employee_Vault/Approved/
# INFO -   Needs_Action: AI_Employee_Vault/Needs_Action/
# INFO - Check interval: 10 seconds
# INFO - Orchestrator started successfully
```

**Test it:**
```bash
# Terminal 2: Move an approved action to Approved folder
# (Use the approval from Test 7)

# Terminal 1 should show:
# INFO - New approved action detected: APPROVAL_email_test.md
# INFO - Action type: send_email
# INFO - Routing to email_mcp server...
# INFO - Executing: send_email(to=..., subject=..., body=...)
# INFO - ✅ Email sent successfully
# INFO - Message ID: <abc123@gmail.com>
# INFO - Moving to Done/
# INFO - Updating original file in Needs_Action/
# INFO - Moving original to Done/
# INFO - Logging to audit trail
```

**Verify:**
```bash
# Check Done folder
ls AI_Employee_Vault/Done/
cat AI_Employee_Vault/Done/EXECUTED_email_test.md

# Check audit log
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Check email was actually sent
# Open Gmail and check Sent folder
```

**Stop the orchestrator:** Press `Ctrl+C`

---

## 🔄 RUNNING ALL COMPONENTS TOGETHER

### Option 1: Manual (Multiple Terminals)

```bash
# Terminal 1: Filesystem watcher (Bronze)
cd /mnt/d/hackathon-0/My_AI_Employee
uv run python run_watcher.py --watcher filesystem

# Terminal 2: Gmail watcher (Silver)
cd /mnt/d/hackathon-0/My_AI_Employee
uv run python run_watcher.py --watcher gmail

# Terminal 3: WhatsApp watcher (Silver)
cd /mnt/d/hackathon-0/My_AI_Employee
uv run python run_watcher.py --watcher whatsapp

# Terminal 4: LinkedIn watcher (Silver)
cd /mnt/d/hackathon-0/My_AI_Employee
uv run python run_watcher.py --watcher linkedin

# Terminal 5: Orchestrator (Silver)
cd /mnt/d/hackathon-0/My_AI_Employee
uv run python orchestrator.py

# Terminal 6: Claude Code (for triage)
# Run /needs-action-triage when needed
```

### Option 2: PM2 (Production - Recommended)

```bash
cd /mnt/d/hackathon-0/My_AI_Employee

# Install PM2 (first time only)
npm install -g pm2

# Start all watchers and orchestrator
pm2 start ecosystem.config.js

# Check status
pm2 status

# Expected output:
# ┌─────┬────────────────────┬─────────┬─────────┐
# │ id  │ name               │ status  │ restart │
# ├─────┼────────────────────┼─────────┼─────────┤
# │ 0   │ filesystem-watcher │ online  │ 0       │
# │ 1   │ gmail-watcher      │ online  │ 0       │
# │ 2   │ whatsapp-watcher   │ online  │ 0       │
# │ 3   │ linkedin-watcher   │ online  │ 0       │
# │ 4   │ orchestrator       │ online  │ 0       │
# └─────┴────────────────────┴─────────┴─────────┘

# Monitor all processes
pm2 monit

# View logs
pm2 logs

# View specific watcher logs
pm2 logs gmail-watcher
pm2 logs orchestrator

# Stop all
pm2 stop all

# Restart all
pm2 restart all

# Delete all (cleanup)
pm2 delete all
```

---

## 🎯 COMPLETE END-TO-END TEST

### Scenario: Email Response Workflow

**Step 1: Send test email**
```bash
# Send email to your Gmail:
# To: your-gmail@gmail.com
# Subject: Project Status Request
# Body: Can you send me the latest project status report?
```

**Step 2: Gmail watcher detects**
```bash
# Check watcher logs
pm2 logs gmail-watcher

# Or if running manually, check Terminal 1
# Should see: "New email detected: Project Status Request"

# Verify action item created
ls AI_Employee_Vault/Needs_Action/
```

**Step 3: Process with Claude Code**
```bash
# In Claude Code:
/needs-action-triage

# Claude will:
# 1. Read the email action item
# 2. Read Company_Handbook.md
# 3. Create plan in Plans/
# 4. Create approval request in Pending_Approval/
```

**Step 4: Review and approve**
```bash
# Open approval request
cat AI_Employee_Vault/Pending_Approval/APPROVAL_*.md

# Review the draft email response
# If good, move to Approved:
mv AI_Employee_Vault/Pending_Approval/APPROVAL_*.md \
   AI_Employee_Vault/Approved/
```

**Step 5: Orchestrator executes**
```bash
# Check orchestrator logs
pm2 logs orchestrator

# Should see:
# "New approved action detected"
# "Routing to email_mcp server"
# "✅ Email sent successfully"

# Verify in Gmail Sent folder
```

**Step 6: Verify completion**
```bash
# Check Done folder
ls AI_Employee_Vault/Done/

# Check audit log
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Check Dashboard
cat AI_Employee_Vault/Dashboard.md
```

**Expected result:**
- ✅ Email received and detected
- ✅ Action item created
- ✅ Plan generated
- ✅ Approval requested
- ✅ Human approved
- ✅ Email sent via Gmail API
- ✅ Audit log created
- ✅ Files moved to Done/
- ✅ Dashboard updated

---

## 🐛 TROUBLESHOOTING

### Filesystem Watcher Issues

**Problem: Files not detected**
```bash
# Check watch folder path
cat .env | grep WATCH_FOLDER

# Verify folder exists
ls -la test_watch_folder/

# Check watcher logs
pm2 logs filesystem-watcher

# Test manually
echo "test" > test_watch_folder/test.txt
```

**Problem: Permission denied**
```bash
# Fix permissions
chmod -R 755 test_watch_folder/
chmod -R 755 AI_Employee_Vault/
```

### Gmail Watcher Issues

**Problem: OAuth token expired**
```bash
# Delete old token
rm token.json

# Re-authenticate
uv run python scripts/setup/setup_gmail_oauth.py

# Test connection
uv run python scripts/debug/debug_gmail.py
```

**Problem: No emails detected**
```bash
# Check dedupe file
cat .gmail_dedupe.json

# Reset dedupe (will reprocess all emails)
rm .gmail_dedupe.json

# Restart watcher
pm2 restart gmail-watcher
```

### WhatsApp Watcher Issues

**Problem: QR code not showing**
```bash
# Check browser installation
uv run playwright install chromium

# Delete old session
rm -rf .whatsapp_session/

# Restart watcher
pm2 restart whatsapp-watcher
```

**Problem: Session expired**
```bash
# Delete session and re-scan QR
rm -rf .whatsapp_session/
pm2 restart whatsapp-watcher
```

### Orchestrator Issues

**Problem: Actions not executing**
```bash
# Check orchestrator logs
pm2 logs orchestrator

# Verify MCP servers
ls mcp_servers/

# Test email MCP directly
uv run python -c "from mcp_servers.email_mcp import send_email; print('✅ Email MCP loaded')"

# Check Approved folder
ls AI_Employee_Vault/Approved/
```

**Problem: Email send fails**
```bash
# Check email backend
cat .env | grep EMAIL_BACKEND

# Test Gmail API
uv run python scripts/debug/debug_gmail_send.py

# Check token
ls -la token.json
```

### Skills Issues

**Problem: /needs-action-triage not working**
```bash
# Check skills are loaded
# In Claude Code, type: /
# Should see list of available skills

# Verify skill files exist
ls .claude/skills/needs-action-triage/

# Check SKILL.md
cat .claude/skills/needs-action-triage/SKILL.md
```

---

## 📊 MONITORING

### Check System Health

```bash
# PM2 status
pm2 status

# View all logs
pm2 logs

# Check vault folders
ls AI_Employee_Vault/Needs_Action/
ls AI_Employee_Vault/Pending_Approval/
ls AI_Employee_Vault/Approved/
ls AI_Employee_Vault/Done/

# Check Dashboard
cat AI_Employee_Vault/Dashboard.md

# Check audit logs
ls AI_Employee_Vault/Logs/
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

### Performance Metrics

```bash
# Watcher uptime
pm2 status

# Action items processed today
ls AI_Employee_Vault/Done/ | grep $(date +%Y%m%d) | wc -l

# Pending approvals
ls AI_Employee_Vault/Pending_Approval/ | wc -l

# Audit log size
du -h AI_Employee_Vault/Logs/
```

---

## ✅ VALIDATION CHECKLIST

### Bronze Tier
- [ ] Filesystem watcher starts without errors
- [ ] Files dropped in watch folder are detected
- [ ] Action items created in Needs_Action/
- [ ] /needs-action-triage processes items
- [ ] Plans created in Plans/
- [ ] Files moved to Done/
- [ ] Dashboard updated

### Silver Tier
- [ ] Gmail watcher connects via OAuth
- [ ] New emails detected and processed
- [ ] WhatsApp watcher scans QR code
- [ ] WhatsApp messages detected
- [ ] LinkedIn watcher authenticates
- [ ] Approval requests created in Pending_Approval/
- [ ] Orchestrator watches Approved folder
- [ ] MCP servers execute actions
- [ ] Emails sent via Gmail API
- [ ] Audit logs created
- [ ] Original files moved to Done/

### End-to-End
- [ ] Complete email workflow works
- [ ] Complete WhatsApp workflow works
- [ ] All components run together via PM2
- [ ] No errors in logs
- [ ] Dashboard shows accurate status

---
