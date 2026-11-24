---
name: retention-pacing-optimizer
description: Tightens script pacing with timed cut targets for Shorts.
category: script
status: implemented
phase: later
type: prompt-only
batch: A
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after script-writer when the script is complete but the first 3 seconds feel slow or scenes run too long for a Short.

# Purpose

Score a draft script for attention decay and return a timed re-cut plan that removes dead air without changing the script's meaning.

# Input

- `projects/<project>/02-script/latest_script.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/02-script/retention-pacing-optimizer.json`

- Format `json_utf8`: `projects/<project>/02-script/retention-pacing-optimizer.json`

# Pacing score criteria

1. The hook must land by 2.5 seconds; if it starts later, score that criterion 0/10.
2. No more than 4 consecutive seconds may pass without a new visual or text change.
3. Score each line 0–10 for novelty, stakes and clarity; any line below 6 is a cut candidate.
4. Target 2.8–3.5 words per second for Bangla narration measured from the script duration fields.
5. Keep the final 5 seconds for a loop or call to action; never delete it.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "retention-pacing-optimizer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Move the salary number into the hook",
      "start_sec": 0,
      "end_sec": 2,
      "reason": "hook originally started at 4.2 seconds"
    },
    {
      "id": 2,
      "action": "Trim the greeting line",
      "start_sec": 2,
      "end_sec": 6,
      "reason": "no new information for 4 seconds"
    },
    {
      "id": 3,
      "action": "Add a wallet graphic on the totals line",
      "start_sec": 6,
      "end_sec": 14,
      "reason": "visual change every 4 seconds"
    }
  ],
  "constraints": [
    "hook by 2.5 seconds",
    "Bangla speech rate 2.8-3.5 words/sec",
    "loop kept in final 5 seconds"
  ],
  "summary": "Three timed edits lift the hook forward and add one visual change; total 45 seconds preserved."
}
```

# Quality rules

1. Each item names the exact line number from the source script.
2. The sum of kept durations stays inside the channel length range.
3. No rule hardcodes English; word-rate guidance is written for Bangla.

# Steps

1. Read language and target duration through project-memory, then load `projects/<project>/02-script/latest_script.json`.
2. Validate the draft with `python scripts/schema_validator.py latest_script projects/<project>/02-script/latest_script.json`.
3. Score every scene line on novelty, stakes and clarity using the 0–10 scale.
4. Locate gaps longer than 4 seconds and propose a visual change or a trim for each one.
5. Write the timed edit list to `projects/<project>/02-script/retention-pacing-optimizer.json`.
6. Re-check the total runtime and validate the file against `config/schemas/plan.json`.

# How to test

- Run `python scripts/schema_validator.py plan projects/_template/02-script/retention-pacing-optimizer.json` after a real run, then `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

script-writer -> final-test

# Failure handling

If the script has no duration fields, return WARN and ask for timings instead of guessing a word rate. On schema failure, stop and name the invalid scene index.
