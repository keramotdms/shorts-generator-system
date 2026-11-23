# Skill review — final verification (2026-11-23)

Status: **93 OK | 0 FIX | 0 WEAK**. Every issue in the original read-only audit was fixed in four committed phases. `git pull origin main` was run first and was already up to date at `abba09f`. No package was installed, `.env` and Windows settings were untouched, no token was placed in chat/repo/`.env`, and no force push was used.

## 1. Fix phases

| phase | commit | outcome |
|---|---|---|
| Phase 1 — chain | `afb6fb7` | End-to-end dry run now reaches a ready handover. `07-edit/captions.json` is produced; `08-final-test/final-video.mp4` has one canonical producer (`render-export-optimizer`); checker report paths match contracts; handover is non-circular and exits 1 when not ready; `script-writer` example/paths fixed. |
| Phase 2 — contracts | `b149a99` | All 93 contract `input`/`output` strings are exact paths; `script-tester` duplicate output removed; all 20 chain mismatches fixed; `tests/test_chain.py` added to health checks. |
| Phase 3 — self-tests | `4385bcc` | All 16 print-only/availability-only self-tests replaced with real assertions (schema round-trip, JSONL round-trip, ffprobe duration/resolution, ready/not-ready handover). Fixed PASS strings removed; `tests/test_skills.py` now reports honest PASS/BLOCKED counts. |
| Phase 4 — documentation | this commit | All copy-paste Steps rewritten to unique, skill-specific procedures; 12 Bangla-touching skills got explicit Bangla rules; missing schemas/examples added; review checks recomputed from current files. |

## 2. Recomputed review checks

| check | original audit | current result |
|---|---:|---:|
| Example vs schema | 1 hard failure + 6 schema/example gaps | **0 errors** — added `project-memory.json`, `trend-report.json`, `handover.json`; added valid examples to `handover` and `voiceover-generator`; fixed `script-writer` |
| Contract paths | ~68 descriptive strings, 1 duplicate output | **0 errors** — 93 exact paths, no duplicates, every input produced upstream (`tests/test_chain.py` PASS) |
| Legacy paths | `scripts/latest_script.json`, `output/voiceover.mp3` | **0 occurrences** in contracts or SKILL.md |
| Chain hand-offs | 20 mismatches, 3 dry-run breaks | **0 mismatches** — all 11 dry-run steps exit 0; handover is `ready` |
| Self-tests | 16 assert nothing; 47 PASS overstated | **0 print-only bodies** — 48 self-tests PASS, 0 BLOCKED, counted honestly |
| Steps similarity | 99 pairs >80% (100% worst case) | **0 pairs >80% and 0 pairs >60%** after removing skill names |
| Bangla rules | 9 skills lacked explicit rules | **0 gaps** — 12 skills now carry explicit Bangla/Noto Sans Bengali/৳ rules |
| Numeric criteria | missing in generic checker/editor Steps | **0 gaps** — every Steps section has numeric, checkable criteria |

## 3. Required test evidence

```text
python scripts/health_check.py          -> 63 PASS | 0 WARN | 0 BLOCKED | 0 FAIL
python tests/test_skills.py             -> 93 skills validated, 48 self-tests passed, 0 blocked
python tests/smoke/run_dummy_pipeline.py-> 93 PASS | 0 FAIL | 0 BLOCKED
python tests/test_no_template.py        -> 55 implemented skills checked, 0 template skills
python tests/test_chain.py              -> PASS: exact paths, no duplicate outputs, every input produced upstream
end-to-end dry run                      -> 11/11 steps exit 0; ready handover; not-ready handover exits 1
```

## 4. Unresolved problems

**None.** The current verdict is 93 OK / 0 FIX / 0 WEAK. Hardcoded-looking niche/language strings that remain inside filled examples or explicit Bangla rules are intentional and load through project-memory; they are not config hardcoding.

---

# Original audit — read-only baseline (2026-11-23)

Historical baseline only — the text below records the original findings before the four fix phases; it does not describe the current state. The current state is the final verification at the top of this file.

Scope was all 93 implemented skills. `git pull origin main` was run first: already up to date at `abba09f`. No skill file, config, schema or script was changed during that audit; no package was installed. The only repo file written was this report. The temporary dry-run project `projects/review-tmp` was created and deleted during the review.

Method: every filled JSON example was parsed and validated with `scripts/schema_validator.py` (not assumed); Input/Output text was compared with `config/skill-contracts.json`; context handling and hardcoded words were grepped; numeric criteria and self-test bodies were read in `scripts/skill_tools.py` and `scripts/effect_ffmpeg.py`; Steps were fuzzy-compared pairwise with `difflib.SequenceMatcher` after removing the skill name and all non-alphanumeric characters.

## 1. Per-skill verdicts (sorted FIX, WEAK, OK)

