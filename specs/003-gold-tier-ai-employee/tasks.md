# Tasks: Gold Tier AI Employee

**Input**: Design documents from `/specs/003-gold-tier-ai-employee/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks are included as Gold Tier requires comprehensive testing per Constitution Principle VII.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Skills-based architecture**: `.claude/skills/[skill-name]/`
- **Scripts**: `.claude/skills/[skill-name]/scripts/`
- **Tests**: `.claude/skills/[skill-name]/tests/`
- **Vault**: `AI_Employee_Vault/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Skill initialization and dependency installation

- [X] T001 Create skill directory structures for 4 Gold tier skills (.claude/skills/social-media-browser-mcp/, .claude/skills/weekly-ceo-briefing/, .claude/skills/xero-accounting/, .claude/skills/social-media-watcher/)
- [X] T002 Initialize pyproject.toml for social-media-browser-mcp skill with dependencies: fastmcp, playwright, pydantic
- [X] T003 Initialize pyproject.toml for weekly-ceo-briefing skill with dependencies: python-frontmatter, pyyaml
- [X] T004 Initialize pyproject.toml for xero-accounting skill with dependencies: requests, python-frontmatter
- [X] T005 Initialize pyproject.toml for social-media-watcher skill with dependencies: python-frontmatter
- [X] T006 [P] Install Playwright browsers for social media automation (playwright install chromium)
- [X] T007 [P] Create test directories for all 4 skills (tests/ folder in each skill)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create shared error handling utility in scripts/shared/error_handler.py with exponential backoff decorator (max 3 retries, 1s/2s/4s delays)
- [X] T009 [P] Create vault operations utility in scripts/shared/vault_ops.py with functions: read_markdown, write_markdown, move_to_done, validate_frontmatter
- [X] T010 [P] Create YAML frontmatter validator in scripts/shared/frontmatter_validator.py with Pydantic models for common vault metadata
- [X] T011 Create audit logging utility in scripts/shared/audit_logger.py with credential sanitization (redact tokens, passwords)
- [X] T012 [P] Create environment configuration loader in scripts/shared/config.py that reads .env and validates required variables
- [X] T013 Add .env.example template to project root with all Gold tier environment variables documented
- [X] T014 Update .gitignore to exclude: .env, .social_session/, .xero_tokens.json, Logs/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Monday Morning CEO Briefing (Priority: P1) 🎯 MVP

**Goal**: Automated Monday morning business audit with health scores, revenue analysis, bottleneck detection, and cost optimization opportunities

**Independent Test**: Create test vault with Business_Goals.md ($10,000 target), Accounting/Current_Month.md ($4,500 MTD revenue, 5 transactions), Tasks/Done/ (12 completed, 2 overdue). Run weekly_audit.py and verify Briefings/YYYY-MM-DD_Monday_Briefing.md contains: executive summary, health score 75/100, bottleneck table with 2 delayed tasks, cost optimization section, action items.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T015 [P] [US1] Unit test for health score calculation in weekly-ceo-briefing/tests/test_health_score.py (test edge cases: zero revenue, negative delays, division by zero)
- [X] T016 [P] [US1] Unit test for revenue parsing from markdown tables in weekly-ceo-briefing/tests/test_revenue_analyzer.py (test Accounting/Current_Month.md parsing, amount extraction, total calculation)
- [X] T017 [P] [US1] Unit test for bottleneck detection in weekly-ceo-briefing/tests/test_bottleneck_detector.py (test delay calculation, severity classification, top 5 sorting)
- [X] T018 [P] [US1] Integration test for briefing generation with graceful degradation in weekly-ceo-briefing/tests/test_briefing_generation.py (test missing Business_Goals.md, empty Accounting/, corrupted YAML)
- [X] T019 [US1] End-to-end test for complete briefing workflow in weekly-ceo-briefing/tests/test_briefing_e2e.py (test vault with sample data, verify all sections generated, validate health score formula)

### Implementation for User Story 1

