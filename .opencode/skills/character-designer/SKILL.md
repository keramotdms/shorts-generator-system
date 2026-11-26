---
name: character-designer
description: Designs the 2D character look.
category: character
status: implemented
phase: 3
type: script-backed
batch: 5
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when designing the 2D character look for a video in `projects/<project>/`.

# Purpose

Build a reusable, parametric 2D presenter from a short brief. The skill picks parts by documented rules (role, age, personality, niche), creates three distinct candidates, locks the best one, and renders layered SVGs plus PNG previews. It supports `detail_level` = `basic`, `standard`, `rich` or `pro`; `pro` adds outline weight variation, inner shadow, rim light, fabric weave, four hair-strand layers, ear/neck shading and five-finger hands without changing creator-01's role, palette or proportions. It also builds a three-character cast (creator, mentor, learner) from the same part library and a prop sheet (coin, phone, notebook, bar-graph board, wallet). It uses the shared `scripts/svg_scene_builder.py` renderer, so the locked look is identical in later scenes.

# Input

- `config/style-bible.json` — palette, `style.skin_palette`, font, channel voice.
- `projects/<project>/04-character/character-brief.json` — `role`, `age`, `gender`, `personality`, `niche`, `language`, `name`, `character_id`.
- `assets/character-parts/parts.json` — parametric SVG parts, the expression/pose map, the `detail` layer library (face, hair, outfit, body, hands), the `detail.pro` layer library, 8 skin tones, 11 outfits and 9 accessories, the 5 props, and the culture notes.
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `assets/characters/creator-01/character.json` — locked creator design (part IDs, colours, proportions)
- `assets/characters/creator-01/layered.svg` — creator layers, each part in its own `<g id="...">`
- `assets/characters/creator-01/preview.png` — creator neutral/idle preview at 1080x1920
- `assets/characters/creator-01/preview-sheet.png` — creator 5 expressions x 3 poses at 1080x1920
- `assets/characters/creator-01/compare.png` — basic vs rich detail, 5 expressions at 1080x1920
- `assets/characters/creator-01-neutral.svg` — legacy neutral expression view
- `assets/characters/creator-01-neutral.png` — legacy neutral expression view
- `assets/characters/creator-01-smile.svg` — legacy smile expression view
- `assets/characters/creator-01-smile.png` — legacy smile expression view
- `assets/characters/creator-01-surprised.svg` — legacy surprised expression view
- `assets/characters/creator-01-surprised.png` — legacy surprised expression view
- `projects/<project>/04-character/character-design-set.json` — generated output
- `assets/characters/creator-01/compare-rich-pro.svg` — rich vs pro detail, 5 expressions at 1080x1920
- `assets/characters/creator-01/compare-rich-pro.png` — rich vs pro detail, 5 expressions at 1080x1920
- `assets/characters/mentor-01/character.json` — locked mentor design (panjabi, tupi)
- `assets/characters/mentor-01/layered.svg` — mentor layered SVG
- `assets/characters/mentor-01/preview.png` — mentor neutral preview at 1080x1920
- `assets/characters/learner-01/character.json` — locked learner design (salwar kameez)
- `assets/characters/learner-01/layered.svg` — learner layered SVG
- `assets/characters/learner-01/preview.png` — learner neutral preview at 1080x1920
- `assets/characters/cast/cast-sheet.svg` — creator, mentor and learner in one art family
- `assets/characters/cast/cast-sheet.png` — creator, mentor and learner in one art family
- `assets/characters/props/props-sheet.svg` — coin, phone, notebook, bar-graph board, wallet
- `assets/characters/props/props-sheet.png` — coin, phone, notebook, bar-graph board, wallet
- `projects/<project>/04-character/character-cast.json` — cast family and prop report

