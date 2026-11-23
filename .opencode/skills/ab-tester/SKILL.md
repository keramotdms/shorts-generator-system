---
name: ab-tester
description: Runs A/B tests on titles and thumbnails.
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

Use after analytics export is available in 10-publish/inputs/ and before analytics-feedback-loop, when a title or thumbnail choice must be made from evidence.

# Purpose

Compare two manually exported title or thumbnail variants and declare a winner only when both arms have enough impressions.

# Input

- projects/<project>/10-publish/inputs/ab-results.json (manual export; no API access)
- projects/<project>/09-description/description.md
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `A/B test report`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Test validity rules

1. Require at least 100 impressions in each arm before declaring a winner.
2. Compute click-through rate as clicks divided by impressions, rounded to two decimals.
3. Declare a winner only when the CTR gap is at least 0.02.
4. Compare exactly two variants: A and B; ignore any third row.
5. Never call a platform API or generate missing export rows.

# Output format (short example)

Schema: `config/schemas/manual-input.json`

```json
{
  "status": "PASS",
  "skill": "ab-tester",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "api_needed": "later",
  "source_file": "projects/<project>/10-publish/inputs/ab-results.json",
  "rows": [
    {
      "variant": "A",
      "impressions": 1200,
      "clicks": 96,
      "ctr": 0.08
    },
    {
      "variant": "B",
      "impressions": 1180,
      "clicks": 71,
      "ctr": 0.06
    }
  ],
  "summary": "Manual export has 1200 and 1180 impressions; variant A wins by 0.02 CTR with a valid sample."
}
```

# Quality rules

1. Rows contain exactly two variants named A and B.
2. Both impression counts are at least 100.
3. Summary names the winner only if the CTR gap meets 0.02.

# Steps

1. Confirm the manual export exists at projects/<project>/10-publish/inputs/ab-results.json.
2. Read both rows and reject any variant label other than A or B.
3. Check the 100-impression minimum on each arm before computing rates.
4. Calculate both CTR values and their absolute gap.
5. Write the comparison to projects/<project>/10-publish/ab-tester.json.
6. Validate the manual-input schema and record api_needed as later.

# How to test

- Save two A/B rows under projects/_template/10-publish/inputs/ and run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/manual-input.json` by `tests/test_no_template.py`.

# Depends on / feeds into

growth data -> research stage

# Failure handling

If the export is missing, report the exact path and stop; never fabricate impressions. If either arm is under 100 impressions, write INCONCLUSIVE in the summary and declare no winner.
