---
id: 0001
title: Bronze Tier Constitution
stage: constitution
date: 2026-01-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: uneezaismail
command: /sp.constitution
labels: ["constitution","hackathon-zero","bronze-tier","obsidian","claude-code","spec-kit-plus"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - history/prompts/constitution/0001-bronze-tier-constitution.constitution.prompt.md
tests:
 - none
---

## Prompt

Create a project constitution for “My AI Employee” (Hackathon Zero) focused strictly on Bronze tier.

  ## 1) Project goal
  Build a local-first Personal AI Employee using:
  - Obsidian as the “Memory/GUI” (markdown vault)
  - Python watcher script(s) as the “Senses” (start with filesystem watcher)
  - Claude Code as the “Reasoning engine”
  - All AI behavior expressed as Claude Code Agent Skills (stored under `.claude/skills`)

  ## 2) Bronze-tier scope (non-negotiable)
  - Must produce an Obsidian vault containing: `Dashboard.md` and `Company_Handbook.md`
  - Must maintain vault folders: `Inbox/`, `Needs_Action/`, `Done/` (optionally allow `Plans/`)
  - Must have one working watcher (filesystem watcher preferred) that writes markdown action items into `Needs_Action/`
  - Claude Code must read from and write to the vault (plan generation + dashboard updates + archiving to `Done/`)
  - NO MCP servers and NO external actions in Bronze (no sending emails, no posting, no payments)

  ## 3) Local-first + safety principles
  - Never delete user content in the vault; prefer append/section updates
  - Preserve YAML frontmatter when moving/processing markdown items
  - No secrets in repo; credentials must be via `.env` and excluded from git
  - “Human as tool” principle: ask for clarification when vault root/path is ambiguous or when an action could overwrite user-authored notes

  ## 4) Technology & implementation constraints
  - Python 3.13+ (or latest available), uv for packaging, pytest for tests
  - Prefer simple, minimal diffs (no unrelated refactors)
  - Watcher should be resilient: log errors and keep running; prevent duplicate processing (tracked IDs or hashes)
  - Vault path convention for this repo: `My_AI_Employee/AI_Employee_Vault/`

  ## 5) Quality gates
  - Tests required for watcher core logic and action-item formatting
  - Basic lint/format (keep consistent; no heavy tooling requirements unless already in repo)
  - All tasks must be demonstrable with an end-to-end Bronze demo:
    drop file → `Needs_Action` item → Claude processes → plan + dashboard update → item moved to `Done/`

  ## 5a) Artifact conventions (Bronze)

  ### Action Item Contract (Needs_Action)
  - Action items MUST be Markdown files stored under `Needs_Action/`.
  - Action items SHOULD include YAML frontmatter with (at minimum):
    - `type`: `email|file_drop|manual`
    - `received`: ISO timestamp
    - `status`: `pending|processed`
    - `priority`: `high|medium|low|auto` (optional)
    - optional: `source_id`, `from`, `subject`

  ### Plan output location
  - Plans MUST be written to `Plans/` when that folder exists (recommended).
  - If `Plans/` is not used, the chosen plan output location MUST be consistent and documented in the feature spec.

  ### Watcher file handling default
  - Default behavior: the watcher writes a Markdown action item that references the original dropped file path (metadata-only).
  - Copying dropped files into the vault is OPTIONAL and must be an explicit design choice documented in the plan (and ADR if it has long-term impact).

  ## 6) Governance
  - Constitution supersedes specs/plans/tasks when there is conflict
  - Significant architecture choices (e.g., whether watcher copies dropped files into vault vs metadata-only links) should be documented via ADR when they have long-term impact and alternatives
  - Amendments require updating constitution version and noting rationale
  - All automation must be runnable via Claude Code prompts invoking skills; no hidden manual steps besides starting the watcher

## Response snapshot

- Updated `.specify/memory/constitution.md` by replacing all template placeholders with concrete Bronze-tier principles.
- Added a Sync Impact Report at the top, set constitution version to 1.0.0, and recorded deferred ratification date as a TODO.
- Added Bronze artifact conventions: action item contract, plan output location, and watcher file handling default.
- Validated there are no remaining `[PLACEHOLDER]` tokens.

## Outcome

- ✅ Impact: Established Bronze-first project constitution guiding all subsequent spec/plan/tasks and implementation.
- 🧪 Tests: Not applicable (documentation update).
- 📁 Files: Updated constitution and created this PHR.
- 🔁 Next prompts: Run `/sp.specify` for the Bronze feature (vault + filesystem watcher + triage loop) referencing the constitution.
- 🧠 Reflection: Kept constitution Bronze-only (no Silver HITL/MCP requirements) to avoid scope creep.

## Evaluation notes (flywheel)

- Failure modes observed: None.
- Graders run and results (PASS/FAIL): Not run
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Fill `RATIFICATION_DATE` once you confirm the intended project adoption date.
