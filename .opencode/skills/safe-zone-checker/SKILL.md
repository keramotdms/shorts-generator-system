---
name: safe-zone-checker
description: Checks captions stay inside platform safe zones.
category: video-editing
subcategory: automation-export
status: implemented
phase: 4
type: checker
batch: 7
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checks captions stay inside platform safe zones for a video in `projects/<project>/`.

# Purpose

Checks captions stay inside platform safe zones.

# Input

- `projects/<project>/07-edit/captions.json`
- `projects/<project>/07-edit/captioned.mp4`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/safe-zone-checker.json`

- Format `json_utf8`: `projects/<project>/07-edit/safe-zone-checker.json`

# Steps
1. Load `projects/<project>/07-edit/captions.json` and validate it against the captions schema; reject any block whose `end` precedes its `start`.
2. Probe `projects/<project>/07-edit/captioned.mp4` and record the real 1080x1920 frame size.
3. Reserve a 72 px left/right inset and a 180 px top/bottom inset; test every caption box against those margins.
4. Mark a caption WARN when two Bengali lines exceed 32 characters per line; keep ৳ amounts intact.
5. Write the margin measurements, WARN list and overall verdict to `projects/<project>/07-edit/safe-zone-checker.json`.
6. Re-read the report and assert the number of inspected blocks equals the total caption count.

# Bangla rules

1. Measure Bengali glyph insets with Noto Sans Bengali; allow 12 px extra bottom room for vowel signs.
2. Keep ৳ and Bengali numerals ০-৯ fully inside the safe rectangle and at most 2 lines.
3. Flag any caption where Bengali text touches the 72 px side inset.

# How to test

- `python scripts/skill_tools.py safe-zone-checker --self-test` → expected `PASS safe-zone-checker: ...`. Then confirm `projects/<project>/07-edit/safe-zone-checker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

caption-maker -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
