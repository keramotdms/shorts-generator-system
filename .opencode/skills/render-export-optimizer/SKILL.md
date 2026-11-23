---
name: render-export-optimizer
description: Optimizes render settings and file size.
category: video-editing
subcategory: automation-export
status: implemented
phase: later
type: script-backed
batch: 7
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when optimizes render settings and file size for a video in `projects/<project>/`.

# Purpose

Optimizes render settings and file size.

# Input

- `projects/<project>/07-edit/captioned.mp4`
- `config/channel.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/08-final-test/final-video.mp4`
- `projects/<project>/07-edit/render-export-optimizer.json`

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `edit project + video`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py render-export-optimizer run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Export the final video to the canonical path `projects/<project>/08-final-test/final-video.mp4` (create `08-final-test/` first). Every checker, handover and publish skill reads this exact path; do not write a second final video elsewhere.
5. Write the probe report to `projects/<project>/07-edit/render-export-optimizer.json` and re-open it to verify it is valid, non-empty and has `canonical_path` equal to that exact video path. Record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.
6. If `requires: ffmpeg` is set, call `scripts/skill_lib.py::require_ffmpeg()` which reads `FFMPEG_PATH`; on `BLOCKED` print `BLOCKED render-export-optimizer: ffmpeg ...` and exit 0 without a FAIL.

# How to test

- `python scripts/skill_tools.py render-export-optimizer --self-test` → expected `PASS render-export-optimizer: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/07-edit/render-export-optimizer.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

video-editing -> publish stage

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
