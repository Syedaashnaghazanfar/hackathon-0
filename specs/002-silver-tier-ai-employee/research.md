# Research: Silver Tier Technology Decisions

**Feature**: Silver Tier AI Employee
**Date**: 2026-01-22
**Phase**: 0 (Technology Selection)

This document consolidates research findings and technology decisions for implementing Silver tier external action execution with HITL approval.

---

## 1. MCP Server Framework

### Decision: **FastMCP** with Pydantic v2 Validation

**Rationale**:
- Official MCP framework recommended by Anthropic for building Model Context Protocol servers
- Built-in Pydantic v2 validation ensures type-safe tool inputs/outputs
- Native support for tool registration, error handling, and JSON-RPC protocol
- Active community (GitHub stars: 2.5k+, weekly updates)
- Minimal boilerplate compared to raw JSON-RPC implementation

**Alternatives Considered**:
1. **Custom JSON-RPC Server**
   - **Rejected**: Requires implementing protocol details (request/response handling, error codes, tool registry)
   - **Why not chosen**: Reinventing wheel; FastMCP provides all needed abstractions with better error handling

2. **MCP Python SDK (anthropic/mcp-python)**
   - **Considered**: Official reference implementation
   - **Why FastMCP chosen instead**: FastMCP is built on top of mcp-python with developer-friendly decorators (`@mcp.tool()`) and automatic schema generation from Python type hints

**Implementation Notes**:
- Install via `uv add fastmcp`
- Each MCP server (email, LinkedIn, browser) runs as independent FastAPI-like server
- Dry-run mode implemented via environment variable check in tool implementations
- Error responses include actionable messages (e.g., "OAuth token expired - run refresh script")

**References**:
- FastMCP GitHub: https://github.com/jlowin/fastmcp
- MCP Specification: https://spec.modelcontextprotocol.io

---

## 2. Browser Automation for WhatsApp Web

### Decision: **Playwright** (Async Python API)

**Rationale**:
- **WhatsApp Web has no official API** - browser automation is the only option
- Playwright advantages over Selenium:
  - Headless Chrome support out-of-the-box
  - Persistent browser contexts (session stored in `.whatsapp_session/` directory)
  - Auto-wait for elements (reduces flaky tests)
  - CDP (Chrome DevTools Protocol) support for advanced control
  - Better documentation for async Python usage
- Production-proven: Used by 100k+ projects for web scraping

**Alternatives Considered**:
1. **Selenium WebDriver**
   - **Rejected**: More verbose API, slower element detection, requires explicit waits
   - **Why not chosen**: Playwright's auto-wait and persistent contexts are better for long-running watcher processes

2. **Puppeteer (Node.js)**
   - **Rejected**: Would require Node.js runtime alongside Python
   - **Why not chosen**: Stack consistency (keep everything Python 3.13)

3. **WhatsApp Business API**
   - **Rejected**: Requires business account verification, limited to business use cases only
   - **Why not chosen**: Consumer WhatsApp accounts don't have API access

**Implementation Notes**:
- Install via `uv add playwright && playwright install chromium`
- QR code scan once, session reused on restart (`.whatsapp_session/` directory)
- Urgent keyword detection: regex match on message text (`invoice|payment|help|urgent|ASAP` case-insensitive)
- CDP port 9222 for debugging

**References**:
- Playwright Python Docs: https://playwright.dev/python/docs/intro
- WhatsApp Web Automation Guide: https://medium.com/@sahelanand/whatsapp-automation-with-playwright

---

## 3. Gmail API Integration

### Decision: **Google API Python Client** with OAuth 2.0

**Rationale**:
- Official Google library for Gmail API access
- OAuth 2.0 is the only supported authentication method (no API keys or passwords)
- Automatic token refresh via `google-auth` library
- Supports both reading (inbox monitoring) and sending (email MCP server)

**Alternatives Considered**:
1. **IMAP/SMTP for Gmail**
   - **Rejected**: Gmail deprecated "less secure apps" access in 2022
   - **Why not chosen**: OAuth 2.0 is mandatory for modern Gmail integrations

2. **Nylas Email API (third-party wrapper)**
   - **Rejected**: Requires Nylas account and monthly fees for production use
   - **Why not chosen**: Direct Gmail API is free and avoids third-party dependencies

**Implementation Notes**:
- Dependencies:
  ```python
  google-api-python-client>=2.100.0
  google-auth-oauthlib>=1.1.0
  google-auth-httplib2>=0.1.1
  ```
