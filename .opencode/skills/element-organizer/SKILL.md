---
name: element-organizer
description: Versions and indexes scene elements.
category: scene
status: implemented
phase: later
type: prompt-only
batch: A
schema: inventory
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after element-designer and before scenario-designer, when an element has been edited more than once or lives in several folders.

# Purpose

Assign versions to scene elements and keep one active index so scenario-designer always picks the current file.

# Input

- `projects/<project>/05-scene/element-designer.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/05-scene/element-organizer.json`

- Format `json_utf8`: `projects/<project>/05-scene/element-organizer.json`

# Versioning rules

1. Only one entry per element name may have state `active`.
2. Bump version by 1 when the SVG bytes change; otherwise keep the existing number.
3. Archive older files instead of deleting them so renders stay reproducible.
4. Record the exact relative path, never an absolute Windows path.
5. Sort entries by element name so the index is deterministic.

# Output format (short example)

Schema: `config/schemas/inventory.json`

```json
{
  "status": "PASS",
  "skill": "element-organizer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "entries": [
    {
      "path": "assets/scenes/warm-desk-background.svg",
      "version": 2,
      "purpose": "active version after palette fix",
      "state": "active"
    },
    {
      "path": "assets/scenes/warm-desk-background-v1.svg",
      "version": 1,
      "purpose": "previous palette kept for rollback",
      "state": "archive"
    },
    {
      "path": "assets/scenes/warm-desk-notebook.svg",
      "version": 1,
      "purpose": "unchanged notebook prop",
      "state": "active"
    }
  ],
  "summary": "Three versions indexed; one active background at version 2 and one archived original."
}
```

# Quality rules

1. No element name has two active entries.
2. Every path starts with assets/scenes/.
3. Version numbers increase by exactly 1 between successive states of one element.

# Steps

1. Open `projects/<project>/05-scene/element-designer.json` and list current active files.
2. Hash each SVG file and compare it with the recorded version to decide whether to bump.
3. Rename superseded copies to a `-v<number>` suffix and mark them archive.
4. Sort the resulting entries by name and write `projects/<project>/05-scene/element-organizer.json`.
5. Validate against `config/schemas/inventory.json` and assert one active entry per name.
6. Report any path that is absolute or missing from disk.

# How to test

- Run `python tests/test_skills.py --batch 5`, then validate `projects/_template/05-scene/element-organizer.json` with the inventory schema.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/inventory.json` by `tests/test_no_template.py`.

# Depends on / feeds into

element-designer -> scenario-designer

# Failure handling

If an SVG file is missing, keep its last known entry as archive and write a WARN with the path. Never invent a replacement file.
