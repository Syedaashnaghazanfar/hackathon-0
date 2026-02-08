# Feature Specification: Gold Tier AI Employee

**Feature Branch**: `003-gold-tier-ai-employee`
**Created**: 2026-02-05
**Status**: Draft
**Input**: Implement comprehensive Gold Tier AI Employee with Monday Morning CEO Briefing, social media automation (Facebook/Instagram/Twitter), Xero accounting integration, and full cross-domain integration between personal and business domains.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Monday Morning CEO Briefing (Priority: P1)

As a business owner, I want to receive an automated Monday morning briefing that analyzes my business performance, revenue, completed tasks, bottlenecks, and cost optimization opportunities, so that I can start my week with strategic clarity and focus on high-impact activities.

**Why this priority**: This is the highest value Gold Tier feature - it transforms the AI Employee from reactive task executor to proactive business advisor. Provides immediate ROI through data-driven insights and bottleneck identification. Independently testable as a standalone MVP.

**Independent Test**: Can be fully tested by creating Business_Goals.md, Accounting/Current_Month.md, and Tasks/Done/ in vault, running the briefing generator, and verifying comprehensive Monday_Briefing.md output with health scores, revenue analysis, bottleneck detection, and action items.

**Acceptance Scenarios**:

1. **Given** a vault with Business_Goals.md containing $10,000 monthly revenue target, Accounting/Current_Month.md with $4,500 MTD revenue from 5 client transactions, and Tasks/Done/ with 12 completed tasks (2 overdue), **When** Monday morning briefing runs at 7:00 AM, **Then** system generates Briefings/YYYY-MM-DD_Monday_Briefing.md with executive summary showing 45% revenue progress, health score 75/100, bottleneck table listing 2 delayed tasks with severity HIGH/MEDIUM, and action items prioritized by urgency.

2. **Given** a vault with minimal data (no Business_Goals.md, empty Accounting/), **When** Monday morning briefing runs, **Then** system generates briefing with graceful degradation - shows "No revenue targets set" and "No accounting data found" warnings, generates partial briefing with available task data, logs missing data sources for user awareness.

3. **Given** a vault with Business_Goals.md specifying software cost audit rules (flag if no login in 30 days or cost increased >20%), Accounting/Current_Month.md showing Notion subscription $15/month with last login 45 days ago and Adobe CC $54.99/month with 25% cost increase, **When** Monday morning briefing runs, **Then** cost optimization section identifies both subscriptions, recommends cancellation/consolidation with projected annual savings ($180 for Notion, $330 for Adobe), creates HIGH priority action items for review.

---

### User Story 2 - Social Media Cross-Posting (Priority: P2)

As a business owner, I want to create social media content once and automatically post it to Facebook, Instagram, and Twitter/X with platform-specific formatting, so that I can maintain consistent social presence without manual repetition and save 2-3 hours per week.

**Why this priority**: Critical time-saver for business owners managing multiple social platforms. Builds on existing WhatsApp/LinkedIn infrastructure from Silver tier. Independently testable - can demonstrate posting to one platform without full three-platform implementation.

**Independent Test**: Can be fully tested by installing social-media-browser-mcp skill, logging into one platform (e.g., Facebook) via browser automation, creating Pending_Approval/social_post.md with content, approving via @mcp-executor, and verifying successful post with engagement data logged to Done/.

**Acceptance Scenarios**:

1. **Given** user has created Pending_Approval/social_post_facebook.md with text content "Check out our latest project!" and image attachment, and social-media-browser-mcp has active Facebook session in .social_session/, **When** human approves the action item, **Then** @mcp-executor uses social-media-browser-mcp to post content to Facebook, moves file to Done/Social_Media_Posts/ with frontmatter added (posted_at timestamp, post_url, engagement_initial: 0), and creates confirmation notification in Dashboard.md.

2. **Given** user has created Pending_Approval/social_post_instagram.md with text and image, but Instagram session is expired (requires re-login), **When** @mcp-executor attempts to post, **Then** system detects authentication failure, gracefully degrades with error message "Instagram session expired - please re-login via social-media-browser-mcp skill", leaves action item in Pending_Approval/ with error note, logs failure to Done/ with failed_reason: "auth_expired", and provides clear re-login instructions.

3. **Given** user wants to post thread to Twitter/X with 5 tweets, **When** creating Pending_Approval/social_post_twitter.md, **Then** system validates thread format (each tweet < 280 chars, numbered 1/5, 2/5, etc.), creates single approval request for all tweets, upon approval posts sequentially via social-media-browser-mcp with 2-second delays between tweets to avoid rate limiting, and aggregates all tweet URLs in Done/ file with thread_summary: "5 tweets posted successfully".

