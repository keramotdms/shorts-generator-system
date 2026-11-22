---
name: watermark-logo-placer
description: Places the channel watermark or logo.
category: video-editing
subcategory: text-graphics
status: implemented
phase: later
type: script-backed
batch: 7
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when places the channel watermark or logo for a video in `projects/<project>/`.

# Purpose

Places the channel watermark or logo.

# Input

- `video + logo asset`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `branded video`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `video + logo asset`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py watermark-logo-placer run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `branded video` under `projects/<project>/`; create parent folders first.
5. Re-open `branded video` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.
6. If `requires: ffmpeg` is set, call `scripts/skill_lib.py::require_ffmpeg()` which reads `FFMPEG_PATH`; on `BLOCKED` print `BLOCKED watermark-logo-placer: ffmpeg ...` and exit 0 without a FAIL.

# How to test

- `python scripts/skill_tools.py watermark-logo-placer --self-test` → expected `PASS watermark-logo-placer: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `branded video` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
