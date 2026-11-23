---
name: error-log-keeper
description: Records errors and fixes for every stage.
category: core
status: implemented
phase: later
type: script-backed
batch: 1
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when records errors and fixes for every stage for a video in `projects/<project>/`.

# Purpose

Records errors and fixes for every stage.

# Input

- `projects/<project>/08-final-test/`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/08-final-test/error-log.jsonl`

# Steps
1. Create `projects/<project>/08-final-test/error-log.jsonl` if absent; never truncate an existing log.
2. Accept only entries with skill, stage, status and reason keys; reject an empty reason.
3. Append one JSON object per line with an ISO timestamp and the exact failing path when available.
4. De-duplicate a repeat only when skill, stage and reason are all identical.
5. Read back the last line and assert it parses as JSON with the same skill name.
6. Report the number of entries added; never print a fixed PASS without this round-trip check.

# How to test

- `python scripts/skill_tools.py error-log-keeper --self-test` → expected `PASS error-log-keeper: ...`. Then confirm `projects/<project>/error-log-keeper.jsonl` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

all stages -> pipeline-health-checker

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
