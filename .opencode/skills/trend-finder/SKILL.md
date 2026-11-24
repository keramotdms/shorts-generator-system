---
name: trend-finder
description: Finds location-based YouTube and Facebook trends from free sources.
category: research
status: implemented
phase: 1
type: script-backed
batch: 2
schema: trend-report
---

> Context is always loaded via project-memory; generated research lives under `research/` and per-project work stays in `projects/<project>/`.

# When to use

Use when you need current, location-based topic signals before `story-thinker` chooses a story angle.

# Purpose

Collect free trend signals from YouTube, Google Trends, YouTube autosuggest and user exports, merge them, and write a transparent scored report. No source is called with a paid API and no missing metric is invented.

# Input

- `config/channel.json`
- `research/trend-inputs/`
- `research/trend-cache/`
- `YOUTUBE_API_KEY` in `.env` (never commit the key; `.env.example` contains only the empty placeholder)
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `research/trend-cache/trend-report.json`
- `research/trend-cache/quota-log.jsonl` (one line per YouTube API call; no key is written)

- Format `json_utf8`: `research/trend-cache/trend-report.json`

# Steps

1. Read `config/channel.json` through project-memory. Use `niche` for filtering and search seeds, `language` for autosuggest language, and `audience_location` for the region code (`BD` for Bangladesh).
2. Build exactly 5 niche search keywords from the configured niche. Do not use a fixed topic list.
3. Read `YOUTUBE_API_KEY` from `.env` and request the YouTube Data API v3 `videos.list` endpoint with `chart=mostPopular`, `regionCode=BD` and `part=snippet,statistics`. Keep only videos whose title, description or tags match the niche tokens. Record 1 quota unit and append it to `research/trend-cache/quota-log.jsonl`.
4. Request YouTube search autosuggest for each of the 5 niche keywords. This endpoint needs no API key. Keep at most 3 suggestions per seed.
5. Try Google Trends through `pytrends` for the same 5 keywords. This source is optional: if the package is missing or the request fails, write a `warn` source status and continue.
6. Read every CSV, JSON, Markdown and text export in `research/trend-inputs/`, including YouTube Studio Research CSV, Facebook notes and vidIQ notes. Merge rows by keyword and keep the strongest score and confidence.
7. Write `research/trend-cache/trend-report.json` with `source`, `date`, `keyword`, `score` (0-100), `confidence` (0-1) and per-source status. If a source is unavailable, put that exact fact in `sources` and `warnings`; never replace it with a made-up trend. Validate the file with `python scripts/schema_validator.py trend-report research/trend-cache/trend-report.json`.

**Acceptance criteria**
- The report contains exactly 5 `keywords`, copied or derived from the configured niche.
- Every `trends[]` item has `source`, `date`, `keyword`, `score` (0-100) and `confidence` (0-1).
- At least one `sources[]` entry explains each unavailable or failed source; no fabricated values appear.
- YouTube quota use is recorded in `quota` and appended to `research/trend-cache/quota-log.jsonl` when the API is called.
- The report passes `config/schemas/trend-report.json` and `research/trend-cache/trend-report.json` exists.

**Output format (short example)**
```json
{
  "region": "Bangladesh / Bangla-speaking",
  "generated_on": "2026-11-23",
  "niche": "Personal finance / side hustles",
  "language": "bn",
  "keywords": ["personal finance", "side hustles", "personal finance ideas", "side hustles ideas", "personal finance tips"],
  "source_files": ["research/trend-inputs/studio-research.csv"],
  "sources": [
    {"name": "youtube-most-popular", "status": "ok", "detail": "4 niche-matched items from mostPopular", "items": 4},
    {"name": "google-trends", "status": "warn", "detail": "pytrends not installed; optional source skipped", "items": 0},
    {"name": "youtube-autosuggest", "status": "ok", "detail": "12 suggestions from 5 niche keywords", "items": 12},
    {"name": "manual-inputs", "status": "ok", "detail": "3 rows merged from 1 manual file", "items": 3}
  ],
  "trends": [
    {
      "source": "youtube-most-popular",
      "sources": ["youtube-most-popular", "manual:studio-research.csv"],
      "date": "2026-11-20",
      "keyword": "low-cost side hustle for students",
      "score": 88.5,
      "confidence": 0.93,
      "platform": "youtube-shorts",
      "signals": {"views": 120000, "rank": 1},
      "source_file": "youtube-api:mostPopular?regionCode=BD"
    }
  ],
  "warnings": ["google-trends: pytrends not installed; optional source skipped"],
  "quota": {"youtube_units": 1, "autosuggest_units": 0, "google_trends_units": 0, "total_units": 1, "log_file": "research/trend-cache/quota-log.jsonl"},
  "status": "WARN"
}
```

**Quality rules**
1. Never invent views, search volume, rank, date or a trend. Copy the value from the cited API response or manual file.
2. Keep the key secret: never print `YOUTUBE_API_KEY`, never put it in `trend-report.json`, and never commit `.env`.
3. Treat `pytrends` as optional. A missing package is a `warn` status, not a failed pipeline.
4. Keep only the configured region and niche. Drop unrelated trending videos instead of relabelling them.
5. Keep the report useful when a source is down: write the source status and continue with the other free sources.

# How to test

- `python scripts/skill_tools.py trend-finder --self-test` → runs with fake YouTube, autosuggest and pytrends responses; expected `PASS trend-finder: ...`.
- Put a YouTube Studio Research CSV, Facebook notes or vidIQ notes in `research/trend-inputs/`, then run `python scripts/skill_tools.py trend-finder run`; inspect `research/trend-cache/trend-report.json` and `research/trend-cache/quota-log.jsonl`.
- Checklist: context came from project-memory; 5 niche keywords exist; every item has source/date/keyword/score/confidence; unavailable sources are named; no key appears anywhere in the report.

# Depends on / feeds into

channel config -> story-thinker

# Failure handling

If `config/channel.json` is missing or invalid, stop and report the exact path. If `YOUTUBE_API_KEY` is absent, write `youtube-most-popular` as `unavailable`, continue with autosuggest/manual inputs, and do not fabricate YouTube rows. If `pytrends` is absent or fails, write `google-trends` as `warn`, continue, and log the reason via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`. If no source returns data, still write a valid report with an empty `trends` list, `status: WARN`, and the exact source reasons. Never change Windows settings or install a package without user approval.
