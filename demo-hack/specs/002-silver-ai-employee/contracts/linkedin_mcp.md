# LinkedIn MCP Server Contract

**Server Name**: `linkedin-mcp`
**Purpose**: Create posts and manage LinkedIn presence
**Technology**: FastMCP + LinkedIn API (with Playwright fallback)
**Location**: `My_AI_Employee/mcp_servers/linkedin_mcp.py`

---

## Overview

The LinkedIn MCP Server provides tools for creating posts, sharing content, and managing LinkedIn presence. It uses LinkedIn API as the primary method with Playwright as a fallback for unsupported features.

---

## Tools

### 1. create_post

**Description**: Create a LinkedIn post on user's profile

**Input Schema**:
```python
{
    "text": str,         # Post content (required, max 3000 chars)
    "hashtags": list[str],  # Hashtags to include (optional)
    "visibility": str,   # "PUBLIC" | "CONNECTIONS" (optional, default: "PUBLIC")
    "dry_run": bool      # If true, don't actually post (optional, default: false)
}
```

**Output Schema**:
```python
{
    "status": "posted" | "queued" | "failed",
    "post_id": str,              # LinkedIn post ID
    "post_url": str,             # URL to view post
    "posted_at": str,            # ISO8601 timestamp
    "method": "api" | "playwright",  # Which method was used
    "engagement": {
        "likes": int,
        "comments": int,
        "shares": int
    },
    "error": str | null
}
```

**Validation Rules**:
- `text` MUST be non-empty and <= 3000 characters
- `hashtags` MUST start with # if provided
- `visibility` MUST be "PUBLIC" or "CONNECTIONS"
- If `dry_run` is true, return status "queued" without posting

**Error Handling**:
- API failure → Retry with Playwright
- Rate limit → Queue for later (respect LinkedIn rate limits)
- Authentication failure → Return error with instructions to refresh credentials

**Example Usage**:
```python
result = await ctx.call_tool(
    "create_post",
    arguments={
        "text": "Excited to share our latest automation insights!",
        "hashtags": ["#automation", "#business", "#innovation"],
        "visibility": "PUBLIC",
        "dry_run": False
    }
)
# Returns: {"status": "posted", "post_id": "123", "post_url": "https://linkedin.com/...", "posted_at": "2026-01-15T09:00:00Z"}
```

---

### 2. schedule_post

**Description**: Schedule a LinkedIn post for future publication

**Input Schema**:
```python
{
    "text": str,         # Post content (required)
    "hashtags": list[str],  # Hashtags (optional)
    "scheduled_time": str,  # ISO8601 timestamp (required)
    "visibility": str    # "PUBLIC" | "CONNECTIONS" (optional)
}
```

**Output Schema**:
```python
{
    "status": "scheduled",
    "schedule_id": str,
    "scheduled_for": str,  # ISO8601 timestamp
    "created_at": str
}
```

**Validation Rules**:
- `scheduled_time` MUST be in the future
- `scheduled_time` MUST be at least 10 minutes from now
- Maximum 25 scheduled posts at a time (LinkedIn limit)

**Example Usage**:
```python
result = await ctx.call_tool(
    "schedule_post",
    arguments={
        "text": "Monday motivation post",
        "hashtags": ["#MondayMotivation"],
        "scheduled_time": "2026-01-20T09:00:00Z"
    }
)
```

---

### 3. get_post_analytics

**Description**: Get engagement metrics for a posted content

**Input Schema**:
```python
{
    "post_id": str,      # LinkedIn post ID (required)
    "metrics": list[str]  # ["likes", "comments", "shares", "views"] (optional, default: all)
}
```

**Output Schema**:
```python
{
    "status": "success",
    "post_id": str,
    "metrics": {
        "likes": int,
        "comments": int,
        "shares": int,
        "views": int,
        "engagement_rate": float  # percentage
    },
    "last_updated": str  # ISO8601 timestamp
}
```

**Example Usage**:
```python
result = await ctx.call_tool(
    "get_post_analytics",
    arguments={
        "post_id": "123",
        "metrics": ["likes", "comments", "shares"]
    }
)
```

---

## Resources

### 1. linkedin://config

**Description**: LinkedIn API configuration

**URI**: `linkedin://config`

**Content Type**: `application/json`

**Schema**:
```json
{
    "api": {
        "enabled": true,
        "client_id": "your_client_id",
        "client_secret": "[REDACTED]",
        "redirect_uri": "http://localhost:8000/callback",
        "scopes": ["w_member_social", "r_liteprofile"]
    },
    "playwright": {
        "enabled": true,
        "session_file": "linkedin_session.json",
        "headless": false
    },
    "rate_limits": {
        "posts_per_day": 25,
        "posts_per_hour": 5
    },
    "posting_schedule": {
        "preferred_times": ["09:00", "14:00"],
        "timezone": "America/New_York"
    }
}
```

---

### 2. linkedin://scheduled_posts

**Description**: List of scheduled posts

**URI**: `linkedin://scheduled_posts`

**Content Type**: `application/json`

**Schema**:
```json
{
    "scheduled_posts": [
        {
            "schedule_id": "sched_001",
            "text": "Monday motivation post",
            "hashtags": ["#MondayMotivation"],
            "scheduled_for": "2026-01-20T09:00:00Z",
            "status": "pending"
        }
    ],
    "total_scheduled": 1
}
```

---

## Authentication

### LinkedIn API OAuth 2.0

**Setup**:
1. Create LinkedIn App at https://www.linkedin.com/developers/
2. Get Client ID and Client Secret
3. Set redirect URI: `http://localhost:8000/callback`
4. Request scopes: `w_member_social`, `r_liteprofile`
5. Run OAuth flow (opens browser)
6. Token saved to secure storage

