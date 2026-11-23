---
name: consistency-guardian
description: Checks character consistency across scenes.
category: character
status: implemented
phase: later
type: checker
batch: 5
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checking character consistency across scenes for a video in `projects/<project>/`.

# Purpose

Compares every rendered scene against the locked parametric character and proves the same part IDs, colours and proportions produce byte-identical renders.

# Input

- `projects/<project>/06-video/scenes/`
- `assets/characters/creator-01/character.json`
- `assets/character-parts/parts.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/04-character/consistency-guardian.json`

# Steps

1. Build a reference fingerprint from `assets/characters/creator-01/character.json`: every `parts` key/value (part IDs and hex colours) plus `proportions` (head height, total height, head-to-body ratio, shoulder width).
2. Render the same design twice with `scripts/character_designer.py` and compare the two PNGs by SHA-256; any difference is FAIL.
3. Inspect every MP4 in `projects/<project>/06-video/scenes/` and extract its first frame with ffmpeg.
4. Compare each frame with the fingerprint; flag a changed shirt colour, hair style, skin tone or missing palette colour as FAIL.
5. Count scene files and compare that number with the collector scene list; a gap is WARN.
6. Save frame indexes, mismatch reasons, both render hashes and a continuity verdict to `projects/<project>/04-character/consistency-guardian.json`.
7. Assert the report lists every scene filename that was examined.

# How to test

- `python scripts/skill_tools.py consistency-guardian --self-test` → expected `PASS consistency-guardian: identical part ids/colors/proportions and byte-identical renders across two scenes`. Then confirm `projects/<project>/04-character/consistency-guardian.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

video-maker -> final-test

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
