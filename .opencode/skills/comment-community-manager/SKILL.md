---
name: comment-community-manager
description: Manages comments and community replies.
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

Use after a video is published and its comments have been exported to 10-publish/inputs/, before the next research round.

# Purpose

Sort a manual comment export into questions, praise and objections, then draft Bangla replies for the questions and objections only.

# Input

- `projects/<project>/10-publish/inputs/`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/10-publish/comment-community-manager.json`

- Format `json_utf8`: `projects/<project>/10-publish/comment-community-manager.json`

# Reply rules

1. Require at least 5 exported comments before drafting any reply.
2. Classify every row as question, praise or objection.
3. Draft replies only for questions and objections.
4. Write each reply in Bangla and keep it under 120 characters.
5. Never promise a personal finance outcome or ask for private financial details.

# Output format (short example)

Schema: `config/schemas/manual-input.json`

```json
{
  "status": "PASS",
  "skill": "comment-community-manager",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "api_needed": "later",
  "source_file": "projects/<project>/10-publish/inputs/comments-export.json",
  "rows": [
    {
      "id": 1,
      "text": "এই টাকা কীভাবে বাঁচাব?",
      "type": "question",
      "reply": "প্রতিদিন ২০ টাকা আলাদা রাখুন, তারপর মাসে যোগ করুন।"
    },
    {
      "id": 2,
      "text": "ভালো ভিডিও",
      "type": "praise",
      "reply": ""
    }
  ],
  "summary": "Two exported comments sorted; one Bangla reply drafted for the question, praise left unanswered by design."
}
```

# Quality rules

1. Every row has exactly one of the three allowed types.
2. Praise rows have an empty reply string.
3. All drafted replies are under 120 characters and written in Bangla.

# Steps

1. Confirm projects/<project>/10-publish/inputs/comments-export.json exists and read the tone from project-memory.
2. Validate that every exported row has text and an id.
3. Label each row as question, praise or objection.
4. Draft short Bangla replies for non-praise rows and leave praise replies empty.
5. Write the reply set to projects/<project>/10-publish/comment-community-manager.json.
6. Validate the manual-input schema and check reply character counts.

# How to test

- Export five sample comments under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/manual-input.json` by `tests/test_no_template.py`.

# Depends on / feeds into

published video -> research stage

# Failure handling

If the export is missing, report the path and stop. Never invent a viewer comment or reply as if it came from a real user.
