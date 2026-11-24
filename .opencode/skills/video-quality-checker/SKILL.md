---
name: video-quality-checker
description: Checks rendered scene quality.
category: video-making
status: implemented
phase: later
type: checker
batch: 6
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checks rendered scene quality for a video in `projects/<project>/`.

# Purpose

Checks rendered scene quality.

# Input

- `projects/<project>/06-video/scenes/`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/06-video/video-quality-checker.json`

- Format `json_utf8`: `projects/<project>/06-video/video-quality-checker.json`

# Steps
1. Enumerate MP4 files under `projects/<project>/06-video/scenes/` and probe each one individually.
2. Require 1080x1920 pixels, yuv420p format and a duration from 1 to 15 seconds.
3. Reject a clip with a black first frame or an unexpected audio stream; note the exact filename.
4. Compute average bitrate and flag any clip below 500 kbps as WARN.
5. Write per-clip measurements and the worst-case verdict to `projects/<project>/06-video/video-quality-checker.json`.
6. Assert the report contains one entry for every scene file found.

# How to test

- `python scripts/skill_tools.py video-quality-checker --self-test` → expected `PASS video-quality-checker: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/06-video/video-quality-checker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

video-maker -> rough-cut-assembler

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
