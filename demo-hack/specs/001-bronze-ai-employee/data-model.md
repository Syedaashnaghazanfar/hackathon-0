# Data Model: Bronze Tier AI Employee

This feature is local-file based and does not require a database. The “data model” is represented as a set of Markdown artifacts in the Obsidian vault plus a small local (non-vault) state file used for deduplication.

## Entities

### Vault
- **Represents**: The Obsidian vault directory used as the system’s source of truth.
- **Key paths (required)**:
  - `Inbox/`
  - `Needs_Action/`
  - `Done/`
  - `Dashboard.md`
  - `Company_Handbook.md`
- **Key paths (optional)**:
  - `Plans/`

### Action Item (Markdown file)
- **Location**: `Needs_Action/` (pending) → `Done/` (processed)
- **Format**: Markdown with YAML frontmatter.
- **Minimum frontmatter fields**:
  - `type`: `email|file_drop|manual`
  - `received`: ISO timestamp
  - `status`: `pending|processed`
- **Optional fields**:
  - `priority`: `high|medium|low|auto`
  - `source_id`, `from`, `subject`

### Plan (Markdown file)
- **Location**: `Plans/` when present (otherwise consistent alternate location)
- **Represents**: Concrete next steps for a specific action item.
- **Content expectations**:
  - actionable checkbox list
  - done condition
  - reference to the source action item

### Dashboard (Markdown file)
- **Location**: `Dashboard.md`
- **Represents**: System status summary.
- **Content expectations**:
  - pending count
  - recent activity
  - warnings (e.g., malformed items)

### Dedupe State (local non-vault file)
- **Location**: Outside the vault (exact path to be defined in implementation).
- **Represents**: Set of processed IDs/hashes so the watcher does not generate duplicate action items.
- **Notes**: Must not be user-authored content; must be safe to regenerate.
