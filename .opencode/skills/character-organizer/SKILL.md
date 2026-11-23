---
name: character-organizer
description: Indexes character JSON files and their references.
category: character
status: implemented
phase: later
type: prompt-only
batch: A
schema: inventory
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after character-thinker-counter and before character-designer, when several character files and PNG sheets start accumulating in assets/characters/.

# Purpose

Keep one canonical JSON file per character id and produce an inventory that maps every file to its purpose and version.

# Input

- - `assets/characters/*.json`
- - `projects/<project>/04-character/character-thinker-counter.json`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `character reference index`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Naming and version rules

1. One JSON file per character id; duplicate ids are a FAIL.
2. File name must equal the `id` field plus `.json`, in lowercase-kebab-case.
3. Every expression PNG must be named `<id>-<expression>.png` with expression from neutral, smile or surprised.
4. Increment `version` only when the character JSON changes, not when a PNG is regenerated.
5. Mark superseded files as `archive`, never delete them silently.

# Output format (short example)

Schema: `config/schemas/inventory.json`

```json
{
  "status": "PASS",
  "skill": "character-organizer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "entries": [
    {
      "path": "assets/characters/creator-01.json",
      "version": 1,
      "purpose": "canonical look from the shortlist",
      "state": "active"
    },
    {
      "path": "assets/characters/creator-01-smile.png",
      "version": 1,
      "purpose": "smile expression sheet",
      "state": "active"
    },
    {
      "path": "assets/characters/creator-00.json",
      "version": 1,
      "purpose": "old draft kept for reference",
      "state": "archive"
    }
  ],
  "summary": "Three character files indexed; one active id and one archived draft."
}
```

# Quality rules

1. Each path exists on disk at the time of the run.
2. Version numbers are positive integers.
3. No two active entries share the same character id.

# Steps

1. Load the shortlist ids from `projects/<project>/04-character/character-thinker-counter.json`.
2. List every JSON and PNG under `assets/characters/` without following links.
3. Compare each file name to its `id` field and record mismatches as FAIL entries.
4. Assign version numbers from the existing file metadata or start at 1.
5. Write the inventory to `projects/<project>/04-character/character-organizer.json`.
6. Validate against `config/schemas/inventory.json` and report duplicate ids.

# How to test

- Run `python scripts/svg_scene_builder.py sample`, then `python tests/test_no_template.py` to check the inventory output.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/inventory.json` by `tests/test_no_template.py`.

# Depends on / feeds into

character-thinker-counter -> character-designer

# Failure handling

If two files claim the same character id, write a FAIL inventory listing both exact paths and stop before character-designer runs.
