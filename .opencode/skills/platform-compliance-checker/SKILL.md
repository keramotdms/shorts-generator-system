---
name: platform-compliance-checker
description: Checks YouTube and Facebook rules.
category: final-test
status: implemented
phase: later
type: checker
batch: 8
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checks youtube and facebook rules for a video in `projects/<project>/`.

# Purpose

Checks YouTube and Facebook rules.

# Input

- `projects/<project>/08-final-test/final-video.mp4`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/08-final-test/platform-compliance-checker.json`

# Steps
1. Probe `projects/<project>/08-final-test/final-video.mp4` and confirm 1080x1920 frames with a 30-60 second runtime.
2. Check the cover frame for captions inside the safe inset and record any crop risk.
3. Verify H.264 video and AAC audio, the pair accepted by both YouTube Shorts and Facebook Reels.
4. Scan the script title for misleading claims and record any claim lacking a source as WARN.
5. Write measured values, crop notes and an ALLOW/WARN/BLOCK verdict to `projects/<project>/08-final-test/platform-compliance-checker.json`.
6. Assert the verdict string is one of those three allowed values.

# Bangla rules

1. Confirm Bangla captions use Noto Sans Bengali and that ৳ plus Bengali numerals survive export.
2. Reject a cover frame with romanised Bangla or missing Bengali glyphs.

# How to test

- `python scripts/skill_tools.py platform-compliance-checker --self-test` → expected `PASS platform-compliance-checker: ...`. Then confirm `projects/<project>/08-final-test/platform-compliance-checker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

final-test -> publish stage

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
