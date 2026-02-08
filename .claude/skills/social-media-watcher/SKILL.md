---
name: social-media-watcher
description: >
  Watch social media platforms (Facebook, Instagram, Twitter/X) for comments, messages, and engagement.
  Creates action items in Needs_Action when important interactions detected. Use when: (1) Monitoring social
  media for client interactions, (2) Tracking comments and messages, (3) Generating engagement summaries,
  (4) Alerting about important social notifications. Trigger phrases: "monitor social media", "check social media",
  "social media watcher", "watch Facebook comments", "track Instagram messages", "Twitter notifications".
---

# Social Media Watcher (Gold Tier - Optional)

Monitor social media platforms for important interactions and create action items for follow-up. Works with `social-media-browser-mcp` for complete social media automation.

## Quick Start

### Prerequisites

- `social-media-browser-mcp` skill configured and logged in
- Session files in `.social_session/`
- Company_Handbook.md social media rules configured

### Start Watching

```bash
python scripts/social_media_watcher.py --vault-path "AI_Employee_Vault"
```

The watcher will:
1. Check each platform for new notifications
2. Filter for important interactions (comments, messages, mentions)
3. Create action items in `Needs_Action/`
4. Log all detected activity

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ SOCIAL MEDIA WATCHER                                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CHECKS EVERY: 10 minutes                                    │
│                                                              │
│  FACEBOOK                                                    │
│  ├─ Page comments                                           │
│  ├─ Page messages                                           │
│  ├─ Mentions                                                │
│  └─ Post reactions (threshold)                              │
│                                                              │
│  INSTAGRAM                                                   │
│  ├─ Post comments                                           │
│  ├─ DM messages                                             │
│  ├─ Mentions                                                │
│  └── New followers (business accounts)                      │
│                                                              │
│  TWITTER/X                                                    │
│  ├─ Mentions                                                │
│  ├─ Replies                                                 │
│  ├─ DM messages                                             │
│  └─ Quote tweets                                            │
│                                                              │
│  FILTERS                                                     │
│  ├─ Client/lead keywords                                    │
│  ├─ Urgency indicators                                      │
│  ├─ Business-related hashtags                               │
│  └─ Account whitelist                                       │
│                                                              │
│  OUTPUT                                                      │
│  └─ Action items in Needs_Action/                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Platform-Specific Monitoring

### Facebook

**What it monitors**:
- Comments on page posts
- Messages to page inbox
- Mentions of page name
- Post reactions (when > threshold)

**Priority detection**:
- **HIGH**: Client names, pricing questions, "urgent", "help"
- **MEDIUM**: General inquiries, feedback
- **LOW**: Spam, reactions only

### Instagram

**What it monitors**:
- Comments on posts
- DM messages
- Mentions in comments/stories
- New followers (business accounts only)

**Priority detection**:
- **HIGH**: Client inquiries, collaboration requests
- **MEDIUM**: Comments asking for information
- **LOW**: Generic comments, emoji-only

### Twitter/X

**What it monitors**:
- Mentions of @handle
- Replies to tweets
- DM messages
- Quote tweets

**Priority detection**:
- **HIGH**: Client mentions, support requests, pricing
- **MEDIUM**: Industry discussions, networking
- **LOW**: Generic mentions, retweets

## Configuration

### Environment Variables (.env)

```bash
# Social Media Watcher
SOCIAL_WATCHER_ENABLED=true
SOCIAL_WATCHER_INTERVAL=600        # Check every 10 minutes
SOCIAL_SESSION_DIR=.social_session

# Priority Keywords (comma-separated)
SOCIAL_HIGH_PRIORITY_KEYWORDS=urgent,help,pricing,cost,invoice,payment,client,emergency
SOCIAL_BUSINESS_KEYWORDS=project,services,quote,proposal,consulting,hire,contract

# Account Whitelist (accounts to always monitor)
SOCIAL_WHITELIST_ACCOUNTS=client_a,client_b,important_contact

# Engagement Thresholds
SOCIAL_FB_REACTION_THRESHOLD=10    # Alert when post gets 10+ reactions
SOCIAL_IG_COMMENT_THRESHOLD=5     # Alert when post gets 5+ comments
SOCIAL_TWITTER_MENTION_THRESHOLD=3 # Alert when 3+ mentions in hour
```

### Company_Handbook.md Integration

```markdown
## Social Media Monitoring

### Watcher Schedule
- Check interval: Every 10 minutes
- Platforms: Facebook, Instagram, Twitter/X
- Action: Create action items for important interactions

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

### Engagement Summaries
- Generate: Daily at 6 PM
- Include: Top posts, total engagement, follower growth
- Location: Briefings/Social_Media_YYYY-MM-DD.md
```

## Key Scripts

### 1. social_media_watcher.py

Main watcher orchestration script.

**Usage**:
```bash
python scripts/social_media_watcher.py --vault-path "AI_Employee_Vault"
```

**Features**:
- Checks all platforms periodically
- Filters interactions by priority
- Creates action items for important events
- Logs all activity

### 2. facebook_monitor.py

Facebook-specific monitoring logic.

**Monitors**:
- Page comments
- Page messages
- Post reactions

**Action Item Creation**:
```markdown
---
type: social_media_notification
platform: facebook
source: comment
priority: HIGH
created: 2026-01-15T10:30:00Z
---

# Facebook Comment: Client Inquiry

**Post**: [Link to post]
**Comment**: "Hi, I'm interested in your services. What's your pricing?"

**Commenter**: John Doe
**Time**: 2 hours ago

## Suggested Action
- Respond with pricing information
- Ask about project scope
- Offer consultation call

**Priority**: HIGH - Client showing purchase intent
```