4. **Given** user has scheduled 3 social posts for the week (Monday, Wednesday, Friday), **When** Monday arrives, **Then** system auto-moves Monday's post from Scheduled/ to Pending_Approval/ at 8:00 AM, sends notification "Social post ready for review: [title]", and human can approve immediately or snooze until later.

---

### User Story 3 - Xero Accounting Integration (Priority: P2)

As a business owner, I want my AI Employee to automatically sync financial data from Xero accounting system (invoices, payments, bank transactions) into my Obsidian vault, so that I always have current financial visibility without manual data entry and can make informed business decisions.

**Why this priority**: Eliminates manual bookkeeping, provides real-time financial visibility for CEO briefings. Medium priority because requires Xero account setup (not all users have Xero). Independently testable - can sync to Accounting/ without affecting other Gold tier features.

**Independent Test**: Can be fully tested by configuring Xero OAuth credentials in .env, running xero_watcher.py manually, verifying Accounting/Current_Month.md is populated with 3-5 sample transactions (invoices, payments, expenses), and confirming revenue totals match Xero dashboard.

**Acceptance Scenarios**:

1. **Given** user has configured Xero API credentials (client_id, client_secret, refresh_token) in .env and xero_watcher.py is running every 5 minutes, **When** Xero account receives 2 new invoices (INV-0010 for $1,500 from Client A, INV-0011 for $2,000 from Client B) and 1 payment of $800, **Then** xero_watcher detects new transactions via Xero API, creates/updates Accounting/Current_Month.md with revenue table showing 3 new entries with correct Date/Source/Amount/Status columns, calculates total revenue $4,300, and logs sync activity to logs/xero_watcher.log with deduplication (no duplicate entries for same invoice_id).

2. **Given** user runs weekly_audit.py for Monday CEO briefing, **When** Xero accounting data is present in Accounting/Current_Month.md, **Then** briefing integrates revenue data automatically - shows "Total Revenue: $4,300", "Revenue Sources: 3 transactions", "Month-to-Date: $4,300 (43% of $10,000 target)", and creates revenue trend visualization.

3. **Given** Xero refresh token expires after 60 days (Xero security requirement), **When** xero_watcher attempts API call, **Then** system detects 401 Unauthorized error, attempts token refresh using refresh_token, if successful saves new tokens to .xero_tokens.json and continues syncing, if refresh fails (token expired > 30 days) logs critical error "Xero token expired - please re-run setup_xero_oauth.py", stops syncing gracefully, and sends Dashboard.md notification requiring manual re-authentication.

---

### User Story 4 - Social Media Engagement Monitoring (Priority: P3)

As a business owner, I want my AI Employee to monitor my social media accounts for important interactions (comments, messages, mentions) and automatically create action items for high-priority engagement, so that I never miss client inquiries or urgent requests while filtering out low-value noise.

**Why this priority**: Nice-to-have feature for proactive customer service. Lowest priority because manual social media checking works for small businesses. Independently testable - can monitor one platform without full implementation.

**Independent Test**: Can be fully tested by running social_media_watcher.py with Facebook monitoring enabled, having 3 test interactions (1 client inquiry with "pricing" keyword, 1 generic comment, 1 spam), and verifying only 1 HIGH priority action item created in Needs_Action/ for the client inquiry.

**Acceptance Scenarios**:

1. **Given** social_media_watcher.py is running every 10 minutes with Facebook enabled, and Company_Handbook.md specifies HIGH priority keywords: "urgent, help, pricing, client", **When** Facebook page receives 5 new comments (1 with "pricing inquiry", 2 general questions, 2 spam), **Then** watcher filters interactions, creates 1 action item in Needs_Action/ for "pricing inquiry" comment with priority=HIGH, full comment text, commenter name, post URL, suggested response strategy based on handbook rules, and logs all 5 interactions to logs/social_media_watcher.log with priority scores.

2. **Given** watcher detects Instagram DM from business account @tech_corp asking "project quote for website redesign", **When** message contains business keyword "project" and "quote", **Then** system creates MEDIUM priority action item with message content, sender handle, timestamp, and pre-drafts response: "Hi! Thanks for reaching out. I'd be happy to provide a quote for your website redesign project. Could you share more details about scope, timeline, and budget?"

3. **Given** Twitter/X account receives 10 mentions in 1 hour (viral post), **When** this exceeds SOCIAL_TWITTER_MENTION_THRESHOLD=3, **Then** watcher creates "Viral Alert" action item with priority=HIGH, summary of viral activity (10 mentions in 1 hour, top tweets), suggested engagement strategy (reply to top 5 mentions, create thread), and aggregates engagement data for daily summary.

4. **Given** watcher has been running for 24 hours, **When** daily summary generation triggers at 6:00 PM, **Then** system generates Briefings/Social_Media_YYYY-MM-DD.md with platform-by-platform breakdown (Facebook: 5 new comments, 2 HIGH priority; Instagram: 3 DMs, 1 MEDIUM; Twitter: 15 mentions, 1 viral), total action items created, response rate tracking, and top performing posts by engagement.

