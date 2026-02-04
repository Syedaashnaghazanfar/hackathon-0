# Personal AI Employee - Silver Tier

**Status**: 🟢 Production Ready (95% Complete)
**Version**: Silver Tier (v2.0)
**Architecture**: Hackathon Zero - Four-Layer AI Employee System

---

## Overview

Personal AI Employee is a functional assistant that monitors multiple communication channels (Gmail, WhatsApp, LinkedIn), reasons about required actions using Claude Code, routes external actions through Human-in-the-Loop (HITL) approval workflow, and executes approved actions on your behalf.

**Key Features**:
- 📧 **Gmail Monitoring**: Detects client emails, drafts responses, sends after approval
- 💬 **WhatsApp Support**: Monitors urgent messages, drafts replies, sends after approval
- 💼 **LinkedIn Posting**: Creates scheduled business posts, publishes after approval
- ✅ **HITL Approval Workflow**: All external actions require human approval
- 📊 **Audit Logging**: Complete audit trail with sanitized credentials
- 🔄 **Graceful Degradation**: System continues when components fail
- 🔐 **Security First**: OAuth2 authentication, credential sanitization, local-first vault

---

## Architecture

### Four-Layer System (Hackathon Zero)

```
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                          │
│  Watchers: Gmail, WhatsApp, LinkedIn → Needs_Action/        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                           │
│  Claude Code + Skills → Plans/ + Pending_Approval/          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    HUMAN APPROVAL                            │
│  You move files: Pending_Approval/ → Approved/              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    ACTION LAYER                              │
│  MCP Servers: Email, LinkedIn, Browser → Done/              │
└─────────────────────────────────────────────────────────────┘
```

### Components

**Perception Layer** (Watchers):
- `watchers/gmail_watcher.py` - Gmail OAuth2 monitoring
- `watchers/whatsapp_watcher.py` - WhatsApp Web with CDP architecture
- `watchers/linkedin_watcher.py` - LinkedIn REST API v2

**Reasoning Layer** (Claude Code Skills):
- `needs-action-triage` - Process action items, create plans
- `approval-workflow-manager` - Handle approval/rejection
- `mcp-executor` - Execute approved actions

**Action Layer** (MCP Servers):
- `mcp_servers/email_mcp.py` - Gmail API email sending
- `mcp_servers/linkedin_mcp.py` - LinkedIn REST API v2 posting
- `mcp_servers/browser_mcp.py` - WhatsApp CDP messaging

**Orchestration Layer**:
- `orchestrator.py` - Watches Approved/ folder, routes to MCP servers
- `run_watcher.py` - Multi-watcher orchestration with health monitoring

---

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js (for PM2 process management)
- Gmail account with API access
- WhatsApp account
- LinkedIn account (optional, requires OAuth2 setup)
- Obsidian (recommended for vault viewing)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd hackathon-0
   ```

2. **Install Python dependencies**:
   ```bash
   cd My_AI_Employee
   uv sync
   ```

3. **Install PM2 (optional, for production)**:
   ```bash
   npm install -g pm2
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Set up Gmail OAuth2**:
   ```bash
   # Follow instructions in docs/WATCHER_SETUP.md
   python scripts/setup/setup_gmail_oauth.py
   ```

6. **Set up WhatsApp**:
   ```bash
   # Start watcher and scan QR code once
   python run_watcher.py --watcher whatsapp
   # Scan QR code in browser, session persists in .whatsapp_session/
   ```

7. **Set up LinkedIn (optional)**:
   ```bash
   # Follow instructions in LINKEDIN_MIGRATION_GUIDE.md
   python scripts/linkedin_oauth2_setup.py
   ```

### Running the System

**Development Mode** (single watcher):
```bash
cd My_AI_Employee

# Start Gmail watcher
python run_watcher.py --watcher gmail

# Start WhatsApp watcher
python run_watcher.py --watcher whatsapp

# Start LinkedIn watcher
python run_watcher.py --watcher linkedin
```