- [X] T020 [P] [US1] Create revenue_analyzer.py module in weekly-ceo-briefing/scripts/ with RevenueAnalyzer class and methods: load_business_goals, analyze_revenue, calculate_mtd, extract_transactions
- [X] T021 [P] [US1] Create bottleneck_detector.py module in weekly-ceo-briefing/scripts/ with BottleneckDetector class and methods: analyze_completed_tasks, detect_delays, calculate_severity, rank_bottlenecks
- [X] T022 [P] [US1] Create cost_optimizer.py module in weekly-ceo-briefing/scripts/ with CostOptimizer class and methods: analyze_subscriptions, detect_unused_tools, calculate_savings, flag_cost_increases
- [X] T023 [US1] Implement WeeklyAuditGenerator orchestrator in weekly-ceo-briefing/scripts/weekly_audit.py with methods: __init__, generate_briefing, _generate_briefing_content, _calculate_health_score
- [X] T024 [US1] Add Business_Goals.md parsing in weekly_audit.py load_business_goals method (extract frontmatter: monthly_goal, metrics, active_projects, audit_rules)
- [X] T025 [US1] Add Accounting/Current_Month.md parsing in weekly_audit.py analyze_revenue method (parse revenue table, calculate totals, extract transaction details)
- [X] T026 [US1] Add Tasks/Done/ analysis in weekly_audit.py analyze_completed_tasks method (count completed, calculate on-time rate, identify overdue)
- [X] T027 [US1] Implement health score calculation in weekly_audit.py _calculate_health_score method (formula: revenue_progress * 0.5 + on_time_rate * 0.5 - bottleneck_count * 10)
- [X] T028 [US1] Implement graceful degradation in weekly_audit.py generate_briefing method (try-except around each data source, generate partial briefing with warnings for missing sources)
- [X] T029 [US1] Add briefing markdown generation in weekly_audit.py _generate_briefing_content method (sections: Executive Summary, Revenue, Completed Tasks, Bottlenecks, Cost Optimization, Action Items, Notes)
- [X] T030 [US1] Create CLI entry point in weekly-ceo-briefing/scripts/weekly_audit.py main function with argparse for --vault-path argument
- [X] T031 [US1] Add Dashboard.md update in weekly_audit.py generate_briefing method (append latest briefing link, health score badge, revenue progress)
- [X] T032 [US1] Add logging to weekly_audit.py all methods (use scripts/shared/audit_logger.py, log data source loading, calculation steps, warnings)
- [X] T033 [US1] Create Business_Goals.md template in weekly-ceo-briefing/templates/Business_Goals.md with example frontmatter and structure
- [X] T034 [US1] Create Accounting/Current_Month.md template in weekly-ceo-briefing/templates/Accounting_Current_Month.md with revenue and expenses table examples

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Social Media Cross-Posting (Priority: P2)

**Goal**: Browser automation for Facebook, Instagram, Twitter/X posting with persistent sessions and HITL approval workflow

**Independent Test**: Install social-media-browser-mcp skill, run login_facebook.py to authenticate, create Pending_Approval/social_post_facebook.md with text content, move to Approved/, verify @mcp-executor posts to Facebook within 60 seconds, file moved to Done/Social_Media_Posts/ with post_url and posted_at timestamp.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T035 [P] [US2] Unit test for MCP tool schema validation in social-media-browser-mcp/tests/test_mcp_tools.py (test Pydantic v2 validation for post_to_facebook, post_to_instagram, post_to_twitter inputs)
- [X] T036 [P] [US2] Unit test for session persistence in social-media-browser-mcp/tests/test_session_persistence.py (test browser context saves/loads from .social_session/, verify cookies persist across restarts)
- [X] T037 [P] [US2] Integration test for HITL approval workflow in social-media-browser-mcp/tests/test_approval_workflow.py (test Pending_Approval → Approved → execution → Done/)
- [X] T038 [P] [US2] Unit test for authentication error handling in social-media-browser-mcp/tests/test_auth_errors.py (test session expiration detection, error messages, re-login prompts)
- [X] T039 [US2] End-to-end test for Facebook posting in social-media-browser-mcp/tests/test_facebook_e2e.py (test login → create post → approve → verify post on Facebook → check Done/ file)

