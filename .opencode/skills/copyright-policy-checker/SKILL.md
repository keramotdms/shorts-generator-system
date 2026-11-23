---
name: copyright-policy-checker
description: Checks copyright and policy risks.
category: final-test
status: implemented
phase: later
type: checker
batch: 8
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checks copyright and policy risks for a video in `projects/<project>/`.

# Purpose

Checks copyright and policy risks.

# Input

- `projects/<project>/02-script/latest_script.json`
- `assets/characters/creator-01/character.json`
- `projects/<project>/08-final-test/final-video.mp4`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/08-final-test/copyright-policy-checker.json`

# Steps
1. Read `projects/<project>/02-script/latest_script.json` and extract narration, visual_prompt and highlight_words for source tracing.
2. Compare `assets/characters/creator-01/character.json` with the drawing in `projects/<project>/08-final-test/final-video.mp4`; flag an unlicensed look-alike as WARN.
3. Check that music and SFX cue names in the script match the licensed list in `music-sfx-selector.json`; an absent cue id is FAIL.
4. Look for third-party brand names in narration and require a clearance note for each one.
5. Save each finding with its source line and risk level to `projects/<project>/08-final-test/copyright-policy-checker.json`.
6. Assert the report holds at least one checked script field and one explicit risk level.

# How to test

- `python scripts/skill_tools.py copyright-policy-checker --self-test` → expected `PASS copyright-policy-checker: ...`. Then confirm `projects/<project>/08-final-test/copyright-policy-checker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

final-test -> publish stage

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
