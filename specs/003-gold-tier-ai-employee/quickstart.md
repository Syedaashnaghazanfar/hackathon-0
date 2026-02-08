# Gold Tier AI Employee - Quick Start Guide

**Version**: 1.0.0
**Last Updated**: 2026-02-05
**Prerequisites**: Silver Tier AI Employee fully operational

## Overview

Gold Tier extends Silver with four major features:
1. **Monday Morning CEO Briefing** - Automated business audit with health scores
2. **Social Media Cross-Posting** - Facebook/Instagram/Twitter automation
3. **Xero Accounting Integration** - Financial data sync
4. **Social Media Monitoring** - Engagement tracking (optional)

## Prerequisites Checklist

Before starting Gold Tier setup, ensure:

- [ ] Silver Tier fully operational (multi-watcher infrastructure running)
- [ ] Obsidian vault exists with folder structure: `Needs_Action/`, `Pending_Approval/`, `Approved/`, `Done/`, `Logs/`
- [ ] Python 3.13+ installed with `uv` package manager
- [ ] Playwright installed (`uv run playwright install chromium`)
- [ ] At least 4GB RAM available for browser automation
- [ ] Active internet connection for all external integrations

## Installation

### Step 1: Clone Gold Tier Skills

Gold tier skills are already created in `.claude/skills/`. Verify they exist:

```bash
ls .claude/skills/
# Expected output:
# social-media-browser-mcp/
# weekly-ceo-briefing/
# xero-accounting/
# social-media-watcher/
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies
cd .claude/skills/weekly-ceo-briefing
uv sync

cd ../social-media-browser-mcp
uv sync

cd ../xero-accounting
uv sync

cd ../social-media-watcher
uv sync
```

### Step 3: Configure Environment Variables

Create or update `.env` file in project root:

```bash
# Gold Tier: CEO Briefing Settings
BRIEFING_DAY=monday
BRIEFING_TIME=07:00
BRIEFING_TIMEZONE=America/New_York

# Gold Tier: Social Media Posting
SOCIAL_SESSION_DIR=.social_session
SOCIAL_FB_CDP_PORT=9223
SOCIAL_IG_CDP_PORT=9224
SOCIAL_TW_CDP_PORT=9225

# Gold Tier: Social Media Monitoring (Optional)
SOCIAL_WATCHER_ENABLED=true
SOCIAL_WATCHER_INTERVAL=600  # 10 minutes
SOCIAL_HIGH_PRIORITY_KEYWORDS=urgent,help,pricing,cost,invoice,payment,client,emergency
SOCIAL_BUSINESS_KEYWORDS=project,services,quote,proposal,consulting,hire,contract
SOCIAL_WHITELIST_ACCOUNTS=client_a,client_b,important_contact

# Gold Tier: Xero Accounting (Optional)
XERO_CLIENT_ID=your_client_id_here
XERO_CLIENT_SECRET=your_client_secret_here
XERO_REDIRECT_URI=http://localhost:3000/callback
XERO_TENANT_ID=your_tenant_id_here
XERO_REFRESH_TOKEN=your_refresh_token_here
XERO_WATCHER_INTERVAL=300  # 5 minutes
```

## Feature Setup Guides

### Feature 1: Monday Morning CEO Briefing

**Setup Time**: 15 minutes

#### 1.1 Create Business Goals Template

Create `AI_Employee_Vault/Business_Goals.md`:

