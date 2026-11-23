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
1. Load `projects/<project>/03-voice/voiceover.mp3` and the cue list at `projects/<project>/03-voice/music-sfx-selector.json`.
2. Set narration bus to 0 dB, music bed to -18 dB and SFX peaks to -6 dB relative to narration.
3. Render one mix and probe it for one audio stream and duration matching the voice track within 0.20 seconds.
4. Measure integrated loudness and keep it between -16 and -14 LUFS.
5. Store bus gains, measured loudness and any block reason in `projects/<project>/03-voice/audio-mixer.json`.
6. Re-open the report and assert the three gain values are numbers no greater than zero.

# How to test

- `python scripts/skill_tools.py audio-mixer --self-test` → expected `PASS audio-mixer: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/03-voice/audio-mixer.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

voice and music -> video-editing

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
