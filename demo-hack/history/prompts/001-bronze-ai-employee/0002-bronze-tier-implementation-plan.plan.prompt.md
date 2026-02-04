---
id: 0002
title: Bronze Tier Implementation Plan
stage: plan
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-bronze-ai-employee
branch: 001-bronze-ai-employee
user: uneezaismail
command: /sp.plan
labels: ["plan","bronze-tier","ai-employee","watcher","obsidian","claude-code","spec-kit-plus"]
links:
  spec: specs/001-bronze-ai-employee/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-bronze-ai-employee/plan.md
 - specs/001-bronze-ai-employee/research.md
 - specs/001-bronze-ai-employee/data-model.md
 - specs/001-bronze-ai-employee/quickstart.md
 - specs/001-bronze-ai-employee/contracts/vault-artifacts.md
 - CLAUDE.md
 - history/prompts/001-bronze-ai-employee/0002-bronze-tier-implementation-plan.plan.prompt.md
tests:
 - none
---

## Prompt

Create the implementation plan for the Bronze Tier AI Employee feature (`specs/001-bronze-ai-employee/spec.md`) under the project constitution (`.specify/memory/constitution.md`).

  ## Scope (Bronze-only, non-negotiable)
  - Implement ONLY Bronze tier: local Obsidian vault + one filesystem watcher + Claude vault I/O + Agent Skills.
  - NO MCP servers and NO external actions.
  - Preserve vault safety: never delete user-authored content; preserve YAML frontmatter.

  ## Tech stack (guardrails)
  - Python 3.13+
  - uv for packaging
  - pytest for tests
  - Local filesystem Obsidian vault at `My_AI_Employee/AI_Employee_Vault/`

  ## Use Agent Skills (non-negotiable)
  - All AI workflows MUST be expressed via skills under `.claude/skills/`.
  - Reuse the existing skills already created in this repo (e.g., `@watcher-runner-filesystem`, `@needs-action-triage`, `@obsidian-vault-ops`, `@bronze-demo-check`) and plan the implementation so the end-to-end demo can be run by invoking these skills.
  - Avoid “hidden manual steps” other than starting the watcher.

  ## Use Context7 for documentation/research (required)
  - Whenever selecting a Python library (e.g., filesystem watching approach, YAML/frontmatter parsing, hashing/dedupe), query Context7 for the latest docs/examples and capture key findings in `research.md` (or within plan sections if that’s the template used).
  - Prefer minimal dependencies; justify any non-standard library additions.

  ## Required outputs (plan artifacts)
  Produce a concrete technical plan in `specs/001-bronze-ai-employee/plan.md` that includes:
  1) Architecture overview: components + data flow for:
     drop file → `Needs_Action` item → triage skill → plan + dashboard update → item moved to `Done/`
  2) Watcher design:
     - configuration inputs (vault path, watch folder, interval if needed)
     - duplicate-prevention strategy (IDs/hashes) and where state is stored (local, non-vault)
     - error handling and “keep running” behavior
  3) Vault I/O contracts:
     - action item markdown format (frontmatter keys, required sections)
     - plan output location rules (`Plans/` if present)
     - dashboard update strategy that is append/section-based (non-destructive)
  4) Testing strategy:
     - pytest test plan for watcher core logic + action-item formatting
     - smoke test steps for WSL/filesystem reliability
  5) Implementation steps:
     - file-by-file list of what will be added/changed (paths, responsibilities)
     - minimal sequence to reach an end-to-end Bronze demo
  6) Risks + mitigations (top 3)
  7) Validation checklist for Bronze demo using `@bronze-demo-check`

  ## Constraints / non-goals
  - Do not plan any Gmail watcher work in this feature.
  - Do not plan any MCP/external action functionality.
  - Do not introduce unrelated refactors.     the plan.md and research.md are created yoe read them then continue next files creating that creates with the plan command

## Response snapshot

- Created `specs/001-bronze-ai-employee/plan.md` describing Bronze-only architecture, watcher design (events + polling fallback), vault I/O contracts, testing strategy, implementation steps, risks/mitigations, and done conditions.
- Created `specs/001-bronze-ai-employee/research.md` capturing Context7-backed decisions:
  - `watchdog` for filesystem watching (with `PollingObserver` fallback)
  - `python-frontmatter` for YAML frontmatter parsing/writing
  - dedupe state stored outside the vault
- Created plan artifacts:
  - `specs/001-bronze-ai-employee/data-model.md`
  - `specs/001-bronze-ai-employee/contracts/vault-artifacts.md`
  - `specs/001-bronze-ai-employee/quickstart.md`
- Updated `CLAUDE.md` via `.specify/scripts/bash/update-agent-context.sh claude` using plan metadata.

## Outcome

- ✅ Impact: Produced a complete Bronze-tier implementation plan and supporting artifacts, ready for `/sp.tasks`.
- 🧪 Tests: Not applicable (plan phase).
- 📁 Files: Created plan + research + supporting plan artifacts and updated agent context.
- 🔁 Next prompts: Run `/sp.tasks` to generate an executable task list for implementation.
- 🧠 Reflection: Kept the plan minimal and constitution-aligned (skills-driven workflows, non-destructive vault operations, no MCP/external actions).

## Evaluation notes (flywheel)

- Failure modes observed: None.
- Graders run and results (PASS/FAIL): Not run
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Decide whether polling fallback should be auto-detected (filesystem type) or configured explicitly, and document via ADR if needed.
