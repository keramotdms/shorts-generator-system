---
name: virtual-camera-planner
description: Plans virtual camera moves.
category: video-editing
subcategory: visual
status: implemented
phase: later
type: prompt-only
batch: C
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after scenario-designer and before video-maker, when a static layout needs controlled movement instead of random animation.

# Purpose

Write a timed camera plan that tells the SVG renderer when to pan or zoom a flat scene while keeping every caption inside the safe zone.

# Input

- `projects/<project>/05-scene/scenario-designer.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/07-edit/virtual-camera-planner.json`

# Camera move constraints

1. Allow at most two camera moves per scene.
2. Keep each move between 2 and 5 seconds.
3. Cap zoom changes at 8% so flat art does not pixelate.
4. Never pan the bottom 15% of the frame where captions sit.
5. Give each move an explicit reason tied to the scene's visual job.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "virtual-camera-planner",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Zoom 4% toward the coffee cup",
      "start_sec": 0,
      "end_sec": 3,
      "reason": "draws attention to the hook object"
    },
    {
      "id": 2,
      "action": "Pan right across the notebook",
      "start_sec": 8,
      "end_sec": 12,
      "reason": "reveals the side-hustle prop"
    },
    {
      "id": 3,
      "action": "Hold camera steady",
      "start_sec": 38,
      "end_sec": 45,
      "reason": "keeps the loop line readable"
    }
  ],
  "constraints": [
    "max 2 moves per scene",
    "zoom change at most 8%",
    "bottom 15% protected"
  ],
  "summary": "Three timed camera decisions with modest zoom and a protected caption band."
}
```

# Quality rules

1. No item duration is under 2 or over 5 seconds except an explicit hold.
2. Every action names a zoom or pan direction and a magnitude.
3. Constraints include the bottom 15% protection rule.

# Steps

1. Read safe margins and resolution from project-memory before opening the scene layout.
2. Validate projects/<project>/05-scene/scenario-designer.json and list its scenes.
3. Assign at most two moves per scene with durations between 2 and 5 seconds.
4. Check each zoom against the 8% cap and each pan against the caption band.
5. Write the camera plan to projects/<project>/05-scene/virtual-camera-planner.json.
6. Validate the plan schema and report any scene that exceeds the move limit.

# How to test

- Validate projects/_template/05-scene/virtual-camera-planner.json with the plan schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

video-making -> video-editor

# Failure handling

If the scene layout is missing, stop and name the path. If a move would violate the caption band, replace it with a hold and add a WARN instead of shifting captions.
