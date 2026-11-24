---
name: voiceover-generator
description: Generates natural speech audio and word timings.
category: voice
status: implemented
phase: 3
type: script-backed
batch: 4
schema: latest_script
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when generates natural speech audio and word timings for a video in `projects/<project>/`.

# Purpose

Generates natural speech audio and word timings.

# Input

- `projects/<project>/02-script/latest_script.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/03-voice/voiceover.mp3`
- `projects/<project>/03-voice/captions.json`

- Format `mp3_voice`: `projects/<project>/03-voice/voiceover.mp3`
- Format `json_utf8`: `projects/<project>/03-voice/captions.json`

# Steps

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `projects/<project>/02-script/latest_script.json`; if it is missing or malformed, follow Failure handling and stop. Validate `projects/<project>/02-script/latest_script.json` against `config/schemas/latest_script.json` with `python scripts/schema_validator.py latest_script projects/<project>/02-script/latest_script.json`.
3. Run `python scripts/generate_audio.py --project <project> --gender <male|female>`; it validates the script, writes `03-voice/voiceover.mp3` plus `03-voice/captions.json`, and reports the exact duration.
4. Write `projects/<project>/03-voice/voiceover.mp3` and `projects/<project>/03-voice/captions.json`; create parent folders first.
5. Re-open both files, confirm the MP3 is non-empty and report its exact duration; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`. Validate `projects/<project>/03-voice/captions.json` against `config/schemas/captions.json` with `python scripts/schema_validator.py captions projects/<project>/03-voice/captions.json` before accepting it.

# Bangla rules

1. Use the Bangla `bn` voice and check TTS pronunciation of Bengali numerals and spoken ৳ amounts.
2. Keep each narration line to 8-12 words so the 110-130 wpm Bangla pace stays natural.
3. Reject a take that switches to English mid-line unless the script explicitly requests it.

**Input example (validated before TTS)**
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
      "highlight_words": ["পুঁজি", "কিছু"],
      "duration_sec": 12
    },
    {
      "scene_number": 2,
      "narration": "শুরু করুন এক ছোট কাজ দিয়ে, যার খরচ প্রায় শূন্য।",
      "visual_prompt": "Flat 2D illustration of a phone and a notebook on a desk, warm amber accent",
      "highlight_words": ["ছোট"],
      "duration_sec": 14
    },
    {
      "scene_number": 3,
      "narration": "আজই একটার নাম লিখুন, কালকে শুরু করুন।",
      "visual_prompt": "Flat 2D illustration of a checklist with one item ticked, green accent",
      "highlight_words": ["আজই"],
      "duration_sec": 14
    }
  ]
}
```

# How to test

- `python scripts/skill_tools.py voiceover-generator --self-test` → expected `PASS voiceover-generator: ...`. Then confirm `projects/<project>/03-voice/voiceover.mp3 + projects/<project>/03-voice/captions.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

script-writer -> collector

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
