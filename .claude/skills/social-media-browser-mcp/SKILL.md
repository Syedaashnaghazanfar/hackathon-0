---
name: social-media-browser-mcp
description: >
  Unified browser automation MCP server for Facebook, Instagram, and Twitter/X posting via Playwright.
  Manages persistent browser sessions for all three social platforms, handles post creation with images/text,
  generates engagement summaries, and provides health monitoring. Use when: (1) Posting to social media platforms,
  (2) Generating engagement summaries, (3) Managing multiple social media accounts, (4) Browser-based social automation.
  Trigger phrases: "post to Facebook", "post to Instagram", "tweet this", "social media post", "generate engagement summary",
  "check social media status", "FB post", "IG post", "X post", "Twitter post".
---

# Social Media Browser MCP (Gold Tier)

Unified browser automation MCP server for posting to Facebook, Instagram, and Twitter/X using Playwright. Replaces official APIs which have restrictive approval processes and rate limits.

## Quick Start

### Prerequisites

- Playwright browsers installed: `playwright install chromium`
- `.env` configured with session directory path
- Facebook, Instagram, Twitter/X accounts ready for login
- Python 3.13+ with FastMCP installed

### First-Time Setup (One Login Per Platform)

```bash
# Start the MCP server in initialization mode
python scripts/social_browser_mcp.py --init

# This will:
# 1. Launch browser for each platform
# 2. Show login page for you to authenticate
# 3. Save session to .social_session/ directory
# 4. You only need to login ONCE per platform
```

### Normal Operation

```bash
# Start the MCP server (uses saved sessions)
python scripts/social_browser_mcp.py

# Or register in .mcp.json for Claude Code
```

## Architecture: Session Persistence Pattern

**Critical Design**: Uses persistent browser context (same pattern as WhatsApp watcher)

```
┌─────────────────────────────────────────────────────────────┐
│ SINGLE BROWSER INSTANCE (Chromium)                          │
│ Persistent Context: .social_session/                         │
│ CDP Port: 9223 (different from WhatsApp's 9222)            │
├─────────────────────────────────────────────────────────────┤
│ Tab 1: facebook.com   (logged in, session saved)           │
│ Tab 2: instagram.com  (logged in, session saved)           │
│ Tab 3: x.com          (logged in, session saved)           │
└─────────────────────────────────────────────────────────────┘
```

**Benefits**:
- ✅ Login ONCE, session persists forever
- ✅ No API approval needed
- ✅ No rate limits (platform-dependent)
- ✅ Full control over post content
- ✅ Can post images, videos, text
- ✅ Works immediately (no waiting for app review)

## MCP Tools

### 1. post_to_facebook

Post content to Facebook timeline or page.

**Parameters**:
```python
{
  "text": str,                    # Post text content
  "image_path": str | None,       # Path to image file (optional)
  "page_name": str | None         # Specific page (optional)
}
```

**Returns**:
```python
{
  "success": bool,
  "post_url": str,                # URL to view post
  "timestamp": str,
  "error": str | None
}
```

**Example**:
```python
result = await post_to_facebook(
    text="Excited to share our latest project!",
    image_path="path/to/image.png"
)
```

### 2. post_to_instagram

Post content to Instagram feed or stories.

**Parameters**:
```python
{
  "text": str,                    # Caption text
  "image_path": str,              # Path to image (required for IG)
  "is_story": bool                # True for story, False for feed
}
```

**Returns**:
```python
{
  "success": bool,
  "post_url": str,
  "timestamp": str,
  "error": str | None
}
```

### 3. post_to_twitter

Post content to Twitter/X.

**Parameters**:
```python
{
  "text": str,                    # Tweet text (max 280 chars for free tier)
  "image_path": str | None,       # Path to image (optional)
  "reply_to": str | None          # Tweet ID to reply to (optional)
}
```

**Returns**:
```python
{
  "success": bool,
  "tweet_id": str,
  "tweet_url": str,
  "timestamp": str,
  "error": str | None
}
```

### 4. get_engagement_summary

Generate engagement summary across all platforms.

