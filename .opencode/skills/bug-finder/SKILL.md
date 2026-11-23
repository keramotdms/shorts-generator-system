---
name: bug-finder
description: Finds bugs in the final video.
category: final-test
status: implemented
phase: 5
type: checker
batch: 8
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when finds bugs in the final video for a video in `projects/<project>/`.

# Purpose

Finds bugs in the final video.

# Input

- `projects/<project>/08-final-test/final-video.mp4`
- `projects/<project>/08-final-test/red-team.json`
- `projects/<project>/08-final-test/ruthless-team.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/08-final-test/bug-finder.json`

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `final video + reports`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py bug-finder run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/08-final-test/bug-finder.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/08-final-test/bug-finder.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- `python scripts/skill_tools.py bug-finder --self-test` → expected `PASS bug-finder: ...`. Then confirm `projects/<project>/08-final-test/bug-finder.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

video-editing -> description-maker

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