**Production Mode** (all watchers + orchestrator):
```bash
cd My_AI_Employee

# Start all watchers simultaneously
python run_watcher.py --watcher all

# In another terminal, start orchestrator
python orchestrator.py
```

**Using PM2** (recommended for production):
```bash
cd My_AI_Employee
pm2 start ecosystem.config.js
pm2 logs  # View logs
pm2 status  # Check status
```

---

## Usage Workflow

### 1. Perception (Watchers Detect Events)

Watchers monitor communication channels and create action items:

```
Gmail: New email from client
  ↓
watchers/gmail_watcher.py detects email
  ↓
Creates: AI_Employee_Vault/Needs_Action/20260121_email_client.md
```

### 2. Reasoning (Claude Code Creates Plan)

Use Claude Code skills to process action items:

```bash
# In Claude Code
/needs-action-triage process the tasks
```

This creates:
- `Plans/Plan_20260121_email_client.md` - Reasoning and recommendation
- `Pending_Approval/APPROVAL_20260121_email_client.md` - Approval request

### 3. Human Approval (You Decide)

Review the approval request in your vault:

```bash
# Approve: Move to Approved/
mv Pending_Approval/APPROVAL_20260121_email_client.md Approved/

# Reject: Move to Rejected/
mv Pending_Approval/APPROVAL_20260121_email_client.md Rejected/
```

### 4. Action (MCP Servers Execute)

Orchestrator detects approved action and executes:

```
orchestrator.py watches Approved/
  ↓
Routes to mcp_servers/email_mcp.py
  ↓
Sends email via Gmail API
  ↓
Moves to Done/EXECUTED_20260121_email_client.md
```

---

## Project Structure

```
My_AI_Employee/
├── AI_Employee_Vault/           # Obsidian vault (local markdown)
│   ├── Needs_Action/            # Unprocessed action items
│   ├── Pending_Approval/        # Awaiting human decision
│   ├── Approved/                # Approved for execution
│   ├── Rejected/                # Rejected by human
│   ├── Failed/                  # Failed executions
│   ├── Done/                    # Completed actions
│   ├── Plans/                   # Planning artifacts
│   ├── Logs/                    # Audit logs (YYYY-MM-DD.json)
│   ├── Dashboard.md             # Status summary
│   └── Company_Handbook.md      # Rules and preferences
│
├── watchers/                    # Perception layer
│   ├── gmail_watcher.py         # Gmail OAuth2 monitoring
│   ├── whatsapp_watcher.py      # WhatsApp Web (CDP)
│   └── linkedin_watcher.py      # LinkedIn REST API v2
│
├── mcp_servers/                 # Action layer
│   ├── email_mcp.py             # Gmail API email sending
│   ├── linkedin_mcp.py          # LinkedIn REST API v2 posting
│   └── browser_mcp.py           # WhatsApp CDP messaging
│
├── utils/                       # Shared utilities
│   ├── sanitizer.py             # Credential sanitization
│   ├── audit_logger.py          # Action logging
│   ├── auth_helper.py           # OAuth2 handling
│   └── retry_logic.py           # Exponential backoff
│
├── orchestrator.py              # Orchestration layer
├── run_watcher.py               # Multi-watcher runner
├── .env                         # Credentials (gitignored)
└── ecosystem.config.js          # PM2 configuration
```

---

## Configuration

### Environment Variables

See `.env.example` for all configuration options. Key variables:

**Gmail**:
```bash
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.modify
GMAIL_CHECK_INTERVAL=60
```

**WhatsApp**:
```bash
WHATSAPP_SESSION_DIR=.whatsapp_session
WHATSAPP_CDP_PORT=9222
WHATSAPP_CHECK_INTERVAL=30
```

**LinkedIn**:
```bash
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_PERSON_URN=urn:li:person:your_id
```

### Company Handbook

Edit `AI_Employee_Vault/Company_Handbook.md` to define:
- Communication tone and style
- Approval thresholds (Low, Medium, High)
- LinkedIn posting schedule
- Business rules and preferences

---

## Testing

### Unit Tests

```bash
cd My_AI_Employee
pytest tests/unit/
```

