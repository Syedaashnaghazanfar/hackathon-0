---
name: weekly-ceo-briefing
description: >
  Monday Morning CEO Briefing generator for autonomous business audit. Analyzes business goals,
  completed tasks, revenue metrics, bottlenecks, and cost optimization opportunities. Generates
  comprehensive briefing documents in Obsidian vault. Use when: (1) Running weekly business audits,
  (2) Generating CEO briefings, (3) Analyzing business performance, (4) Identifying bottlenecks,
  (5) Reviewing revenue and costs. Trigger phrases: "generate CEO briefing", "weekly business audit",
  "Monday morning briefing", "business summary", "revenue analysis", "bottleneck report", "cost optimization".
---

# Weekly CEO Briefing (Gold Tier)

Monday Morning CEO Briefing - autonomous business audit that transforms your AI Employee from reactive to proactive. Generates comprehensive weekly business briefings by analyzing your vault data.

## Quick Start

### Prerequisites

- Obsidian vault with Business_Goals.md, Tasks/Done/, Accounting/
- Python 3.13+
- Cron (Linux/Mac) or Task Scheduler (Windows)

### Generate Briefing

```bash
# Manual generation
python scripts/weekly_audit.py --vault-path "AI_Employee_Vault"

# Or use the skill
/skill weekly-ceo-briefing "Generate Monday CEO briefing"
```

### Setup Automatic Scheduling

**Linux/Mac (cron)**:
```bash
# Edit crontab
crontab -e

# Add: Every Monday at 7:00 AM
0 7 * * 1 cd /path/to/project && python .claude/skills/weekly-ceo-briefing/scripts/weekly_audit.py --vault-path "AI_Employee_Vault"
```

**Windows (Task Scheduler)**:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Weekly on Monday at 7:00 AM
4. Action: `python.exe`
5. Arguments: `.claude\skills\weekly-ceo-briefing\scripts\weekly_audit.py --vault-path "AI_Employee_Vault"`

## Architecture: How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ WEEKLY CEO BRIEFING GENERATION                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. READ DATA SOURCES                                        │
│     ├─ Business_Goals.md (revenue targets, metrics)        │
│     ├─ Tasks/Done/ (completed tasks, performance)           │
│     ├─ Accounting/Current_Month.md (revenue, expenses)     │
│     └─ Dashboard.md (current status)                        │
│                                                              │
│  2. ANALYZE                                                  │
│     ├─ Revenue Analyzer → Total revenue, MTD, trend        │
│     ├─ Bottleneck Detector → Delayed tasks, issues         │
│     ├─ Cost Optimizer → Unused subscriptions, waste         │
│     └─ Performance Metrics → Goals vs actual                │
│                                                              │
│  3. GENERATE BRIEFING                                        │
│     └─ Briefings/YYYY-MM-DD_Monday_Briefing.md             │
│                                                              │
│  4. UPDATE DASHBOARD                                         │
│     └─ Add briefing link to Dashboard.md                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Data Sources

### Required Vault Structure

```
AI_Employee_Vault/
├── Business_Goals.md          # Business objectives, targets, metrics
├── Accounting/
│   └── Current_Month.md       # Revenue, expenses, transactions
├── Tasks/
│   └── Done/                  # Completed tasks with metadata
├── Briefings/                 # Generated briefings (auto-created)
│   └── 2026-01-06_Monday_Briefing.md
└── Dashboard.md               # Updated with briefing link
```

### Business_Goals.md Template

Create this in your vault:

```markdown
# Business Goals

## Q1 2026 Objectives

### Revenue Target
- Monthly goal: $10,000
- Current MTD: $4,500
- Target date: January 31

### Key Metrics to Track

| Metric | Target | Alert Threshold | Current |
|--------|--------|-----------------|---------|
| Client response time | < 24 hours | > 48 hours | 18 hours |
| Invoice payment rate | > 90% | < 80% | 85% |
| Software costs | < $500/month | > $600/month | $450 |

### Active Projects

1. Project Alpha - Due Jan 15 - Budget $2,000 - Status: On Track
2. Project Beta - Due Jan 30 - Budget $3,000 - Status: At Risk

### Subscription Audit Rules

Flag for review if:
- No login in 30 days
- Cost increased > 20%
- Duplicate functionality with another tool
```

