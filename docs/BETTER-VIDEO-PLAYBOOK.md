# Better Than The Reference — Video Playbook

Date: 2026-11-27 | PC: Office
Goal: given a voiceover + script, output a Short that beats the two reference videos in
clarity, consistency and reliability. Uses only our own pipeline; no reference asset is reused.

## What the references do well (keep)

1. One story, one character on screen at a time, caption pill locked to the same spot.
2. A hero motion graphic every 2-3 scenes (chat, clock, result table, law card) so the eye resets.
3. Yellow keyword highlighting inside a black pill — readable at thumbnail size.
4. Slow zoom on static art instead of static frames, so nothing looks frozen.

## Where they fall short (beat them here)

| Weakness in references | Our fix |
| --- | --- |
| 360p source, soft edges and mushy text | Render at 1080x1920 from vector SVG, so text stays crisp |
| Result numbers and names unreadable | One number per card, 64 px minimum glyph height |
| Watermark sits over faces/props | Watermark in a reserved safe corner, never over the face |
| Captions run under the right-side UI | Caption box ends 140 px before the right edge |
| Repeated beats (same tears shot twice) | Shot list de-duplicates poses per scene |
| Uneven cuts (0 s burst, then 30 s drift) | Cut every 6-9 s, one motion graphic per 2-3 scenes |
| No breathing room in audio | Keep 0.3-0.5 s of music between narration lines |

## Our built-in advantages

- `character-designer` pro detail (40 layers, 8 skin tones, 11 outfits, 5 props) with a locked
  identity: same outline width and light direction across creator, mentor and learner.
- `svg_scene_builder` renders deterministic SVG → PNG with the installed Edge converter.
- `scenario-designer` gives one job per 9:16 scene; `safe-zone-checker` proves caption placement.
- `caption-maker` produces word timings, so captions and mouth shapes follow the real voiceover.
- `render-export-optimizer` checks 1080x1920 / 30 fps / h264 / faststart before handover.

## Scene recipe for a 60 s Short

1. 0-3 s: hook — face close-up + title chip, no caption yet.
2. 3-12 s: beat 1 — medium shot, slow 6% zoom, caption pill bottom-centre.
3. 12-20 s: beat 2 — hero motion graphic (chat / clock / result card).
4. 20-30 s: beat 3 — two-shot or split-screen, cut on the stressed word.
5. 30-42 s: beat 4 — reaction close-up, one prop (coin, notebook, bar-graph board).
6. 42-52 s: beat 5 — payoff motion graphic (stamp, law card, money rain).
7. 52-60 s: end card — channel name, posting schedule, subscribe pill, copyright line.

## Quality rules (checkable)

- Resolution exactly 1080x1920, 30 fps, h264 High, yuv420p, faststart, ≤60 s.
- Caption contrast ≥ 4.5:1 against its pill; pill fully inside the safe zone.
- Skin/outline contrast ≥ 3.0; palette only from `config/style-bible.json`.
- One cut every 6-9 s; no shot shorter than 1.5 s.
- Every scene has a unique layer id set; two renders of the same scene are byte-identical.
- Narration loudness ≈ -14 LUFS with a continuous music bed, no gap ≥0.4 s at -32 dB.

## Pipeline mapping

script-writer → voiceover-generator → character-designer → scenario-designer →
svg_scene_builder → caption-maker → safe-zone-checker → rough-cut-assembler →
video-maker → render-export-optimizer → description-maker → handover
