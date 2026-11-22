---
name: voiceover-captions
description: Generates natural Bangla or English voiceover audio (MP3) and exact word/phrase-level caption timestamps (JSON) from scripts/latest_script.json using free edge-tts.
---

# Shorts Voiceover & Captions Skill

When the user asks to generate voiceover or captions from the script:
1. Ensure the Python package `edge-tts` is installed (run `pip install edge-tts` if missing).
2. Run `python scripts/generate_audio.py` (pass `--gender female` if the user requests a female voice; default is male).
3. Verify that both `output/voiceover.mp3` and `output/captions.json` are generated successfully and report the exact total audio duration in seconds.
