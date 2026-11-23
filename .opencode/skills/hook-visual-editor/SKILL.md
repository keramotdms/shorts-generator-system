---
name: hook-visual-editor
description: Enhances the opening hook visually.
category: video-editing
subcategory: pacing
status: implemented
phase: later
type: script-backed
batch: C
schema: media-effect
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after story-organizer and before final edit, when the hook script is strong but the first frames are visually flat.

# Purpose

Add a two-second opening push-in on the hook frame so the promise lands before the viewer can scroll away.

# Input

- `projects/<project>/07-edit/rough-cut.mp4`
- `projects/<project>/02-script/hook.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/hook-visual-editor.json`

# Opening push-in parameters

1. Hold a 1.10 zoom for the first 60 frames, then return to 1.0.
2. Run zoompan at 30 fps and scale every output frame to the configured resolution.
3. Keep the original audio with AAC 128k and trim with -shortest.
4. Do not alter scenes after the second 2; the command must affect the opening only.
5. Require ffprobe to confirm resolution, audio and a duration within the style-bible range.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "hook-visual-editor",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/hook-visual-editor.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": true,
  "parameters": {
    "opening_zoom": 1.1,
    "opening_frames": 60,
    "fps": 30,
    "affected_seconds": 2
  },
  "summary": "First 60 frames pushed in at 1.10 zoom, then returned to normal with audio intact."
}
```

# Quality rules

1. The report names the 60-frame opening window.
2. Resolution matches config/defaults.json exactly.
3. No criterion asks for changes after second 2.

# Steps

1. Open hook.json through project-memory and note the first promise second.
2. Check ffmpeg availability and emit BLOCKED when it cannot be found.
3. Build a zoompan expression that caps zoom at 1.10 for the first 60 frames.
4. Scale the filtered frames to the configured size and carry audio as AAC.
5. Probe the result and compare duration against the source clip.
6. Write projects/<project>/07-edit/hook-visual-editor.json and validate the media-effect schema.

# Bangla rules

1. Hook overlay text must be Bengali script in Noto Sans Bengali, not romanised words.
2. Limit the overlay to 2 lines and 32 characters so ৳ signs and Bengali numerals stay readable.
3. Check the first frame for correct Bengali glyph shaping before exporting.

# How to test

- `python scripts/skill_tools.py hook-visual-editor --self-test` runs the push-in on generated media and checks the output with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If hook.json is missing, report the path and stop. If the clip is under 2 seconds, apply the zoom for the whole clip and record a WARN in the report.
