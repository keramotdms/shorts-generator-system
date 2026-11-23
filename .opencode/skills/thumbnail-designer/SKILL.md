---
name: thumbnail-designer
description: Designs a clickable thumbnail.
category: video-editing
subcategory: automation-export
status: implemented
phase: later
type: script-backed
batch: C
schema: media-effect
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after the final edit and before description-maker, when the video needs a still image that matches its title.

# Purpose

Grab one representative frame from the finished Short and stamp the uppercase project title on it as a single PNG thumbnail.

# Input

- `projects/<project>/08-final-test/final-video.mp4`
- `projects/<project>/02-script/latest_script.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/thumbnail-designer.json`

# Thumbnail parameters

1. Select frame 75 or the last available frame for shorter clips.
2. Scale the selected frame to the configured resolution before drawing text.
3. Draw the uppercase project title at fontsize 72 with x=60 and y=120.
4. Write exactly one PNG and no audio stream.
5. Verify with ffprobe that the PNG has the configured width and height.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "thumbnail-designer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/thumbnail-designer.png",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": false,
  "parameters": {
    "frame": 74,
    "fontsize": 72,
    "text_position": [
      60,
      120
    ],
    "format": "png"
  },
  "summary": "Frame 74 of a 3-second clip scaled to 1080x1920 with the project title at the top."
}
```

# Quality rules

1. Output path ends in .png and ffprobe reports one image.
2. Frame index stays within the probed frame count of the source.
3. Title text is uppercase and taken from the PROJECT value.

# Steps

1. Read the title from the PROJECT value and the font from project-memory.
2. Require ffmpeg and print BLOCKED with the FFMPEG_PATH hint when absent.
3. Compute a safe frame index from the probed duration and fps.
4. Build select, scale and drawtext filters in that order and limit output to one frame.
5. Probe the PNG dimensions and confirm the file exists under projects/<project>/07-edit/.
6. Write projects/<project>/07-edit/thumbnail-designer.json and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py thumbnail-designer --self-test` extracts a titled PNG from generated media and checks it with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

final video -> description-maker

# Failure handling

If the source video is missing, report the exact path and stop. If no font is configured, draw no text and write a WARN about the plain thumbnail.
