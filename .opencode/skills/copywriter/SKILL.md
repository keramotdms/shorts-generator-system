---
name: copywriter
description: Writes marketing copy for the video.
category: marketing
status: implemented
phase: later
type: prompt-only
batch: D
schema: selection
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after final-test and before description-maker, when the video is approved but the supporting words are still missing.

# Purpose

Choose one Bangla copy angle for the Short and produce the one-line pitch, description opening and hashtag set that match the audience persona.

# Input

- `projects/<project>/02-script/latest_script.json`
- `projects/<project>/01-research/audience-persona-builder.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/09-description/copywriter.md`

- Format `markdown`: `projects/<project>/09-description/copywriter.md`

# Copy angle scoring

1. Draft exactly three angles and pick one.
2. Score each 0–10 for persona fit, clarity of money benefit and Bangla naturalness.
3. Keep the pitch line under 60 Bangla characters.
4. Use at most three hashtags, all written in Bangla.
5. Never promise a guaranteed income or use words implying get-rich-quick results.

# Output format (short example)

Schema: `config/schemas/selection.json`

```json
{
  "status": "PASS",
  "skill": "copywriter",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "candidates": [
    {
      "id": "angle-01",
      "score": 9,
      "reason": "one coffee equals ৳120, under 60 characters"
    },
    {
      "id": "angle-02",
      "score": 6,
      "reason": "too vague about the saving benefit"
    },
    {
      "id": "angle-03",
      "score": 7,
      "reason": "good benefit but over 60 characters"
    }
  ],
  "chosen_id": "angle-01",
  "rationale": "Highest persona fit and clarity; pitch stays under 60 Bangla characters with three Bangla hashtags."
}
```

# Quality rules

1. There are three candidates and one chosen id from that list.
2. No rationale contains an income guarantee.
3. All hashtag examples are written in Bangla script.

# Steps

1. Read tone and language from project-memory before opening the persona shortlist.
2. Validate the final script and extract its single money benefit.
3. Draft three short Bangla angles and score them against the numeric rules.
4. Select the winner and write a pitch line, description opening and three hashtags.
5. Save the copy choice to projects/<project>/09-description/copywriter.json.
6. Validate the selection schema and count the pitch characters.

# How to test

- Validate projects/_template/09-description/copywriter.json with the selection schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/selection.json` by `tests/test_no_template.py`.

# Depends on / feeds into

final-test -> description-maker

# Failure handling

If the persona shortlist is missing, report the path and stop. If no angle reaches 7 points, return WARN with the best angle instead of inventing a stronger claim.