```markdown
---
monthly_goal: 10000.00
currency: USD
target_date: "2026-01-31"
metrics:
  - metric: "Client response time"
    target: "< 24 hours"
    alert_threshold: "> 48 hours"
    current: "18 hours"
  - metric: "Invoice payment rate"
    target: "> 90%"
    alert_threshold: "< 80%"
    current: "85%"
active_projects:
  - name: "Project Alpha"
    due_date: "2026-01-15"
    budget: 2000.00
    status: "On Track"
audit_rules:
  unused_subscription_days: 30
  cost_increase_threshold: 20
---

# Business Goals

## Q1 2026 Objectives

### Revenue Target
- Monthly goal: $10,000
- Current MTD: $0 (will update automatically)
- Target date: January 31

### Key Metrics to Track

| Metric | Target | Alert Threshold | Current |
|--------|--------|-----------------|---------|
| Client response time | < 24 hours | > 48 hours | 18 hours |
| Invoice payment rate | > 90% | < 80% | 85% |
| Software costs | < $500/month | > $600/month | $450 |

### Active Projects

1. Project Alpha - Due Jan 15 - Budget $2,000 - Status: On Track

### Subscription Audit Rules

Flag for review if:
- No login in 30 days
- Cost increased > 20%
- Duplicate functionality with another tool
```

#### 1.2 Create Accounting Template

Create `AI_Employee_Vault/Accounting/Current_Month.md`:

```markdown
# Accounting - January 2026

## Revenue Summary

| Date | Source | Invoice ID | Amount | Status | Notes |
|------|--------|------------|--------|--------|-------|
| 2026-01-05 | Client A - Project Alpha | INV-0010 | $1,500.00 | Paid | Deposit received |

**Total Revenue**: $1,500.00

## Expenses

| Date | Category | Description | Amount | Account | Notes |
|------|----------|-------------|--------|---------|-------|
| 2026-01-01 | Software | Adobe CC | $54.99 | 610 | Monthly subscription |

**Total Expenses**: $54.99
**Net Profit**: $1,445.01
```

#### 1.3 Test Briefing Generation

```bash
# Manual generation (for testing)
python .claude/skills/weekly-ceo-briefing/scripts/weekly_audit.py --vault-path "AI_Employee_Vault"

# Expected output:
# Briefing generated: AI_Employee_Vault/Briefings/2026-01-06_Monday_Briefing.md
```

#### 1.4 Schedule Automatic Briefing

**Linux/Mac (cron)**:
```bash
# Edit crontab
crontab -e

# Add: Every Monday at 7:00 AM
0 7 * * 1 cd /path/to/project && python .claude/skills/weekly-ceo-briefing/scripts/weekly_audit.py --vault-path "AI_Employee_Vault"
```

**Windows (Task Scheduler)**:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Weekly on Monday at 7:00 AM
4. Action: `python.exe`
5. Arguments: `.claude\skills\weekly-ceo-briefing\scripts\weekly_audit.py --vault-path "AI_Employee_Vault"`

---

### Feature 2: Social Media Cross-Posting

**Setup Time**: 30 minutes (first-time login per platform)

#### 2.1 Start Social Media Browser MCP Server

```bash
cd .claude/skills/social-media-browser-mcp
uv run mcp dev
```

Expected output: `MCP server running on http://localhost:9223`

#### 2.2 Login to Facebook (One-Time Setup)

```bash
# In separate terminal, run login helper
uv run python scripts/login_facebook.py
```

1. Browser opens to Facebook login
2. Login with your Facebook credentials
3. Navigate to your Facebook Page
4. Press Enter when logged in
5. Session saved to `.social_session/facebook/`

#### 2.3 Login to Instagram (One-Time Setup)

```bash
uv run python scripts/login_instagram.py
```

1. Browser opens to Instagram login
2. Login with your Instagram credentials (business account)
3. Press Enter when logged in
4. Session saved to `.social_session/instagram/`

#### 2.4 Login to Twitter/X (One-Time Setup)

```bash
uv run python scripts/login_twitter.py
```

1. Browser opens to Twitter/X login
2. Login with your Twitter/X credentials
3. Press Enter when logged in
4. Session saved to `.social_session/twitter/`

#### 2.5 Test Social Posting

Create test action item `AI_Employee_Vault/Pending_Approval/social_post_facebook_test.md`:

```markdown
---
type: social_post
platform: facebook
content_type: text
status: pending
created: 2026-01-06T08:00:00Z
---

# Test Post

## Content

**Text**: "Testing Gold Tier social media automation! 🚀"

## Target Platform

**Facebook**: Post to page feed (no image)

## Approval Decision

**[ ] APPROVE** - Move this file to `/Approved/` folder
**[ ] REJECT** - Move this file to `/Rejected/` folder with reason
```

