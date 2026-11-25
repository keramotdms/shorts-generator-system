# Output formats

One format profile per output. `config/output-formats.json` is the registry;
`config/skill-contracts.json` binds every output path to exactly one profile.
`scripts/format_validator.py` performs the checks. A skill may not write another
format until its contract and SKILL.md Output section are changed first.

## Profiles

| Profile | Extension | Encoding / codec | Checkable parameters |
| --- | --- | --- | --- |
| `json_utf8` | `.json` | utf-8 | valid_json=True, no_bom=True, utf8=True |
| `markdown` | `.md` | utf-8 | no_bom=True, utf8=True, non_empty=True |
| `jsonl` | `.jsonl` | utf-8 | valid_jsonl=True, no_bom=True, utf8=True |
| `csv` | `.csv` | utf-8 | valid_csv=True, no_bom=True, utf8=True |
| `mp3_voice` | `.mp3` | binary | ffprobe=True, container_in=['mp3'], audio_codec=mp3, sample_rate_in=[44100, 48000], channels_max=2, max_duration_sec=120 |
| `wav_mix` | `.wav` | binary | ffprobe=True, container_in=['wav'], audio_codec_in=['pcm_s16le', 'pcm_s24le', 'pcm_f32le'], sample_rate=48000, channels_max=2, max_duration_sec=120 |
| `srt` | `.srt` | utf-8 | valid_srt=True, no_bom=True, utf8=True |
| `svg_layered` | `.svg` | utf-8 | valid_xml=True, root_svg=True, layer_groups_min=1, no_bom=True |
| `png_transparent` | `.png` | binary | png_signature=True, width_min=1, height_min=1, alpha_allowed=True |
| `png_frame_1080x1920` | `.png` | binary | png_signature=True, width=1080, height=1920, color_type_in=[2, 6] |
| `ttf_font` | `.ttf` | binary | font_signature=True |
| `mp4_clip` | `.mp4` | binary | ffprobe=True, container=mp4, video_codec=h264, pixel_format=yuv420p, width=1080, height=1920, fps=30, audio_codec_in=['aac', 'none'], max_duration_sec=60 |
| `mp4_final` | `.mp4` | binary | ffprobe=True, container=mp4, video_codec=h264, video_profile=High, pixel_format=yuv420p, width=1080, height=1920, fps=30, audio_codec=aac, audio_sample_rate=48000, faststart=True, max_duration_sec=60, max_duration_exclusive=True |

## Output path -> profile, writer and readers

