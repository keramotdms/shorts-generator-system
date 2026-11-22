---
name: orchestrator
description: Pipeline Manager that tracks the 10-stage Shorts production workflow and advances one stage at a time.
category: core
status: mvp
phase: 1
---

# Orchestrator / Pipeline Manager Skill

## Purpose
Keep the whole Shorts production pipeline organized. It remembers which stage we are on, what skill owns that stage, and what must be finished before moving to the next stage.

## Input
- A project folder under `projects/` (starter: `projects/_template/`).
- The pipeline state file: `projects/_template/pipeline-state.json`.
- Commands given to `scripts/orchestrator.py`: `init`, `status`, `complete <stage_id>`, `reset`.

## Output
- `projects/_template/pipeline-state.json` with stage statuses and the current stage.
- A clear terminal status list showing `pending`, `current`, and `done`.

## Stages (in order)
1. `research` — Research (book/niche/trend finder)
2. `script` — Script (story, hook, script writer)
3. `voice` — Voice over and captions
4. `character` — Character design
5. `scene` — Scene collection
6. `video` — Video making
7. `edit` — Rough cut, captions, safe zone
8. `final_test` — Bug finder and health check
9. `description` — Description and SEO
10. `publish` — Handover and publishing

## Steps
1. Run `python scripts/orchestrator.py init` once to create the state file.
2. Run `python scripts/orchestrator.py status` to see the current stage.
3. Only build/test the skill that owns the current stage.
4. After that skill passes its own test, run `python scripts/orchestrator.py complete <stage_id>`.
5. The orchestrator marks that stage `done` and moves `current` to the next stage.
6. Before any final render, run the Pipeline Health Checker (built later in Phase 1).

## How to test
1. Run `python scripts/orchestrator.py init` — should say state created or already exists.
2. Run `python scripts/orchestrator.py status` — `research` should be marked `current`.
3. Run `python scripts/orchestrator.py complete research` — `research` becomes `done`, `script` becomes `current`.
4. Run `python scripts/orchestrator.py status` again to confirm.
5. Run `python scripts/orchestrator.py reset` to return to a clean state.
