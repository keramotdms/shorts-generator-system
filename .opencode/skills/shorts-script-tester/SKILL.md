---
name: shorts-script-tester
description: Audits and scores generated YouTube Shorts scripts (Bangla or English) for hook strength, tone, emotional feel, word count pacing, goal alignment, and visual clarity, then offers an improved rewrite if needed.
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
