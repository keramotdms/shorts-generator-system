---
name: caption-maker
description: Creates word-level caption timings and burns captions.
category: video-editing
subcategory: text-graphics
status: implemented
phase: 4
type: script-backed
batch: 7
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when creates word-level caption timings and burns captions for a video in `projects/<project>/`.

# Purpose

Creates word-level caption timings and burns captions.

# Input

- `projects/<project>/03-voice/captions.json`
- `projects/<project>/07-edit/rough-cut.mp4`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/captions.json`
- `projects/<project>/07-edit/caption-maker.json`
- `projects/<project>/07-edit/captioned.mp4`

- Format `json_utf8`: `projects/<project>/07-edit/captions.json`
- Format `json_utf8`: `projects/<project>/07-edit/caption-maker.json`
- Format `mp4_clip`: `projects/<project>/07-edit/captioned.mp4`

# Steps
1. Validate `projects/<project>/03-voice/captions.json` and take its caption blocks plus total duration.
2. Read `projects/<project>/07-edit/rough-cut.mp4` duration and reject blocks whose start or end exceeds it.
3. Plan each caption as at most 2 lines of 32 characters using Noto Sans Bengali; preserve Bengali numerals and ৳ exactly.
4. Burn the planned blocks into `projects/<project>/07-edit/captioned.mp4` with the ffmpeg subtitles filter.
5. Write safe-zone-ready blocks to `projects/<project>/07-edit/captions.json` and the burn report to `projects/<project>/07-edit/caption-maker.json`.
6. Re-open both JSON files and assert the caption count is identical in each and greater than zero.

# Bangla rules

1. Render caption text in Bengali script using Noto Sans Bengali only.
2. Keep each caption to at most 2 lines of 32 characters; expand ৳ amounts instead of replacing them with BDT.
3. Preserve Bengali numerals ০-৯ from the voice caption source and never transliterate them.

# How to test

- `python scripts/skill_tools.py caption-maker --self-test` → expected `PASS caption-maker: ...`. Then confirm `projects/<project>/07-edit/captions.json + projects/<project>/07-edit/caption-maker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

voice and rough cut -> safe-zone-checker

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
