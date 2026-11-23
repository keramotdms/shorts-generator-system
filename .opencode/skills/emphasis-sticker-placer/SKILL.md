---
name: emphasis-sticker-placer
description: Places emphasis stickers and highlights.
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

Use after caption-maker and before final-test, when a number in the hook needs a visual accent but no new artwork is available.

# Purpose

Flash a translucent palette-coloured highlight behind the first key line of a Short so the money figure reads at a glance.

# Input

- `projects/<project>/07-edit/captioned.mp4`
- `config/style-bible.json` palette
- `config/defaults.json` resolution
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `video with emphasis graphics`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Highlight placement

1. Set the highlight x to 8% of width and y to 12% of height.
2. Make the box 84% of width and 12% of height so captions below stay readable.
3. Use the third palette colour at 0.35 alpha and fill the box.
4. Enable the box only for the first 1.2 seconds or half the clip, whichever is shorter.
5. Verify the output keeps the source resolution and audio with ffprobe.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "emphasis-sticker-placer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/emphasis-sticker-placer.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": true,
  "parameters": {
    "x_pct": 8,
    "y_pct": 12,
    "box_pct": "84x12",
    "alpha": 0.35,
    "window_sec": 1.2
  },
  "summary": "Palette highlight shown for 1.2 seconds behind the hook text on a 3-second clip."
}
```

# Quality rules

1. Report parameters include the 0.35 alpha value.
2. The enable window is at most half the probed duration.
3. ffprobe reports unchanged dimensions and audio present.

# Steps

1. Read palette and resolution from project-memory, then probe the captioned video.
2. Require ffmpeg and print BLOCKED if the configured executable is absent.
3. Compute the box geometry from the probed frame size rather than fixed pixels.
4. Build the drawbox filter with an enable expression limited to the hook window.
5. Encode with libx264 and AAC, then verify the output stream with ffprobe.
6. Save the measured report to projects/<project>/07-edit/emphasis-sticker-placer.json.

# How to test

- `python scripts/skill_tools.py emphasis-sticker-placer --self-test` draws the highlight on generated media and verifies it with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

caption-maker -> final-test

# Failure handling

If the source is shorter than 0.4 seconds, skip the highlight and copy the input with a WARN. Never use a sticker image that is not already in assets/.
