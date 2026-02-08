---
name: xero-accounting
description: >
  Xero accounting integration for Gold Tier AI Employee. Monitors Xero transactions, syncs invoices,
  generates accounting reports, and integrates with CEO briefing. Uses official Xero MCP server or custom
  implementation. Use when: (1) Syncing Xero accounting data, (2) Generating accounting reports,
  (3) Tracking invoices and payments, (4) Business financial audits, (5) Integrating accounting with CEO briefings.
  Trigger phrases: "sync Xero", "accounting report", "invoice tracking", "financial audit", "Xero integration",
  "accounting summary", "revenue from Xero".
---

# Xero Accounting Integration (Gold Tier)

Xero accounting system integration for tracking business finances, invoices, and transactions. Integrates with CEO briefing for comprehensive financial reporting.

## Quick Start

### Option A: Use Official Xero MCP Server (Recommended)

The official Xero MCP server is available at: https://github.com/XeroAPI/xero-mcp-server

**Installation**:
```bash
# Clone the official server
git clone https://github.com/XeroAPI/xero-mcp-server.git xero-mcp
cd xero-mcp

# Install dependencies
npm install

# Configure .env with Xero credentials
cp .env.example .env
# Edit .env with your Xero API credentials
```

**Register in .mcp.json**:
```json
{
  "mcpServers": {
    "xero-mcp": {
      "command": "node",
      "args": ["/path/to/xero-mcp/dist/index.js"],
      "env": {
        "XERO_CLIENT_ID": "your_client_id",
        "XERO_CLIENT_SECRET": "your_client_secret",
        "XERO_REDIRECT_URI": "http://localhost:3000/callback",
        "XERO_SCOPES": "accounting.transactions accounting.contacts"
      }
    }
  }
}
```

### Option B: Use This Skill's Custom Implementation

This skill provides a simplified Xero integration using Python.

**Setup Xero OAuth2**:
```bash
# Create Xero app at https://developer.xero.com/app/manage
# Get client ID and secret
# Configure redirect URI

# Run setup script
python scripts/setup_xero_oauth.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ XERO ACCOUNTING INTEGRATION                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. XERO API (Official)                                      │
│     ├─ Invoices                                             │
│     ├─ Bank Transactions                                    │
│     ├─ Contacts                                             │
│     └─ Accounts                                             │
│                                                              │
│  2. XERO WATCHER (scripts/xero_watcher.py)                  │
│     ├─ Monitor new transactions                             │
│     ├─ Create accounting entries in vault                   │
│     └─ Sync to Accounting/Current_Month.md                  │
│                                                              │
│  3. ACCOUNTING AUDIT (scripts/accounting_audit.py)           │
│     ├─ Generate financial summaries                         │
│     ├─ Revenue analysis                                     │
│     └─ Expense tracking                                     │
│                                                              │
│  4. CEO BRIEFING INTEGRATION                                 │
│     └─ Feed financial data to weekly briefing               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Xero API Setup

### Step 1: Create Xero App

1. Go to https://developer.xero.com/app/manage
2. Create new app:
   - **App Type**: Public
   - **Company**: Select your company
   - **Redirect URI**: `http://localhost:3000/callback`

3. Note your credentials:
   - Client ID
   - Client Secret
   - Redirect URI

### Step 2: Configure OAuth2 Scopes

Required scopes for accounting:
```
accounting.transactions          # Read/write transactions
accounting.contacts             # Read/write contacts
accounting.reports.read         # Read financial reports
accounting.settings             # Read settings
```

### Step 3: Setup Environment Variables

**Add to .env**:
```bash
# Xero API Credentials
XERO_CLIENT_ID=your_client_id_here
XERO_CLIENT_SECRET=your_client_secret_here
XERO_REDIRECT_URI=http://localhost:3000/callback
XERO_SCOPES=accounting.transactions accounting.contacts accounting.reports.read

# Xero Tenant (organization)
XERO_TENANT_ID=your_tenant_id_here

# Refresh Token (obtained after first OAuth)
XERO_REFRESH_TOKEN=your_refresh_token_here
```

## Key Scripts

### 1. xero_watcher.py

Monitor Xero for new transactions and sync to vault.

**Usage**:
```bash
python scripts/xero_watcher.py --vault-path "AI_Employee_Vault"
```

**Features**:
- Polls Xero API every 5 minutes
- Detects new invoices, payments, bank transactions
- Creates accounting entries in `Accounting/Current_Month.md`
- Deduplicates based on transaction ID

**Output Format** (in Accounting/Current_Month.md):
```markdown
## Revenue Summary

| Date | Source | Invoice ID | Amount | Status |
|------|--------|------------|--------|--------|
| 2026-01-05 | Client A - Project Alpha | INV-0010 | $1,500.00 | Paid |
| 2026-01-10 | Client B - Website | INV-0011 | $2,000.00 | Paid |

## Expenses

| Date | Category | Description | Amount | Account |
|------|----------|-------------|--------|---------|
| 2026-01-01 | Software | Adobe CC | $54.99 | 610 |
| 2026-01-03 | Hosting | AWS | $45.00 | 620 |
```

### 2. accounting_audit.py

Generate accounting reports for CEO briefing.

**Usage**:
```bash
python scripts/accounting_audit.py --vault-path "AI_Employee_Vault" --period week
```

**Reports Generated**:
- Revenue summary (week, month, YTD)
- Expense breakdown by category
- Profit/loss statement
- Accounts receivable aging
- Accounts payable summary

### 3. setup_xero_oauth.py

