# Safety rules for vault file operations

These rules exist to prevent accidental data loss in a local-first Obsidian vault.

## Invariants

- Do not delete files.
- Do not move files outside the vault root.
- Preserve YAML frontmatter unless explicitly instructed.
- Prefer incremental updates over full rewrites.

## Dashboard update rule

If `Dashboard.md` contains a separator line like:

```markdown
---
*Auto-generated above. User notes below.*
```

Only update the auto-generated section above the separator.

## Editing strategy

- For small edits: use exact string replacement with tight context.
- For larger changes: rewrite only the target section.

## When to stop and ask

Stop and ask the user when:
- The vault root is ambiguous.
- A move would cross vault boundaries.
- A file appears to be user-authored and the requested change might overwrite substantial content.
