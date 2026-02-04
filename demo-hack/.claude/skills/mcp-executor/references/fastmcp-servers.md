# FastMCP Servers Implementation Guide

## Email MCP Server (`mcp_servers/email_mcp.py`)

Sends emails via Gmail API or SMTP (configurable). Supports both backends with automatic selection.

### Backends

**Gmail API (Default - Secure OAuth 2.0)**
- Secure OAuth 2.0 authentication
- Works with Gmail accounts
- Recommended for security
- Set: `EMAIL_BACKEND=gmail` in .env

**SMTP (Universal - TLS Encryption)**
- Works with ANY email provider (Gmail, Outlook, custom SMTP)
- SMTP with TLS encryption
- Username/password authentication
- Set: `EMAIL_BACKEND=smtp` in .env

### Tools

#### `send_email`

```python
@mcp.tool
def send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> dict:
    """Send email via configured backend (Gmail API or SMTP).

    Automatically selects backend based on EMAIL_BACKEND environment variable:
    - EMAIL_BACKEND=gmail (default): Uses Gmail API with OAuth 2.0
    - EMAIL_BACKEND=smtp: Uses SMTP with TLS encryption

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body (plain text or HTML)
        cc: Comma-separated CC addresses (optional)
        bcc: Comma-separated BCC addresses (optional)

    Returns:
        {
            'success': True/False,
            'message_id': 'Unique message ID',
            'timestamp': '2026-01-14T14:30:00Z',
            'backend_used': 'gmail' or 'smtp',
            'error': 'error message if failed (None if successful)'
        }
    """
```

### Pydantic Models (Type-Safe Validation)

```python
from pydantic import BaseModel, Field, field_validator

class EmailRequest(BaseModel):
    """Email request with validation."""
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body (HTML or plain text)")
    cc: str = Field(default="", description="Comma-separated CC addresses")
    bcc: str = Field(default="", description="Comma-separated BCC addresses")

    @field_validator('to')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email address')
        return v

class EmailResponse(BaseModel):
    """Email response."""
    success: bool
    message_id: str
    timestamp: str
    backend_used: str  # 'gmail' or 'smtp'
    error: str | None = None
```

### Backend Implementation Pattern

#### Gmail Backend (OAuth 2.0)

```python
class GmailBackend(EmailBackend):
    """Send emails via Gmail API with OAuth 2.0."""

    def __init__(self):
        # Initializes Gmail service with credentials
        # Handles token refresh automatically
        # Raises error if credentials missing

    def send(self, request: EmailRequest) -> EmailResponse:
        # Build MIME message with CC/BCC support
        # Send via Gmail API
        # Return result with message ID

    def validate_config(self) -> tuple[bool, str]:
        # Check if credentials.json exists
        # Returns (is_valid, error_message)
```

**Configuration**:
```bash
EMAIL_BACKEND=gmail
GMAIL_TOKEN_FILE=token.json
GMAIL_CREDENTIALS_FILE=credentials.json
```

#### SMTP Backend (TLS - Universal)

```python
class SMTPBackend(EmailBackend):
    """Send emails via SMTP with TLS encryption."""

    def __init__(self):
        # Load SMTP configuration from environment
        # Validates all required settings

    def send(self, request: EmailRequest) -> EmailResponse:
        # Create MIME message with CC/BCC support
        # Connect to SMTP server with TLS
        # Login and send email
        # Handle SMTP errors (auth, connection, etc.)
        # Return result with message ID

    def validate_config(self) -> tuple[bool, str]:
        # Check SMTP_HOST, SMTP_PORT, credentials
        # Returns (is_valid, error_message)
```

**Configuration**:
```bash
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.gmail.com          # or smtp.office365.com, mail.example.com, etc.
SMTP_PORT=587                      # 587 for TLS, 465 for SSL
SMTP_USERNAME=user@gmail.com       # Email address
SMTP_PASSWORD=app-specific-pwd     # Password or app-specific password
SMTP_FROM_ADDRESS=user@gmail.com   # From address (defaults to USERNAME)
```

### Backend Factory Pattern

```python
def get_email_backend() -> EmailBackend:
    """
    Factory function to get configured backend.

    Reads EMAIL_BACKEND from .env:
    - 'gmail' (default) → GmailBackend()
    - 'smtp' → SMTPBackend()

    Validates configuration before returning.
    Raises RuntimeError if configuration invalid.
    """
    backend_name = os.getenv('EMAIL_BACKEND', 'gmail').lower()

    if backend_name == 'gmail':
        backend = GmailBackend()
    elif backend_name == 'smtp':
        backend = SMTPBackend()
    else:
        raise ValueError(f"Unknown EMAIL_BACKEND: {backend_name}")

    is_valid, error = backend.validate_config()
    if not is_valid:
        raise RuntimeError(f"Configuration error: {error}")

    return backend
```

### Usage Examples

