---
name: story-organizer
description: Turns story beats into timed 9:16 scenes with one job each.
category: script
status: implemented
phase: later
type: prompt-only
batch: A
schema: plan
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after story-thinker when the concept exists but nobody has decided which beat goes where or how many seconds each beat gets.

# Purpose

Convert a loose story concept into a timed beat sheet where every scene has a single job and fits the 30–60 second Short format.

# Input

- - `projects/<project>/02-script/story.json`
- - `config/channel.json` video length range
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `organized story beats`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Beat timing criteria

1. Use at most 4 beats for a 30-second video and at most 6 beats for a 60-second video.
2. Give each beat 5–12 seconds; no beat may be shorter than 5 seconds.
3. Assign exactly one job per beat: hook, problem, turn, payoff or closure.
4. Sum every `start_sec`/`end_sec` pair to the channel's 30–60 second target.
5. Describe each beat with one visual idea that the SVG scene builder can draw with flat shapes.

# Output format (short example)

Schema: `config/schemas/plan.json`

```json
{
  "status": "PASS",
  "skill": "story-organizer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "items": [
    {
      "id": 1,
      "action": "Coffee price joke",
      "start_sec": 0,
      "end_sec": 7,
      "reason": "hook in the first 3 seconds"
    },
    {
      "id": 2,
      "action": "Monthly total appears",
      "start_sec": 7,
      "end_sec": 18,
      "reason": "raise the money problem"
    },
    {
      "id": 3,
      "action": "Side hustle notebook",
      "start_sec": 18,
      "end_sec": 34,
      "reason": "show the turn"
    },
    {
      "id": 4,
      "action": "First ৳500 saved",
      "start_sec": 34,
      "end_sec": 45,
      "reason": "payoff and loop back"
    }
  ],
  "constraints": [
    "flat 2D shapes only",
    "Bangla narration",
    "vertical 9:16"
  ],
  "summary": "Four beats totalling 45 seconds, each with one visual job."
}
```

# Quality rules

1. Every item has a unique id and both timing fields present.
2. No beat duration is under 5 or over 12 seconds.
3. The constraints include the language read from project-memory, never a hardcoded language word.

# Steps

1. Load niche, language and the 30–60 second range through project-memory before reading the story file.
2. Validate `projects/<project>/02-script/story.json` against `config/schemas/story.json` and stop on any schema error.
3. Rebuild the beat list from `story.json`, giving each beat one job and a 5–12 second window.
4. Check the total against the channel video-length range; merge or split beats until it fits.
5. Write the timed plan to `projects/<project>/02-script/story-organizer.json` with status and project metadata.
6. Validate the written file against `config/schemas/plan.json` and log any failure via error-log-keeper.

# How to test

- Run `python tests/test_skills.py --batch 3` then `python tests/test_no_template.py`; expect this skill absent from the template list.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/plan.json` by `tests/test_no_template.py`.

# Depends on / feeds into

story-thinker -> hook-writer

# Failure handling

If the story file is missing or fails its schema, stop without writing a beat sheet and report the exact path. If the beats cannot fit 30–60 seconds, return a WARN with the overrun in seconds instead of inventing timings.