---

### Edge Cases

- **What happens when** all three social media sessions expire simultaneously? System should create grouped "Re-authentication Required" action item listing all platforms needing login, with step-by-step re-login instructions for each platform.
- **How does system handle** Xero API rate limiting (60 requests/minute)? System implements exponential backoff, logs rate limit events, queues failed requests for retry after 60-second cooldown, and surfaces persistent rate limiting in CEO briefing as operational bottleneck.
- **What happens when** Monday briefing falls on public holiday? System checks holiday calendar in Company_Handbook.md, if holiday detected briefings generate on next business day (Tuesday) with note "Briefing delayed due to holiday", or user can configure BRIEFING_SKIP_HOLIDAYS=false in .env to force generation.
- **How does system handle** vault file corruption (malformed Business_Goals.md)? System validates YAML frontmatter before parsing, if corruption detected creates corrupted file backup with .bak extension, logs error with file path and line number, generates partial briefing with available data, and creates HIGH priority action item "Fix corrupted vault file: Business_Goals.md".
- **What happens when** social media post fails due to platform downtime (Facebook API error 500)? System retries with exponential backoff (3 attempts: 30s, 2m, 10m delays), after all retries fail creates action item in Done/ with failed_reason: "platform_downtime", post_url: null, and suggests manual posting via native app.
- **How does system handle** currency mismatches in Xero sync (some invoices in USD, others in EUR)? System reads Xero's currency code for each transaction, converts all amounts to base currency specified in Company_Handbook.md using exchange rate API, stores both original and converted amounts in Accounting/Current_Month.md, and notes conversion rate used.
- **What happens when** vault storage limit reached (Obsidian Sync quota exceeded)? System detects quota exceeded error, stops creating new files, creates CRITICAL alert in Dashboard.md, implements cleanup strategy (archive briefings older than 90 days to Archive/ folder), and provides storage breakdown by folder.
- **How does system handle** timezone differences for scheduled briefings? User configures BRIEFING_TIMEZONE in .env, system converts all times to user's local timezone for display, and stores UTC timestamps in ISO8601 format for consistency.

## Requirements *(mandatory)*

### Functional Requirements

**CEO Briefing Requirements:**

- **FR-001**: System MUST generate Monday Morning CEO Briefing every Monday at 7:00 AM (configurable via BRIEFING_DAY, BRIEFING_TIME, BRIEFING_TIMEZONE in .env)
- **FR-002**: System MUST read Business_Goals.md from vault root and extract revenue targets, key metrics, and active projects
- **FR-003**: System MUST analyze Accounting/Current_Month.md and calculate total revenue MTD, revenue by source, and month-over-month trend
- **FR-004**: System MUST analyze Tasks/Done/ and calculate total completed tasks, on-time completion rate, and overdue task count
- **FR-005**: System MUST detect bottlenecks by comparing task completion_date vs due_date and flag delays > BOTTLENECK_THRESHOLD_DAYS (default: 2 days)
- **FR-006**: System MUST identify cost optimization opportunities by analyzing Accounting/Current_Month.md for software subscriptions with no login in 30 days or cost increases > 20%
- **FR-007**: System MUST calculate health score (0-100) as weighted average of revenue progress (50%), operations score (50%), minus bottleneck penalty (-10 per bottleneck)
- **FR-008**: System MUST generate briefing document at Briefings/YYYY-MM-DD_Monday_Briefing.md with sections: Executive Summary, Revenue Analysis, Completed Tasks, Bottlenecks, Cost Optimization, Upcoming Deadlines, Proactive Suggestions, Action Items, Metrics Summary
- **FR-009**: System MUST update Dashboard.md with link to latest briefing, health score badge, and revenue progress indicator
- **FR-010**: System MUST generate ASCII revenue trend chart comparing current revenue to target with visual progress bar

**Social Media Posting Requirements:**

- **FR-011**: System MUST provide social-media-browser-mcp skill with MCP tools: post_to_facebook, post_to_instagram, post_to_twitter, get_engagement_summary, social_media_health_check
- **FR-012**: System MUST maintain persistent browser sessions in .social_session/ directory with separate context for each platform (Facebook, Instagram, Twitter/X)
- **FR-013**: System MUST support creating social post action items in Pending_Approval/ with frontmatter: platform, content_type (text/image/video), scheduled_date, status
- **FR-014**: System MUST require human approval via @mcp-executor agent before posting to social media (HITL validation)
- **FR-015**: System MUST post text content to Facebook page feed with support for image attachments and link previews
- **FR-016**: System MUST post text + image content to Instagram business account with automatic caption formatting and hashtag support
- **FR-017**: System MUST post to Twitter/X with support for threads (multiple tweets), character validation (< 280 chars per tweet), and image uploads
- **FR-018**: System MUST handle authentication failures gracefully by detecting session expiration, prompting re-login, and preserving pending posts for retry
- **FR-019**: System MUST move approved posts from Pending_Approval/ to Done/Social_Media_Posts/ with added frontmatter: posted_at (ISO8601), post_url, platform_post_id, engagement_initial
- **FR-020**: System MUST support scheduled posting by moving posts from Scheduled/ to Pending_Approval/ at configured time (default: 8:00 AM on post date)

