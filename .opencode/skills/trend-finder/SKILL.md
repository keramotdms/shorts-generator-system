---
name: trend-finder
description: Finds location-based YouTube and Facebook trends.
category: research
status: implemented
phase: 1
type: prompt-only
batch: 2
schema: trend-report
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when finds location-based youtube and facebook trends for a video in `projects/<project>/`.

# Purpose

Finds location-based YouTube and Facebook trends.

# Input

- `config/channel.json`
- `projects/<project>/01-research/trend-cache/`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/01-research/trend-report.json`

# Steps

1. Read `config/channel.json` and `config/style-bible.json` through project-memory. Use `audience_location` as the filtering region; do not assume a global trend applies to Bangladesh.
2. Look for source data inside `projects/<project>/01-research/trend-cache/` (user-supplied CSV/JSON exports or an earlier run). Create that folder if it does not exist. If there is no source file, ask the user to drop an export there and stop; do not install or call a paid API.
3. For each source row keep only items where the topic maps to the channel niche and the region from `config/channel.json`. Record `platform` (`youtube-shorts` or `facebook-reels`), `topic`, `signals` (views/shares or rank), `observed_on`, and `source_file`.
4. Score every kept item 1-5 for freshness, local relevance, and reuse as a 30-60 s Short. Sort by the total and keep at most 10 items.
5. Write the result to `projects/<project>/01-research/trend-report.json`; create `projects/<project>/01-research/` first. Re-open it, confirm it parses and is non-empty, and log problems via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Acceptance criteria**
- `projects/<project>/01-research/trend-report.json` exists under the current project and parses.
- Every entry has `platform`, `topic`, `signals`, `observed_on`, `source_file`, and 3 scores.
- Every entry cites a real file inside `projects/<project>/01-research/trend-cache/`.
- No entry is older than 30 days from `observed_on`.

**Output format (short example)**
```json
{
  "region": "Bangladesh / Bangla-speaking",
  "source_files": ["projects/<project>/01-research/trend-cache/youtube-export.csv"],
  "trends": [
    {"platform": "youtube-shorts", "topic": "low-cost side hustle",
     "signals": {"views": 120000}, "observed_on": "2026-11-20",
     "source_file": "projects/<project>/01-research/trend-cache/youtube-export.csv",
     "scores": {"freshness": 5, "local": 5, "reuse": 4}}
  ]
}
```

**Quality rules**
1. Never guess a view count or rank; copy it from a cited source file.
2. Drop any trend that cannot be shown in a vertical 9:16 frame.
3. Keep `region` copied from `config/channel.json`, not rewritten by hand.

# How to test

- Type: `Use the trend-finder skill with PROJECT=<project>`. Expected: `projects/<project>/01-research/trend-report.json` exists, parses cleanly, and contains no hardcoded niche or language value.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

channel config -> story-thinker

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
