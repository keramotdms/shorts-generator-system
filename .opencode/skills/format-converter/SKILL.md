---
name: format-converter
description: Converts to platform-ready formats.
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

Use when converts to platform-ready formats for a video in `projects/<project>/`.

# Purpose

Converts to platform-ready formats.

# Input

- `projects/<project>/08-final-test/final-video.mp4`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/format-converter.json`

- Format `json_utf8`: `projects/<project>/07-edit/format-converter.json`

# Steps
1. Read `projects/<project>/08-final-test/final-video.mp4` and note its current codec, pixel format and bitrate.
2. Choose the delivery preset: vertical 1080x1920, H.264, yuv420p and AAC; do not upscale past the source frame.
3. Convert with ffmpeg to a temporary file, then rename it only after ffprobe confirms the preset.
4. Record source and output byte counts, codec names and duration delta in `projects/<project>/07-edit/format-converter.json`.
5. Assert the output still has one video stream and one audio stream, and that duration delta stays below 0.10 seconds.

# How to test

- `python scripts/skill_tools.py format-converter --self-test` → expected `PASS format-converter: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/07-edit/format-converter.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

final video -> publish stage

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
