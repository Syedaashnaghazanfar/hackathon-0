---
id: 0001
title: Bronze Tier Constitution Creation
stage: constitution
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: unknown
command: /sp.constitution
labels: ["constitution", "bronze-tier", "hackathon-zero", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none (constitution document)
---

## Prompt

Create a project constitution for "My AI Employee" (Hackathon Zero) focused strictly on Bronze tier. ## 1) Project goal Build a local-first Personal AI Employee using: - Obsidian as the "Memory/GUI" (markdown vault) - Python watcher script(s) as the "Senses" (start with filesystem watcher) - Claude Code as the "Reasoning engine" - All AI behavior expressed as Claude Code Agent Skills (stored under .claude/skills) ## 2) Bronze-tier scope (non-negotiable) - Must produce an Obsidian vault containing: Dashboard.md and Company_Handbook.md - Must maintain vault folders: Inbox/, Needs_Action/, Done/ (optionally allow Plans/) - Must have one working watcher (filesystem watcher preferred) that writes markdown action items into Needs_Action/ - Claude Code must read from and write to the vault (plan generation + dashboard updates + archiving to Done/) - NO MCP servers and NO external actions in Bronze (no sending emails, no posting, no payments) ## 3) Local-first + safety principles - Never delete user content in the vault; prefer append/section updates - Preserve YAML frontmatter when moving/processing markdown items - No secrets in repo; credentials must be via .env and excluded from git - "Human as tool" principle: ask for clarification when vault root/path is ambiguous or when an action could overwrite user-authored notes ## 4) Technology & implementation constraints - Python 3.13+ (or latest available), uv for packaging, pytest for tests - Prefer simple, minimal diffs (no unrelated refactors) - Watcher should be resilient: log errors and keep running; prevent duplicate processing (tracked IDs or hashes) - Vault path convention for this repo: hack-zero/AI_Employee_Vault/ ## 5) Quality gates - Tests required for watcher core logic and action-item formatting - Basic lint/format (keep consistent; no heavy tooling requirements unless already in repo) - All tasks must be demonstrable with an end-to-end Bronze demo: drop file → Needs_Action item → Claude processes → plan + dashboard update → item moved to Done/ ## 5a) Artifact conventions (Bronze) ### Action Item Contract (Needs_Action) - Action items MUST be Markdown files stored under Needs_Action/. - Action items SHOULD include YAML frontmatter with (at minimum): - type: email|file_drop|manual - received: ISO timestamp - status: pending|processed - priority: high|medium|low|auto (optional) - optional: source_id, from, subject ### Plan output location - Plans MUST be written to Plans/ when that folder exists (recommended). - If Plans/ is not used, the chosen plan output location MUST be consistent and documented in the feature spec. ### Watcher file handling default - Default behavior: the watcher writes a Markdown action item that references the original dropped file path (metadata-only). - Copying dropped files into the vault is OPTIONAL and must be an explicit design choice documented in the plan (and ADR if it has long-term impact). ## 6) Governance - Constitution supersedes specs/plans/tasks when there is conflict - Significant architecture choices (e.g., whether watcher copies dropped files into vault vs metadata-only links) should be documented via ADR when they have long-term impact and alternatives - Amendments require updating constitution version and noting rationale - All automation must be runnable via Claude Code prompts invoking skills; no hidden manual steps besides starting the watcher

## Response snapshot

Created the "My AI Employee (Hackathon Zero) Constitution" v1.0.0 with seven core principles:

1. **Local-First Personal AI Employee**: Defines the three-layer architecture (Memory/GUI via Obsidian, Senses via Python watchers, Reasoning via Claude Code) and non-negotiable Bronze tier scope (vault with Dashboard.md/Company_Handbook.md, folders Inbox/Needs_Action/Done, filesystem watcher, no MCP/external actions).

2. **Vault Safety and Non-Destructive Operations**: Mandates never deleting user content, preserving YAML frontmatter, preferring append/section updates, and archiving to Done/ rather than deletion.

3. **Human-as-Tool Principle**: Requires invoking the user for guidance in ambiguous situations (vault path unclear, potential overwrites, multiple valid approaches, unexpected formats, plans requiring user context).

4. **Watcher Resilience and Idempotency**: Specifies production-grade requirements (log errors and continue, prevent duplicates via tracked IDs/hashes, handle filesystem race conditions, graceful shutdown/resume, atomic writes).

5. **Secret Management and Security**: Enforces no secrets in repo, API keys as environment variables, vault path in .env, PII sanitization before logging, content redaction.

6. **Technology Stack and Implementation Constraints**: Mandates Python 3.13+, uv for packaging, pytest for tests, watchdog library, minimal dependencies, type hints, docstrings, actionable error messages, vault path convention at hack-zero/AI_Employee_Vault/.

7. **Test-Driven Development for Core Logic**: Requires test coverage for watcher core logic, action item formatting, vault safety operations, plan generation, with unit/integration/e2e strategies.

Added sections:
- **Artifact Conventions**: Action Item Contract (required YAML frontmatter: type, received, status, priority; body structure), Plan output location (Plans/ folder), Watcher file handling default (metadata-only references, not copying files unless explicit decision).
- **Quality Gates**: Bronze Tier Acceptance Criteria (6-step end-to-end demo validation), Code Review Checklist (tests, no secrets/PII, YAML preservation, error handling, alignment, ADR/PHR creation).
- **Governance**: Amendment process (rationale, semantic versioning, template updates, sync impact report), ADR requirements (multiple alternatives, long-term impact, core deliverables), Compliance enforcement (skills reference constitution, PRs verify safety/security, justify complexity, runtime guidance in .claude/skills/).

Sync Impact Report included as HTML comment documenting version 1.0.0 rationale and template consistency verification.

## Outcome

- ✅ Impact: Initial constitution created for Hackathon Zero Bronze tier, establishing all governance principles and constraints for the AI Employee project
- 🧪 Tests: None required (governance document)
- 📁 Files: Created .specify/memory/constitution.md (v1.0.0)
- 🔁 Next prompts: Implement filesystem watcher following constitution principles, create Obsidian vault structure, develop Claude Code skills for triage and vault operations
- 🧠 Reflection: Constitution successfully captures all Bronze tier requirements with clear principles, artifact conventions, quality gates, and governance rules. All seven principles are testable and enforceable. Sync impact report documents baseline state for future amendments.

## Evaluation notes (flywheel)

- Failure modes observed: None (initial creation)
- Graders run and results (PASS/FAIL): Manual review - PASS (all placeholders filled, principles aligned with user requirements, no conflicts)
- Prompt variant (if applicable): Standard constitution creation with detailed Bronze tier constraints
- Next experiment (smallest change to try): Validate constitution compliance by implementing first watcher and vault operations, identify any missing constraints or ambiguities