- Format `json_utf8`: `assets/characters/creator-01/character.json`
- Format `svg_layered`: `assets/characters/creator-01/layered.svg`
- Format `png_transparent`: `assets/characters/creator-01/preview.png`
- Format `png_transparent`: `assets/characters/creator-01/preview-sheet.png`
- Format `png_transparent`: `assets/characters/creator-01/compare.png`
- Format `svg_layered`: `assets/characters/creator-01-neutral.svg`
- Format `png_transparent`: `assets/characters/creator-01-neutral.png`
- Format `svg_layered`: `assets/characters/creator-01-smile.svg`
- Format `png_transparent`: `assets/characters/creator-01-smile.png`
- Format `svg_layered`: `assets/characters/creator-01-surprised.svg`
- Format `png_transparent`: `assets/characters/creator-01-surprised.png`
- Format `json_utf8`: `projects/<project>/04-character/character-design-set.json`
- Format `svg_layered`: `assets/characters/creator-01/compare-rich-pro.svg`
- Format `png_transparent`: `assets/characters/creator-01/compare-rich-pro.png`
- Format `json_utf8`: `assets/characters/mentor-01/character.json`
- Format `svg_layered`: `assets/characters/mentor-01/layered.svg`
- Format `png_transparent`: `assets/characters/mentor-01/preview.png`
- Format `json_utf8`: `assets/characters/learner-01/character.json`
- Format `svg_layered`: `assets/characters/learner-01/layered.svg`
- Format `png_transparent`: `assets/characters/learner-01/preview.png`
- Format `svg_layered`: `assets/characters/cast/cast-sheet.svg`
- Format `png_transparent`: `assets/characters/cast/cast-sheet.png`
- Format `svg_layered`: `assets/characters/props/props-sheet.svg`
- Format `png_transparent`: `assets/characters/props/props-sheet.png`
- Format `json_utf8`: `projects/<project>/04-character/character-cast.json`

# Steps

1. Read `config/style-bible.json`, `projects/<project>/04-character/character-brief.json` and `assets/character-parts/parts.json` through project-memory. Stop if any is missing.
2. Run `python scripts/skill_tools.py character-designer` (or `python scripts/character_designer.py`). The script applies the documented rules: role picks outfit and accessory, age picks head/body, personality picks eyes/brows/mouth, and the palette comes only from the style bible.
3. Choose `detail_level` (`pro` is the default): `basic` keeps the 10 flat layers, `standard` adds the face and hair detail set, `rich` adds outfit, hands, shoes, ground shadow and gradients, and `pro` adds outline variation, inner shadow, rim light, fabric weave, four hair-strand layers, ear/neck shading and five-finger hands.
4. The script writes three candidates to `assets/characters/creator-01-candidate-01/`, `-candidate-02/`, `-candidate-03/`, each with `character.json`, `layered.svg` and `preview.png`.
5. It scores each candidate with `fit_score`, locks the winner as `assets/characters/creator-01/character.json`, and writes the layered SVG, previews, expression/pose sheet, `compare.png` (basic vs rich) and `compare-rich-pro.png` (rich vs pro).
6. It builds `mentor-01` (panjabi and tupi) and `learner-01` (salwar kameez) from the same part library, writes their previews, then renders `assets/characters/cast/cast-sheet.png` and `assets/characters/props/props-sheet.png`.
7. It regenerates the three legacy expression views from the locked design so every downstream consumer sees the same look.
8. It validates the locked file and the cast against `config/schemas/character.json`, checks every layer id, gradient def, stroke width, five-finger hand marker and SVG size, measures the PNGs, and reports the evidence in `projects/<project>/04-character/character-design-set.json` and `character-cast.json`.

**Acceptance criteria (numeric)**
- `character.json` passes `config/schemas/character.json`; `id` matches `^[a-z0-9-]+$`.
- Exactly 3 distinct candidates are produced and one is locked with `locked: true`.
- `detail_level` is one of `basic`, `standard`, `rich` or `pro`; `pro` is the default and is used for `creator-01`.
- `basic` contains the 10 base layer ids: body, outfit, arms, neck, head, hair, brows, eyes, mouth, accessory.
- `standard` adds 13 face/hair ids: ears, jaw_shadow, hairline_shadow, hair_strands, hair_highlight, brow_detail, iris, pupils, eye_highlights, eyelids, lashes, nose, blush.
- `rich` adds 8 body/outfit/hand ids: ground_shadow, shoes, folds, belt, collar, placket, cuffs, hands (31 ids total).
- `pro` adds 9 ids: inner_shadow, rim_light, ear_shading, neck_shading, fabric_pattern, hair_strands_02, hair_strands_03, hair_strands_04, outline_variation (40 ids total).
- `standard`, `rich` and `pro` define 4 linear gradients (skin, hair, outfit, iris); `pro` uses only the documented stroke scale: 14 contour, 10 outline, 6 inner, 4 detail, 44 arm body.
- `pro` hands carry `data-fingers="5"` on both hands; eyebrow, eyelid, mouth and blush layers change for every one of the 5 expressions.
- The part library exposes 8 skin tones, 11 outfits (including panjabi, shirt+trousers, salwar kameez and saree), 9 accessories (including tupi and glasses) and 5 props (coin, phone, notebook, bar-graph board, wallet).
- `mentor-01` and `learner-01` share `creator-01`'s outline colour, light colour and `art_family` measurements, so all three sit in one art family.
- The layered SVG stays under 200 KB and one pro PNG render finishes in under 5 seconds.
- Head-to-body ratio is between 0.18 and 0.30 (inclusive).
- Skin/outline contrast ratio is at least 3.0.
- `appearance.palette` has at least 3 distinct hex colours, all sourced from `config/style-bible.json`.
- Every PNG is exactly 1080x1920, and two renders of the same design are byte-identical.
- The preview sheet covers 5 expressions (neutral, happy, worried, surprised, thinking) x 3 poses (idle, wave, point).
- Each expression changes eyebrows, eyelids, mouth and cheeks together; `mouth_shapes` still exposes closed, open, wide and smile for lip-sync.
- `compare.png` shows basic and rich side by side, and `compare-rich-pro.png` shows rich and pro side by side, for all 5 expressions at 1080x1920.
- `cast-sheet.png` shows creator-01, mentor-01 and learner-01; `props-sheet.png` shows all 5 props, both at 1080x1920.

