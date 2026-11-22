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

1. Read niche, language, location, video length and style through project-memory (`config/channel.json` + `config/style-bible.json`); never hardcode them.
2. Validate `projects/<project>/02-script/story.json`, `projects/<project>/02-script/hook.json` and `config/channel.json`; stop if any is missing or malformed.
3. Write `title`, `hook`, `narration` and `highlight_words` in the project language; keep `visual_prompt` in clear English for renderers.
4. Apply the original real rules: hook at 0-3 s, fast body at 3-45 s with 8-12-word sentences, strong CTA/loop in the last 3-5 s.
5. Save `projects/<project>/02-script/latest_script.json` with `language`, `title`, `hook`, `total_duration_sec` (30-60) and `scenes[].scene_number/narration/visual_prompt/highlight_words`.
6. Re-open the JSON, confirm it parses and every scene has a renderable visual prompt; validate it with `python scripts/schema_validator.py latest_script projects/<project>/02-script/latest_script.json` before accepting it, then show a readable summary in chat and log problems to `projects/<project>/08-final-test/error-log.jsonl`.

# How to test

- Prompt: `Use the script-writer skill with PROJECT=<project>` after story and hook exist.
- Checklist: expected `projects/<project>/02-script/latest_script.json` exists, parses, has 30-60 s total, every scene has 1-2 `highlight_words` present in its narration, and no niche/language value is hardcoded.

# Depends on / feeds into


story and hook -> voice stage

# Failure handling


If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