### Implementation for User Story 2

- [X] T040 [P] [US2] Create FastMCP server in social-media-browser-mcp/scripts/social_browser_mcp.py with FastMCP(name="social-browser-mcp") initialization
- [X] T041 [P] [US2] Implement Playwright context manager in social-media-browser-mcp/scripts/social_browser_mcp.py with SocialMediaBrowser class and methods: __init__, start, stop, get_context (supports separate contexts for FB/IG/Twitter with unique CDP ports 9223/9224/9225)
- [X] T042 [P] [US2] Create Facebook login helper in social-media-browser-mcp/scripts/login_facebook.py (opens browser to Facebook login, saves session to .social_session/facebook/)
- [X] T043 [P] [US2] Create Instagram login helper in social-media-browser-mcp/scripts/login_instagram.py (opens browser to Instagram login, saves session to .social_session/instagram/)
- [X] T044 [P] [US2] Create Twitter login helper in social-media-browser-mcp/scripts/login_twitter.py (opens browser to Twitter/X login, saves session to .social_session/twitter/)
- [ ] T045 [US2] Implement post_to_facebook MCP tool in social-media-browser-mcp/scripts/social_browser_mcp.py with async function post_to_facebook(text: str, image_path: str = None) -> dict (navigate to page, find composer, type text, upload image if provided, click post, extract post_url)
- [ ] T046 [US2] Implement post_to_instagram MCP tool in social-media-browser-mcp/scripts/social_browser_mcp.py with async function post_to_instagram(text: str, image_path: str) -> dict (validate image required, navigate to create post, upload image, add caption, click share, extract post_url)
- [ ] T047 [US2] Implement post_to_twitter MCP tool in social-media-browser-mcp/scripts/social_browser_mcp.py with async function post_to_twitter(tweets: list[dict]) -> dict (validate each tweet < 280 chars, post sequentially with 2s delays, aggregate all tweet URLs)
- [ ] T048 [US2] Add authentication error detection in social-media-browser-mcp/scripts/social_browser_mcp.py (detect login prompts, session expired messages, raise auth_expired error with clear message)
- [ ] T049 [US2] Implement retry logic with exponential backoff in social-media-browser-mcp/scripts/social_browser_mcp.py (3 attempts: 30s/2m/10m delays, use scripts/shared/error_handler.py decorator)
- [ ] T050 [US2] Add session health check in social-media-browser-mcp/scripts/social_browser_mcp.py with social_media_health_check tool (verify all platforms authenticated, return session age hours, list platforms needing re-auth)
- [ ] T051 [US2] Add engagement summary retrieval in social-media-browser-mcp/scripts/social_browser_mcp.py with get_engagement_summary tool (query likes/comments/shares for recent posts)
- [ ] T052 [US2] Create Done/Social_Media_Posts/ folder structure in vault_ops.py move_to_done function (move approved posts from Approved/ to Done/Social_Media_Posts/ with added frontmatter: posted_at, post_url, platform_post_id, engagement_initial)
- [ ] T053 [US2] Integrate with @mcp-executor agent in social-media-browser-mcp/SKILL.md (document MCP server registration, tool usage examples, error handling)
- [ ] T054 [US2] Add scheduling support in social-media-browser-mcp/scripts/ (move posts from Scheduled/ to Pending_Approval/ at configured time, default 8:00 AM)
- [ ] T055 [US2] Add logging to all MCP tools in social-media-browser-mcp/scripts/social_browser_mcp.py (use scripts/shared/audit_logger.py, log execution attempts, success/failure, post URLs)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Xero Accounting Integration (Priority: P2)

**Goal**: Automatic sync of Xero financial data (invoices, payments, bank transactions) to Accounting/Current_Month.md with token refresh and multi-currency support

