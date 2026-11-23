---
name: script-voice-character-collector
description: Collects script, voice and character inputs.
category: video-making
status: implemented
phase: 3
type: script-backed
batch: 6
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when collects script, voice and character inputs for a video in `projects/<project>/`.

# Purpose

Collects script, voice and character inputs.

# Input

- `projects/<project>/02-script/latest_script.json`
- `projects/<project>/03-voice/voiceover.mp3`
- `assets/characters/creator-01.json`
- `assets/scenes/scene-warm-desk-smile.png`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/05-scene/collection.json`

# Steps

1. Read context through project-memory (`config/channel.json` + `config/style-bible.json`). Validate `projects/<project>/02-script/latest_script.json` with `python scripts/schema_validator.py latest_script projects/<project>/02-script/latest_script.json`; stop on failure.
2. Confirm the three production inputs exist: `projects/<project>/03-voice/voiceover.mp3`, `projects/<project>/03-voice/captions.json` (word timings from voiceover-generator) and at least one file in `assets/characters/*.json`. Report each missing path explicitly.
3. Run `python scripts/skill_tools.py script-voice-character-collector run` with `PROJECT=<project>`. The helper builds `collection.json` with `project`, `context`, `script`, `voiceover`, `characters` and `status`; `status` is `PASS` only when the MP3 exists, otherwise `WARN`.
4. Write the result to `projects/<project>/05-scene/collection.json`; create the folder first. Do not copy any JSON into a skill folder.
5. Run `python scripts/schema_validator.py collection projects/<project>/05-scene/collection.json`, re-open the file, and log any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Acceptance criteria**
- `collection.json` passes `config/schemas/collection.json`.
- `context.niche`, `context.language` and `context.audience_location` match channel config exactly.
- `script` is the full latest script object, not a path string.
- `voiceover` is a relative path that exists, or `null` with `status: WARN`.

**Output format (short example)**
```json
{
  "project": "my-video",
  "status": "PASS",
  "context": {"niche": "Personal finance / side hustles", "language": "bn",
              "audience_location": "Bangladesh / Bangla-speaking"},
  "script": {"language": "bn", "title": "...", "scenes": []},
  "voiceover": "projects/my-video/03-voice/voiceover.mp3",
  "characters": {"creator-01": {"voice": {"gender": "male"}}}
}
```

**Quality rules**
1. Never fabricate a voiceover path — a missing MP3 must produce `WARN`, not a fake `PASS`.
2. Keep `characters` keyed by the `id` used in `assets/characters/`.
3. Do not merge in scene or video files; those belong to the later stage.

# How to test

- `python scripts/skill_tools.py script-voice-character-collector --self-test` → expected `PASS script-voice-character-collector: ...`. Then confirm `projects/<project>/05-scene/collection.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

script, voice and character -> video-maker

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
