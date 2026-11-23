---
name: content-calendar
description: Plans topics and posting dates.
category: research
status: implemented
phase: later
type: prompt-only
batch: B
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after niche research and before scheduler-publisher, when the channel needs a repeatable posting rhythm rather than ad-hoc uploads.

# Purpose

Turn research topics into a two-week posting calendar with fixed weekdays, local publish times and one clear goal per video.

# Input

- `projects/<project>/01-research/niche-report.md`
- `research/trend-cache/trend-report.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/01-research/content-calendar.json`

# Calendar constraints

1. Plan exactly 14 days starting on the next Monday after the current date.
2. Schedule at most 4 Shorts per week on distinct weekdays.
3. Use Bangladesh local time in every reason string; write the hour with `BST`.
4. Post no more than one money-topic video on two consecutive days.
5. Give each item one goal: reach, save or comment, and repeat each goal at least twice.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "content-calendar",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Publish coffee-price Short",
      "start_sec": 0,
      "end_sec": 45,
      "reason": "Mon 2026-11-23 19:00 BST - reach"
    },
    {
      "id": 2,
      "action": "Publish side-hustle notebook Short",
      "start_sec": 0,
      "end_sec": 45,
      "reason": "Wed 2026-11-25 12:30 BST - save"
    },
    {
      "id": 3,
      "action": "Publish saving-loop Short",
      "start_sec": 0,
      "end_sec": 45,
      "reason": "Fri 2026-11-27 19:00 BST - comment"
    }
  ],
  "constraints": [
    "14-day window",
    "max 4 Shorts per week",
    "Bangladesh local time (BST)"
  ],
  "summary": "Two-week calendar with three Bangla finance Shorts on separate weekdays and three distinct goals."
}
```

# Quality rules

1. Every reason string contains a weekday, a BST time and a goal word.
2. No two items share the same weekday.
3. The constraints list the 14-day window and the weekly cap.

# Steps

1. Read the cadence and region from project-memory so weekday and time rules match the channel.
2. List topic ideas from projects/<project>/01-research/niche-report.md and the newest trend cache file.
3. Place one topic on each chosen weekday inside the 14-day window.
4. Check that money topics are not on consecutive days and that goals repeat.
5. Write the calendar to projects/<project>/01-research/content-calendar.json.
6. Validate against `config/schemas/plan.json` and recheck every BST time string.

# How to test

- Validate projects/_template/01-research/content-calendar.json with the plan schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

research outputs -> scheduler-publisher

# Failure handling

If trend cache and niche report are both empty, stop with a WARN instead of inventing topics. If the cadence exceeds 4 per week in channel config, keep the config value and note the conflict in the summary.
