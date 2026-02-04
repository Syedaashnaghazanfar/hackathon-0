---
name: bronze-demo-check
description: >
  Validate and demonstrate Hackathon Zero Bronze tier end-to-end (Perception → Reasoning → Write-back)
  using a filesystem watcher + Obsidian vault + Claude Code skills.
  This skill should be used when the user asks to "demo Bronze tier", "validate Bronze deliverables",
  "run the end-to-end test", "prove the watcher-to-vault loop works", "check my submission readiness",
  or "generate a demo checklist".
  Trigger phrases include: "Bronze tier checklist", "end-to-end", "smoke test", "judge demo", and "acceptance criteria".
---

# Bronze Demo Check

Run a repeatable end-to-end check:
1) vault exists and is writable
2) watcher creates `Needs_Action` items
3) Claude processes and writes back plans/dashboard updates
4) items get archived to `Done/`

## Checklist

Follow `references/bronze-acceptance.md`.

## Outputs to show in the demo

- Vault tree showing required files/folders
- A newly created `Needs_Action/*.md`
- A generated plan file
- An updated `Dashboard.md`
- The original item moved to `Done/`

## Resources

- Reference: `references/bronze-acceptance.md`
- Example demo script (human-readable): `templates/DemoRun.md`
- Examples: `examples.md`
