---
name: voiceover-tester
description: Checks voice clarity, speed and duration.
category: voice
status: implemented
phase: later
type: checker
batch: 4
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checks voice clarity, speed and duration for a video in `projects/<project>/`.

# Purpose

Checks voice clarity, speed and duration.

# Input

- `projects/<project>/03-voice/voiceover.mp3`
- `projects/<project>/02-script/latest_script.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/03-voice/voiceover-tester.json`

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `voiceover.mp3 + final script`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py voiceover-tester run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/03-voice/voiceover-tester.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/03-voice/voiceover-tester.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- `python scripts/skill_tools.py voiceover-tester --self-test` → expected `PASS voiceover-tester: ...`. Then confirm `projects/<project>/03-voice/voiceover-tester.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

voiceover-generator -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
