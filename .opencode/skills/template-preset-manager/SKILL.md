---
name: template-preset-manager
description: Stores reusable editing templates.
category: video-editing
subcategory: automation-export
status: implemented
phase: later
type: prompt-only
batch: C
schema: inventory
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after color-grading-keeper and before variant-batch-renderer, when the same grade and caption layout will be applied to many videos.

# Purpose

Register the small set of edit presets that may be reused across Shorts and keep exactly one active preset for each effect type.

# Input

- `config/style-bible.json` palette and font
- `config/defaults.json` resolution
- `config/presets/*.json` local preset files
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `template library`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Preset rules

1. Maintain exactly three preset types: grade, caption and brand.
2. Only one preset per type may be active; older copies are archive.
3. Every preset path must be a JSON file under config/presets/.
4. Bump the version when the preset bytes change and keep the previous file as archive.
5. Record the resolution source as config/defaults.json in every preset purpose.

# Output format (short example)

Schema: `config/schemas/inventory.json`

```json
{
  "status": "PASS",
  "skill": "template-preset-manager",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "entries": [
    {
      "path": "config/presets/grade-warm.json",
      "version": 2,
      "purpose": "grade preset, defaults.json resolution source",
      "state": "active"
    },
    {
      "path": "config/presets/grade-warm-v1.json",
      "version": 1,
      "purpose": "previous grade preset",
      "state": "archive"
    },
    {
      "path": "config/presets/caption-bangla.json",
      "version": 1,
      "purpose": "caption preset, defaults.json resolution source",
      "state": "active"
    },
    {
      "path": "config/presets/brand-bar.json",
      "version": 1,
      "purpose": "brand preset, defaults.json resolution source",
      "state": "active"
    }
  ],
  "summary": "Three active preset types registered with one archived earlier grade version."
}
```

# Quality rules

1. There is exactly one active entry for each of the three preset types.
2. All paths start with config/presets/ and end in .json.
3. Archived versions have a lower version number than their active counterpart.

# Steps

1. Load the palette, font and resolution through project-memory before reading preset files.
2. List JSON files under config/presets/ and group them by preset type.
3. Compare file bytes with the last known version to decide which entry stays active.
4. Rename older copies with a -v suffix and mark them archive instead of deleting them.
5. Write the preset inventory to projects/<project>/07-edit/template-preset-manager.json.
6. Validate the inventory schema and assert one active entry per preset type.

# How to test

- Validate projects/_template/07-edit/template-preset-manager.json with the inventory schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/inventory.json` by `tests/test_no_template.py`.

# Depends on / feeds into

style bible -> video-editing

# Failure handling

If a preset type has no file, list it as draft with the expected path and stop before variant-batch-renderer. Never copy a preset from another project.
