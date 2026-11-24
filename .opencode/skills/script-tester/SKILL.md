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

When the user asks to test, audit, or review a script, read `projects/<project>/02-script/latest_script.json` (or the specified script) and perform a strict quality audit across these 5 pillars:

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
- If any pillar scores below 8/10, automatically provide an **Optimized Version** and ask the user: *"Should I overwrite `projects/<project>/02-script/latest_script.json` with this improved version?"*

# When to use


Use when audits script quality across five pillars for a video in `projects/<project>/`.

# Purpose


Audits script quality across five pillars.

# Input


- `projects/<project>/02-script/latest_script.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/02-script/script-tester.json`

- Format `json_utf8`: `projects/<project>/02-script/script-tester.json`

# Steps

1. Read language and style through project-memory (`config/channel.json` + `config/style-bible.json`); use that language for all pacing estimates.
2. Load `projects/<project>/02-script/latest_script.json`; stop if it is missing or malformed. Validate it first with `python scripts/schema_validator.py latest_script projects/<project>/02-script/latest_script.json`.
3. Count words in every `narration`, estimate speaking time from the project language (Bangla ~110-130 wpm, English ~140-160 wpm), compare with `total_duration_sec`, and flag scenes over 15 words.
4. Score hook power, tone/naturalness, goal alignment and visual readiness on 1-10 with a short reason for each, keeping the original 5-pillar rubric above.
5. Write the scorecard to `projects/<project>/02-script/script-tester.json`; if any pillar scores below 8, also write an improved script to `projects/<project>/02-script/latest_script.optimized.json`.
6. Validate both JSON outputs and log any problem to `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- `python scripts/skill_tools.py script-tester --self-test` → expected `PASS script-tester: helper imports and contract verified`.
- Checklist: feed the fixture script; expect 5 pillar scores in the report; if any score is below 8, the optimized script file exists and parses.

# Depends on / feeds into


script-writer -> voice stage

# Failure handling


If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
