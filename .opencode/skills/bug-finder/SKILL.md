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

- Format `json_utf8`: `projects/<project>/08-final-test/bug-finder.json`

# Steps
1. Probe `projects/<project>/08-final-test/final-video.mp4` and reject a file with no moov atom, no video stream or zero duration.
2. Read the attack notes in `projects/<project>/08-final-test/red-team.json` and `ruthless-team.json`; carry unresolved items forward.
3. Check pixel dimensions, codec names and byte size against the 1080x1920 Shorts target.
4. Rank findings as FAIL, WARN or INFO with the exact evidence path proving each one.
5. Write the ranked list and final gate verdict to `projects/<project>/08-final-test/bug-finder.json`.
6. Re-open the JSON and assert every FAIL entry has a non-empty evidence field.

# How to test

- `python scripts/skill_tools.py bug-finder --self-test` → expected `PASS bug-finder: ...`. Then confirm `projects/<project>/08-final-test/bug-finder.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

video-editing -> description-maker

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
