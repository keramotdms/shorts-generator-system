---
name: color-grading-keeper
description: Keeps color style consistent.
category: video-editing
subcategory: visual
status: implemented
phase: later
type: script-backed
batch: C
schema: media-effect
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after scene rendering and before final-test, when scenes were rendered at different times and colours have drifted.

# Purpose

Apply one repeatable eq curve derived from the palette length so every scene keeps the same contrast and saturation as the style bible.

# Input

- `projects/<project>/07-edit/rough-cut.mp4`
- `config/style-bible.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/color-grading-keeper.json`

- Format `json_utf8`: `projects/<project>/07-edit/color-grading-keeper.json`

# Grade parameters

1. Set contrast to 1 plus 0.01 times the number of palette colours.
2. Hold saturation at 1.03 and brightness at 0.01 for every clip.
3. Never apply per-scene creative grades; the grade must be byte-identical across videos.
4. Use libx264 veryfast with yuv420p and keep AAC audio unchanged.
5. Check with ffprobe that duration and resolution match the source within 0.1 seconds.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "color-grading-keeper",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/color-grading-keeper.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": true,
  "parameters": {
    "contrast": 1.04,
    "saturation": 1.03,
    "brightness": 0.01,
    "palette_count": 4
  },
  "summary": "Single palette-derived eq curve applied to a 3-second clip with audio preserved."
}
```

# Quality rules

1. Contrast in the report equals 1 plus 0.01 times the palette count.
2. Saturation and brightness are the fixed values 1.03 and 0.01.
3. ffprobe duration differs from the input by at most 0.1 seconds.

# Steps

1. Fetch the palette from project-memory and count its entries.
2. Verify ffmpeg is installed at the configured path before touching any media.
3. Derive the contrast value from the palette count and build the eq filter.
4. Encode the graded clip and keep the original audio stream as AAC.
5. Compare probed duration and resolution against the source values.
6. Write projects/<project>/07-edit/color-grading-keeper.json and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py color-grading-keeper --self-test` grades generated media and checks resolution, duration and audio with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If ffmpeg is blocked, return BLOCKED with the FFMPEG_PATH hint. If the palette is empty, use four as the count and write a WARN about the fallback.
