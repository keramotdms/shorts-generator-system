---
name: audio-ducking-controller
description: Ducks music under the voice.
category: video-editing
subcategory: audio-sync
status: implemented
phase: later
type: script-backed
batch: 7
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when ducks music under the voice for a video in `projects/<project>/`.

# Purpose

Ducks music under the voice.

# Input

- `projects/<project>/03-voice/voiceover.mp3`
- `projects/<project>/03-voice/music-sfx-selector.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/audio-ducking-controller.json`

# Steps
1. Load the voice track from `projects/<project>/03-voice/voiceover.mp3` and cues from `projects/<project>/03-voice/music-sfx-selector.json`.
2. Measure voice loudness in LUFS and set the music bed 12 dB below it during speech windows.
3. Apply a 150 ms attack and a 300 ms release so the bed returns smoothly between lines.
4. Keep the true-peak ceiling at -1 dBTP and reject clipping above that level.
5. Save measured loudness, gain reduction and ceiling to `projects/<project>/07-edit/audio-ducking-controller.json`.
6. Re-open the report and assert the gain-reduction value is a negative number.

# How to test

- `python scripts/skill_tools.py audio-ducking-controller --self-test` → expected `PASS audio-ducking-controller: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/07-edit/audio-ducking-controller.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

audio-mixer -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
