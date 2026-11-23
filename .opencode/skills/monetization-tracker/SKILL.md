---
name: monetization-tracker
description: Tracks revenue and monetization.
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

Use after a video earns revenue and its statement has been exported to 10-publish/inputs/, before the next planning round.

# Purpose

Summarise a manually exported revenue file in Bangla taka and flag any row where the amount and views do not agree with the stated rate.

# Input

- `projects/<project>/10-publish/inputs/`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/10-publish/monetization-tracker.json`

# Revenue checks

1. Require at least 3 exported rows before reporting a trend.
2. Keep every amount in Bangla taka; never convert to another currency.
3. Flag a row when amount divided by views differs from the stated rate by more than 20%.
4. Report totals as whole taka with no decimal paise.
5. Never estimate revenue for a video missing from the export.

# Output format (short example)

Schema: `config/schemas/manual-input.json`

```json
{
  "status": "PASS",
  "skill": "monetization-tracker",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "api_needed": "later",
  "source_file": "projects/<project>/10-publish/inputs/revenue-export.json",
  "rows": [
    {
      "video": "coffee-price",
      "views": 4200,
      "amount_taka": 1260,
      "rate": 0.3
    },
    {
      "video": "side-hustle",
      "views": 2800,
      "amount_taka": 700,
      "rate": 0.3
    }
  ],
  "summary": "Two exported rows total 1960 taka; neither row deviates from its stated rate by more than 20 percent."
}
```

# Quality rules

1. Every amount field is named amount_taka and is an integer.
2. The summary contains a whole-taka total.
3. No row has an estimated or invented view count.

# Steps

1. Confirm the manual revenue export exists under projects/<project>/10-publish/inputs/.
2. Read the currency from project-memory and reject any row using another currency symbol.
3. Count rows and compute the whole-taka total.
4. Compare each amount with views times rate and flag deviations over 20 percent.
5. Write the tracker output to projects/<project>/10-publish/monetization-tracker.json.
6. Validate the manual-input schema and confirm every amount is an integer.

# How to test

- Export three sample revenue rows under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/manual-input.json` by `tests/test_no_template.py`.

# Depends on / feeds into

published video -> research stage

# Failure handling

If the export is missing, report the path and stop. Never call a monetization API or guess earnings for a video absent from the export.