| Output path | Format profile | Written by | Read by |
| --- | --- | --- | --- |
| `assets/characters/creator-01-neutral.png` | `png_transparent` | character-designer | _(none in contracts)_ |
| `assets/characters/creator-01-neutral.svg` | `svg_layered` | character-designer | _(none in contracts)_ |
| `assets/characters/creator-01-smile.png` | `png_transparent` | character-designer | _(none in contracts)_ |
| `assets/characters/creator-01-smile.svg` | `svg_layered` | character-designer | _(none in contracts)_ |
| `assets/characters/creator-01-surprised.png` | `png_transparent` | character-designer | _(none in contracts)_ |
| `assets/characters/creator-01-surprised.svg` | `svg_layered` | character-designer | _(none in contracts)_ |
| `assets/characters/creator-01/character.json` | `json_utf8` | character-designer | character-qa-tester, character-setup-manager, consistency-guardian, copyright-policy-checker, expression-pose-library, lipsync-motion-planner, script-voice-character-collector |
| `assets/characters/creator-01/compare.png` | `png_transparent` | character-designer | _(none in contracts)_ |
| `assets/characters/creator-01/layered.svg` | `svg_layered` | character-designer | _(none in contracts)_ |
| `assets/characters/creator-01/preview-sheet.png` | `png_transparent` | character-designer | _(none in contracts)_ |
| `assets/characters/creator-01/preview.png` | `png_transparent` | character-designer | _(none in contracts)_ |
| `assets/scenes/scene-warm-desk-smile.png` | `png_transparent` | scenario-designer | script-voice-character-collector |
| `assets/scenes/warm-desk-background.svg` | `svg_layered` | scenario-designer | _(none in contracts)_ |
| `config/style-bible.json` | `json_utf8` | project-memory | branding-manager, character-designer, character-thinker-counter, color-grading-keeper, element-designer, intro-outro-manager, motion-graphic-editor, music-sfx-selector, scenario-designer, stock-asset-finder, template-preset-manager, transition-designer, voiceover-organizer, watermark-logo-placer |
| `projects/<project>/01-research/audience-persona-builder.json` | `json_utf8` | audience-persona-builder | copywriter, marketing-specialist |
| `projects/<project>/01-research/competitor-analyzer.json` | `json_utf8` | competitor-analyzer | _(none in contracts)_ |
| `projects/<project>/01-research/content-calendar.json` | `json_utf8` | content-calendar | _(none in contracts)_ |
| `projects/<project>/01-research/fact-checker.json` | `json_utf8` | fact-checker | _(none in contracts)_ |
| `projects/<project>/01-research/niche-report.md` | `markdown` | book-finder | audience-persona-builder, competitor-analyzer, content-calendar, story-thinker |
| `projects/<project>/02-script/hook.json` | `json_utf8` | hook-writer | hook-visual-editor, pattern-interrupt-inserter, script-writer |
| `projects/<project>/02-script/latest_script.json` | `json_utf8` | script-writer | broll-variety-planner, character-thinker-counter, copyright-policy-checker, copywriter, cut-rhythm-editor, description-maker, element-designer, emphasis-sticker-placer, fact-checker, localization, loop-cta-designer, music-sfx-selector, pronunciation-emotion-director, red-team, retention-pacing-optimizer, scenario-designer, script-tester, script-user-tester, script-voice-character-collector, seo-specialist, stock-asset-finder, thumbnail-designer, variant-batch-renderer, voiceover-captions, voiceover-generator, voiceover-organizer, voiceover-tester |
| `projects/<project>/02-script/localization.json` | `json_utf8` | localization | _(none in contracts)_ |
| `projects/<project>/02-script/loop-cta-designer.json` | `json_utf8` | loop-cta-designer | seamless-loop-editor |
| `projects/<project>/02-script/retention-pacing-optimizer.json` | `json_utf8` | retention-pacing-optimizer | _(none in contracts)_ |
| `projects/<project>/02-script/script-tester.json` | `json_utf8` | script-tester | _(none in contracts)_ |
| `projects/<project>/02-script/script-user-tester.json` | `json_utf8` | script-user-tester | _(none in contracts)_ |
| `projects/<project>/02-script/story-organizer.json` | `json_utf8` | story-organizer | _(none in contracts)_ |
| `projects/<project>/02-script/story.json` | `json_utf8` | story-thinker | hook-writer, script-writer, story-organizer |
| `projects/<project>/03-voice/audio-mixer.json` | `json_utf8` | audio-mixer | _(none in contracts)_ |
| `projects/<project>/03-voice/captions.json` | `json_utf8` | voiceover-captions, voiceover-generator | caption-maker, lipsync-motion-planner |
| `projects/<project>/03-voice/music-sfx-selector.json` | `json_utf8` | music-sfx-selector | audio-ducking-controller, audio-mixer, beat-sync-editor, sfx-timing-placer |
| `projects/<project>/03-voice/pronunciation-emotion-director.json` | `json_utf8` | pronunciation-emotion-director | _(none in contracts)_ |
| `projects/<project>/03-voice/voiceover-organizer.json` | `json_utf8` | voiceover-organizer | pronunciation-emotion-director |
| `projects/<project>/03-voice/voiceover-tester.json` | `json_utf8` | voiceover-tester | _(none in contracts)_ |
| `projects/<project>/03-voice/voiceover.mp3` | `mp3_voice` | voiceover-captions, voiceover-generator | accessibility-safety-checker, audio-ducking-controller, audio-mixer, script-voice-character-collector, voiceover-tester |
| `projects/<project>/04-character/character-design-set.json` | `json_utf8` | character-designer | _(none in contracts)_ |
| `projects/<project>/04-character/character-organizer.json` | `json_utf8` | character-organizer | _(none in contracts)_ |
| `projects/<project>/04-character/character-qa-tester.json` | `json_utf8` | character-qa-tester | _(none in contracts)_ |
| `projects/<project>/04-character/character-setup-manager.json` | `json_utf8` | character-setup-manager | _(none in contracts)_ |
| `projects/<project>/04-character/character-thinker-counter.json` | `json_utf8` | character-thinker-counter | character-organizer |
| `projects/<project>/04-character/consistency-guardian.json` | `json_utf8` | consistency-guardian | _(none in contracts)_ |
| `projects/<project>/04-character/expression-pose-library.json` | `json_utf8` | expression-pose-library | _(none in contracts)_ |
| `projects/<project>/05-scene/collection.json` | `json_utf8` | script-voice-character-collector | rough-cut-assembler, script-video-voice-collector, video-maker |
| `projects/<project>/05-scene/element-designer.json` | `json_utf8` | element-designer | element-organizer |
| `projects/<project>/05-scene/element-organizer.json` | `json_utf8` | element-organizer | animator |
| `projects/<project>/05-scene/scenario-designer.json` | `json_utf8` | scenario-designer | virtual-camera-planner |
| `projects/<project>/06-video/lipsync-motion-planner.json` | `json_utf8` | lipsync-motion-planner | _(none in contracts)_ |
| `projects/<project>/06-video/scenes/` | `mp4_clip` | video-maker | consistency-guardian, rough-cut-assembler, script-video-voice-collector, video-quality-checker |
| `projects/<project>/06-video/video-maker-report.json` | `json_utf8` | video-maker | _(none in contracts)_ |
| `projects/<project>/06-video/video-quality-checker.json` | `json_utf8` | video-quality-checker | _(none in contracts)_ |
| `projects/<project>/07-edit/animator.json` | `json_utf8` | animator | _(none in contracts)_ |
| `projects/<project>/07-edit/audio-ducking-controller.json` | `json_utf8` | audio-ducking-controller | _(none in contracts)_ |
| `projects/<project>/07-edit/av-sync-checker.json` | `json_utf8` | av-sync-checker | _(none in contracts)_ |
| `projects/<project>/07-edit/beat-sync-editor.json` | `json_utf8` | beat-sync-editor | _(none in contracts)_ |
| `projects/<project>/07-edit/branding-manager.json` | `json_utf8` | branding-manager | _(none in contracts)_ |
| `projects/<project>/07-edit/broll-variety-planner.json` | `json_utf8` | broll-variety-planner | _(none in contracts)_ |
| `projects/<project>/07-edit/caption-maker.json` | `json_utf8` | caption-maker | _(none in contracts)_ |
| `projects/<project>/07-edit/captioned.mp4` | `mp4_clip` | caption-maker | beat-sync-editor, emphasis-sticker-placer, intro-outro-manager, kinetic-text-animator, render-export-optimizer, safe-zone-checker, sfx-timing-placer, watermark-logo-placer |
| `projects/<project>/07-edit/captions.json` | `json_utf8` | caption-maker | accessibility-safety-checker, handover, kinetic-text-animator, safe-zone-checker |
| `projects/<project>/07-edit/color-grading-keeper.json` | `json_utf8` | color-grading-keeper | _(none in contracts)_ |
| `projects/<project>/07-edit/cut-rhythm-editor.json` | `json_utf8` | cut-rhythm-editor | _(none in contracts)_ |
| `projects/<project>/07-edit/emphasis-sticker-placer.json` | `json_utf8` | emphasis-sticker-placer | _(none in contracts)_ |
| `projects/<project>/07-edit/format-converter.json` | `json_utf8` | format-converter | _(none in contracts)_ |
| `projects/<project>/07-edit/hook-visual-editor.json` | `json_utf8` | hook-visual-editor | _(none in contracts)_ |
| `projects/<project>/07-edit/intro-outro-manager.json` | `json_utf8` | intro-outro-manager | _(none in contracts)_ |
| `projects/<project>/07-edit/kinetic-text-animator.json` | `json_utf8` | kinetic-text-animator | _(none in contracts)_ |
| `projects/<project>/07-edit/motion-graphic-editor.json` | `json_utf8` | motion-graphic-editor | _(none in contracts)_ |
| `projects/<project>/07-edit/pattern-interrupt-inserter.json` | `json_utf8` | pattern-interrupt-inserter | _(none in contracts)_ |
| `projects/<project>/07-edit/preview-frame-extractor.json` | `json_utf8` | preview-frame-extractor | _(none in contracts)_ |
| `projects/<project>/07-edit/render-export-optimizer.json` | `json_utf8` | render-export-optimizer | _(none in contracts)_ |
| `projects/<project>/07-edit/rough-cut-assembler-report.json` | `json_utf8` | rough-cut-assembler | _(none in contracts)_ |
| `projects/<project>/07-edit/rough-cut.mp4` | `mp4_clip` | rough-cut-assembler | animator, branding-manager, caption-maker, color-grading-keeper, cut-rhythm-editor, hook-visual-editor, motion-graphic-editor, pattern-interrupt-inserter, seamless-loop-editor, transition-designer, video-editor |
| `projects/<project>/07-edit/safe-zone-checker.json` | `json_utf8` | safe-zone-checker | _(none in contracts)_ |
| `projects/<project>/07-edit/script-video-voice-collector.json` | `json_utf8` | script-video-voice-collector | video-editor |
| `projects/<project>/07-edit/seamless-loop-editor.json` | `json_utf8` | seamless-loop-editor | _(none in contracts)_ |
| `projects/<project>/07-edit/sfx-timing-placer.json` | `json_utf8` | sfx-timing-placer | _(none in contracts)_ |
| `projects/<project>/07-edit/stock-asset-finder.json` | `json_utf8` | stock-asset-finder | broll-variety-planner |
| `projects/<project>/07-edit/template-preset-manager.json` | `json_utf8` | template-preset-manager | variant-batch-renderer |
| `projects/<project>/07-edit/thumbnail-designer.json` | `json_utf8` | thumbnail-designer | _(none in contracts)_ |
| `projects/<project>/07-edit/transition-designer.json` | `json_utf8` | transition-designer | _(none in contracts)_ |
| `projects/<project>/07-edit/variant-batch-renderer.json` | `json_utf8` | variant-batch-renderer | _(none in contracts)_ |
| `projects/<project>/07-edit/video-editor.json` | `json_utf8` | video-editor | template-preset-manager |
| `projects/<project>/07-edit/virtual-camera-planner.json` | `json_utf8` | virtual-camera-planner | _(none in contracts)_ |
| `projects/<project>/07-edit/watermark-logo-placer.json` | `json_utf8` | watermark-logo-placer | _(none in contracts)_ |
| `projects/<project>/08-final-test/accessibility-safety-checker.json` | `json_utf8` | accessibility-safety-checker | _(none in contracts)_ |
| `projects/<project>/08-final-test/bug-finder.json` | `json_utf8` | bug-finder | description-maker, solver |
| `projects/<project>/08-final-test/copyright-policy-checker.json` | `json_utf8` | copyright-policy-checker | _(none in contracts)_ |
| `projects/<project>/08-final-test/error-log.jsonl` | `jsonl` | error-log-keeper | _(none in contracts)_ |
| `projects/<project>/08-final-test/final-video.mp4` | `mp4_final` | render-export-optimizer | accessibility-safety-checker, av-sync-checker, bug-finder, copyright-policy-checker, cross-platform-repurposer, format-converter, handover, marketing-specialist, pipeline-health-checker, platform-compliance-checker, preview-frame-extractor, red-team, ruthless-team, thumbnail-designer |
| `projects/<project>/08-final-test/platform-compliance-checker.json` | `json_utf8` | platform-compliance-checker | _(none in contracts)_ |
| `projects/<project>/08-final-test/red-team.json` | `json_utf8` | red-team | bug-finder |
| `projects/<project>/08-final-test/ruthless-team.json` | `json_utf8` | ruthless-team | bug-finder |
| `projects/<project>/08-final-test/solver.json` | `json_utf8` | solver | _(none in contracts)_ |
| `projects/<project>/09-description/copywriter.md` | `markdown` | copywriter | _(none in contracts)_ |
| `projects/<project>/09-description/description.md` | `markdown` | description-maker | handover, seo-specialist, youtube-seo-specialist |
| `projects/<project>/09-description/marketing-specialist.md` | `markdown` | marketing-specialist | _(none in contracts)_ |
| `projects/<project>/09-description/seo-specialist.md` | `markdown` | seo-specialist | _(none in contracts)_ |
| `projects/<project>/10-publish/ab-tester.json` | `json_utf8` | ab-tester | _(none in contracts)_ |
| `projects/<project>/10-publish/analytics-feedback-loop.json` | `json_utf8` | analytics-feedback-loop | _(none in contracts)_ |
| `projects/<project>/10-publish/comment-community-manager.json` | `json_utf8` | comment-community-manager | _(none in contracts)_ |
| `projects/<project>/10-publish/cross-platform-repurposer.json` | `json_utf8` | cross-platform-repurposer | _(none in contracts)_ |
| `projects/<project>/10-publish/handover-check.json` | `json_utf8` | handover | _(none in contracts)_ |
| `projects/<project>/10-publish/handover.md` | `markdown` | handover | cross-platform-repurposer, scheduler-publisher |
| `projects/<project>/10-publish/monetization-tracker.json` | `json_utf8` | monetization-tracker | _(none in contracts)_ |
| `projects/<project>/10-publish/scheduler-publisher.json` | `json_utf8` | scheduler-publisher | _(none in contracts)_ |
| `projects/<project>/10-publish/youtube-analyst.json` | `json_utf8` | youtube-analyst | analytics-feedback-loop |
| `projects/<project>/10-publish/youtube-seo-specialist.json` | `json_utf8` | youtube-seo-specialist | _(none in contracts)_ |
| `projects/<project>/asset-manager.json` | `json_utf8` | asset-manager | _(none in contracts)_ |
| `projects/<project>/orchestrator.json` | `json_utf8` | orchestrator | _(none in contracts)_ |
| `projects/<project>/pipeline-health-checker.json` | `json_utf8` | pipeline-health-checker | _(none in contracts)_ |
| `projects/<project>/task-tracker.json` | `json_utf8` | task-tracker | _(none in contracts)_ |
| `research/trend-cache/trend-report.json` | `json_utf8` | trend-finder | content-calendar, story-thinker |

## Notes

- `mp4_clip` covers scene clips, the rough cut and captioned video: H.264, yuv420p, 1080x1920, 30 fps.
- `mp4_final` adds High profile, AAC 48 kHz, faststart `moov` atom and a duration under 60 s.
- `png_transparent` covers character/scene renders; `png_frame_1080x1920` is the frame/thumbnail profile.
- `wav_mix`, `srt`, `csv` and `ttf_font` are defined for planned outputs; no current contract writes them yet.
- On an office PC, an absent ffprobe produces INFO rather than FAIL for media profiles.
