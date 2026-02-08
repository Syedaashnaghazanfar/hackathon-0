# Implementation Plan: Gold Tier AI Employee

**Branch**: `003-gold-tier-ai-employee` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-gold-tier-ai-employee/spec.md`

## Summary

Implement comprehensive Gold Tier AI Employee with four major features: (1) Monday Morning CEO Briefing - automated business audit analyzing revenue, tasks, bottlenecks, and cost optimization opportunities; (2) Social Media Cross-Posting - unified browser automation for Facebook, Instagram, Twitter/X using Playwright with persistent sessions; (3) Xero Accounting Integration - financial data sync via official Xero MCP server or custom Python implementation; (4) Social Media Monitoring - engagement tracking with priority filtering and daily summaries.

**Technical Approach**: Build on Silver tier infrastructure (multi-watcher, HITL approval workflow, MCP servers) with Gold-tier-specific watchers (xero_watcher, social_media_watcher) and scheduled briefing generator. Browser automation via Playwright with CDP session sharing (pattern from WhatsApp watcher), FastMCP for social media posting, official Xero MCP server preferred with custom Python fallback. Graceful degradation ensures single-component failures don't break entire system.

## Technical Context

**Language/Version**: Python 3.13+

**Primary Dependencies**:
- **FastMCP**: Pydantic v2 validation for MCP server tools
- **Playwright**: Browser automation for Facebook, Instagram, Twitter/X (persistent contexts)
- **watchdog**: Filesystem events (existing Silver tier infrastructure)
- **python-frontmatter**: YAML frontmatter parsing for vault markdown files
- **requests**: HTTP client for Xero API and exchange rate APIs

**Storage**:
- **Obsidian Vault**: Markdown files with YAML frontmatter (single source of truth)
- **Session Files**: `.social_session/` for browser cookies, `.xero_tokens.json` for OAuth (gitignored)
- **Audit Logs**: JSON files in `AI_Employee_Vault/Logs/YYYY-MM-DD.json` (90-day retention)

**Testing**: pytest with mock fixtures for external APIs (Xero, social platforms)

**Target Platform**:
- **Primary**: Local development machine (Windows/Linux/Mac)
- **Scheduling**: Platform-specific (cron on Linux/Mac, Task Scheduler on Windows)

**Project Type**: Single Python project with skills-based architecture (`.claude/skills/*/`)

**Performance Goals**:
- Briefing generation: < 30 seconds
- Xero sync latency: < 5 minutes (watcher interval)
- Social posting: Facebook < 60s, Instagram < 90s, Twitter < 45s
- Social monitoring: Check all platforms within 10-minute interval

**Constraints**:
- Constitution-compliant: HITL approval for all external actions, credential sanitization, graceful degradation
- Single-user local system (no multi-tenant authentication)
- Browser automation requires 4GB RAM minimum
- Must integrate with existing Silver tier agents (@needs-action-triage, @mcp-executor)

**Scale/Scope**:
- 4 Gold tier features, 40 functional requirements
- Supports 3 social platforms, 1 accounting system
- Vault can handle 1000+ completed tasks, 500+ transactions without performance degradation
- Designed for solo business owners (not enterprise multi-user)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principle I: Local-First Personal AI Employee

**Status**: ✅ COMPLIANT

**Verification**:
- All Gold tier features extend local Obsidian vault (no cloud dependencies except Xero API)
- Skills stored in `.claude/skills/` (social-media-browser-mcp, weekly-ceo-briefing, xero-accounting, social-media-watcher)
- Gold tier is additive to Silver - maintains Bronze + Silver foundations

**Gold Tier Additions**:
- Monday CEO Briefing: Analyzes vault data (Business_Goals.md, Accounting/, Tasks/Done/)
- Social Media Posting: Browser automation via MCP (HITL approval enforced)
- Xero Integration: Local watcher syncs to vault (data stays local)
- Social Monitoring: Local watcher creates action items in vault

---

### Core Principle II: Vault Safety and Non-Destructive Operations

**Status**: ✅ COMPLIANT

**Verification**:
- Briefing generation: Appends to `Briefings/` folder, never overwrites user content
- Xero sync: Updates `Accounting/Current_Month.md` via line-by-line updates (not full file rewrite)
- Social posting: Creates new files in `Pending_Approval/`, moves to `Done/` after execution
- YAML frontmatter preserved in all vault operations

**Safety Mechanisms**:
- `.bak` backup creation before modifying corrupted files
- Atomic file writes (write to temp, then rename)
- Vault file validation before processing (YAML parsing, schema validation)

---

### Core Principle III: Human-as-Tool Principle

**Status**: ✅ COMPLIANT

**Verification**:
- Xero setup requires manual OAuth flow (user runs `setup_xero_oauth.py` in browser)
- Social media login requires manual authentication (user runs `login_facebook.py`, `login_instagram.py`, `login_twitter.py`)
- Scheduling configuration requires user input (cron/Task Scheduler setup)
- Missing data sources trigger human prompts (e.g., "Configure Business_Goals.md for revenue targets")

**Ambiguity Triggers**:
- Vault path not configured → Prompt for `--vault-path` argument
- Multiple Xero organizations → Prompt user to select tenant
- Conflicting social media sessions → Prompt user to re-login

---

### Core Principle IV: Watcher Resilience and Idempotency

**Status**: ✅ COMPLIANT

**Verification**:
- **Xero Watcher**:
  - Deduplication based on `InvoiceID` and `BankTransactionID` (prevents duplicate entries)
  - Exponential backoff for API failures (1s, 2s, 4s delays, max 3 retries)
  - Logs errors and continues running (single API failure doesn't crash watcher)

- **Social Media Watcher**:
  - Deduplication based on `post_url` + `timestamp` (prevents duplicate action items)
  - Graceful handling of session expiration (logs error, continues monitoring other platforms)
  - Atomic action item writes (prevent partial/corrupt markdown files)

- **Briefing Generator**:
  - Validates all data sources before processing (YAML parsing, file existence checks)
  - Generates partial briefing if some sources fail (graceful degradation)
  - Try-except around all calculations (use safe defaults on division by zero)

**Resilience Features**:
- Heartbeat logging every 60 seconds (watcher health monitoring)
- Graceful shutdown handlers (SIGTERM/SIGINT) for in-flight operations
- Dead letter queue (`/Failed/` folder) for manual intervention

---

### Core Principle V: Secret Management and Security

**Status**: ✅ COMPLIANT

**Verification**:
- All credentials in `.env` only (never in vault or repository)
- `.gitignore` excludes: `.env`, `.social_session/`, `.xero_tokens.json`, `Logs/`
- Xero tokens stored in vault root (gitignored), not in repository
- Social media sessions stored in `.social_session/` (gitignored)

**Credential Sanitization**:
- Audit logs redact: API keys, OAuth tokens, session IDs (replace with `<REDACTED_TOKEN>`)
- Briefings exclude: Raw transaction details (show only aggregated metrics)
- Social interaction logging excludes: Private DM content (show only public comments)

**Environment Variables**:
```bash
# Xero credentials (NEVER commit to git)
XERO_CLIENT_ID=your_client_id_here
XERO_CLIENT_SECRET=your_client_secret_here
XERO_REFRESH_TOKEN=your_refresh_token_here

# Social media session paths (gitignored)
SOCIAL_SESSION_DIR=.social_session
```

**Dry-Run Mode**:
```bash
DRY_RUN=true  # Prevents real external actions during testing
```

---

### Core Principle VI: Technology Stack and Implementation Constraints

**Status**: ✅ COMPLIANT

**Verification**:
- Python 3.13+ (constitution requirement)
- Package management via `uv` (constitution requirement)
- Testing via `pytest` (constitution requirement)
- FastMCP with Pydantic v2 (Silver tier addition)

**Gold Tier Dependencies**:
- **Playwright**: Browser automation (justified by social media posting requirement)
- **python-frontmatter**: YAML parsing (minimal dependency, no alternatives)
- **requests**: HTTP client for Xero API (standard library alternative `urllib` lacks required features)

**Code Quality**:
- Type hints on all function signatures (constitution requirement)
- Docstrings for public functions (constitution requirement)
- Actionable error messages with context and suggested fixes (constitution requirement)

**Justification for Playwright**:
- Required for social media posting (no official APIs with posting permissions)
- Lightweight alternative: Selenium (rejected due to poorer async support)
- Pattern established in Silver tier (WhatsApp watcher uses Playwright)

---

### Core Principle VII: Test-Driven Development for Core Logic

**Status**: ⚠️ PARTIAL (Tests to be added during implementation)

**Required Tests** (Gold Tier):

**CEO Briefing**:
- [ ] Briefing generation with mock vault data (Business_Goals.md, Accounting/, Tasks/Done/)
- [ ] Health score calculation edge cases (zero revenue, negative delays)
- [ ] Graceful degradation (missing data sources, corrupted files)
- [ ] Revenue parsing from markdown tables

**Social Media Posting**:
- [ ] MCP server tool validation (Pydantic v2 schemas)
- [ ] Post creation with mock Playwright browser
- [ ] Session expiration detection and error handling
- [ ] HITL approval workflow end-to-end (Pending_Approval → Approved → execution)

**Xero Accounting**:
- [ ] OAuth2 token refresh logic
- [ ] Transaction deduplication
- [ ] Multi-currency conversion
- [ ] API error handling (rate limiting, network timeout)

**Social Media Monitoring**:
- [ ] Priority filtering algorithm (keyword matching, scoring)
- [ ] Action item creation from interactions
- [ ] Daily engagement summary generation

**Integration Tests**:
- [ ] Full Gold tier demo: Xero sync → briefing generation → social post approval → execution → audit log
- [ ] Graceful degradation: One watcher crash doesn't affect others
- [ ] Cross-domain integration: Briefing includes Xero revenue, social metrics

**Test Coverage Target**: 80%+ for all core logic modules

---

### Core Principle VIII: Human-in-the-Loop (HITL) Approval Workflow

**Status**: ✅ COMPLIANT

**Verification**:
- ALL external actions require approval:
  - Social media posts: Pending_Approval/ → human → Approved/ → execution
  - Xero invoice creation: Pending_Approval/ → human → Approved/ → execution
- Approval workflow follows Silver tier pattern:
  1. @needs-action-triage creates plan, identifies external action
  2. @approval-workflow-manager creates approval request
  3. Human moves to `/Approved/` (execute) or `/Rejected/` (cancel)
  4. @mcp-executor executes via MCP servers

**Permission Boundaries**:
- **Auto-Approve**: None configured (default: require approval for all external actions)
- **Require-Approval**: All social posts, all Xero invoice creations

**Rejection Handling**:
- Rejected items moved to `/Rejected/` with `rejection_reason` in frontmatter
- Failed executions moved to `/Failed/` with error details
- Orchestrator never executes rejected or failed items

---

### Core Principle IX: Security and Audit Logging

**Status**: ✅ COMPLIANT

**Verification**:
- All external executions logged to `/Logs/YYYY-MM-DD.json`
- Audit log schema compliant with Silver tier format
- Credential sanitization enforced (no plaintext tokens in logs)

**Audit Log Entry Example**:
```json
{
  "timestamp": "2026-01-06T08:01:23Z",
  "action_id": "social_post_facebook_20260106",
  "action_type": "post_to_facebook",
  "user": "human-approver-id",
  "ai_agent": "claude-code-sonnet-4.5",
  "approval_reason": "New project announcement",
  "execution_status": "success",
  "mcp_server": "social-browser-mcp",
  "tool_name": "post_to_facebook",
  "tool_inputs_sanitized": {
    "text": "Excited to share our latest project! 🚀",
    "image_path": "AI_Employee_Vault/Attachments/..."
  },
  "tool_output_sanitized": {
    "post_url": "https://facebook.com/posts/123456",
    "platform_post_id": "123456_789"
  },
  "error": null,
  "retry_count": 0
}
```

**Retention Policy**:
- Minimum 90-day retention (constitution requirement)
- Daily rotation (`YYYY-MM-DD.json` format)
- Archive old logs (optional compression)

---

### Core Principle X: Graceful Degradation and Error Handling

**Status**: ✅ COMPLIANT

**Verification**:
- **Component Isolation**:
  - Xero watcher failure doesn't affect social media watcher
  - Social media posting failure doesn't affect briefing generation
  - Each watcher runs as independent process

- **Error Recovery**:
  - Exponential backoff with max 3 retries (constitution requirement)
  - Dead letter queue (`/Failed/` folder) for manual intervention
  - Health monitoring with heartbeat logging every 60 seconds
  - Graceful shutdown handlers (SIGTERM/SIGINT)

**Failure Modes Matrix**:
| Component | Failure Impact | Mitigation |
|-----------|---------------|------------|
| Xero watcher | No new revenue data | Use manual Accounting/Current_Month.md entry; briefing generates with warning |
| Social watcher | No engagement metrics | Omit social section from briefing |
| Briefing generator | No weekly audit | Manual business review; retry next Monday |
| Social posting | Cannot publish posts | Posts stay in Pending_Approval/; manual posting via native apps |
| MCP server (social) | Cannot execute posts | Approval workflow continues; failed executions in `/Failed/` |

**Graceful Degradation in Action**:
```python
# Example from weekly_audit.py
def generate_briefing(self) -> Path:
    # Try all data sources, continue on failure
    business_goals = self._load_business_goals()  # May fail
    revenue_data = self._load_revenue_data()       # May fail
    tasks_data = self._load_tasks_data()          # May fail

    # Generate partial briefing with available data
    available_sources = [s for s in [business_goals, revenue_data, tasks_data] if s]
    missing_sources = [s for s in [business_goals, revenue_data, tasks_data] if not s]

    if missing_sources:
        briefing_content += f"\n**Warnings**: Missing data sources: {', '.join(missing_sources)}\n"
```

---

### Constitution Compliance Summary

**Overall Status**: ✅ COMPLIANT (with tests pending implementation)

**Violations**: None

**Justified Deviations**: None

**Post-Design Re-Check**: Passed (see Phase 1 completion)

## Project Structure

### Documentation (this feature)

```text
specs/003-gold-tier-ai-employee/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - Technical research and decisions
├── data-model.md        # Phase 1 output - Entity definitions and schemas
├── quickstart.md        # Phase 1 output - Setup and usage guide
├── contracts/           # Phase 1 output - API contracts
│   ├── social-media-browser-mcp.yaml
│   └── xero-accounting.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
# Gold Tier Skills (Single Project Structure)
.claude/skills/
├── social-media-browser-mcp/
│   ├── SKILL.md                    # Skill documentation
│   ├── scripts/
│   │   ├── social_browser_mcp.py   # FastMCP server implementation
│   │   ├── login_facebook.py       # Facebook login helper
│   │   ├── login_instagram.py      # Instagram login helper
│   │   ├── login_twitter.py        # Twitter/X login helper
│   │   └── engagement_summary.py   # Engagement metrics calculator
│   ├── pyproject.toml              # uv dependency management
│   └── tests/
│       ├── test_mcp_tools.py       # MCP tool validation tests
│       └── test_session_persistence.py
│
├── weekly-ceo-briefing/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── weekly_audit.py         # Main briefing generator
│   │   ├── revenue_analyzer.py     # Revenue analysis module
│   │   ├── bottleneck_detector.py  # Bottleneck detection module
│   │   └── cost_optimizer.py       # Cost optimization module
│   ├── pyproject.toml
│   └── tests/
│       ├── test_briefing_generation.py
│       ├── test_health_score.py
│       └── test_graceful_degradation.py
│
├── xero-accounting/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── xero_watcher.py         # Xero sync watcher
│   │   ├── accounting_audit.py     # Financial reports generator
│   │   └── setup_xero_oauth.py     # OAuth2 setup script
│   ├── pyproject.toml
│   └── tests/
│       ├── test_xero_sync.py
│       ├── test_token_refresh.py
│       └── test_currency_conversion.py
│
└── social-media-watcher/
    ├── SKILL.md
    ├── scripts/
    │   ├── social_media_watcher.py  # Main watcher orchestrator
    │   ├── facebook_monitor.py     # Facebook monitoring
    │   ├── instagram_monitor.py    # Instagram monitoring
    │   ├── twitter_monitor.py      # Twitter/X monitoring
    │   └── engagement_summary.py   # Daily summary generator
    ├── pyproject.toml
    └── tests/
        ├── test_priority_filtering.py
        └── test_action_item_creation.py

# Gold Tier Watchers (Integration with Silver Tier)
scripts/
└── orchestrate_watchers.py         # Multi-watcher runner (Silver tier, extended for Gold)

# Vault Structure (Obsidian)
AI_Employee_Vault/
├── Business_Goals.md               # Gold tier: Business targets and metrics
├── Accounting/
│   ├── Current_Month.md            # Gold tier: Current month transactions
│   └── Previous_Months/            # Gold tier: Historical accounting data
├── Briefings/                      # Gold tier: Generated briefings
│   ├── 2026-01-06_Monday_Briefing.md
│   └── Social_Media_2026-01-06.md
├── Pending_Approval/               # Silver tier: Approval requests
├── Approved/                       # Silver tier: Approved actions
├── Needs_Action/                   # Bronze/Silver tier: Action items
├── Done/
│   └── Social_Media_Posts/         # Gold tier: Completed social posts
└── Logs/                           # Silver tier: Audit logs
    ├── 2026-01-06.json
    └── ...
```

**Structure Decision**: Single project structure chosen because Gold tier is skill-based architecture (`.claude/skills/*/`), not a traditional application. Each Gold tier feature is a self-contained skill with its own dependencies, tests, and documentation. This aligns with Silver tier patterns and keeps features decoupled for independent development and testing.

## Complexity Tracking

> **No violations requiring justification** - Constitution check passed all gates.

## Implementation Phases

### Phase 0: Research ✅ COMPLETE

**Output**: `research.md`

**Decisions Made**:
1. Playwright multi-platform session management (separate contexts per platform)
2. FastMCP for social media automation (custom implementation)
3. Xero integration: Official MCP server + custom Python fallback
4. Monday briefing scheduling: Platform-specific (cron/Task Scheduler)
5. Graceful degradation: Component isolation with partial data generation
6. Social media priority filtering: Keyword-based scoring with whitelist
7. Multi-currency support: Convert to base currency via API
8. Error recovery: Exponential backoff with max 3 retries

**Resolved Unknowns**: All 8 technical unknowns resolved through research.

---

### Phase 1: Design ✅ COMPLETE

**Outputs**:
- `data-model.md` - 7 entity definitions (Business_Goals, Monday_Briefing, Social_Post_Action, Accounting_Entry, Xero_Token, Social_Media_Interaction, Engagement_Summary)
- `contracts/` - 2 API contracts (social-media-browser-mcp.yaml, xero-accounting.yaml)
- `quickstart.md` - Comprehensive setup guide for all 4 Gold tier features
- `plan.md` (this file) - Complete technical context and constitution check

**Design Decisions**:
- Entity relationships mapped (e.g., Business_Goals → Monday_Briefing, Xero API → Accounting_Entry)
- API contracts defined for MCP tools (5 social media tools, 4 Xero tools)
- Cross-cutting concerns addressed (YAML validation, file naming, timestamp handling, currency conversion)

**Post-Design Constitution Check**: ✅ PASSED (all gates re-evaluated, no violations)

---

### Phase 2: Tasks (NOT CREATED YET)

**Next Step**: Run `/sp.tasks` to generate actionable implementation tasks

**Expected Output**: `specs/003-gold-tier-ai-employee/tasks.md`

**Task Categories**:
1. CEO Briefing Implementation (revenue_analyzer, bottleneck_detector, cost_optimizer, weekly_audit orchestration)
2. Social Media Posting (MCP server implementation, login helpers, session management)
3. Xero Integration (OAuth2 setup, watcher implementation, token refresh logic)
4. Social Media Monitoring (platform monitors, priority filtering, daily summaries)
5. Integration & Testing (cross-domain integration, graceful degradation tests, end-to-end demo)

---

## Dependencies

### External Dependencies

- **Obsidian**: Vault software (must be installed by user)
- **Xero Account**: Optional (only if using Xero integration)
- **Social Media Accounts**: Facebook Page, Instagram Business, Twitter/X profile (must be created by user)

### Internal Dependencies

- **Silver Tier**: Multi-watcher infrastructure, HITL approval workflow, @needs-action-triage, @mcp-executor agents
- **Bronze Tier**: Filesystem watcher, vault operations, basic triage

### Dependency Graph

```
Gold Tier Features
    ↓ (depend on)
