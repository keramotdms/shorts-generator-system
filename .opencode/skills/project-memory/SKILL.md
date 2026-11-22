---
name: project-memory
description: Stores tone, colors, fonts, character look and voice choices.
category: core
status: implemented
phase: 1
type: script-backed
batch: 1
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when stores tone, colors, fonts, character look and voice choices for a video in `projects/<project>/`.

# Purpose

Stores tone, colors, fonts, character look and voice choices.

# Input

- `config/channel.json`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `config/style-bible.json`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps

1. Read `config/channel.json` directly as the source of truth; if niche, language or location is null, ask the user once and save the answer back there.
2. Validate the input at `config/channel.json`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py project-memory run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `config/style-bible.json` at the repository root (do not add a projects/<project>/ prefix); create parent folders first.
5. Re-open `config/style-bible.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- `python scripts/skill_tools.py project-memory --self-test` → expected `PASS project-memory: ...`. Then confirm `config/style-bible.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

channel config -> script, voice and character stages

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
