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
1. Validate `projects/<project>/07-edit/captions.json` and confirm every cue has start, end and Bangla text.
2. Probe `projects/<project>/03-voice/voiceover.mp3` and `projects/<project>/08-final-test/final-video.mp4`; require durations above 0.
3. Reject any caption shown for under 0.8 seconds or over 7 seconds.
4. Scan the frame sequence for flashes above 3 Hz and record the first offending timestamp.
5. Save cue counts, flash findings, duration values and verdict to `projects/<project>/08-final-test/accessibility-safety-checker.json`.
6. Assert the report has at least one checked caption and one measured duration.

# Bangla rules

1. Read every caption as Bengali script; do not accept romanised Bangla or garbled glyphs.
2. Require Noto Sans Bengali for on-screen text and preserve ৳ and Bengali numerals such as ০-৯.
3. Reject a cue that hides the ৳ symbol or splits a Bengali word across lines.

# How to test

- `python scripts/skill_tools.py accessibility-safety-checker --self-test` → expected `PASS accessibility-safety-checker: ...`. Then confirm `projects/<project>/08-final-test/accessibility-safety-checker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

final-test -> publish stage

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
