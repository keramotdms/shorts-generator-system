# How to use the Shorts production system

Every video is a folder under `projects/<project>/`. Set `PROJECT=my-video` (or use the default `_template`) before starting. Niche, language, location and style are **never typed into a prompt** — they are always read through `project-memory` from `config/channel.json` and `config/style-bible.json`.

## 0. One-time setup (do this once per channel)

Type:

```text
Use the project-memory skill with PROJECT=_template. Read config/channel.json and write config/style-bible.json. Never hardcode niche or language.
```

Expected: `config/style-bible.json` exists and contains `channel.niche`, `channel.language`, `channel.audience_location`.

If `config/channel.json` has a null value, the skill will stop and ask you once. Answer, then repeat this prompt; it saves the answer through project-memory.

Optional: when FFmpeg is usable, set `FFMPEG_PATH` to the executable before any video skill. While it is blocked, those skills report `BLOCKED ...` and the pipeline continues without a FAIL.

## 1. New video idea → research

```text
Use the book-finder skill with PROJECT=my-video. Find 3 niche ideas from config/channel.json via project-memory and write projects/my-video/01-research/niche-report.md.
```

```text
Use the trend-finder skill with PROJECT=my-video. Read free YouTube/Google/manual sources from project-memory and write research/trend-cache/trend-report.json.
```

Optional depth: `competitor-analyzer`, `audience-persona-builder`, `fact-checker`, `content-calendar` use the same pattern.

## 2. Story → hook → script

```text
Use the story-thinker skill with PROJECT=my-video. Turn projects/my-video/01-research/niche-report.md and research/trend-cache/trend-report.json into projects/my-video/02-script/story.json using the cached niche/language/style.
```

```text
Use the hook-writer skill with PROJECT=my-video. Write a 3-second hook into projects/my-video/02-script/hook.json.
```

```text
Use the script-writer skill with PROJECT=my-video. Write projects/my-video/02-script/latest_script.json (30-60s, 9:16) using story.json + hook.json + style context.
```

```text
Use the script-tester skill with PROJECT=my-video. Audit projects/my-video/02-script/latest_script.json and write the report to projects/my-video/02-script/script-tester.json.
```

## 3. Voice

```text
Use the voiceover-generator skill with PROJECT=my-video. Generate projects/my-video/03-voice/voiceover.mp3 and word timings projects/my-video/03-voice/captions.json from latest_script.json; read language from project-memory.
```

```text
Use the caption-maker skill with PROJECT=my-video. Turn projects/my-video/03-voice/captions.json into projects/my-video/07-edit/captions.json with safe-zone data, then burn it into projects/my-video/07-edit/captioned.mp4 and write projects/my-video/07-edit/caption-maker.json.
```

`voiceover-captions` is a legacy pointer only; use the two skills above.

## 4. Character + scene

```text
Use the character-designer skill with PROJECT=my-video. Read config/style-bible.json through project-memory and write assets/characters/creator-01/character.json plus its SVG/PNG expressions.
```

```text
Use the scenario-designer skill with PROJECT=my-video. Build projects/my-video/05-scene/scenario-designer.json from the final script and style context, plus assets/scenes/warm-desk-background.svg and assets/scenes/scene-warm-desk-smile.png.
```

## 5. Collect + render video

```text
Use the script-voice-character-collector skill with PROJECT=my-video. Combine projects/my-video/02-script/latest_script.json, projects/my-video/03-voice/voiceover.mp3, assets/characters/creator-01/character.json and assets/scenes/scene-warm-desk-smile.png into projects/my-video/05-scene/collection.json (including scene_images[] and scenes[]).
```

```text
Use the video-maker skill with PROJECT=my-video. Render projects/my-video/06-video/scenes/ from collection.json using FFMPEG_PATH.
```

If this prints `BLOCKED video-maker: ffmpeg ...`, leave it — the block is reported, not failed. Everything else can continue.

## 6. Edit

```text
Use the rough-cut-assembler skill with PROJECT=my-video. Assemble projects/my-video/06-video/scenes/ into projects/my-video/07-edit/rough-cut.mp4.
```

```text
Use the caption-maker skill with PROJECT=my-video. Produce projects/my-video/07-edit/captions.json.
```

```text
Use the safe-zone-checker skill with PROJECT=my-video. Validate projects/my-video/07-edit/captions.json and write projects/my-video/07-edit/safe-zone-checker.json.
```

All other editing skills (animator, transitions, color, audio sync, thumbnails) follow the same `Use the <skill> skill with PROJECT=my-video` pattern and read FFMPEG_PATH when needed.

Export the one canonical final video before final tests:

```text
Use the render-export-optimizer skill with PROJECT=my-video. Export projects/my-video/07-edit/captioned.mp4 to projects/my-video/08-final-test/final-video.mp4 and write projects/my-video/07-edit/render-export-optimizer.json.
```

Every later skill (bug-finder, platform/accessibility checkers, handover, publishing) reads that exact path.

## 7. Final test

```text
Use the bug-finder skill with PROJECT=my-video. Check projects/my-video/08-final-test/final-video.mp4 and write projects/my-video/08-final-test/bug-finder.json.
```

```text
Use the platform-compliance-checker skill with PROJECT=my-video. Validate the final video and metadata against YouTube Shorts and Facebook Reels rules.
```

## 8. Description / SEO → handover

```text
Use the description-maker skill with PROJECT=my-video. Write projects/my-video/09-description/description.md using the final script and style context.
```

```text
Use the handover skill with PROJECT=my-video. Verify projects/my-video/08-final-test/final-video.mp4, projects/my-video/07-edit/captions.json and projects/my-video/09-description/description.md, then write projects/my-video/10-publish/handover.md and projects/my-video/10-publish/handover-check.json.
```

Expected: `ready: true`. If any asset is missing, handover writes both files but exits non-zero and lists the exact missing paths; fix them and repeat.

## Testing the whole system (no real media needed)

```powershell
python tests\smoke\run_dummy_pipeline.py
python tests\test_skills.py
python scripts\health_check.py
```

The dummy pipeline uses a 5-second fixture at `tests/fixtures/latest_script.json`, writes to `projects/dummy/`, and prints `PASS`, `FAIL` or `BLOCKED` for every one of the 93 skills.
