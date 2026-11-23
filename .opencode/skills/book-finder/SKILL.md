---
name: book-finder
description: Finds niche and topic ideas for the channel.
category: research
status: implemented
phase: 1
type: prompt-only
batch: 2
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when finds niche and topic ideas for the channel for a video in `projects/<project>/`.

# Purpose

Finds niche and topic ideas for the channel.

# Input

- `config/channel.json`
- Context is read through project-memory from `config/channel.json` and `config/style-bible.json`; nothing niche/language/style is hardcoded.
- `PROJECT` environment variable (defaults to `_template`).

# Output

- `projects/<project>/01-research/niche-report.md`

# Steps

1. Read `config/channel.json` and `config/style-bible.json` through project-memory; take `niche`, `language` and `audience_location` from there, never from memory. If either file is missing or a value is null, stop and ask once.
2. Build a candidate list of exactly 3 low-startup-cost topics that fit the niche and a Bangladesh audience (examples: mobile-based side hustle, small home service, reselling). For each candidate write: who pays, what is sold, first action possible with under 1,000 BDT, and one concrete Bangla hook line.
3. Rank the candidates with a simple 1-5 score for demand, ease of first sale, and story potential. Pick the top topic and write one paragraph explaining why it beats the other two.
4. Write the report to `projects/<project>/01-research/niche-report.md`; create `projects/<project>/01-research/` first.
5. Re-open the report and check that all 3 candidates, their scores, the winner and the source files are present. Log any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Acceptance criteria**
- `projects/<project>/01-research/niche-report.md` exists under the current project and is not empty.
- It contains exactly 3 ranked candidates with a demand/ease/story score each.
- The winning topic names the payer, the offer, and a first action under 1,000 BDT.
- Niche, language and location match `config/channel.json` exactly.

**Output format (short example)**
```markdown
# Niche report — {niche} — {audience_location}
Sources: config/channel.json, config/style-bible.json

| # | Topic | Payer | First action (<1,000 BDT) | Demand | Ease | Story | Total |
|---|-------|-------|---------------------------|--------|------|-------|-------|
| 1 | Phone reselling | local buyers | list one used phone | 4 | 5 | 4 | 13 |

Winner: Phone reselling — easiest first sale and clear visual story.
Bangla hook: "পুরনো ফোন দিয়েই শুরু করুন।"
```

**Quality rules**
1. Never invent market statistics; say "estimate" or ask the user for data instead.
2. Keep every topic achievable inside 7 days with under 1,000 BDT.
3. Write the hook in natural spoken Bangla; keep file names and scores in English.

# How to test

- Type: `Use the book-finder skill with PROJECT=<project>`. Expected: `projects/<project>/01-research/niche-report.md` exists, parses cleanly, and contains no hardcoded niche or language value.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

channel config -> story-thinker

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