### Integration Tests

```bash
pytest tests/integration/
```

### End-to-End Tests

```bash
# Gmail OAuth2 setup
python scripts/setup/setup_gmail_oauth.py

# Test LinkedIn API connection
python scripts/test_linkedin_api.py
```

---

## Monitoring

### Dashboard

View real-time status in `AI_Employee_Vault/Dashboard.md`:
- Pending approvals count
- Recent completions
- Watcher health status
- Failed actions

### Audit Logs

All external actions logged to `AI_Employee_Vault/Logs/YYYY-MM-DD.json`:
```json
{
  "timestamp": "2026-01-21T10:30:00Z",
  "action_type": "email_sent",
  "actor": "orchestrator",
  "target": "client@example.com",
  "approval_status": "approved",
  "approved_by": "user",
  "result": "success"
}
```

### PM2 Monitoring

```bash
pm2 status          # Check process status
pm2 logs            # View logs
pm2 monit           # Real-time monitoring
pm2 restart all     # Restart all processes
```

---

## Troubleshooting

### Gmail Authentication Issues

```bash
# Re-authenticate
python scripts/setup/setup_gmail_oauth.py

# Test connection
python scripts/debug/debug_gmail.py
```

### WhatsApp Session Expired

```bash
# Restart watcher and scan QR code
python run_watcher.py --watcher whatsapp
# Scan QR code in browser
```

### LinkedIn Rate Limits

LinkedIn REST API has rate limits. The system automatically:
- Queues pending posts
- Retries with exponential backoff (1s, 2s, 4s, 8s, 16s)
- Notifies you of delays

### Orchestrator Not Executing

```bash
# Check orchestrator logs
tail -f logs/orchestrator.log

# Verify MCP servers are running
/mcp list

# Restart orchestrator
pm2 restart orchestrator
```

---

## Documentation

- **[SILVER_QUICKSTART.md](SILVER_QUICKSTART.md)** - Quick start guide with examples
- **[docs/MCP_SERVERS.md](docs/MCP_SERVERS.md)** - MCP server API documentation
- **[docs/APPROVAL_WORKFLOW.md](docs/APPROVAL_WORKFLOW.md)** - Approval workflow details
- **[docs/WATCHER_SETUP.md](docs/WATCHER_SETUP.md)** - Watcher configuration guide
- **[LINKEDIN_MIGRATION_GUIDE.md](My_AI_Employee/LINKEDIN_MIGRATION_GUIDE.md)** - LinkedIn OAuth2 setup
- **[SILVER_TIER_STATUS_REPORT.md](SILVER_TIER_STATUS_REPORT.md)** - Implementation status

---

## Security

### Credential Management

- All credentials stored in `.env` (gitignored)
- OAuth2 tokens auto-refresh
- Audit logs sanitize sensitive data:
  - API keys: First 4 chars + `***`
  - Passwords: `[REDACTED]`
  - Credit cards: Last 4 digits only
  - PII: Truncated

### Approval Workflow

- **All external actions require human approval**
- No action executes without explicit approval
- Rejection is logged and respected
- Approval requests expire after 24 hours

### Audit Trail

- All actions logged with timestamp, actor, target, result
- 90-day minimum retention
- JSONL format for easy parsing
- Credentials sanitized before logging

---

## Contributing

This is a personal AI employee system. If you want to adapt it for your use:

1. Fork the repository
2. Update `Company_Handbook.md` with your rules
3. Configure your credentials in `.env`
4. Customize watchers and MCP servers as needed

---

## License

[Your License Here]

---

## Support

For issues, questions, or feature requests:
- Check the documentation in `docs/`
- Review the status report: `SILVER_TIER_STATUS_REPORT.md`
- Check the troubleshooting section above

---

**Built with**: Python 3.13, FastMCP, Playwright, Google APIs, Claude Code
**Architecture**: Hackathon Zero Four-Layer AI Employee System
**Status**: 🟢 Production Ready (Gmail ✅, WhatsApp ✅, LinkedIn ⚠️ requires OAuth2 setup)
