---
name: script-user-tester
description: Runs a manual viewer feedback round on a draft script.
category: script
status: implemented
phase: later
type: prompt-only
batch: A
schema: analysis
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when a script is ready for a small human read-through and you have collected viewer answers into a local JSON file.

# Purpose

Collect structured feedback from at least five manually recruited viewers and turn it into a scored script usability report before voice recording.

# Input

- `projects/<project>/02-script/latest_script.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/02-script/script-user-tester.json`

- Format `json_utf8`: `projects/<project>/02-script/script-user-tester.json`

# Viewer scoring criteria

1. Require at least 5 responses; fewer than 5 is a WARN, not a PASS.
2. At least 4 of 5 viewers must answer `understood_hook: true`, otherwise the hook fails.
3. Average `would_watch` must be 4 or higher on a 1–5 scale.
4. Group every `confusion` string by scene and flag any scene named by 2 or more viewers.
5. Quote Bangla feedback verbatim; do not translate it into another language in the report.

# Output format (short example)

Schema: `config/schemas/analysis.json`

```json
{
  "status": "PASS",
  "skill": "script-user-tester",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "source_file": "projects/<project>/02-script/inputs/viewer-feedback.json",
  "criteria": [
    {
      "name": "hook understood",
      "score": 8,
      "evidence": "4 of 5 viewers answered true"
    },
    {
      "name": "would watch",
      "score": 8,
      "evidence": "average 4.2 out of 5"
    },
    {
      "name": "scene clarity",
      "score": 6,
      "evidence": "scene 3 named by 2 viewers"
    }
  ],
  "findings": [
    "Scene 3 lists three numbers at once; split it.",
    "Bangla hook line was understood without explanation."
  ],
  "summary": "Five manual viewers tested; hook passes, scene 3 needs one simplification."
}
```

# Quality rules

1. The report states the exact number of responses used.
2. Every score is between 0 and 10 and has a quoted evidence string.
3. The report never claims automated or API-based viewer collection.

# Steps

1. Confirm the manual export exists at `projects/<project>/02-script/inputs/viewer-feedback.json`.
2. Validate the draft script with the latest_script schema before reading feedback about it.
3. Count responses and refuse to score if fewer than five are present.
4. Compute hook understanding, average would_watch and per-scene confusion counts.
5. Write the scored report to `projects/<project>/02-script/script-user-tester.json`.
6. Validate the report against `config/schemas/analysis.json` and preserve Bangla quotes.

# How to test

- Save five sample responses in `projects/_template/02-script/inputs/viewer-feedback.json`, run the skill, then `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/analysis.json` by `tests/test_no_template.py`.

# Depends on / feeds into

script-writer -> script-tester

# Failure handling

Never fabricate viewer responses. If the input file is missing, report its exact path and stop with WARN instead of producing a fake report.
