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

- `voice timings + rough cut`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `projects/<project>/07-edit/captions.json + projects/<project>/07-edit/caption-maker.json`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `voice timings + rough cut`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py caption-maker run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/07-edit/captions.json + projects/<project>/07-edit/caption-maker.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/07-edit/captions.json + projects/<project>/07-edit/caption-maker.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- `python scripts/skill_tools.py caption-maker --self-test` → expected `PASS caption-maker: ...`. Then confirm `projects/<project>/07-edit/captions.json + projects/<project>/07-edit/caption-maker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

voice and rough cut -> safe-zone-checker

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
