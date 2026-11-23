---
name: handover
description: Packages final files for publishing.
category: final-test
status: implemented
phase: 5
type: script-backed
batch: 8
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when packages final files for publishing for a video in `projects/<project>/`.

# Purpose

Packages final files for publishing.

# Input

- `projects/<project>/08-final-test/final-video.mp4`
- `projects/<project>/07-edit/captions.json`
- `projects/<project>/09-description/description.md`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/10-publish/handover.md`
- `projects/<project>/10-publish/handover-check.json`

# Steps

1. Read `config/channel.json` and `config/style-bible.json` through project-memory so the handover lists the real niche, language and location.
2. Check these three upstream final assets by exact path: `projects/<project>/08-final-test/final-video.mp4`, `projects/<project>/07-edit/captions.json`, `projects/<project>/09-description/description.md`. `handover.md` is this skill's own output, never an input; list every missing upstream path.
3. Validate `projects/<project>/07-edit/captions.json` with `python scripts/schema_validator.py captions projects/<project>/07-edit/captions.json`. Run `python scripts/skill_tools.py handover run` with `PROJECT=<project>`; the helper writes both `handover-check.json` and `handover.md`.
4. The helper writes `projects/<project>/10-publish/handover.md` with an asset checklist with PASS/MISSING, the exact publish path, and the real niche/language/audience from project-memory. Do not invent a duration that is not in captions.
5. Re-open both `handover.md` and `handover-check.json`; confirm `ready` matches the checklist and the file list is identical. If any asset is missing, exit NON-ZERO so the pipeline cannot report success; log the problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Acceptance criteria**
- `handover.md` and `handover-check.json` both exist under `projects/<project>/10-publish/`.
- Every checked asset appears with its exact relative path and a PASS or MISSING status.
- Captions pass `config/schemas/captions.json` and the duration is copied from that file.
- `ready` is true only when all three upstream assets are present; otherwise the command exits non-zero.

**Output format (short example)**
```markdown
# Handover — my-video
Niche: Personal finance / side hustles | Language: bn

## Assets
- PASS projects/my-video/08-final-test/final-video.mp4
- PASS projects/my-video/07-edit/captions.json
- PASS projects/my-video/09-description/description.md

## Publish
Path: projects/my-video/08-final-test/final-video.mp4
Ready: yes
```

**Quality rules**
1. Never mark an asset PASS without checking the file on disk.
2. Report `BLOCKED` items separately from FAIL so a blocked render is not called a broken video.
3. Keep the publish path relative to the repository root; no absolute paths.

# How to test

- `python scripts/skill_tools.py handover run` → exits 0 with `ready: true` only when all three upstream assets exist; otherwise exits 1 and still writes `projects/<project>/10-publish/handover.md` and `projects/<project>/10-publish/handover-check.json` listing the missing paths.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

final-test -> publish stage

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
