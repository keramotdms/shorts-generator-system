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
## LOGIN RULE

- Trigger: I write "Login into Home PC" / "Log in to Home PC" (also accept "Office", and small spelling variations).
- Step 1: git pull origin main. Show the latest commit.
- Step 2: Remember which PC I am on in this session (Home or Office).
- Step 3: Read docs/SESSION-LOG.md and select the last 3 entries from the OTHER PC only:
  * I log in to Home -> show the last 3 Office PC sessions
  * I log in to Office -> show the last 3 Home PC sessions
- Step 4: For each of the 3 entries show: date, commit hash, what was done, what is pending. Then give a combined "pending list" and one suggested next step. Then wait.
- If the other PC has fewer than 3 entries, show what exists and say how many. If it has none, say so clearly. Do not invent entries.
- Never show this PC's own entries unless I ask.

## END SESSION RULE

- When I say "end session" (or the session finishes), add an entry to docs/SESSION-LOG.md with: date, PC (Home or Office, from my login message; if unknown, ask me once), last commit hash, what was done (3-5 lines), what is pending, next step.
- Then run health_check.py, commit, push, confirm main == origin/main.

## PC ROLES

- `PC_ROLE=home|office` lives in `.env` (see `.env.example`).
- **Home PC = production.** Voice generation, rendering, FFmpeg work and package installs happen here.
- **Office PC = text/skills/docs only.** Scripts, skill content, docs and reviews; no installs.
- On the Office PC, a missing `edge-tts`, `pytrends` or Bangla font is `INFO`, not `FAIL`.
- On the Home PC, those same gaps are `WARN` so they get fixed before production.
- Never change Windows security settings to make a blocked tool run; find a working path instead.

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
- voiceover-generator
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

- `voiceover-captions` currently combines voice + captions. See `config/skill-contracts.json` for the proposed split into `voiceover-generator` and `caption-maker`. Do not write those new skill contents yet.
