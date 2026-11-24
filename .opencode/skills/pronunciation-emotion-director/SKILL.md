---
name: pronunciation-emotion-director
description: Adds Bangla pronunciation and emotion cues per line.
category: voice
status: implemented
phase: later
type: prompt-only
batch: A
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after voiceover-organizer and before voiceover-generator when numbers, loanwords or emotionally flat lines need reading notes.

# Purpose

Attach pronunciation, emphasis and emotion notes to every spoken line so the voiceover sounds natural in Bangla.

# Input

- `projects/<project>/03-voice/voiceover-organizer.json`
- `projects/<project>/02-script/latest_script.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/03-voice/pronunciation-emotion-director.json`

- Format `json_utf8`: `projects/<project>/03-voice/pronunciation-emotion-director.json`

# Delivery criteria

1. Write every pronunciation note in Bangla script for Bangla lines; use Latin only for brand names.
2. Spell out currency and numbers as words, for example ৳120 as 'একশ কুড়ি টাকা'.
3. Assign exactly one emotion per line from: calm, curious, worried, hopeful.
4. Mark at most one emphasized word per sentence to avoid a shouty delivery.
5. Keep the emotion of the final line consistent with the loop plan.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "pronunciation-emotion-director",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Read ৳120 as একশ কুড়ি টাকা",
      "start_sec": 0,
      "end_sec": 6,
      "reason": "number would otherwise be mispronounced"
    },
    {
      "id": 2,
      "action": "Emotion worried on the debt line",
      "start_sec": 6,
      "end_sec": 18,
      "reason": "sets up the problem"
    },
    {
      "id": 3,
      "action": "Emotion hopeful on the saving line",
      "start_sec": 38,
      "end_sec": 45,
      "reason": "matches the loop ending"
    }
  ],
  "constraints": [
    "Bangla script for pronunciation",
    "one emotion per line",
    "one emphasized word maximum"
  ],
  "summary": "Three delivery notes cover number reading, a worried turn and a hopeful loop line."
}
```

# Quality rules

1. Every `action` string contains either a Bangla word or an allowed brand name.
2. No line carries two emotion labels.
3. The plan uses the same scene ids as the voice plan.

# Steps

1. Load language from project-memory and confirm it is Bangla before writing Bangla script notes.
2. Open `projects/<project>/03-voice/voiceover-organizer.json` and the validated script.
3. Rewrite every number and currency amount as spoken Bangla words.
4. Choose one emotion from the allowed four and one emphasis word per sentence.
5. Write the delivery notes to `projects/<project>/03-voice/pronunciation-emotion-director.json`.
6. Validate against `config/schemas/plan.json` and flag any line with two emotions.

# How to test

- Run `python tests/test_skills.py --batch 4`, then validate `projects/_template/03-voice/pronunciation-emotion-director.json` with the plan schema.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

voice plan -> voiceover-generator

# Failure handling

If the script language is not Bangla, stop and report that this skill only covers Bangla delivery. Never transliterate Bangla lines into Latin text.
