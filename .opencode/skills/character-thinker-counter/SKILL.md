---
name: character-thinker-counter
description: Brainstorms and scores character ideas before design.
category: character
status: implemented
phase: later
type: prompt-only
batch: A
schema: selection
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after the script and voice plan are ready and before character-designer, when you need exactly one creator character to draw.

# Purpose

Generate five character concepts from the script and style bible, then shortlist three using a fixed score so design work starts with a clear choice.

# Input

- - `config/style-bible.json`
- - `projects/<project>/02-script/latest_script.json`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `character idea list`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Character score criteria

1. Produce exactly five candidates before scoring; shortlist exactly three.
2. Score on 0–10 for recognisable silhouette, flat-shape simplicity and audience fit.
3. Reject any candidate that needs fine detail, gradients or photo texture.
4. Keep the default character from the style bible as one candidate.
5. Give every candidate a stable id in the form `creator-01` without spaces.

# Output format (short example)

Schema: `config/schemas/selection.json`

```json
{
  "status": "PASS",
  "skill": "character-thinker-counter",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "candidates": [
    {
      "id": "creator-01",
      "score": 9,
      "reason": "style-bible default; round face, simple shirt"
    },
    {
      "id": "creator-02",
      "score": 7,
      "reason": "glasses add detail but still flat"
    },
    {
      "id": "creator-03",
      "score": 5,
      "reason": "needs hair texture; rejected"
    },
    {
      "id": "creator-04",
      "score": 8,
      "reason": "distinct cap silhouette"
    },
    {
      "id": "creator-05",
      "score": 6,
      "reason": "too close to creator-01"
    }
  ],
  "chosen_id": "creator-01",
  "rationale": "Highest score on silhouette and flat-shape simplicity; matches the style-bible default."
}
```

# Quality rules

1. There are exactly five candidates and the chosen id is one of them.
2. Every id matches the lowercase-kebab pattern.
3. No reason mentions photorealism or gradient shading.

# Steps

1. Load the character block and palette from `config/style-bible.json` via project-memory.
2. Read the narrator description from the validated script.
3. Draft five distinct silhouettes using only flat shapes from the palette.
4. Score each candidate on silhouette, simplicity and audience fit.
5. Write the shortlist to `projects/<project>/04-character/character-thinker-counter.json`.
6. Validate against `config/schemas/selection.json` and check id format.

# How to test

- Run `python tests/test_skills.py --batch 5`, then validate the written selection with the selection schema.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/selection.json` by `tests/test_no_template.py`.

# Depends on / feeds into

script and voice -> character-designer

# Failure handling

If the style bible has no character block, stop and ask project-memory to regenerate it rather than inventing a look. If fewer than five ideas exist, report WARN with the count.
