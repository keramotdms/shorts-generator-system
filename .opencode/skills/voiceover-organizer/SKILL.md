---
name: voiceover-organizer
description: Plans narrator gender, scene order and line lengths.
category: voice
status: implemented
phase: later
type: prompt-only
batch: A
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after the script is locked and before voiceover-generator, when the narrator voice and scene reading order are still undecided.

# Purpose

Produce a voice plan that fixes the narrator, speaking order and per-scene word budget before any audio is generated.

# Input

- `projects/<project>/02-script/latest_script.json`
- `config/style-bible.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/03-voice/voiceover-organizer.json`

- Format `json_utf8`: `projects/<project>/03-voice/voiceover-organizer.json`

# Voice plan criteria

1. Use exactly one narrator for the whole Short; a second voice requires a new project.
2. Take gender from `voice.default_gender` in the style bible instead of choosing it here.
3. Keep each scene to at most 18 Bangla words so it fits one breath.
4. Order scenes by the script's beat order, never by file name.
5. Reserve the last scene for the loop line and mark it as the final item.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "voiceover-organizer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Narrate hook: one coffee costs ৳120",
      "start_sec": 0,
      "end_sec": 6,
      "reason": "12 Bangla words, under 18"
    },
    {
      "id": 2,
      "action": "Narrate monthly total",
      "start_sec": 6,
      "end_sec": 18,
      "reason": "16 Bangla words"
    },
    {
      "id": 3,
      "action": "Narrate loop line",
      "start_sec": 38,
      "end_sec": 45,
      "reason": "reserved final 7 seconds"
    }
  ],
  "constraints": [
    "one narrator",
    "gender from style bible",
    "max 18 Bangla words per scene"
  ],
  "summary": "Single male narrator reads three grouped scenes in beat order with a reserved loop line."
}
```

# Quality rules

1. The gender string matches the style bible value exactly.
2. No item contains more than 18 words when split on whitespace.
3. Items follow the numeric order of script scenes.

# Steps

1. Read the voice block from `config/style-bible.json` through project-memory.
2. Validate `projects/<project>/02-script/latest_script.json` against its schema.
3. Count words per scene and group adjoining short scenes into one reading unit.
4. Assign the style-bible gender to the single narrator and mark the last scene as the loop line.
5. Write the plan to `projects/<project>/03-voice/voiceover-organizer.json`.
6. Validate against `config/schemas/plan.json` and report any scene over 18 words.

# How to test

- Run `python scripts/schema_validator.py plan projects/_template/03-voice/voiceover-organizer.json` then `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

script-writer -> voiceover-generator

# Failure handling

If the style bible has no voice.default_gender, stop and ask project-memory to regenerate it. Never default to a gender based on the creator's name.
