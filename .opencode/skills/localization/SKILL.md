---
name: localization
description: Adapts the script for other languages and regions.
category: script
status: implemented
phase: later
type: prompt-only
batch: B
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after the script is locked and before voiceover-organizer, when the same Short must serve a second Bangla-speaking region.

# Purpose

Rewrite an approved Bangla script for one target region while preserving every money figure, timing and loop line.

# Input

- projects/<project>/02-script/latest_script.json
- config/channel.json default language and region
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `localized script`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Localization rules

1. Preserve all ৳ amounts and Arabic digits exactly; never convert currency.
2. Keep the target language in the constraints from project-memory, not a hardcoded value.
3. Each localized line must fit the original scene duration within 0.5 seconds.
4. Change at most 3 region-specific words per scene to avoid rewriting the story.
5. The final loop line must remain the last item with the same wording as the source.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "localization",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Replace 'মেসে খাওয়া' with a regional food word",
      "start_sec": 0,
      "end_sec": 6,
      "reason": "one region word changed in scene 1"
    },
    {
      "id": 2,
      "action": "Keep '৳120' unchanged in the hook",
      "start_sec": 6,
      "end_sec": 14,
      "reason": "currency preservation rule"
    },
    {
      "id": 3,
      "action": "Repeat the source loop line verbatim",
      "start_sec": 38,
      "end_sec": 45,
      "reason": "loop line protected from edits"
    }
  ],
  "constraints": [
    "Bangla source",
    "regional variant: Sylheti-friendly wording",
    "preserve ৳ amounts"
  ],
  "summary": "Three scene-level localization edits preserve figures, timings and the final loop line."
}
```

# Quality rules

1. Each action names the exact scene it changes.
2. No action contains a dollar sign or a converted price.
3. The loop line item is last and uses the same timing as the source.

# Steps

1. Read source language and target region from project-memory, then load the validated script.
2. List every ৳ amount and mark those lines as locked from translation.
3. Rewrite at most three region words per scene inside the original time window.
4. Copy the final loop line unchanged and confirm it remains last.
5. Write the localized plan to projects/<project>/02-script/localization.json.
6. Validate against the plan schema and diff the figures against the source.

# How to test

- Validate projects/_template/02-script/localization.json with the plan schema, then run `python tests/test_no_template.py`.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

script-writer -> voice stage

# Failure handling

If the target region is missing from channel config, stop and ask for it. If a line cannot fit its duration, keep the source line and add a WARN rather than speeding up the voice.
