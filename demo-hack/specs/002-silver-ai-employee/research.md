# Technology Research: Silver Tier AI Employee

**Date**: 2026-01-15
**Feature**: Silver Tier AI Employee
**Research Method**: Context7 MCP queries + HACKATHON-ZERO.md analysis

## Overview

This document consolidates technology research for Silver Tier implementation, covering FastMCP for MCP servers, Playwright for browser automation, Gmail API for email integration, and LinkedIn API for social media posting.

---

## 1. FastMCP (MCP Server Framework)

### Decision: Use FastMCP for all MCP servers

**Library**: `/jlowin/fastmcp` (Context7 ID)
**Version**: Latest stable (check PyPI)
**Source Reputation**: High
**Benchmark Score**: 78

### Rationale

1. **Pythonic Framework**: Native Python with Pydantic v2 validation
2. **Tool & Resource Support**: Decorator-based tool registration, static and dynamic resources
3. **Built-in Features**: Authentication, deployment, progress tracking, structured output
4. **Production Ready**: Used in production environments, well-documented

### Key Features for Silver Tier

```python
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field
from typing import Annotated

# Server initialization
mcp = FastMCP(name="email-mcp")

# Tool with Pydantic validation
@mcp.tool
async def send_email(
    to: Annotated[str, Field(description="Recipient email address")],
    subject: Annotated[str, Field(description="Email subject line")],
    body: Annotated[str, Field(description="Email body content")],
    ctx: Context
) -> dict:
    """Send email via Gmail API with audit logging."""
    await ctx.info(f"Sending email to {to}")
    # Implementation...
    return {"status": "sent", "message_id": "..."}

# Resource for configuration
@mcp.resource("config://email")
def get_email_config() -> dict:
    """Email server configuration."""
    return {"smtp_host": "smtp.gmail.com", "port": 587}

# Run server
if __name__ == "__main__":
    mcp.run()
```

### Testing Strategy

```python
import pytest
from mcp.client import ClientSession, StdioServerParameters

@pytest.fixture
async def mcp_client():
    """Fixture to create MCP client."""
    server_params = StdioServerParameters(
        command="python",
        args=["email_mcp.py"],
        env={"DRY_RUN": "true"}
    )
    async with ClientSession(server_params) as session:
        await session.initialize()
        yield session

@pytest.mark.asyncio
async def test_send_email(mcp_client):
    """Test email sending tool."""
    result = await mcp_client.call_tool(
        "send_email",
        arguments={
            "to": "test@example.com",
            "subject": "Test",
            "body": "Test email"
        }
    )
    assert "sent" in result.content[0].text
```

### Alternatives Considered

- **Raw MCP SDK**: More control but requires more boilerplate
- **Custom implementation**: Reinventing the wheel, not recommended

**Decision**: FastMCP provides the right balance of simplicity and power for our use case.

---

## 2. Playwright (Browser Automation)

### Decision: Use Playwright Python for WhatsApp Web and browser automation

**Library**: `/microsoft/playwright-python` (Context7 ID)
**Version**: Latest stable (check PyPI)
**Source Reputation**: High
**Benchmark Score**: 89.9

### Rationale

1. **Cross-Browser Support**: Chromium, Firefox, WebKit
2. **Session Persistence**: Save/load authentication state
3. **Reliable Automation**: Auto-wait, retry logic built-in
4. **Python Native**: Async/sync APIs, type hints

### Key Features for Silver Tier

#### WhatsApp Web Session Management

```python
from playwright.sync_api import sync_playwright

def whatsapp_watcher():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Headless=False for QR code

        # Load saved session if exists
        context = browser.new_context(
            storage_state='whatsapp_session.json' if os.path.exists('whatsapp_session.json') else None
        )

        page = context.new_page()
        page.goto('https://web.whatsapp.com')

        # Wait for QR code or chat list
        try:
            page.wait_for_selector('div[data-testid="chat-list"]', timeout=60000)
            # Save session for next time
            context.storage_state(path='whatsapp_session.json')
        except TimeoutError:
            print("QR code scan required")
            return

        # Monitor for new messages
        while True:
            messages = page.locator('.message-in').all()
            for msg in messages:
                text = msg.text_content()
                if any(keyword in text.lower() for keyword in ['urgent', 'help', 'asap']):
                    # Create action item
                    create_action_item(text)
            time.sleep(30)
```