**Xero Accounting Requirements:**

- **FR-021**: System MUST provide xero-accounting skill with option to use official Xero MCP server (https://github.com/XeroAPI/xero-mcp-server) or custom Python implementation
- **FR-022**: System MUST support Xero OAuth2 authentication with setup_xero_oauth.py script that opens browser for authorization and stores tokens in .xero_tokens.json
- **FR-023**: System MUST run xero_watcher.py every XERO_WATCHER_INTERVAL (default: 5 minutes) to poll Xero API for new transactions
- **FR-024**: System MUST sync invoices from Xero to Accounting/Current_Month.md with columns: Date, Source (Contact + Invoice ID), Amount, Status, Notes
- **FR-025**: System MUST sync bank transactions from Xero to Accounting/Current_Month.md expenses table with columns: Date, Category, Description, Amount, Account Code
- **FR-026**: System MUST implement deduplication based on transaction_id to prevent duplicate entries in accounting file
- **FR-027**: System MUST automatically refresh Xero access tokens using refresh_token before expiry (60-day lifetime) and save updated tokens to .xero_tokens.json
- **FR-028**: System MUST handle Xero API rate limiting (60 requests/minute) with exponential backoff and request queuing
- **FR-029**: System MUST generate financial summary for CEO briefing including revenue (week/month/YTD), expenses by category, and profit/loss
- **FR-030**: System MUST support multi-currency conversion if Xero account contains transactions in multiple currencies (convert to base currency specified in Company_Handbook.md)

**Social Media Monitoring Requirements (Optional Gold Tier):**

- **FR-031**: System MUST provide social-media-watcher skill that monitors Facebook, Instagram, Twitter/X for new interactions
- **FR-032**: System MUST check social platforms every SOCIAL_WATCHER_INTERVAL (default: 10 minutes) for new notifications
- **FR-033**: System MUST filter interactions by priority using keywords from Company_Handbook.md and environment variables (SOCIAL_HIGH_PRIORITY_KEYWORDS, SOCIAL_BUSINESS_KEYWORDS)
- **FR-034**: System MUST create action items in Needs_Action/ for HIGH and MEDIUM priority interactions with content, author, timestamp, and suggested response
- **FR-035**: System MUST generate daily engagement summaries at 6:00 PM saved to Briefings/Social_Media_YYYY-MM-DD.md
- **FR-036**: System MUST support engagement thresholds for alerts (SOCIAL_FB_REACTION_THRESHOLD=10, SOCIAL_IG_COMMENT_THRESHOLD=5, SOCIAL_TWITTER_MENTION_THRESHOLD=3)

**Cross-Domain Integration Requirements:**

- **FR-037**: System MUST integrate data from all Gold tier features into Monday CEO briefing (revenue from Xero, social metrics from watcher, tasks from existing Silver tier)
- **FR-038**: System MUST maintain Company_Handbook.md as single source of truth for business rules (social media response templates, accounting category mappings, priority keywords)
- **FR-039**: System MUST support graceful degradation - if one Gold tier feature fails (e.g., Xero sync error), other features continue operating and partial briefing is generated
- **FR-040**: System MUST log all operations to platform-specific log files (logs/weekly_audit.log, logs/social_media_watcher.log, logs/xero_watcher.log) with timestamp, log level, and context

### Key Entities *(include if feature involves data)*

- **Business_Goals**: Vault markdown file storing business objectives, revenue targets, key metrics with alert thresholds, active projects, and subscription audit rules. Frontmatter contains structured data (monthly_goal: 10000, metrics: [...]), main content contains narrative goals.

- **Monday_Briefing**: Generated markdown document in Briefings/ folder. Frontmatter: generated (ISO8601), period (date range), week_number (1-52). Content sections: Executive Summary, Revenue, Completed Tasks, Bottlenecks, Cost Optimization, Action Items. Includes calculated fields: health_score (0-100), revenue_progress (%), on_time_rate (%).

- **Social_Post_Action**: Markdown file in Pending_Approval/ or Done/Social_Media_Posts/. Frontmatter: platform (facebook|instagram|twitter), content_type (text|image|video), status (pending|approved|posted|failed), scheduled_date (ISO8601), posted_at (ISO8601, null if pending), post_url (null if pending/failed), platform_post_id (null if pending/failed). Content: Post text, image paths, hashtags, mention handles.

- **Accounting_Entry**: Row in Accounting/Current_Month.md markdown table. Fields: Date (YYYY-MM-DD), Source (Contact + Description), Amount (decimal), Status (Paid/Draft/Pending), Notes (optional). For expenses: Category (Software/Hosting/Services), Account Code (Xero account code).

- **Xero_Token**: JSON object in .xero_tokens.json. Fields: access_token (string, expires 30 min), refresh_token (string, expires 60 days), tenant_id (string, Xero organization ID), expires_at (ISO8601), token_type: "Bearer".

- **Social_Media_Interaction**: Detected by social-media-watcher. Fields: platform (facebook|instagram|twitter), interaction_type (comment|message|mention), author_name, author_handle, content (text), timestamp (ISO8601), post_url, priority (HIGH|MEDIUM|LOW), detected_keywords ([]), suggested_response (string).

- **Engagement_Summary**: Daily report in Briefings/Social_Media_YYYY-MM-DD.md. Frontmatter: generated_date (ISO8601), platforms ([]). Content: Platform-by-platform breakdown (new comments count, new messages count, new mentions count, priority breakdown), total action items created, top performing posts by engagement, response rate tracking.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Monday Morning CEO Briefing generates successfully within 30 seconds on configured day/time, with all required sections populated (Executive Summary, Revenue, Completed Tasks, Bottlenecks, Cost Optimization, Action Items), measured by automated test running weekly_audit.py against test vault with sample data.

- **SC-002**: CEO Briefing health score calculation produces accurate score (0-100) matching manual calculation formula: health_score = (revenue_progress * 0.5 + on_time_rate * 0.5) - (bottleneck_count * 10), validated by test suite with 10 sample scenarios.

- **SC-003**: Xero accounting watcher syncs new transactions within 5 minutes of occurrence (XERO_WATCHER_INTERVAL=300), measured by creating test invoice in Xero and verifying appearance in Accounting/Current_Month.md with correct amount, contact, and status.

- **SC-004**: Social media posting completes successfully within 60 seconds for Facebook text+image post, 90 seconds for Instagram post (image upload slower), and 45 seconds for Twitter/X tweet, measured by end-to-end timing from approval to Done/ file creation.

- **SC-005**: Social media watcher detects and prioritizes interactions with 95% accuracy, measured by test suite with 100 sample interactions (50 HIGH priority, 30 MEDIUM, 20 LOW) and verifying correct priority assignment based on keyword matching rules.

- **SC-006**: System achieves graceful degradation when components fail - if Xero API is down, CEO briefing still generates with partial data (revenue section shows "Xero sync unavailable"), measured by simulating Xero API failure and verifying briefing generation continues.

- **SC-007**: Session persistence maintains login state across browser restarts - social media platforms remain logged in for minimum 7 days without re-authentication, measured by logging in once, restarting machine after 24 hours, and verifying posting still works without new login.

- **SC-008**: Human-in-the-loop (HITL) approval workflow prevents unauthorized external actions - 100% of social media posts and Xero invoice creations require explicit human approval before execution, measured by code inspection and integration test attempting to post without approval.

- **SC-009**: Cost optimization recommendations identify minimum 3 cost-saving opportunities per month in test scenarios with sample subscription data, measured by creating 10 test subscriptions (3 unused, 2 with >20% cost increase, 5 normal) and verifying all 5 problematic subscriptions flagged.

- **SC-010**: CEO briefing action items are actionable and specific - each action item includes clear success criteria and owner assignment (CEO/AI Employee), measured by manual review of 5 consecutive briefings and rating specificity on 1-5 scale (target: 4+ average).

- **SC-011**: Social media posting handles authentication failures with clear error messages - user can successfully re-authenticate and retry post within 5 minutes following on-screen instructions, measured by user testing with expired sessions and timing to successful post.

- **SC-012**: Multi-platform social posting supports thread formatting for Twitter/X - threads of 5+ tweets post sequentially with 2-second delays, all tweets succeed, and Done/ file aggregates all tweet URLs, measured by test thread of 7 tweets.

- **SC-013**: Xero token refresh succeeds automatically before expiry - system detects token expiry within 24-hour window before expiration, refreshes without user intervention, and continues syncing without interruption, measured by monitoring tokens over 60-day cycle in test environment.

- **SC-014**: Briefing generation handles vault data corruption gracefully - if Business_Goals.md has malformed YAML, system creates .bak backup, logs error, and generates partial briefing with available data, measured by injecting malformed YAML and verifying graceful handling.

- **SC-015**: Social media watcher engagement summaries generate within 10 seconds at 6:00 PM daily, include all platform interactions from past 24 hours with correct counts and priority breakdown, measured by automated test injecting known interactions and verifying summary accuracy.

- **SC-016**: System maintains cross-domain data consistency - revenue figures in CEO briefing match Xero accounting data within 0.01% tolerance, measured by comparing briefing totals to Xero dashboard across 5 test months.

- **SC-017**: Log files capture sufficient debugging information - all failures include timestamp, error message, stack trace, and context (vault path, file names, API endpoints), measured by code review of logging statements and simulated failure scenarios.

- **SC-018**: User can configure all time-sensitive operations (briefing schedule, watcher intervals, posting times) via .env file without code changes, measured by modifying BRIEFING_TIMEZONE, BRIEFING_TIME, XERO_WATCHER_INTERVAL and verifying system respects new values.

- **SC-019**: System documentation enables new user to complete setup (Xero OAuth, social media login, briefing configuration) within 60 minutes following SKILL.md instructions, measured by user testing with 5 new users on fresh machines.

- **SC-020**: Gold tier features integrate seamlessly with existing Silver tier infrastructure - Silver tier agents (@needs-action-triage, @mcp-executor) work with Gold tier action items without modification, measured by running existing Silver tier tests with Gold tier action items.

## Assumptions

1. **User has Obsidian vault**: All Gold tier features assume user has existing Obsidian vault at path specified by --vault-path argument. System does not create vault if missing.

2. **Xero account availability**: Xero accounting integration is optional - if user does not have Xero account, CEO briefing will show "No accounting data found" and other features continue normally.

3. **Social media business accounts**: Facebook, Instagram, Twitter/X posting requires business/professional accounts (not personal accounts). User must have admin access to Facebook Page, Instagram Business Account, Twitter/X profile.

4. **Browser automation permissions**: Social media posting via Playwright requires user to run browser login process at least once per platform. System does not bypass platform authentication or terms of service.

5. **Network connectivity**: All Gold tier features (Xero API, social media posting, social monitoring) require active internet connection. System handles network failures gracefully but cannot function offline.

6. **Platform API stability**: Social media platforms may change UI/DOM structure requiring updates to social-media-browser-mcp selectors. System is designed to detect failures and prompt for updates but cannot prevent breaking changes from platforms.

7. **Gold tier dependencies**: Gold tier builds on Silver tier foundation - requires Silver tier agents (@needs-action-triage, @mcp-executor), vault structure (Needs_Action/, Pending_Approval/, Done/), and Company_Handbook.md to be fully functional.

8. **User timezone configuration**: All scheduling (briefings, social posting, summaries) assumes user configures BRIEFING_TIMEZONE correctly in .env. System defaults to UTC if not specified.

9. **Hardware requirements**: Browser automation for social media requires minimum 4GB RAM available for Playwright contexts. System may fail gracefully on resource-constrained machines.

10. **Data privacy compliance**: User is responsible for ensuring social media posting and Xero syncing comply with their business's data privacy policies (GDPR, CCPA). System does not include built-in compliance features.

## Technical Context

**Architecture:**

Gold tier extends Silver tier architecture with four major components:

1. **Monday Morning CEO Briefing** (weekly-ceo-briefing skill)
   - Orchestrator: scripts/weekly_audit.py
   - Analysis modules: revenue_analyzer.py, bottleneck_detector.py, cost_optimizer.py
   - Output: Briefings/YYYY-MM-DD_Monday_Briefing.md
   - Schedule: Cron/Task Scheduler every Monday at 7:00 AM

2. **Social Media Posting** (social-media-browser-mcp skill)
   - MCP Server: FastMCP with tools: post_to_facebook, post_to_instagram, post_to_twitter
   - Browser Automation: Playwright with persistent contexts in .social_session/
   - Session Management: CDP (Chrome DevTools Protocol) on port 9223 (distinct from WhatsApp's 9222)
   - Approval Workflow: Creates Pending_Approval/social_post_*.md, executes via @mcp-executor

3. **Xero Accounting** (xero-accounting skill)
   - API Client: Official Xero MCP server OR custom Python implementation
   - Watcher: scripts/xero_watcher.py polling every 5 minutes
   - OAuth2: scripts/setup_xero_oauth.py for initial authentication
   - Token Storage: .xero_tokens.json (gitignored)
   - Sync Target: Accounting/Current_Month.md

4. **Social Media Monitoring** (social-media-watcher skill, optional)
   - Watcher: scripts/social_media_watcher.py polling every 10 minutes
   - Platform Monitors: facebook_monitor.py, instagram_monitor.py, twitter_monitor.py
   - Priority Filtering: Keyword-based (HIGH/MEDIUM/LOW)
   - Action Item Creation: Needs_Action/ for important interactions
   - Daily Summaries: Briefings/Social_Media_YYYY-MM-DD.md

**Integration Points:**

- **Silver Tier Agents**: @needs-action-triage processes Gold tier action items (social posts, engagement alerts), @mcp-executor executes Gold tier MCP tools
- **Vault Structure**: Gold tier creates new folders (Briefings/, Accounting/, Done/Social_Media_Posts/) within existing vault
- **Company_Handbook.md**: Gold tier reads business rules from existing handbook (social media response templates, priority keywords, accounting categories)
- **Dashboard.md**: Gold tier updates dashboard with latest briefing links, health scores, social media metrics
- **Multi-Watcher Orchestrator**: Gold tier watchers (xero_watcher, social_media_watcher) integrate with existing Silver tier watcher orchestration (whatsapp_watcher, email_watcher)

**Data Flow:**

```
External Data Sources
├── Xero API → xero_watcher → Accounting/Current_Month.md
├── Facebook/IG/Twitter → social_media_watcher → Needs_Action/ → Briefings/Social_Media_*.md
└── Human Input → Pending_Approval/social_post_*.md

Processing
├── weekly_audit.py reads: Business_Goals.md, Accounting/, Tasks/Done/, Briefings/Social_Media_*.md
├── Analyzes: Revenue, Bottlenecks, Cost Optimization, Social Engagement
└── Generates: Briefings/YYYY-MM-DD_Monday_Briefing.md

Action Execution
├── @needs-action-triage processes: Needs_Action/ social interactions
├── @mcp-executor executes: social-media-browser-mcp tools (post_to_*)
└── Results logged to: Done/Social_Media_Posts/
```

**Technology Stack:**

- **MCP Protocol**: Model Context Protocol for tool integration (FastMCP Python framework)
- **Browser Automation**: Playwright (Python sync API) with persistent contexts
- **OAuth2**: Xero authentication using authorization code flow with PKCE
- **Scheduling**: Platform-specific (cron on Linux/Mac, Task Scheduler on Windows)
- **Data Storage**: Obsidian vault (markdown files with YAML frontmatter), JSON for tokens
- **Logging**: Python logging module to platform-specific log files

## Security & Privacy

**Session Management:**

- Social media browser sessions stored in .social_session/ directory (gitignored)
- Xero OAuth tokens stored in .xero_tokens.json (gitignored)
- Sessions persist for 7-60 days depending on platform policies
- No credentials in code or vault - only in .env file and gitignored files

**Human-in-the-Loop (HITL) Approval:**

- ALL external actions (social posting, Xero invoice creation) require human approval
- Approval workflow: Pending_Approval/ → human review → @mcp-executor execution → Done/
- No autonomous posting without explicit approval
- Approval recorded in action item frontmatter (approved_by: "human", approved_at: timestamp)

**Data Minimization:**

- Social media watcher only collects: post URL, author name, comment text, timestamp (no personal data beyond public profile)
- Xero sync only collects: transaction date, amount, contact name, invoice ID (no sensitive payment details)
- Briefings only include: aggregated metrics (no raw transaction details in executive summary)

**Audit Trail:**

- All external actions logged to Done/ with full execution context
- Log files include: timestamp, action type, success/failure, error details
- Dashboard.md updated with activity summaries for transparency

**Access Control:**

- All Gold tier features respect existing Silver tier access controls (single-user vault)
- No multi-user authentication - assumes single user on local machine
- API tokens (Xero, social platforms) stored locally and never transmitted except to respective APIs

## Error Recovery

**Social Media Posting Failures:**

- **Authentication Failure**: Detect expired session → create "Re-authentication Required" action item → preserve post in Pending_Approval/ → provide re-login instructions → retry on approval
- **Platform Downtime**: Retry with exponential backoff (3 attempts: 30s, 2m, 10m) → if all fail, move to Done/ with failed_reason: "platform_downtime" → suggest manual posting
- **Rate Limiting**: Detect rate limit response (HTTP 429) → calculate retry-after from headers → queue request → retry after cooldown
- **Content Validation**: Pre-validate content before posting (Twitter character count < 280, image file exists, text not empty) → reject invalid content with specific error message → no retry until fixed

**Xero Sync Failures:**

- **Token Refresh Failure**: Attempt token refresh → if successful continue, if failed (401) → log critical error → stop syncing → create "Xero Authentication Failed" action item → require manual re-auth via setup_xero_oauth.py
- **API Rate Limit**: Detect HTTP 429 → extract retry-after from response headers → queue failed requests → resume after cooldown → log rate limit events
- **Network Timeout**: Retry with exponential backoff (3 attempts: 5s, 30s, 2m) → if all fail → log error → skip sync cycle → retry on next scheduled cycle
- **Malformed Data**: Skip transactions with missing required fields (date, amount, contact) → log skipped transactions with reason → continue syncing valid data → create action item "Review skipped Xero transactions"

**Briefing Generation Failures:**

- **Missing Data Sources**: Generate partial briefing with available data → add warnings for missing sources (e.g., "No revenue targets set - configure Business_Goals.md") → log missing data → create action item to configure missing sources
- **Vault File Corruption**: Validate YAML frontmatter before parsing → if malformed → create .bak backup → log error with file path and line number → use default values for corrupted data → create action item to fix corrupted file
- **Calculation Errors**: Wrap calculations in try-except → if calculation fails (e.g., divide by zero) → use safe defaults (0 for missing values) → log calculation error → add note to briefing: "Some calculations failed - see logs"
- **File Write Failure**: If Briefings/ directory not writable → log error → attempt to create Briefings/ directory → if fails → write to /tmp/ as fallback → create critical action item to fix vault permissions

**Graceful Degradation:**

- Each Gold tier feature operates independently - failure in one does not break others
- CEO briefing includes data from all available sources - if Xero fails, still generates briefing with task data and social metrics
- Social posting failures don't affect social monitoring (separate watchers)
- All errors logged with context for debugging
- Dashboard.md updated with system health status (all features operational, some degraded, critical failures)

## Testing Strategy

**Unit Testing:**

- **weekly_audit.py modules**: Test revenue_analyzer, bottleneck_detector, cost_optimizer with mock vault data
- **Xero sync**: Test transaction parsing, deduplication, currency conversion with mock API responses
- **Social media watcher**: Test priority filtering, keyword matching, action item creation with sample interactions
- **Health score calculation**: Test edge cases (zero revenue, zero tasks, negative delays) with test fixtures

**Integration Testing:**

- **CEO briefing end-to-end**: Create test vault with Business_Goals.md, Accounting/, Tasks/Done/ → run weekly_audit.py → verify briefing generated with correct calculations
- **Social posting workflow**: Create Pending_Approval/social_post.md → approve → verify post created via social-media-browser-mcp → verify Done/ file created with post_url
- **Xero sync workflow**: Mock Xero API with test transactions → run xero_watcher.py → verify Accounting/Current_Month.md updated → verify deduplication works
- **Cross-domain integration**: Verify CEO briefing includes Xero revenue data, social engagement metrics, task completion stats

**Manual Testing:**

- **Browser login**: Test social media login flow for each platform (Facebook, Instagram, Twitter/X) → verify session persists across browser restarts
- **Human approval workflow**: Create action item → approve → verify execution → reject → verify no execution
- **Error recovery**: Simulate failures (expired session, network timeout, rate limit) → verify graceful handling and recovery
- **Configuration**: Test all .env variables (BRIEFING_TIMEZONE, XERO_WATCHER_INTERVAL, SOCIAL_HIGH_PRIORITY_KEYWORDS) → verify system respects config

**Performance Testing:**

- **Briefing generation time**: Measure time to generate briefing with 1000 completed tasks, 500 transactions, 200 social interactions → target: < 30 seconds
- **Xero sync latency**: Create test invoice in Xero → measure time to appear in Accounting/ → target: < 5 minutes (XERO_WATCHER_INTERVAL)
- **Social posting latency**: Measure time from approval to successful post for each platform → target: < 60 seconds (FB), < 90 seconds (IG), < 45 seconds (Twitter)

**Acceptance Testing:**

- Test each user story acceptance scenario individually
- Verify all success criteria (SC-001 through SC-020) pass
- Conduct end-to-end test: Run full Gold tier system for 1 week with realistic data → verify all features work correctly
- User acceptance testing: 5 users test setup process following SKILL.md → measure time to complete setup (target: < 60 minutes)

**Test Data Management:**

- Create test vault fixtures with sample Business_Goals.md, Accounting/, Tasks/Done/
- Mock Xero API responses for test transactions (invoices, payments, expenses)
- Mock social media API responses for test posts and interactions
- Clean up test data after each test run
- Use test Xero organization (sandbox environment) for integration testing

## References

- **HACKATHON-ZERO.md**: Lines 183-198 (Gold Tier requirements), Lines 533-656 (CEO Briefing templates)
- **Silver Tier Spec**: specs/002-silver-tier-ai-employee/spec.md (reference for specification structure, Silver tier architecture to build upon)
- **social-media-browser-mcp**: .claude/skills/social-media-browser-mcp/SKILL.md (browser automation patterns, session management)
- **weekly-ceo-briefing**: .claude/skills/weekly-ceo-briefing/SKILL.md (briefing architecture, data sources, output format)
- **xero-accounting**: .claude/skills/xero-accounting/SKILL.md (Xero OAuth2 flow, API integration patterns)
- **social-media-watcher**: .claude/skills/social-media-watcher/SKILL.md (priority filtering, engagement monitoring)
- **Demo-Hack Reference**: demo-hack/ implementation for WhatsApp watcher (Playwright pattern), LinkedIn REST API v2 (official API vs browser automation tradeoffs)