**Send via Gmail API (Default)**:
```python
# .env: EMAIL_BACKEND=gmail
result = send_email(
    to="client@example.com",
    subject="Project Update",
    body="Here's your project status..."
)
# Returns: {'success': True, 'message_id': 'abc123', 'backend_used': 'gmail', ...}
```

**Send via SMTP (Outlook)**:
```python
# .env settings:
# EMAIL_BACKEND=smtp
# SMTP_HOST=smtp.office365.com
# SMTP_PORT=587
# SMTP_USERNAME=user@outlook.com
# SMTP_PASSWORD=your-app-password

result = send_email(
    to="client@example.com",
    subject="Project Update",
    body="Here's your project status...",
    cc="manager@example.com"
)
# Returns: {'success': True, 'message_id': 'smtp-2026-01-14...', 'backend_used': 'smtp', ...}
```

**Send via SMTP (Custom Server)**:
```python
# .env settings:
# EMAIL_BACKEND=smtp
# SMTP_HOST=mail.company.com
# SMTP_PORT=587
# SMTP_USERNAME=user@company.com
# SMTP_PASSWORD=company-password
# SMTP_FROM_ADDRESS=notifications@company.com

result = send_email(
    to="contact@client.com",
    subject="Notification",
    body="Important notification...",
    bcc="admin@company.com"
)
# Returns: {'success': True, 'message_id': 'smtp-...', 'backend_used': 'smtp', ...}
```

### Common SMTP Providers

| Provider | Host | Port | Username | Password |
|----------|------|------|----------|----------|
| Gmail | smtp.gmail.com | 587 | your@gmail.com | App-specific password* |
| Outlook | smtp.office365.com | 587 | your@outlook.com | Your password |
| Yahoo | smtp.mail.yahoo.com | 587 | your@yahoo.com | App password** |
| AWS SES | email-smtp.region.amazonaws.com | 587 | SMTP username | SMTP password |
| Custom | mail.example.com | 587 | user@example.com | Password |

*Gmail: Generate at https://myaccount.google.com/apppasswords
**Yahoo: Generate at https://login.yahoo.com/account/security

### Error Handling

**Gmail Backend Errors**:
- `FileNotFoundError`: credentials.json not found
- `RefreshError`: Token refresh failed (perform new OAuth)
- `BuildError`: Gmail API service initialization failed

**SMTP Backend Errors**:
- `SMTPAuthenticationError`: Wrong username/password
- `SMTPServerDisconnected`: Connection to server failed
- `SMTPException`: SMTP protocol error
- `TimeoutError`: Connection timeout (increase timeout or check network)

---

## LinkedIn MCP Server (`mcp_servers/linkedin_mcp.py`)

Posts content to LinkedIn, integrated with approval workflow.

### Tools

#### `create_post`

```python
@mcp.tool
def create_post(text: str, hashtags: str = "") -> dict:
    """Create and publish LinkedIn post.

    Args:
        text: Post content (up to 3000 characters)
        hashtags: Comma-separated hashtags (optional)

    Returns:
        {
            'success': True/False,
            'post_id': '...',
            'post_url': 'https://linkedin.com/feed/update/...',
            'timestamp': '2026-01-14T14:30:00Z',
            'error': 'error message if failed'
        }
    """
```

### Implementation Pattern

```python
from fastmcp import FastMCP
import os
import requests
from datetime import datetime

mcp = FastMCP(name="LinkedIn MCP Server")

@mcp.tool
def create_post(text: str, hashtags: str = "") -> dict:
    """Create LinkedIn post."""
    try:
        token = os.getenv('LINKEDIN_ACCESS_TOKEN')

        # LinkedIn v2 API endpoint
        url = 'https://api.linkedin.com/v2/ugcPosts'

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'LinkedIn-Version': '202601'
        }

        # Build post payload
        payload = {
            'author': 'urn:li:person:YOUR_PERSON_ID',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.PublishedContent': {
                    'shareMediaCategory': 'ARTICLE',
                    'shareCommentary': {
                        'text': f"{text}\n\n{hashtags}"
                    },
                    'media': []
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }

        # Post to LinkedIn
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            post_id = response.headers.get('X-RestLi-Id')
            return {
                'success': True,
                'post_id': post_id,
                'post_url': f'https://linkedin.com/feed/update/{post_id}',
                'timestamp': datetime.now().isoformat(),
            }
        else:
            return {
                'success': False,
                'error': f"LinkedIn API error: {response.status_code}",
                'timestamp': datetime.now().isoformat(),
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
        }

if __name__ == '__main__':
    mcp.run()
```

---

## Browser Automation MCP Server (`mcp_servers/browser_mcp.py`)

Automate browser interactions using Playwright, integrated with approval workflow.

### Tools

#### `navigate_to`