#### Form Filling and Payments

```python
async def fill_payment_form(url: str, amount: float, vendor: str):
    """Fill payment form with Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url)
        await page.fill('input[name="amount"]', str(amount))
        await page.fill('input[name="vendor"]', vendor)

        # Take screenshot before submission
        await page.screenshot(path='payment_preview.png')

        # Click submit (only if not DRY_RUN)
        if not os.getenv('DRY_RUN'):
            await page.click('button[type="submit"]')
            await page.wait_for_url('**/confirmation')

        await browser.close()
```

### Session Persistence Pattern

```python
# Save authentication state
context.storage_state(path='auth.json')

# Load authentication state in new context
context = browser.new_context(storage_state='auth.json')
```

### Alternatives Considered

- **Selenium**: Older, less reliable, more verbose
- **Puppeteer**: Node.js only, not Python-native

**Decision**: Playwright is the modern standard for browser automation with excellent Python support.

---

## 3. Gmail API (Email Integration)

### Decision: Use Gmail API with OAuth 2.0 for email monitoring and sending

**Library**: `/websites/developers_google_workspace_gmail_api` (Context7 ID)
**Python Client**: `google-api-python-client`, `google-auth-oauthlib`
**Source Reputation**: High
**Benchmark Score**: 80

### Rationale

1. **Official Google API**: Well-maintained, reliable
2. **OAuth 2.0 Support**: Secure authentication
3. **Push Notifications**: Gmail watch API for real-time updates
4. **Comprehensive Features**: Read, send, search, labels

### Key Features for Silver Tier

#### OAuth 2.0 Authentication

```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_gmail_service():
    """Get authenticated Gmail service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)
```

#### List and Monitor Messages

```python
def list_new_messages(service):
    """List new messages from inbox."""
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        maxResults=10
    ).execute()

    messages = results.get('messages', [])
    for message in messages:
        msg = service.users().messages().get(
            userId='me',
            id=message['id']
        ).execute()

        # Extract headers
        headers = msg['payload']['headers']
        subject = next(h['value'] for h in headers if h['name'] == 'Subject')
        sender = next(h['value'] for h in headers if h['name'] == 'From')

        # Create action item
        create_action_item(subject, sender, msg['snippet'])
```

#### Send Email

```python
import base64
from email.message import EmailMessage

def send_email(service, to: str, subject: str, body: str):
    """Send email via Gmail API."""
    message = EmailMessage()
    message.set_content(body)
    message['To'] = to
    message['From'] = 'me'
    message['Subject'] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}

    send_message = service.users().messages().send(
        userId='me',
        body=create_message
    ).execute()

    return send_message['id']
```

#### Gmail Watch API (Push Notifications)

```python
def setup_gmail_watch(service, topic_name: str):
    """Set up push notifications for Gmail."""
    request = {
        'labelIds': ['INBOX'],
        'topicName': topic_name,  # Google Cloud Pub/Sub topic
        'labelFilterBehavior': 'INCLUDE'
    }

    response = service.users().watch(userId='me', body=request).execute()
    return response  # Contains historyId and expiration
```

### SMTP Fallback Strategy

```python
import smtplib
from email.mime.text import MIMEText

def send_email_smtp(to: str, subject: str, body: str):
    """Fallback to SMTP if Gmail API fails."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('SMTP_FROM')
    msg['To'] = to

    with smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT'))) as server:
        server.starttls()
        server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
        server.send_message(msg)
```

### Alternatives Considered

