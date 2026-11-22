---
name: voiceover-captions
description: Generates natural Bangla or English voiceover audio (MP3) and exact word/phrase-level caption timestamps (JSON) from scripts/latest_script.json using free edge-tts.
category: voice
status: legacy
phase: later
note: legacy pointer to voiceover-generator and caption-maker
type: prompt-only
batch: 4
---


# Shorts Voiceover & Captions Skill

When the user asks to generate voiceover or captions from the script:
1. Ensure the Python package `edge-tts` is installed (run `pip install edge-tts` if missing).
2. Run `python scripts/generate_audio.py` (pass `--gender female` if the user requests a female voice; default is male).
3. Verify that both `output/voiceover.mp3` and `output/captions.json` are generated successfully and report the exact total audio duration in seconds.

# When to use


Use when legacy combined voiceover and caption generator for a video in `projects/<project>/`.

# Purpose


Legacy combined voiceover and caption generator.

# Input


- `projects/<project>/02-script/latest_script.json`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output


- `output/voiceover.mp3 + output/captions.json`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps


1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `projects/<project>/02-script/latest_script.json`; if it is missing or malformed, follow Failure handling and stop.
3. Follow this skill's prompt instructions to legacy combined voiceover and caption generator, using only the context loaded in step 1.
4. Write the result to `output/voiceover.mp3 + output/captions.json` under `projects/<project>/`; create parent folders first.
5. Re-open `output/voiceover.mp3 + output/captions.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test


- Type: `Use the voiceover-captions skill with PROJECT=<project>`. Expected: `output/voiceover.mp3 + output/captions.json` exists, parses cleanly, and contains no hardcoded niche or language value.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into


script -> legacy split targets

# Failure handling


If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