**Parameters**:
```python
{
  "platform": str,                # "facebook", "instagram", "twitter", "all"
  "days": int = 7                 # Number of days to analyze
}
```

**Returns**:
```python
{
  "platform": str,
  "period": str,
  "total_posts": int,
  "total_likes": int,
  "total_comments": int,
  "total_shares": int,
  "top_posts": list               # Top 3 performing posts
}
```

### 5. social_media_health_check

Check login status and session validity for all platforms.

**Returns**:
```python
{
  "facebook": {"logged_in": bool, "status": str},
  "instagram": {"logged_in": bool, "status": str},
  "twitter": {"logged_in": bool, "status": str},
  "overall_health": str           # "healthy", "degraded", "unhealthy"
}
```

## Platform-Specific Implementation Details

### Facebook (facebook_poster.py)

**Login URL**: `https://www.facebook.com`

**Post Flow**:
1. Navigate to homepage
2. Click "What's on your mind?" box
3. Type post text
4. If image_path provided: Upload image
5. Click "Post" button
6. Extract post URL from confirmation

**Selectors** (may change):
- Post box: `div[contenteditable="true"][data-text]`
- Post button: `div[aria-label="Post"]`
- Image upload: `input[type="file"]`

### Instagram (instagram_poster.py)

**Login URL**: `https://www.instagram.com`

**Post Flow**:
1. Navigate to homepage
2. Click "+" button (create post)
3. Select image from file system
4. Add caption text
5. Click "Share"
6. Extract post URL

**Selectors** (may change):
- Create button: `svg[aria-label="New post"]`
- Image upload: `input[type="file"]`
- Caption: `textarea[aria-label="Write a caption…"]`
- Share button: `div[role="button"] > button:has-text("Share")`

**Note**: Instagram requires images for posts. Text-only stories not supported.

### Twitter/X (twitter_poster.py)

**Login URL**: `https://x.com`

**Post Flow**:
1. Navigate to homepage
2. Click "Post" box
3. Type tweet text
4. If image_path provided: Upload image
5. Click "Post" button
6. Extract tweet ID and URL

**Selectors** (may change):
- Post box: `div[contenteditable="true"][data-text="What's happening?!"]`
- Post button: `div[role="button"][data-testid="tweetButtonInline"]`
- Image upload: `input[type="file"]`

## Configuration

### Environment Variables (.env)

```bash
# Social Media Session
SOCIAL_SESSION_DIR=.social_session
SOCIAL_CDP_PORT=9223

# Platform Settings
FACEBOOK_ENABLED=true
INSTAGRAM_ENABLED=true
TWITTER_ENABLED=true

# Post Defaults
DEFAULT_VISIBILITY=public        # Facebook: public, friends
INSTAGRAM_DEFAULT=feed            # feed or story

# Rate Limiting (self-imposed)
MIN_POST_INTERVAL=300            # 5 minutes between posts
DAILY_POST_LIMIT=20               # Max posts per day per platform
```

### Company_Handbook.md Integration

Add this section to your Company_Handbook.md:

```markdown
## Social Media Posting Guidelines

### Facebook
- Post frequency: 2-3 times per week
- Content type: Business updates, client success stories
- Tone: Professional but approachable
- Hashtags: 3-5 relevant tags

### Instagram
- Post frequency: 3-4 times per week
- Content type: Visual content (project screenshots, team photos)
- Caption style: Short, engaging, emoji-friendly
- Hashtags: 10-15 relevant tags

### Twitter/X
- Post frequency: 1-2 times per day
- Content type: Quick updates, industry insights, links
- Tweet style: Concise, conversational
- Hashtags: 2-3 relevant tags

### Approval Rules
- ALL social media posts require approval
- Client-facing posts: Additional legal review
- Personal content: Do not post
- Sensitive topics: Require manager approval
```

## Integration with Approval Workflow

Social media posts follow the same approval workflow as other external actions:

```
1. @needs-action-triage detects social media task
2. Creates draft post in Pending_Approval/
3. Human reviews and moves to Approved/
4. @mcp-executor triggers social_media_browser_mcp
5. Post published via browser automation
6. Result logged to Done/ with post URL
```

