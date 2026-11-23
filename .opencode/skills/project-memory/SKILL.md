---
name: project-memory
description: Stores tone, colors, fonts, character look and voice choices.
category: core
status: implemented
phase: 1
type: script-backed
batch: 1
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when stores tone, colors, fonts, character look and voice choices for a video in `projects/<project>/`.

# Purpose

Stores tone, colors, fonts, character look and voice choices.

# Input

- `config/channel.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `config/style-bible.json`

# Steps

1. Open `config/channel.json` directly (this skill is the source, so it must not call itself). Read `niche`, `language`, `audience_location`, `video.length_sec` and `platforms`. If any of the first three is null, empty or `TO BE DECIDED`, ask the user once, save the answers back into that file, then continue.
2. Check the file parses as JSON and that `language` is `bn` or `en`. Stop with the exact missing key name if it does not; do not guess a niche.
3. Derive the style from the confirmed channel values: tone = natural and conversational, visual style = flat 2D with bold shapes, palette = dark slate / white / amber / green, font = Noto Sans Bengali for `bn`. Never write the niche or language into a skill folder.
4. Run `python scripts/skill_tools.py project-memory run` with `PROJECT=<project>` to write `config/style-bible.json` at the repository root (no `projects/<project>/` prefix). The helper copies channel values and the derived style.
5. Re-open `config/style-bible.json`, confirm `version`, `style`, `characters`, `voice` and `channel` exist and that `channel.niche`/`channel.language` match `config/channel.json`. Log any mismatch via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Acceptance criteria**
- `config/channel.json` has non-null `niche`, `language`, `audience_location`.
- `config/style-bible.json` exists at the repository root and parses.
- Style bible `channel` block matches channel config field for field.
- No value is hardcoded inside any skill folder.

**Output format (short example)**
```json
{
  "version": 1,
  "style": {"tone": "natural, conversational", "visual_style": "flat 2D illustration",
            "palette": ["#111827", "#F9FAFB", "#F59E0B", "#10B981"],
            "font": "Noto Sans Bengali"},
  "voice": {"language": "bn", "default_gender": "male"},
  "channel": {"niche": "Personal finance / side hustles", "language": "bn"}
}
```

**Quality rules**
1. Ask at most one clarification round; store the answer instead of asking again later.
2. Keep the palette to 4 colours and the font to one per language.
3. Never create a per-video folder in `projects/` — this is channel-level data.

# How to test

- `python scripts/skill_tools.py project-memory --self-test` → expected `PASS project-memory: ...`. Then confirm `config/style-bible.json` exists and is non-empty after a real run.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

channel config -> script, voice and character stages

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
