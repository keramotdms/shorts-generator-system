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

- `collector output + style bible`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `projects/<project>/05-scene/scenario-designer.json`
- `assets/scenes/<scene-id>-background.svg` and `.png`
- `assets/scenes/<scene-id>.svg` and `.png`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `collector output + style bible`; if it is missing or malformed, follow Failure handling and stop.
3. Follow this skill's prompt instructions to builds scene layouts and visual plans, using only the context loaded in step 1.
4. Write the result to `projects/<project>/05-scene/scenario-designer.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/05-scene/scenario-designer.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.
6. Draw the scene with `python scripts/svg_scene_builder.py scene --character assets/characters/<character-id>.json --description "<scene visual prompt>" --out assets/scenes/<scene-id> --background-out assets/scenes/<scene-id>-background`. The helper infers expression and pose from the description, draws a flat-shape background plus character, validates the SVG, rasterizes both PNGs with the already-installed Edge renderer, and prints the exact paths.

**Acceptance criteria**
- `projects/<project>/05-scene/scenario-designer.json` is valid and non-empty.
- `assets/scenes/<scene-id>-background.svg/.png` and `assets/scenes/<scene-id>.svg/.png` exist.
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
