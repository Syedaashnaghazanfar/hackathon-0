# Bronze tier acceptance (Hackathon Zero)

Source requirement: `HACKATHON-ZERO.md:163-168`.

## Required artifacts

- [ ] Obsidian vault contains `Dashboard.md`
- [ ] Obsidian vault contains `Company_Handbook.md`
- [ ] Vault contains folders: `Inbox/`, `Needs_Action/`, `Done/`
- [ ] One watcher works (filesystem watcher OR Gmail watcher)
- [ ] Claude Code can read/write the vault
- [ ] AI functionality is implemented as Agent Skills

## End-to-end proof (filesystem watcher path)

- [ ] Start filesystem watcher (`@watcher-runner-filesystem`)
- [ ] Drop a test file into WATCH_FOLDER
- [ ] Confirm watcher created a new `Needs_Action/*.md`
- [ ] Run Claude processing (`@needs-action-triage`)
- [ ] Confirm a plan file exists (location depends on your convention)
- [ ] Confirm `Dashboard.md` updated (timestamp + counts)
- [ ] Confirm original action item moved to `Done/`

## Failure paths to demonstrate handling

- [ ] Malformed action item stays in `Needs_Action/` and dashboard shows warning
- [ ] Missing `Company_Handbook.md` falls back to default triage rules