- OAuth2 flow:
  1. User runs `setup_gmail_oauth.py` script → opens browser for Google consent
  2. Callback handler saves `token.json` with refresh token
  3. Watcher/MCP server loads token, auto-refreshes if expired (using `Credentials.refresh()`)
- Scopes: `https://www.googleapis.com/auth/gmail.modify` (read + send)
- Setup script guides user through Google Cloud Console credential creation

**References**:
- Gmail API Quickstart: https://developers.google.com/gmail/api/quickstart/python
- OAuth 2.0 Guide: https://developers.google.com/identity/protocols/oauth2

---

## 4. LinkedIn Integration

### Decision: **LinkedIn REST API v2** with Bearer Token

**Rationale**:
- Official API for LinkedIn posting (UGC Post API)
- OAuth 2.0 access token obtained via authorization code flow
- Rate limits: 100 requests/day for individual developers (sufficient for Silver tier)
- Supports text posts, media uploads, hashtags, visibility control

**Alternatives Considered**:
1. **Playwright-based LinkedIn Automation**
   - **Considered**: Fallback if API rate limits are too restrictive
   - **Why API preferred**: Reliable, no CAPTCHA/bot detection risks, official support

2. **Third-party services (Buffer, Hootsuite)**
   - **Rejected**: Monthly fees, external dependencies, not local-first
   - **Why not chosen**: Direct API keeps everything in user's control

**Implementation Notes**:
- Environment variables:
  ```bash
  LINKEDIN_ACCESS_TOKEN=<oauth2_access_token>
  LINKEDIN_PERSON_URN=<urn:li:person:ABC123>
  ```
- Token acquisition: `scripts/setup/linkedin_oauth2_setup.py` guides user through OAuth flow
- API endpoint: `POST https://api.linkedin.com/v2/ugcPosts`
- Error handling: Exponential backoff for 429 (rate limit), fail fast for 401 (expired token)
- **Note**: LinkedIn API has restrictive permissions - user must be approved for "Share on LinkedIn" permission

**References**:
- LinkedIn UGC Post API: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin
- OAuth 2.0 Setup: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication

---

## 5. Process Management for 24/7 Operation

### Decision: **PM2** (Primary) with **Custom watchdog.py** (Fallback)

**Rationale**:
- PM2 is battle-tested process manager (10M+ downloads/month on npm)
- Auto-restart on crash, log management, cluster mode, zero-downtime reloads
- Cross-platform (Windows, macOS, Linux)
- Simple config file (`ecosystem.config.js`) defines all processes
- Supports system startup integration (`pm2 startup`)

**Alternatives Considered**:
1. **Supervisor (Python)**
   - **Rejected**: Python-specific, less mature than PM2, Unix-only
   - **Why not chosen**: PM2 has broader community support and better Windows compatibility

2. **systemd (Linux-only)**
   - **Rejected**: Not cross-platform, complex service file syntax
   - **Why not chosen**: Windows/macOS users would need different solutions

3. **Docker Compose with restart policies**
   - **Rejected**: Adds containerization complexity, overkill for local-first project
   - **Why not chosen**: PM2 provides same restart behavior without Docker overhead

**Implementation Notes**:
- PM2 installation: `npm install -g pm2` (one-time global install)
- Configuration file: `ecosystem.config.js`
  ```javascript
  module.exports = {
    apps: [
      { name: "gmail-watcher", script: "uv", args: "run python -m my_ai_employee.watchers.gmail_watcher" },
      { name: "whatsapp-watcher", script: "uv", args: "run python -m my_ai_employee.watchers.whatsapp_watcher" },
      { name: "linkedin-watcher", script: "uv", args: "run python -m my_ai_employee.watchers.linkedin_watcher" },
      { name: "orchestrator", script: "uv", args: "run python -m my_ai_employee.orchestrator" }
    ]
  };
  ```
- Custom watchdog.py fallback:
  - Python script that spawns watcher subprocesses, monitors PIDs, restarts on crash
  - Used when PM2 is unavailable (e.g., restricted environments without Node.js)
- Health monitoring: PM2 built-in status dashboard (`pm2 status`, `pm2 logs`)

**References**:
- PM2 Documentation: https://pm2.keymetrics.io/docs/usage/quick-start/
- PM2 Ecosystem File: https://pm2.keymetrics.io/docs/usage/application-declaration/

---

## 6. Deduplication Strategy

### Decision: **SHA256 Content Hashing** with JSON State Files

