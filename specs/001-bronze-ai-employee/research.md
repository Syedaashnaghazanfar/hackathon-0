# Research: Bronze Tier AI Employee

**Feature**: `specs/001-bronze-ai-employee/spec.md`
**Branch**: `001-bronze-ai-employee`
**Date**: 2026-01-13

## Decision 1: Filesystem watching approach

**Decision**: Use `watchdog` for filesystem watching.

**Rationale**:
- Provides a straightforward Python API (`Observer`, `FileSystemEventHandler`) for directory monitoring.
- Supports a polling-based observer for environments where native filesystem events are unreliable (e.g., CIFS / some WSL setups) by importing `PollingObserver`.

**Alternatives considered**:
- Polling-only implementation: simpler but less responsive and requires manual scanning logic.

**Notes / References**:
- `watchdog` basic observer pattern and graceful shutdown uses `observer.start()`, `observer.stop()`, and `observer.join()`.
- For CIFS/polling: `from watchdog.observers.polling import PollingObserver as Observer`.

## Decision 2: YAML frontmatter parsing

**Decision**: Use `python-frontmatter` to load and write Markdown action items with YAML frontmatter.

**Rationale**:
- Simple API to `load()` and access metadata via `post[...]`.
- Can serialize back via `frontmatter.dumps(post)` or write via `frontmatter.dump(post, file)`.
- Allows preserving and updating metadata (e.g., `status`) while keeping content intact.

**Alternatives considered**:
- Manual YAML parsing via `PyYAML` + custom delimiter parsing: fewer dependencies but higher risk of edge-case bugs.

## Decision 3: Duplicate prevention strategy

**Decision**: Track processed items using stable identifiers derived from the dropped file (e.g., hash of absolute path + size + mtime) and store dedupe state outside the vault.

**Rationale**:
- Prevents duplicate action items for repeated events.
- Storing outside the vault respects “vault as source of truth for artifacts” while keeping operational state from cluttering user notes.

**Alternatives considered**:
- Storing dedupe markers inside the vault: simpler visibility, but risks polluting user content and complicating safety rules.

## Decision 4: Error handling / reliability

**Decision**: Watcher and triage must log errors and continue running; malformed action items remain in `Needs_Action/` and produce a dashboard warning.

**Rationale**:
- Aligns with constitution resilience and non-destructive vault safety requirements.