**Bangla cultural note**
- Use a Bengali name in `name` (for example "রাফি", "রফিক" or "তিশা") and the `role_label` in Bengali (শিক্ষক, শিক্ষার্থী, ফ্রিল্যান্সার, দোকানদার, চাকরিজীবী, কনটেন্ট ক্রিয়েটর).
- Pick context-appropriate clothing from the part library: `outfit-panjabi` or `outfit-kurta` with optional `accessory-tupi`, `outfit-shirt-trousers` for an office/bank role, `outfit-salwar-kameez` for the learner, `outfit-saree` for a woman at an event, and `outfit-shirt-vest` for the teacher.
- Treat `accessory-tupi` and `accessory-earrings` as optional, never automatic for a role.
- Draw from all 8 `style.skin_palette` tones so Bangladesh / Bangla-speaking viewers see skin-tone variety; never hardcode one tone.

**Output format (short example)**
```json
{
  "id": "creator-01",
  "name": "রাফি",
  "style_source": "config/style-bible.json",
  "parts": {"head": "head-oval", "hair": "hair-short-crop", "eyes": "eyes-round",
            "brows": "brows-soft", "mouth": "mouth-smile", "body": "body-slim",
            "outfit": "outfit-shirt-vest", "accessory": "accessory-glasses"},
  "proportions": {"head_height": 356, "total_height": 1290, "head_to_body": 0.276,
                  "shoulder_width": 170},
  "detail_level": "pro",
  "culture": {"region": "Bangladesh", "skin_tone": "light warm",
              "outfit_name": "Shirt with vest", "accessory_name": "Glasses"},
  "art_family": {"outline_width": 10, "contour_width": 14, "inner_width": 6,
                 "detail_width": 4, "light_direction": "top-left"}
}
```

**Quality rules**
1. Choose parts with the documented rules; never pick randomly and never hand-edit a generated SVG or PNG.
2. Keep part IDs, colours and proportions identical for one `id` across every scene. `creator-01`'s role, palette, outfit and proportions are locked and must not change when the detail level changes.
3. Do not add a second unrelated character here; add a cast member that reuses the same part library, outline width and light direction.
4. Reuse `scripts/svg_scene_builder.py` for all rasterising.
5. Keep `detail_level` explicit in `character.json`; never hand-edit a generated layer, gradient or stroke width.
6. Every cast member must declare the same `art_family` values so scenes can mix them safely.

# How to test

- `python scripts/skill_tools.py character-designer --self-test` → expected `PASS character-designer: 3 distinct pro candidates, 40 layers each, schema valid`, then pro hair/hands/strokes, byte-identical render, render-time, expression, basic/rich, creator-identity, cast, props, preview-sheet, compare-sheet and rich-vs-pro PASS lines.
- `PROJECT=<project> python scripts/skill_tools.py character-designer` → expected `PASS character-designer: 3 candidates, locked creator-01 at pro detail with 40 layers ...` plus OUTPUT paths for the character, design set, cast and report.
- `python scripts/character_designer.py --detail-level rich` → still writes a valid 31-layer character with the 10/4/44 stroke scale.
- `python scripts/character_designer.py --detail-level basic` → still writes a valid 10-layer character without gradients.
- `python scripts/schema_validator.py character assets/characters/creator-01/character.json` → expected `PASS character`.
- Show `assets/characters/creator-01/compare-rich-pro.png`, `assets/characters/cast/cast-sheet.png` and `assets/characters/props/props-sheet.png` and confirm they match the described look.
- Checklist: context came from project-memory; input validated; output paths are exact; no placeholder steps remain.

# Depends on / feeds into

style bible -> collector

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
