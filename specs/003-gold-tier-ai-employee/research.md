# Research: Gold Tier AI Employee

**Feature**: Gold Tier AI Employee
**Date**: 2026-02-05
**Status**: Complete

## Overview

This document consolidates research findings for implementing Gold Tier features: Monday Morning CEO Briefing, Social Media Cross-Posting (Facebook/Instagram/Twitter), Xero Accounting Integration, and Social Media Monitoring.

## Research Areas

### 1. Playwright Multi-Platform Session Management

**Question**: How to maintain persistent browser sessions across Facebook, Instagram, and Twitter/X without conflicts?

**Decision**: Use separate Playwright persistent contexts per platform with unique CDP ports

**Rationale**:
- Each social platform requires separate authentication and session storage
- CDP (Chrome DevTools Protocol) port isolation prevents context conflicts
- WhatsApp watcher already uses port 9222, so social media will use 9223
- Playwright's `launch_persistent_context()` handles session cookies, localStorage, and sessionStorage automatically

**Implementation**:
```python
# Separate contexts per platform
contexts = {
    'facebook': {
        'user_data_dir': '.social_session/facebook/',
        'cdp_port': 9223
    },
    'instagram': {
        'user_data_dir': '.social_session/instagram/',
        'cdp_port': 9224
    },
    'twitter': {
        'user_data_dir': '.social_session/twitter/',
        'cdp_port': 9225
    }
}
```

**Alternatives Considered**:
- Single context with multiple tabs: Rejected due to cookie conflicts between platforms
- Shared CDP port: Rejected due to WhatsApp watcher already using 9222

**References**:
- Playwright Documentation: https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch-persistent-context
- Demo-hack WhatsApp watcher pattern for session persistence

---

### 2. FastMCP for Social Media Automation

**Question**: Should we use official MCP servers or build custom FastMCP servers for social media posting?

**Decision**: Build custom FastMCP server using FastMCP Python framework

**Rationale**:
- No official MCP servers exist for Facebook/Instagram/Twitter posting
- FastMCP provides Pydantic v2 validation out of the box
- Browser automation via Playwright is more reliable than scraping APIs
- Faster implementation (days vs. weeks for official API approval)
- No rate limiting concerns (browser automation respects platform UI)

**Implementation**:
```python
from fastmcp import FastMCP

mcp = FastMCP(name="social-browser-mcp")

@mcp.tool()
async def post_to_facebook(
    text: str,
    image_path: str | None = None
) -> dict:
    """Post content to Facebook page via browser automation."""
    # Playwright implementation
    pass
```

**Alternatives Considered**:
- Official Facebook Graph API: Rejected due to 1-2 week approval process, restrictive rate limits
- Official Instagram Basic Display API: Rejected due to limited posting permissions, requires business account verification
- Official Twitter/X API v2: Rejected due to tiered pricing, write API requires paid tier
- Scrapy/requests-html: Rejected due to poor JavaScript rendering support

**References**:
- FastMCP Documentation: https://github.com/jlowin/fastmcp
- Demo-hack LinkedIn REST API v2 implementation (existing pattern)

---

### 3. Xero Integration: Official MCP vs. Custom Implementation

**Question**: Should we use official Xero MCP server or build custom Python implementation?

**Decision**: Support both - recommend official Xero MCP server, provide custom fallback