**Independent Test**: Configure Xero OAuth credentials in .env, run setup_xero_oauth.py to authenticate, manually create 3 invoices in Xero, run xero_watcher.py, verify Accounting/Current_Month.md populated with 3 transactions (correct Date/Source/Amount/Status), run weekly_audit.py and verify briefing includes Xero revenue data.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T056 [P] [US3] Unit test for OAuth2 token refresh in xero-accounting/tests/test_token_refresh.py (mock Xero API 401 response, verify refresh_token used, new tokens saved to .xero_tokens.json)
- [ ] T057 [P] [US3] Unit test for transaction deduplication in xero-accounting/tests/test_xero_sync.py (mock 2 sync calls with same invoice_id, verify only 1 entry in Accounting/)
- [ ] T058 [P] [US3] Unit test for multi-currency conversion in xero-accounting/tests/test_currency_conversion.py (mock EUR invoice, verify conversion to USD, store both amounts in Accounting/)
- [ ] T059 [P] [US3] Integration test for Xero API error handling in xero-accounting/tests/test_api_errors.py (mock rate limiting 429, network timeout, verify exponential backoff and retry logic)
- [ ] T060 [US3] End-to-end test for Xero sync workflow in xero-accounting/tests/test_xero_e2e.py (mock Xero sandbox with test invoices, run xero_watcher, verify Accounting/ updated, verify briefing integration)

### Implementation for User Story 3

- [ ] T061 [P] [US3] Create Xero API client in xero-accounting/scripts/xero_api_client.py with XeroClient class and methods: __init__ (load tokens from .xero_tokens.json), get_invoices, get_bank_transactions, refresh_token, make_request (with retry logic)
- [ ] T062 [P] [US3] Implement OAuth2 setup script in xero-accounting/scripts/setup_xero_oauth.py (opens browser for Xero authorization, exchanges auth code for tokens, saves to .xero_tokens.json)
- [ ] T063 [P] [US3] Create Xero watcher in xero-accounting/scripts/xero_watcher.py with XeroWatcher class and methods: __init__, sync_invoices, sync_bank_transactions, update_accounting_file, run (polling loop with XERO_WATCHER_INTERVAL)
- [ ] T064 [P] [US3] Implement invoice sync in xero-accounting/scripts/xero_watcher.py sync_invoices method (call Xero API, extract InvoiceID, Contact, Date, Total, Status, append to Accounting/Current_Month.md revenue table)
- [ ] T065 [P] [US3] Implement bank transaction sync in xero-accounting/scripts/xero_watcher.py sync_bank_transactions method (call Xero API, extract Date, Category, Description, Amount, AccountCode, append to Accounting/Current_Month.md expenses table)
- [ ] T066 [P] [US3] Add deduplication logic in xero-accounting/scripts/xero_watcher.py (track synced InvoiceID and BankTransactionID in .xero_sync_state.json, skip already-synced transactions)
- [ ] T067 [US3] Implement token refresh in xero-accounting/scripts/xero_api_client.py refresh_token method (detect 401 error, call Xero token endpoint with refresh_token, update .xero_tokens.json with new access_token and refresh_token)
- [ ] T068 [US3] Add multi-currency support in xero-accounting/scripts/xero_watcher.py (read currency code from Xero transaction, call exchange rate API, convert to base currency from Company_Handbook.md, store both original and converted amounts)
- [ ] T069 [US3] Implement accounting file update in xero-accounting/scripts/xero_watcher.py update_accounting_file method (use scripts/shared/vault_ops.py write_markdown, validate YAML frontmatter, preserve existing entries, append new transactions)
- [ ] T070 [US3] Add rate limiting handling in xero-accounting/scripts/xero_api_client.py make_request method (detect HTTP 429, extract retry-after header, queue request, retry after cooldown, log rate limit events)
- [ ] T071 [US3] Add error handling in xero-accounting/scripts/xero_watcher.py (wrap API calls in try-except, log errors, continue syncing on single failure, create action item in Needs_Action/ for manual intervention if sync fails)
- [ ] T072 [US3] Create CLI entry point in xero-accounting/scripts/xero_watcher.py main function with argparse for --vault-path argument
- [ ] T073 [US3] Add accounting audit module in xero-accounting/scripts/accounting_audit.py with functions: generate_financial_summary (calculate revenue/expenses/profit for week/month/YTD), analyze_expenses_by_category
- [ ] T074 [US3] Integrate Xero data into CEO briefing in weekly-ceo-briefing/scripts/weekly_audit.py (modify analyze_revenue method to read Accounting/Current_Month.md populated by xero_watcher, include revenue sources, totals, trend in briefing)
- [ ] T075 [US3] Add logging to all Xero operations in xero-accounting/scripts/ (use scripts/shared/audit_logger.py, log sync cycles, API calls, token refreshes, currency conversions with rates used)
- [ ] T076 [US3] Create Accounting/Current_Month.md template in xero-accounting/templates/Accounting_Current_Month.md with revenue and expenses table structure matching Xero sync output