| skill | verdict | one-line issue |
|---|---|---|
| accessibility-safety-checker | FIX | Steps 99% identical to bug-finder after removing skill name (copy-paste) / +2 more |
| asset-manager | FIX | Steps 96% identical to task-tracker after removing skill name (copy-paste) |
| audio-ducking-controller | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +2 more |
| audio-mixer | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +2 more |
| av-sync-checker | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +2 more |
| bug-finder | FIX | Steps 99% identical to accessibility-safety-checker after removing skill name (copy-paste) / +1 more |
| caption-maker | FIX | OUTPUT NOT WRITTEN: declares 07-edit/captions.json + caption-maker.json; helper writes captioned.mp4 + caption-maker-report.json; cmd_caption_maker() is dead code / +2 more |
| character-qa-tester | FIX | Steps 96% identical to consistency-guardian after removing skill name (copy-paste) / +1 more |
| consistency-guardian | FIX | Steps 96% identical to character-qa-tester after removing skill name (copy-paste) / +1 more |
| copyright-policy-checker | FIX | Steps 99% identical to accessibility-safety-checker after removing skill name (copy-paste) / +2 more |
| description-maker | FIX | no Bangla rule for script/voice/caption skill / +2 more |
| error-log-keeper | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +2 more |
| format-converter | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +2 more |
| handover | FIX | OUTPUT NOT WRITTEN: declares 10-publish/handover.md; helper writes only handover-check.json and checks handover.md as an input (circular) / +3 more |
| hook-visual-editor | FIX | no Bangla rule for script/voice/caption skill / +1 more |
| hook-writer | FIX | no Bangla rule for script/voice/caption skill |
| intro-outro-manager | FIX | no Bangla rule for script/voice/caption skill / +1 more |
| kinetic-text-animator | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +3 more |
| orchestrator | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +1 more |
| pipeline-health-checker | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +2 more |
| platform-compliance-checker | FIX | Steps 99% identical to accessibility-safety-checker after removing skill name (copy-paste) / +2 more |
| render-export-optimizer | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +2 more |
| rough-cut-assembler | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +1 more |
| safe-zone-checker | FIX | OUTPUT NOT WRITTEN: declares 07-edit/safe-zone-checker.json; helper writes 07-edit/safe-zone-report.json / +3 more |
| script-tester | FIX | DOC PATH: contract output path is duplicated: script-tester.json + script-tester.json / +1 more |
| script-writer | FIX | EXAMPLE FAILS SCHEMA: ex0: $.scenes: fewer than minItems 3 / +2 more |
| task-tracker | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +2 more |
| transition-designer | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +2 more |
| video-maker | FIX | OUTPUT NOT WRITTEN: declares 06-video/scenes/ but helper ignores declared collection.json and reads latest_script.json + loose PNGs / +3 more |
| video-quality-checker | FIX | self-test asserts no expected value (prints only / ffmpeg availability) / +2 more |
| voiceover-captions | FIX | DOC PATH: legacy output folder output/voiceover.mp3 + output/captions.json conflicts with 03-voice/ stage layout / +1 more |
| voiceover-generator | FIX | no Bangla rule for script/voice/caption skill / +1 more |
| voiceover-tester | FIX | Steps 95% identical to safe-zone-checker after removing skill name (copy-paste) / +2 more |
| animator | WEAK | contract Input/Output is descriptive, not an exact path |
| audience-persona-builder | WEAK | contract Input/Output is descriptive, not an exact path |
| beat-sync-editor | WEAK | contract Input/Output is descriptive, not an exact path |
| book-finder | WEAK | contract Input/Output is descriptive, not an exact path / +1 more |
| branding-manager | WEAK | contract Input/Output is descriptive, not an exact path |
| broll-variety-planner | WEAK | contract Input/Output is descriptive, not an exact path |
| character-organizer | WEAK | contract Input/Output is descriptive, not an exact path |
| character-setup-manager | WEAK | contract Input/Output is descriptive, not an exact path |
| character-thinker-counter | WEAK | contract Input/Output is descriptive, not an exact path |
| color-grading-keeper | WEAK | contract Input/Output is descriptive, not an exact path |
| competitor-analyzer | WEAK | contract Input/Output is descriptive, not an exact path |
| content-calendar | WEAK | contract Input/Output is descriptive, not an exact path |
| copywriter | WEAK | contract Input/Output is descriptive, not an exact path |
| cross-platform-repurposer | WEAK | contract Input/Output is descriptive, not an exact path |
| cut-rhythm-editor | WEAK | contract Input/Output is descriptive, not an exact path |
| element-designer | WEAK | contract Input/Output is descriptive, not an exact path |
| element-organizer | WEAK | contract Input/Output is descriptive, not an exact path |
| emphasis-sticker-placer | WEAK | contract Input/Output is descriptive, not an exact path |
| expression-pose-library | WEAK | contract Input/Output is descriptive, not an exact path |
| fact-checker | WEAK | contract Input/Output is descriptive, not an exact path |
| lipsync-motion-planner | WEAK | contract Input/Output is descriptive, not an exact path |
| localization | WEAK | contract Input/Output is descriptive, not an exact path / +1 more |
| loop-cta-designer | WEAK | contract Input/Output is descriptive, not an exact path |
| marketing-specialist | WEAK | contract Input/Output is descriptive, not an exact path |
| motion-graphic-editor | WEAK | contract Input/Output is descriptive, not an exact path |
| music-sfx-selector | WEAK | contract Input/Output is descriptive, not an exact path |
| pattern-interrupt-inserter | WEAK | contract Input/Output is descriptive, not an exact path |
| preview-frame-extractor | WEAK | contract Input/Output is descriptive, not an exact path |
| project-memory | WEAK | has an example but declares no schema in config/schemas/ / +1 more |
| pronunciation-emotion-director | WEAK | contract Input/Output is descriptive, not an exact path |
| red-team | WEAK | contract Input/Output is descriptive, not an exact path |
| retention-pacing-optimizer | WEAK | contract Input/Output is descriptive, not an exact path |
| ruthless-team | WEAK | contract Input/Output is descriptive, not an exact path |
| scenario-designer | WEAK | contract Input/Output is descriptive, not an exact path |
| script-user-tester | WEAK | contract Input/Output is descriptive, not an exact path |
| script-video-voice-collector | WEAK | contract Input/Output is descriptive, not an exact path |
| script-voice-character-collector | WEAK | contract Input/Output is descriptive, not an exact path |
| seamless-loop-editor | WEAK | contract Input/Output is descriptive, not an exact path |
| seo-specialist | WEAK | contract Input/Output is descriptive, not an exact path |
| sfx-timing-placer | WEAK | contract Input/Output is descriptive, not an exact path |
| solver | WEAK | contract Input/Output is descriptive, not an exact path |
| stock-asset-finder | WEAK | contract Input/Output is descriptive, not an exact path |
| story-organizer | WEAK | contract Input/Output is descriptive, not an exact path / +1 more |
| story-thinker | WEAK | mentions hardcoded-looking niche/language words in examples |
| thumbnail-designer | WEAK | contract Input/Output is descriptive, not an exact path |
| trend-finder | WEAK | has an example but declares no schema in config/schemas/ / +2 more |
| variant-batch-renderer | WEAK | contract Input/Output is descriptive, not an exact path |
| video-editor | WEAK | contract Input/Output is descriptive, not an exact path |
| virtual-camera-planner | WEAK | contract Input/Output is descriptive, not an exact path |
| voiceover-organizer | WEAK | contract Input/Output is descriptive, not an exact path |
| watermark-logo-placer | WEAK | contract Input/Output is descriptive, not an exact path |
| ab-tester | OK | No issue found in checks a-g. |
| analytics-feedback-loop | OK | No issue found in checks a-g. |
| character-designer | OK | No issue found in checks a-g. |
| comment-community-manager | OK | No issue found in checks a-g. |
| monetization-tracker | OK | No issue found in checks a-g. |
| scheduler-publisher | OK | No issue found in checks a-g. |
| template-preset-manager | OK | No issue found in checks a-g. |
| youtube-analyst | OK | No issue found in checks a-g. |
| youtube-seo-specialist | OK | No issue found in checks a-g. |

