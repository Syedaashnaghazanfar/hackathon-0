# Contracts: Vault Artifacts (Bronze)

This document defines the file-based contracts used by the Bronze tier AI Employee.

## Vault Root

Default vault root convention:
- `My_AI_Employee/AI_Employee_Vault/`

Required contents:
- Folders: `Inbox/`, `Needs_Action/`, `Done/`
- Files: `Dashboard.md`, `Company_Handbook.md`

Optional:
- `Plans/`

## Action Item Contract (Needs_Action)

- **Location**: `Needs_Action/*.md`
- **Format**: Markdown with YAML frontmatter.

Recommended minimum YAML frontmatter:

```yaml
---
type: file_drop
received: 2026-01-13T00:00:00Z
status: pending
priority: auto
source_id: FILE_example_20260113_000000
---
```

Content expectations:
- Must include a reference to the original dropped file path for `type: file_drop`.

## Plan Contract

- **Location**: `Plans/` if present.
- **Format**: Markdown.

Content expectations:
- Must include actionable checkbox steps.
- Must include a done condition.
- Should link back to its source action item.

## Archive Contract (Done)

- **Location**: `Done/*.md`
- Must preserve the original YAML frontmatter.
- Must record `status: processed`.

## Dashboard Contract

- **Location**: `Dashboard.md`
- Must be updated non-destructively.
- Should contain:
  - pending counts
  - recent activity
  - warnings / manual review needed
