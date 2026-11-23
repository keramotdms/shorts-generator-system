---
name: accessibility-safety-checker
description: Checks captions, audio and viewer safety.
category: final-test
status: implemented
phase: later
type: checker
batch: 8
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checks captions, audio and viewer safety for a video in `projects/<project>/`.

# Purpose

Checks captions, audio and viewer safety.

# Input

- `projects/<project>/07-edit/captions.json`
- `projects/<project>/03-voice/voiceover.mp3`
- `projects/<project>/08-final-test/final-video.mp4`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/08-final-test/accessibility-safety-checker.json`

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `final video`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py accessibility-safety-checker run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/08-final-test/accessibility-safety-checker.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/08-final-test/accessibility-safety-checker.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- `python scripts/skill_tools.py accessibility-safety-checker --self-test` → expected `PASS accessibility-safety-checker: ...`. Then confirm `projects/<project>/08-final-test/accessibility-safety-checker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

final-test -> publish stage

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
