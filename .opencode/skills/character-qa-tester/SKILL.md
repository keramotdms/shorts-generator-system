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

Use when tests character outputs for errors for a video in `projects/<project>/`.

# Purpose

Tests character outputs for errors.

# Input

- `assets/characters/creator-01.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/04-character/character-qa-tester.json`

# Steps
1. Open `assets/characters/creator-01.json` and validate it against the character schema.
2. Confirm the palette has exactly 4 hex colours and the expression set contains neutral, smile and surprised.
3. Check each SVG and PNG sidecar under `assets/characters/` parses and measures exactly 1080x1920.
4. Compare hair, clothing and voice fields with `config/style-bible.json`; report any contradiction as FAIL.
5. Write field-by-field findings to `projects/<project>/04-character/character-qa-tester.json`.
6. Assert the report holds at least 3 checked fields and one explicit PASS or FAIL verdict.

# How to test

- `python scripts/skill_tools.py character-qa-tester --self-test` → expected `PASS character-qa-tester: ...`. Then confirm `projects/<project>/04-character/character-qa-tester.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

character-designer -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
