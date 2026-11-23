---
name: preview-frame-extractor
description: Extracts preview frames for review.
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

Use after the final edit and before bug-finder, when a human needs a quick visual summary instead of scrubbing the video.

# Purpose

Build one 2x3 contact sheet from a finished clip so a reviewer can judge six evenly spaced frames in a single image.

# Input

- `projects/<project>/08-final-test/final-video.mp4`
- `config/defaults.json` resolution
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `preview frames`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Contact sheet parameters

1. Sample one frame every 2 seconds with fps=1/2.
2. Scale each sampled frame to half the configured width and one third of the height.
3. Tile the samples into a 2x3 grid and emit exactly one PNG file.
4. Do not create an audio stream; the output is a still image.
5. Verify with ffprobe that the PNG width and height equal the configured resolution.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "preview-frame-extractor",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/preview-frame-extractor.png",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": false,
  "parameters": {
    "sample_fps": "1/2",
    "tile": "2x3",
    "cell": "540x640",
    "format": "png"
  },
  "summary": "Six-frame contact sheet tiled at 2x3 and probed as a 1080x1920 PNG."
}
```

# Quality rules

1. The output path ends in .png.
2. Tile dimensions multiply back to the configured resolution.
3. ffprobe reports no audio stream and exactly one image output.

# Steps

1. Load the resolution from config/defaults.json through project-memory before computing cell size.
2. Check ffmpeg availability and print BLOCKED with the setup hint if it is absent.
3. Build fps, scale and tile filters in that order for the source video.
4. Limit the command to one output frame and write a PNG under projects/<project>/07-edit/.
5. Probe the PNG and compare its dimensions to the configured resolution.
6. Write projects/<project>/07-edit/preview-frame-extractor.json and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py preview-frame-extractor --self-test` tiles generated media and checks the PNG with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

video-editing -> final-test

# Failure handling

If the source is shorter than 2 seconds, tile whatever frames exist and note the reduced sample count in the report. If ffmpeg is blocked, produce no image.
