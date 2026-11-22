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

- `script + voiceover + character references`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `projects/<project>/05-scene/collection.json`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `script + voiceover + character references`; if it is missing or malformed, follow Failure handling and stop. Validate `projects/<project>/02-script/latest_script.json` against `config/schemas/latest_script.json` with `python scripts/schema_validator.py latest_script projects/<project>/02-script/latest_script.json`.
3. Run `python scripts/skill_tools.py script-voice-character-collector run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/05-scene/collection.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/05-scene/collection.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`. Validate `projects/<project>/05-scene/collection.json` against `config/schemas/collection.json` with `python scripts/schema_validator.py collection projects/<project>/05-scene/collection.json` before accepting it.

# How to test

- `python scripts/skill_tools.py script-voice-character-collector --self-test` → expected `PASS script-voice-character-collector: ...`. Then confirm `projects/<project>/05-scene/collection.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

script, voice and character -> video-maker

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
