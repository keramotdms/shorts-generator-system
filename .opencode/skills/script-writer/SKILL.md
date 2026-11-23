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
   - Create `projects/<project>/02-script/` if it doesn't exist.
   - Save the output as `projects/<project>/02-script/latest_script.json` with this exact structure:
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


- `projects/<project>/02-script/story.json`
- `projects/<project>/02-script/hook.json`
- `config/channel.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output


- `projects/<project>/02-script/latest_script.json`

# Steps

1. Read `config/channel.json` and `config/style-bible.json` through project-memory for language, video length and tone. Read `projects/<project>/02-script/story.json` and `projects/<project>/02-script/hook.json`; stop if either is missing or malformed.
2. Copy the exact field `hook.json.text` into `latest_script.json.hook` unchanged; never rename it through prose alone. Write `title`, `narration` and `highlight_words` in the project language; keep every `visual_prompt` in plain English so renderers can parse it.
3. Apply the real pacing rules: hook at 0-3 s, fast body from 3-45 s with sentences of 8-12 words, and a CTA or loop back to the hook in the last 3-5 s. Use the 3 story beats as scenes 1-3.
4. Save `projects/<project>/02-script/latest_script.json` with `language`, `title`, `hook`, `total_duration_sec` (30-60) and `scenes[].scene_number/narration/visual_prompt/highlight_words`. Give each scene a `duration_sec` whose sum is within 2 seconds of the total.
5. Run `python scripts/schema_validator.py latest_script projects/<project>/02-script/latest_script.json`; re-open the file and confirm each `highlight_words` entry appears in its scene narration.
6. Show a short summary in chat (title, duration, scene count). Log any problem to `projects/<project>/08-final-test/error-log.jsonl` and re-run after fixing the input.

**Acceptance criteria**
- `latest_script.json` passes `config/schemas/latest_script.json`.
- `total_duration_sec` is between 30 and 60; scene durations sum within 2 seconds.
- 3 or more scenes, each with an English `visual_prompt` and 1-2 `highlight_words` present in its narration.
- Hook text equals the approved `hook.json` text.

**Output format (short example)**
```json
{
  "language": "bn",
  "title": "টাকা ছাড়াই সাইড হাসল",
  "hook": "আপনার পকেটে টাকা না থাকলেও শুরু করা যায়",
  "total_duration_sec": 40,
  "scenes": [
    {
      "scene_number": 1,
      "narration": "অনেকের মনে হয় পুঁজি না থাকলে কিছু করা যাবে না।",
      "visual_prompt": "Flat 2D illustration of a worried person looking at an empty wallet, bold shapes",
      "highlight_words": [
        "পুঁজি",
        "কিছু"
      ],
      "duration_sec": 12
    },
    {
      "scene_number": 2,
      "narration": "শুরু করুন এক ছোট কাজ দিয়ে, যার খরচ প্রায় শূন্য।",
      "visual_prompt": "Flat 2D illustration of a phone and a notebook on a desk, warm amber accent",
      "highlight_words": [
        "ছোট"
      ],
      "duration_sec": 14
    },
    {
      "scene_number": 3,
      "narration": "আজই একটার নাম লিখুন, কালকে শুরু করুন।",
      "visual_prompt": "Flat 2D illustration of a checklist with one item ticked, green accent",
      "highlight_words": [
        "আজই"
      ],
      "duration_sec": 14
    }
  ]
}
```

**Quality rules**
1. One idea per sentence, max 12 words; cut adjectives that do not change the action.
2. Every visual prompt must describe a single 9:16 frame drawable in flat 2D.
3. Never add a fact, price or statistic that is not in the story or niche report.

# How to test

- Prompt: `Use the script-writer skill with PROJECT=<project>` after story and hook exist.
- Checklist: expected `projects/<project>/02-script/latest_script.json` exists, parses, has 30-60 s total, every scene has 1-2 `highlight_words` present in its narration, and no niche/language value is hardcoded.

# Depends on / feeds into


story and hook -> voice stage

# Failure handling


If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
