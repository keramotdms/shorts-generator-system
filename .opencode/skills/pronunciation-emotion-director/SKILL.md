---
name: pronunciation-emotion-director
description: Sets pronunciation and emotion for each line.
category: voice
status: implemented
phase: later
type: prompt-only
batch: 4
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when sets pronunciation and emotion for each line for a video in `projects/<project>/`.

# Purpose

Sets pronunciation and emotion for each line.

# Input

- `voice plan + final script`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `pronunciation and emotion notes`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `voice plan + final script`; if it is missing or malformed, follow Failure handling and stop.
3. Follow this skill's prompt instructions to sets pronunciation and emotion for each line, using only the context loaded in step 1.
4. Write the result to `pronunciation and emotion notes` under `projects/<project>/`; create parent folders first.
5. Re-open `pronunciation and emotion notes` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- Type: `Use the pronunciation-emotion-director skill with PROJECT=<project>`. Expected: `pronunciation and emotion notes` exists, parses cleanly, and contains no hardcoded niche or language value.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

voice plan -> voiceover-generator

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
