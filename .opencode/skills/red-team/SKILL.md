---
name: red-team
description: Attacks the video to find weaknesses before release.
category: final-test
status: implemented
phase: later
type: prompt-only
batch: A
schema: analysis
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after the final edit and before bug-finder, when you want an adversarial review rather than a friendly check.

# Purpose

Challenge the final video from three hostile angles and return a scored weakness report with the strongest objection stated first.

# Input

- `projects/<project>/08-final-test/final-video.mp4`
- `projects/<project>/02-script/latest_script.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/08-final-test/red-team.json`

- Format `json_utf8`: `projects/<project>/08-final-test/red-team.json`

# Attack criteria

1. Attack exactly three angles: hook, trust and pacing.
2. Score each angle 0–10 where 10 means the video fully resists that attack.
3. Any angle scoring below 6 must have at least one concrete finding.
4. Quote the exact second where the hook first makes sense.
5. Write findings in the project language from project-memory, which is Bangla for this channel.

# Output format (short example)

Schema: `config/schemas/analysis.json`

```json
{
  "status": "PASS",
  "skill": "red-team",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "criteria": [
    {
      "name": "hook",
      "score": 4,
      "evidence": "the money figure appears at 4.2 seconds, after the required 3 seconds"
    },
    {
      "name": "trust",
      "score": 8,
      "evidence": "every number is attributed to a stated saving example"
    },
    {
      "name": "pacing",
      "score": 6,
      "evidence": "one 5-second static stretch at second 20"
    }
  ],
  "findings": [
    "Move the ৳120 figure into the first 2 seconds.",
    "Replace the static stretch with a notebook close-up."
  ],
  "summary": "Hook is the weakest angle at 4/10; two concrete fixes are listed in priority order."
}
```

# Quality rules

1. There are exactly three scored criteria named hook, trust and pacing.
2. Each finding names a time or a script line.
3. Findings use Bangla wording for the Bangla channel without hardcoding the language value.

# Steps

1. Load language and niche through project-memory before reading the video report inputs.
2. Confirm `projects/<project>/08-final-test/final-video.mp4` exists and note its ffprobe duration if available.
3. Attack the hook by checking when the main promise first appears.
4. Attack trust by checking each number against the script's stated source.
5. Attack pacing by listing any static stretch longer than 4 seconds.
6. Write the scored report to `projects/<project>/08-final-test/red-team.json` and validate the analysis schema.

# How to test

- Validate `projects/_template/08-final-test/red-team.json` with the analysis schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/analysis.json` by `tests/test_no_template.py`.

# Depends on / feeds into

video-editing -> bug-finder

# Failure handling

If the final video is missing, report the exact path and stop without a fake critique. If ffprobe is unavailable, mark pacing evidence as unverified instead of inventing timestamps.
