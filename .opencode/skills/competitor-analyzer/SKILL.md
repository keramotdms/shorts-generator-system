---
name: competitor-analyzer
description: Analyzes competing channels and formats.
category: research
status: implemented
phase: later
type: prompt-only
batch: B
schema: analysis
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after audience-persona-builder and before story-thinker, when manual notes about competitor videos have been collected in research/competitor-notes.md.

# Purpose

Compare three locally noted competitor Shorts against our own format and return the single format gap worth copying next.

# Input

- `projects/<project>/01-research/niche-report.md`
- `config/channel.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/01-research/competitor-analyzer.json`

- Format `json_utf8`: `projects/<project>/01-research/competitor-analyzer.json`

# Comparison criteria

1. Score each competitor 0–10 for hook clarity, number specificity and Bangla naturalness.
2. Compare only Shorts between 30 and 60 seconds; longer videos are excluded with a reason.
3. Require at least three noted competitors; two or fewer is a WARN.
4. Name the single lowest-scoring dimension of our own format as the gap to copy.
5. Never invent view counts; cite only numbers written in the manual notes.

# Output format (short example)

Schema: `config/schemas/analysis.json`

```json
{
  "status": "PASS",
  "skill": "competitor-analyzer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "source_file": "research/competitor-notes.md",
  "criteria": [
    {
      "name": "hook clarity",
      "score": 8,
      "evidence": "competitor A shows the salary in second 1"
    },
    {
      "name": "number specificity",
      "score": 6,
      "evidence": "only two of three notes include taka amounts"
    },
    {
      "name": "Bangla naturalness",
      "score": 9,
      "evidence": "all hooks use spoken Bangla, not translated English"
    }
  ],
  "findings": [
    "Our hook waits 4 seconds while competitor A pays off in 1.",
    "Add one taka figure to the first line."
  ],
  "summary": "Three manual competitor notes reviewed; number specificity is the format gap to copy next."
}
```

# Quality rules

1. Each criterion has a 0–10 score and an evidence string from the notes.
2. Findings reference a named competitor or a specific second.
3. No view count appears unless the manual notes contain it.

# Steps

1. Load the 30–60 second limit and language from project-memory before opening the notes.
2. Read research/competitor-notes.md and discard entries outside the length limit.
3. Score the remaining entries on hook clarity, number specificity and Bangla naturalness.
4. Compare the averages to our current style bible format and name one gap.
5. Write the report to projects/<project>/01-research/competitor-analyzer.json.
6. Validate the analysis schema and confirm every score cites a note.

# How to test

- Write three lines to research/competitor-notes.md, run the skill, then `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/analysis.json` by `tests/test_no_template.py`.

# Depends on / feeds into

niche report -> story-thinker

# Failure handling

If the manual notes file is missing, report the exact path and stop. If fewer than three eligible Shorts exist, write WARN with the count instead of pretending a full comparison.