**Rationale**:
- Prevents duplicate processing when same message arrives multiple times (e.g., email re-sync, WhatsApp reconnection)
- SHA256 hash of `(source_type + content + timestamp)` provides stable identifier
- Separate state files per watcher (`.gmail_dedupe.json`, `.whatsapp_dedupe.json`, `.linkedin_dedupe.json`)
- JSON format for easy inspection and manual cleanup if needed

**Alternatives Considered**:
1. **SQLite Database for Deduplication State**
   - **Rejected**: Adds dependency, overkill for simple key-value lookup
   - **Why not chosen**: JSON files are sufficient for 1000s of IDs, easier to debug

2. **In-Memory Set (No Persistence)**
   - **Rejected**: State lost on watcher restart, duplicates would reprocess
   - **Why not chosen**: Persistence is required for long-running watchers

3. **Redis for Distributed State**
   - **Rejected**: Requires Redis server, not local-first
   - **Why not chosen**: Silver tier is single-machine, no distributed requirements

**Implementation Notes**:
- File structure:
  ```json
  {
    "processed_ids": [
      "gmail_abc123_2026-01-18T10:00:00Z",
      "gmail_def456_2026-01-18T11:30:00Z"
    ]
  }
  ```
- Hash generation:
  ```python
  import hashlib
  source_id = hashlib.sha256(f"{source_type}_{content}_{timestamp}".encode()).hexdigest()[:16]
  ```
- Cleanup strategy: Rotate deduplication files monthly (keep last 30 days to handle delayed message arrivals)

**References**:
- Python hashlib: https://docs.python.org/3/library/hashlib.html

---

## 7. Credential Sanitization for Audit Logs

### Decision: **Regex-based Redaction** with Allowlist Patterns

**Rationale**:
- Audit logs must redact sensitive data before writing to `/Logs/YYYY-MM-DD.json`
- Regex patterns detect API keys, OAuth tokens, passwords, credit cards, emails
- Allowlist approach: Only explicitly safe fields (timestamps, status codes, sanitized subjects) pass through unmodified

**Patterns**:
| Data Type | Pattern | Replacement |
|-----------|---------|-------------|
| API Keys | `sk-[a-zA-Z0-9]{20,}` | `<REDACTED_API_KEY>` |
| OAuth Tokens | `ya29\.[a-zA-Z0-9\-_]+` | `<REDACTED_OAUTH_TOKEN>` |
| Passwords | `"password": ".*?"` | `"password": "<REDACTED>"` |
| Credit Cards | `\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}` | `<REDACTED_CC_LAST4:####>` |
| Emails (PII) | `([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})` | `<REDACTED_EMAIL>` (preserve domain for debugging) |

**Alternatives Considered**:
1. **Machine Learning-based PII Detection**
   - **Rejected**: Too complex, adds model dependencies, high false positive rate
   - **Why not chosen**: Regex patterns are deterministic and sufficient for known credential formats

2. **Scrubadub Library**
   - **Considered**: Python library for PII removal
   - **Why not chosen**: Overkill for our use case, regex gives more control over replacements

**Implementation Notes**:
- Sanitizer module: `src/my_ai_employee/utils/sanitizer.py`
- Applied to all MCP tool inputs/outputs before audit logging
- Unit tests verify no credential leakage in test logs

**References**:
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

---

## 8. Retry Logic for Transient Failures

### Decision: **Exponential Backoff** (1s, 2s, 4s) with Max 3 Retries

**Rationale**:
- External APIs (Gmail, LinkedIn) experience transient failures (network timeouts, rate limits, temporary outages)
- Exponential backoff prevents thundering herd problem (multiple retries hitting rate limit simultaneously)
- Max 3 retries balances recovery chances vs. execution latency
- Failed actions after retries moved to `/Failed/` for manual intervention

**Implementation**:
```python
import time

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise  # Max retries exceeded
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            logger.warning(f"Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
            time.sleep(wait_time)
```

**Alternatives Considered**:
1. **Linear Backoff (1s, 1s, 1s)**
   - **Rejected**: Doesn't reduce load on failing service, may hit rate limits repeatedly
   - **Why not chosen**: Exponential backoff is standard practice for API retries

2. **Jittered Exponential Backoff**
   - **Considered**: Add random jitter to prevent synchronized retries
   - **Why not chosen**: Silver tier is single-user, no distributed retry synchronization issues

**Failure Categories**:
- **Transient** (retry): Network timeout, 429 rate limit, 502/503/504 server errors
- **Permanent** (fail fast): 401 authentication, 404 not found, 400 bad request
- **Unknown** (retry once, then fail): Unexpected exceptions