**Checkpoint**: All user stories should now be independently functional (US1, US2, US3)

---

## Phase 6: User Story 4 - Social Media Engagement Monitoring (Priority: P3)

**Goal**: Monitor Facebook/Instagram/Twitter for comments/messages/mentions, create action items for HIGH/MEDIUM priority interactions, generate daily engagement summaries

**Independent Test**: Configure Company_Handbook.md with HIGH priority keywords ("urgent, help, pricing, client"), run social_media_watcher.py with Facebook enabled, simulate 5 new comments (1 with "pricing inquiry", 2 general, 2 spam), verify 1 HIGH priority action item created in Needs_Action/ with full comment text and suggested response, verify all 5 interactions logged to logs/social_media_watcher.log.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T077 [P] [US4] Unit test for priority filtering algorithm in social-media-watcher/tests/test_priority_filtering.py (test keyword matching, scoring, HIGH/MEDIUM/LOW classification, whitelist override)
- [ ] T078 [P] [US4] Unit test for action item creation in social-media-watcher/tests/test_action_item_creation.py (test interaction → markdown file with correct frontmatter, content, suggested response)
- [ ] T079 [P] [US4] Integration test for Facebook monitoring in social-media-watcher/tests/test_facebook_monitor.py (mock Facebook page with 5 new comments, verify action items created for HIGH/MEDIUM, LOW logged only)
- [ ] T080 [P] [US4] Integration test for daily engagement summary in social-media-watcher/tests/test_engagement_summary.py (mock 24h of interactions across all platforms, verify Briefings/Social_Media_YYYY-MM-DD.md generated with correct breakdown)
- [ ] T081 [US4] End-to-end test for complete monitoring workflow in social-media-watcher/tests/test_monitoring_e2e.py (run watcher for 10 minutes, simulate interactions, verify action items in Needs_Action/, verify daily summary at 6 PM)

### Implementation for User Story 4

