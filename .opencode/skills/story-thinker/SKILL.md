---
name: story-thinker
description: Turns research into a short story concept.
category: script
status: implemented
phase: 2
type: prompt-only
batch: 3
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when turns research into a short story concept for a video in `projects/<project>/`.

# Purpose

Turns research into a short story concept.

# Input

- `projects/<project>/01-research/niche-report.md`
- `research/trend-cache/trend-report.json`
- `config/channel.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/02-script/story.json`

- Format `json_utf8`: `projects/<project>/02-script/story.json`

# Steps

1. Read `projects/<project>/01-research/niche-report.md` (winner and ranking) plus `config/channel.json` and `config/style-bible.json` through project-memory. Read `research/trend-cache/trend-report.json` if it exists and use its highest-scoring local trend as a timing hint.
2. Pick the single winner topic. Write one sentence naming the viewer's pain in Bangladesh, one sentence naming the promised outcome, and one `hook_seed` phrased as a question or bold claim in the project language.
3. Split the story into exactly 3 beats: (1) show the pain, (2) give one cheap action, (3) return to the hook for the loop. Each beat must be visualisable in one 9:16 frame.
4. Write `projects/<project>/02-script/story.json` using the schema fields below; create the `02-script` folder first. Copy `niche` and `audience` from channel config.
5. Run `python scripts/schema_validator.py story projects/<project>/02-script/story.json` and re-open the file. If validation fails, fix and re-run; log remaining problems via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Acceptance criteria**
- `story.json` passes `config/schemas/story.json`.
- `beats` has 3 items, each with `beat` (1-3) and a `purpose` naming what the viewer sees.
- `angle` names one specific action, not a vague theme.
- `niche` and `audience` are copied verbatim from channel config.

**Output format (short example)**
```json
{
  "niche": "Personal finance / side hustles",
  "audience": "Bangladesh / Bangla-speaking",
  "angle": "Resell one used phone this week",
  "hook_seed": "পুরনো ফোন দিয়েই শুরু করা যায়?",
  "source_files": ["projects/<project>/01-research/niche-report.md"],
  "beats": [
    {"beat": 1, "purpose": "show an empty wallet"},
    {"beat": 2, "purpose": "list one used phone"},
    {"beat": 3, "purpose": "repeat the hook as a loop"}
  ]
}
```

**Quality rules**
1. One story, one promise — never combine two side hustles in one Short.
2. Every beat must be drawable as a flat 2D frame; drop abstract-only ideas.
3. Keep the hook seed in spoken Bangla and under 12 words.

# How to test

- Type: `Use the story-thinker skill with PROJECT=<project>`. Expected: `projects/<project>/02-script/story.json` exists, parses cleanly, and contains no hardcoded niche or language value.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

research outputs -> hook-writer

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
