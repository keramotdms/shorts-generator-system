---
name: red-team
description: Challenges the video to find weaknesses.
category: final-test
status: implemented
phase: later
type: prompt-only
batch: 8
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when challenges the video to find weaknesses for a video in `projects/<project>/`.

# Purpose

Challenges the video to find weaknesses.

# Input

- `final video + final script`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `red-team findings`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `final video + final script`; if it is missing or malformed, follow Failure handling and stop.
3. Follow this skill's prompt instructions to challenges the video to find weaknesses, using only the context loaded in step 1.
4. Write the result to `red-team findings` under `projects/<project>/`; create parent folders first.
5. Re-open `red-team findings` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- Type: `Use the red-team skill with PROJECT=<project>`. Expected: `red-team findings` exists, parses cleanly, and contains no hardcoded niche or language value.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

video-editing -> bug-finder

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
