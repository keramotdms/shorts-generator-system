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
1. Take `projects/<project>/07-edit/captioned.mp4` as the source and read target length from `config/channel.json` through project-memory.
2. Encode H.264 with CRF 23, preset veryfast, yuv420p and AAC audio; keep 1080x1920.
3. Write the one canonical deliverable to `projects/<project>/08-final-test/final-video.mp4`; never create a second final file elsewhere.
4. Probe the result and require one video stream, one audio stream and duration equal to the source within 0.20 seconds.
5. Record source bytes, output bytes, codec settings and `canonical_path` in `projects/<project>/07-edit/render-export-optimizer.json`.
6. Assert `canonical_path` equals `projects/<project>/08-final-test/final-video.mp4` before reporting PASS.

# How to test

- `python scripts/skill_tools.py render-export-optimizer --self-test` → expected `PASS render-export-optimizer: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/07-edit/render-export-optimizer.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

video-editing -> publish stage

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
