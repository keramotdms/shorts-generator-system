---
name: variant-batch-renderer
description: Renders multiple variants in batch.
category: video-editing
subcategory: automation-export
status: implemented
phase: later
type: script-backed
batch: C
schema: media-effect
requires: ffmpeg
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use after template-preset-manager and before ab-tester, when three visual variants must exist from the same source video.

# Purpose

Render three hue-shifted copies of one clip in a single FFmpeg run so title and thumbnail tests can compare visual variants cheaply.

# Input

- `projects/<project>/07-edit/rough-cut.mp4`
- `config/style-bible.json` palette
- `config/presets/*.json` active presets
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `batch rendered videos`
- `status`, `skill`, `project` and `generated_at` are written into the JSON output

# Variant parameters

1. Produce exactly three outputs named with -v1, -v2 and -v3 suffixes.
2. Use hue 0 for the first copy and plus or minus 10 degrees per palette colour for the others.
3. Split the input once and map each filtered branch to its own output file.
4. Drop audio from all variants to keep the test focused on visuals.
5. Probe every output with ffprobe and require identical configured resolution.

# Output format (short example)

Schema: `config/schemas/media-effect.json`

```json
{
  "status": "PASS",
  "skill": "variant-batch-renderer",
  "project": "_template",
  "generated_at": "2026-11-23T10:00:00Z",
  "language": "bn",
  "video": "projects/<project>/07-edit/variant-batch-renderer-v1.mp4",
  "duration_sec": 3.0,
  "width": 1080,
  "height": 1920,
  "has_audio": false,
  "parameters": {
    "variant_count": 3,
    "hue_step_deg": 40,
    "suffixes": [
      "v1",
      "v2",
      "v3"
    ],
    "palette_count": 4
  },
  "summary": "Three silent variants rendered with hue 0, +40 and -40 degrees from a four-colour palette."
}
```

# Quality rules

1. Report parameters list three suffixes and a hue step derived from palette count.
2. Every variant path exists after the run.
3. All probed resolutions equal config/defaults.json resolution.

# Steps

1. Read the palette count and resolution through project-memory before choosing hue offsets.
2. Check ffmpeg availability and emit BLOCKED if the executable is missing.
3. Build a three-way split with a hue filter on each branch.
4. Map each branch to a separate output with libx264 veryfast and no audio.
5. Probe all three files and collect their durations and dimensions.
6. Write projects/<project>/07-edit/variant-batch-renderer.json and validate the media-effect schema.

# How to test

- `python scripts/skill_tools.py variant-batch-renderer --self-test` renders three variants and probes each with ffprobe.
- Run `python tests/test_no_template.py` and confirm this skill is not listed.
- The filled example above is validated against `config/schemas/media-effect.json` by `tests/test_no_template.py`.

# Depends on / feeds into

template-preset-manager -> growth stage

# Failure handling

If fewer than three presets are active, render the neutral variant only and write a WARN listing the missing presets. Do not reuse another project's presets.
