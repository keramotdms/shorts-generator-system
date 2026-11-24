---
name: script-video-voice-collector
description: Gathers script, video clips and voice for editing.
category: video-editing
subcategory: core
status: implemented
phase: later
type: prompt-only
batch: B
schema: inventory
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after video-maker and before rough-cut-assembler, when several scene versions exist and the editor needs one authoritative edit package.

# Purpose

Verify and index the exact script, rendered scene clips and voiceover file that rough-cut-assembler needs, so editing never starts with stale assets.

# Input

- `projects/<project>/05-scene/collection.json`
- `projects/<project>/06-video/scenes/`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/script-video-voice-collector.json`

- Format `json_utf8`: `projects/<project>/07-edit/script-video-voice-collector.json`

# Edit package rules

1. Require exactly one script file, one voiceover file and at least one scene clip.
2. Every scene clip must carry the same resolution as config/defaults.json.
3. Reject any path written as an absolute Windows drive path.
4. Scene clips must be listed in the numeric order of the script scenes.
5. Mark any clip whose duration differs from its script scene by more than 1 second as draft.

# Output format (short example)

Schema: `config/schemas/inventory.json`

```json
{
  "status": "PASS",
  "skill": "script-video-voice-collector",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "entries": [
    {
      "path": "projects/<project>/02-script/latest_script.json",
      "version": 3,
      "purpose": "locked script for the edit",
      "state": "active"
    },
    {
      "path": "projects/<project>/03-voice/voiceover.mp3",
      "version": 1,
      "purpose": "narration master",
      "state": "active"
    },
    {
      "path": "projects/<project>/06-video/scenes/scene-01.mp4",
      "version": 1,
      "purpose": "scene 1, 7 seconds",
      "state": "active"
    },
    {
      "path": "projects/<project>/06-video/scenes/scene-02-old.mp4",
      "version": 1,
      "purpose": "superseded scene 2",
      "state": "archive"
    }
  ],
  "summary": "Four edit inputs indexed in script order; one superseded scene clip kept as archive."
}
```

# Quality rules

1. All entry paths are relative and begin with projects/<project>/.
2. Exactly one voiceover entry is active.
3. Scene entries appear in ascending numeric order by file name.

# Steps

1. Read resolution from config/defaults.json through project-memory before probing clips.
2. Validate the script with `config/schemas/latest_script.json` and note its scene count.
3. List scene MP4 files and probe each with ffprobe if it is available.
4. Compare clip durations to script scenes and flag deviations over 1 second as draft.
5. Write the edit package to projects/<project>/07-edit/script-video-voice-collector.json.
6. Validate the inventory schema and assert there is exactly one active voiceover row.

# How to test

- Validate projects/_template/07-edit/script-video-voice-collector.json with the inventory schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/inventory.json` by `tests/test_no_template.py`.

# Depends on / feeds into

video-making -> rough-cut-assembler

# Failure handling

If the voiceover or script is missing, stop with a FAIL that names both exact paths. If ffprobe is unavailable, record durations as unverified instead of guessing them.