Full issue detail (every failing sub-check, in the same order):

- **accessibility-safety-checker (FIX)**: Steps 99% identical to bug-finder after removing skill name (copy-paste); no Bangla rule for script/voice/caption skill; contract Input/Output is descriptive, not an exact path
- **asset-manager (FIX)**: Steps 96% identical to task-tracker after removing skill name (copy-paste)
- **audio-ducking-controller (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 98% identical to format-converter after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **audio-mixer (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 88% identical to voiceover-tester after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **av-sync-checker (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 100% identical to format-converter after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **bug-finder (FIX)**: Steps 99% identical to accessibility-safety-checker after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **caption-maker (FIX)**: OUTPUT NOT WRITTEN: declares 07-edit/captions.json + caption-maker.json; helper writes captioned.mp4 + caption-maker-report.json; cmd_caption_maker() is dead code; no Bangla rule for script/voice/caption skill; declares schema but has no filled JSON example in SKILL.md
- **character-qa-tester (FIX)**: Steps 96% identical to consistency-guardian after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **consistency-guardian (FIX)**: Steps 96% identical to character-qa-tester after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **copyright-policy-checker (FIX)**: Steps 99% identical to accessibility-safety-checker after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path; self-test coverage unclear
- **description-maker (FIX)**: no Bangla rule for script/voice/caption skill; contract Input/Output is descriptive, not an exact path; mentions hardcoded-looking niche/language words in examples
- **error-log-keeper (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 95% identical to task-tracker after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **format-converter (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 100% identical to av-sync-checker after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **handover (FIX)**: OUTPUT NOT WRITTEN: declares 10-publish/handover.md; helper writes only handover-check.json and checks handover.md as an input (circular); self-test asserts no expected value (prints only / ffmpeg availability); declares schema but has no filled JSON example in SKILL.md; contract Input/Output is descriptive, not an exact path
- **hook-visual-editor (FIX)**: no Bangla rule for script/voice/caption skill; contract Input/Output is descriptive, not an exact path
- **hook-writer (FIX)**: no Bangla rule for script/voice/caption skill
- **intro-outro-manager (FIX)**: no Bangla rule for script/voice/caption skill; contract Input/Output is descriptive, not an exact path
- **kinetic-text-animator (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 99% identical to format-converter after removing skill name (copy-paste); no Bangla rule for script/voice/caption skill; contract Input/Output is descriptive, not an exact path
- **orchestrator (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); no project-memory/style_context reference
- **pipeline-health-checker (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 96% identical to asset-manager after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **platform-compliance-checker (FIX)**: Steps 99% identical to accessibility-safety-checker after removing skill name (copy-paste); no Bangla rule for script/voice/caption skill; contract Input/Output is descriptive, not an exact path
- **render-export-optimizer (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 99% identical to format-converter after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **rough-cut-assembler (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 96% identical to format-converter after removing skill name (copy-paste)
- **safe-zone-checker (FIX)**: OUTPUT NOT WRITTEN: declares 07-edit/safe-zone-checker.json; helper writes 07-edit/safe-zone-report.json; self-test asserts no expected value (prints only / ffmpeg availability); Steps 96% identical to asset-manager after removing skill name (copy-paste); no Bangla rule for script/voice/caption skill
- **script-tester (FIX)**: DOC PATH: contract output path is duplicated: script-tester.json + script-tester.json; contract Input/Output is descriptive, not an exact path
- **script-writer (FIX)**: EXAMPLE FAILS SCHEMA: ex0: $.scenes: fewer than minItems 3; DOC PATH: legacy lead instructions still say save to scripts/latest_script.json (outside projects/<project>/); example has 1 scene but schema minItems=3; mentions hardcoded-looking niche/language words in examples
- **task-tracker (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 96% identical to asset-manager after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **transition-designer (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 98% identical to format-converter after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **video-maker (FIX)**: OUTPUT NOT WRITTEN: declares 06-video/scenes/ but helper ignores declared collection.json and reads latest_script.json + loose PNGs; self-test asserts no expected value (prints only / ffmpeg availability); Steps 86% identical to video-quality-checker after removing skill name (copy-paste); declares schema but has no filled JSON example in SKILL.md
- **video-quality-checker (FIX)**: self-test asserts no expected value (prints only / ffmpeg availability); Steps 97% identical to format-converter after removing skill name (copy-paste); contract Input/Output is descriptive, not an exact path
- **voiceover-captions (FIX)**: DOC PATH: legacy output folder output/voiceover.mp3 + output/captions.json conflicts with 03-voice/ stage layout; no Bangla rule for script/voice/caption skill
- **voiceover-generator (FIX)**: no Bangla rule for script/voice/caption skill; declares schema but has no filled JSON example in SKILL.md
- **voiceover-tester (FIX)**: Steps 95% identical to safe-zone-checker after removing skill name (copy-paste); no Bangla rule for script/voice/caption skill; contract Input/Output is descriptive, not an exact path
- **animator (WEAK)**: contract Input/Output is descriptive, not an exact path
- **audience-persona-builder (WEAK)**: contract Input/Output is descriptive, not an exact path
- **beat-sync-editor (WEAK)**: contract Input/Output is descriptive, not an exact path
- **book-finder (WEAK)**: contract Input/Output is descriptive, not an exact path; mentions hardcoded-looking niche/language words in examples
- **branding-manager (WEAK)**: contract Input/Output is descriptive, not an exact path
- **broll-variety-planner (WEAK)**: contract Input/Output is descriptive, not an exact path
- **character-organizer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **character-setup-manager (WEAK)**: contract Input/Output is descriptive, not an exact path
- **character-thinker-counter (WEAK)**: contract Input/Output is descriptive, not an exact path
- **color-grading-keeper (WEAK)**: contract Input/Output is descriptive, not an exact path
- **competitor-analyzer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **content-calendar (WEAK)**: contract Input/Output is descriptive, not an exact path
- **copywriter (WEAK)**: contract Input/Output is descriptive, not an exact path
- **cross-platform-repurposer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **cut-rhythm-editor (WEAK)**: contract Input/Output is descriptive, not an exact path
- **element-designer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **element-organizer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **emphasis-sticker-placer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **expression-pose-library (WEAK)**: contract Input/Output is descriptive, not an exact path
- **fact-checker (WEAK)**: contract Input/Output is descriptive, not an exact path
- **lipsync-motion-planner (WEAK)**: contract Input/Output is descriptive, not an exact path
- **localization (WEAK)**: contract Input/Output is descriptive, not an exact path; mentions hardcoded-looking niche/language words in examples
- **loop-cta-designer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **marketing-specialist (WEAK)**: contract Input/Output is descriptive, not an exact path
- **motion-graphic-editor (WEAK)**: contract Input/Output is descriptive, not an exact path
- **music-sfx-selector (WEAK)**: contract Input/Output is descriptive, not an exact path
- **pattern-interrupt-inserter (WEAK)**: contract Input/Output is descriptive, not an exact path
- **preview-frame-extractor (WEAK)**: contract Input/Output is descriptive, not an exact path
- **project-memory (WEAK)**: has an example but declares no schema in config/schemas/; mentions hardcoded-looking niche/language words in examples
- **pronunciation-emotion-director (WEAK)**: contract Input/Output is descriptive, not an exact path
- **red-team (WEAK)**: contract Input/Output is descriptive, not an exact path
- **retention-pacing-optimizer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **ruthless-team (WEAK)**: contract Input/Output is descriptive, not an exact path
- **scenario-designer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **script-user-tester (WEAK)**: contract Input/Output is descriptive, not an exact path
- **script-video-voice-collector (WEAK)**: contract Input/Output is descriptive, not an exact path
- **script-voice-character-collector (WEAK)**: contract Input/Output is descriptive, not an exact path
- **seamless-loop-editor (WEAK)**: contract Input/Output is descriptive, not an exact path
- **seo-specialist (WEAK)**: contract Input/Output is descriptive, not an exact path
- **sfx-timing-placer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **solver (WEAK)**: contract Input/Output is descriptive, not an exact path
- **stock-asset-finder (WEAK)**: contract Input/Output is descriptive, not an exact path
- **story-organizer (WEAK)**: contract Input/Output is descriptive, not an exact path; mentions hardcoded-looking niche/language words in examples
- **story-thinker (WEAK)**: mentions hardcoded-looking niche/language words in examples
- **thumbnail-designer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **trend-finder (WEAK)**: has an example but declares no schema in config/schemas/; contract Input/Output is descriptive, not an exact path; mentions hardcoded-looking niche/language words in examples
- **variant-batch-renderer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **video-editor (WEAK)**: contract Input/Output is descriptive, not an exact path
- **virtual-camera-planner (WEAK)**: contract Input/Output is descriptive, not an exact path
- **voiceover-organizer (WEAK)**: contract Input/Output is descriptive, not an exact path
- **watermark-logo-placer (WEAK)**: contract Input/Output is descriptive, not an exact path

### CHECK 1 sub-check notes

- **a. Example vs schema (actually executed):** 1 hard failure — `script-writer`'s example has 1 scene but `config/schemas/latest_script.json` requires `minItems: 3`. Four skills declare a schema but ship no filled example (`caption-maker`, `handover`, `video-maker`, `voiceover-generator`), and two ship an example with no declared schema (`project-memory`, `trend-finder`). Of the 10 spotlight skills, 5 have no filled example at all.
- **b. Contract paths:** no literal path conflicts, but ~68 contracts use descriptive strings (`rough cut + hook plan`, `final video + reports`, `all final assets`) instead of exact paths, so exact hand-off validation is impossible. `script-tester` lists the same output path twice. Legacy `script-writer` lead instructions still say `scripts/latest_script.json`, and legacy `voiceover-captions` still says `output/`. 4 helper outputs use different file names from their contracts (see CHECK 2).
- **c. Context/hardcoding:** every skill except `orchestrator` mentions project-memory or `style_context()`. Hardcoded niche/language words found in 30 skills are mostly inside illustrative examples or Bangla-output rules, not config values; `script-writer`, `story-thinker` and `book-finder` are the clearest cases where example literals contradict a 'no hardcoded niche/language' test line.
- **d. Numeric criteria:** present and checkable in all 55 batch A-D skills and in the 8 original script/character skills. Absent in the 5-step generic checker/editor template (`caption-maker`, `safe-zone-checker`, `bug-finder`, `format-converter`, `av-sync-checker`, etc.) — those only say 'verify it is valid and non-empty'.
- **e. Self-tests:** 30 have real assertions (schema validation or ffprobe expected values, including all 18 effect-FFmpeg skills). 16 assert nothing: 6 print a fixed PASS string (`task-tracker`, `error-log-keeper`, `safe-zone-checker`, `orchestrator`, `pipeline-health-checker`, `handover`) and 10 only check ffmpeg availability (`video-maker`, `rough-cut-assembler`, `format-converter`, `render-export-optimizer`, `audio-mixer`, `audio-ducking-controller`, `kinetic-text-animator`, `transition-designer`, `video-quality-checker`, `av-sync-checker`). Prompt-only skills have no self-test by design.
- **f. Steps similarity:** 99 pairs exceed 80% after removing the skill name. All are inside the 38 original (batch 1-8) skills; none of the 55 batch A-D rewrites appear. Top pairs: av-sync-checker≈format-converter 100.0%, accessibility-safety-checker≈bug-finder 99.4%, accessibility-safety-checker≈platform-compliance-checker 99.4%, accessibility-safety-checker≈copyright-policy-checker 99.0%, format-converter≈render-export-optimizer 99.0%.
- **g. Bangla rules:** 9 script/voice/caption-touching skills have no explicit Bangla rule (`hook-writer`, `script-writer`, `voiceover-generator`, `voiceover-captions`, `caption-maker`, `safe-zone-checker`, `description-maker`, `hook-visual-editor`, `kinetic-text-animator`); they rely on a generic 'use project language' line.

## 2. Counts by category

| category | OK | FIX | WEAK | total |
|---|---:|---:|---:|---:|
| character | 1 | 2 | 4 | 7 |
| core | 0 | 5 | 1 | 6 |
| final-test | 0 | 5 | 3 | 8 |
| growth | 7 | 0 | 1 | 8 |
| marketing | 0 | 1 | 3 | 4 |
| research | 0 | 0 | 6 | 6 |
| scene | 0 | 0 | 3 | 3 |
| script | 0 | 3 | 6 | 9 |
| video-editing | 1 | 11 | 19 | 31 |
| video-making | 0 | 2 | 2 | 4 |
| voice | 0 | 4 | 3 | 7 |
| **total** | **9** | **33** | **51** | **93** |

## 3. Chain compatibility mismatches (research → publish)

| # | hand-off | mismatch | type | evidence |
|---|---|---|---|---|
| 1 | book-finder → story-thinker | research/niche-report.md is at repo root while 01-research skills write to projects/<project>/01-research/ | wrong folder | both paths in config/skill-contracts.json |
| 2 | trend-finder → story-thinker | OUT is research/trend-cache/*.json but Step 1 reads research/trend-cache/trend-report.json | file name | contract wildcard vs literal step path |
| 3 | story-thinker → hook-writer | hook_seed/angle fields match, but hook.json field `text` becomes latest_script.json field `hook` via prose only | field name | schemas hook.json vs latest_script.json |
| 4 | script-writer → voiceover-generator | lead instructions save to scripts/latest_script.json instead of projects/<project>/02-script/latest_script.json; example fails schema | wrong folder + schema | script-writer SKILL.md lines 14-22, 79-84 |
| 5 | character-designer → script-voice-character-collector | character JSON under assets/characters/ is ignored; helper reads config/style-bible.json `characters` object | file name / missing consumer | cmd_collector() line 259 |
| 6 | script-voice-character-collector → video-maker | helper ignores declared collection.json and reads latest_script.json + loose PNGs | missing consumer | cmd_video_maker() lines 366-370 |
| 7 | collector → rough-cut-assembler | helper looks for collection['scenes'] which collector never writes; silently falls back to glob | missing field | cmd_collector() 260-267 vs cmd_rough_cut() 393 |
| 8 | rough-cut-assembler → caption-maker | cmd_caption_maker() that writes 07-edit/captions.json is never called (dead code); CLI routes to cmd_caption_burn_in() | missing producer | skill_tools.py def 228 vs call 757 |
| 9 | caption-maker → safe-zone-checker | safe-zone requires 07-edit/captions.json, which the chain never writes | file name + missing producer | cmd_safe_zone() line 274 - first dry-run break |
| 10 | caption-maker output | contract says 07-edit/captions.json + caption-maker.json; helper writes captioned.mp4 + caption-maker-report.json | file name | contract vs cmd_caption_burn_in() 434-441 |
| 11 | safe-zone-checker output | contract says 07-edit/safe-zone-checker.json; helper writes 07-edit/safe-zone-report.json | file name | cmd_safe_zone() line 307 |
| 12 | final video producer | no skill declares 08-final-test/final-video.mp4 as output, yet bug-finder, platform/accessibility checkers, handover and effect_ffmpeg require it | missing producer | grep final-video.mp4 in scripts/ - second dry-run break |
| 13 | checker reports | cmd_checker() always writes stage 8 <skill>-report.json; contracts declare stage 2/3/4/7 <skill>.json | wrong folder + file name | cmd_checker() line 627 vs contracts |
| 14 | av-sync-checker / video-quality-checker | both write stage 8 <skill>-report.json; av-sync contract says 07-edit/av-sync-checker.json | wrong folder | cmd_ffprobe_check() line 326 |
| 15 | final-test → description-maker | description-maker takes final script + channel config; no hand-off from bug-finder/red-team findings | broken hand-off | contract inputs |
| 16 | handover → publish | handover requires 10-publish/handover.md as an input and never writes it; exits 0 with 'not ready' | circular + missing producer | cmd_handover() lines 638-648 - third dry-run break |
| 17 | handover output | contract says 10-publish/handover.md; helper only writes handover-check.json | file name | cmd_handover() line 647 |
| 18 | publish skills | marketing-specialist, scheduler-publisher and cross-platform-repurposer all require handover.md, so all are blocked | downstream block | their SKILL.md inputs |
| 19 | voiceover-captions (legacy) | output/voiceover.mp3 + output/captions.json conflicts with 03-voice stage layout | wrong folder | contract + AGENTS.md rule 10 |
| 20 | script-tester contract | output path listed twice: 02-script/script-tester.json + 02-script/script-tester.json | contract defect | config/skill-contracts.json |

## 4. Dry run with fake data (CHECK 3)

`projects/review-tmp` was created with hand-made files only: valid fixtures for `story.json`, `hook.json`, `latest_script.json`, `captions.json`, a 1-second ffmpeg sine `voiceover.mp3`, and one copied 1080x1920 PNG. No AI/TTS/API generation was used. All commands ran with `PROJECT=review-tmp`; the folder was deleted afterwards.

| step | command | result |
|---|---|---|
| 00 | ffmpeg status | OK (ffmpeg 9.1 full build) |
| 01 | tiny voiceover.mp3 via ffmpeg sine | PASS - 03-voice/voiceover.mp3 |
| 02 | skill_tools.py script-voice-character-collector run | PASS - 05-scene/collection.json |
| 03 | skill_tools.py video-maker run | PASS - 3 scene MP4s (ignored collection.json) |
| 04 | skill_tools.py rough-cut-assembler run | PASS - 07-edit/rough-cut.mp4 |
| 05 | skill_tools.py caption-maker run | PASS - captioned.mp4 + caption-maker-report.json; **no 07-edit/captions.json** |
| 06 | internal cmd_caption_burn_in() | PASS - same output as 05; confirms duplicate path |
| 07 | skill_tools.py safe-zone-checker run | **FIRST BREAK** - FAIL: missing 07-edit/captions.json |
| 08 | skill_tools.py bug-finder run | **SECOND BREAK** - FAIL: missing 08-final-test/final-video.mp4 |
| 09 | skill_tools.py handover run | **THIRD BREAK** - exit 0 but 'not ready': final-video.mp4, 07-edit/captions.json, 09-description/description.md, 10-publish/handover.md missing |

**First break:** `caption-maker → safe-zone-checker`. The CLI command for `caption-maker` calls `cmd_caption_burn_in()`, so the function that writes the contract's `07-edit/captions.json` (`cmd_caption_maker()`) is unreachable. `cmd_safe_zone()` treats that file as required and aborts. Even if fixed, the next break is `bug-finder`: no skill produces `08-final-test/final-video.mp4`. The third break is `handover`, which lists its own output as a required input and returns success while reporting 'not ready'.

## 5. Top 10 most serious problems

1. caption-maker's CLI never writes its declared output `07-edit/captions.json` (`cmd_caption_maker()` is dead code), so safe-zone-checker fails immediately — confirmed in the dry run.
2. No skill produces `08-final-test/final-video.mp4`, although bug-finder, platform-compliance, accessibility-safety, handover and all 18 effect-FFmpeg skills depend on it.
3. handover requires `10-publish/handover.md` as an input and never writes it; it exits 0 with 'not ready', blocking marketing-specialist, scheduler-publisher and cross-platform-repurposer.
4. script-writer's filled example fails its own schema (1 scene vs minItems 3), and its lead instructions still write to `scripts/latest_script.json` — the first artifact of the flagship chain is wrong.
5. 99 Steps pairs are over 80% identical after removing the skill name (av-sync-checker vs format-converter = 100%); all are among the 38 original skills, so the earlier anti-fake test missed them.
6. Helper output file names and folders disagree with contracts across all checkers and several editors (`safe-zone-report.json` vs `safe-zone-checker.json`, `cmd_checker()` always writing stage 8).
7. 16 script-backed/checker self-tests assert no expected value — 6 only print PASS, 10 only check ffmpeg availability — so '47 self-tests passed' overstates coverage.
8. video-maker ignores its declared `collection.json` input and collector ignores character-designer's JSON; the chain only works by glob fallbacks.
9. ~68 contracts use descriptive Input/Output strings instead of exact paths, defeating automated hand-off checks; script-tester lists one output twice.
10. 5 of the 10 spotlight skills have no filled Output example; 9 script/voice/caption skills have no explicit Bangla rule; 2 skills have examples with no schema.

## 6. Full Steps + Output example for the 10 requested skills

### story-thinker

**Steps**

1. Read `research/niche-report.md` (winner and ranking) plus `config/channel.json` and `config/style-bible.json` through project-memory. Read `research/trend-cache/trend-report.json` if it exists and use its top local trend as a timing hint.
2. Pick the single winner topic. Write one sentence naming the viewer's pain in Bangladesh, one sentence naming the promised outcome, and one `hook_seed` phrased as a question or bold claim in the project language.
3. Split the story into exactly 3 beats: (1) show the pain, (2) give one cheap action, (3) return to the hook for the loop. Each beat must be visualisable in one 9:16 frame.
4. Write `projects/<project>/02-script/story.json` using the schema fields below; create the `02-script` folder first. Copy `niche` and `audience` from channel config.
5. Run `python scripts/schema_validator.py story projects/<project>/02-script/story.json` and re-open the file. If validation fails, fix and re-run; log remaining problems via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Acceptance criteria**
- `story.json` passes `config/schemas/story.json`.
- `beats` has 3 items, each with `beat` (1-3) and a `purpose` naming what the viewer sees.
- `angle` names one specific action, not a vague theme.
- `niche` and `audience` are copied verbatim from channel config.

**Output format (short example)**
```json
{
  "niche": "Personal finance / side hustles",
  "audience": "Bangladesh / Bangla-speaking",
  "angle": "Resell one used phone this week",
  "hook_seed": "পুরনো ফোন দিয়েই শুরু করা যায়?",
  "source_files": ["research/niche-report.md"],
  "beats": [
    {"beat": 1, "purpose": "show an empty wallet"},
    {"beat": 2, "purpose": "list one used phone"},
    {"beat": 3, "purpose": "repeat the hook as a loop"}
  ]
}
```

**Quality rules**
1. One story, one promise — never combine two side hustles in one Short.
2. Every beat must be drawable as a flat 2D frame; drop abstract-only ideas.
3. Keep the hook seed in spoken Bangla and under 12 words.

**Output example**

```
{
  "niche": "Personal finance / side hustles",
  "audience": "Bangladesh / Bangla-speaking",
  "angle": "Resell one used phone this week",
  "hook_seed": "পুরনো ফোন দিয়েই শুরু করা যায়?",
  "source_files": ["research/niche-report.md"],
  "beats": [
    {"beat": 1, "purpose": "show an empty wallet"},
    {"beat": 2, "purpose": "list one used phone"},
    {"beat": 3, "purpose": "repeat the hook as a loop"}
  ]
}
```

### hook-writer

**Steps**

1. Read `projects/<project>/02-script/story.json` (`hook_seed`, `angle`, first beat) and `config/channel.json` + `config/style-bible.json` through project-memory. Use `language` from channel config for the hook text.
2. Choose one hook type from `question`, `shock`, `relatable`, `promise`, `contrarian`. Write the hook in one spoken sentence of at most 12 words; it must name the viewer's pain or the promised outcome from the story angle.
3. Write a `visual_prompt` in English describing one contrasting image for the first frame (for example: empty wallet → coin stack). Keep it to one flat 2D scene that a renderer can draw without extra assets.
4. Set `duration_sec` to 2.5 or 3 and write `projects/<project>/02-script/hook.json` with the fields below; create the folder first.
5. Run `python scripts/schema_validator.py hook projects/<project>/02-script/hook.json`, re-open the file, and log any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Acceptance criteria**
- `hook.json` passes `config/schemas/hook.json`.
- `text` is in the project language, at most 12 words, and matches the story `hook_seed` in meaning.
- `type` is one of the 5 allowed values and `duration_sec` is 2-3.5.
- `visual_prompt` is English, at least 8 characters, and describes exactly one frame.

**Output format (short example)**
```json
{
  "text": "পুরনো ফোন দিয়েই শুরু করা যায়?",
  "type": "question",
  "duration_sec": 3,
  "visual_prompt": "Flat 2D split frame: empty wallet on left, one coin stack on right",
  "language": "bn"
}
```

**Quality rules**
1. No polite openings ("আজ আমরা আলোচনা করব") — the first word must create tension or curiosity.
2. Do not promise unrealistic money; keep the outcome reachable in 7 days.
3. The visual prompt must not require a photo, logo, or FFmpeg effect.

**Output example**

```
{
  "text": "পুরনো ফোন দিয়েই শুরু করা যায়?",
  "type": "question",
  "duration_sec": 3,
  "visual_prompt": "Flat 2D split frame: empty wallet on left, one coin stack on right",
  "language": "bn"
}
```

### script-writer

**Steps**

1. Read `config/channel.json` and `config/style-bible.json` through project-memory for language, video length and tone. Read `projects/<project>/02-script/story.json` and `projects/<project>/02-script/hook.json`; stop if either is missing or malformed.
2. Carry the hook text into the script's `hook` field unchanged. Write `title`, `narration` and `highlight_words` in the project language; keep every `visual_prompt` in plain English so renderers can parse it.
3. Apply the real pacing rules: hook at 0-3 s, fast body from 3-45 s with sentences of 8-12 words, and a CTA or loop back to the hook in the last 3-5 s. Use the 3 story beats as scenes 1-3.
4. Save `projects/<project>/02-script/latest_script.json` with `language`, `title`, `hook`, `total_duration_sec` (30-60) and `scenes[].scene_number/narration/visual_prompt/highlight_words`. Give each scene a `duration_sec` whose sum is within 2 seconds of the total.
5. Run `python scripts/schema_validator.py latest_script projects/<project>/02-script/latest_script.json`; re-open the file and confirm each `highlight_words` entry appears in its scene narration.
6. Show a short summary in chat (title, duration, scene count). Log any problem to `projects/<project>/08-final-test/error-log.jsonl` and re-run after fixing the input.

**Acceptance criteria**
- `latest_script.json` passes `config/schemas/latest_script.json`.
- `total_duration_sec` is between 30 and 60; scene durations sum within 2 seconds.
- 3 or more scenes, each with an English `visual_prompt` and 1-2 `highlight_words` present in its narration.
- Hook text equals the approved `hook.json` text.

**Output format (short example)**
```json
{
  "language": "bn",
  "title": "টাকা ছাড়াই সাইড হাসল",
  "hook": "পুরনো ফোন দিয়েই শুরু করা যায়?",
  "total_duration_sec": 40,
  "scenes": [
    {"scene_number": 1, "narration": "অনেকের মনে হয় পুঁজি না থাকলে চলে না।",
     "visual_prompt": "Flat 2D worried person with empty wallet",
     "highlight_words": ["পুঁজি"], "duration_sec": 12}
  ]
}
```

**Quality rules**
1. One idea per sentence, max 12 words; cut adjectives that do not change the action.
2. Every visual prompt must describe a single 9:16 frame drawable in flat 2D.
3. Never add a fact, price or statistic that is not in the story or niche report.

**Output example**

```
{
  "language": "bn",
  "title": "টাকা ছাড়াই সাইড হাসল",
  "hook": "পুরনো ফোন দিয়েই শুরু করা যায়?",
  "total_duration_sec": 40,
  "scenes": [
    {"scene_number": 1, "narration": "অনেকের মনে হয় পুঁজি না থাকলে চলে না।",
     "visual_prompt": "Flat 2D worried person with empty wallet",
     "highlight_words": ["পুঁজি"], "duration_sec": 12}
  ]
}
```

### voiceover-generator

**Steps**

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `projects/<project>/02-script/latest_script.json`; if it is missing or malformed, follow Failure handling and stop. Validate `projects/<project>/02-script/latest_script.json` against `config/schemas/latest_script.json` with `python scripts/schema_validator.py latest_script projects/<project>/02-script/latest_script.json`.
3. Run `python scripts/generate_audio.py --project <project> --gender <male|female>`; it validates the script, writes `03-voice/voiceover.mp3` plus `03-voice/captions.json`, and reports the exact duration.
4. Write `projects/<project>/03-voice/voiceover.mp3` and `projects/<project>/03-voice/captions.json`; create parent folders first.
5. Re-open both files, confirm the MP3 is non-empty and report its exact duration; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`. Validate `projects/<project>/03-voice/captions.json` against `config/schemas/captions.json` with `python scripts/schema_validator.py captions projects/<project>/03-voice/captions.json` before accepting it.

**Output example**

```
(no filled Output example in SKILL.md)
```

### character-designer

**Steps**

1. Read `config/style-bible.json` (`style.palette`, `style.visual_style`, `characters`, `voice`) and `projects/<project>/02-script/latest_script.json` through project-memory. Stop if the style bible is missing or has no palette.
2. Derive one reusable character: `id` in lowercase-kebab-case, `name` in the project language, `appearance` with `body`, `hair`, `clothing` and a `palette` copied from the style bible, and `voice` with `gender` and `tone` matching the script's narrator.
3. Check the design against the real 2D constraint: simple shapes only (circle head, rounded body, 2-3 clothing shapes), no fine facial detail, no gradients, no photo texture. Describe each part in one short English phrase.
4. Write `assets/characters/<character-id>.json` at the repository root (no `projects/<project>/` prefix); create `assets/characters/` first.
5. Run `python scripts/schema_validator.py character assets/characters/<character-id>.json`, re-open the file, and log any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.
6. Render the reusable flat-shape views with `python scripts/svg_scene_builder.py character --character assets/characters/<character-id>.json --expression <neutral|smile|surprised> --out assets/characters/<character-id>-<expression>`. The helper validates the SVG, rasterizes it to PNG with the already-installed Edge renderer, and prints both exact paths. Repeat for all three expressions.

**Acceptance criteria**
- `character.json` passes `config/schemas/character.json`.
- `id` matches `^[a-z0-9-]+$` and is unique inside `assets/characters/`.
- `appearance.palette` is copied from `config/style-bible.json`, not invented.
- `voice.gender` and `voice.tone` agree with the script's narrator.
- All three `<character-id>-<expression>.svg` and `.png` files exist, parse as SVG, and are exactly 1080x1920 PNGs.

**Output format (short example)**
```json
{
  "id": "creator-01",
  "name": "অনিক",
  "style_source": "config/style-bible.json",
  "appearance": {
    "body": "slim, rounded young adult", "hair": "short black hair",
    "clothing": "simple blue shirt",
    "palette": ["#111827", "#F9FAFB", "#F59E0B", "#10B981"]
  },
  "voice": {"gender": "male", "tone": "calm and conversational"}
}
```

**Quality rules**
1. Use at most 3 clothing shapes so the look stays consistent across scenes.
2. Keep hair, shirt and palette identical for this `id` in every scene.
3. Do not add a second character here; create a new file with a new `id` instead.
4. Reuse `scripts/svg_scene_builder.py` for every expression; never hand-edit the generated SVG or PNG.

**Output example**

```
{
  "id": "creator-01",
  "name": "অনিক",
  "style_source": "config/style-bible.json",
  "appearance": {
    "body": "slim, rounded young adult", "hair": "short black hair",
    "clothing": "simple blue shirt",
    "palette": ["#111827", "#F9FAFB", "#F59E0B", "#10B981"]
  },
  "voice": {"gender": "male", "tone": "calm and conversational"}
}
```

### video-maker

**Steps**

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `projects/<project>/05-scene/collection.json`; if it is missing or malformed, follow Failure handling and stop. Validate `projects/<project>/05-scene/collection.json` against `config/schemas/collection.json` with `python scripts/schema_validator.py collection projects/<project>/05-scene/collection.json`.
3. Run `python scripts/skill_tools.py video-maker run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/06-video/scenes/` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/06-video/scenes/` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.
6. If `requires: ffmpeg` is set, call `scripts/skill_lib.py::require_ffmpeg()` which reads `FFMPEG_PATH`; on `BLOCKED` print `BLOCKED video-maker: ffmpeg ...` and exit 0 without a FAIL.

**Output example**

```
(no filled Output example in SKILL.md)
```

### caption-maker

**Steps**

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `projects/<project>/03-voice/captions.json + projects/<project>/07-edit/rough-cut.mp4`; if it is missing or malformed, follow Failure handling and stop. Validate `projects/<project>/03-voice/captions.json` against `config/schemas/captions.json` with `python scripts/schema_validator.py captions projects/<project>/03-voice/captions.json`.
3. Run `python scripts/skill_tools.py caption-maker run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/07-edit/captions.json + projects/<project>/07-edit/caption-maker.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/07-edit/captions.json + projects/<project>/07-edit/caption-maker.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`. Validate `projects/<project>/07-edit/captions.json` against `config/schemas/captions.json` with `python scripts/schema_validator.py captions projects/<project>/07-edit/captions.json` before accepting it.

**Output example**

```
(no filled Output example in SKILL.md)
```

### safe-zone-checker

**Steps**

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `captioned video`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py safe-zone-checker run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/07-edit/safe-zone-checker.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/07-edit/safe-zone-checker.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Output example**

```
(no filled Output example in SKILL.md)
```

### bug-finder

**Steps**

1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.
2. Validate the input at `final video + reports`; if it is missing or malformed, follow Failure handling and stop.
3. Run `python scripts/skill_tools.py bug-finder run` with `PROJECT=<project>`; the helper reads context through `scripts/skill_lib.py::style_context()`.
4. Write the result to `projects/<project>/08-final-test/bug-finder.json` inside the current project under projects/<project>/; create parent folders first.
5. Re-open `projects/<project>/08-final-test/bug-finder.json` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Output example**

```
(no filled Output example in SKILL.md)
```

### handover

**Steps**

1. Read `config/channel.json` and `config/style-bible.json` through project-memory so the handover lists the real niche, language and location.
2. Check these four final assets by exact path: `projects/<project>/08-final-test/final-video.mp4`, `projects/<project>/07-edit/captions.json`, `projects/<project>/09-description/description.md`, `projects/<project>/10-publish/handover.md`. List every missing path; do not publish while any is missing.
3. Validate `projects/<project>/07-edit/captions.json` with `python scripts/schema_validator.py captions projects/<project>/07-edit/captions.json`. Run `python scripts/skill_tools.py handover run` with `PROJECT=<project>` to write `handover-check.json`.
4. Write `projects/<project>/10-publish/handover.md` with the exact sections shown below: asset checklist with PASS/MISSING, exact publish path, duration from captions `total_duration_sec`, and any `BLOCKED` items from FFmpeg skills.
5. Re-open both `handover.md` and `handover-check.json`; confirm `ready` matches the checklist and the file list is identical. Log any mismatch via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.

**Acceptance criteria**
- `handover.md` and `handover-check.json` both exist under `projects/<project>/10-publish/`.
- Every checked asset appears with its exact relative path and a PASS or MISSING status.
- Captions pass `config/schemas/captions.json` and the duration is copied from that file.
- `ready` is true only when all four assets are present.

**Output format (short example)**
```markdown

**Output example**

```
# Handover — my-video
Niche: Personal finance / side hustles | Language: bn

## Assets
- PASS projects/my-video/08-final-test/final-video.mp4
- PASS projects/my-video/07-edit/captions.json
- MISSING projects/my-video/09-description/description.md

## Publish
Path: projects/my-video/08-final-test/final-video.mp4
Duration: 40.0 s (from captions.json)
Blocked: video-maker (ffmpeg BLOCKED by application control)
Ready: no
```

## 7. Review boundaries

- Nothing was fixed. No skill, script, schema, config, `.env` or Windows setting was modified.
- No package was installed; no token was used; no push or force push was made.
- `projects/review-tmp` was deleted; `git status --short` is clean except for this report.