### Accounting/Current_Month.md Template

Create this in your vault:

```markdown
# Accounting - January 2026

## Revenue Summary

| Date | Source | Amount | Notes |
|------|--------|--------|-------|
| 2026-01-05 | Client A - Project Alpha | $1,500 | Deposit received |
| 2026-01-10 | Client B - Website | $2,000 | Full payment |
| 2026-01-12 | Consulting - TechCorp | $800 | Hourly work |

**Total Revenue**: $4,300

## Expenses

| Date | Category | Amount | Notes |
|------|----------|--------|-------|
| 2026-01-01 | Software - Adobe CC | $54.99 | Monthly subscription |
| 2026-01-01 | Software - Notion | $15.00 | Monthly subscription |
| 2026-01-03 | Hosting - AWS | $45.00 | Server costs |

**Total Expenses**: $114.99
**Net Profit**: $4,185.01
```

## Output: CEO Briefing Template

Generated briefings follow this structure (saved to `/Briefings/YYYY-MM-DD_Monday_Briefing.md`):

```markdown
---
generated: 2026-01-06T07:00:00Z
period: 2025-12-30 to 2026-01-05
week_number: 1
---

# Monday Morning CEO Briefing - Week of January 6, 2026

## Executive Summary

Strong week with revenue ahead of target. One bottleneck identified in Project Beta.

**Overall Status**: 🟢 On Track

---

## Revenue

### This Week
- **Total**: $4,300
- **Sources**: 3 clients
- **Largest**: Client B ($2,000)

### Month-to-Date
- **Current**: $4,500 (45% of $10,000 target)
- **Trend**: ✅ On track
- **Days Remaining**: 26

### Revenue Trend
```
Week 1: $4,300 ████████████
Target: $10,000 ████████████████████████
```

---

## Completed Tasks

### This Week's Accomplishments

- [x] Client A invoice sent and paid ($1,500)
- [x] Project Alpha milestone 2 delivered
- [x] Weekly social media posts scheduled (3 posts)
- [x] TechCorp consulting completed ($800)

**Total Completed**: 12 tasks
**On-Time Completion**: 92%
**Overdue Tasks**: 1 (Project Beta - design phase)

---

## Bottlenecks

| Task | Expected | Actual | Delay | Root Cause |
|------|----------|--------|-------|------------|
| Project Beta - Design | 2 days | 5 days | +3 days | Waiting for client assets |
| Client C Proposal | 1 day | 2 days | +1 day | Scope clarification needed |

### Bottleneck Analysis

**Critical**: Project Beta design delay
- **Impact**: Milestone at risk
- **Action Required**: Follow up with client today
- **Prevention**: Request all assets upfront in future contracts

---

## Cost Optimization Opportunities

### Software Subscriptions Under Review

**Notion**: No team activity in 45 days
- Cost: $15/month
- Last login: November 22, 2025
- **Recommendation**: Cancel or consolidate to alternative
- **Savings**: $180/year

**Adobe Creative Cloud**: Utilization at 15%
- Cost: $54.99/month
- Used by: 1/5 team members
- **Recommendation**: Review licenses, reassign or cancel unused seats
- **Potential Savings**: $330/year (6 seats)

### Immediate Actions

- [ ] Audit Notion usage by end of week
- [ ] Reassign Adobe licenses by Friday
- [ ] Cancel unused subscriptions by Jan 15

**Total Potential Savings**: $510/year

---

## Upcoming Deadlines

### This Week

| Task | Due Date | Priority | Status |
|------|----------|----------|--------|
| Project Alpha final delivery | Jan 15 | HIGH | On track (9 days) |
| Quarterly tax prep | Jan 31 | MEDIUM | Not started |
| Client D proposal | Jan 10 | HIGH | In progress |

### Next Week

- Project Beta milestone 3 - Jan 20
- Team performance reviews - Jan 22

---

## Proactive Suggestions

### Revenue Growth

1. **Upsell Opportunity**: Client A expressed interest in Phase 2
   - Potential: +$3,000 revenue
   - Action: Schedule call this week

2. **New Lead**: TechCorp mentioned referral opportunity
   - Potential: Unknown
   - Action: Send portfolio this week

### Operational Improvements

1. **Process Gap**: Design phase delays recurring
   - **Fix**: Implement asset collection checklist
   - **Timeline**: Implement by Jan 15

2. **Communication**: Client response time averaging 18 hours (target: 24h)
   - **Status**: ✅ Good
   - **Maintain**: Current practices working well

---

## Metrics Summary

### Goal Progress

| Goal | Target | Current | Status |
|------|--------|---------|--------|
| Monthly Revenue | $10,000 | $4,500 (45%) | 🟢 On track |
| Response Time | < 24h | 18h | 🟢 Exceeding |
| Invoice Payment Rate | > 90% | 85% | 🟡 Below target |
| Software Costs | < $500 | $450 | 🟢 On track |

### Health Score: 85/100

**Breakdown**:
- Revenue: 90/100 (strong performance)
- Operations: 80/100 (one bottleneck)
- Financial: 85/100 (good profit margin)
- Client Satisfaction: 85/100 (payment rate slightly below target)

---

## Action Items for CEO

### Today (High Priority)
- [ ] Follow up with Project Beta client for missing assets
- [ ] Send portfolio to TechCorp referral

### This Week (Medium Priority)
- [ ] Audit Notion usage
- [ ] Reassign Adobe licenses
- [ ] Schedule Client A upsell call
- [ ] Start quarterly tax preparation

### Review Items (Low Priority)
- [ ] Update pricing based on market rates
- [ ] Review Project Alpha lessons learned
- [ ] Plan Q2 objectives

---

## Notes

- No critical issues this week
- Business operations running smoothly
- Revenue tracking well ahead of target
- Focus on eliminating Project Beta bottleneck

---

*Generated by AI Employee v1.0 (Gold Tier)*
*Report Period: December 30, 2025 - January 5, 2026*
```

