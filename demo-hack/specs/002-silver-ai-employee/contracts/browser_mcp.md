# Browser Automation MCP Server Contract

**Server Name**: `browser-mcp`
**Purpose**: Automate browser interactions for WhatsApp Web, payments, and form filling
**Technology**: FastMCP + Playwright
**Location**: `My_AI_Employee/mcp_servers/browser_mcp.py`

---

## Overview

The Browser Automation MCP Server provides tools for interacting with web applications that don't have APIs, including WhatsApp Web, payment portals, and form submissions. It uses Playwright for reliable browser automation with session persistence.

---

## Tools

### 1. navigate_to

**Description**: Navigate to a URL and wait for page load

**Input Schema**:
```python
{
    "url": str,          # URL to navigate to (required)
    "wait_until": str,   # "load" | "domcontentloaded" | "networkidle" (optional, default: "load")
    "timeout": int       # Timeout in milliseconds (optional, default: 30000)
}
```

**Output Schema**:
```python
{
    "status": "success" | "failed",
    "url": str,          # Final URL after navigation
    "title": str,        # Page title
    "loaded_at": str,    # ISO8601 timestamp
    "error": str | null
}
```

**Example Usage**:
```python
result = await ctx.call_tool(
    "navigate_to",
    arguments={
        "url": "https://web.whatsapp.com",
        "wait_until": "networkidle"
    }
)
```

---

### 2. fill_form

**Description**: Fill out a form with provided data

**Input Schema**:
```python
{
    "fields": dict,      # Field selector -> value mapping (required)
    "submit": bool,      # Whether to submit form (optional, default: false)
    "screenshot": bool,  # Take screenshot before submit (optional, default: true)
    "dry_run": bool      # Don't actually submit (optional, default: false)
}
```

**Output Schema**:
```python
{
    "status": "filled" | "submitted" | "failed",
    "fields_filled": int,
    "screenshot_path": str | null,
    "submitted_at": str | null,
    "error": str | null
}
```

**Validation Rules**:
- `fields` MUST be non-empty dictionary
- Keys MUST be valid CSS selectors
- If `submit` is true and `dry_run` is false, form will be submitted
- Screenshot always taken before submission for audit trail

**Example Usage**:
```python
result = await ctx.call_tool(
    "fill_form",
    arguments={
        "fields": {
            "input[name='amount']": "500.00",
            "input[name='vendor']": "Tech Solutions Inc",
            "input[name='reference']": "Invoice #1234"
        },
        "submit": False,  # Don't submit yet, wait for approval
        "screenshot": True,
        "dry_run": False
    }
)
```

---

### 3. click_element

**Description**: Click an element on the page

**Input Schema**:
```python
{
    "selector": str,     # CSS selector or text selector (required)
    "wait_for": str,     # Selector to wait for after click (optional)
    "timeout": int,      # Timeout in milliseconds (optional, default: 30000)
    "dry_run": bool      # Don't actually click (optional, default: false)
}
```

**Output Schema**:
```python
{
    "status": "clicked" | "failed",
    "selector": str,
    "clicked_at": str,   # ISO8601 timestamp
    "error": str | null
}
```

**Example Usage**:
```python
result = await ctx.call_tool(
    "click_element",
    arguments={
        "selector": "button[type='submit']",
        "wait_for": "div.confirmation",
        "dry_run": False
    }
)
```

---

### 4. send_whatsapp_message

**Description**: Send a WhatsApp message via WhatsApp Web

**Input Schema**:
```python
{
    "contact": str,      # Contact name or phone number (required)
    "message": str,      # Message text (required)
    "dry_run": bool      # Don't actually send (optional, default: false)
}
```

**Output Schema**:
```python
{
    "status": "sent" | "queued" | "failed",
    "contact": str,
    "message_preview": str,  # First 50 chars
    "sent_at": str | null,
    "error": str | null
}
```

**Validation Rules**:
- `contact` MUST be non-empty string
- `message` MUST be non-empty string
- Requires active WhatsApp Web session
- If session expired, returns error with instructions to re-scan QR code

**Example Usage**:
```python
result = await ctx.call_tool(
    "send_whatsapp_message",
    arguments={
        "contact": "Client A",
        "message": "Your invoice has been processed. Thank you!",
        "dry_run": False
    }
)
```

---

### 5. extract_text

**Description**: Extract text content from page elements

**Input Schema**:
```python
{
    "selector": str,     # CSS selector (required)
    "all": bool          # Extract all matching elements (optional, default: false)
}
```

