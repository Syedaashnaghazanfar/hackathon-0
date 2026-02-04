# Obsidian vault conventions (Bronze)

## Required top-level items

- `Dashboard.md`
- `Company_Handbook.md`
- `Inbox/`
- `Needs_Action/`
- `Done/`

## Naming conventions

### Action items (inputs)

Store new actionable items in `Needs_Action/` as markdown.
Recommended filenames:
- `ACTION_<slug>_<YYYYMMDD-HHMMSS>.md`
- `EMAIL_<id>.md` (Gmail watcher)
- `FILE_<original_filename>.md` (filesystem watcher)

### Plans (outputs)

If the Bronze flow generates plans, store them in a predictable place (choose one and stick to it):
- Option A: `Plans/PLAN_<slug>_<YYYYMMDD-HHMMSS>.md`
- Option B: `Needs_Action/` item gets updated in-place with a Plan section (avoid for Bronze unless required)

## Minimal frontmatter conventions

Action items should prefer this minimal frontmatter:

```yaml
---
type: email|file_drop|manual
received: 2026-01-12T00:00:00Z
status: pending
priority: high|medium|low|auto
---
```

Archive metadata (when moving to Done):

```yaml
processed: 2026-01-12T00:00:00Z
result: planned|triaged|error
related_plan: Plans/PLAN_example.md
```
