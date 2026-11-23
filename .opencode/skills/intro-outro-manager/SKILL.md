---
name: intro-outro-manager
description: Adds intro and outro cards.
category: video-editing
subcategory: text-graphics
status: implemented
phase: later
type: script-backed
batch: C
schema: media-effect
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after rough-cut-assembler and before final-test, when a series needs a consistent opening card but the scene itself must not be re-rendered.

# Purpose

Prepend a one-second palette-coloured title card to a locked clip without touching narration or captions in the body.

# Input

- `projects/<project>/07-edit/captioned.mp4`
- `config/style-bible.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/intro-outro-manager.json`

# Card parameters

1. Generate a solid colour card at 30 fps for exactly 1 second.
2. Use the second palette colour converted to 0xRRGGBB as the card background.
3. Concatenate the card before the source video and keep the source frame size.
4. Output has no audio because the card precedes narration and the source clip may be silent.
5. Verify the final duration is the source duration plus 1 second within 0.1 seconds.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "intro-outro-manager",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/intro-outro-manager.mp4",
  "duration_sec": 4.0,
  "width": 1080,
  "height": 1920,
  "has_audio": false,
  "parameters": {
    "card_seconds": 1,
    "card_fps": 30,
    "background": "palette[1] as 0xRRGGBB",
    "position": "before"
  },
  "summary": "One-second colour card prepended to a 3-second clip, producing a 4-second silent output."
}
```

# Quality rules

1. Output duration equals source duration plus 1 second within tolerance.
2. Report background colour starts with 0x.
3. ffprobe shows no audio stream on the output.

# Steps

1. Read palette and frame size from project-memory before building the synthetic input.
2. Confirm ffmpeg is configured or return BLOCKED with the FFMPEG_PATH hint.
3. Create the solid colour source with lavfi at the configured resolution and 30 fps.
4. Concatenate the card and the video, then drop audio from the mapped stream.
5. Probe the concatenated file and check the one-second duration increase.
6. Write projects/<project>/07-edit/intro-outro-manager.json and validate its schema.

# Bangla rules

1. Intro and outro cards must use Bengali script with Noto Sans Bengali.
2. Keep each card to 2 lines and 32 characters; leave ৳ amounts and Bengali numerals unbroken.
3. Check the rendered PNG for missing glyphs before adding it to the cut.

# How to test

- `python scripts/skill_tools.py intro-outro-manager --self-test` prepends a card to generated media and verifies duration with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If the source is longer than the style-bible maximum after adding the card, return WARN with the overshoot and keep the original clip unchanged.
