---
name: video-editor
description: Applies final edits and trims.
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

Use after rough-cut-assembler and before final-test, when the scenes are correct but the first and last fractions of a second need trimming.

# Purpose

Remove a small lead-in and tail from a rough cut using matched video and audio trims so the final clip starts and ends cleanly.

# Input

- `projects/<project>/07-edit/rough-cut.mp4`
- `projects/<project>/02-script/retention-pacing-optimizer.json`
- `config/defaults.json` resolution
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `edited video`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Trim parameters

1. Trim the same number of seconds from the head and tail of both video and audio.
2. Set the trim length to 25% of the source duration, capped at 0.3 seconds.
3. Normalise timestamps with setpts and asetpts after trimming.
4. Re-encode video with libx264 veryfast and audio with AAC 128k.
5. Confirm output duration is the source duration minus twice the trim, within 0.1 seconds.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "video-editor",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/video-editor.mp4",
  "duration_sec": 2.5,
  "width": 1080,
  "height": 1920,
  "has_audio": true,
  "parameters": {
    "trim_head_sec": 0.25,
    "trim_tail_sec": 0.25,
    "video_codec": "libx264",
    "audio_codec": "aac"
  },
  "summary": "A 3-second rough cut trimmed by 0.25 seconds at each end to produce a 2.5-second final clip."
}
```

# Quality rules

1. Head and trim values in the report are equal.
2. Output duration matches the expected subtraction within tolerance.
3. ffprobe reports audio=True and configured resolution.

# Steps

1. Open the pacing notes from project-memory and probe the rough cut duration.
2. Verify ffmpeg is configured before building any trim filter.
3. Compute the capped trim length and apply it to both video and audio branches.
4. Reset both timestamp streams and map them to the output file.
5. Probe the edited clip and compare its duration to the calculated target.
6. Write projects/<project>/07-edit/video-editor.json and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py video-editor --self-test` trims generated media and verifies duration and audio with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If the source is shorter than 1 second, copy it unchanged with a WARN. If ffmpeg is unavailable, print BLOCKED and make no edit.
