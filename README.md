# Hackathon Zero - My AI Employee

A multi-tier AI employee system that monitors, processes, and acts on information from various sources. Currently implements the **Bronze Tier** (Perception Layer) with filesystem watching and Obsidian vault integration.

## Quick Start

```bash
# Navigate to Bronze tier
cd My_AI_Employee

# Install dependencies
uv sync

# Start the watcher
uv run python -m my_ai_employee.run_watcher

# In another terminal, drop a test file
echo "Test content" > watch_folder/test.txt

# Check the created action item
cat AI_Employee_Vault/Needs_Action/FILE_test_*.md
```

## Implementation Tiers

### Bronze Tier (Current - COMPLETE)
**Perception Layer**: Filesystem watcher creates action items in Obsidian vault

**Features:**
- Monitors watch folder for new files
- Creates action items with YAML frontmatter
- Prevents duplicates via stable IDs
- Error resilient
- 11/11 tests passing

### Silver Tier (Future)
**Reasoning Layer**: AI-powered triage and planning

**Planned:**
- Claude Code integration
- Priority detection
- Automated plan generation
- Dashboard analytics
- Email watcher (Gmail)

### Gold Tier (Future)
**Action Layer**: Autonomous task execution

**Planned:**
- Automated task execution
- Slack integration
- Email responses
- Workflow automation

## Project Structure

```
My_AI_Employee/
├── README.md                    # This file
├── My_AI_Employee/              # Bronze tier
│   ├── src/my_ai_employee/     # Source code
│   ├── tests/                  # Tests (11 passing)
│   ├── AI_Employee_Vault/      # Obsidian vault
│   └── watch_folder/           # Drop files here
├── specs/                      # Specifications
└── history/                    # Dev history
```

## Testing

```bash
cd My_AI_Employee
uv run pytest tests/ -v
# Expected: 11/11 passing
```

## Feature Comparison

| Feature | Bronze | Silver | Gold |
|---------|--------|--------|------|
| Filesystem Watching | ✓ | ✓ | ✓ |
| Action Items | ✓ | ✓ | ✓ |
| Deduplication | ✓ | ✓ | ✓ |
| Email Monitoring | - | ✓ | ✓ |
| AI Triage | - | ✓ | ✓ |
| Task Execution | - | - | ✓ |

## Documentation

- [Specification](specs/001-bronze-ai-employee/spec.md)
- [Architecture](specs/001-bronze-ai-employee/plan.md)
- [Tasks](specs/001-bronze-ai-employee/tasks.md)
- [Detailed README](My_AI_Employee/README.md)

## Status

**Bronze Tier: Complete ✓**  
**Silver & Gold: Coming Soon**

Built for Hackathon Zero