## Key Scripts

### 1. weekly_audit.py

Main orchestration script that:
1. Reads all data sources
2. Calls analysis modules
3. Generates briefing document
4. Updates dashboard

**Usage**:
```bash
python scripts/weekly_audit.py --vault-path "AI_Employee_Vault"
```

### 2. revenue_analyzer.py

Analyzes revenue from:
- Accounting/Current_Month.md
- Tasks/Done/ (for completed project revenue)
- Business_Goals.md (for targets)

**Calculates**:
- Total revenue (week, MTD, projected)
- Revenue trend
- Goal progress percentage
- Revenue sources breakdown

### 3. bottleneck_detector.py

Identifies bottlenecks from:
- Tasks/Done/ metadata (completion time vs expected)
- Overdue tasks
- Delayed milestones
- Recurring issues

**Categories**:
- Critical (immediate action required)
- High (address this week)
- Medium (plan for next week)
- Low (monitor)

### 4. cost_optimizer.py

Analyzes expenses and identifies:
- Unused software subscriptions
- Duplicate tools
- Cost increases (> 20%)
- Optimization opportunities

**Outputs**:
- Actionable savings recommendations
- Priority-ranked cost cuts
- Implementation timeline

### 5. briefing_generator.py

Generates the markdown briefing document by:
1. Loading CEO_Briefing.md template
2. Populating with analysis results
3. Adding calculated metrics
4. Formatting sections
5. Saving to `/Briefings/` folder

## Integration with Vault

### Dashboard Updates

After generating briefing, updates `Dashboard.md`:

```markdown
## Latest CEO Briefing

- **Week of**: January 6, 2026
- **Health Score**: 85/100
- **Revenue**: $4,300 MTD ($4,500 total)
- **Status**: 🟢 On track
- **Full Report**: [Briefings/2026-01-06_Monday_Briefing.md](Briefings/2026-01-06_Monday_Briefing.md)
```

### Cross-References

