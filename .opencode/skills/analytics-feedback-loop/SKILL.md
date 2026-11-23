---
name: analytics-feedback-loop
description: Feeds results back into research.
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

Use after youtube-analyst and before the next research phase, when the team needs to change its topic choices based on past results.

# Purpose

Convert a manually exported performance report into three research notes that the next story-thinker run can actually use.

# Input

- `projects/<project>/10-publish/inputs/analytics-report.json` (manual export; no API access)
- `research/niche-report.md`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `insight notes for research`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Feedback rules

1. Use at least 5 published videos from the export before drawing a conclusion.
2. Rank videos by save rate, not by raw views, because this niche is educational.
3. Write exactly three research notes in the summary.
4. Each note must name a topic or format from research/niche-report.md.
5. Never infer demographics that are absent from the export.

# Output format (short example)

Schema: `config/schemas/manual-input.json`

```json
{
  "status": "PASS",
  "skill": "analytics-feedback-loop",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "api_needed": "later",
  "source_file": "projects/<project>/10-publish/inputs/analytics-report.json",
  "rows": [
    {
      "video": "coffee-price",
      "views": 4200,
      "saves": 310,
      "save_rate": 0.074
    },
    {
      "video": "side-hustle",
      "views": 2800,
      "saves": 260,
      "save_rate": 0.093
    }
  ],
  "summary": "Top save rate is the side-hustle format; add two more side-hustle topics and keep the coffee hook style in the next research round."
}
```

# Quality rules

1. Summary contains exactly three research notes.
2. Each note mentions a topic present in the niche report.
3. No row contains a demographic field that was not exported.

# Steps

1. Check that projects/<project>/10-publish/inputs/analytics-report.json exists before reading anything.
2. Count rows and stop with WARN when fewer than five videos are present.
3. Rank the exported videos by save rate and note the top format.
4. Compare that format with topics listed in research/niche-report.md.
5. Write three concrete research notes into the summary.
6. Save the feedback file to projects/<project>/10-publish/analytics-feedback-loop.json and validate its schema.

# How to test

- Export five sample rows under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/manual-input.json` by `tests/test_no_template.py`.

# Depends on / feeds into

youtube-analyst -> research stage

# Failure handling

If the manual analytics export is missing, name the path and stop. Never call a YouTube API or invent view and save numbers.
