---
name: hook-writer
description: Writes the first 3-second attention hook.
category: script
status: implemented
phase: 2
type: prompt-only
batch: 3
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when writes the first 3-second attention hook for a video in `projects/<project>/`.

# Purpose

Writes the first 3-second attention hook.

# Input

- `projects/<project>/02-script/story.json`
- `config/channel.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/02-script/hook.json`

# Steps

1. Read `projects/<project>/02-script/story.json` (`hook_seed`, `angle`, first beat) and `config/channel.json` + `config/style-bible.json` through project-memory. Use `language` from channel config for the hook text.
2. Choose one hook type from `question`, `shock`, `relatable`, `promise`, `contrarian`. Write the hook in one spoken sentence of at most 12 words; it must name the viewer's pain or the promised outcome from the story angle.
3. Write a `visual_prompt` in English describing one contrasting image for the first frame (for example: empty wallet → coin stack). Keep it to one flat 2D scene that a renderer can draw without extra assets.
4. Set `duration_sec` to 2.5 or 3 and write `projects/<project>/02-script/hook.json` with the fields below; create the folder first.
5. Run `python scripts/schema_validator.py hook projects/<project>/02-script/hook.json`, re-open the file, and log any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Acceptance criteria**
- `hook.json` passes `config/schemas/hook.json`.
- `text` is in the project language, at most 12 words, and matches the story `hook_seed` in meaning.
- `type` is one of the 5 allowed values and `duration_sec` is 2-3.5.
- `visual_prompt` is English, at least 8 characters, and describes exactly one frame.

**Output format (short example)**
```json
{
  "text": "পুরনো ফোন দিয়েই শুরু করা যায়?",
  "type": "question",
  "duration_sec": 3,
  "visual_prompt": "Flat 2D split frame: empty wallet on left, one coin stack on right",
  "language": "bn"
}
```

**Quality rules**
1. No polite openings ("আজ আমরা আলোচনা করব") — the first word must create tension or curiosity.
2. Do not promise unrealistic money; keep the outcome reachable in 7 days.
3. The visual prompt must not require a photo, logo, or FFmpeg effect.

# Bangla rules

1. Write the 3-second hook in natural Bangla with 8-12 spoken words.
2. Use Bengali numerals and ৳ for any amount; read the hook aloud once to catch awkward pronunciation.
3. Do not mix English connector words into the Bangla hook.

# How to test

- Type: `Use the hook-writer skill with PROJECT=<project>`. Expected: `projects/<project>/02-script/hook.json` exists, parses cleanly, and contains no hardcoded niche or language value.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

story-thinker -> script-writer

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
