---
name: animator
description: Adds motion and animation to elements.
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

Use after rough-cut-assembler when a static scene needs motion and no new artwork is available.

# Purpose

Turn one flat scene PNG into a short animated clip with a gentle zoompan so a still prop feels alive without needing frame-by-frame art.

# Input

- `projects/<project>/07-edit/rough-cut.mp4`
- `projects/<project>/05-scene/element-organizer.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/animator.json`

# Animation parameters

1. Read width and height from config/defaults.json resolution; never type 1080x1920 by hand.
2. Use zoompan at 30 fps for 75 frames, which is 2.5 seconds of motion.
3. Cap the zoom at 1 plus 0.01 times the palette length, so a four-colour bible zooms to 1.04.
4. Force yuv420p output and drop audio because the source is a still image.
5. Verify with ffprobe that the clip has the configured resolution and a duration of 2.4–2.6 seconds.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "animator",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/animator.mp4",
  "duration_sec": 2.5,
  "width": 1080,
  "height": 1920,
  "has_audio": false,
  "parameters": {
    "zoompan_frames": 75,
    "fps": 30,
    "max_zoom": 1.04,
    "color_source": "config/style-bible.json"
  },
  "summary": "One flat PNG animated with a 2.5-second zoompan capped at the palette-derived zoom value."
}
```

# Quality rules

1. ffprobe reports the exact resolution stored in config/defaults.json.
2. Output duration stays between 2.4 and 2.6 seconds.
3. The report records the palette as the zoom source, not a literal zoom number.

# Steps

1. Load the resolution and palette through project-memory before choosing the input PNG.
2. Require ffmpeg and print BLOCKED with the FFMPEG_PATH hint when it is missing.
3. Build the zoompan filter from the palette length and the configured frame count.
4. Encode the still image with libx264 veryfast and yuv420p, then probe the result.
5. Write the measured effect report to projects/<project>/07-edit/animator.json.
6. Validate the media-effect schema and confirm the clip has no audio stream.

# How to test

- `python scripts/skill_tools.py animator --self-test` generates a tiny PNG, runs the zoompan command and checks resolution and duration with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If ffmpeg is unavailable, print BLOCKED and exit without changing Windows settings. If the PNG is missing, fall back to the generated media fixture and note the substitution in the report.
