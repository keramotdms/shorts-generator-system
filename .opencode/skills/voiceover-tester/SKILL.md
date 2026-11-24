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

- Format `json_utf8`: `projects/<project>/03-voice/voiceover-tester.json`

# Steps
1. Validate `projects/<project>/02-script/latest_script.json` and read its total_duration_sec.
2. Probe `projects/<project>/03-voice/voiceover.mp3`; reject audio shorter than 30 seconds or longer than 60 seconds.
3. Verify language `bn` metadata and flag misread Bengali numerals or spoken ৳ amounts in the listen notes.
4. Compare word count against the 110-130 wpm Bangla range and mark too-fast delivery as WARN.
5. Record measured seconds, WPM estimate and verdict in `projects/<project>/03-voice/voiceover-tester.json`.
6. Re-open the report and assert the measured duration is a number greater than 0.

# Bangla rules

1. Listen for mispronounced Bengali numerals and ৳ amounts in the `bn` take.
2. Confirm spoken line length stays within 8-12 words at 110-130 wpm.
3. Flag English bridging words or romanised pronunciation as WARN with the exact timestamp.

# How to test

- `python scripts/skill_tools.py voiceover-tester --self-test` → expected `PASS voiceover-tester: ...`. Then confirm `projects/<project>/03-voice/voiceover-tester.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

voiceover-generator -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
