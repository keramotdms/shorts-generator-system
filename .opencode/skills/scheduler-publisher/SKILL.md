---
name: scheduler-publisher
description: Schedules and publishes videos.
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

Use after handover and marketing-specialist, when posting times are agreed and a human will perform the upload.

# Purpose

Produce a validated publishing schedule from a manual request file; this skill never contacts a platform and never marks a video as actually published.

# Input

- `projects/<project>/10-publish/inputs/`
- `projects/<project>/10-publish/handover.md`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/10-publish/scheduler-publisher.json`

# Schedule checks

1. Require the handover file to exist before accepting any request row.
2. Allow at most one upload per platform per calendar day.
3. Keep every posted time in Bangladesh local time and label it BST.
4. Compare each request with the content calendar and flag unplanned videos.
5. Mark every row as planned only; never write published or live as a status.

# Output format (short example)

Schema: `config/schemas/manual-input.json`

```json
{
  "status": "PASS",
  "skill": "scheduler-publisher",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "api_needed": "later",
  "source_file": "projects/<project>/10-publish/inputs/schedule-requests.json",
  "rows": [
    {
      "platform": "youtube",
      "video": "coffee-price",
      "when": "2026-11-23 19:00 BST",
      "status": "planned"
    },
    {
      "platform": "facebook",
      "video": "coffee-price",
      "when": "2026-11-23 20:15 BST",
      "status": "planned"
    }
  ],
  "summary": "Two planned uploads validated against the calendar; a human must perform the actual publishing."
}
```

# Quality rules

1. Every row status is exactly planned.
2. No platform has two rows on the same date.
3. Each when value ends with BST.

# Steps

1. Verify projects/<project>/10-publish/handover.md exists and read the calendar through project-memory.
2. Load the manual schedule requests from projects/<project>/10-publish/inputs/schedule-requests.json.
3. Reject duplicate platform-and-day pairs and unplanned video names.
4. Normalise every timestamp to a BST-labelled string.
5. Write the validated schedule to projects/<project>/10-publish/scheduler-publisher.json.
6. Validate the manual-input schema and assert no row claims a published state.

# How to test

- Save two schedule rows under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/manual-input.json` by `tests/test_no_template.py`.

# Depends on / feeds into

handover -> platforms

# Failure handling

If handover.md is missing, stop and name the path. This skill cannot publish; if the user expects a live upload, tell them to use GitHub Desktop sign-in or `gh auth login` for a future API-enabled version.
