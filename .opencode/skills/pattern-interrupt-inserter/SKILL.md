---
name: pattern-interrupt-inserter
description: Inserts visual pattern interrupts.
category: video-editing
subcategory: pacing
status: implemented
phase: later
type: script-backed
batch: C
schema: media-effect
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after retention-pacing-optimizer flags a static stretch and before final-test, when a cheap attention reset is needed.

# Purpose

Flip the middle third of a clip horizontally so the viewer gets a visual jolt at the midpoint without changing the scene artwork.

# Input

- `projects/<project>/07-edit/rough-cut.mp4`
- `projects/<project>/02-script/hook.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/pattern-interrupt-inserter.json`

- Format `json_utf8`: `projects/<project>/07-edit/pattern-interrupt-inserter.json`

# Interrupt timing

1. Split the source into three contiguous segments with no frame gaps.
2. Flip only the middle segment using hflip.
3. Set the first and second split points to 0.4 and 0.8 seconds for a 1.2-second test clip, scaled by duration.
4. Concatenate the three segments back into one silent video stream.
5. Verify with ffprobe that duration is preserved within 0.1 seconds and resolution is unchanged.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "pattern-interrupt-inserter",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/pattern-interrupt-inserter.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": false,
  "parameters": {
    "segments": 3,
    "middle_filter": "hflip",
    "split_seconds": [
      0.4,
      0.8
    ],
    "audio": "dropped"
  },
  "summary": "Middle third of a 3-second clip flipped horizontally and concatenated without audio."
}
```

# Quality rules

1. Report lists exactly three segments and hflip as the middle filter.
2. Split points add up to less than the probed duration.
3. ffprobe confirms no audio stream and unchanged dimensions.

# Steps

1. Read the clip duration and configured resolution through project-memory sources.
2. Require ffmpeg and stop with BLOCKED if it is not installed at the configured path.
3. Compute the two split points from the measured duration and build a three-way split filter.
4. Apply hflip to the middle branch and concatenate all branches with setpts normalised.
5. Encode with libx264 veryfast and yuv420p, then probe the result.
6. Write projects/<project>/07-edit/pattern-interrupt-inserter.json and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py pattern-interrupt-inserter --self-test` flips the middle third of generated media and checks it with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If the clip is under 1 second, skip the flip and copy the input with a WARN. Never add an external sticker or stock clip to create the interrupt.
