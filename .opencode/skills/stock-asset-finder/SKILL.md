---
name: stock-asset-finder
description: Finds reusable stock footage and images.
category: video-editing
subcategory: automation-export
status: implemented
phase: later
type: prompt-only
batch: C
schema: selection
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after scenario-designer and before video-maker, when a scene needs a photo-free visual and no new artwork should be drawn.

# Purpose

Shortlist reusable local images and clips from assets/ for a script's visual gaps, with a score that reflects licence clarity and flat-style fit.

# Input

- `projects/<project>/02-script/latest_script.json`
- `config/style-bible.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/stock-asset-finder.json`

- Format `json_utf8`: `projects/<project>/07-edit/stock-asset-finder.json`

# Asset scoring

1. List only files already inside assets/; no network lookup is allowed.
2. Score each candidate 0–10 for flat-style fit, palette match and licence clarity.
3. Reject any file without a sibling LICENSE note and record the reason.
4. Choose at most two assets per Short and name the scene that uses each one.
5. Prefer PNG or SVG over live-action MP4 for this flat 2D channel.

# Output format (short example)

Schema: `config/schemas/selection.json`

```json
{
  "status": "PASS",
  "skill": "stock-asset-finder",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "candidates": [
    {
      "id": "assets/scenes/warm-desk-background.png",
      "score": 9,
      "reason": "flat shapes, palette match, local LICENSE note"
    },
    {
      "id": "assets/video/crowd-street.mp4",
      "score": 4,
      "reason": "live action, wrong style, no licence note"
    },
    {
      "id": "assets/scenes/wallet-prop.svg",
      "score": 8,
      "reason": "flat wallet prop with licence note"
    }
  ],
  "chosen_id": "assets/scenes/warm-desk-background.png",
  "rationale": "Highest scoring flat asset with a clear local licence; assigned to the opening desk scene."
}
```

# Quality rules

1. Every candidate id is a path that exists under assets/.
2. Chosen id appears in the candidate list.
3. At most two assets are marked as chosen in the rationale.

# Steps

1. Read palette and scene needs from project-memory sources before scanning assets/.
2. Walk assets/scenes/ and assets/video/ for candidate files without following links.
3. Check for a LICENSE note next to each file and record missing ones as rejections.
4. Score candidates on style, palette and licence, then pick up to two.
5. Write the shortlist to projects/<project>/05-scene/stock-asset-finder.json.
6. Validate the selection schema and verify each id resolves to a real local file.

# How to test

- Run `python scripts/svg_scene_builder.py sample`, then validate projects/_template/05-scene/stock-asset-finder.json with the selection schema.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/selection.json` by `tests/test_no_template.py`.

# Depends on / feeds into

research -> scene and video stages

# Failure handling

If no licensed local asset exists, return a WARN selection with no chosen id and ask the user to add an owned file. Never fetch a stock asset from the internet.
