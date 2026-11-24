---
name: asset-manager
description: Validates folder structure, naming and backups.
category: core
status: implemented
phase: 1
type: script-backed
batch: 1
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when validates folder structure, naming and backups for a video in `projects/<project>/`.

# Purpose

Validates folder structure, naming and backups.

# Input

- `config/channel.json`
- `projects/<project>/`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/asset-manager.json`

- Format `json_utf8`: `projects/<project>/asset-manager.json`

# Steps
1. Inventory the starter folders `assets/`, `config/` and the current `projects/<project>/` tree; list every missing required folder by exact path.
2. Compare declared character and scene seeds against `config/style-bible.json` values loaded through project-memory; never invent a new style value.
3. Create only the absent directories under `projects/<project>/`; use lowercase-kebab-case for any new filename.
4. Copy approved SVG and PNG seeds into their expected asset folders without renaming the `creator-01` or `scene-warm-desk-smile` stems.
5. Save the inventory with counts, missing paths and a PASS/WARN/FAIL verdict to `projects/<project>/asset-manager.json`.
6. Re-open that JSON and assert every listed `present` path exists on disk; log any mismatch to error-log-keeper.

# How to test

- `python scripts/skill_tools.py asset-manager --self-test` → expected `PASS asset-manager: ...`. Then confirm `projects/<project>/asset-manager.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

channel config -> all stage folders

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
