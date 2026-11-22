---
name: pipeline-health-checker
description: Checks tools, skills, handoffs and final output.
category: core
status: implemented
phase: 1
type: checker
batch: 1
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checks tools, skills, handoffs and final output for a video in `projects/<project>/`.

# Purpose

Checks tools, skills, handoffs and final output.

# Input

- `whole repository and final video`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `projects/<project>/pipeline-health-checker.json`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `whole repository and final video`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py pipeline-health-checker run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/pipeline-health-checker.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/pipeline-health-checker.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- `python scripts/skill_tools.py pipeline-health-checker --self-test` → expected `PASS pipeline-health-checker: ...`. Then confirm `projects/<project>/pipeline-health-checker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

all stages -> final render gate

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
