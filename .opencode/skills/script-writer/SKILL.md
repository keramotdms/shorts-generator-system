---
name: script-writer
description: Generates viral, high-retention 30-60 second YouTube Shorts scripts in Bangla or English with scene-by-scene visual prompts and timing metadata saved as JSON.
category: script
status: implemented
phase: 2
type: prompt-only
batch: 3
---


# Shorts Script Writer Skill

When the user asks to write a script for a Short, follow these exact steps:

1. **Language & Tone:** Write the `title`, `hook`, `narration`, and `highlight_words` in the language requested by the user (Bangla or English; default to natural, conversational Bangla if unspecified). Keep `visual_prompt` in clear English so code and rendering tools can easily parse it.
2. **Hook First (0-3 seconds):** Start with a pattern-interrupt hook, shocking fact, or bold question that stops viewers from scrolling.
3. **Fast-Paced Body (3-45 seconds):** Keep sentences short (max 8-12 words per sentence), conversational, and value-packed. Remove all fluff.
4. **Strong CTA / Loop (Last 3-5 seconds):** End with a seamless loop back to the first sentence or a clear call-to-action.
5. **Structured Output:** 
   - Create a `scripts/` folder if it doesn't exist.
   - Save the output as `scripts/latest_script.json` with this exact structure:
     - `language`: `"bn"` or `"en"`
     - `title`: Catchy title
     - `hook`: The opening 3-second line
     - `total_duration_sec`: Target duration (30 to 60)
     - `scenes`: An array of objects, each containing:
       - `scene_number`: Integer
       - `narration`: Exact spoken text for this scene (3-5 seconds long)
       - `visual_prompt`: Detailed English description of what should appear on screen (motion graphics, text overlay, or background visual)
       - `highlight_words`: 1-2 key words from the narration to highlight in bold/color on screen
   - Also display a clean, readable summary of the script in the chat for the user to review.

# When to use


Use when writes the full script with scenes and timings for a video in `projects/<project>/`.

# Purpose


Writes the full script with scenes and timings.

# Input


- `story.json + hook.json + config/channel.json`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output


- `projects/<project>/02-script/latest_script.json`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps


1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `story.json + hook.json + config/channel.json`; if it is missing or malformed, follow Failure handling and stop.
3. Follow this skill's prompt instructions to writes the full script with scenes and timings, using only the context loaded in step 1.
4. Write the result to `projects/<project>/02-script/latest_script.json` under `projects/<project>/`; create parent folders first.
5. Re-open `projects/<project>/02-script/latest_script.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

# How to test


- Type: `Use the script-writer skill with PROJECT=<project>`. Expected: `projects/<project>/02-script/latest_script.json` exists, parses cleanly, and contains no hardcoded niche or language value.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into


story and hook -> voice stage

# Failure handling


If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
