---
name: solver
description: Proposes fixes for reported bugs.
category: final-test
status: implemented
phase: later
type: prompt-only
batch: D
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after bug-finder and before final render, when the defect list is known but nobody has decided which fix comes first.

# Purpose

Turn each confirmed bug into one small, ordered fix that can be applied and re-tested without re-rendering the whole Short.

# Input

- `projects/<project>/08-final-test/bug-finder.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/08-final-test/solver.json`

- Format `json_utf8`: `projects/<project>/08-final-test/solver.json`

# Fix ordering rules

1. Create at most five fixes and order them by severity, highest first.
2. Every fix must name the exact bug id it resolves.
3. Give each fix an effort window of 30 to 300 seconds.
4. Never propose a fix that changes the locked script duration.
5. Prefer a trim, label change or local re-render over rebuilding every scene.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "solver",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Move the ৳120 label to second 1",
      "start_sec": 0,
      "end_sec": 90,
      "reason": "fixes bug-01 hook delay"
    },
    {
      "id": 2,
      "action": "Remove the unsupported ৳3,600 line",
      "start_sec": 90,
      "end_sec": 150,
      "reason": "fixes bug-02 missing source"
    },
    {
      "id": 3,
      "action": "Add the replay CTA to the last frame",
      "start_sec": 150,
      "end_sec": 240,
      "reason": "fixes bug-03 weak ending"
    }
  ],
  "constraints": [
    "max 5 fixes",
    "effort 30-300 seconds each",
    "locked duration unchanged"
  ],
  "summary": "Three ordered fixes mapped to bug ids, all achievable without re-rendering the full video."
}
```

# Quality rules

1. No two items reference the same bug id.
2. Each effort window is between 30 and 300 seconds.
3. The constraints include the locked-duration rule.

# Steps

1. Read style constraints through project-memory, then load the confirmed bug list.
2. Validate projects/<project>/08-final-test/bug-finder.json and extract bug ids.
3. Rank bugs by severity and keep only the top five.
4. Write one concrete fix per bug with a 30–300 second effort window.
5. Save the fix plan to projects/<project>/08-final-test/solver.json.
6. Validate the plan schema and assert no bug id is used twice.

# How to test

- Validate projects/_template/08-final-test/solver.json with the plan schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

bug-finder -> final render

# Failure handling

If no bug report exists, stop and name the missing file. If more than five bugs are confirmed, keep the five highest severity and list the rest in the summary as deferred.
