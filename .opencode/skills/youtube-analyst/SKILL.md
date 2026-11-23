---
name: youtube-analyst
description: Analyzes channel performance.
category: growth
status: implemented
phase: later
type: prompt-only
batch: D
schema: manual-input
api_needed: later
data_source: manual-file
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after videos are published and the analytics file has been exported to 10-publish/inputs/, before analytics-feedback-loop.

# Purpose

Summarise a manual YouTube analytics export into three scored dimensions that describe retention, reach and saving behaviour.

# Input

- `projects/<project>/10-publish/inputs/`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/10-publish/youtube-analyst.json`

# Analysis dimensions

1. Require at least 5 exported videos before scoring a dimension.
2. Score retention from average view duration divided by the video length, capped at 10.
3. Score reach from impressions relative to the median of the exported set.
4. Score saves from the save count relative to views, multiplied by 100 and capped at 10.
5. Never report a metric that is absent from the export; write unavailable instead.

# Output format (short example)

Schema: `config/schemas/manual-input.json`

```json
{
  "status": "PASS",
  "skill": "youtube-analyst",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "api_needed": "later",
  "source_file": "projects/<project>/10-publish/inputs/youtube-analytics-export.json",
  "rows": [
    {
      "video": "coffee-price",
      "views": 4200,
      "avg_view_sec": 31,
      "video_sec": 45,
      "impressions": 9000,
      "saves": 310
    },
    {
      "video": "side-hustle",
      "views": 2800,
      "avg_view_sec": 38,
      "video_sec": 45,
      "impressions": 5200,
      "saves": 260
    }
  ],
  "summary": "Five exported videos scored: retention 7/10, reach 6/10, saves 8/10; saving behaviour is the strongest signal."
}
```

# Quality rules

1. Summary reports exactly three scores in the form n/10.
2. No row contains a metric missing from the export.
3. Scores never exceed 10.

# Steps

1. Confirm the manual export exists under projects/<project>/10-publish/inputs/.
2. Read the target length from project-memory and count exported rows.
3. Compute retention, reach and save scores using only exported fields.
4. Write the three scores and their evidence into the summary.
5. Save the report to projects/<project>/10-publish/youtube-analyst.json.
6. Validate the manual-input schema and mark api_needed as later.

# How to test

- Export five sample analytics rows under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/manual-input.json` by `tests/test_no_template.py`.

# Depends on / feeds into

published video -> research loop

# Failure handling

If fewer than five rows are exported, write INSUFFICIENT DATA in the summary. Never call the YouTube API or fabricate impressions, views or saves.