Move to `/Approved/` folder, verify post appears on Facebook page within 60 seconds.

#### 2.6 Verify Session Persistence

```bash
# Stop MCP server (Ctrl+C)
# Restart MCP server
uv run mcp dev

# Test posting again without re-login
# Should work immediately using saved session
```

---

### Feature 3: Xero Accounting Integration

**Setup Time**: 20 minutes (requires Xero account)

#### 3.1 Create Xero App (One-Time Setup)

1. Go to https://developer.xero.com/app/manage
2. Create new app:
   - **App Type**: Public
   - **Company**: Select your company
   - **Redirect URI**: `http://localhost:3000/callback`
3. Note your credentials:
   - Client ID
   - Client Secret

#### 3.2 Configure OAuth2 Scopes

Required scopes (add in Xero app settings):
```
accounting.transactions
accounting.contacts
accounting.reports.read
accounting.settings
```

#### 3.3 Setup Environment Variables

Add to `.env`:
```bash
XERO_CLIENT_ID=your_client_id_here
XERO_CLIENT_SECRET=your_client_secret_here
XERO_REDIRECT_URI=http://localhost:3000/callback
```

#### 3.4 Run OAuth2 Setup

```bash
cd .claude/skills/xero-accounting
uv run python scripts/setup_xero_oauth.py
```

1. Browser opens to Xero authorization
2. Login to Xero and grant permissions
3. Tokens saved to `.xero_tokens.json`

#### 3.5 Test Xero Sync

```bash
# Manual sync (for testing)
uv run python scripts/xero_watcher.py --vault-path "AI_Employee_Vault"

# Expected output:
# Xero watcher started
# Syncing invoices...
# Synced 3 invoices to Accounting/Current_Month.md
# Syncing bank transactions...
# Synced 5 transactions to Accounting/Current_Month.md
# Sync complete
```

#### 3.6 Verify Accounting Data

Check `AI_Employee_Vault/Accounting/Current_Month.md` - should show new transactions from Xero.

#### 3.7 Schedule Automatic Sync

**Linux/Mac (cron)**:
```bash
# Add to crontab: Every 5 minutes
*/5 * * * * cd /path/to/project && uv run python .claude/skills/xero-accounting/scripts/xero_watcher.py --vault-path "AI_Employee_Vault"
```

**Windows (Task Scheduler)**:
1. Create task to run on startup
2. Trigger: At startup, repeat every 5 minutes
3. Action: Run `uv run python scripts/xero_watcher.py`

---

### Feature 4: Social Media Monitoring (Optional)

**Setup Time**: 20 minutes

#### 4.1 Configure Priority Keywords

Update `AI_Employee_Vault/Company_Handbook.md`:

```markdown
## Social Media Monitoring

### Priority Rules

#### HIGH Priority (Immediate Action Required)
- Keywords: urgent, help, pricing, invoice, payment, client
- Sources: Direct messages, high-value clients
- Action: Create action item with priority=HIGH

#### MEDIUM Priority (Respond Within 24 Hours)
- Keywords: project, services, quote, proposal, consulting
- Sources: Comments, mentions
- Action: Create action item with priority=MEDIUM

#### LOW Priority (Monitor Only)
- Generic engagement, spam, low-value interactions
- Action: Log only, no action item
```

#### 4.2 Test Social Media Watcher

```bash
cd .claude/skills/social-media-watcher
uv run python scripts/social_media_watcher.py --vault-path "AI_Employee_Vault"

# Expected output:
# Social media watcher started
# Checking Facebook...
# Checking Instagram...
# Checking Twitter...
# Detected 2 new interactions
# Created 1 action item in Needs_Action/
# Watcher complete (will check again in 10 minutes)
```

#### 4.3 Schedule Continuous Monitoring

