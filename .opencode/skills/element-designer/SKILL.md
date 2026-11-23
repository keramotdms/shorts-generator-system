---
name: element-designer
description: Designs flat reusable scene elements.
category: scene
status: implemented
phase: later
type: prompt-only
batch: A
schema: inventory
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after the character is approved and before scenario-designer, when a scene needs a desk, wallet, phone or notebook prop.

# Purpose

Define a small set of flat 2D scene elements drawn from the style-bible palette so every scene can reuse them without new art.

# Input

- - `config/style-bible.json` palette
- - `projects/<project>/02-script/latest_script.json`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `scene element assets`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Element design rules

1. Design at most 6 elements for one Short.
2. Use only the four palette colours from the style bible plus white and gray for floors.
3. Draw with rect, circle and path only; no gradient, blur or image texture.
4. Each element must be recognisable at 1080x1920 and occupy at least 100 pixels on one axis.
5. Name elements in lowercase-kebab-case such as `warm-desk-notebook`.

# Output format (short example)

Schema: `config/schemas/inventory.json`

```json
{
  "status": "PASS",
  "skill": "element-designer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "entries": [
    {
      "path": "assets/scenes/warm-desk-background.svg",
      "version": 1,
      "purpose": "desk and wall, flat palette shapes",
      "state": "active"
    },
    {
      "path": "assets/scenes/warm-desk-notebook.svg",
      "version": 1,
      "purpose": "notebook prop from the SVG builder",
      "state": "active"
    },
    {
      "path": "assets/scenes/wallet-prop.svg",
      "version": 1,
      "purpose": "wallet prop, draft",
      "state": "draft"
    }
  ],
  "summary": "Three flat elements registered; two active and one draft awaiting script use."
}
```

# Quality rules

1. Every entry path is an .svg file under assets/scenes/.
2. No entry description contains the word gradient or photo.
3. The number of active entries is 6 or fewer.

# Steps

1. Read the palette from `config/style-bible.json` through project-memory.
2. Scan the validated script for prop words such as notebook, wallet or phone.
3. Map each prop word to an existing SVG builder prop or describe a new flat-shape element.
4. Check size and colour limits against the rules above.
5. Write the element list to `projects/<project>/05-scene/element-designer.json`.
6. Validate against `config/schemas/inventory.json` and count active entries.

# How to test

- Run `python scripts/svg_scene_builder.py sample`, then validate `projects/_template/05-scene/element-designer.json` with the inventory schema.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/inventory.json` by `tests/test_no_template.py`.

# Depends on / feeds into

character and voice -> scenario-designer

# Failure handling

If a prop needs texture or fine detail, record it as `draft` with the reason and substitute a simple flat shape rather than blocking the scene.
