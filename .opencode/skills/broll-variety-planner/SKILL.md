---
name: broll-variety-planner
description: Adds a flat B-roll overlay to a rough cut.
category: video-editing
subcategory: visual
status: implemented
phase: later
type: script-backed
batch: A
schema: media-effect
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after the scene plan and before final edit, when a scene stays visually static for more than 5 seconds.

# Purpose

Place one local flat-shape image over a short window of the rough cut so a talking-head scene gains visual variety without stock footage.

# Input

- - `projects/<project>/07-edit/rough-cut.mp4`
- - `assets/scenes/*.png` local flat images
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `B-roll plan`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# B-roll rules

1. Use only images already present under assets/scenes/; never fetch stock footage.
2. Scale the overlay to 270x480, which is one quarter of the 1080x1920 frame.
3. Show the overlay for at most 40% of the video length.
4. Position it at x=w-300 and y=120 so captions at the bottom stay clear.
5. Verify with ffprobe that the output keeps the input resolution and duration.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "broll-variety-planner",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/broll-variety-planner.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": true,
  "parameters": {
    "overlay": "assets/scenes/warm-desk-background.png",
    "scale": "270x480",
    "position": "w-300:120",
    "window_sec": 1.2
  },
  "summary": "One local flat image overlaid for 1.2 seconds on a 3 second test clip."
}
```

# Quality rules

1. The overlay path is a local PNG under assets/scenes/.
2. Window length is 40% or less of the probed duration.
3. ffprobe shows the same width and height as the input.

# Steps

1. Read palette and resolution from project-memory sources `config/style-bible.json` and `config/defaults.json`.
2. Require ffmpeg and stop with BLOCKED if `FFMPEG_PATH` is unavailable.
3. Pick the first local PNG in `assets/scenes/` and probe the rough cut duration.
4. Build an overlay filter that scales the image to 270x480 and enables it for 40% of the duration.
5. Run ffmpeg with libx264 veryfast and keep the audio stream.
6. Write the ffprobe summary to `projects/<project>/07-edit/broll-variety-planner.json`.

# How to test

- `python scripts/skill_tools.py broll-variety-planner --self-test` uses a generated PNG, runs the overlay command and probes width, height and duration.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

video-making -> video-editor

# Failure handling

If no local PNG exists, report WARN and copy the input unchanged rather than downloading an image. On ffmpeg BLOCKED, print the FFMPEG_PATH hint only.
