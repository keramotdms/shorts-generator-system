---
name: transition-designer
description: Designs scene transitions.
category: video-editing
subcategory: visual
status: implemented
phase: later
type: script-backed
batch: 7
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when designs scene transitions for a video in `projects/<project>/`.

# Purpose

Designs scene transitions.

# Input

- `projects/<project>/07-edit/rough-cut.mp4`
- `config/style-bible.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/transition-designer.json`

- Format `json_utf8`: `projects/<project>/07-edit/transition-designer.json`

# Steps
1. Inspect adjacent shot boundaries in `projects/<project>/07-edit/rough-cut.mp4` using scene-change detection.
2. Read the palette and tone from `config/style-bible.json`; use only those colours for an overlay wipe.
3. Assign one of three classes — cut, fade or shape-wipe — and record the reason for each boundary.
4. Keep every transition under 0.40 seconds so the 30-60 second runtime is preserved.
5. Save frame numbers, chosen classes and duration budget to `projects/<project>/07-edit/transition-designer.json`.
6. Re-open the report and assert the decision count equals the detected boundary count.

# How to test

- `python scripts/skill_tools.py transition-designer --self-test` → expected `PASS transition-designer: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/07-edit/transition-designer.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