- [ ] T082 [P] [US4] Create priority filtering utility in social-media-watcher/scripts/priority_filter.py with calculate_priority function (keyword matching: HIGH priority keywords weight 10, BUSINESS keywords weight 5, whitelist weight 15, score >= 15 = HIGH, >= 5 = MEDIUM, else LOW)
- [ ] T083 [P] [US4] Create Facebook monitor in social-media-watcher/scripts/facebook_monitor.py with FacebookMonitor class and methods: __init__, check_notifications, fetch_comments, fetch_messages, fetch_mentions (use Playwright with .social_session/facebook/ context from US2)
- [ ] T084 [P] [US4] Create Instagram monitor in social-media-watcher/scripts/instagram_monitor.py with InstagramMonitor class and methods: __init__, check_notifications, fetch_comments, fetch_dms, fetch_mentions (use Playwright with .social_session/instagram/ context from US2)
- [ ] T085 [P] [US4] Create Twitter monitor in social-media-watcher/scripts/twitter_monitor.py with TwitterMonitor class and methods: __init__, check_notifications, fetch_mentions, fetch_replies, fetch_dms (use Playwright with .social_session/twitter/ context from US2)
- [ ] T086 [US4] Implement main watcher orchestrator in social-media-watcher/scripts/social_media_watcher.py with SocialMediaWatcher class and methods: __init__, check_all_platforms, create_action_items, generate_daily_summary, run (polling loop with SOCIAL_WATCHER_INTERVAL)
- [ ] T087 [US4] Add action item creation in social-media-watcher/scripts/social_media_watcher.py create_action_items method (filter by priority using scripts/priority_filter.py, create markdown files in Needs_Action/ with frontmatter: type, platform, interaction_type, priority, detected, author_name, author_handle, post_url, detected_keywords, suggested_response)
- [ ] T088 [US4] Implement deduplication in social-media-watcher/scripts/social_media_watcher.py (track processed interaction IDs in .social_interactions_state.json, prevent duplicate action items)
- [ ] T089 [US4] Add engagement summary generation in social-media-watcher/scripts/engagement_summary.py with generate_summary function (aggregate interactions by platform, count HIGH/MEDIUM/LOW, calculate response rate, identify top performing posts)
- [ ] T090 [US4] Add daily summary scheduling in social-media-watcher/scripts/social_media_watcher.py run method (trigger at 6:00 PM daily, call scripts/engagement_summary.py generate_summary, save to Briefings/Social_Media_YYYY-MM-DD.md)
- [ ] T091 [US4] Add viral alert detection in social-media-watcher/scripts/twitter_monitor.py (check if mention count exceeds SOCIAL_TWITTER_MENTION_THRESHOLD within 1 hour, create HIGH priority "Viral Alert" action item with engagement strategy)
- [ ] T092 [US4] Add whitelist support in social-media-watcher/scripts/priority_filter.py (read SOCIAL_WHITELEST_ACCOUNTS from .env, always create action items for whitelisted accounts regardless of content)
- [ ] T093 [US4] Add configuration loading in social-media-watcher/scripts/social_media_watcher.py (read SOCIAL_HIGH_PRIORITY_KEYWORDS, SOCIAL_BUSINESS_KEYWORDS, SOCIAL_WHITELIST_ACCOUNTS, engagement thresholds from .env and Company_Handbook.md)
- [ ] T094 [US4] Add logging to all monitoring operations in social-media-watcher/scripts/ (use scripts/shared/audit_logger.py, log all detected interactions, priority scores, action items created, engagement summaries)
- [ ] T095 [US4] Create Company_Handbook.md template section in social-media-watcher/templates/Company_Handbook_Social_Media.md with priority rules, keyword lists, whitelist examples

**Checkpoint**: All 4 user stories should now be independently functional

---

## Phase 7: Integration & Cross-Story Features

**Purpose**: Connect user stories, implement cross-domain data flow, graceful degradation across all features

- [ ] T096 [P] Add Xero revenue data to CEO briefing in weekly-ceo-briefing/scripts/weekly_audit.py (modify analyze_revenue to read Accounting/Current_Month.md populated by xero_watcher, include in briefing: total revenue, revenue sources, MTD progress, trend visualization)
- [ ] T097 [P] Add social media metrics to CEO briefing in weekly-ceo-briefing/scripts/weekly_audit.py (read Briefings/Social_Media_*.md generated by social_media_watcher, include in briefing: total interactions, action items created, top performing posts)
- [ ] T098 [P] Implement graceful degradation across all features in weekly_audit.py generate_briefing method (if Xero sync failed, generate briefing with task data only; if social watcher failed, omit social section; if both failed, generate minimal briefing with warning)
- [ ] T099 Integrate social posting with approval workflow in approval-workflow-manager skill (update skill to handle social_post action items, validate frontmatter, route to @mcp-executor with social-media-browser-mcp tools)
- [ ] T100 [P] Add multi-watcher orchestration support in scripts/orchestrate_watchers.py (include xero_watcher and social_media_watcher alongside existing Silver tier watchers, independent process management, health monitoring, restart on crash)
- [ ] T101 Create cross-domain integration test in tests/integration/test_cross_domain.py (test Xero sync → briefing includes revenue; test social monitoring → briefing includes metrics; test social posting → audit log updated)
- [ ] T102 [P] Add Dashboard.md aggregation across all features in scripts/shared/dashboard_updater.py (update dashboard with: latest briefing link, health score, social media stats, recent posts, pending action items count)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, error handling refinement, performance optimization

