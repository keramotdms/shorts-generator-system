---
name: av-sync-checker
description: Checks audio and video synchronization.
category: video-editing
subcategory: audio-sync
status: implemented
phase: later
type: checker
batch: 7
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checks audio and video synchronization for a video in `projects/<project>/`.

# Purpose

Checks audio and video synchronization.

# Input

- `projects/<project>/08-final-test/final-video.mp4`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/av-sync-checker.json`

# Steps
1. Probe the audio and video streams of `projects/<project>/08-final-test/final-video.mp4` with ffprobe.
2. Compare stream durations; allow at most 0.20 seconds of drift between the first audio sample and the first video frame.
3. Flag a silent track, an absent audio stream, or video longer than audio by over 0.20 seconds as FAIL.
4. Record both measured durations, the drift value and a PASS/WARN/FAIL verdict in `projects/<project>/07-edit/av-sync-checker.json`.
5. Re-open the report and assert the drift field is a finite number, not a fixed PASS string.

# How to test

- `python scripts/skill_tools.py av-sync-checker --self-test` → expected `PASS av-sync-checker: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/07-edit/av-sync-checker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

video-editing -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
