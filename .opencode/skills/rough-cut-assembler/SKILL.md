---
name: rough-cut-assembler
description: Assembles the first cut of all scenes.
category: video-editing
subcategory: core
status: implemented
phase: 4
type: script-backed
batch: 7
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when assembles the first cut of all scenes for a video in `projects/<project>/`.

# Purpose

Assembles the first cut of all scenes.

# Input

- `projects/<project>/06-video/scenes/`
- `projects/<project>/05-scene/collection.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/rough-cut.mp4`
- `projects/<project>/07-edit/rough-cut-assembler-report.json`

# Steps
1. Read `projects/<project>/05-scene/collection.json` and take its `scenes[]` array in declared order.
2. Verify each named MP4 exists under `projects/<project>/06-video/scenes/`; stop at the first missing name instead of globbing.
3. Build an ffmpeg concat list from that verified order and join clips without re-encoding unless durations disagree.
4. Probe the joined file and assert one video stream plus a duration within 0.30 seconds of the summed clip lengths.
5. Save the exact concat order and probe values to `projects/<project>/07-edit/rough-cut-assembler-report.json`.
6. Copy the final joined media to `projects/<project>/07-edit/rough-cut.mp4` only after the probe passes.

# How to test

- `python scripts/skill_tools.py rough-cut-assembler --self-test` → expected `PASS rough-cut-assembler: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/07-edit/rough-cut.mp4` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

video-maker -> caption-maker

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
