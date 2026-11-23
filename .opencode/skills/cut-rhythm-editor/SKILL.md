---
name: cut-rhythm-editor
description: Re-times rough cuts for tighter rhythm.
category: video-editing
subcategory: pacing
status: implemented
phase: later
type: script-backed
batch: A
schema: media-effect
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after rough-cut-assembler when the timeline is too slow but the scene order is correct.

# Purpose

Shorten a rough cut by trimming two halves of the source video and concatenating them, producing a tighter edit without re-encoding the whole scene set.

# Input

- - `projects/<project>/07-edit/rough-cut.mp4`
- - `config/defaults.json` resolution and `config/style-bible.json` video length
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `re-paced video`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Rhythm parameters

1. Read output width and height from `config/defaults.json` resolution, not from a hardcoded string.
2. Trim the source at its measured midpoint, keeping the first 45% and the segment starting at 50%.
3. Target an output duration of about 90% of the input duration.
4. Re-encode with libx264 preset veryfast and pixel format yuv420p for Shorts compatibility.
5. Verify the result with ffprobe and require duration between 1 and 60 seconds.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "cut-rhythm-editor",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/cut-rhythm-editor.mp4",
  "duration_sec": 40.5,
  "width": 1080,
  "height": 1920,
  "has_audio": false,
  "parameters": {
    "trim_a": "0-20.25",
    "trim_b": "22.5-42.75",
    "target_ratio": 0.9,
    "video_codec": "libx264"
  },
  "summary": "Rough cut re-timed from 45 to 40.5 seconds using two trims and a concat filter."
}
```

# Quality rules

1. Output duration is between 85% and 95% of input duration.
2. ffprobe confirms the resolution from defaults.json.
3. No audio is silently dropped without being recorded in the report.

# Steps

1. Load resolution from `config/defaults.json` and length limits from `config/style-bible.json` via project-memory.
2. Require ffmpeg with `FFMPEG_PATH`; print BLOCKED and exit 0 if it is unavailable.
3. Probe `projects/<project>/07-edit/rough-cut.mp4` for its exact duration.
4. Build a two-trim concat filter using 45% and 50% offsets of that duration.
5. Run the ffmpeg command and verify the result with ffprobe.
6. Write the report to `projects/<project>/07-edit/cut-rhythm-editor.json` and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py cut-rhythm-editor --self-test` generates a tiny video, runs the trim-concat command and checks duration with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If ffprobe reports a duration shorter than 2 seconds, skip the trims and copy the source with a WARN. On ffmpeg BLOCKED, report the FFMPEG_PATH hint and do not change Windows settings.