**Output Schema**:
```python
{
    "status": "success" | "failed",
    "text": str | list[str],  # Single string or list if all=true
    "count": int,        # Number of elements found
    "error": str | null
}
```

**Example Usage**:
```python
result = await ctx.call_tool(
    "extract_text",
    arguments={
        "selector": "div.confirmation-number",
        "all": False
    }
)
```

---

### 6. take_screenshot

**Description**: Take a screenshot of the current page

**Input Schema**:
```python
{
    "path": str,         # File path to save screenshot (required)
    "full_page": bool,   # Capture full page (optional, default: false)
    "selector": str      # Capture specific element (optional)
}
```

**Output Schema**:
```python
{
    "status": "success" | "failed",
    "path": str,
    "size_bytes": int,
    "captured_at": str,  # ISO8601 timestamp
    "error": str | null
}
```

**Example Usage**:
```python
result = await ctx.call_tool(
    "take_screenshot",
    arguments={
        "path": "screenshots/payment_confirmation.png",
        "full_page": False
    }
)
```

---

## Resources

### 1. browser://config

**Description**: Browser automation configuration

**URI**: `browser://config`

**Content Type**: `application/json`

**Schema**:
```json
{
    "playwright": {
        "browser": "chromium",
        "headless": false,
        "viewport": {
            "width": 1280,
            "height": 720
        },
        "user_agent": "Mozilla/5.0...",
        "timeout": 30000
    },
    "sessions": {
        "whatsapp": {
            "enabled": true,
            "session_file": "whatsapp_session.json",
            "qr_code_timeout": 60000
        },
        "payment_portal": {
            "enabled": true,
            "session_file": "payment_session.json"
        }
    },
    "screenshots": {
        "enabled": true,
        "directory": "screenshots/",
        "format": "png",
        "quality": 90
    }
}
```

---

### 2. browser://sessions

**Description**: Active browser sessions

**URI**: `browser://sessions`

**Content Type**: `application/json`

**Schema**:
```json
{
    "active_sessions": [
        {
            "name": "whatsapp",
            "status": "active",
            "last_used": "2026-01-15T14:30:00Z",
            "expires_at": "2026-01-22T14:30:00Z"
        }
    ],
    "total_sessions": 1
}
```

---

## Session Management

### WhatsApp Web Session

**Initial Setup**:
```python
async def setup_whatsapp_session():
    """Set up WhatsApp Web session with QR code."""
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    await page.goto('https://web.whatsapp.com')

    # Wait for QR code or chat list
    try:
        await page.wait_for_selector('div[data-testid="chat-list"]', timeout=60000)
        # Save session
        await context.storage_state(path='whatsapp_session.json')
        print("✅ WhatsApp session saved")
    except TimeoutError:
        print("❌ QR code scan timeout - please scan QR code")
        raise
```

**Load Existing Session**:
```python
async def load_whatsapp_session():
    """Load existing WhatsApp session."""
    if not os.path.exists('whatsapp_session.json'):
        raise Exception("No WhatsApp session found - run setup first")

    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        storage_state='whatsapp_session.json'
    )
    page = await context.new_page()
    await page.goto('https://web.whatsapp.com')

    # Verify session is still valid
    try:
        await page.wait_for_selector('div[data-testid="chat-list"]', timeout=10000)
        return page
    except TimeoutError:
        raise Exception("WhatsApp session expired - re-scan QR code")
```

---

## Error Codes

| Code | Description | Action |
|------|-------------|--------|
| `SESSION_EXPIRED` | Browser session expired | Re-authenticate (scan QR code) |
| `ELEMENT_NOT_FOUND` | Element selector not found | Verify selector |
| `TIMEOUT` | Operation timed out | Increase timeout or check network |
| `NAVIGATION_FAILED` | Page navigation failed | Check URL and network |
| `SCREENSHOT_FAILED` | Screenshot capture failed | Check file path permissions |
| `FORM_VALIDATION_ERROR` | Form validation failed | Check input values |

---

## Retry Logic

**Strategy**: Exponential backoff with max 3 attempts

**Delays**:
1. Immediate (0s)
2. 25 seconds
3. 2 hours

**Conditions**:
- Retry on: `TIMEOUT`, `NAVIGATION_FAILED`, `ELEMENT_NOT_FOUND` (with wait)
- Don't retry on: `SESSION_EXPIRED`, `FORM_VALIDATION_ERROR`
- Payment actions: NEVER auto-retry (require fresh approval)

