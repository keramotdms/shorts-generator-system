---
name: sfx-timing-placer
description: Places sound effects at exact moments.
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

Use after audio-mixer and before final-test, when music-sfx-selector has chosen a licensed local cue and it needs a precise timestamp.

# Purpose

Mix one local sound effect 1.2 seconds into a video at 0.35 volume so a payoff accent lands without drowning the narration.

# Input

- `projects/<project>/07-edit/captioned.mp4`
- `projects/<project>/03-voice/music-sfx-selector.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/sfx-timing-placer.json`

- Format `json_utf8`: `projects/<project>/07-edit/sfx-timing-placer.json`

# SFX placement parameters

1. Delay the effect by exactly 1200 milliseconds using adelay on both channels.
2. Lower the effect to 0.35 volume before mixing.
3. Mix with the original audio using amix duration=first so the video length does not change.
4. Use only a cue file listed in music-sfx-selector.json and present under assets/sfx/.
5. Verify with ffprobe that audio is present and duration matches the source within 0.1 seconds.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "sfx-timing-placer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/sfx-timing-placer.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": true,
  "parameters": {
    "delay_ms": 1200,
    "sfx_volume": 0.35,
    "mix": "amix duration=first",
    "source": "music-sfx-selector.json"
  },
  "summary": "One local cue delayed 1.2 seconds and mixed at 0.35 volume with narration intact."
}
```

# Quality rules

1. Report records a 1200 ms delay and 0.35 volume.
2. The cue path appears in the selection report before it is used.
3. ffprobe confirms audio=True and unchanged duration.

# Steps

1. Open the selected cue id from projects/<project>/05-scene/music-sfx-selector.json via project-memory.
2. Confirm ffmpeg is configured and the cue file exists locally before building the filter.
3. Apply adelay and volume to the cue stream and amix it with the source audio.
4. Map the original video stream unchanged and encode audio as AAC 128k.
5. Probe duration and audio presence on the mixed output.
6. Write projects/<project>/07-edit/sfx-timing-placer.json and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py sfx-timing-placer --self-test` mixes a generated cue at 1.2 seconds and verifies audio with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

audio-mixer -> final-test

# Failure handling

If no cue was selected, skip mixing, copy the input and write a WARN. Never download a sound effect or use an unlicensed file.
