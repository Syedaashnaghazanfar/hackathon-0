# Social Media Watcher - Quick Start Guide

## Overview

The Social Media Watcher monitors Facebook, Instagram, and Twitter/X for important interactions (comments, DMs, mentions) and creates intelligent action items in your Obsidian vault.

## Prerequisites

1. **Valid social media sessions** in `.social_session/` directory
   - Created by social-media-browser-mcp skill during setup
   - Sessions are persistent and don't expire for 30+ days

2. **Environment configured** in `.env`:
   ```bash
   cp .env.example .env
   # Edit .env and set SOCIAL_WATCHER_ENABLED=true
   ```

3. **Vault structure** exists:
   ```bash
   AI_Employee_Vault/
   ├── Needs_Action/
   ├── Pending_Approval/
   ├── Approved/
   ├── Done/
   └── Briefings/
   ```

## Quick Start

### Option 1: Run Directly (Testing)

```bash
cd My_AI_Employee

# Run social media watcher (checks every 10 minutes)
python src/my_ai_employee/watchers/social_media_watcher.py

# Or with custom check interval (5 minutes)
python src/my_ai_employee/watchers/social_media_watcher.py --check-interval 300

# Or only specific platforms
python src/my_ai_employee/watchers/social_media_watcher.py --platforms facebook,twitter

# Verbose logging
python src/my_ai_employee/watchers/social_media_watcher.py -v
```

### Option 2: Run with PM2 (Production)

```bash
cd My_AI_Employee

# Start the watcher with PM2
pm2 start ecosystem.config.js --only social-media-watcher

# View logs
pm2 logs social-media-watcher

# Stop the watcher
pm2 stop social-media-watcher

# Restart
pm2 restart social-media-watcher

# Monitor
pm2 monit
```

### Option 3: Run as System Service (Linux)

```bash
# Copy service template
sudo cp social-media-watcher.service.template /etc/systemd/system/social-media-watcher.service

# Edit the service file
sudo nano /etc/systemd/system/social-media-watcher.service
# Replace:
#   YOUR_USERNAME with your actual username
#   /path/to/My_AI_Employee with actual path

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable social-media-watcher.service

# Start service
sudo systemctl start social-media-watcher.service

# Check status
sudo systemctl status social-media-watcher.service

# View logs
sudo journalctl -u social-media-watcher -f
```

## Configuration

### Enable/Disable Platforms

Edit `.env` file:

```bash
# Enable all platforms (default)
SOCIAL_FACEBOOK_ENABLED=true
SOCIAL_INSTAGRAM_ENABLED=true
SOCIAL_TWITTER_ENABLED=true

# Enable only specific platforms
SOCIAL_FACEBOOK_ENABLED=true
SOCIAL_INSTAGRAM_ENABLED=false
SOCIAL_TWITTER_ENABLED=false
```

### Customize Priority Keywords

Edit `.env` file:

```bash
# HIGH priority keywords (urgent inquiries)
SOCIAL_HIGH_PRIORITY_KEYWORDS=urgent,help,pricing,cost,invoice,payment,client,emergency,critical

# MEDIUM priority keywords (business opportunities)
SOCIAL_BUSINESS_KEYWORDS=project,services,quote,proposal,consulting,hire,contract,opportunity
```

### Set Engagement Thresholds

Edit `.env` file:

```bash
# Viral detection thresholds
SOCIAL_FB_REACTION_THRESHOLD=10      # Facebook: 10+ reactions = viral
SOCIAL_IG_COMMENT_THRESHOLD=5       # Instagram: 5+ comments = viral
SOCIAL_TWITTER_MENTION_THRESHOLD=3   # Twitter: 3+ mentions in 1 hour = viral
```

### Set Check Interval

Edit `.env` file:

```bash
# Check interval in seconds (default: 600 = 10 minutes)
SOCIAL_WATCHER_INTERVAL=300  # 5 minutes
SOCIAL_WATCHER_INTERVAL=900  # 15 minutes
SOCIAL_WATCHER_INTERVAL=1800 # 30 minutes
```

### Set Daily Summary Time

Edit `.env` file:

```bash
# Daily summary generation time (24-hour format)
SOCIAL_SUMMARY_TIME=18:00  # 6:00 PM
SOCIAL_SUMMARY_TIME=09:00  # 9:00 AM
```

## How It Works

### 1. Monitoring Loop

```
Every 10 minutes (configurable):
    ↓
Check Facebook → Detect comments/reactions
Check Instagram → Detect DMs/comments
Check Twitter → Detect mentions/replies
    ↓
Filter by keywords → Classify priority (HIGH/MEDIUM/LOW)
    ↓
Create action items in Needs_Action/ for HIGH/MEDIUM only
    ↓
Check for viral activity → Create viral alert if threshold exceeded
    ↓
Log summary of interactions detected
```

### 2. Action Item Creation

