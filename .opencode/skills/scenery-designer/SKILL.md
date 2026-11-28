---
name: scenery-designer
description: Designs the reusable background plate library for a video.
category: scene
status: implemented
phase: later
type: script-backed
batch: E
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when the script is locked and the video needs its background plates, before `scenario-designer` lays characters, elements and captions on top of them. Runs once per project.

# Purpose

Turn `projects/<project>/02-script/latest_script.json` and `config/style-bible.json` into six reusable 1080x1920 background plates — bedroom-night, study-desk, classroom, shop-interior, street-night and ceremony-hall — plus a report that tells `scenario-designer` which plate every script scene uses. Each plate is a deterministic SVG split into four parallax layers (`bg-base`, `bg-props`, `bg-bokeh`, `bg-vignette`), with a `feGaussianBlur` depth-of-field on the bokeh lights and a radial vignette, rasterised to PNG by the already-installed Microsoft Edge renderer. No colour is hardcoded: every hex is either a `scene_palette` entry from the style bible or the result of blending two style-bible colours, and every base colour is fitted into the style bible's `warm_luminance` or `night_luminance` range.

# Input

- `projects/<project>/02-script/latest_script.json`
- `config/style-bible.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/05-scene/scenery-designer.json` — scene-to-plate map, palette, blur/vignette/luminance rules
- `assets/scenes/scenery/bedroom-night.svg` — night bedroom plate, four parallax layers
- `assets/scenes/scenery/bedroom-night.png` — night bedroom plate at 1080x1920
- `assets/scenes/scenery/study-desk.svg` — warm study-desk plate, four parallax layers
- `assets/scenes/scenery/study-desk.png` — warm study-desk plate at 1080x1920
- `assets/scenes/scenery/classroom.svg` — warm classroom plate, four parallax layers
- `assets/scenes/scenery/classroom.png` — warm classroom plate at 1080x1920
- `assets/scenes/scenery/shop-interior.svg` — warm shop-interior plate, four parallax layers
- `assets/scenes/scenery/shop-interior.png` — warm shop-interior plate at 1080x1920
- `assets/scenes/scenery/street-night.svg` — night street plate, four parallax layers
- `assets/scenes/scenery/street-night.png` — night street plate at 1080x1920
- `assets/scenes/scenery/ceremony-hall.svg` — warm ceremony-hall plate, four parallax layers
- `assets/scenes/scenery/ceremony-hall.png` — warm ceremony-hall plate at 1080x1920

- Format `json_utf8`: `projects/<project>/05-scene/scenery-designer.json`
- Format `svg_layered`: `assets/scenes/scenery/bedroom-night.svg`
- Format `png_frame_1080x1920`: `assets/scenes/scenery/bedroom-night.png`
- Format `svg_layered`: `assets/scenes/scenery/study-desk.svg`
- Format `png_frame_1080x1920`: `assets/scenes/scenery/study-desk.png`
- Format `svg_layered`: `assets/scenes/scenery/classroom.svg`
- Format `png_frame_1080x1920`: `assets/scenes/scenery/classroom.png`
- Format `svg_layered`: `assets/scenes/scenery/shop-interior.svg`
- Format `png_frame_1080x1920`: `assets/scenes/scenery/shop-interior.png`
- Format `svg_layered`: `assets/scenes/scenery/street-night.svg`
- Format `png_frame_1080x1920`: `assets/scenes/scenery/street-night.png`
- Format `svg_layered`: `assets/scenes/scenery/ceremony-hall.svg`
- Format `png_frame_1080x1920`: `assets/scenes/scenery/ceremony-hall.png`

# Output format (short example)
```json
{
  "skill": "scenery-designer",
  "style_profile": "bd-explainer",
  "rules": {"layers": ["bg-base", "bg-props", "bg-bokeh", "bg-vignette"],
            "blur_std_dev": [10, 16], "vignette_pct": [15, 30]},
  "plates": [{"id": "study-desk", "mood": "warm", "blur_std_dev": 11.2,
              "base_luminance": 0.4276, "png": "assets/scenes/scenery/study-desk.png"}],
  "scene_plates": [{"scene_number": 1, "plate": "study-desk",
                    "match": "keyword:desk", "duration_sec": 5}],
  "counts": {"plates": 6, "scenes": 1}
}
```

# Steps

