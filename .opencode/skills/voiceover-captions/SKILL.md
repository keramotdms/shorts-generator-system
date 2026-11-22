---
name: voiceover-captions
description: Generates natural Bangla or English voiceover audio (MP3) and exact word/phrase-level caption timestamps (JSON) from scripts/latest_script.json using free edge-tts.
category: voice
status: legacy
phase: later
note: legacy; will later be split into voiceover-generator and caption-maker
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

1. Read language and voice style through project-memory (`config/channel.json` + `config/style-bible.json`); this skill is kept only for compatibility.
2. Validate `projects/<project>/02-script/latest_script.json`; stop if it is missing or malformed.
3. Keep the original behaviour: ensure `edge-tts` is available, then run `python scripts/generate_audio.py` with the gender requested by the user.
4. Verify `output/voiceover.mp3` and `output/captions.json` were created and report exact audio duration in seconds.
5. Tell the user to use `voiceover-generator` + `caption-maker` for new projects; do not duplicate their logic here.

# How to test

- Prompt: `Use the voiceover-captions skill with PROJECT=<project>` on a legacy project only.
- Checklist: both legacy output files exist, `captions.json` parses, duration is reported, and the reply points to the two replacement skills.

# Depends on / feeds into


script -> legacy split targets

# Failure handling


If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
