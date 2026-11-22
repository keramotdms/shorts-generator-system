---
name: copyright-policy-checker
description: Checks copyright and policy risks.
category: final-test
status: implemented
phase: later
type: checker
batch: 8
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when checks copyright and policy risks for a video in `projects/<project>/`.

# Purpose

Checks copyright and policy risks.

# Input

- `final script + assets + video`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `projects/<project>/08-final-test/copyright-policy-checker.json`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `final script + assets + video`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py copyright-policy-checker run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/08-final-test/copyright-policy-checker.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/08-final-test/copyright-policy-checker.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- `python scripts/skill_tools.py copyright-policy-checker --self-test` → expected `PASS copyright-policy-checker: ...`. Then confirm `projects/<project>/08-final-test/copyright-policy-checker.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

final-test -> publish stage

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
