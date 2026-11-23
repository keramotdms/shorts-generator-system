#!/usr/bin/env python3
"""Generate the complete SKILL.md skeleton set, contracts, index and roadmap.

This is a scaffolding utility only. It never writes real skill logic.
Existing skills with real content are left untouched except for frontmatter.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".opencode" / "skills"

# name, category, subcategory, purpose, input, output, depends (upstream -> downstream)
SKILLS: list[tuple[str, str, str, str, str, str, str]] = [
    # ---- core ----
    ("orchestrator", "core", "", "Tracks the 10-stage pipeline and advances one stage at a time.", "projects/<project>/pipeline-state.json", "updated pipeline state and current stage", "channel config -> all pipeline stages"),
    ("project-memory", "core", "", "Stores tone, colors, fonts, character look and voice choices.", "config/channel.json", "config/style-bible.json", "channel config -> script, voice and character stages"),
    ("task-tracker", "core", "", "Tracks tasks and progress across the pipeline.", "pipeline state and task list", "task status report", "orchestrator -> all stages"),
    ("asset-manager", "core", "", "Validates folder structure, naming and backups.", "assets/ and projects/<project>/", "validated structure and naming report", "channel config -> all stage folders"),
    ("error-log-keeper", "core", "", "Records errors and fixes for every stage.", "error reports from skills", "structured error log", "all stages -> pipeline-health-checker"),
    ("pipeline-health-checker", "core", "", "Checks tools, skills, handoffs and final output.", "whole repository and final video", "PASS / WARN / FAIL report", "all stages -> final render gate"),
    # ---- research ----
    ("book-finder", "research", "", "Finds niche and topic ideas for the channel.", "config/channel.json", "research/niche-report.md", "channel config -> story-thinker"),
    ("trend-finder", "research", "", "Finds location-based YouTube and Facebook trends from free sources.", "config/channel.json + research/trend-inputs/ + research/trend-cache/", "research/trend-cache/trend-report.json", "channel config -> story-thinker"),
    ("competitor-analyzer", "research", "", "Analyzes competing channels and formats.", "research/niche-report.md", "competitor analysis report", "niche report -> story-thinker"),
    ("audience-persona-builder", "research", "", "Builds a clear viewer persona.", "config/channel.json + niche report", "audience persona profile", "research outputs -> hook-writer"),
    ("fact-checker", "research", "", "Verifies factual claims used in scripts.", "draft script claims", "fact-check notes", "draft script -> final-test"),
    ("content-calendar", "research", "", "Plans topics and posting dates.", "niche and trend reports", "content calendar", "research outputs -> scheduler-publisher"),
    # ---- script ----
    ("story-thinker", "script", "", "Turns research into a short story concept.", "research/niche-report.md + config/channel.json", "projects/<project>/02-script/story.json", "research outputs -> hook-writer"),
    ("story-organizer", "script", "", "Structures the story into beats and scenes.", "story.json", "organized story beats", "story-thinker -> hook-writer"),
    ("hook-writer", "script", "", "Writes the first 3-second attention hook.", "story.json + config/channel.json", "projects/<project>/02-script/hook.json", "story-thinker -> script-writer"),
    ("script-writer", "script", "", "Writes the full script with scenes and timings.", "story.json + hook.json + config/channel.json", "projects/<project>/02-script/latest_script.json", "story and hook -> voice stage"),
    ("retention-pacing-optimizer", "script", "", "Improves pacing to hold viewer attention.", "draft script", "pacing suggestions", "script-writer -> final-test"),
    ("loop-cta-designer", "script", "", "Designs the loop ending and call to action.", "draft script", "loop and CTA plan", "script-writer -> video-editing"),
    ("script-tester", "script", "", "Audits script quality across five pillars.", "projects/<project>/02-script/latest_script.json", "audit report + optional optimized script", "script-writer -> voice stage"),
    ("script-user-tester", "script", "", "Tests the script with real viewer feedback.", "draft script + test audience", "viewer feedback report", "script-writer -> script-tester"),
    ("localization", "script", "", "Adapts the script for other languages and regions.", "final script + config/channel.json", "localized script", "script-writer -> voice stage"),
    # ---- voice ----
    ("voiceover-organizer", "voice", "", "Plans voice style, gender and scene order.", "final script + style bible", "voice plan", "script-writer -> voiceover-generator"),
    ("pronunciation-emotion-director", "voice", "", "Sets pronunciation and emotion for each line.", "voice plan + final script", "pronunciation and emotion notes", "voice plan -> voiceover-generator"),
    ("voiceover-generator", "voice", "", "Generates natural speech audio and word timings.", "projects/<project>/02-script/latest_script.json", "projects/<project>/03-voice/voiceover.mp3 + projects/<project>/03-voice/captions.json", "script-writer -> collector"),
    ("voiceover-tester", "voice", "", "Checks voice clarity, speed and duration.", "voiceover.mp3 + final script", "voice QA report", "voiceover-generator -> final-test"),
    ("music-sfx-selector", "voice", "", "Chooses background music and sound effects.", "video mood + style bible", "music and SFX selection list", "scene plan -> audio-mixer"),
    ("audio-mixer", "voice", "", "Mixes voice, music and sound effect levels.", "voice + music + SFX files", "mixed audio track", "voice and music -> video-editing"),
    ("voiceover-captions", "voice", "", "Legacy combined voiceover and caption generator.", "projects/<project>/02-script/latest_script.json", "output/voiceover.mp3 + output/captions.json", "script -> legacy split targets"),
    # ---- character ----
    ("character-thinker-counter", "character", "", "Brainstorms and shortlists character ideas.", "style bible + final script", "character idea list", "script and voice -> character-designer"),
    ("character-organizer", "character", "", "Organizes character files and references.", "character ideas + assets", "character reference index", "character-thinker-counter -> character-designer"),
    ("character-designer", "character", "", "Designs the 2D character look.", "config/style-bible.json", "assets/characters/<character-id>.json", "style bible -> collector"),
    ("character-setup-manager", "character", "", "Sets up reusable character rigs and layers.", "character design files", "character setup assets", "character-designer -> video-maker"),
    ("expression-pose-library", "character", "", "Stores reusable expressions and poses.", "character setup assets", "expression and pose library", "character-designer -> video-maker"),
    ("consistency-guardian", "character", "", "Checks character consistency across scenes.", "rendered scenes + character references", "consistency report", "video-maker -> final-test"),
    ("character-qa-tester", "character", "", "Tests character outputs for errors.", "character assets", "character QA report", "character-designer -> final-test"),
    # ---- scene ----
    ("element-designer", "scene", "", "Designs reusable 2D scene elements.", "style bible + final script", "scene element assets", "character and voice -> scenario-designer"),
    ("element-organizer", "scene", "", "Organizes and versions scene elements.", "scene elements", "element index", "element-designer -> scenario-designer"),
    ("scenario-designer", "scene", "", "Builds scene layouts and visual plans.", "collector output + style bible", "scene layout specs", "collector -> video-maker"),
    # ---- video-making ----
    ("script-voice-character-collector", "video-making", "", "Collects script, voice and character inputs.", "script + voiceover + character references", "projects/<project>/05-scene/collection.json", "script, voice and character -> video-maker"),
    ("lipsync-motion-planner", "video-making", "", "Plans lip sync and basic motion.", "voice timings + character references", "lip sync and motion plan", "collector -> video-maker"),
    ("video-maker", "video-making", "", "Renders vertical scene videos.", "projects/<project>/05-scene/collection.json", "projects/<project>/06-video/scenes/", "collector -> rough-cut-assembler"),
    ("video-quality-checker", "video-making", "", "Checks rendered scene quality.", "rendered scene videos", "video quality report", "video-maker -> rough-cut-assembler"),
    # ---- video-editing / core ----
    ("script-video-voice-collector", "video-editing", "core", "Gathers script, video clips and voice for editing.", "script + rendered scenes + voiceover", "edit package", "video-making -> rough-cut-assembler"),
    ("rough-cut-assembler", "video-editing", "core", "Assembles the first cut of all scenes.", "projects/<project>/06-video/scenes/", "projects/<project>/07-edit/rough-cut.mp4", "video-maker -> caption-maker"),
    ("video-editor", "video-editing", "core", "Applies final edits and trims.", "rough cut + edit notes", "edited video", "rough-cut-assembler -> final-test"),
    ("animator", "video-editing", "core", "Adds motion and animation to elements.", "rough cut + scene elements", "animated video", "rough-cut-assembler -> final-test"),
    ("motion-graphic-editor", "video-editing", "core", "Creates motion graphics overlays.", "rough cut + brand assets", "motion graphics video", "rough-cut-assembler -> final-test"),
    ("branding-manager", "video-editing", "core", "Applies channel branding consistently.", "style bible + edited video", "branded video", "rough-cut-assembler -> final-test"),
    # ---- video-editing / pacing ----
    ("cut-rhythm-editor", "video-editing", "pacing", "Tightens cut rhythm for retention.", "rough cut + script timings", "re-paced video", "rough-cut-assembler -> final-test"),
    ("pattern-interrupt-inserter", "video-editing", "pacing", "Inserts visual pattern interrupts.", "rough cut + final script", "video with pattern interrupts", "rough-cut-assembler -> final-test"),
    ("hook-visual-editor", "video-editing", "pacing", "Enhances the opening hook visually.", "rough cut + hook plan", "hook-enhanced video", "rough-cut-assembler -> final-test"),
    ("seamless-loop-editor", "video-editing", "pacing", "Makes the ending loop smoothly.", "rough cut + loop plan", "loop-ready video", "rough-cut-assembler -> final-test"),
    # ---- video-editing / visual ----
    ("virtual-camera-planner", "video-editing", "visual", "Plans virtual camera moves.", "scene layouts", "camera move plan", "video-making -> video-editor"),
    ("transition-designer", "video-editing", "visual", "Designs scene transitions.", "rough cut + style bible", "transition plan and video", "rough-cut-assembler -> final-test"),
    ("color-grading-keeper", "video-editing", "visual", "Keeps color style consistent.", "edited video + style bible", "color-graded video", "rough-cut-assembler -> final-test"),
    ("broll-variety-planner", "video-editing", "visual", "Adds visual variety with B-roll.", "final script + stock assets", "B-roll plan", "video-making -> video-editor"),
    # ---- video-editing / text-graphics ----
    ("caption-maker", "video-editing", "text-graphics", "Creates word-level caption timings and burns captions.", "projects/<project>/03-voice/captions.json + projects/<project>/07-edit/rough-cut.mp4", "projects/<project>/07-edit/captions.json + captioned video", "voice and rough cut -> safe-zone-checker"),
    ("kinetic-text-animator", "video-editing", "text-graphics", "Animates on-screen text.", "caption data + video", "video with kinetic text", "caption-maker -> final-test"),
    ("emphasis-sticker-placer", "video-editing", "text-graphics", "Places emphasis stickers and highlights.", "final script + video", "video with emphasis graphics", "caption-maker -> final-test"),
    ("intro-outro-manager", "video-editing", "text-graphics", "Adds intro and outro cards.", "video + brand assets", "video with intro and outro", "rough-cut-assembler -> final-test"),
    ("watermark-logo-placer", "video-editing", "text-graphics", "Places the channel watermark or logo.", "video + logo asset", "branded video", "rough-cut-assembler -> final-test"),
    # ---- video-editing / audio-sync ----
    ("beat-sync-editor", "video-editing", "audio-sync", "Syncs cuts to music beats.", "video + music track", "beat-synced video", "audio-mixer -> final-test"),
    ("audio-ducking-controller", "video-editing", "audio-sync", "Ducks music under the voice.", "voice track + music track", "ducked audio track", "audio-mixer -> final-test"),
    ("sfx-timing-placer", "video-editing", "audio-sync", "Places sound effects at exact moments.", "video + SFX list", "video with SFX", "audio-mixer -> final-test"),
    ("av-sync-checker", "video-editing", "audio-sync", "Checks audio and video synchronization.", "final video", "AV sync report", "video-editing -> final-test"),
    # ---- video-editing / automation-export ----
    ("template-preset-manager", "video-editing", "automation-export", "Stores reusable editing templates.", "style bible + edit presets", "template library", "style bible -> video-editing"),
    ("safe-zone-checker", "video-editing", "automation-export", "Checks captions stay inside platform safe zones.", "captioned video", "safe-zone report", "caption-maker -> final-test"),
    ("preview-frame-extractor", "video-editing", "automation-export", "Extracts preview frames for review.", "final video", "preview frames", "video-editing -> final-test"),
    ("format-converter", "video-editing", "automation-export", "Converts to platform-ready formats.", "final video", "converted video files", "final video -> publish stage"),
    ("thumbnail-designer", "video-editing", "automation-export", "Designs a clickable thumbnail.", "final video + title", "thumbnail image", "final video -> description-maker"),
    ("render-export-optimizer", "video-editing", "automation-export", "Optimizes render settings and file size.", "edit project + video", "optimized render settings", "video-editing -> publish stage"),
    ("variant-batch-renderer", "video-editing", "automation-export", "Renders multiple variants in batch.", "template + variant list", "batch rendered videos", "template-preset-manager -> growth stage"),
    ("stock-asset-finder", "video-editing", "automation-export", "Finds reusable stock footage and images.", "final script + asset needs", "stock asset list", "research -> scene and video stages"),
    # ---- final-test ----
    ("red-team", "final-test", "", "Challenges the video to find weaknesses.", "final video + final script", "red-team findings", "video-editing -> bug-finder"),
    ("ruthless-team", "final-test", "", "Gives a harsh quality critique.", "final video", "harsh critique report", "video-editing -> bug-finder"),
    ("bug-finder", "final-test", "", "Finds bugs in the final video.", "final video + reports", "bug report", "video-editing -> description-maker"),
    ("solver", "final-test", "", "Proposes fixes for reported bugs.", "bug report", "fix plan", "bug-finder -> final render"),
    ("copyright-policy-checker", "final-test", "", "Checks copyright and policy risks.", "final script + assets + video", "copyright risk report", "final-test -> publish stage"),
    ("platform-compliance-checker", "final-test", "", "Checks YouTube and Facebook rules.", "final video + metadata", "compliance report", "final-test -> publish stage"),
    ("accessibility-safety-checker", "final-test", "", "Checks captions, audio and viewer safety.", "final video", "accessibility report", "final-test -> publish stage"),
    ("handover", "final-test", "", "Packages final files for publishing.", "all final assets", "projects/<project>/10-publish/handover.md", "final-test -> publish stage"),
    # ---- marketing ----
    ("description-maker", "marketing", "", "Writes the title, description and hashtags.", "final script + channel config", "projects/<project>/09-description/description.md", "final-test -> growth stage"),
    ("copywriter", "marketing", "", "Writes marketing copy for the video.", "final script + audience persona", "marketing copy", "final-test -> description-maker"),
    ("seo-specialist", "marketing", "", "Optimizes keywords and metadata.", "description + final script", "SEO metadata", "description-maker -> growth stage"),
    ("marketing-specialist", "marketing", "", "Plans promotion across channels.", "final video + audience persona", "marketing plan", "final-test -> growth stage"),
    # ---- growth ----
    ("youtube-seo-specialist", "growth", "", "Optimizes for YouTube search and Shorts.", "video metadata", "YouTube SEO plan", "description-maker -> publish stage"),
    ("youtube-analyst", "growth", "", "Analyzes channel performance.", "YouTube analytics data", "performance report", "published video -> research loop"),
    ("analytics-feedback-loop", "growth", "", "Feeds results back into research.", "analytics reports", "insight notes for research", "youtube-analyst -> research stage"),
    ("scheduler-publisher", "growth", "", "Schedules and publishes videos.", "final assets + content calendar", "scheduled or published video", "handover -> platforms"),
    ("cross-platform-repurposer", "growth", "", "Adapts videos for other platforms.", "final video", "platform-specific variants", "handover -> other platforms"),
    ("comment-community-manager", "growth", "", "Manages comments and community replies.", "viewer comments", "reply plan", "published video -> research stage"),
    ("ab-tester", "growth", "", "Runs A/B tests on titles and thumbnails.", "variants + analytics data", "A/B test report", "growth data -> research stage"),
    ("monetization-tracker", "growth", "", "Tracks revenue and monetization.", "analytics and revenue data", "monetization report", "published video -> research stage"),
]

MVP_PHASES = {
    "1": ["orchestrator", "project-memory", "asset-manager", "pipeline-health-checker", "book-finder", "trend-finder"],
    "2": ["story-thinker", "hook-writer", "script-writer"],
    "3": ["voiceover-generator", "character-designer", "script-voice-character-collector", "video-maker"],
    "4": ["rough-cut-assembler", "caption-maker", "safe-zone-checker"],
    "5": ["bug-finder", "description-maker", "handover"],
}
PHASE_BY_NAME = {name: phase for phase, names in MVP_PHASES.items() for name in names}
MVP_NAMES = set(PHASE_BY_NAME)
LEGACY_NAMES = {"voiceover-captions"}
REAL_SKILLS = {"orchestrator", "script-writer", "script-tester", "voiceover-captions"}
STATUS_OVERRIDES = {"script-tester": "implemented"}


def meta(name: str) -> tuple[str, str]:
    if name in STATUS_OVERRIDES:
        return STATUS_OVERRIDES[name], "later"
    if name in LEGACY_NAMES:
        return "legacy", "later"
    if name in MVP_NAMES:
        return "mvp", PHASE_BY_NAME[name]
    return "planned", "later"


def split_depends(depends: str) -> tuple[str, str]:
    upstream, downstream = depends.split(" -> ", 1)
    return upstream, downstream


def write_skeleton(folder: Path, name: str, category: str, subcategory: str,
                   purpose: str, input_text: str, output: str, depends: str) -> None:
    status, phase = meta(name)
    lines = [
        "---",
        f"name: {name}",
        f"description: {purpose}",
        f"category: {category}",
    ]
    if subcategory:
        lines.append(f"subcategory: {subcategory}")
    lines += [f"status: {status}", f"phase: {phase}", "---", ""]
    if name in LEGACY_NAMES:
        lines.insert(-2, "note: legacy; will later be split into voiceover-generator and caption-maker")
    lines += [
        "# Purpose", "", purpose, "",
        "# Input", "", input_text, "",
        "# Output", "", output, "",
        "# Steps", "", "TODO", "",
        "# How to test", "", "TODO", "",
        "# Depends on / feeds into", "", depends, "",
    ]
    (folder / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")


def patch_real_frontmatter(path: Path, name: str, category: str) -> None:
    status, phase = meta(name)
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return
    end = text.find("\n---", 3)
    if end == -1:
        return
    header = text[3:end].strip().splitlines()
    body = text[end + 4:]
    managed = {"category", "status", "phase", "subcategory", "note"}
    header = [line for line in header if not any(line.startswith(k + ":") for k in managed)]
    insert_at = next((i + 1 for i, line in enumerate(header) if line.startswith("description:")), len(header))
    fields = [f"category: {category}", f"status: {status}", f"phase: {phase}"]
    if name in LEGACY_NAMES:
        fields.append("note: legacy; will later be split into voiceover-generator and caption-maker")
    header[insert_at:insert_at] = fields
    path.write_text("---\n" + "\n".join(header) + "\n---" + body, encoding="utf-8")


def build_contracts() -> dict:
    return {
        "naming_rule": "lowercase-kebab-case, no 'shorts-' prefix",
        "notes": [
            "Skill folders live under .opencode/skills/<skill-name>/SKILL.md.",
            "Generated project data lives under projects/<project>/<stage>/, never inside skill folders.",
            "A skill's output must exactly match the next skill's input.",
            "upstream and downstream mirror the 'Depends on / feeds into' line in each SKILL.md.",
        ],
        "voiceover_captions_split_proposal": {
            "problem": "The legacy 'voiceover-captions' skill does two jobs: audio generation and caption timing generation.",
            "decision": "Keep it as legacy compatibility until voiceover-generator and caption-maker are built.",
            "mapping": {
                "voiceover-generator": {
                    "phase": 3,
                    "input": "projects/<project>/02-script/latest_script.json",
                    "output": "projects/<project>/03-voice/voiceover.mp3 + projects/<project>/03-voice/captions.json",
                    "job": "Generate natural Bangla/English speech and word-level timing metadata.",
                    "maps_to": ["voiceover-captions"],
                },
                "caption-maker": {
                    "phase": 4,
                    "input": "projects/<project>/03-voice/captions.json + projects/<project>/07-edit/rough-cut.mp4",
                    "output": "projects/<project>/07-edit/captions.json + captioned video",
                    "job": "Create word/phrase caption timings and safe-zone-ready caption data only.",
                    "maps_to": ["voiceover-captions"],
                },
                "voiceover-captions": {
                    "status": "legacy-compat",
                    "maps_to": ["voiceover-generator", "caption-maker"],
                    "current_helper": "scripts/generate_audio.py",
                    "output_today": "output/voiceover.mp3 + output/captions.json",
                    "migration": "When both target skills are built, keep this skill as a thin wrapper that calls both, then deprecate it.",
                },
            },
        },
        "skills": {
            name: {
                "input": input_text,
                "output": output,
                "upstream": split_depends(depends)[0],
                "downstream": split_depends(depends)[1],
                "category": category,
                "status": meta(name)[0],
                "phase": meta(name)[1],
            }
            for name, category, _sub, _purpose, input_text, output, depends in SKILLS
        },
    }


def build_index() -> str:
    lines = [
        "# Skill Index", "",
        f"Total skills: {len(SKILLS)}", "",
        "| Name | Category | Subcategory | Status | Phase |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, category, subcategory, _purpose, _i, _o, _d in SKILLS:
        status, phase = meta(name)
        lines.append(f"| {name} | {category} | {subcategory or '-'} | {status} | {phase} |")
    return "\n".join(lines) + "\n"


def build_roadmap() -> str:
    lines = [
        "# Roadmap", "",
        "## Pipeline order", "",
        "Research -> Script -> Voice -> Character -> Scene -> Video -> Edit -> Final Test -> Description/SEO -> Publish", "",
        "## MVP skills (19, build one at a time)", "",
    ]
    phase_titles = {
        "1": "Phase 1 - Foundation",
        "2": "Phase 2 - Content",
        "3": "Phase 3 - Production",
        "4": "Phase 4 - Edit",
        "5": "Phase 5 - Finish",
    }
    for phase in ["1", "2", "3", "4", "5"]:
        lines += [f"### {phase_titles[phase]}", ""]
        for name in MVP_PHASES[phase]:
            suffix = " (implemented)" if name in REAL_SKILLS else ""
            lines.append(f"- {name}{suffix}")
        lines.append("")
    lines += [
        "## Legacy / compatibility", "",
        "- `voiceover-captions` - legacy skill that combines voice and captions. It will be split into `voiceover-generator` (Phase 3) and `caption-maker` (Phase 4). See `config/skill-contracts.json`.", "",
        "## All skills by category", "",
    ]
    categories: dict[str, list[str]] = {}
    for name, category, _sub, _p, _i, _o, _d in SKILLS:
        categories.setdefault(category, []).append(name)
    for category, names in categories.items():
        lines += [f"### {category}", ""]
        for name in names:
            status, phase = meta(name)
            lines.append(f"- {name} — {status}, phase {phase}")
        lines.append("")
    lines += [
        "## Pending decisions", "",
        "- FFmpeg: installed but `ffmpeg.exe` is blocked by Windows Smart App Control. Revisit before video skills.",
        "- Niche and language remain pending confirmation in the live pipeline (config defaults are placeholders).", "",
        "Full skill table: `docs/SKILL-INDEX.md`.",
    ]
    return "\n".join(lines)


def main() -> None:
    names = [item[0] for item in SKILLS]
    if len(names) != len(set(names)):
        raise SystemExit("Duplicate skill names in the scaffold table")

    for name, category, subcategory, purpose, input_text, output, depends in SKILLS:
        folder = SKILLS_DIR / name
        folder.mkdir(parents=True, exist_ok=True)
        skill_md = folder / "SKILL.md"
        if skill_md.is_file() and "TODO" not in skill_md.read_text(encoding="utf-8"):
            print(f"keep     {name} (implemented)")
        elif name in REAL_SKILLS and skill_md.is_file():
            patch_real_frontmatter(skill_md, name, category)
            print(f"patched  {name}")
        else:
            write_skeleton(folder, name, category, subcategory, purpose, input_text, output, depends)
            print(f"created  {name}")

    # Remove only empty leftover placeholder folders (never real content).
    for folder in sorted(SKILLS_DIR.iterdir()):
        if folder.is_dir() and folder.name not in names and not any(folder.iterdir()):
            folder.rmdir()
            print(f"removed empty extra folder: {folder.name}")

    (ROOT / "config" / "skill-contracts.json").write_text(
        json.dumps(build_contracts(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (ROOT / "docs" / "SKILL-INDEX.md").write_text(build_index(), encoding="utf-8")
    (ROOT / "docs" / "ROADMAP.md").write_text(build_roadmap(), encoding="utf-8")

    counts = {"mvp": 0, "planned": 0, "implemented": 0, "legacy": 0}
    for name in names:
        counts[meta(name)[0]] += 1
    print(
        f"\nTotal: {len(names)} | mvp: {counts['mvp']} | planned: {counts['planned']}"
        f" | implemented: {counts['implemented']} | legacy: {counts['legacy']}"
    )


if __name__ == "__main__":
    main()