**References**:
- Google Cloud Retry Strategy: https://cloud.google.com/storage/docs/retry-strategy

---

## 9. Configuration Management

### Decision: **python-dotenv** with Centralized `Config` Class

**Rationale**:
- All secrets in `.env` file (gitignored)
- Centralized validation on app startup (fail fast if required credentials missing)
- Type-safe access via dataclass properties

**Configuration Structure**:
```python
# .env
VAULT_ROOT=AI_Employee_Vault
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
LINKEDIN_ACCESS_TOKEN=xyz
DRY_RUN=false
LOG_LEVEL=INFO

# config.py
from dataclasses import dataclass
from dotenv import load_dotenv
import os

@dataclass
class Config:
    vault_root: str
    gmail_credentials: str
    gmail_token: str
    linkedin_token: str
    dry_run: bool
    log_level: str

    @classmethod
    def load(cls):
        load_dotenv()
        return cls(
            vault_root=os.getenv("VAULT_ROOT", "AI_Employee_Vault"),
            gmail_credentials=os.getenv("GMAIL_CREDENTIALS_FILE"),
            # ... validate required fields
        )
```

**Alternatives Considered**:
1. **Pydantic Settings**
   - **Considered**: More powerful validation, auto-type conversion
   - **Why not chosen**: python-dotenv + dataclass is simpler, avoids extra dependency

2. **YAML Config Files**
   - **Rejected**: Secrets would be in YAML file (must gitignore), less secure than .env
   - **Why not chosen**: .env is standard for credentials (Docker, 12-factor apps)

**References**:
- 12-Factor App Config: https://12factor.net/config
- python-dotenv: https://github.com/theskumar/python-dotenv

---

## 10. Heartbeat and Health Monitoring

### Decision: **60-Second Interval Logging** with PM2 Status Checks

**Rationale**:
- Each watcher/orchestrator logs heartbeat message every 60 seconds
- PM2 tracks process status (running/stopped/crashed)
- Gaps in heartbeat logs indicate downtime for investigation

**Heartbeat Format**:
```json
{
  "timestamp": "2026-01-22T10:00:00Z",
  "component": "gmail-watcher",
  "status": "running",
  "items_processed": 42,
  "uptime_seconds": 3600
}
```

**Monitoring Commands**:
```bash
pm2 status              # Show all process statuses
pm2 logs gmail-watcher  # Tail logs for specific watcher
pm2 monit               # Real-time dashboard
```

**Alternatives Considered**:
1. **Prometheus + Grafana Metrics**
   - **Rejected**: Too complex for Silver tier, requires separate services
   - **Why not chosen**: PM2 built-in monitoring is sufficient for single-user deployment

2. **Healthcheck HTTP Endpoints**
   - **Rejected**: Watchers are background processes, no HTTP server needed
   - **Why not chosen**: Log-based heartbeats are simpler

**References**:
- PM2 Monitoring: https://pm2.keymetrics.io/docs/usage/monitoring/

---

## Summary Table

| Decision Area | Chosen Technology | Key Reason |
|---------------|-------------------|------------|
| MCP Framework | FastMCP (Pydantic v2) | Official framework, type-safe tools, minimal boilerplate |
| Browser Automation | Playwright (Async Python) | WhatsApp has no API, Playwright has persistent sessions |
| Gmail Integration | Google API Python Client (OAuth 2.0) | Official library, auto token refresh, free |
| LinkedIn Integration | LinkedIn REST API v2 | Official API, reliable, no CAPTCHA risks |
| Process Management | PM2 (Node.js) | Battle-tested, cross-platform, auto-restart |
| Deduplication | SHA256 hashing + JSON files | Simple, inspectable, sufficient for single-machine |
| Credential Sanitization | Regex-based redaction | Deterministic, testable, OWASP-compliant |
| Retry Logic | Exponential backoff (1s, 2s, 4s) | Industry standard, prevents thundering herd |
| Configuration | python-dotenv + Config dataclass | Secure, type-safe, 12-factor compliant |
| Health Monitoring | 60s heartbeat logs + PM2 status | Simple, built-in PM2 dashboard, log-based |

---

## Next Steps (Phase 1)

1. Create `data-model.md` - Schema definitions for Action Item, Approval Request, Audit Log Entry
2. Create `contracts/` - OpenAPI specs for email, LinkedIn, browser MCP servers
3. Create `quickstart.md` - Setup guide for OAuth, .env configuration, PM2 deployment
4. Update agent context - Add new technologies to `.specify/context/claude-context.md`

