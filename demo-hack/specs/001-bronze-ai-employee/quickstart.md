# Quickstart: Bronze Tier AI Employee

## Prereqs

- Python 3.13+
- uv
- pytest
- Obsidian vault path: `My_AI_Employee/AI_Employee_Vault/`

## Local Vault Setup (Bronze)

Required structure:

```text
My_AI_Employee/AI_Employee_Vault/
├── Inbox/
├── Needs_Action/
├── Done/
├── Dashboard.md
└── Company_Handbook.md
```

Optional:

```text
My_AI_Employee/AI_Employee_Vault/Plans/
```

## Running the Bronze Loop

1) Start the filesystem watcher using the skill:
- `@watcher-runner-filesystem`

2) Drop a file into your watch folder.

3) Process pending items using the triage skill:
- `@needs-action-triage`

4) Validate end-to-end readiness:
- `@bronze-demo-check`

## Notes

- Bronze tier must not use MCP servers or perform any external actions.
- If filesystem events are unreliable (common on some WSL/network paths), use the watcher polling mode described in the implementation plan.
