---
id: 0001
title: Bronze Tier Specification
stage: spec
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-bronze-ai-employee
branch: 001-bronze-ai-employee
user: uneezaismail
command: /sp.specify
labels: ["spec","bronze-tier","ai-employee","watcher","obsidian","claude-code","spec-kit-plus"]
links:
  spec: specs/001-bronze-ai-employee/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-bronze-ai-employee/spec.md
 - specs/001-bronze-ai-employee/checklists/requirements.md
 - history/prompts/001-bronze-ai-employee/0001-bronze-tier-specification.spec.prompt.md
tests:
 - none
---

## Prompt

Build “My AI Employee” (Hackathon Zero) — Bronze Tier only.

  ## Goal (what/why)
  Build a local-first Personal AI Employee where an Obsidian vault is the single source of truth for tasks and status. A Python watcher creates actionable markdown items, and Claude Code processes those items into plans and dashboard updates.

  ## Bronze scope (non-negotiable)
  - MUST be Bronze tier only.
  - MUST NOT use MCP servers or perform external actions (no sending emails, no posting, no payments).
  - MUST implement all AI behavior as Claude Code Agent Skills stored under `.claude/skills/`.

  ## Vault source of truth
  Use this vault root convention:
  - Vault root: `My_AI_Employee/AI_Employee_Vault/`

  Vault must include:
  - Files: `Dashboard.md`, `Company_Handbook.md`
  - Folders: `Inbox/`, `Needs_Action/`, `Done/`
  - SHOULD allow `Plans/` folder (recommended)

  ## Watcher (one watcher only for Bronze)
  Implement one working watcher: filesystem watcher.
  - It monitors a user-provided “drop folder” path.
  - When a file is dropped, it creates ONE Markdown action item in `Needs_Action/`.
  - Default: action item references the original dropped file path (metadata-only; copying into vault is optional and must be explicit).

  ## Action item contract (Needs_Action)
  Action items MUST be markdown files in `Needs_Action/` and SHOULD include YAML frontmatter:
  - type: email|file_drop|manual
  - received: ISO timestamp
  - status: pending|processed
  - priority: high|medium|low|auto (optional)
  - optional: source_id, from, subject

  ## Claude reasoning loop (skills-driven)
  Claude Code must be able to:
  - Read `Needs_Action/` items (pending)
  - Read `Company_Handbook.md` as operating rules
  - Create a plan file per item (write to `Plans/` if it exists)
  - Update `Dashboard.md` with counts + recent activity
  - Move processed action items to `Done/` while preserving YAML frontmatter and adding processed metadata
  - Never delete user-authored vault content
  - MUST implement the action-item processing workflow via a Claude Code Agent Skill (e.g., `@needs-action-triage`) stored under `.claude/skills/`.

  ## Failure-path expectations
  - If an action item is malformed (e.g., invalid/missing required frontmatter), MUST NOT delete it and MUST NOT move it to `Done/`.
  - Malformed items MUST remain in `Needs_Action/`, a dashboard warning MUST be added, and processing MUST continue for other items.

  ## End-to-end demo acceptance criteria (Bronze)
  Provide acceptance criteria for a demonstrable loop:
  1) Drop a file into the watch folder
  2) A new `Needs_Action/*.md` is created (correct frontmatter)
  3) Claude triage produces a plan file and updates the dashboard
  4) The processed item is moved to `Done/` (not deleted)

  ## Quality gates
  - MUST include tests (pytest) for watcher core logic and action-item formatting.
  - Watcher must be resilient: log errors, continue running, and prevent duplicates (tracked IDs/hashes).
  - No secrets committed; config via `.env` (gitignored) if needed.

## Response snapshot

- Created `specs/001-bronze-ai-employee/spec.md` with prioritized, independently testable user stories (P1–P5) covering watcher output, triage, dashboard visibility, vault setup, and action-item format.
- Defined edge cases and a complete set of functional requirements (FR-001+) aligned to Bronze constraints (no MCP/external actions), vault safety, and skills-driven processing.
- Added measurable success criteria for the end-to-end Bronze demo loop.
- Created `specs/001-bronze-ai-employee/checklists/requirements.md` and validated the spec (all items pass).

## Outcome

- ✅ Impact: Established a complete Bronze-tier feature specification ready for planning.
- 🧪 Tests: Not applicable (spec phase).
- 📁 Files: Created the feature spec, a spec quality checklist, and this PHR.
- 🔁 Next prompts: Run `/sp.plan` to design the implementation, then `/sp.tasks` to generate executable tasks.
- 🧠 Reflection: Kept scope strictly Bronze (local-first vault + one watcher + skills-driven triage) with safety and testability requirements.

## Evaluation notes (flywheel)

- Failure modes observed: None.
- Graders run and results (PASS/FAIL): Spec quality checklist - all PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Consider whether the watcher should default to filesystem events vs polling on WSL paths, and capture that decision during `/sp.plan`.
