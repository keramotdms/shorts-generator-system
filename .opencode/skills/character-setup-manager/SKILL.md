---
name: character-setup-manager
description: Sets up reusable character rigs and layers.
category: character
status: implemented
phase: later
type: prompt-only
batch: B
schema: inventory
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after character-designer and before video-maker, when the character JSON exists but layers are still drawn ad hoc per scene.

# Purpose

Register the flat body, mouth and prop layers that the SVG builder can swap independently, so one character can be reused across every scene.

# Input

- `assets/characters/creator-01.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/04-character/character-setup-manager.json`

# Rig rules

1. Exactly three layers per character: body, mouth and prop.
2. Each layer is a separate SVG file under assets/characters/layers/.
3. Layer names follow `<character-id>-<layer>.svg` in lowercase-kebab-case.
4. Only the mouth layer may be animated between open and closed states.
5. Record the builder name as the entry purpose so the version can be traced.

# Output format (short example)

Schema: `config/schemas/inventory.json`

```json
{
  "status": "PASS",
  "skill": "character-setup-manager",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "entries": [
    {
      "path": "assets/characters/layers/creator-01-body.svg",
      "version": 1,
      "purpose": "svg-builder body layer",
      "state": "active"
    },
    {
      "path": "assets/characters/layers/creator-01-mouth.svg",
      "version": 2,
      "purpose": "svg-builder mouth layer, open state",
      "state": "active"
    },
    {
      "path": "assets/characters/layers/creator-01-prop.svg",
      "version": 1,
      "purpose": "svg-builder notebook prop layer",
      "state": "active"
    }
  ],
  "summary": "Three independent rig layers registered for creator-01 with the mouth at version 2."
}
```

# Quality rules

1. There are exactly three active entries, one for each allowed layer.
2. Every path ends in .svg and starts with assets/characters/layers/.
3. Only the mouth entry has a version above 1.

# Steps

1. Validate assets/characters/creator-01.json against `config/schemas/character.json` first.
2. Read the builder's accepted layer aliases from scripts/svg_scene_builder.py without modifying it.
3. Confirm each of the three layer files exists on disk before registering it.
4. Assign versions from the file metadata and keep old SVGs as archive entries.
5. Write the rig inventory to projects/<project>/04-character/character-setup-manager.json.
6. Validate the inventory schema and check that no layer name is duplicated.

# How to test

- Run `python scripts/svg_scene_builder.py sample` then validate projects/_template/04-character/character-setup-manager.json with the inventory schema.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/inventory.json` by `tests/test_no_template.py`.

# Depends on / feeds into

character-designer -> video-maker

# Failure handling

If a layer file is missing, mark that layer draft with its exact path and stop before video-maker. Never draw a substitute layer outside the SVG builder.
