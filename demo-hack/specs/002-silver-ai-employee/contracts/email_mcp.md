# Email MCP Server Contract

**Server Name**: `email-mcp`
**Purpose**: Send and manage emails via Gmail API with SMTP fallback
**Technology**: FastMCP + google-api-python-client + smtplib
**Location**: `My_AI_Employee/mcp_servers/email_mcp.py`

---

## Overview

The Email MCP Server provides tools for sending emails, drafting emails, and searching the mailbox. It uses Gmail API as the primary method with SMTP as a fallback for reliability.

---

## Tools

### 1. send_email

**Description**: Send an email via Gmail API (primary) or SMTP (fallback)

**Input Schema**:
```python
{
    "to": str,           # Recipient email address (required)
    "subject": str,      # Email subject line (required)
    "body": str,         # Email body content (required)
    "cc": list[str],     # CC recipients (optional)
    "bcc": list[str],    # BCC recipients (optional)
    "reply_to": str,     # Reply-to address (optional)
    "dry_run": bool      # If true, don't actually send (optional, default: false)
}
```

**Output Schema**:
```python
{
    "status": "sent" | "queued" | "failed",
    "message_id": str,              # Gmail message ID or SMTP message ID
    "method": "gmail_api" | "smtp", # Which method was used
    "sent_at": str,                 # ISO8601 timestamp
    "error": str | null             # Error message if failed
}
```

**Validation Rules**:
- `to` MUST be valid email address format
- `subject` MUST be non-empty string
- `body` MUST be non-empty string
- `cc` and `bcc` MUST be valid email addresses if provided
- If `dry_run` is true, return status "queued" without sending

**Error Handling**:
- Gmail API failure → Retry with SMTP
- SMTP failure → Return error with status "failed"
- Authentication failure → Return error with instructions to refresh credentials
- Rate limit → Queue locally and return status "queued"

**Example Usage**:
```python
result = await ctx.call_tool(
    "send_email",
    arguments={
        "to": "client@example.com",
        "subject": "Project Update",
        "body": "The project is complete.",
        "dry_run": False
    }
)
# Returns: {"status": "sent", "message_id": "abc123", "method": "gmail_api", "sent_at": "2026-01-15T14:30:00Z"}
```

---

### 2. draft_email

**Description**: Create a draft email without sending

**Input Schema**:
```python
{
    "to": str,           # Recipient email address (required)
    "subject": str,      # Email subject line (required)
    "body": str,         # Email body content (required)
    "cc": list[str],     # CC recipients (optional)
    "bcc": list[str]     # BCC recipients (optional)
}
```

**Output Schema**:
```python
{
    "status": "draft_created",
    "draft_id": str,     # Gmail draft ID
    "created_at": str    # ISO8601 timestamp
}
```

**Validation Rules**:
- Same as `send_email` for email addresses
- Draft is saved to Gmail drafts folder

**Example Usage**:
```python
result = await ctx.call_tool(
    "draft_email",
    arguments={
        "to": "client@example.com",
        "subject": "Project Update",
        "body": "Draft content"
    }
)
# Returns: {"status": "draft_created", "draft_id": "draft123", "created_at": "2026-01-15T14:30:00Z"}
```

---

### 3. search_mail

**Description**: Search mailbox for messages matching query

**Input Schema**:
```python
{
    "query": str,        # Gmail search query (required)
    "max_results": int,  # Maximum results to return (optional, default: 10, max: 100)
    "label_ids": list[str]  # Filter by labels (optional, e.g., ["INBOX", "UNREAD"])
}
```

**Output Schema**:
```python
{
    "status": "success",
    "messages": [
        {
            "id": str,
            "thread_id": str,
            "from": str,
            "subject": str,
            "snippet": str,
            "date": str,  # ISO8601 timestamp
            "labels": list[str]
        }
    ],
    "total_count": int
}
```

**Validation Rules**:
- `query` MUST be non-empty string
- `max_results` MUST be between 1 and 100
- Uses Gmail search syntax (e.g., "from:client@example.com subject:urgent")

**Example Usage**:
```python
result = await ctx.call_tool(
    "search_mail",
    arguments={
        "query": "from:client@example.com",
        "max_results": 5,
        "label_ids": ["INBOX"]
    }
)
# Returns: {"status": "success", "messages": [...], "total_count": 5}
```

---

## Resources

### 1. email://config

**Description**: Email server configuration

**URI**: `email://config`

**Content Type**: `application/json`

**Schema**:
```json
{
    "gmail_api": {
        "enabled": true,
        "scopes": [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.readonly"
        ],
        "credentials_file": "credentials.json",
        "token_file": "token.json"
    },
    "smtp": {
        "enabled": true,
        "host": "smtp.gmail.com",
        "port": 587,
        "use_tls": true,
        "from_address": "user@example.com"
    },
    "rate_limits": {
        "gmail_api": 100,  # per day
        "smtp": 500        # per day
    }
}
```

---

### 2. email://queue

**Description**: Queued emails waiting to be sent (when API is down)

**URI**: `email://queue`

**Content Type**: `application/json`

**Schema**:
```json
{
    "queued_emails": [
        {
            "id": "queue_001",
            "to": "client@example.com",
            "subject": "Project Update",
            "body": "...",
            "queued_at": "2026-01-15T14:30:00Z",
            "retry_count": 0,
            "next_retry": "2026-01-15T14:30:25Z"
        }
    ],
    "total_queued": 1
}
```

---

## Authentication

### Gmail API OAuth 2.0

**Setup**:
1. Create Google Cloud project
2. Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json`
5. Run authentication flow (opens browser)
6. Token saved to `token.json`

**Scopes Required**:
- `https://www.googleapis.com/auth/gmail.send` - Send emails
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails

