---
name: beat-sync-editor
description: Syncs cuts to music beats.
category: video-editing
subcategory: audio-sync
status: implemented
phase: later
type: script-backed
batch: C
schema: media-effect
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after audio-mixer and before final-test, when a music track exists and cuts still fall on arbitrary frames.

# Purpose

Quantise scene changes to two beats per second so the visual rhythm matches a common Bengali music tempo without hand-placing every cut.

# Input

- `projects/<project>/07-edit/captioned.mp4`
- `projects/<project>/03-voice/music-sfx-selector.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/beat-sync-editor.json`

# Beat grid parameters

1. Sample the video at 2 frames per second to create a half-second beat grid.
2. Re-sample the grid to 30 fps so Shorts players accept the output.
3. Keep the audio stream as AAC at 128k and use -shortest to avoid trailing silence.
4. Scale to the configured resolution and force yuv420p for compatibility.
5. Require ffprobe to report audio present and a duration no longer than the style-bible maximum.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "beat-sync-editor",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/beat-sync-editor.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": true,
  "parameters": {
    "grid_fps": 2,
    "output_fps": 30,
    "audio_codec": "aac",
    "audio_bitrate": "128k"
  },
  "summary": "Rough cut quantised to a 2 fps beat grid, re-sampled to 30 fps with AAC audio preserved."
}
```

# Quality rules

1. The report shows audio=True after the run.
2. Output resolution equals config/defaults.json resolution.
3. Duration does not exceed the style-bible maximum length.

# Steps

1. Open the audio settings in project-memory and read the channel length cap.
2. Check ffmpeg availability and stop with BLOCKED if the executable is not configured.
3. Build a filter chain that downsamples to the beat grid then returns to 30 fps.
4. Copy the audio as AAC with a 128k bitrate and finish the command with -shortest.
5. Probe the encoded file and record resolution, duration and audio presence.
6. Write projects/<project>/07-edit/beat-sync-editor.json and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py beat-sync-editor --self-test` runs the beat-grid command on generated media and verifies audio and resolution with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

audio-mixer -> final-test

# Failure handling

If the source has no audio stream, report WARN and continue with video only. If ffmpeg is missing, print the FFMPEG_PATH hint and do not attempt a download.
