---
name: fact-checker
description: Verifies factual claims used in scripts.
category: research
status: implemented
phase: later
type: prompt-only
batch: B
schema: analysis
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after script-writer and before final-test, when a script contains prices, percentages or income figures that must not be guessed.

# Purpose

Check every number and named claim in a draft Bangla script against local source notes and mark the exact lines that need a citation.

# Input

- `projects/<project>/02-script/latest_script.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/01-research/fact-checker.json`

# Claim criteria

1. Extract every claim containing a digit, a ৳ symbol or a percentage from the script.
2. Score each claim 0–10: 10 only when source-notes.md contains the exact figure.
3. Any claim scoring below 7 must appear in findings with its scene number.
4. Compare Bangla number words with Arabic digits; a mismatch is a FAIL finding.
5. Do not replace an unverified figure with a new number; mark it for removal instead.

# Output format (short example)

Schema: `config/schemas/analysis.json`

```json
{
  "status": "PASS",
  "skill": "fact-checker",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "source_file": "projects/<project>/02-script/inputs/source-notes.md",
  "criteria": [
    {
      "name": "coffee price",
      "score": 9,
      "evidence": "scene 1 ৳120 matches line 4 of source notes"
    },
    {
      "name": "monthly total",
      "score": 4,
      "evidence": "scene 2 ৳3,600 has no note"
    },
    {
      "name": "saving rate",
      "score": 7,
      "evidence": "scene 3 'দশ শতাংশ' matches 10% in notes"
    }
  ],
  "findings": [
    "Scene 2: remove ৳3,600 or add a source note.",
    "Scene 3: keep the Bangla word form as written."
  ],
  "summary": "Three numeric claims checked; one lacks evidence and must be removed before publication."
}
```

# Quality rules

1. The number of scored criteria equals the number of numeric claims found.
2. Every low score has a matching finding with a scene number.
3. No finding introduces a replacement figure.

# Steps

1. Load language from project-memory and confirm Bangla number words are expected.
2. Validate the script with `config/schemas/latest_script.json` before scanning it.
3. Extract claims with digits, ৳ or percent and record their scene numbers.
4. Search source-notes.md for each exact figure and assign the 0–10 score.
5. Write the verification report to projects/<project>/02-script/fact-checker.json.
6. Validate the analysis schema and list every unsupported figure in findings.

# How to test

- Add one ৳ figure to projects/_template/02-script/inputs/source-notes.md and run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/analysis.json` by `tests/test_no_template.py`.

# Depends on / feeds into

draft script -> final-test

# Failure handling

If source-notes.md is missing, report BLOCKED and produce no scores. Never fabricate a citation or a local note line.
