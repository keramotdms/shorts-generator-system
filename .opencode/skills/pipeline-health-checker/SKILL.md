---
name: pipeline-health-checker
description: Checks tools, skills, handoffs and final output.
category: core
status: implemented
phase: 1
type: checker
batch: 1
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checks tools, skills, handoffs and final output for a video in `projects/<project>/`.

# Purpose

Checks tools, skills, handoffs and final output.

# Input

- `config/skill-contracts.json`
- `projects/<project>/08-final-test/final-video.mp4`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/pipeline-health-checker.json`

- Format `json_utf8`: `projects/<project>/pipeline-health-checker.json`

# Steps
1. Count the 93 skill folders and confirm every entry in `config/skill-contracts.json` has both an input and output path.
2. Verify `projects/<project>/08-final-test/final-video.mp4` exists and ffprobe reports 1080x1920 with a positive duration.
3. Check that the four required harness scripts are registered in health_check.py.
4. Confirm no SKILL.md still carries the generic template phrase or an unresolved `<character-id>` path.
5. Write PASS/WARN/BLOCKED totals and the checked file list to `projects/<project>/pipeline-health-checker.json`.
6. Assert the totals add up to the number of checks actually executed.

# How to test

- `python scripts/skill_tools.py pipeline-health-checker --self-test` → expected `PASS pipeline-health-checker: ...`. Then confirm `projects/<project>/pipeline-health-checker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

all stages -> final render gate

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