```python
@mcp.tool
def navigate_to(url: str) -> dict:
    """Navigate to URL in browser.

    Args:
        url: Target URL

    Returns:
        {'success': True/False, 'title': page_title, 'url': current_url}
    """
```

#### `fill_form`

```python
@mcp.tool
def fill_form(selector: str, value: str) -> dict:
    """Fill form field using CSS selector.

    Args:
        selector: CSS selector for input field
        value: Value to enter

    Returns:
        {'success': True/False, 'field': selector, 'value': value}
    """
```

#### `click_button`

```python
@mcp.tool
def click_button(selector: str) -> dict:
    """Click button or element.

    Args:
        selector: CSS selector for button

    Returns:
        {'success': True/False, 'element': selector}
    """
```

#### `extract_text`

```python
@mcp.tool
def extract_text(selector: str = "body") -> dict:
    """Extract text from page element.

    Args:
        selector: CSS selector (default: entire page)

    Returns:
        {'success': True/False, 'text': extracted_text}
    """
```

### Implementation Pattern

```python
from fastmcp import FastMCP
from playwright.async_api import async_playwright
import asyncio
from datetime import datetime

mcp = FastMCP(name="Browser Automation MCP Server")

class BrowserManager:
    def __init__(self):
        self.browser = None
        self.page = None

    async def init(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch()
        self.page = await self.browser.new_page()

    async def close(self):
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()

browser_mgr = BrowserManager()

@mcp.tool
def navigate_to(url: str) -> dict:
    """Navigate to URL."""
    try:
        async def _nav():
            if not browser_mgr.page:
                await browser_mgr.init()
            await browser_mgr.page.goto(url, wait_until='networkidle')
            title = await browser_mgr.page.title()
            return {'success': True, 'title': title, 'url': url}

        result = asyncio.run(_nav())
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}

@mcp.tool
def fill_form(selector: str, value: str) -> dict:
    """Fill form field."""
    try:
        async def _fill():
            if not browser_mgr.page:
                await browser_mgr.init()
            await browser_mgr.page.fill(selector, value)
            return {'success': True, 'field': selector, 'value': value}

        result = asyncio.run(_fill())
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}

@mcp.tool
def click_button(selector: str) -> dict:
    """Click button."""
    try:
        async def _click():
            if not browser_mgr.page:
                await browser_mgr.init()
            await browser_mgr.page.click(selector)
            return {'success': True, 'element': selector}

        result = asyncio.run(_click())
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}

@mcp.tool
def extract_text(selector: str = "body") -> dict:
    """Extract text from page."""
    try:
        async def _extract():
            if not browser_mgr.page:
                await browser_mgr.init()
            text = await browser_mgr.page.text_content(selector)
            return {'success': True, 'text': text}

        result = asyncio.run(_extract())
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    mcp.run()
```

---

## Starting MCP Servers

### Single Server (Development)

```bash
# Start email server
python mcp_servers/email_mcp.py

# In another terminal, start LinkedIn server
python mcp_servers/linkedin_mcp.py

# In another terminal, start browser server
python mcp_servers/browser_mcp.py
```

### All Servers (Production)

```bash
# Start all MCP servers
python scripts/start_all_servers.py

# Or with PM2
pm2 start mcp_servers/email_mcp.py --name "email-mcp"
pm2 start mcp_servers/linkedin_mcp.py --name "linkedin-mcp"
pm2 start mcp_servers/browser_mcp.py --name "browser-mcp"
```

---

## Creating Custom MCP Servers

Use this template for new MCP servers:

```python
from fastmcp import FastMCP
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
mcp = FastMCP(name="Custom MCP Server")

# Add tools
@mcp.tool
def tool_name(param1: str, param2: int) -> dict:
    """Tool description.

    Args:
        param1: Parameter description
        param2: Parameter description

    Returns:
        dict: Result with success status
    """
    try:
        # Implementation
        result = do_something(param1, param2)
        return {
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'success': False,
            'error': str(e),
        }

# Add static resources
@mcp.resource("config://server")
def get_config() -> dict:
    """Get server configuration."""
    return {
        'version': '1.0',
        'capabilities': ['tool_name'],
    }

# Add dynamic resources (templates)
@mcp.resource("results://{request_id}")
def get_result(request_id: str) -> dict:
    """Get result for request ID."""
    # Fetch from database or cache
    return {'request_id': request_id, 'result': '...'}

if __name__ == '__main__':
    mcp.run()
```

---

## Error Handling in MCP Servers

All MCP server tools should return structured error responses:

```python
{
    'success': False,
    'error': 'Human-readable error message',
    'error_type': 'authentication|network|validation|system',
    'timestamp': '2026-01-14T14:30:00Z',
    'retry_after': 60  # Optional: seconds to wait before retry
}
```

Success responses:

```python
{
    'success': True,
    'data': {...},  # The actual result
    'timestamp': '2026-01-14T14:30:00Z',
}
```

---