- [ ] T103 [P] Update all skill SKILL.md files with complete usage examples (social-media-browser-mcp, weekly-ceo-briefing, xero-accounting, social-media-watcher)
- [ ] T104 [P] Create comprehensive quickstart guide in specs/003-gold-tier-ai-employee/quickstart.md (step-by-step setup for all 4 features with troubleshooting)
- [ ] T105 [P] Add vault file corruption recovery to scripts/shared/vault_ops.py (detect malformed YAML, create .bak backup, log error with line number, use safe defaults)
- [ ] T106 [P] Implement timezone handling in weekly_audit.py (read BRIEFING_TIMEZONE from .env, convert all timestamps to user local timezone for display, store UTC in ISO8601 format)
- [ ] T107 [P] Add holiday briefing skip logic in weekly_audit.py (check Company_Handbook.md for holiday calendar, if briefing day is holiday, generate on next business day with note)
- [ ] T108 [P] Optimize briefing performance for large vaults in weekly_audit.py (implement pagination for Tasks/Done/ reading, optimize Accounting/ parsing with regex, add caching for Business_Goals.md)
- [ ] T109 [P] Add storage quota detection to scripts/shared/vault_ops.py (detect Obsidian Sync quota exceeded error, create CRITICAL alert in Dashboard.md, implement cleanup strategy: archive briefings older than 90 days)
- [ ] T110 Create end-to-end Gold tier demo script in scripts/gold_tier_demo.py (demonstrate full workflow: Xero sync → social monitoring → briefing generation → social post approval → execution → audit log verification)
- [ ] T111 [P] Add comprehensive logging configuration to all skills (create logs/ directory, set up daily log rotation YYYY-MM-DD.json format, ensure 90-day retention per Constitution Principle IX)
- [ ] T112 Run all test suites and verify 80%+ coverage per Constitution Principle VII (pytest --cov, generate coverage report, address gaps)
- [ ] T113 Create architecture decision records for significant decisions (ADR for browser automation vs official APIs, ADR for graceful degradation strategy, ADR for multi-currency conversion approach)

---

## Dependencies

### User Story Dependencies

- **US1 (CEO Briefing)**: No dependencies (can be implemented independently)
- **US2 (Social Posting)**: No dependencies on other user stories (can be implemented independently)
- **US3 (Xero Integration)**: No dependencies on other user stories (can be implemented independently)
- **US4 (Social Monitoring)**: Depends on US2 for browser session reuse (uses .social_session/ contexts created by US2 login helpers)

### Cross-Story Integration Dependencies

- **Integration Phase (T096-T102)**: Requires US1, US2, US3, US4 complete (connects all features)
- **Briefing Integration (T096-T097)**: Requires US1 (weekly_audit.py) + US3 (xero_watcher) + US4 (social_media_watcher)
- **Multi-Watcher Orchestration (T100)**: Requires US3 (xero_watcher) + US4 (social_media_watcher) + Silver tier watchers

### Dependency Graph

```
Setup (T001-T007)
    ↓
Foundational (T008-T014)
    ↓
├─────────────────┬─────────────────┬─────────────────┐
↓                 ↓                 ↓                 ↓
US1 (T015-T034)   US2 (T035-T055)   US3 (T056-T076)   US4 (T077-T095)
└─────┬───────┬───┴───────┬─────────┴───────┬─────────┴────┐
      ↓       ↓          ↓                 ↓              ↓
      Integration (T096-T102) ←──────────────────────────────┘
      ↓
      Polish (T103-T113)
```

### Parallel Opportunities

