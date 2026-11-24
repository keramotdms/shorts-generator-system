---
name: ruthless-team
description: Gives a harsh quality critique.
category: final-test
status: implemented
phase: later
type: prompt-only
batch: D
schema: analysis
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after red-team and before bug-finder, when friendly review has gone soft and a blunt second opinion is needed.

# Purpose

Deliver an unkind but evidence-based critique of the final Short so weak hooks and vague numbers are caught before publication.

# Input

- `projects/<project>/08-final-test/final-video.mp4`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/08-final-test/ruthless-team.json`

- Format `json_utf8`: `projects/<project>/08-final-test/ruthless-team.json`

# Harsh critique criteria

1. Score exactly four dimensions: hook, trust, originality and call to action.
2. A score of 5 or lower requires a finding written in plain Bangla with no softener words.
3. Quote the exact second of the worst moment in each finding.
4. Do not repeat a red-team finding unless the video still shows the same problem.
5. Praise is not allowed; findings must only name defects and fixes.

# Output format (short example)

Schema: `config/schemas/analysis.json`

```json
{
  "status": "PASS",
  "skill": "ruthless-team",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "criteria": [
    {
      "name": "hook",
      "score": 3,
      "evidence": "money figure appears at 4.2 seconds, far too late"
    },
    {
      "name": "trust",
      "score": 5,
      "evidence": "monthly total has no source in the script"
    },
    {
      "name": "originality",
      "score": 7,
      "evidence": "coffee example is common but the loop is fresh"
    },
    {
      "name": "call to action",
      "score": 4,
      "evidence": "no replay instruction anywhere in the final 3 seconds"
    }
  ],
  "findings": [
    "Steam roller: put ৳120 in second 1, not second 5.",
    "The ৳3,600 claim is unsupported; cut it."
  ],
  "summary": "Four dimensions scored; hook and call to action are the two worst and need fixes before release."
}
```

# Quality rules

1. There are exactly four scored criteria with the required names.
2. Every finding includes a second or a script line.
3. No finding contains reassuring words such as 'good' or 'nice'.

# Steps

1. Load language and niche from project-memory so the blunt wording stays in Bangla.
2. Read red-team.json first and mark which problems are already reported.
3. Watch the final video metadata and score hook, trust, originality and call to action.
4. Write one harsh finding per dimension scoring 5 or below, each with a timestamp.
5. Save the critique to projects/<project>/08-final-test/ruthless-team.json.
6. Validate the analysis schema and check that no finding merely repeats red-team.json.

# How to test

- Validate projects/_template/08-final-test/ruthless-team.json with the analysis schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/analysis.json` by `tests/test_no_template.py`.

# Depends on / feeds into

video-editing -> bug-finder

# Failure handling

If the final video is absent, name the path and stop. If red-team.json is absent, continue but record the missing context in the summary instead of inventing prior findings.
