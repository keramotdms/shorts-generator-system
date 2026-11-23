---
name: seamless-loop-editor
description: Makes the ending loop smoothly.
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

Use after loop-cta-designer and before final-test, when a Short must replay without a visible cut at the seam.

# Purpose

Reverse the final 0.4 seconds of a clip and append it so the last frame walks back into the preceding motion instead of jumping on replay.

# Input

- `projects/<project>/07-edit/rough-cut.mp4`
- `projects/<project>/02-script/loop-cta-designer.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/seamless-loop-editor.json`

# Loop seam parameters

1. Take a tail of at most 0.4 seconds, or half the clip if it is shorter.
2. Reverse only that tail with the reverse filter, never the whole video.
3. Concatenate the kept head and the reversed tail into one silent video stream.
4. Keep the total duration equal to the source duration within 0.1 seconds.
5. Probe the result with ffprobe for unchanged resolution and no audio stream.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "seamless-loop-editor",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/seamless-loop-editor.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": false,
  "parameters": {
    "tail_sec": 0.4,
    "tail_filter": "reverse",
    "segments": 2,
    "audio": "dropped"
  },
  "summary": "Last 0.4 seconds reversed and re-appended to make a 3-second clip loop without a hard cut."
}
```

# Quality rules

1. Tail length never exceeds 0.4 seconds or half the source duration.
2. Concatenation uses exactly two segments.
3. ffprobe confirms unchanged frame size and no audio.

# Steps

1. Read the loop window from project-memory sources and probe the source duration.
2. Verify ffmpeg is available or return BLOCKED with the FFMPEG_PATH hint.
3. Compute the split point by subtracting the capped tail from the measured duration.
4. Build two trim branches, apply reverse to the tail branch and join them.
5. Encode with libx264 veryfast and probe the loop-ready file.
6. Write projects/<project>/07-edit/seamless-loop-editor.json and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py seamless-loop-editor --self-test` reverses the tail of generated media and verifies the loop with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

rough-cut-assembler -> final-test

# Failure handling

If the clip is under 0.5 seconds, copy the input and write a WARN because no useful tail exists. If ffmpeg is unavailable, print BLOCKED only.
