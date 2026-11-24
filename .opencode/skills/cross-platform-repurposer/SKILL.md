---
name: cross-platform-repurposer
description: Adapts videos for other platforms.
category: growth
status: implemented
phase: later
type: prompt-only
batch: D
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after handover and before scheduler-publisher, when the same video must serve Facebook and another configured platform.

# Purpose

Plan local crops and caption adjustments for reposting one finished Short to two additional platforms without new scripting or API calls.

# Input

- `projects/<project>/08-final-test/final-video.mp4`
- `projects/<project>/10-publish/handover.md`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/10-publish/cross-platform-repurposer.json`

- Format `json_utf8`: `projects/<project>/10-publish/cross-platform-repurposer.json`

# Repurposing constraints

1. Plan at most two additional platforms beyond the primary one.
2. Keep the 9:16 layout for Reels-style feeds and never stretch to 16:9.
3. Move captions inward by 5% of width for platforms with right-side controls.
4. Keep the original 30–60 second duration; do not add intro cards.
5. List only platforms present in config/channel.json.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "cross-platform-repurposer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Export 9:16 copy for Facebook Reels",
      "start_sec": 0,
      "end_sec": 45,
      "reason": "same frame size, caption inset 5%"
    },
    {
      "id": 2,
      "action": "Export square crop preview for the feed",
      "start_sec": 0,
      "end_sec": 45,
      "reason": " centred crop keeps the hook object visible"
    },
    {
      "id": 3,
      "action": "Replace the CTA with a Bangla follow line",
      "start_sec": 42,
      "end_sec": 45,
      "reason": "platform-specific ending, same duration"
    }
  ],
  "constraints": [
    "max 2 extra platforms",
    "no 16:9 stretch",
    "original duration preserved"
  ],
  "summary": "Two local export plans and one CTA swap, all using the finished video without external services."
}
```

# Quality rules

1. Every item names a configured platform or a local crop action.
2. No action increases the video duration.
3. Constraints include the no-16:9-stretch rule.

# Steps

1. Read the platform list and resolution from project-memory before opening the final video path.
2. Confirm projects/<project>/08-final-test/final-video.mp4 exists locally.
3. Choose at most two configured platforms and state the crop rule for each.
4. Adjust caption inset by 5% in the plan for platforms with overlays.
5. Write the repurposing plan to projects/<project>/10-publish/cross-platform-repurposer.json.
6. Validate the plan schema and confirm no platform name is invented.

# How to test

- Validate projects/_template/10-publish/cross-platform-repurposer.json with the plan schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

handover -> other platforms

# Failure handling

If the final video is missing, name the path and stop. If only one platform is configured, return WARN with a single-platform plan instead of inventing a destination.
