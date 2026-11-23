---
name: marketing-specialist
description: Plans promotion across channels.
category: marketing
status: implemented
phase: later
type: prompt-only
batch: D
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after handover and before scheduler-publisher, when the final assets are ready and promotion still needs a plan.

# Purpose

Build a three-channel promotion plan with fixed posting windows so one Short can be promoted without spamming the same audience everywhere.

# Input

- `projects/<project>/08-final-test/final-video.mp4`
- `projects/<project>/01-research/audience-persona-builder.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/09-description/marketing-specialist.md`

# Promotion constraints

1. Use at most three channels from config/channel.json.
2. Stagger the first two posts by at least 60 minutes.
3. Give each channel one job: discovery, saves or community.
4. Write every on-screen or caption line in Bangla for this channel.
5. Do not promise cross-posting to a platform absent from the channel config.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "marketing-specialist",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Post the Short to YouTube",
      "start_sec": 0,
      "end_sec": 45,
      "reason": "discovery job at 19:00 BST"
    },
    {
      "id": 2,
      "action": "Share a still to Facebook at 20:15",
      "start_sec": 60,
      "end_sec": 75,
      "reason": "community job, 75-minute stagger"
    },
    {
      "id": 3,
      "action": "Pin a Bangla comment with the saving tip",
      "start_sec": 90,
      "end_sec": 100,
      "reason": "saves job"
    }
  ],
  "constraints": [
    "max 3 channels",
    "60-minute minimum stagger",
    "Bangla copy only"
  ],
  "summary": "Three promotion actions across YouTube and Facebook with a staggered schedule and distinct jobs."
}
```

# Quality rules

1. Every action names a channel present in config/channel.json.
2. The first two posting items differ by at least 60 minutes.
3. The constraints list the Bangla copy rule.

# Steps

1. Load platform list and language from project-memory before reading the handover file.
2. Confirm projects/<project>/10-publish/handover.md exists and lists the final assets.
3. Assign one job to each of at most three configured channels.
4. Stagger posting windows by at least 60 minutes and write Bangla copy notes.
5. Save the promotion plan to projects/<project>/09-description/marketing-specialist.json.
6. Validate the plan schema and check every channel name against the config.

# How to test

- Validate projects/_template/09-description/marketing-specialist.json with the plan schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

final-test -> growth stage

# Failure handling

If handover.md is missing, stop and report the path. If fewer than two platforms are configured, plan a single channel and write a WARN about the reduced reach.
