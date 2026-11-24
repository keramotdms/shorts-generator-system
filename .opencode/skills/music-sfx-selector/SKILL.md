---
name: music-sfx-selector
description: Chooses licensed-safe music and SFX cues.
category: voice
status: implemented
phase: later
type: prompt-only
batch: A
schema: selection
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after the scene plan exists and before audio-mixer, when the video needs a music bed and a few accent sounds.

# Purpose

Select a background music track and a short sound-effect list that fit the scene mood while staying inside the mixer's gain budget.

# Input

- `config/style-bible.json`
- `projects/<project>/02-script/latest_script.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/03-voice/music-sfx-selector.json`

- Format `json_utf8`: `projects/<project>/03-voice/music-sfx-selector.json`

# Selection criteria

1. Choose at most one music bed and at most three SFX cues for a 60-second Short.
2. Only list files that exist in `assets/music/` or `assets/sfx/`; never invent a file name.
3. Reject any track whose license is unknown; write `license: unknown` as a FAIL reason.
4. Keep music under 0.2 relative gain so narration stays intelligible.
5. Place SFX at most 2 per 10 seconds to avoid clutter.

# Output format (short example)

Schema: `config/schemas/selection.json`

```json
{
  "status": "PASS",
  "skill": "music-sfx-selector",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "candidates": [
    {
      "id": "assets/music/soft-tabla.mp3",
      "score": 9,
      "reason": "owned track, calm mood, 42 seconds"
    },
    {
      "id": "assets/music/loud-drums.mp3",
      "score": 3,
      "reason": "no license note; rejected"
    },
    {
      "id": "assets/sfx/coin.mp3",
      "score": 8,
      "reason": "owned cue for the saving payoff"
    }
  ],
  "chosen_id": "assets/music/soft-tabla.mp3",
  "rationale": "Owned calm tabla bed plus one coin cue fits the 0.2 gain budget and the scene mood."
}
```

# Quality rules

1. Every candidate id is an existing local path.
2. The chosen id appears in the candidate list.
3. The rationale names the relative gain budget from the criteria.

# Steps

1. Read the scene mood from `config/style-bible.json` through project-memory.
2. List files actually present in `assets/music/` and `assets/sfx/`.
3. Score each file against mood, licence clarity and the 0.2 gain budget.
4. Cap the shortlist at one bed and three cues and pick the highest scoring bed.
5. Write the selection to `projects/<project>/05-scene/music-sfx-selector.json`.
6. Validate against `config/schemas/selection.json` and confirm every id is a local file.

# How to test

- Place one owned mp3 in `assets/music/`, run the skill, then `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/selection.json` by `tests/test_no_template.py`.

# Depends on / feeds into

scene plan -> audio-mixer

# Failure handling

If no licensed local file exists, write a WARN selection with an empty shortlist and tell the user to add an owned file. Never download or stream music in this skill.
