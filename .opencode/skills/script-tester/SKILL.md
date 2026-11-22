---
name: script-tester
description: Audits and scores generated YouTube Shorts scripts (Bangla or English) for hook strength, tone, emotional feel, word count pacing, goal alignment, and visual clarity, then offers an improved rewrite if needed.
category: script
status: implemented
phase: later
type: checker
batch: 3
---


# Shorts Script Tester & QA Skill

When the user asks to test, audit, or review a script, read `scripts/latest_script.json` (or the specified script) and perform a strict quality audit across these 5 pillars:

1. **Wordage & Pacing Check (Math & Timing):**
   - Count the exact total words across all `narration` fields.
   - Calculate estimated speaking duration (Bangla average: ~110–130 words/min; English average: ~140–160 words/min).
   - Compare estimated duration with `total_duration_sec`. Flag any individual scene whose narration exceeds 15 words (too slow/dense for a 3-5 second Short scene).

2. **Hook & Scroll-Stop Power (0-3s):**
   - Evaluate if the first sentence creates immediate curiosity, tension, or relatability. Rate 1-10 and explain why it works or fails.

3. **Tone, Feels & Language Naturalness:**
   - Check if the language (`bn` or `en`) sounds natural, conversational, and spoken—not robotic, overly formal, or directly translated.
   - Verify emotional resonance (does it make the viewer feel curious, inspired, or urgent?).

4. **Goal & Audience Alignment:**
   - Check if the script stays laser-focused on a single core message/goal without wandering off-topic, and ends with a strong CTA or seamless loop.

5. **Visual & Code Readiness:**
   - Verify that every scene has a clear, renderable English `visual_prompt` and 1-2 `highlight_words` that actually exist in that scene's `narration`.

## Output Format
- Present a clean **Script Audit Scorecard** in the chat (Overall Score out of 10, Word Count vs. Target Time, Strengths, and Specific Fixes).
- If any pillar scores below 8/10, automatically provide an **Optimized Version** and ask the user: *"Should I overwrite `scripts/latest_script.json` with this improved version?"*

# When to use


Use when audits script quality across five pillars for a video in `projects/<project>/`.

# Purpose


Audits script quality across five pillars.

# Input


- `projects/<project>/02-script/latest_script.json`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Steps


1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `projects/<project>/02-script/latest_script.json`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py script-tester run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `audit report + optional optimized script` under `projects/<project>/`; create parent folders first.
5. Re-open `audit report + optional optimized script` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test


- `python scripts/skill_tools.py script-tester --self-test` → expected `PASS script-tester: ...`. Then confirm `audit report + optional optimized script` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into


script-writer -> voice stage

# Failure handling


If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
