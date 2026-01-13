# Bronze Tier AI Employee

Filesystem watcher that creates action items in an Obsidian vault for Bronze-tier AI employee workflows.

## Quick Start

```bash
# Install dependencies
cd My_AI_Employee && uv sync

# Start watcher
uv run python -m my_ai_employee.run_watcher

# Drop files into watch_folder/ - action items appear in AI_Employee_Vault/Needs_Action/
```

## Features

- 🔍 Filesystem watching (native events + polling fallback for WSL)
- 📝 Action items with YAML frontmatter (type, received, status)
- 🛡️ Deduplication via stable file IDs  
- ⚡ Error resilient - continues after failures
- ✅ 11/11 tests passing

## Configuration

Edit `.env` or use command line:

```bash
uv run python -m my_ai_employee.run_watcher \
  --vault-path ./AI_Employee_Vault \
  --watch-folder ./watch_folder \
  --watch-mode events  # or polling for WSL/CIFS
```

## Vault Structure

```
AI_Employee_Vault/
├── Needs_Action/  # Watcher writes here
├── Done/          # Archived items
├── Plans/         # Generated plans
├── Dashboard.md
└── Company_Handbook.md
```

## Testing

```bash
uv run pytest tests/ -v  # 11/11 passing
```

## Documentation

- Full specs: `specs/001-bronze-ai-employee/`
- Architecture: `specs/001-bronze-ai-employee/plan.md`
- Contracts: `specs/001-bronze-ai-employee/contracts/`

## Claude Code Skills

- `@watcher-runner-filesystem` - Run and test watcher
- `@obsidian-vault-ops` - Create vault structure
- `@bronze-demo-check` - Validate Bronze tier

## Status

**Bronze MVP Complete**: Filesystem watcher functional, tested, and documented.
