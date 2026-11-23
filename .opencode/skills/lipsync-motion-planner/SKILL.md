---
name: lipsync-motion-planner
description: Plans simple mouth and body motion from word timings.
category: video-making
status: implemented
phase: later
type: prompt-only
batch: A
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after the collector and before video-maker, when a static character needs timed mouth opening and one simple body move per scene.

# Purpose

Turn caption word timings into a minimal lip-sync and motion plan that the flat SVG character can actually perform.

# Input

- `projects/<project>/03-voice/captions.json`
- `assets/characters/creator-01/character.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/06-video/lipsync-motion-planner.json`

# Motion constraints

1. Allow only two mouth states: open and closed; no phoneme-level shapes.
2. Open the mouth only during a word interval from captions.json; never between words.
3. Allow one body motion per scene from idle, wave, point or think.
4. Keep motion events at least 1.5 seconds apart to stay readable at 9:16.
5. Use the pose names from expression-pose-library exactly as written.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "lipsync-motion-planner",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Mouth open onেকশ in scene 1",
      "start_sec": 0.4,
      "end_sec": 0.9,
      "reason": "word interval from captions"
    },
    {
      "id": 2,
      "action": "Pose wave during the greeting scene",
      "start_sec": 2.0,
      "end_sec": 5.0,
      "reason": "one body motion per scene"
    },
    {
      "id": 3,
      "action": "Mouth open on the saving line",
      "start_sec": 36.0,
      "end_sec": 37.2,
      "reason": "final payoff word"
    }
  ],
  "constraints": [
    "mouth states open/closed only",
    "poses idle/wave/point/think",
    "1.5 seconds between motions"
  ],
  "summary": "Three timed cues derived from caption intervals and the supported pose list."
}
```

# Quality rules

1. Every cue start and end matches a caption interval in the source file.
2. No unsupported pose name appears in any action.
3. Body motions are at least 1.5 seconds apart.

# Steps

1. Load language from project-memory and validate `projects/<project>/03-voice/captions.json`.
2. Read the collection file to learn which character and scenes exist.
3. Map caption word intervals to open-mouth windows, one per word.
4. Choose one supported pose per scene and space body motions by at least 1.5 seconds.
5. Write the plan to `projects/<project>/06-video/lipsync-motion-planner.json`.
6. Validate against `config/schemas/plan.json` and cross-check every interval with captions.

# How to test

- Validate `projects/_template/06-video/lipsync-motion-planner.json` with the plan schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

collector -> video-maker

# Failure handling

If captions are missing or word timings are absent, report BLOCKED for motion planning and render the character in idle pose instead of guessing mouth movement.
