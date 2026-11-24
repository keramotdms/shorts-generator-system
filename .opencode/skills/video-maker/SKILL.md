---
name: video-maker
description: Renders vertical scene videos.
category: video-making
status: implemented
phase: 3
type: script-backed
batch: 6
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when renders vertical scene videos for a video in `projects/<project>/`.

# Purpose

Renders vertical scene videos.

# Input

- `projects/<project>/05-scene/collection.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/06-video/scenes/`
- `projects/<project>/06-video/video-maker-report.json`

- Format `mp4_clip`: `projects/<project>/06-video/scenes/`
- Format `json_utf8`: `projects/<project>/06-video/video-maker-report.json`

# Steps
1. Open `projects/<project>/05-scene/collection.json` and require matching `scene_images[]` and `scenes[]` arrays.
2. For each image path, confirm the PNG exists at 1080x1920; stop on the first missing file.
3. Use the matching script scene's duration_sec, clamped to 1-15 seconds, when encoding the still into an MP4.
4. Write each clip to the exact name in `scenes[]` under `projects/<project>/06-video/scenes/`.
5. Probe every produced clip and save dimensions, duration and filenames to `projects/<project>/06-video/video-maker-report.json`.
6. Assert the clip count equals the declared array length before reporting PASS.

# How to test

- `python scripts/skill_tools.py video-maker --self-test` → expected `PASS video-maker: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/06-video/scenes/` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

collector -> rough-cut-assembler

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
