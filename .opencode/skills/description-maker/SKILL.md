---
name: description-maker
description: Writes the title, description and hashtags.
category: marketing
status: implemented
phase: 5
type: prompt-only
batch: 8
---

> Context is always loaded via project-memory; all generated data lives under projects/<project>/.

# When to use

Use when writes the title, description and hashtags for a video in `projects/<project>/`.

# Purpose

Writes the title, description and hashtags.

# Input

- `final script + channel config`
- `config/channel.json` and `config/style-bible.json`, read through project-memory
- `PROJECT` environment variable (defaults to `_template`)

# Output

- `projects/<project>/09-description/description.md`
- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it

# Steps

1. Read `projects/<project>/02-script/latest_script.json`, `config/channel.json` and `config/style-bible.json` through project-memory. Use `language` for the copy and `niche` for the keyword.
2. Write a title of at most 60 characters that contains the niche keyword and the hook promise from `script.hook`. Write the first 2 description lines as the hook itself, because Shorts collapses the rest.
3. Add 2-4 short sentences that state the value and one call to action. Add optional timestamps only if the script has `scene[].duration_sec`; otherwise omit them. Finish with 3-5 hashtags, lower-case, niche-related, no more than 2 generic tags.
4. Write `projects/<project>/09-description/description.md` with the exact blocks shown below; create the `09-description` folder first.
5. Re-open the file and check the character count of the title, that the hook lines match `script.hook`, and that the hashtag count is 3-5. Log any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Acceptance criteria**
- `description.md` exists and has `TITLE:`, `DESCRIPTION:` and `HASHTAGS:` blocks.
- Title is 60 characters or fewer and contains the channel niche keyword.
- First description line equals `script.hook`.
- 3-5 hashtags; no capital letters and no unrelated trends.

**Output format (short example)**
```markdown
TITLE: টাকা ছাড়াই সাইড হাসল | Phone Reselling

DESCRIPTION:
পুরনো ফোন দিয়েই শুরু করা যায়?
একটি_used ফোন তালিকাভুক্ত করুন, ক্রেতা খুঁজুন, প্রথম বিক্রি করুন।
আপনার প্রথম পদক্ষেপ কী? কমেন্টে লিখুন।

HASHTAGS:
#sidehustle #বাংলাদেশ #phoneselling #personal finance
```

**Quality rules**
1. No clickbait that contradicts the script outcome.
2. No keyword stuffing — the niche keyword appears at most twice.
3. Keep hashtags specific to the video; drop any tag unrelated to the niche.

# How to test

- Type: `Use the description-maker skill with PROJECT=<project>`. Expected: `projects/<project>/09-description/description.md` exists, parses cleanly, and contains no hardcoded niche or language value.
- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.

# Depends on / feeds into

final-test -> growth stage

# Failure handling

If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.