**Linux/Mac (cron)**:
```bash
# Add to crontab: Every 10 minutes
*/10 * * * * cd /path/to/project && uv run python .claude/skills/social-media-watcher/scripts/social_media_watcher.py --vault-path "AI_Employee_Vault"
```

**Windows (Task Scheduler)**:
1. Create task to run on startup
2. Trigger: At startup, repeat every 10 minutes
3. Action: Run `uv run python scripts/social_media_watcher.py`

---

## Verification Checklist

After completing all feature setups, verify Gold Tier is operational:

### CEO Briefing
- [ ] Monday briefing generates automatically at 7:00 AM
- [ ] Briefing includes health score, revenue analysis, bottleneck detection
- [ ] Dashboard.md updated with briefing link
- [ ] Briefing handles missing data gracefully (graceful degradation)

### Social Media Posting
- [ ] Facebook posts publish successfully < 60 seconds from approval
- [ ] Instagram posts publish successfully < 90 seconds from approval
- [ ] Twitter/X posts publish successfully < 45 seconds from approval
- [ ] Sessions persist across browser restarts (no re-login needed)
- [ ] Authentication failures detected and reported clearly

### Xero Accounting
- [ ] Invoices sync from Xero within 5 minutes of creation
- [ ] Bank transactions sync to Accounting/Current_Month.md
- [ ] Multi-currency transactions converted to base currency
- [ ] Token refresh happens automatically before expiry
- [ ] CEO briefing includes Xero revenue data

### Social Media Monitoring
- [ ] Watcher detects new comments/messages/mentions
- [ ] HIGH priority interactions create action items
- [ ] LOW priority interactions logged only
- [ ] Daily engagement summaries generate at 6:00 PM
- [ ] Whitelisted accounts always create action items

### Integration
- [ ] CEO briefing includes data from all Gold tier features
- [ ] Single Gold tier feature failure doesn't break others
- [ ] All external actions require HITL approval
- [ ] Audit logs capture all executions with sanitized credentials

## Troubleshooting

### Issue: "Briefing not generating automatically"

**Solution**:
- Check cron/task scheduler logs for errors
- Verify vault path is correct in scheduled command
- Test manual briefing generation to isolate issue

### Issue: "Social media session expired"

**Solution**:
```bash
# Re-run login helper for affected platform
cd .claude/skills/social-media-browser-mcp
uv run python scripts/login_facebook.py  # or login_instagram.py, login_twitter.py
```

### Issue: "Xero token expired"

**Solution**:
```bash
cd .claude/skills/xero-accounting
uv run python scripts/setup_xero_oauth.py
```

### Issue: "Briefing missing revenue data"

**Solution**:
- Verify Xero watcher is running and syncing
- Check `Accounting/Current_Month.md` has transactions
- Ensure `Business_Goals.md` exists with `monthly_goal` in frontmatter

### Issue: "Social media posting slow (> 2 minutes)"

**Solution**:
- Check internet connection speed
- Verify browser automation is not blocked by antivirus
- Reduce image file size (Instagram upload slower with large files)

## Next Steps

1. **Customize Business Goals**: Update `Business_Goals.md` with your actual targets and metrics
2. **Configure Priority Keywords**: Tailor social media filtering rules in `Company_Handbook.md`
3. **Set Up Multi-Watcher Orchestrator**: Integrate Gold tier watchers with existing Silver tier watchers
4. **Monitor First Week**: Review all generated briefings, social posts, and Xero sync logs
5. **Adjust Scheduling**: Fine-tune briefing time, watcher intervals based on your workflow

## Support

For issues or questions:
- Check skill-specific SKILL.md files in `.claude/skills/*/`
- Review logs in `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- Consult Silver Tier documentation for HITL approval workflow
- Report bugs via GitHub issues

---

**Congratulations! You've successfully set up Gold Tier AI Employee! 🎉**

Your AI Employee now provides:
- 📊 Automated business audits every Monday morning
- 📱 Social media cross-posting to 3 platforms
- 💰 Real-time financial data from Xero
- 👥 Proactive social media engagement monitoring

Enjoy your proactive AI-powered business assistant!
