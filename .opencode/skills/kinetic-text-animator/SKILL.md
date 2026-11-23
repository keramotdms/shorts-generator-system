---
name: kinetic-text-animator
description: Animates on-screen text.
category: video-editing
subcategory: text-graphics
status: implemented
phase: later
type: script-backed
batch: 7
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when animates on-screen text for a video in `projects/<project>/`.

# Purpose

Animates on-screen text.

# Input

- `projects/<project>/07-edit/captions.json`
- `projects/<project>/07-edit/captioned.mp4`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/kinetic-text-animator.json`

# Steps
1. Pair each caption block from `projects/<project>/07-edit/captions.json` with its exact start and end time.
2. Assign one motion style per emphasis word — pop, slide or fade — and never cut inside a Bengali consonant cluster.
3. Render with Noto Sans Bengali at 56 px minimum over frames from `projects/<project>/07-edit/captioned.mp4`.
4. Cap each animated phrase at 2 lines and 32 characters so ৳ signs and Bengali numerals remain readable.
5. Save timing offsets, style names and output path to `projects/<project>/07-edit/kinetic-text-animator.json`.
6. Re-open the report and assert the styled-phrase count equals the caption-block count.

# Bangla rules

1. Animate Bengali text only with Noto Sans Bengali and never split a consonant cluster across frames.
2. Cap each phrase at 2 lines and 32 characters; keep ৳ and numerals ০-৯ on the same line as the amount.
3. Verify that motion does not clip Bengali vowel signs at 1080x1920.

# How to test

- `python scripts/skill_tools.py kinetic-text-animator --self-test` → expected `PASS kinetic-text-animator: ...` or `BLOCKED ...: ffmpeg ...` while Smart App Control is active. Then confirm `projects/<project>/07-edit/kinetic-text-animator.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

caption-maker -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
