# Filesystem watcher runbook (Bronze)

## Inputs

- `VAULT_PATH`: absolute path to the Obsidian vault
- `WATCH_FOLDER`: absolute path to a local folder to monitor for new files

## Expected behavior

- On a new file created in WATCH_FOLDER, the watcher should:
  - create a corresponding markdown action item in `Needs_Action/` (e.g., `FILE_<name>.md`)
  - optionally copy the dropped file into the vault (only if you choose that design)

## Common failure modes

- Wrong vault path → action files written somewhere else
- Permissions → watcher cannot write to vault
- Missing dependency (`watchdog`) → watcher crashes on import
- Platform-specific file events not delivered (network drive / WSL) → switch to polling approach

## Minimal smoke test

- Start watcher
- Run `scripts/create_test_drop.py <WATCH_FOLDER>`
- Confirm a new `.md` appears in `Needs_Action/`
