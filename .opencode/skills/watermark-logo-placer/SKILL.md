---
name: watermark-logo-placer
description: Places the channel watermark or logo.
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

Use after branding-manager and before handover, when a logo file exists and must appear consistently on all outputs.

# Purpose

Overlay a small local logo in the top-right corner of every edited clip so the channel is visible without covering captions or the hook object.

# Input

- `projects/<project>/07-edit/captioned.mp4`
- `config/style-bible.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/watermark-logo-placer.json`

- Format `json_utf8`: `projects/<project>/07-edit/watermark-logo-placer.json`

# Watermark parameters

1. Scale the logo to exactly 120 by 120 pixels.
2. Place it at x = width minus 150 and y = 40 to keep clear of the caption band.
3. Use the overlay filter with format=auto so transparent PNGs composite correctly.
4. Keep the source audio when present and encode it as AAC 128k.
5. Verify with ffprobe that resolution and duration are unchanged and audio survives when the source had it.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "watermark-logo-placer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/watermark-logo-placer.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": true,
  "parameters": {
    "logo_size": "120x120",
    "overlay": "x=w-150:y=40",
    "format": "auto",
    "source": "local PNG"
  },
  "summary": "Local logo scaled to 120px and overlaid in the top-right corner with audio preserved."
}
```

# Quality rules

1. Overlay expression uses w-150 and y=40.
2. Logo path is local and ends in .png.
3. ffprobe confirms configured resolution and unchanged duration.

# Steps

1. Read the resolution from config/defaults.json through project-memory and locate a local logo PNG.
2. Confirm ffmpeg is available or return BLOCKED with the FFMPEG_PATH hint.
3. Scale the logo input to 120x120 and overlay it using width-relative coordinates.
4. Map the original audio when available and encode with libx264 plus AAC.
5. Probe the watermarked file and compare it with the source metadata.
6. Write projects/<project>/07-edit/watermark-logo-placer.json and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py watermark-logo-placer --self-test` overlays a generated logo and verifies the output with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If no local logo exists, use the first scene PNG as a temporary mark and write a WARN with its path. Never download a channel logo.
