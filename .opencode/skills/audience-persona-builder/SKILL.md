---
name: audience-persona-builder
description: Builds a clear viewer persona.
category: research
status: implemented
phase: later
type: prompt-only
batch: B
schema: selection
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after book-finder and trend-finder, before hook-writer, when the niche report exists but nobody has defined who the Short is for.

# Purpose

Pick one primary Bangla-speaking viewer from three researched candidates so hooks and examples can be written for a real person instead of a vague audience.

# Input

- `projects/<project>/01-research/niche-report.md`
- `config/channel.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/01-research/audience-persona-builder.json`

# Persona shortlist criteria

1. Draft exactly three candidate viewers and choose exactly one primary persona.
2. Score each 0–10 for finance pain, phone access and likelihood to watch a 45-second Short.
3. The winner must score at least 7 on finance pain and at least 7 on phone access.
4. State monthly income in Bangla taka; do not use dollars or invented currencies.
5. Give each candidate a stable id such as `viewer-01` and keep it for later research files.

# Output format (short example)

Schema: `config/schemas/selection.json`

```json
{
  "status": "PASS",
  "skill": "audience-persona-builder",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "candidates": [
    {
      "id": "viewer-01",
      "score": 9,
      "reason": "Dhaka delivery rider, ৳28k/month, saves on a phone"
    },
    {
      "id": "viewer-02",
      "score": 6,
      "reason": "student with low income but limited data for video"
    },
    {
      "id": "viewer-03",
      "score": 7,
      "reason": "office worker, ৳55k/month, already follows finance pages"
    }
  ],
  "chosen_id": "viewer-01",
  "rationale": "Highest combined score: clear ৳28k/month pain and daily phone access suit a Bangla 45-second Short."
}
```

# Quality rules

1. There are three candidates and the chosen id is one of them.
2. Every reason contains a taka amount written with the ৳ symbol.
3. Scores stay within 0–10 and the winner passes both minimum thresholds.

# Steps

1. Open project-memory first and copy the language and region values into the persona constraints.
2. Read `projects/<project>/01-research/niche-report.md` and `research/trend-cache/trend-report.json` without calling any external API.
3. Write three short viewer sketches with a taka income, a device and one money worry.
4. Score the sketches against the three numeric thresholds above and select the top passing one.
5. Save the shortlist to projects/<project>/01-research/audience-persona-builder.json.
6. Run the selection schema validator and confirm the chosen id appears in the candidate list.

# How to test

- Run `python tests/test_no_template.py` and `python tests/test_skills.py`; neither may list this skill as a template.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/selection.json` by `tests/test_no_template.py`.

# Depends on / feeds into

research outputs -> hook-writer

# Failure handling

If no niche report exists, stop and name the missing file rather than inventing a viewer. If no candidate passes both 7-point thresholds, return WARN with the best score and ask for more research.
