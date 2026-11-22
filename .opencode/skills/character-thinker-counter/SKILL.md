---
name: character-thinker-counter
description: Brainstorms and shortlists character ideas.
category: character
status: implemented
phase: later
type: prompt-only
batch: 5
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when brainstorms and shortlists character ideas for a video in `projects/<project>/`.

# Purpose

Brainstorms and shortlists character ideas.

# Input

- `style bible + final script`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `projects/<project>/04-character/character-thinker-counter.json`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `style bible + final script`; if it is missing or malformed, follow Failure handling and stop.
3. Follow this skill's prompt instructions to brainstorms and shortlists character ideas, using only the context loaded in step 1.
4. Write the result to `projects/<project>/04-character/character-thinker-counter.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/04-character/character-thinker-counter.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- Type: `Use the character-thinker-counter skill with PROJECT=<project>`. Expected: `projects/<project>/04-character/character-thinker-counter.json` exists, parses cleanly, and contains no hardcoded niche or language value.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

script and voice -> character-designer

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