1. Read `projects/<project>/02-script/latest_script.json` and `config/style-bible.json` through project-memory. Stop if either is missing.
2. Run `python scripts/skill_tools.py scenery-designer`. The script loads the active style profile's `scene_palette`, `background.blur_std_dev`, `background.vignette_pct`, `background.warm_luminance` and `background.night_luminance`, and refuses to continue if `night`, `cream`, `warm_tan` or `brown_dark` is missing.
3. The script builds six plate specs. Each wall-top colour is fitted into `warm_luminance` (day plates) or `night_luminance` (night plates) by blending toward `cream` or `night`; blur and vignette values are spread evenly across the style bible's range in plate order.
4. Each plate is rendered as one deterministic SVG with exactly four layer groups — `bg-base` (gradient wall plus floor), `bg-props` (furniture, buildings, curtains and so on), `bg-bokeh` (three or four lights each carrying `filter="url(#dof-<plate>)"` with an `feGaussianBlur`) and `bg-vignette` (radial `stop-opacity` gradient). The blur filter sits on each light rather than the whole group so Edge does not rasterise a 1080x1920 blur.
5. Every hex in the SVG must already be allowed: `blend()` rejects any input outside `scene_palette` plus previously derived colours, so a hardcoded colour raises `SkillError` instead of rendering.
6. Each SVG is written to `assets/scenes/scenery/<plate>.svg` and rasterised to `assets/scenes/scenery/<plate>.png` at exactly 1080x1920 with the installed Edge renderer.
7. Script scenes are mapped to plates by keyword (location words win over mood words: classroom, shop-interior, street-night, ceremony-hall, study-desk, bedroom-night) with a `scene_number` round-robin fallback, and the whole hand-off is written to `projects/<project>/05-scene/scenery-designer.json`.

**Acceptance criteria (numeric)**
- Exactly 6 plates and 13 output files; plate ids are bedroom-night, study-desk, classroom, shop-interior, street-night and ceremony-hall.
- Every plate SVG contains `id="bg-base"`, `id="bg-props"`, `id="bg-bokeh"` and `id="bg-vignette"` and at least one `<feGaussianBlur stdDeviation="...">`.
- Every `fill`, `stop-color` and `stroke` value is either a `scene_palette` colour or a `blend()` result — the self-test fails on any other hex.
- Warm plates report a `base_luminance` inside `background.warm_luminance` (0.35–0.5 by default); night plates inside `background.night_luminance` (0.1–0.25 by default).
- Blur values span `background.blur_std_dev` (10–16) and vignette edge opacity spans `background.vignette_pct` (15–30).
- Building the six SVGs twice produces byte-identical text, and two PNG renders of the same plate are byte-identical at exactly 1080x1920.
- One warm PNG render stays under `MAX_RENDER_SECONDS` (8 s; a bare Edge screenshot already costs 2.9–3.7 s on this machine).
- A scene whose `visual_prompt` mentions a classroom maps to `classroom` with `match` starting `keyword:`; a scene with no keywords maps with `match` = `round-robin`.
- `projects/<project>/05-scene/scenery-designer.json` passes the `json_utf8` profile and declares `counts.plates` = 6.

# How to test

- `python scripts/skill_tools.py scenery-designer --self-test` → expected `PASS scenery-designer: 6 plate specs built from bd-explainer style bible`, then layer/colour, determinism, PNG render, scene-assignment and final PASS lines.
- `PROJECT=<project> python scripts/skill_tools.py scenery-designer` → expected `PASS scenery-designer: plate <id> rendered ...` for all six plates, then `PASS scenery-designer: 6 plates and N scene assignments`, with `OUTPUT` lines for the 12 assets and the report.
- `python -c "import sys; sys.path.insert(0,'scripts'); import scenery_designer as s; print(sorted(s.allowed_colours()))"` → only style-bible colours plus their blends.
- Open `assets/scenes/scenery/street-night.png` and `assets/scenes/scenery/classroom.png` and confirm the four layers read as background, props, soft bokeh lights and a dark edge vignette.
- `python scripts/format_validator.py` → expected `PASS` for the 13 declared outputs once they exist.
- Checklist: context came from project-memory; no hex outside the style bible; every PNG is exactly 1080x1920; no generated file lands inside a skill folder.

# Depends on / feeds into

script-writer and project-memory -> scenario-designer

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the style bible lacks a palette colour the plates need, report the colour name and run project-memory instead of inventing a hex. If Edge is unavailable, report `BLOCKED: svg-to-png` with the exact message from `scripts/svg_scene_builder.py`; never install a converter or change Windows application-control settings to make it run. If a rendered PNG is not 1080x1920 or two renders differ, delete the plate pair and re-run after fixing the SVG — never hand-edit a generated SVG or PNG.
