# AGENTS.md — Project Rules

## Who / what

Beginner-friendly, step-by-step build of an automated system for 2D animated YouTube Shorts and Facebook Reels (30–60 seconds, vertical 9:16). You are the senior engineering partner.

## Confirmed decisions

- Niche: Personal finance / side hustles
- Language: Bangla
- Audience: Bangladesh / Bangla-speaking
- Video length: 30–60 seconds, 9:16
- Editing/rendering: FFmpeg + Python

## Rules

1. Do NOT build everything at once. Build only MVP skills first.
2. Build ONE skill at a time. After each, show what was made and how to test it, then wait for OK.
3. Before installing any tool or package, tell the user what and why, and ask.
4. Keep everything organized in the GitHub repo with clear folders, naming rules, and a commit after each finished skill.
5. Explain things in simple language.
6. If anything is unclear, ask 1–2 questions before proceeding.
7. Log mistakes and lessons in `docs/lessons.md` so they are not repeated.
8. Every skill must have: purpose, input, output, steps, and a way to test it.
9. Skill naming rule: lowercase-kebab-case, no `shorts-` prefix.
10. Generated project data lives under `projects/<project>/<stage>/`, never inside skill folders.

## Pipeline order

Research -> Script -> Voice -> Character -> Scene -> Video -> Edit -> Final Test -> Description/SEO -> Publish

## MVP skill list

### Phase 1 — Foundation
- orchestrator
- project-memory
- asset-manager
- book-finder
- trend-finder
- pipeline-health-checker

### Phase 2 — Content
- story-thinker
- hook-writer
- script-writer

### Phase 3 — Production
- voice-over-generator
- character-designer
- script-voice-character-collector
- video-maker

### Phase 4 — Edit
- rough-cut-assembler
- caption-maker
- safe-zone-checker

### Phase 5 — Finish
- bug-finder
- description-maker
- handover

## Legacy compatibility

- `voiceover-captions` currently combines voice + captions. See `config/skill-contracts.json` for the proposed split into `voice-over-generator` and `caption-maker`. Do not write those new skill contents yet.
