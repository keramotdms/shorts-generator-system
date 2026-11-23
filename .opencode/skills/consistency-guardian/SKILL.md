---
name: consistency-guardian
description: Checks character consistency across scenes.
category: character
status: implemented
phase: later
type: checker
batch: 5
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checks character consistency across scenes for a video in `projects/<project>/`.

# Purpose

Checks character consistency across scenes.

# Input

- `projects/<project>/06-video/scenes/`
- `assets/characters/creator-01.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/04-character/consistency-guardian.json`

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `rendered scenes + character references`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py consistency-guardian run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/04-character/consistency-guardian.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/04-character/consistency-guardian.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- `python scripts/skill_tools.py consistency-guardian --self-test` → expected `PASS consistency-guardian: ...`. Then confirm `projects/<project>/04-character/consistency-guardian.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

video-maker -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