- **IMAP/SMTP only**: Less reliable, no push notifications
- **Third-party email services**: Adds dependency, less control

**Decision**: Gmail API primary with SMTP fallback provides best reliability.

---

## 4. LinkedIn API (Social Media Integration)

### Decision: Use LinkedIn API with Playwright fallback

**Library**: `/websites/learn_microsoft_en-us_linkedin` (Context7 ID)
**Python Client**: `linkedin-api-python-client` (official)
**Source Reputation**: High
**Benchmark Score**: 59.1

### Rationale

1. **Official API**: Supported by Microsoft/LinkedIn
2. **Marketing API**: Post creation, company pages
3. **OAuth 2.0**: Secure authentication
4. **Fallback Option**: Playwright for unsupported features

### Key Features for Silver Tier

#### LinkedIn API Post Creation

```python
from linkedin_api import Linkedin

def create_linkedin_post(api: Linkedin, text: str, hashtags: list):
    """Create LinkedIn post via API."""
    post_content = f"{text}\n\n{' '.join(hashtags)}"

    response = api.post_update(
        text=post_content,
        visibility='PUBLIC'
    )

    return response['updateKey']
```

#### Playwright Fallback (if API unavailable)

```python
async def create_linkedin_post_playwright(text: str, hashtags: list):
    """Create LinkedIn post via Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(storage_state='linkedin_session.json')
        page = await context.new_page()

        await page.goto('https://www.linkedin.com')
        await page.click('button[aria-label="Start a post"]')
        await page.fill('div[role="textbox"]', f"{text}\n\n{' '.join(hashtags)}")

        if not os.getenv('DRY_RUN'):
            await page.click('button[data-test-id="share-box-post-button"]')

        await browser.close()
```

### Alternatives Considered

- **Playwright only**: Works but less reliable, no API rate limits
- **Third-party services**: Buffer, Hootsuite (adds cost and complexity)

**Decision**: LinkedIn API primary with Playwright fallback for flexibility.

---

## 5. Process Management (PM2)

### Decision: Use PM2 for process management

**Tool**: PM2 (Node.js process manager)
**Recommendation Source**: HACKATHON-ZERO.md Lines 1297-1315

### Rationale

1. **Auto-Restart**: Automatically restarts crashed processes
2. **Log Management**: Centralized logging
3. **Startup Persistence**: Survives system reboots
4. **Monitoring**: Built-in status dashboard

### Configuration (ecosystem.config.js)

```javascript
module.exports = {
  apps: [
    {
      name: 'gmail-watcher',
      script: 'python',
      args: 'My_AI_Employee/watchers/gmail_watcher.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: 'logs/gmail-watcher-error.log',
      out_file: 'logs/gmail-watcher-out.log'
    },
    {
      name: 'whatsapp-watcher',
      script: 'python',
      args: 'My_AI_Employee/watchers/whatsapp_watcher.py',
      interpreter: 'none',
      autorestart: true,
      watch: false
    },
    {
      name: 'linkedin-watcher',
      script: 'python',
      args: 'My_AI_Employee/watchers/linkedin_watcher.py',
      interpreter: 'none',
      autorestart: true,
      watch: false
    },
    {
      name: 'orchestrator',
      script: 'python',
      args: 'My_AI_Employee/orchestrator.py',
      interpreter: 'none',
      autorestart: true,
      watch: false
    }
  ]
};
```

### Usage

```bash
# Install PM2
npm install -g pm2

# Start all processes
pm2 start ecosystem.config.js

# Monitor status
pm2 status
pm2 logs

# Save configuration for startup
pm2 save
pm2 startup
```

### Alternative: Unified Watcher Runner

