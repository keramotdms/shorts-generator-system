# Roadmap

## Pipeline order

Research -> Script -> Voice -> Character -> Scene -> Video -> Edit -> Final Test -> Description/SEO -> Publish

## MVP skills (19, build one at a time)

### Phase 1 - Foundation

- orchestrator (implemented)
- project-memory
- asset-manager
- pipeline-health-checker
- book-finder
- trend-finder

### Phase 2 - Content

- story-thinker
- hook-writer
- script-writer (implemented)

### Phase 3 - Production

- voiceover-generator
- character-designer
- script-voice-character-collector
- video-maker

### Phase 4 - Edit

- rough-cut-assembler
- caption-maker
- safe-zone-checker

### Phase 5 - Finish

- bug-finder
- description-maker
- handover

## Legacy / compatibility

- `voiceover-captions` - legacy skill that combines voice and captions. It will be split into `voiceover-generator` (Phase 3) and `caption-maker` (Phase 4). See `config/skill-contracts.json`.

## All skills by category

### core

- orchestrator — mvp, phase 1
- project-memory — mvp, phase 1
- task-tracker — planned, phase later
- asset-manager — mvp, phase 1
- error-log-keeper — planned, phase later
- pipeline-health-checker — mvp, phase 1

### research

- book-finder — mvp, phase 1
- trend-finder — mvp, phase 1
- competitor-analyzer — planned, phase later
- audience-persona-builder — planned, phase later
- fact-checker — planned, phase later
- content-calendar — planned, phase later

### script

- story-thinker — mvp, phase 2
- story-organizer — planned, phase later
- hook-writer — mvp, phase 2
- script-writer — mvp, phase 2
- retention-pacing-optimizer — planned, phase later
- loop-cta-designer — planned, phase later
- script-tester — planned, phase later
- script-user-tester — planned, phase later
- localization — planned, phase later

### voice

- voiceover-organizer — planned, phase later
- pronunciation-emotion-director — planned, phase later
- voiceover-generator — mvp, phase 3
- voiceover-tester — planned, phase later
- music-sfx-selector — planned, phase later
- audio-mixer — planned, phase later
- voiceover-captions — legacy, phase later

### character

- character-thinker-counter — planned, phase later
- character-organizer — planned, phase later
- character-designer — mvp, phase 3
- character-setup-manager — planned, phase later
- expression-pose-library — planned, phase later
- consistency-guardian — planned, phase later
- character-qa-tester — planned, phase later

### scene

- element-designer — planned, phase later
- element-organizer — planned, phase later
- scenario-designer — planned, phase later

### video-making

- script-voice-character-collector — mvp, phase 3
- lipsync-motion-planner — planned, phase later
- video-maker — mvp, phase 3
- video-quality-checker — planned, phase later

### video-editing

- script-video-voice-collector — planned, phase later
- rough-cut-assembler — mvp, phase 4
- video-editor — planned, phase later
- animator — planned, phase later
- motion-graphic-editor — planned, phase later
- branding-manager — planned, phase later
- cut-rhythm-editor — planned, phase later
- pattern-interrupt-inserter — planned, phase later
- hook-visual-editor — planned, phase later
- seamless-loop-editor — planned, phase later
- virtual-camera-planner — planned, phase later
- transition-designer — planned, phase later
- color-grading-keeper — planned, phase later
- broll-variety-planner — planned, phase later
- caption-maker — mvp, phase 4
- kinetic-text-animator — planned, phase later
- emphasis-sticker-placer — planned, phase later
- intro-outro-manager — planned, phase later
- watermark-logo-placer — planned, phase later
- beat-sync-editor — planned, phase later
- audio-ducking-controller — planned, phase later
- sfx-timing-placer — planned, phase later
- av-sync-checker — planned, phase later
- template-preset-manager — planned, phase later
- safe-zone-checker — mvp, phase 4
- preview-frame-extractor — planned, phase later
- format-converter — planned, phase later
- thumbnail-designer — planned, phase later
- render-export-optimizer — planned, phase later
- variant-batch-renderer — planned, phase later
- stock-asset-finder — planned, phase later

### final-test

- red-team — planned, phase later
- ruthless-team — planned, phase later
- bug-finder — mvp, phase 5
- solver — planned, phase later
- copyright-policy-checker — planned, phase later
- platform-compliance-checker — planned, phase later
- accessibility-safety-checker — planned, phase later
- handover — mvp, phase 5

### marketing

- description-maker — mvp, phase 5
- copywriter — planned, phase later
- seo-specialist — planned, phase later
- marketing-specialist — planned, phase later

### growth

- youtube-seo-specialist — planned, phase later
- youtube-analyst — planned, phase later
- analytics-feedback-loop — planned, phase later
- scheduler-publisher — planned, phase later
- cross-platform-repurposer — planned, phase later
- comment-community-manager — planned, phase later
- ab-tester — planned, phase later
- monetization-tracker — planned, phase later

## Pending decisions

- FFmpeg: installed but `ffmpeg.exe` is blocked by Windows Smart App Control. Revisit before video skills.
- Niche and language remain pending confirmation in the live pipeline (config defaults are placeholders).

Full skill table: `docs/SKILL-INDEX.md`.