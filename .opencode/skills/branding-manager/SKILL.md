---
name: branding-manager
description: Applies channel branding consistently.
category: video-editing
subcategory: core
status: implemented
phase: later
type: script-backed
batch: C
schema: media-effect
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after video-editor and before final-test, when the edit is locked and only the channel signature is missing.

# Purpose

Stamp a palette-coloured channel bar and the project label onto every edited clip so the brand looks identical across all Shorts.

# Input

- `projects/<project>/07-edit/rough-cut.mp4`
- `config/style-bible.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/branding-manager.json`

# Brand placement parameters

1. Draw the brand bar at 7% of the configured height and span the full input width.
2. Take the bar colour from the third palette entry converted to 0xRRGGBB for FFmpeg.
3. Print the uppercase project name at fontsize 48 using the style-bible font file.
4. Keep the caption area clear by placing text above the bar, not over the centre frame.
5. Verify with ffprobe that resolution and duration are unchanged and audio survives.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "branding-manager",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/branding-manager.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": true,
  "parameters": {
    "bar_height": "7% of height",
    "bar_color": "palette[2] as 0xRRGGBB",
    "fontsize": 48,
    "label": "_TEMPLATE"
  },
  "summary": "Channel bar and label drawn from the style bible on a 3-second clip, verified by ffprobe."
}
```

# Quality rules

1. The bar height equals seven percent of the probed height.
2. The colour string starts with 0x, not #.
3. ffprobe confirms audio=True and unchanged dimensions.

# Steps

1. Read palette, font and project name through project-memory before building the filter.
2. Confirm ffmpeg is available and otherwise print BLOCKED with the setup hint.
3. Convert the CSS palette colour into FFmpeg's 0x notation and compute the bar height.
4. Chain drawbox and drawtext with ih/ih expressions so the bar follows the real frame size.
5. Encode with libx264 and AAC, then probe the branded output.
6. Save the report to projects/<project>/07-edit/branding-manager.json and validate its schema.

# How to test

- `python scripts/skill_tools.py branding-manager --self-test` draws the bar and label on generated media and verifies them with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If the style bible has fewer than three palette colours, fall back to the default amber with a WARN. If the font file is missing, draw only the bar and record the omission in the report.