One-time OAuth2 setup for Xero API access.

**Usage**:
```bash
python scripts/setup_xero_oauth.py
```

**Process**:
1. Opens browser for Xero authorization
2. User logs in and grants permissions
3. Receives authorization code
4. Exchanges for access token and refresh token
5. Saves tokens to `.xero_tokens.json`

## MCP Tools (Custom Implementation)

If building custom implementation (instead of official MCP server):

### get_invoices

Fetch invoices from Xero.

**Parameters**:
```python
{
  "status": "DRAFT" | "SUBMITTED" | "AUTHORISED" | "PAID",
  "date_from": "YYYY-MM-DD",
  "date_to": "YYYY-MM-DD"
}
```

**Returns**:
```python
{
  "invoices": [
    {
      "invoice_id": "INV-0010",
      "contact": "Client A",
      "amount": 1500.00,
      "status": "PAID",
      "date": "2026-01-05"
    }
  ]
}
```

### create_invoice

Create new invoice in Xero.

**Parameters**:
```python
{
  "contact": "Client Name",
  "amount": 1500.00,
  "description": "Project Phase 1",
  "due_date": "2026-01-30",
  "account_code": "200"  # Sales account
}
```

### get_bank_transactions

Fetch bank transactions from Xero.

**Parameters**:
```python
{
  "bank_account_id": "xxx-xxx-xxx",
  "date_from": "YYYY-MM-DD",
  "limit": 100
}
```

### get_financial_summary

Generate financial summary for CEO briefing.

**Returns**:
```python
{
  "revenue": {
    "week": 4300.00,
    "month": 8500.00,
    "ytd": 25000.00
  },
  "expenses": {
    "week": 500.00,
    "month": 1200.00,
    "ytd": 4500.00
  },
  "profit": {
    "week": 3800.00,
    "month": 7300.00,
    "ytd": 20500.00
  }
}
```

## Integration with CEO Briefing

The accounting data feeds into the weekly CEO briefing:

```python
# In weekly_audit.py
from xero_accounting import accounting_audit

# Get financial summary
financial_summary = accounting_audit.generate_summary(vault_path)

# Include in briefing
briefing_data['revenue'] = financial_summary['revenue']
briefing_data['expenses'] = financial_summary['expenses']
briefing_data['profit'] = financial_summary['profit']
```

## Vault Structure

```
AI_Employee_Vault/
├── Accounting/
│   ├── Current_Month.md          # This month's transactions (auto-synced)
│   ├── Previous_Months/          # Historical accounting data
│   │   ├── 2025-12.md
│   │   └── 2025-11.md
│   └── Financial_Reports/        # Generated reports
│       ├── Profit_Loss_YYYY-MM.md
│       └── Cash_Flow_YYYY-MM.md
└── .xero_tokens.json            # OAuth tokens (gitignored)
```

## Configuration

### Environment Variables (.env)

```bash
# Xero API
XERO_CLIENT_ID=your_client_id
XERO_CLIENT_SECRET=your_client_secret
XERO_REDIRECT_URI=http://localhost:3000/callback
XERO_TENANT_ID=your_tenant_id
XERO_REFRESH_TOKEN=your_refresh_token

# Watcher Settings
XERO_WATCHER_INTERVAL=300        # Check every 5 minutes
XERO_SYNC_DAYS_BACK=30           # Sync last 30 days on first run
```

### Company_Handbook.md Integration

```markdown
## Xero Accounting Integration

### Sync Settings
- Watcher interval: Every 5 minutes
- Sync period: Last 30 days
- Auto-categorization: Enabled

### Account Codes
- 200: Sales Revenue
- 610: Software Subscriptions
- 620: Hosting & Infrastructure
- 630: Professional Services
- 400: Cost of Goods Sold

### Invoice Rules
- Draft invoices: Review weekly
- Payment terms: Net 15
- Late fee: 1.5% monthly
```

## Troubleshooting

### Common Issues

**Issue**: "Invalid refresh token"

**Solution**: Tokens expired, re-run OAuth setup:
```bash
python scripts/setup_xero_oauth.py
```

**Issue**: "Tenant not authorized"

**Solution**: Re-authorize the app in Xero:
1. Go to https://login.xero.com/
2. Settings → Connected Apps
3. Reauthorize your app

**Issue**: "Rate limit exceeded"

**Solution**: Xero API allows 60 requests per minute. Add delay:
```bash
# In .env
XERO_REQUEST_DELAY=1  # Seconds between requests
```

### Logging

Xero watcher logs to `logs/xero_watcher.log`:
```bash
tail -f logs/xero_watcher.log
```

## Security Best Practices

### Token Storage

- Tokens stored in `.xero_tokens.json` (gitignored)
- Encrypt tokens for production use
- Never commit tokens to git
- Rotate tokens every 60 days

### Access Control

- Use read-only scopes where possible
- Limit access to required accounts only
- Audit API access regularly

### Data Protection

- Financial data stored locally only
- No cloud transmission beyond Xero API
- Audit all API calls

## References

- [Xero API Documentation](https://developer.xero.com/documentation/)
- [Official Xero MCP Server](https://github.com/XeroAPI/xero-mcp-server)
- [Xero OAuth2 Guide](https://developer.xero.com/app/overview)

## Key Scripts

- `scripts/setup_xero_oauth.py` - OAuth2 setup
- `scripts/xero_watcher.py` - Transaction watcher
- `scripts/accounting_audit.py` - Financial reports
- `scripts/xero_mcp.py` - Custom MCP server (optional)