---

## Audit Logging

**Every browser action MUST be logged**:
```json
{
    "timestamp": "2026-01-15T14:30:00.123456Z",
    "action_type": "send_whatsapp_message",
    "actor": "browser_mcp",
    "target": "Client A",
    "approval_status": "approved",
    "approved_by": "Jane Doe",
    "execution_status": "completed",
    "screenshot_path": "screenshots/whatsapp_20260115_143000.png",
    "credentials_sanitized": true
}
```

**Sanitization**:
- Phone numbers: Show last 4 digits (e.g., "***-***-1234")
- Session tokens: `[REDACTED]`
- Payment details: Sanitize credit card numbers

---

## Testing

### Unit Tests

```python
@pytest.mark.asyncio
async def test_navigate_to_success(mcp_client):
    """Test successful navigation."""
    result = await mcp_client.call_tool(
        "navigate_to",
        arguments={
            "url": "https://example.com",
            "wait_until": "load"
        }
    )
    assert "success" in result.content[0].text

@pytest.mark.asyncio
async def test_fill_form_dry_run(mcp_client):
    """Test form filling in dry run mode."""
    result = await mcp_client.call_tool(
        "fill_form",
        arguments={
            "fields": {"input[name='test']": "value"},
            "submit": False,
            "dry_run": True
        }
    )
    assert "filled" in result.content[0].text
```

---

## Dependencies

```python
# pyproject.toml
dependencies = [
    "fastmcp>=0.1.0",
    "playwright>=1.40.0",
]
```

---

## Example Implementation

```python
from fastmcp import FastMCP, Context
from playwright.async_api import async_playwright
from pydantic import Field
from typing import Annotated

mcp = FastMCP(name="browser-mcp")

@mcp.tool
async def send_whatsapp_message(
    contact: Annotated[str, Field(description="Contact name or phone")],
    message: Annotated[str, Field(description="Message text")],
    dry_run: Annotated[bool, Field(description="Don't actually send")] = False,
    ctx: Context = None
) -> dict:
    """Send WhatsApp message via WhatsApp Web."""
    if dry_run:
        await ctx.info(f"DRY RUN: Would send WhatsApp to {contact}")
        return {"status": "queued", "contact": contact, "message_preview": message[:50]}

    try:
        # Load WhatsApp session
        page = await load_whatsapp_session()

        # Search for contact
        await page.fill('div[contenteditable="true"]', contact)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(1000)

        # Type message
        message_box = page.locator('div[contenteditable="true"][data-tab="10"]')
        await message_box.fill(message)

        # Send message
        await page.keyboard.press('Enter')
        await ctx.info(f"Sent WhatsApp message to {contact}")

        return {
            "status": "sent",
            "contact": contact,
            "message_preview": message[:50],
            "sent_at": datetime.now().isoformat()
        }
    except Exception as e:
        await ctx.error(f"WhatsApp send failed: {e}")
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    mcp.run()
```

---

## Security Considerations

1. **Session Files**: Store in secure location, never commit to git
2. **Screenshots**: Sanitize sensitive data before storing
3. **Payment Actions**: Always take screenshot before submission
4. **Audit Trail**: Log all browser actions with sanitized data
5. **DRY_RUN Mode**: Always test with `dry_run=true` first
6. **Headless Mode**: Use headless=false for initial setup, headless=true for production

---

## Deployment

```bash
# Install Playwright browsers
playwright install chromium

# Start MCP server
python My_AI_Employee/mcp_servers/browser_mcp.py

# Or via PM2
pm2 start ecosystem.config.js --only browser-mcp
```

---

## WhatsApp Web Setup Guide

1. **First Time Setup**:
   ```bash
   python -c "from browser_mcp import setup_whatsapp_session; setup_whatsapp_session()"
   ```
   - Browser opens to WhatsApp Web
   - Scan QR code with phone
   - Session saved to `whatsapp_session.json`

2. **Verify Session**:
   ```bash
   python -c "from browser_mcp import verify_whatsapp_session; verify_whatsapp_session()"
   ```

3. **Session Expiration**:
   - Sessions expire after ~7 days of inactivity
   - System notifies when session expires
   - Re-run setup to refresh

---

**Status**: Ready for implementation
**Dependencies**: Playwright, Chromium browser
**Testing**: Unit tests + integration tests + manual QR code setup required
