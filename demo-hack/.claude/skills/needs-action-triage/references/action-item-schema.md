# Action item schema (Bronze)

## Required fields (frontmatter)

```yaml
---
type: email|file_drop|manual
received: 2026-01-12T00:00:00Z
status: pending
---
```

## Optional fields

```yaml
from: someone@example.com
subject: "Invoice request"
priority: high|medium|low|auto
source_id: "EMAIL_123"|"FILE_abc"
```

## Required body sections (recommended)

```markdown
## Content
<primary content>

## Metadata
<watcher-provided context>
```

## Malformed handling

If frontmatter is missing or invalid:
- Do not rewrite the file.
- Create a short plan titled "Manual review required".
- Leave the item in `Needs_Action/`.