```python
# run_watcher.py (unified approach - CHOSEN IMPLEMENTATION)
# Supports running individual watchers or all watchers with orchestration

# Usage:
# python run_watcher.py --watcher gmail
# python run_watcher.py --watcher all

import argparse
import logging
import threading
from pathlib import Path

WATCHERS = {
    'filesystem': 'watchers.filesystem_watcher.FilesystemWatcher',
    'gmail': 'watchers.gmail_watcher.GmailWatcher',
    'whatsapp': 'watchers.whatsapp_watcher.WhatsAppWatcher',
    'linkedin': 'watchers.linkedin_watcher.LinkedInWatcher'
}

def run_watcher(watcher_name):
    """Run a single watcher in a thread."""
    # Import and instantiate watcher
    # Run watcher.run() in thread
    pass

def run_all_watchers():
    """Run all watchers with orchestration."""
    threads = []
    for name in ['gmail', 'linkedin', 'whatsapp']:
        thread = threading.Thread(target=run_watcher, args=(name,))
        thread.start()
        threads.append(thread)

    # Monitor health and restart on crash
    for thread in threads:
        thread.join()
```

**Decision**: PM2 recommended for production, unified run_watcher.py for development/testing.

---

## 6. Dependency Summary

### Python Dependencies (pyproject.toml)

```toml
[project]
name = "silver-tier-ai-employee"
version = "2.0.0"
requires-python = ">=3.13"

dependencies = [
    # Bronze tier (already installed)
    "watchdog>=4.0.0",
    "python-frontmatter>=1.1.0",

    # Silver tier - MCP servers
    "fastmcp>=0.1.0",

    # Silver tier - Browser automation
    "playwright>=1.40.0",

    # Silver tier - Gmail API
    "google-api-python-client>=2.100.0",
    "google-auth-oauthlib>=1.1.0",
    "google-auth-httplib2>=0.1.1",

    # Silver tier - LinkedIn API
    "linkedin-api-python-client>=0.1.0",

    # Testing
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
]
```

### System Dependencies

- **Node.js**: For PM2 process management
- **Chromium**: For Playwright browser automation (auto-installed by Playwright)

---

## 7. Security & Compliance

### Credential Storage

- **Location**: `.env` file (gitignored)
- **OAuth Tokens**: OS-specific secure storage (keyring)
- **Never**: Commit credentials to git or store in vault

### Audit Log Sanitization

```python
def sanitize_credentials(data: dict) -> dict:
    """Sanitize sensitive data for audit logs."""
    sanitized = data.copy()

    # API keys: show first 4 chars
    if 'api_key' in sanitized:
        sanitized['api_key'] = sanitized['api_key'][:4] + '***'

    # Passwords: redact entirely
    if 'password' in sanitized:
        sanitized['password'] = '[REDACTED]'

    # Credit cards: show last 4 digits
    if 'credit_card' in sanitized:
        sanitized['credit_card'] = '****' + sanitized['credit_card'][-4:]

    # PII: truncate emails
    if 'email' in sanitized:
        user, domain = sanitized['email'].split('@')
        sanitized['email'] = f"{user}@*****.{domain.split('.')[-1]}"

    return sanitized
```

---

## 8. Testing Strategy

### Unit Tests

- **Watchers**: Mock API responses, test action item creation
- **MCP Servers**: Test tool execution with DRY_RUN=true
- **Orchestrator**: Test routing logic, retry logic

### Integration Tests

- **Approval Workflow**: End-to-end from Needs_Action to Done
- **Credential Sanitization**: Verify audit logs don't contain secrets
- **Graceful Degradation**: Test offline scenarios

### E2E Tests

- **User Story 1 (P1)**: Client email response workflow
- **User Story 2 (P2)**: LinkedIn post creation workflow
- **User Story 3 (P3)**: WhatsApp message response workflow

---

## Conclusion

All technology choices align with:
- ✅ Constitution v2.0.0 principles
- ✅ HACKATHON-ZERO.md architecture (Lines 1200-1250)
- ✅ Production-ready libraries with high reputation
- ✅ Security and audit logging requirements
- ✅ Graceful degradation and error recovery

**Ready for Phase 1: Design Artifacts**
