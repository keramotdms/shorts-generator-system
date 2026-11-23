---
name: loop-cta-designer
description: Designs the loop ending and call to action.
category: script
status: implemented
phase: later
type: prompt-only
batch: B
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after script-writer and before caption-maker, when the final line is still a plain ending instead of a replay trigger.

# Purpose

Design a last-3-seconds handoff where the ending frame flows back into the opening hook and the call to action stays inside the caption safe zone.

# Input

- `projects/<project>/02-script/latest_script.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/02-script/loop-cta-designer.json`

# Loop design criteria

1. Use the final 3 seconds only; never extend the video beyond its locked duration.
2. The last frame must repeat the opening object or colour from hook.json.
3. Keep the spoken CTA to 8 Bangla words or fewer.
4. Place the CTA text above the bottom 15% of the frame to protect captions.
5. Write one explicit replay instruction in Bangla for the on-screen line.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "loop-cta-designer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Return the coffee cup to the opening position",
      "start_sec": 42,
      "end_sec": 43,
      "reason": "matches the hook object"
    },
    {
      "id": 2,
      "action": "Show 'আবার দেখুন' above the caption band",
      "start_sec": 43,
      "end_sec": 44,
      "reason": "4 Bangla words, safe zone clear"
    },
    {
      "id": 3,
      "action": "Freeze on the opening colour",
      "start_sec": 44,
      "end_sec": 45,
      "reason": "seamless replay point"
    }
  ],
  "constraints": [
    "final 3 seconds",
    "CTA at most 8 Bangla words",
    "text above bottom 15%"
  ],
  "summary": "Three-second loop returns the cup, shows a short Bangla CTA and freezes on the hook colour."
}
```

# Quality rules

1. All items fall inside the final 3 seconds of the script duration.
2. The CTA item contains a Bangla phrase of at most 8 words.
3. The constraints include the bottom 15% safe-zone rule.

# Steps

1. Read safe margins from config/style-bible.json through project-memory.
2. Open hook.json and note the opening object and palette colour.
3. Load the script duration and reserve its last 3 seconds for the loop.
4. Draft the replay instruction and count its Bangla words.
5. Write the loop plan to projects/<project>/02-script/loop-cta-designer.json.
6. Validate the plan schema and assert every item starts after the 42-second mark in a 45-second script.

# How to test

- Validate projects/_template/02-script/loop-cta-designer.json with the plan schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

script-writer -> video-editing

# Failure handling

If hook.json is missing, report the exact path and do not design a loop. If the script is shorter than 10 seconds, return WARN and reuse the whole final frame as the loop point.