Briefings link to:
- Specific tasks in `Tasks/Done/`
- Accounting entries in `Accounting/`
- Goals in `Business_Goals.md`
- Previous briefings for trend analysis

## Configuration

### Environment Variables (.env)

```bash
# Weekly Briefing Settings
BRIEFING_DAY=monday
BRIEFING_TIME=07:00
BRIEFING_TIMEZONE=America/New_York

# Analysis Thresholds
BOTTLENECK_THRESHOLD_DAYS=2     # Flag tasks delayed > 2 days
COST_INCREASE_THRESHOLD=20      # Flag cost increases > 20%
LOW_USAGE_THRESHOLD_DAYS=30     # Flag unused subscriptions (30 days)

# Briefing Content
INCLUDE_METRICS_CHARTS=true     # Generate ASCII charts
INCLUDE_ACTION_ITEMS=true       # Add CEO action items
INCLUDE_COST_OPTIMIZATION=true  # Analyze costs
```

### Company_Handbook.md Integration

Add this section to your handbook:

```markdown
## Weekly CEO Briefing

### Schedule
- Generated: Every Monday at 7:00 AM
- Review time: 15 minutes recommended
- Action items: Prioritize High items

### Briefing Sections
1. Executive Summary
2. Revenue Analysis
3. Completed Tasks
4. Bottlenecks
5. Cost Optimization
6. Upcoming Deadlines
7. Proactive Suggestions
8. Action Items

### Response Protocol
- Health Score < 70: Immediate review required
- Health Score 70-85: Review within 24 hours
- Health Score > 85: Review when convenient
```

## Scheduling Automation

### Cron Schedule Examples

**Every Monday at 7 AM**:
```cron
0 7 * * 1 cd /path/to/project && python .claude/skills/weekly-ceo-briefing/scripts/weekly_audit.py
```

**First Monday of every month at 8 AM**:
```cron
0 8 1-7 * * [ "$(date '+\%u')" = "1" ] && cd /path/to/project && python .claude/skills/weekly-ceo-briefing/scripts/weekly_audit.py
```

**Every Monday, Wednesday, Friday at 9 AM** (more frequent):
```cron
0 9 * * 1,3,5 cd /path/to/project && python .claude/skills/weekly-ceo-briefing/scripts/weekly_audit.py
```

## Troubleshooting

### Common Issues

**Issue**: "Business_Goals.md not found"

**Solution**: Create the template in your vault root:
```bash
cp templates/Business_Goals.md AI_Employee_Vault/
```

**Issue**: "No revenue data found"

**Solution**: Ensure `Accounting/Current_Month.md` exists with revenue entries

**Issue**: "No completed tasks analyzed"

**Solution**: Ensure tasks are being moved to `Tasks/Done/` with proper metadata

**Issue**: Briefing not generating automatically

**Solution**: Check cron/task scheduler logs:
```bash
# Linux/Mac
grep CRON /var/log/syslog

# Windows
# Check Task Scheduler → Task History
```

## Customization

### Custom Analysis Modules

Add custom analysis by creating new modules in `scripts/`:

**Example: customer_satisfaction_analyzer.py**
```python
def analyze_customer_satisfaction(vault_path):
    """Analyze customer feedback and satisfaction."""
    # Read customer feedback from vault
    # Calculate satisfaction score
    # Return metrics for briefing
    pass
```

Then integrate in `weekly_audit.py`:
```python
from customer_satisfaction_analyzer import analyze_customer_satisfaction

# In main briefing generation
satisfaction_metrics = analyze_customer_satisfaction(vault_path)
```

### Custom Briefing Sections

Add custom sections by editing `templates/CEO_Briefing.md`:

```markdown
## Custom Section

### My Custom Metrics

| Metric | Value |
|--------|-------|
| Custom KPI 1 | {{ custom_value_1 }} |
| Custom KPI 2 | {{ custom_value_2 }} |
```

Then populate in `briefing_generator.py`:
```python
briefing_content = briefing_content.replace('{{ custom_value_1 }}', str(custom_value_1))
```

## References

See `references/business-metrics.md` for detailed metric definitions.

See `templates/CEO_Briefing.md` for the complete briefing template.