### 3. instagram_monitor.py

Instagram-specific monitoring logic.

**Monitors**:
- Post comments
- DM messages
- New followers (business accounts)

### 4. twitter_monitor.py

Twitter/X-specific monitoring logic.

**Monitors**:
- Mentions
- Replies
- DM messages
- Quote tweets

## Action Item Schema

Social media action items follow this structure:

```markdown
---
type: social_media_notification
platform: facebook|instagram|twitter
source: comment|message|mention
priority: HIGH|MEDIUM|LOW
created: ISO8601 timestamp
original_url: link to social media post
---

# Social Media Interaction: [Platform] - [Type]

**Platform**: Facebook
**Source**: Comment on post "Latest Project Update"
**Author**: [Name] ([@handle])
**Time**: [Relative time]

## Content

[The actual comment/message text]

## Context

- Post URL: [Link]
- Post date: [Date]
- Post engagement: [Likes, comments, shares]

## Analysis

**Intent**: [Pricing inquiry, support request, general question]
**Sentiment**: [Positive, neutral, negative]
**Priority**: [HIGH/MEDIUM/LOW with reason]

## Suggested Actions

- [ ] Response strategy
- [ ] Key points to address
- [ ] Call to action

## Automated Response Draft

[Optional: Pre-drafted response based on Company_Handbook rules]
```

## Integration with Approval Workflow

Social media interactions requiring responses follow the approval workflow:

```
1. Watcher detects comment/message
2. Creates action item in Needs_Action/
3. @needs-action-triage processes item
4. Generates response draft (if approved)
5. Creates approval request in Pending_Approval/
6. Human reviews and approves
7. @mcp-executor posts response via social-media-browser-mcp
8. Logs to Done/ with result
```

## Engagement Summaries

Daily engagement summaries generated by watcher:

```markdown
# Social Media Engagement Summary - January 15, 2026

## Facebook
- **New Comments**: 5 (2 HIGH priority, 3 MEDIUM)
- **New Messages**: 2
- **Post Reactions**: 45 total across 3 posts
- **Top Post**: [Link] - 25 reactions, 8 comments

## Instagram
- **New Comments**: 12 (1 HIGH priority, 11 MEDIUM)
- **New DMs**: 3
- **New Followers**: 8 (5 business accounts)
- **Top Post**: [Link] - 50 likes, 12 comments

## Twitter/X
- **New Mentions**: 8
- **New Replies**: 3
- **New DMs**: 1
- **Top Tweet**: [Link] - 15 retweets, 5 replies

## Action Items Created

- [x] Client pricing inquiry (HIGH) - Responded
- [ ] Collaboration request (MEDIUM) - Awaiting approval
- [ ] Support question (LOW) - Scheduled for batch response

## Summary
- Total interactions: 33
- Action items created: 3
- Response rate: 90%
```

## Troubleshooting

### Common Issues

**Issue**: "No new notifications detected"

**Possible causes**:
1. Session expired - Re-login via `social-media-browser-mcp`
2. No new activity - Check platforms manually
3. Rate limiting - Wait 15 minutes

**Issue**: "Too many LOW priority items"

**Solution**: Adjust keyword filtering in `.env`:
```bash
# Add more specific keywords
SOCIAL_BUSINESS_KEYWORDS=client,project,pricing,consulting
```

**Issue**: "Missing important messages"

**Solution**: Add account to whitelist:
```bash
# Add important accounts
SOCIAL_WHITELIST_ACCOUNTS=client_a,prospect_b,partner_c
```

### Logging

Watcher logs to `logs/social_media_watcher.log`:
```bash
tail -f logs/social_media_watcher.log
```

## Scheduling

### Run as Background Process

**Linux/Mac (using nohup)**:
```bash
nohup python scripts/social_media_watcher.py --vault-path "AI_Employee_Vault" > logs/social_watcher.log 2>&1 &
```

**Windows (Task Scheduler)**:
1. Create task to run on startup
2. Trigger: At startup, repeat every 10 minutes
3. Action: Run `python.exe scripts/social_media_watcher.py`

### Integration with Multi-Watcher Runner

Add to existing orchestrator (`multi-watcher-runner` skill):

```python
# In orchestrate_watchers.py
from social_media_watcher import SocialMediaWatcher

watchers = [
    # Existing watchers...
    SocialMediaWatcher(vault_path, check_interval=600)  # 10 minutes
]

for watcher in watchers:
    watcher.start()
```

## Best Practices

### Response Prioritization

1. **HIGH**: Respond within 1 hour
   - Client inquiries
   - Pricing questions
   - Urgent requests

2. **MEDIUM**: Respond within 24 hours
   - General questions
   - Collaboration requests
   - Feedback

3. **LOW**: Batch responses
   - Generic comments
   - Spam filtering
   - Low-value interactions

### Engagement Strategy

- **Monitor daily**: Review all HIGH and MEDIUM items
- **Batch LOW items**: Respond once per day
- **Track patterns**: Identify common questions for FAQ
- **Measure response time**: Aim for < 1 hour for HIGH priority

## References

See `references/social-prioritization.md` for filtering strategies.

See `references/engagement-metrics.md` for tracking KPIs.

## Key Scripts

- `scripts/social_media_watcher.py` - Main watcher
- `scripts/facebook_monitor.py` - Facebook monitoring
- `scripts/instagram_monitor.py` - Instagram monitoring
- `scripts/twitter_monitor.py` - Twitter/X monitoring
- `scripts/engagement_summary.py` - Daily summaries