**HIGH Priority Example:**
```yaml
---
type: social_media
source: facebook
interaction_type: comment
author: john_doe
priority: HIGH
subject: facebook comment from john_doe
tags: [facebook, comment, social_media]
---

# Facebook comment from john_doe

**Author:** john_doe
**Platform:** facebook
**Type:** comment
**Priority:** HIGH
**Priority Reason:** Matched HIGH priority keyword: 'pricing'

**Content:** Hi! I'm interested in your services. What are your pricing?

## Suggested Actions
1. Review this interaction
2. Determine if response is needed
3. If response needed, move to Pending_Approval/
4. Otherwise, move to Done/
```

**Viral Alert Example:**
```yaml
---
type: social_media
source: twitter
priority: HIGH
subject: twitter mention from System
---

⚠️ VIRAL ALERT on Twitter

**Total Interactions:** 15
**Threshold:** 3
**Exceeded By:** 12 interactions

**Time Window:** 2026-02-09 14:00 to 2026-02-09 15:00

**Breakdown:**
- Mentions: 15

**Top 5 Recent Interactions:**
1. @user1: Your project is amazing!
2. @user2: Can you share more details?
3. @user3: This is exactly what I was looking for!
4. @user4: Impressive work!
5. @user5: Following your progress with interest

**Suggested Actions:**
1. Review the viral activity immediately
2. Respond to high-priority interactions
3. Consider posting follow-up content to capitalize on engagement
```

### 3. Daily Summary

Every day at 6:00 PM (configurable), a daily summary is generated:

```
AI_Employee_Vault/Briefings/Social_Media_2026-02-09.md
```

Includes:
- Platform breakdown (FB/IG/Twitter metrics)
- Priority breakdown (HIGH/MEDIUM/LOW counts)
- Total interactions and action items
- Top performing posts by engagement
- Response rate tracking
- Viral activity alerts
- Insights and recommendations

## Troubleshooting

### Watcher not creating action items

**Solution:**
```bash
# Check if watcher is running
pm2 logs social-media-watcher --lines 50

# Check if SOCIAL_WATCHER_ENABLED=true in .env
grep SOCIAL_WATCHER_ENABLED .env

# Check vault folders exist
ls -la AI_Employee_Vault/Needs_Action/

# Verify session exists
ls -la .social_session/facebook/
ls -la .social_session/instagram/
ls -la .social_session/twitter/
```

### Session expired

**Error:** "Session expired - login form detected"

**Solution:**
```bash
# Re-authenticate using social-media-browser-mcp skill
cd .claude/skills/social-media-browser-mcp
.venv/Scripts/python social_browser_mcp.py

# Select option to login to expired platform
# Session will be saved automatically
```

### Not all platforms working

**Check platform enable status in .env:**
```bash
grep "SOCIAL_.*_ENABLED" .env
```

**Check logs for errors:**
```bash
pm2 logs social-media-watcher --lines 100
```

### Too many action items (LOW priority spam)

**Adjust keywords** to be more specific:
```bash
# Change from broad keywords
SOCIAL_HIGH_PRIORITY_KEYWORDS=urgent,help

# To very specific keywords
SOCIAL_HIGH_PRIORITY_KEYWORDS=pricing_inquiry,invoice_request
```

### Viral alerts too sensitive

**Increase thresholds:**
```bash
# Increase Twitter threshold from 3 to 10
SOCIAL_TWITTER_MENTION_THRESHOLD=10

# Increase Facebook threshold from 10 to 20
SOCIAL_FB_REACTION_THRESHOLD=20
```

## Performance

### Resource Usage

- **Memory:** ~500MB peak (3 browser contexts)
- **CPU:** Minimal when idle, spikes during browser checks
- **Cycle Time:** ~30-60 seconds per full check (all platforms)

### Optimization Tips

1. **Reduce memory usage:**
   - Disable platforms you don't need
   - Use headless mode (if browser automation supports it)
   - Increase check interval (15-30 minutes)

2. **Faster checks:**
   - Reduce check interval (5 minutes)
   - Disable slower platforms
   - Use SSD storage

3. **Reduce false positives:**
   - Tune keywords to be more specific
   - Add whitelist to only process certain accounts
   - Increase viral thresholds

## Advanced Usage

### Manual Summary Generation

```bash
python src/my_ai_employee/watchers/social_media_watcher.py --generate-summary
```

### Run Once Only (No Loop)

```bash
# Check once and exit
python src/my_ai_employee/watchers/social_media_watcher.py --check-interval 0
```

### Integration with Other Watchers

The social media watcher integrates seamlessly with existing Silver tier watchers:

```bash
# Start all watchers (including social media)
pm2 start ecosystem.config.js

# View all watcher logs
pm2 logs

# Check all watcher status
pm2 status
```

## Support

For issues or questions:
1. Check logs: `pm2 logs social-media-watcher`
2. Check configuration: `grep SOCIAL .env`
3. Verify sessions: `ls -la .social_session/`
4. Review documentation: `specs/003-gold-tier-ai-employee/spec.md`

---

**Generated by Gold Tier AI Employee - Social Media Monitoring**