**Scopes Required**:
- `w_member_social` - Create posts
- `r_liteprofile` - Read profile info

**Token Refresh**:
- Tokens expire after 60 days
- Automatic refresh when possible
- Manual re-authentication if refresh fails

### Playwright Fallback

**Setup**:
1. First run: Opens browser for login
2. Scan QR code or enter credentials
3. Session saved to `linkedin_session.json`
4. Subsequent runs: Load saved session

**Session Management**:
```python
# Save session
context.storage_state(path='linkedin_session.json')

# Load session
context = browser.new_context(storage_state='linkedin_session.json')
```

---

## Error Codes

| Code | Description | Action |
|------|-------------|--------|
| `AUTH_FAILED` | Authentication failed | Refresh OAuth token or re-login via Playwright |
| `RATE_LIMIT` | Rate limit exceeded | Queue post for later |
| `INVALID_CONTENT` | Content violates LinkedIn policies | Review content |
| `NETWORK_ERROR` | Network connection failed | Retry with exponential backoff |
| `API_ERROR` | LinkedIn API error | Fallback to Playwright |
| `SESSION_EXPIRED` | Playwright session expired | Re-authenticate |

---

## Retry Logic

**Strategy**: Exponential backoff with max 3 attempts

**Delays**:
1. Immediate (0s)
2. 25 seconds
3. 2 hours

**Conditions**:
- Retry on: `NETWORK_ERROR`, `API_ERROR`, `RATE_LIMIT`
- Don't retry on: `AUTH_FAILED`, `INVALID_CONTENT`
- Always queue if rate limit hit

---

## Audit Logging

**Every post MUST be logged**:
```json
{
    "timestamp": "2026-01-15T09:00:00.123456Z",
    "action_type": "create_post",
    "actor": "linkedin_mcp",
    "target": "linkedin_profile",
    "approval_status": "approved",
    "approved_by": "Jane Doe",
    "execution_status": "completed",
    "method": "api",
    "post_id": "123",
    "post_url": "https://linkedin.com/...",
    "credentials_sanitized": true
}
```

**Sanitization**:
- OAuth tokens: `[REDACTED]`
- Client secrets: `[REDACTED]`

---

## Testing

### Unit Tests

```python
@pytest.mark.asyncio
async def test_create_post_success(mcp_client):
    """Test successful post creation."""
    result = await mcp_client.call_tool(
        "create_post",
        arguments={
            "text": "Test post",
            "hashtags": ["#test"],
            "dry_run": True
        }
    )
    assert "queued" in result.content[0].text

@pytest.mark.asyncio
async def test_create_post_too_long(mcp_client):
    """Test post with content too long."""
    with pytest.raises(Exception) as exc_info:
        await mcp_client.call_tool(
            "create_post",
            arguments={
                "text": "x" * 3001,  # Exceeds 3000 char limit
                "hashtags": []
            }
        )
    assert "too long" in str(exc_info.value).lower()
```

---

## Dependencies

```python
# pyproject.toml
dependencies = [
    "fastmcp>=0.1.0",
    "linkedin-api-python-client>=0.1.0",
    "playwright>=1.40.0",
]
```

---

## Example Implementation

```python
from fastmcp import FastMCP, Context
from pydantic import Field
from typing import Annotated

mcp = FastMCP(name="linkedin-mcp")

@mcp.tool
async def create_post(
    text: Annotated[str, Field(description="Post content", max_length=3000)],
    hashtags: Annotated[list[str], Field(description="Hashtags")] = [],
    visibility: Annotated[str, Field(description="Post visibility")] = "PUBLIC",
    dry_run: Annotated[bool, Field(description="Don't actually post")] = False,
    ctx: Context = None
) -> dict:
    """Create LinkedIn post via API with Playwright fallback."""
    if dry_run:
        await ctx.info(f"DRY RUN: Would post to LinkedIn")
        return {"status": "queued", "post_id": "dry_run", "method": "dry_run"}

    # Format post content
    post_content = f"{text}\n\n{' '.join(hashtags)}"

    try:
        # Try API first
        api = get_linkedin_api()
        post_id = api.post_update(text=post_content, visibility=visibility)
        await ctx.info(f"Posted via API: {post_id}")
        return {
            "status": "posted",
            "post_id": post_id,
            "post_url": f"https://linkedin.com/feed/update/{post_id}",
            "posted_at": datetime.now().isoformat(),
            "method": "api"
        }
    except Exception as e:
        await ctx.warning(f"API failed: {e}, trying Playwright")
        try:
            # Fallback to Playwright
            post_id = await create_post_playwright(post_content)
            await ctx.info(f"Posted via Playwright: {post_id}")
            return {
                "status": "posted",
                "post_id": post_id,
                "posted_at": datetime.now().isoformat(),
                "method": "playwright"
            }
        except Exception as pw_error:
            await ctx.error(f"Playwright also failed: {pw_error}")
            return {"status": "failed", "error": str(pw_error)}

if __name__ == "__main__":
    mcp.run()
```

---

## Security Considerations

1. **Credentials**: Never log OAuth tokens or client secrets
2. **Rate Limits**: Respect LinkedIn limits (25 posts/day, 5 posts/hour)
3. **Content Validation**: Check for policy violations before posting
4. **Audit Trail**: Log all post attempts with sanitized data
5. **DRY_RUN Mode**: Always test with `dry_run=true` first

---

## Deployment

```bash
# Start MCP server
python My_AI_Employee/mcp_servers/linkedin_mcp.py

# Or via PM2
pm2 start ecosystem.config.js --only linkedin-mcp
```

---

**Status**: Ready for implementation
**Dependencies**: LinkedIn API credentials OR Playwright session
**Testing**: Unit tests + integration tests required
