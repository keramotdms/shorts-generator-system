---
name: character-qa-tester
description: Tests character outputs for errors.
category: character
status: implemented
phase: later
type: checker
batch: 5
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when testing character outputs for errors for a video in `projects/<project>/`.

# Purpose

Tests the locked parametric character, its layer structure and its rendered previews, then writes a field-by-field verdict.

# Input

- `assets/characters/creator-01/character.json`
- `assets/character-parts/parts.json`
- `assets/characters/creator-01/layered.svg`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/04-character/character-qa-tester.json`

# Steps

1. Validate `assets/characters/creator-01/character.json` against `config/schemas/character.json`.
2. Confirm each part ID in `parts` exists in `assets/character-parts/parts.json`, and that the library holds at least 6 heads, 8 hairstyles, 6 eyes, 4 brows, 8 mouths, 5 bodies, 8 outfits and 8 accessories.
3. Parse `assets/characters/creator-01/layered.svg` and assert all 10 layer ids exist: body, outfit, arms, neck, head, hair, brows, eyes, mouth, accessory.
4. Assert head-to-body ratio is 0.18–0.30, skin/outline contrast is at least 3.0, and `appearance.palette` holds at least 3 distinct hex colours from `config/style-bible.json`.
5. Check `assets/characters/creator-01/preview.png` and `assets/characters/creator-01/preview-sheet.png` parse as PNG and measure exactly 1080x1920.
6. Compare hair, clothing and voice fields with `config/style-bible.json`; report any contradiction as FAIL.
7. Write field-by-field findings to `projects/<project>/04-character/character-qa-tester.json`, with at least 3 checked fields and one explicit PASS or FAIL verdict.

# How to test

- `python scripts/skill_tools.py character-qa-tester --self-test` → expected `PASS character-qa-tester: schema, 10 layer ids, palette (5) and 1080x1920 PNGs verified`. Then confirm `projects/<project>/04-character/character-qa-tester.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

character-designer -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
