# Roadmap

## Pipeline order

Research -> Script -> Voice -> Character -> Scene -> Video -> Edit -> Final Test -> Description/SEO -> Publish

## MVP skills (19, build one at a time)

### Phase 1 - Foundation

- orchestrator (implemented)
- project-memory (implemented)
- asset-manager (implemented)
- pipeline-health-checker (implemented)
- book-finder (implemented)
- trend-finder (implemented)

### Phase 2 - Content

- story-thinker (implemented)
- hook-writer (implemented)
- script-writer (implemented)

### Phase 3 - Production

- voiceover-generator (implemented)
- character-designer (implemented)
- script-voice-character-collector (implemented)
- video-maker (implemented)

### Phase 4 - Edit

- rough-cut-assembler (implemented)
- caption-maker (implemented)
- safe-zone-checker (implemented)

### Phase 5 - Finish

- bug-finder (implemented)
- description-maker (implemented)
- handover (implemented)

## Legacy / compatibility

- `voiceover-captions` - legacy skill that combines voice and captions. It will be split into `voiceover-generator` (Phase 3) and `caption-maker` (Phase 4). See `config/skill-contracts.json`.

## All skills by category

### core

- orchestrator — implemented, phase 1
- project-memory — implemented, phase 1
- task-tracker — implemented, phase later
- asset-manager — implemented, phase 1
- error-log-keeper — implemented, phase later
- pipeline-health-checker — implemented, phase 1

### research

- book-finder — implemented, phase 1
- trend-finder — implemented, phase 1
- competitor-analyzer — implemented, phase later
- audience-persona-builder — implemented, phase later
- fact-checker — implemented, phase later
- content-calendar — implemented, phase later

### script

- story-thinker — implemented, phase 2
- story-organizer — implemented, phase later
- hook-writer — implemented, phase 2
- script-writer — implemented, phase 2
- retention-pacing-optimizer — implemented, phase later
- loop-cta-designer — implemented, phase later
- script-tester — implemented, phase later
- script-user-tester — implemented, phase later
- localization — implemented, phase later

### voice

- voiceover-organizer — implemented, phase later
- pronunciation-emotion-director — implemented, phase later
- voiceover-generator — implemented, phase 3
- voiceover-tester — implemented, phase later
- music-sfx-selector — implemented, phase later
- audio-mixer — implemented, phase later
- voiceover-captions — legacy, phase later

### character

- character-thinker-counter — implemented, phase later
- character-organizer — implemented, phase later
- character-designer — implemented, phase 3
- character-setup-manager — implemented, phase later
- expression-pose-library — implemented, phase later
- consistency-guardian — implemented, phase later
- character-qa-tester — implemented, phase later

### scene

- element-designer — implemented, phase later
- element-organizer — implemented, phase later
- scenario-designer — implemented, phase later

### video-making

- script-voice-character-collector — implemented, phase 3
- lipsync-motion-planner — implemented, phase later
- video-maker — implemented, phase 3
- video-quality-checker — implemented, phase later

### video-editing

- script-video-voice-collector — implemented, phase later
- rough-cut-assembler — implemented, phase 4
- video-editor — implemented, phase later
- animator — implemented, phase later
- motion-graphic-editor — implemented, phase later
- branding-manager — implemented, phase later
- cut-rhythm-editor — implemented, phase later
- pattern-interrupt-inserter — implemented, phase later
- hook-visual-editor — implemented, phase later
- seamless-loop-editor — implemented, phase later
- virtual-camera-planner — implemented, phase later
- transition-designer — implemented, phase later
- color-grading-keeper — implemented, phase later
- broll-variety-planner — implemented, phase later
- caption-maker — implemented, phase 4
- kinetic-text-animator — implemented, phase later
- emphasis-sticker-placer — implemented, phase later
- intro-outro-manager — implemented, phase later
- watermark-logo-placer — implemented, phase later
- beat-sync-editor — implemented, phase later
- audio-ducking-controller — implemented, phase later
- sfx-timing-placer — implemented, phase later
- av-sync-checker — implemented, phase later
- template-preset-manager — implemented, phase later
- safe-zone-checker — implemented, phase 4
- preview-frame-extractor — implemented, phase later
- format-converter — implemented, phase later
- thumbnail-designer — implemented, phase later
- render-export-optimizer — implemented, phase later
- variant-batch-renderer — implemented, phase later
- stock-asset-finder — implemented, phase later

### final-test

- red-team — implemented, phase later
- ruthless-team — implemented, phase later
- bug-finder — implemented, phase 5
- solver — implemented, phase later
- copyright-policy-checker — implemented, phase later
- platform-compliance-checker — implemented, phase later
- accessibility-safety-checker — implemented, phase later
- handover — implemented, phase 5

### marketing

- description-maker — implemented, phase 5
- copywriter — implemented, phase later
- seo-specialist — implemented, phase later
- marketing-specialist — implemented, phase later

### growth

- youtube-seo-specialist — implemented, phase later
- youtube-analyst — implemented, phase later
- analytics-feedback-loop — implemented, phase later
- scheduler-publisher — implemented, phase later
- cross-platform-repurposer — implemented, phase later
- comment-community-manager — implemented, phase later
- ab-tester — implemented, phase later
- monetization-tracker — implemented, phase later

## Pending decisions

- FFmpeg: installed but `ffmpeg.exe` is blocked by Windows Smart App Control. Revisit before video skills.
- Niche and language remain pending confirmation in the live pipeline (config defaults are placeholders).

Full skill table: `docs/SKILL-INDEX.md`.
