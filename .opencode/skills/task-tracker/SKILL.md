---
name: task-tracker
description: Tracks tasks and progress across the pipeline.
category: core
status: implemented
phase: later
type: script-backed
batch: 1
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when tracks tasks and progress across the pipeline for a video in `projects/<project>/`.

# Purpose

Tracks tasks and progress across the pipeline.

# Input

- `projects/<project>/pipeline-state.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/task-tracker.json`

- Format `json_utf8`: `projects/<project>/task-tracker.json`

# Steps
1. Open `projects/<project>/pipeline-state.json` and read the current stage name.
2. Load the per-task ledger at `projects/<project>/task-tracker.json`; create it with an empty `tasks` array if absent.
3. Add one row for the active skill with status pending, start time and owner stage; never mark done before its test passes.
4. When a test passes, flip only that row to done and leave pipeline-state.json untouched here.
5. Write the ledger back and assert one row per active skill with no duplicate skill names.

# How to test

- `python scripts/skill_tools.py task-tracker --self-test` → expected `PASS task-tracker: ...`. Then confirm `projects/<project>/task-tracker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

orchestrator -> all stages

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