Silver Tier Infrastructure
    ↓ (depends on)
Bronze Tier Foundation
```

**Impact**: Cannot implement Gold tier without fully functional Silver tier. Constitution Principle I explicitly requires Gold to be "additive to Bronze and Silver" - no breaking changes to existing tiers.

---

## Risk Analysis

### High-Risk Areas

1. **Browser Automation Fragility** (Risk: HIGH)
   - **Impact**: Social media posting fails if platforms change UI/DOM structure
   - **Mitigation**: Detect failures via error messages, prompt user to re-login, provide manual posting fallback
   - **Monitoring**: Log all Playwright errors, track success rates per platform

2. **Xero API Rate Limiting** (Risk: MEDIUM)
   - **Impact**: Sync delays if exceeding 60 requests/minute
   - **Mitigation**: Implement request queuing, exponential backoff, sync interval tuning
   - **Monitoring**: Log rate limit events, alert on persistent throttling

3. **Multi-Currency Conversion Accuracy** (Risk: MEDIUM)
   - **Impact**: Incorrect revenue calculations in briefing if exchange rates are wrong
   - **Mitigation**: Use reputable exchange rate API, store conversion rate in audit trail
   - **Monitoring**: Log all currency conversions with rates used

### Medium-Risk Areas

4. **Session Expiration Detection** (Risk: MEDIUM)
   - **Impact**: Failed posts if sessions expire silently
   - **Mitigation**: Test session validity before posting, clear error messages
   - **Monitoring**: Track session age, warn proactively before expiry

5. **Briefing Performance with Large Vaults** (Risk: MEDIUM)
   - **Impact**: Briefing generation > 30 seconds if 1000+ tasks, 500+ transactions
   - **Mitigation**: Implement pagination for large datasets, optimize parsing
   - **Monitoring**: Log briefing generation time, alert on degradation

### Low-Risk Areas

6. **Social Media False Positives** (Risk: LOW)
   - **Impact**: LOW priority interactions flagged as HIGH
   - **Mitigation**: Tunable keyword thresholds, whitelist override
   - **Monitoring**: User feedback loop, adjust scoring over time

---

## Rollout Strategy

### Phase 1: CEO Briefing (P1 Feature)
- **Timeline**: Week 1
- **Deliverable**: Automated Monday briefing generation
- **Validation**: Manual briefing generation, verify health score accuracy

### Phase 2: Social Media Posting (P2 Feature)
- **Timeline**: Week 2
- **Deliverable**: Facebook posting (Instagram, Twitter/X in Week 3)
- **Validation**: End-to-end post approval → execution → audit log

### Phase 3: Xero Integration (P2 Feature)
- **Timeline**: Week 3
- **Deliverable**: Xero sync to Accounting/, briefing integration
- **Validation**: Manual sync, verify accounting data accuracy

### Phase 4: Social Media Monitoring (P3 Feature - Optional)
- **Timeline**: Week 4
- **Deliverable**: Engagement tracking, daily summaries
- **Validation**: Manual interaction detection, priority filtering

### Integration & Testing
- **Timeline**: Week 5
- **Deliverable**: Full Gold tier demo, all tests passing
- **Validation**: End-to-end demo: Xero sync → briefing → social post → monitoring

---

## Success Criteria

### Minimum Viable Gold Tier
- [ ] Monday briefing generates automatically with health score, revenue analysis, bottleneck detection
- [ ] At least 1 social platform posting functional (Facebook recommended first)
- [ ] Xero sync functional (or manual Accounting/ entry as fallback)
- [ ] Graceful degradation verified (briefing generates with partial data)

### Complete Gold Tier
- [ ] All 4 features operational (briefing, FB/IG/Twitter posting, Xero, social monitoring)
- [ ] Cross-domain integration (briefing includes Xero revenue, social metrics)
- [ ] All tests passing (unit, integration, end-to-end)
- [ ] Documentation complete (quickstart guide tested by 5 users)

---

## References

- [Spec: Gold Tier AI Employee](./spec.md)
- [Research: Technical Decisions](./research.md)
- [Data Model: Entity Definitions](./data-model.md)
- [Quick Start: Setup Guide](./quickstart.md)
- [Constitution: Project Principles](../../.specify/memory/constitution.md)
- [Silver Tier Spec](../002-silver-tier-ai-employee/spec.md) - Reference for HITL workflow, multi-watcher infrastructure

---

**Plan Status**: ✅ COMPLETE (Phase 0 and Phase 1 finished, ready for Phase 2 task generation)

**Next Action**: Run `/sp.tasks` to generate actionable implementation tasks