**Token Refresh**:
- Automatic refresh when token expires
- Refresh token stored in `token.json`
- Manual re-authentication if refresh token expires

### SMTP Authentication

**Setup**:
1. Enable "App Passwords" in Google Account
2. Generate app-specific password
3. Store in `.env` file:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=user@example.com
   SMTP_PASSWORD=app_password_here
   ```

---

## Error Codes

| Code | Description | Action |
|------|-------------|--------|
| `AUTH_FAILED` | Authentication failed | Refresh OAuth token or check SMTP credentials |
| `RATE_LIMIT` | API rate limit exceeded | Queue email for later |
| `INVALID_EMAIL` | Invalid email address format | Validate input |
| `NETWORK_ERROR` | Network connection failed | Retry with exponential backoff |
| `API_ERROR` | Gmail API error | Fallback to SMTP |
| `SMTP_ERROR` | SMTP send failed | Queue for retry |

---

## Retry Logic

**Strategy**: Exponential backoff with max 3 attempts

**Delays**:
1. Immediate (0s)
2. 25 seconds
3. 2 hours

**Conditions**:
- Retry on: `NETWORK_ERROR`, `API_ERROR`, `RATE_LIMIT`
- Don't retry on: `AUTH_FAILED`, `INVALID_EMAIL`
- Banking/payment emails: NEVER auto-retry (require fresh approval)

---

## Audit Logging

**Every email send MUST be logged**:
```json
{
    "timestamp": "2026-01-15T14:30:00.123456Z",
    "action_type": "send_email",
    "actor": "email_mcp",
    "target": "client@example.com",
    "approval_status": "approved",
    "approved_by": "Jane Doe",
    "execution_status": "completed",
    "method": "gmail_api",
    "message_id": "abc123",
    "credentials_sanitized": true
}
```

**Sanitization**:
- Email addresses: `user@*****.com`
- OAuth tokens: `[REDACTED]`
- SMTP passwords: `[REDACTED]`

---

## Testing

### Unit Tests

```python
@pytest.mark.asyncio
async def test_send_email_success(mcp_client):
    """Test successful email send."""
    result = await mcp_client.call_tool(
        "send_email",
        arguments={
            "to": "test@example.com",
            "subject": "Test",
            "body": "Test email",
            "dry_run": True
        }
    )
    assert result.content[0].text == "queued"

@pytest.mark.asyncio
async def test_send_email_invalid_address(mcp_client):
    """Test email send with invalid address."""
    with pytest.raises(Exception) as exc_info:
        await mcp_client.call_tool(
            "send_email",
            arguments={
                "to": "invalid-email",
                "subject": "Test",
                "body": "Test"
            }
        )
    assert "Invalid email" in str(exc_info.value)
```

### Integration Tests

```python
def test_gmail_api_fallback_to_smtp():
    """Test fallback from Gmail API to SMTP."""
    # Mock Gmail API failure
    with mock.patch('gmail_api.send', side_effect=Exception("API down")):
        result = send_email("test@example.com", "Test", "Body")
        assert result["method"] == "smtp"
        assert result["status"] == "sent"
```

---

## Dependencies

```python
# pyproject.toml
dependencies = [
    "fastmcp>=0.1.0",
    "google-api-python-client>=2.100.0",
    "google-auth-oauthlib>=1.1.0",
    "google-auth-httplib2>=0.1.1",
]
```

---

## Example Implementation

```python
from fastmcp import FastMCP, Context
from pydantic import Field
from typing import Annotated

mcp = FastMCP(name="email-mcp")

@mcp.tool
async def send_email(
    to: Annotated[str, Field(description="Recipient email address")],
    subject: Annotated[str, Field(description="Email subject line")],
    body: Annotated[str, Field(description="Email body content")],
    dry_run: Annotated[bool, Field(description="Don't actually send")] = False,
    ctx: Context = None
) -> dict:
    """Send email via Gmail API with SMTP fallback."""
    if dry_run:
        await ctx.info(f"DRY RUN: Would send email to {to}")
        return {"status": "queued", "message_id": "dry_run", "method": "dry_run"}

    try:
        # Try Gmail API first
        service = get_gmail_service()
        message_id = send_via_gmail_api(service, to, subject, body)
        await ctx.info(f"Sent email via Gmail API: {message_id}")
        return {
            "status": "sent",
            "message_id": message_id,
            "method": "gmail_api",
            "sent_at": datetime.now().isoformat()
        }
    except Exception as e:
        await ctx.warning(f"Gmail API failed: {e}, trying SMTP")
        try:
            # Fallback to SMTP
            message_id = send_via_smtp(to, subject, body)
            await ctx.info(f"Sent email via SMTP: {message_id}")
            return {
                "status": "sent",
                "message_id": message_id,
                "method": "smtp",
                "sent_at": datetime.now().isoformat()
            }
        except Exception as smtp_error:
            await ctx.error(f"SMTP also failed: {smtp_error}")
            return {
                "status": "failed",
                "error": str(smtp_error),
                "method": "none"
            }

if __name__ == "__main__":
    mcp.run()
```

---

## Security Considerations

1. **Credentials**: Never log OAuth tokens or SMTP passwords
2. **Rate Limits**: Respect Gmail API quotas (100 emails/day for free tier)
3. **Validation**: Always validate email addresses before sending
4. **Audit Trail**: Log all send attempts with sanitized data
5. **DRY_RUN Mode**: Always test with `dry_run=true` first

---

## Deployment

```bash
# Start MCP server
python My_AI_Employee/mcp_servers/email_mcp.py

# Or via PM2
pm2 start ecosystem.config.js --only email-mcp
```

---

**Status**: Ready for implementation
**Dependencies**: Gmail API credentials, SMTP credentials (fallback)
**Testing**: Unit tests + integration tests required
