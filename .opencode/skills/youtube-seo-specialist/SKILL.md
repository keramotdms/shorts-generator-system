---
name: youtube-seo-specialist
description: Optimizes for YouTube search and Shorts.
category: growth
status: implemented
phase: later
type: prompt-only
batch: D
schema: manual-input
api_needed: later
data_source: manual-file
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after seo-specialist and before publishing, when a keyword export exists in 10-publish/inputs/ and the title needs a final choice.

# Purpose

Rank manually exported keywords for a Bangla Short and choose the one phrase that should lead the title and first caption line.

# Input

- `projects/<project>/10-publish/inputs/`
- `projects/<project>/09-description/description.md`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/10-publish/youtube-seo-specialist.json`

- Format `json_utf8`: `projects/<project>/10-publish/youtube-seo-specialist.json`

# Keyword ranking rules

1. Require at least 5 exported keywords before choosing a leader.
2. Score each keyword as volume divided by competition, capped at 10.
3. Prefer Bangla-script keywords when two candidates tie.
4. Reject any keyword that does not appear in the script or description.
5. Never invent search volume or query a search API.

# Output format (short example)

Schema: `config/schemas/manual-input.json`

```json
{
  "status": "PASS",
  "skill": "youtube-seo-specialist",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "api_needed": "later",
  "source_file": "projects/<project>/10-publish/inputs/keyword-export.json",
  "rows": [
    {
      "keyword": "সাইড হুস্টল",
      "volume": 1200,
      "competition": 150,
      "score": 8
    },
    {
      "keyword": "টাকা বাঁচানো",
      "volume": 900,
      "competition": 120,
      "score": 7.5
    }
  ],
  "summary": "Five manual keywords ranked; 'সাইড হুস্টল' leads the title and the first Bangla caption line."
}
```

# Quality rules

1. Every score equals volume divided by competition, capped at 10.
2. The leading keyword appears in the description file.
3. No row contains a keyword absent from the manual export.

# Steps

1. Check projects/<project>/10-publish/inputs/keyword-export.json exists before reading the description.
2. Count rows and stop with WARN when fewer than five keywords are exported.
3. Compute each score from volume and competition using exported numbers only.
4. Filter out keywords missing from the script or description, then pick the top scorer.
5. Write the ranking to projects/<project>/10-publish/youtube-seo-specialist.json.
6. Validate the manual-input schema and confirm api_needed is set to later.

# How to test

- Export five sample keywords under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/manual-input.json` by `tests/test_no_template.py`.

# Depends on / feeds into

description-maker -> publish stage

# Failure handling

If the keyword export is missing, report the exact path and stop. Never fabricate a search volume, a competition score, or an API result.
