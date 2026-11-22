---
name: script-writer
description: Generates viral, high-retention 30-60 second YouTube Shorts scripts in Bangla or English with scene-by-scene visual prompts and timing metadata saved as JSON.
category: script
status: mvp
phase: 2
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