**Within User Stories** (tasks marked [P] can run in parallel):
- Phase 1 Setup: T002-T007 can run in parallel (5 independent pyproject.toml initializations)
- Phase 2 Foundational: T009-T011 can run in parallel (3 independent utilities)
- US1 Tests: T015-T019 can run in parallel (5 independent test files)
- US1 Implementation: T020-T022 can run in parallel (3 independent modules)
- US2 Tests: T035-T039 can run in parallel (5 independent test files)
- US2 Implementation: T040-T044 can run in parallel (5 independent login/helpers)
- US3 Tests: T056-T060 can run in parallel (5 independent test files)
- US3 Implementation: T061-T066 can run in parallel (6 independent Xero operations)
- US4 Tests: T077-T081 can run in parallel (5 independent test files)
- US4 Implementation: T082-T085 can run in parallel (4 independent platform monitors)
- Integration: T096-T097, T099-T100, T101-T102 can run in parallel (6 independent integration tasks)
- Polish: T103-T104, T105-T109 can run in parallel (9 independent polish tasks)

**Total Parallel Opportunities**: 45 tasks can run in parallel across all phases

## Implementation Strategy

### MVP Scope (Minimum Viable Gold Tier)

**Recommended MVP**: User Story 1 (CEO Briefing) only
- **Delivers Value**: Automated business audit with health scores, revenue analysis, bottleneck detection
- **Independence**: No dependencies on other user stories
- **Testability**: Can be fully tested with sample vault data
- **Timeline**: Week 1 (per plan.md rollout strategy)

**MVP Tasks**: T001-T014 (Setup + Foundational) + T015-T034 (US1 complete) = 34 tasks

### Incremental Delivery

**Sprint 1** (Week 1): MVP - CEO Briefing (US1)
- Complete Setup and Foundational phases
- Implement all US1 tasks
- Deliver automated Monday briefing
- **Value Demonstration**: Health scores, bottleneck detection, cost optimization

**Sprint 2** (Week 2): Social Media Posting (US2)
- Implement all US2 tasks
- Deliver Facebook posting (Instagram, Twitter in Week 3)
- **Value Demonstration**: HITL approval workflow, browser automation, session persistence

**Sprint 3** (Week 3): Xero Integration (US3)
- Implement all US3 tasks
- Deliver financial data sync
- **Value Demonstration**: Automated bookkeeping, CEO briefing integration

**Sprint 4** (Week 4): Social Media Monitoring (US4)
- Implement all US4 tasks
- Deliver engagement tracking
- **Value Demonstration**: Priority filtering, daily summaries, proactive customer service

**Sprint 5** (Week 5): Integration & Polish
- Implement cross-domain integration
- Polish all features
- End-to-end testing
- **Value Demonstration**: Full Gold tier demo

### Success Metrics

**Per Plan.md Success Criteria**:

- **SC-001**: Briefing generation < 30 seconds (validated by T019)
- **SC-003**: Xero sync < 5 minutes (validated by T060)
- **SC-004**: Social posting latency targets (validated by T039)
- **SC-006**: Graceful degradation (validated by T018, T098)
- **SC-020**: Silver tier integration (validated by T101)

**Test Coverage Target**: 80%+ per Constitution Principle VII (validated by T112)

---

## Task Summary

- **Total Tasks**: 113
- **Setup Phase**: 7 tasks (T001-T007)
- **Foundational Phase**: 7 tasks (T008-T014)
- **User Story 1 (CEO Briefing)**: 20 tasks (T015-T034)
- **User Story 2 (Social Posting)**: 21 tasks (T035-T055)
- **User Story 3 (Xero Integration)**: 21 tasks (T056-T076)
- **User Story 4 (Social Monitoring)**: 19 tasks (T077-T095)
- **Integration Phase**: 7 tasks (T096-T102)
- **Polish Phase**: 11 tasks (T103-T113)

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel

**Independent Tests**: Each user story has defined independent test criteria (see phase headers)

**Suggested MVP**: User Story 1 (T001-T034 = 34 tasks for standalone CEO briefing MVP)