**Example Approval File**:
```markdown
---
type: approval_request
action_type: social_media_post
platform: instagram
status: pending
---

# Instagram Post: Project Launch

## Draft Content

🚀 Excited to launch our new project! #tech #startup #innovation

Attached image: /path/to/launch-image.png

## Approval Instructions
Move to /Approved/ to publish this post.
```

## Session Management

### First-Time Setup (Required)

```bash
python scripts/social_browser_mcp.py --init
```

This will:
1. Launch browser
2. Open Facebook login → Scan QR code or enter credentials
3. Open Instagram login → Enter credentials
4. Open Twitter/X login → Enter credentials
5. Save all sessions to `.social_session/`
6. Close browser

Sessions persist indefinitely. Re-authenticate only when:
- Session expires (usually 30-60 days)
- Password changed
- Manual logout

### Session Re-Authentication

If a session expires:
```bash
# Re-initialize specific platform
python scripts/social_browser_mcp.py --reauth facebook
```

## Monitoring and Health Checks

### Check All Platforms

```python
health = await social_media_health_check()
```

**Output**:
```json
{
  "facebook": {
    "logged_in": true,
    "status": "Session active",
    "last_check": "2026-01-15T10:00:00Z"
  },
  "instagram": {
    "logged_in": true,
    "status": "Session active",
    "last_check": "2026-01-15T10:00:00Z"
  },
  "twitter": {
    "logged_in": false,
    "status": "Session expired - re-authentication required",
    "last_check": "2026-01-15T10:00:00Z"
  },
  "overall_health": "degraded"
}
```

### Engagement Analytics

Generate weekly summary:
```python
summary = await get_engagement_summary(
    platform="all",
    days=7
)
```

**Output** (saved to `/Briefings/Social_Media_YYYY-MM-DD.md`):
```markdown
# Social Media Engagement Summary - Week of Jan 15

## Facebook
- Posts: 3
- Likes: 45
- Comments: 12
- Shares: 5
- Top Post: [link]

## Instagram
- Posts: 4
- Likes: 128
- Comments: 34
- Top Post: [link]

## Twitter/X
- Tweets: 7
- Likes: 23
- Retweets: 5
- Replies: 8
- Top Tweet: [link]
```

## Error Handling and Troubleshooting

### Common Issues

**Issue**: "Session expired - re-authentication required"

**Solution**:
```bash
python scripts/social_browser_mcp.py --reauth <platform>
```

**Issue**: "Element not found: post box selector"

**Solution**: Platform UI changed, update selectors in `scripts/*_poster.py`

**Issue**: "Image upload failed"

**Solution**: Check image format (JPG/PNG recommended), file size (<5MB)

**Issue**: "Rate limit exceeded"

**Solution**: Add delay between posts, reduce posting frequency

### Logging

All actions logged to `logs/social_media_mcp.log`:
```bash
tail -f logs/social_media_mcp.log
```

## Security and Privacy

### Session Protection

- Sessions stored in `.social_session/` (gitignored)
- Never commit session files to git
- Session files contain login cookies (treat as sensitive)

### Approval Workflow

- ALL posts require human approval
- No automated posting without review
- Posts stored in `Pending_Approval/` before execution
- Execution results logged to `Done/` with full audit trail

### Platform Terms of Service

⚠️ **Warning**: Browser automation may violate platform ToS

- Use at your own risk
- Recommended for personal/business accounts only
- Don't spam or abuse automation
- Respect rate limits and community guidelines

## References

See `references/session-management.md` for detailed session persistence patterns.

See `references/playwright-social-patterns.md` for platform-specific automation patterns.

## Key Scripts

- `scripts/social_browser_mcp.py` - Main MCP server
- `scripts/facebook_poster.py` - Facebook posting logic
- `scripts/instagram_poster.py` - Instagram posting logic
- `scripts/twitter_poster.py` - Twitter/X posting logic
- `scripts/engagement_tracker.py` - Engagement analytics
