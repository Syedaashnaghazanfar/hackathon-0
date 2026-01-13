---
name: obsidian-vault-ops
description: >
  Safely operate on an Obsidian vault used as the "Memory/GUI" for Hackathon Zero.
  This skill should be used when the user asks to "create an Obsidian vault", "set up Dashboard.md",
  "update Company_Handbook.md", "read/write markdown in the vault", "move items between /Inbox, /Needs_Action, /Done",
  "organize the vault", "rename or relocate vault files", or when Claude needs to perform ANY filesystem actions inside the vault
  (read, create, edit, move) while preserving YAML frontmatter and avoiding destructive changes.
  Trigger phrases include: "update the dashboard", "check the vault", "move to Done", "create Needs_Action file",
  "vault folder structure", "Obsidian file ops", and "preserve frontmatter".
---

# Obsidian Vault Ops

Operate on the Obsidian vault as a **local-first task/memory system**.

Keep this skill narrowly focused on:
- Reading/writing markdown files in the vault
- Creating/ensuring the required Bronze-tier folder structure
- Moving processed items between folders
- Updating `Dashboard.md` and `Company_Handbook.md` without clobbering user content

## Workflow decision tree

1. **Need to find the vault root?**
   - Follow “Locate the vault root”.
2. **Need to ensure folders/files exist?**
   - Follow “Ensure Bronze vault structure”.
3. **Need to update a markdown file safely?**
   - Follow “Safe edit rules”.
4. **Need to archive/move an item?**
   - Follow “Safe move rules”.

## Locate the vault root

Determine the vault root using, in order:
1. A user-provided absolute path
2. A repo convention (e.g., `MY-AI-EMPLOYEE/` if the project stores the vault there)
3. A folder containing both `Dashboard.md` and `Company_Handbook.md`

If multiple candidates exist, stop and ask for confirmation before writing.

## Ensure Bronze vault structure

Ensure these exist under the vault root (create if missing):
- `Dashboard.md`
- `Company_Handbook.md`
- `Inbox/`
- `Needs_Action/`
- `Done/`

Use templates:
- `templates/DashboardTemplate.md`
- `templates/CompanyHandbookTemplate.md`

## Safe edit rules (non-negotiable)

- Read a file before editing it.
- Preserve YAML frontmatter exactly (unless explicitly asked to change it).
- Do not delete user content.
- Prefer **append** or **surgical section replacement** over rewriting entire files.
- When updating dashboards, preserve any user-custom sections below a clear separator line.

See `references/safety-rules.md` for the exact invariants.

## Safe move rules

- Never move files outside the vault.
- Never delete files.
- When archiving an item from `Needs_Action/` to `Done/`, add minimal processing metadata:
  - `processed: <ISO_TIMESTAMP>`
  - `result: planned|triaged|error`
  - `related_plan: <path>` if applicable

See `references/vault-conventions.md` for naming conventions.

## Resources

- Reference: `references/vault-conventions.md`
- Reference: `references/safety-rules.md`
- Examples: `examples.md`
- Templates: `templates/DashboardTemplate.md`, `templates/CompanyHandbookTemplate.md`