**Rationale**:
- Official Xero MCP server (https://github.com/XeroAPI/xero-mcp-server) exists and is maintained
- Official server handles OAuth2 token refresh, rate limiting, and API changes
- Custom implementation as fallback for users who prefer Python-only stack
- Both approaches use same Xero API endpoints and data structures

**Implementation (Official MCP)**:
```json
{
  "mcpServers": {
    "xero-mcp": {
      "command": "node",
      "args": ["/path/to/xero-mcp/dist/index.js"],
      "env": {
        "XERO_CLIENT_ID": "your_client_id",
        "XERO_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

**Implementation (Custom Python)**:
```python
# Fallback for users without Node.js
import requests
from datetime import datetime, timedelta

class XeroWatcher:
    def __init__(self, client_id, client_secret, refresh_token):
        self.base_url = "https://api.xero.com/api.xro/2.0"
        # OAuth2 and token management
```

**Alternatives Considered**:
- QuickBooks integration: Rejected due to hackathon scope (Xero specified in requirements)
- Manual accounting entry: Rejected due to Gold tier automation requirements

**References**:
- Official Xero MCP Server: https://github.com/XeroAPI/xero-mcp-server
- Xero API Documentation: https://developer.xero.com/documentation/

---

### 4. Monday Briefing Scheduling Strategy

**Question**: How to schedule Monday 7:00 AM briefing generation across platforms (Windows/Linux/Mac)?

**Decision**: Platform-specific scheduling (cron on Linux/Mac, Task Scheduler on Windows)

**Rationale**:
- No Python-native cross-platform scheduler with platform persistence
- Cron and Task Scheduler are built-in and reliable
- Python scripts can be invoked by platform schedulers
- Simple configuration via .env file for user customization

**Implementation (Linux/Mac - Cron)**:
```bash
# Edit crontab
crontab -e

# Add: Every Monday at 7:00 AM
0 7 * * 1 cd /path/to/project && python .claude/skills/weekly-ceo-briefing/scripts/weekly_audit.py --vault-path "AI_Employee_Vault"
```

**Implementation (Windows - Task Scheduler)**:
```xml
<Task>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-06T07:00:00</StartBoundary>
      <ScheduleByWeek>
        <DaysOfWeek>
          <Day Monday="true"/>
        </DaysOfWeek>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>python.exe</Command>
      <Arguments>.claude\skills\weekly-ceo-briefing\scripts\weekly_audit.py --vault-path "AI_Employee_Vault"</Arguments>
    </Exec>
  </Actions>
</Task>
```

**Alternatives Considered**:
- Python `schedule` library: Rejected due to lack of persistence across restarts
- APScheduler with SQLAlchemy: Rejected as over-engineered for single-user system
- Cloud-based scheduling (GitHub Actions): Rejected due to local-first architecture

**References**:
- Cron documentation: https://man7.org/linux/man-pages/man5/crontab.5.html
- Windows Task Scheduler: https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page

---

### 5. Graceful Degradation Strategy

**Question**: How to ensure CEO briefing generation continues when Xero sync or social monitoring fails?

**Decision**: Component isolation with partial data generation

**Rationale**:
- Each Gold tier feature operates independently
- Weekly briefing generator should use available data and warn about missing sources
- Constitution Principle X (Graceful Degradation) requires this design
- Prevents single point of failure from breaking entire Gold tier

**Implementation**:
```python
def generate_briefing(self) -> Path:
    # Load all data sources with try-except
    business_goals = self.load_business_goals()  # May fail
    revenue_data = self.load_revenue_data()       # May fail
    tasks_data = self.load_tasks_data()          # May fail
    social_data = self.load_social_data()        # May fail

    # Generate briefing with available data
    available_sources = []
    missing_sources = []

    if business_goals:
        available_sources.append("Business_Goals.md")
    else:
        missing_sources.append("Business_Goals.md")

    # Include warnings in briefing
    if missing_sources:
        briefing_content += f"\n**Warnings**: Missing data sources: {', '.join(missing_sources)}\n"
```

**Failure Modes Matrix**:
| Component | Failure Impact | Mitigation |
|-----------|---------------|------------|
| Xero watcher | No revenue data | Use manual Accounting/Current_Month.md entry |
| Social watcher | No engagement metrics | Omit social section from briefing |
| Tasks/Done/ | No completed task analysis | Warning in briefing |
| Business_Goals.md | No revenue targets | Skip progress percentage, show absolute revenue only |

**Alternatives Considered**:
- All-or-nothing approach: Rejected due to single point of failure
- Retry until success: Rejected due to potential indefinite delays

**References**:
- Constitution Principle X: Graceful Degradation and Error Handling
- Silver tier multi-watcher isolation pattern

---

### 6. Social Media Priority Filtering Algorithm

**Question**: How to accurately prioritize social media interactions (HIGH/MEDIUM/LOW) for action item creation?

**Decision**: Keyword-based scoring with whitelist override

**Rationale**:
- Simple to implement and maintain
- Company_Handbook.md as single source of truth for keywords
- Whitelist for important accounts (clients, partners)
- Scoring system allows fine-tuning priority thresholds

**Implementation**:
```python
def calculate_priority(interaction: dict, handbook_rules: dict) -> str:
    score = 0

    # HIGH priority keywords (weight: 10)
    high_keywords = handbook_rules.get('HIGH_PRIORITY_KEYWORDS', [])
    for keyword in high_keywords:
        if keyword.lower() in interaction['content'].lower():
            score += 10

    # BUSINESS keywords (weight: 5)
    business_keywords = handbook_rules.get('BUSINESS_KEYWORDS', [])
    for keyword in business_keywords:
        if keyword.lower() in interaction['content'].lower():
            score += 5

    # Whitelist override (weight: 15)
    whitelist = handbook_rules.get('WHITELIST_ACCOUNTS', [])
    if interaction['author_handle'] in whitelist:
        score += 15

    # Assign priority based on score
    if score >= 15:
        return 'HIGH'
    elif score >= 5:
        return 'MEDIUM'
    else:
        return 'LOW'
```

**Alternatives Considered**:
- Machine learning classification: Rejected as over-engineered for MVP
- Sentiment analysis API: Rejected due to external dependency and cost
- Manual triage for all interactions: Rejected due to time cost

**References**:
- Social Media Watcher SKILL.md: Keyword filtering rules
- Company_Handbook.md integration pattern

---

### 7. Multi-Currency Support for Xero Integration

**Question**: How to handle Xero transactions in multiple currencies (USD, EUR, GBP)?

**Decision**: Convert all amounts to base currency using exchange rate API

**Rationale**:
- CEO briefing needs single-currency revenue totals for health score calculation
- Xero API provides currency code for each transaction
- Exchange rate API (exchangerate-api.io) has free tier for < 1,500 requests/month
- Store both original and converted amounts for audit trail

**Implementation**:
```python
def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert currency using exchange rate API."""
    if from_currency == to_currency:
        return amount

    response = requests.get(
        f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    )
    rates = response.json()['rates']
    converted = amount * rates[to_currency]
    return converted

# Store in Accounting/Current_Month.md
# | Date | Source | Amount (Original) | Amount (USD) | Status |
# | 2026-01-05 | Client A - INV-0010 | €1,200.00 | $1,308.00 | Paid |
```

**Alternatives Considered**:
- Store in original currency only: Rejected due to health score calculation issues
- Require all transactions in single currency: Rejected as unrealistic for global businesses
- Use paid currency API (Xe.com, OANDA): Rejected due to cost

**References**:
- Exchange Rate API: https://www.exchangerate-api.com/
- Xero API Currency Documentation: https://developer.xero.com/documentation/api/accounting/transactions

---

### 8. Error Recovery and Retry Strategy

**Question**: What retry strategy for transient failures (network timeout, rate limit, API errors)?

**Decision**: Exponential backoff with max 3 retries

**Rationale**:
- Constitution Principle VI (Technology Stack) specifies exponential backoff with max 3 retries
- Prevents hammering failing APIs
- Balances resilience with fast failure notification
- Dead letter queue (/Failed/ folder) for manual intervention

**Implementation**:
```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (TimeoutError, HTTPError, ConnectionError) as e:
                    if attempt == max_retries - 1:
                        raise  # Re-raise after final attempt
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, base_delay=1)
def post_to_social_media(platform: str, content: dict) -> dict:
    # Implementation
    pass
```

**Retry Schedule**:
- Attempt 1: Immediate
- Attempt 2: 1 second delay
- Attempt 3: 2 seconds delay
- Attempt 4: 4 seconds delay (final attempt)

**Failure Handling**:
- All retries exhausted → Move to /Failed/ with error details
- Create action item in Needs_Action/ for manual intervention
- Log all retry attempts with timestamps

**Alternatives Considered**:
- No retries (fail fast): Rejected due to transient network issues
- Infinite retries: Rejected due to resource exhaustion risk
- Circuit breaker pattern: Rejected as over-engineered for single-user system

**References**:
- Constitution Principle VI: Technology Stack (error handling)
- Silver tier graceful degradation patterns

---

## Summary of Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| Browser Sessions | Separate Playwright contexts per platform | Avoid cookie conflicts, leverage WhatsApp pattern |
| MCP Servers | Custom FastMCP for social, official Xero MCP | No official social MCP servers, Xero has official support |
| Scheduling | Platform-specific (cron/Task Scheduler) | Built-in, reliable, no Python dependency |
| Graceful Degradation | Component isolation with partial data | Prevent single point of failure |
| Priority Filtering | Keyword-based scoring with whitelist | Simple, maintainable, Company_Handbook-driven |
| Multi-Currency | Convert to base currency via API | Health score needs single currency |
| Retry Strategy | Exponential backoff, max 3 retries | Balance resilience with fast failure |

## Unresolved Questions

None - all technical unknowns have been resolved through research.

## Next Steps

1. ✅ Research complete
2. ⏭️ Create data-model.md (entity definitions from spec)
3. ⏭️ Create contracts/ (API contracts for MCP tools)
4. ⏭️ Create quickstart.md (setup and usage guide)
5. ⏭️ Update plan.md with complete technical context
6. ⏭️ Run agent context update script
7. ⏭️ Re-evaluate Constitution Check post-design
