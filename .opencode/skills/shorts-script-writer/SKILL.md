---
name: shorts-script-writer
description: Generates viral, high-retention 30-60 second YouTube Shorts scripts with scene-by-scene visual prompts and timing metadata saved as JSON.
---

# Shorts Script Writer Skill

When the user asks to write a script for a Short, follow these exact steps:

1. **Hook First (0-3 seconds):** Start with a pattern-interrupt hook, shocking fact, or bold question that stops viewers from scrolling.
2. **Fast-Paced Body (3-45 seconds):** Keep sentences short (max 8-12 words per sentence), conversational, and value-packed. Remove all fluff.
3. **Strong CTA / Loop (Last 3-5 seconds):** End with a seamless loop back to the first sentence or a clear call-to-action.
4. **Structured Output:** 
   - Create a `scripts/` folder if it doesn't exist.
   - Save the output as `scripts/latest_script.json` with this exact structure:
     - `title`: Catchy title
     - `hook`: The opening 3-second line
     - `total_duration_sec`: Target duration (30 to 60)
     - `scenes`: An array of objects, each containing:
       - `scene_number`: Integer
       - `narration`: Exact spoken text for this scene (3-5 seconds long)
       - `visual_prompt`: Detailed description of what should appear on screen (motion graphics, text overlay, or background visual)
       - `highlight_words`: 1-2 key words to highlight in bold/color on screen
   - Also display a clean, readable summary of the script in the chat for the user to review.
