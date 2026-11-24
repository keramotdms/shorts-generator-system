---
name: motion-graphic-editor
description: Creates motion graphics overlays.
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

Use after branding-manager and before final-test, when a short on-screen label should move rather than sit still.

# Purpose

Slide the project label across the upper third of a clip using a time-based drawtext expression, giving a cheap motion graphic without a compositing app.

# Input

- `projects/<project>/07-edit/rough-cut.mp4`
- `config/style-bible.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/motion-graphic-editor.json`

- Format `json_utf8`: `projects/<project>/07-edit/motion-graphic-editor.json`

# Moving text parameters

1. Use drawtext with x driven by (main_w-text_w)*t/3 so the label crosses in 3 seconds.
2. Place the label at y=300 to stay above the caption band.
3. Set fontsize 64 and take the font colour from the third palette entry.
4. Enable the overlay only during the first 3 seconds of the clip.
5. Check ffprobe for unchanged resolution, audio presence and valid duration.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "motion-graphic-editor",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/motion-graphic-editor.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": true,
  "parameters": {
    "fontsize": 64,
    "x_expression": "(main_w-text_w)*t/3",
    "y": 300,
    "window_sec": 3
  },
  "summary": "Project label slides across the upper third for 3 seconds with audio preserved."
}
```

# Quality rules

1. The x expression contains main_w and a time term.
2. Font colour comes from the palette rather than a hardcoded hex string.
3. ffprobe confirms the output retains audio and configured dimensions.

# Steps

1. Load the font file and palette through project-memory and read the project label.
2. Verify ffmpeg is available before constructing the drawtext filter.
3. Escape the label text and escape the filter commas in the enable expression.
4. Build the time-based x expression and encode with libx264 plus AAC.
5. Probe duration, frame size and audio, then record the measurements.
6. Write projects/<project>/07-edit/motion-graphic-editor.json and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py motion-graphic-editor --self-test` slides a label on generated media and verifies the output with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If no font file is configured, omit drawtext, copy the video and write a WARN. If ffmpeg is blocked, return BLOCKED without editing any file.
