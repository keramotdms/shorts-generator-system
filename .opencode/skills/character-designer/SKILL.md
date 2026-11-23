---
name: character-designer
description: Designs the 2D character look.
category: character
status: implemented
phase: 3
type: prompt-only
batch: 5
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when designs the 2d character look for a video in `projects/<project>/`.

# Purpose

Designs the 2D character look.

# Input

- `config/style-bible.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `assets/characters/creator-01.json`
- `assets/characters/creator-01-neutral.svg`
- `assets/characters/creator-01-neutral.png`

# Steps

1. Read `config/style-bible.json` (`style.palette`, `style.visual_style`, `characters`, `voice`) and `projects/<project>/02-script/latest_script.json` through project-memory. Stop if the style bible is missing or has no palette.
2. Derive one reusable character: `id` in lowercase-kebab-case, `name` in the project language, `appearance` with `body`, `hair`, `clothing` and a `palette` copied from the style bible, and `voice` with `gender` and `tone` matching the script's narrator.
3. Check the design against the real 2D constraint: simple shapes only (circle head, rounded body, 2-3 clothing shapes), no fine facial detail, no gradients, no photo texture. Describe each part in one short English phrase.
4. Write `assets/characters/creator-01.json` under `assets/characters/`; create that folder first.
5. Run `python scripts/schema_validator.py character assets/characters/creator-01.json`, re-open the file, and log any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.
6. Render the three reusable flat-shape views with `python scripts/svg_scene_builder.py character --character assets/characters/creator-01.json --expression neutral --out assets/characters/creator-01-neutral`, then repeat with `smile` and `surprised`. The helper validates the SVG, rasterizes it to PNG with the already-installed Edge renderer, and prints both exact paths.

**Acceptance criteria**
- `character.json` passes `config/schemas/character.json`.
- `id` matches `^[a-z0-9-]+$` and is unique inside `assets/characters/`.
- `appearance.palette` is copied from `config/style-bible.json`, not invented.
- `voice.gender` and `voice.tone` agree with the script's narrator.
- `assets/characters/creator-01-neutral.svg/.png`, `creator-01-smile.svg/.png` and `creator-01-surprised.svg/.png` exist, parse as SVG, and are exactly 1080x1920 PNGs.

**Output format (short example)**
```json
{
  "id": "creator-01",
  "name": "অনিক",
  "style_source": "config/style-bible.json",
  "appearance": {
    "body": "slim, rounded young adult", "hair": "short black hair",
    "clothing": "simple blue shirt",
    "palette": ["#111827", "#F9FAFB", "#F59E0B", "#10B981"]
  },
  "voice": {"gender": "male", "tone": "calm and conversational"}
}
```

**Quality rules**
1. Use at most 3 clothing shapes so the look stays consistent across scenes.
2. Keep hair, shirt and palette identical for this `id` in every scene.
3. Do not add a second character here; create a new file with a new `id` instead.
4. Reuse `scripts/svg_scene_builder.py` for every expression; never hand-edit the generated SVG or PNG.

# How to test

- Type: `Use the character-designer skill with PROJECT=<project>`. Expected: `assets/characters/creator-01.json` exists, parses cleanly, and contains no hardcoded niche or language value.
- Run `python scripts/svg_scene_builder.py --self-test` → expected `PASS svg-scene-builder: PNG 1080x1920 ...`.
- Run `python scripts/svg_scene_builder.py sample` → expected `assets/characters/creator-01-neutral.png`, `creator-01-smile.png` and `creator-01-surprised.png` are printed as OUTPUT paths.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

style bible -> collector

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
