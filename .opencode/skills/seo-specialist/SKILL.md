---
name: seo-specialist
description: Optimizes keywords and metadata.
category: marketing
status: implemented
phase: later
type: prompt-only
batch: D
schema: analysis
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after description-maker and before growth, when the title and description exist but keyword placement is still guesswork.

# Purpose

Score the description's keyword choices against local search notes and return the three concrete metadata edits with the highest expected payoff.

# Input

- `projects/<project>/09-description/description.md`
- `research/keyword-notes.md` (manual notes, no API)
- `config/channel.json` language
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `SEO metadata`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Keyword criteria

1. Score exactly three dimensions: title match, first-line match and Bangla spelling.
2. A dimension scores 10 only when the keyword from keyword-notes.md appears verbatim.
3. Require the main keyword in the first 60 characters of the description.
4. Reject any English keyword that displaces an equivalent Bangla term.
5. Every finding must quote the exact phrase to add or move.

# Output format (short example)

Schema: `config/schemas/analysis.json`

```json
{
  "status": "PASS",
  "skill": "seo-specialist",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "source_file": "research/keyword-notes.md",
  "criteria": [
    {
      "name": "title match",
      "score": 8,
      "evidence": "সাইড হুস্টল appears in the title"
    },
    {
      "name": "first-line match",
      "score": 4,
      "evidence": "keyword first appears at character 91"
    },
    {
      "name": "Bangla spelling",
      "score": 9,
      "evidence": "spelling matches the manual note"
    }
  ],
  "findings": [
    "Move 'সাইড হুস্টল' into the first 60 characters.",
    "Do not replace it with the English word 'side hustle'."
  ],
  "summary": "Three keyword dimensions scored; first-line placement is the single metadata fix needed."
}
```

# Quality rules

1. There are exactly three scored criteria with the required names.
2. Each finding quotes a phrase from the manual notes.
3. No suggested keyword is written only in Latin script.

# Steps

1. Read language through project-memory and open research/keyword-notes.md.
2. Load the generated description and measure where the main keyword first appears.
3. Score title match, first-line match and Bangla spelling on the 0–10 scale.
4. Write each metadata fix as a finding that quotes the exact phrase.
5. Save the review to projects/<project>/09-description/seo-specialist.json.
6. Validate the analysis schema and confirm no finding invents a keyword.

# How to test

- Add one Bangla keyword to research/keyword-notes.md, run the skill, then `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/analysis.json` by `tests/test_no_template.py`.

# Depends on / feeds into

description-maker -> growth stage

# Failure handling

If keyword-notes.md is missing, report BLOCKED and produce no scores. Never query a search API or invent search volume for this skill.
