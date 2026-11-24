---
name: scenario-designer
description: Builds scene layouts and visual plans.
category: scene
status: implemented
phase: later
type: prompt-only
batch: 5
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when builds scene layouts and visual plans for a video in `projects/<project>/`.

# Purpose

Builds scene layouts and visual plans.

# Input

- `projects/<project>/02-script/latest_script.json`
- `config/style-bible.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/05-scene/scenario-designer.json`
- `assets/scenes/warm-desk-background.svg`
- `assets/scenes/scene-warm-desk-smile.png`

- Format `json_utf8`: `projects/<project>/05-scene/scenario-designer.json`
- Format `svg_layered`: `assets/scenes/warm-desk-background.svg`
- Format `png_transparent`: `assets/scenes/scene-warm-desk-smile.png`

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `collector output + style bible`; if it is missing or malformed, follow Failure handling and stop.
3. Lay out the scene as flat shapes: background colour from the character JSON palette, the character placed inside the 9:16 frame, and one prop that matches the scene visual prompt.
4. Write the result to `projects/<project>/05-scene/scenario-designer.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/05-scene/scenario-designer.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.
6. Draw the scene with `python scripts/svg_scene_builder.py scene --character assets/characters/creator-01/character.json --description "<scene visual prompt>" --out assets/scenes/scene-warm-desk-smile --background-out assets/scenes/warm-desk-background`. The helper infers expression and pose from the description, draws a flat-shape background plus character, validates the SVG, rasterizes both PNGs with the already-installed Edge renderer, and prints the exact paths.

**Acceptance criteria**
- `projects/<project>/05-scene/scenario-designer.json` is valid and non-empty.
- `assets/scenes/warm-desk-background.svg/.png` and `assets/scenes/scene-warm-desk-smile.svg/.png` exist.
- Rendered PNGs are exactly 1080x1920 and use the palette from the character JSON.
- No fine detail, gradient or photo texture appears in the SVG.

# How to test

- Type: `Use the scenario-designer skill with PROJECT=<project>`. Expected: `projects/<project>/05-scene/scenario-designer.json` exists, parses cleanly, and contains no hardcoded niche or language value.
- Run `python scripts/svg_scene_builder.py --self-test` → expected `PASS svg-scene-builder: PNG 1080x1920 ...`.
- Run `python scripts/svg_scene_builder.py sample` → expected `assets/scenes/warm-desk-background.png` and `assets/scenes/scene-warm-desk-smile.png` are printed as OUTPUT paths.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

collector -> video-maker

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
