---
name: audio-mixer
description: Mixes voice, music and sound effect levels.
category: voice
status: implemented
phase: later
type: script-backed
batch: 4
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when mixes voice, music and sound effect levels for a video in `projects/<project>/`.

# Purpose

Mixes voice, music and sound effect levels.

# Input

- `projects/<project>/03-voice/voiceover.mp3`
- `projects/<project>/03-voice/music-sfx-selector.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/03-voice/audio-mixer.json`

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `voice + music + SFX files`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py audio-mixer run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/03-voice/audio-mixer.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/03-voice/audio-mixer.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.
6. If `requires: ffmpeg` is set, call `scripts/skill_lib.py::require_ffmpeg()` which reads `FFMPEG_PATH`; on `BLOCKED` print `BLOCKED audio-mixer: ffmpeg ...` and exit 0 without a FAIL.

# How to test

- `python scripts/skill_tools.py audio-mixer --self-test` → expected `PASS audio-mixer: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/03-voice/audio-mixer.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

voice and music -> video-editing

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
