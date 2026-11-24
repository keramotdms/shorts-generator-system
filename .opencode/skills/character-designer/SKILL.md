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

Build a reusable, parametric 2D presenter from a short brief. The skill picks parts by documented rules (role, age, personality, niche), creates three distinct candidates, locks the best one, and renders layered SVGs plus PNG previews. It uses the shared `scripts/svg_scene_builder.py` renderer, so the locked look is identical in later scenes.

# Input

- `config/style-bible.json` — palette, `style.skin_palette`, font, channel voice.
- `projects/<project>/04-character/character-brief.json` — `role`, `age`, `gender`, `personality`, `niche`, `language`, `name`, `character_id`.
- `assets/character-parts/parts.json` — parametric SVG parts and the expression/pose map.
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `assets/characters/creator-01/character.json` — locked design (part IDs, colours, proportions).
- `assets/characters/creator-01/layered.svg` — each part in its own `<g id="...">`.
- `assets/characters/creator-01/preview.png` — neutral/idle preview at 1080x1920.
- `assets/characters/creator-01/preview-sheet.png` — 5 expressions x 3 poses at 1080x1920.
- `assets/characters/creator-01-neutral.svg` / `assets/characters/creator-01-neutral.png` — legacy expression view.
- `assets/characters/creator-01-smile.svg` / `assets/characters/creator-01-smile.png` — legacy expression view.
- `assets/characters/creator-01-surprised.svg` / `assets/characters/creator-01-surprised.png` — legacy expression view.
- `projects/<project>/04-character/character-design-set.json` — candidates, chosen design, criteria.

- Format `json_utf8`: `assets/characters/creator-01/character.json`
- Format `svg_layered`: `assets/characters/creator-01/layered.svg`
- Format `png_transparent`: `assets/characters/creator-01/preview.png`
- Format `png_transparent`: `assets/characters/creator-01/preview-sheet.png`
- Format `svg_layered`: `assets/characters/creator-01-neutral.svg`
- Format `png_transparent`: `assets/characters/creator-01-neutral.png`
- Format `svg_layered`: `assets/characters/creator-01-smile.svg`
- Format `png_transparent`: `assets/characters/creator-01-smile.png`
- Format `svg_layered`: `assets/characters/creator-01-surprised.svg`
- Format `png_transparent`: `assets/characters/creator-01-surprised.png`
- Format `json_utf8`: `projects/<project>/04-character/character-design-set.json`

# Steps

1. Read `config/style-bible.json`, `projects/<project>/04-character/character-brief.json` and `assets/character-parts/parts.json` through project-memory. Stop if any is missing.
2. Run `python scripts/skill_tools.py character-designer` (or `python scripts/character_designer.py`). The script applies the documented rules: role picks outfit and accessory, age picks head/body, personality picks eyes/brows/mouth, and the palette comes only from the style bible.
3. The script writes three candidates to `assets/characters/creator-01-candidate-01/`, `-candidate-02/`, `-candidate-03/`, each with `character.json`, `layered.svg` and `preview.png`.
4. It scores each candidate with `fit_score`, locks the winner as `assets/characters/creator-01/character.json`, and writes the layered SVG, previews and expression/pose sheet.
5. It regenerates the three legacy expression views from the locked design so every downstream consumer sees the same look.
6. It validates the locked file against `config/schemas/character.json`, checks every layer id, measures the PNGs and reports the evidence in `projects/<project>/04-character/character-design-set.json`.

**Acceptance criteria (numeric)**
- `character.json` passes `config/schemas/character.json`; `id` matches `^[a-z0-9-]+$`.
- Exactly 3 distinct candidates are produced and one is locked with `locked: true`.
- The layered SVG contains all 10 layer ids: body, outfit, arms, neck, head, hair, brows, eyes, mouth, accessory.
- Head-to-body ratio is between 0.18 and 0.30 (inclusive).
- Skin/outline contrast ratio is at least 3.0.
- `appearance.palette` has at least 3 distinct hex colours, all sourced from `config/style-bible.json`.
- Every PNG is exactly 1080x1920, and two renders of the same design are byte-identical.
- The preview sheet covers 5 expressions (neutral, happy, worried, surprised, thinking) x 3 poses (idle, wave, point).

**Bangla cultural note**
- Use a Bengali name in `name` (for example "রাফি" or "নুসরাত") and the `role_label` in Bengali (শিক্ষক, শিক্ষার্থী, ফ্রিল্যান্সার, দোকানদার, চাকরিজীবী, কনটেন্ট ক্রিয়েটর).
- Pick context-appropriate clothing from the part library: `outfit-panjabi`, `outfit-kurta`, `outfit-shirt-vest` or `outfit-formal` for a finance teacher; `outfit-hoodie` or `outfit-t-shirt` for a student/freelancer.
- Draw from the full `style.skin_palette` so Bangladesh / Bangla-speaking viewers see skin-tone variety; never hardcode one tone.

**Output format (short example)**
```json
{
  "id": "creator-01",
  "name": "রাফি",
  "style_source": "config/style-bible.json",
  "parts": {"head": "head-oval", "hair": "hair-side-part", "eyes": "eyes-round",
            "brows": "brows-soft", "mouth": "mouth-smile", "body": "body-average",
            "outfit": "outfit-shirt-vest", "accessory": "accessory-glasses"},
  "proportions": {"head_height": 356, "total_height": 1300, "head_to_body": 0.274}
}
```

**Quality rules**
1. Choose parts with the documented rules; never pick randomly and never hand-edit a generated SVG or PNG.
2. Keep part IDs, colours and proportions identical for one `id` across every scene.
3. Do not add a second character here; create a new `character_id` in the brief instead.
4. Reuse `scripts/svg_scene_builder.py` for all rasterising.

# How to test

- `python scripts/skill_tools.py character-designer --self-test` → expected `PASS character-designer: 3 distinct candidates, 10 layers each, schema valid`, then the byte-identical render and preview-sheet PASS lines.
- `PROJECT=<project> python scripts/skill_tools.py character-designer` → expected `PASS character-designer: 3 candidates, locked creator-01 ...` plus OUTPUT paths for the character, design set and report.
- `python scripts/schema_validator.py character assets/characters/creator-01/character.json` → expected `PASS character`.
- Checklist: context came from project-memory; input validated; output paths are exact; no placeholder steps remain.

# Depends on / feeds into

style bible -> collector

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
