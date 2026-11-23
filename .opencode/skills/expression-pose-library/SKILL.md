---
name: expression-pose-library
description: Defines reusable expressions and poses for SVG rendering.
category: character
status: implemented
phase: later
type: prompt-only
batch: A
schema: inventory
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after character-organizer and before scenario-designer, when scene prompts need to name a facial expression or body pose.

# Purpose

Publish the exact expression and pose vocabulary that scripts/svg_scene_builder.py can draw, so scene prompts never ask for unsupported art.

# Input

- `assets/characters/creator-01/character.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/04-character/expression-pose-library.json`

# Library rules

1. Exactly three expressions are supported: neutral, smile, surprised.
2. Exactly four poses are supported: idle, wave, point, think.
3. Each entry path must point to an SVG or PNG produced by the SVG builder.
4. Reject any entry whose name needs fine detail such as fingers or eyebrow texture.
5. Record the builder script version as the entry purpose prefix.

# Output format (short example)

Schema: `config/schemas/inventory.json`

```json
{
  "status": "PASS",
  "skill": "expression-pose-library",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "entries": [
    {
      "path": "assets/characters/creator-01-neutral.png",
      "version": 1,
      "purpose": "svg-builder expression neutral",
      "state": "active"
    },
    {
      "path": "assets/characters/creator-01-smile.png",
      "version": 1,
      "purpose": "svg-builder expression smile",
      "state": "active"
    },
    {
      "path": "assets/characters/creator-01-surprised.png",
      "version": 1,
      "purpose": "svg-builder expression surprised",
      "state": "active"
    },
    {
      "path": "assets/scenes/pose-point-preview.png",
      "version": 1,
      "purpose": "svg-builder pose point",
      "state": "active"
    }
  ],
  "summary": "Three expressions and one pose preview registered for the scene prompt writer."
}
```

# Quality rules

1. Only the seven allowed expression and pose names appear.
2. Every entry path ends in .svg or .png.
3. The library never lists an expression that the builder cannot render.

# Steps

1. Read the palette and character id from `assets/characters/creator-01/character.json` after schema validation.
2. Query the builder's expression and pose alias tables by reading `scripts/svg_scene_builder.py`.
3. Generate one PNG per expression with the builder if the file is missing.
4. Register each generated file with its builder version and state.
5. Write the library to `projects/<project>/04-character/expression-pose-library.json`.
6. Validate against `config/schemas/inventory.json` and reject unknown names.

# How to test

- Run `python scripts/svg_scene_builder.py sample`, then validate `projects/_template/04-character/expression-pose-library.json` with the inventory schema.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/inventory.json` by `tests/test_no_template.py`.

# Depends on / feeds into

character-designer -> video-maker

# Failure handling

If a requested expression is not one of the three supported names, report the unsupported name and substitute neutral with a WARN instead of failing the render.
