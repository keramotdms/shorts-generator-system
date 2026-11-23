#!/usr/bin/env python3
"""Walk the whole pipeline and fail on any upstream-output / downstream-input mismatch.

The contracts are the source of truth. No files need to exist: this checks the
data hand-off graph, exact paths and the 20 defects listed in docs/SKILL-REVIEW.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "config" / "skill-contracts.json"
P = "projects/<project>/"
FINAL = P + "08-final-test/final-video.mp4"

# Dependency order (not folder order): every input must be made by an earlier skill.
ORDER = [
    "project-memory", "orchestrator", "task-tracker", "asset-manager", "error-log-keeper",
    "book-finder", "trend-finder", "competitor-analyzer", "audience-persona-builder",
    "content-calendar", "story-thinker", "story-organizer", "hook-writer", "script-writer",
    "script-tester", "script-user-tester", "retention-pacing-optimizer", "loop-cta-designer",
    "localization", "fact-checker", "voiceover-organizer", "pronunciation-emotion-director",
    "voiceover-generator", "voiceover-tester", "voiceover-captions", "music-sfx-selector",
    "audio-mixer", "character-thinker-counter", "character-organizer", "character-designer",
    "character-setup-manager", "expression-pose-library", "character-qa-tester",
    "element-designer", "element-organizer",
    "scenario-designer", "script-voice-character-collector", "lipsync-motion-planner",
    "video-maker", "video-quality-checker", "script-video-voice-collector",
    "rough-cut-assembler", "stock-asset-finder", "broll-variety-planner",
    "virtual-camera-planner", "video-editor", "animator", "motion-graphic-editor",
    "branding-manager", "cut-rhythm-editor", "pattern-interrupt-inserter", "hook-visual-editor",
    "seamless-loop-editor", "transition-designer", "color-grading-keeper",
    "template-preset-manager", "variant-batch-renderer", "caption-maker", "safe-zone-checker",
    "kinetic-text-animator", "emphasis-sticker-placer", "intro-outro-manager",
    "watermark-logo-placer", "beat-sync-editor", "audio-ducking-controller",
    "sfx-timing-placer", "render-export-optimizer", "format-converter",
    "preview-frame-extractor", "thumbnail-designer", "av-sync-checker", "red-team",
    "ruthless-team", "bug-finder", "solver", "copyright-policy-checker",
    "platform-compliance-checker", "accessibility-safety-checker", "consistency-guardian",
    "pipeline-health-checker", "description-maker", "copywriter", "seo-specialist",
    "marketing-specialist", "handover", "youtube-seo-specialist", "scheduler-publisher",
    "cross-platform-repurposer", "youtube-analyst", "analytics-feedback-loop",
    "comment-community-manager", "ab-tester", "monetization-tracker",
]

# Files/directories that enter the pipeline from outside (config, manual exports, seeds).
SEEDS = {
    "config/channel.json", "config/style-bible.json", "config/skill-contracts.json",
    P + "pipeline-state.json", P + "10-publish/inputs/", P, P + "08-final-test/",
}

ALLOWED_PREFIXES = ("projects/<project>/", "config/", "assets/", "research/")


def paths(value: str) -> list[str]:
    return [part.strip() for part in value.split(" + ") if part.strip()]


def main() -> int:
    errors: list[str] = []
    data = json.loads(CONTRACTS.read_text(encoding="utf-8"))
    skills: dict = data["skills"]

    if len(ORDER) != len(set(ORDER)):
        errors.append("ORDER contains duplicate skill names")
    if set(ORDER) != set(skills):
        errors.append(f"ORDER mismatch: missing={sorted(set(skills)-set(ORDER))} extra={sorted(set(ORDER)-set(skills))}")

    for name, entry in skills.items():
        ins, outs = paths(entry["input"]), paths(entry["output"])
        if not ins or not outs:
            errors.append(f"{name}: empty input or output")
        for part in ins + outs:
            if not part.startswith(ALLOWED_PREFIXES):
                errors.append(f"{name}: not an exact path: {part!r}")
            if part.startswith(P) and "<" in part[len(P):]:
                errors.append(f"{name}: placeholder in path: {part!r}")
        if len(outs) != len(set(outs)):
            errors.append(f"{name}: duplicate output path: {outs}")
        body = (ROOT / ".opencode" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        for part in ins + outs:
            if part not in body:
                errors.append(f"{name}: contract path missing from SKILL.md: {part}")

    produced: set[str] = set()
    for name in ORDER:
        entry = skills[name]
        for part in paths(entry["output"]):
            produced.add(part)
        for part in paths(entry["input"]):
            if part in SEEDS or part.endswith("/"):
                continue
            if part not in produced:
                errors.append(f"{name}: input {part} is not produced earlier in the chain")

    # Explicit regression checks for the 20 mismatches in docs/SKILL-REVIEW.md.
    checks = {
        "book-finder output": skills["book-finder"]["output"] == P + "01-research/niche-report.md",
        "trend-finder output": skills["trend-finder"]["output"] == P + "01-research/trend-report.json",
        "story-thinker reads exact research paths": P + "01-research/trend-report.json" in skills["story-thinker"]["input"],
        "script-tester duplicate output fixed": skills["script-tester"]["output"] == P + "02-script/script-tester.json",
        "hook field mapping is explicit": "hook.json.text" in (ROOT / ".opencode/skills/script-writer/SKILL.md").read_text(encoding="utf-8"),
        "collector consumes character design": "assets/characters/creator-01.json" in skills["script-voice-character-collector"]["input"],
        "video-maker consumes collection.json": skills["video-maker"]["input"] == P + "05-scene/collection.json",
        "rough-cut consumes collection.json": P + "05-scene/collection.json" in skills["rough-cut-assembler"]["input"],
        "caption-maker writes captions.json": P + "07-edit/captions.json" in skills["caption-maker"]["output"],
        "safe-zone output name": skills["safe-zone-checker"]["output"] == P + "07-edit/safe-zone-checker.json",
        "single canonical final video": skills["render-export-optimizer"]["output"].startswith(FINAL),
        "handover has no circular input": P + "10-publish/handover.md" not in skills["handover"]["input"],
        "handover writes handover.md": P + "10-publish/handover.md" in skills["handover"]["output"],
        "legacy voiceover-captions uses stage folders": skills["voiceover-captions"]["output"] == P + "03-voice/voiceover.mp3 + " + P + "03-voice/captions.json",
        "description-maker reads bug report": P + "08-final-test/bug-finder.json" in skills["description-maker"]["input"],
        "no output/ paths": not any("output/" in v["output"] for v in skills.values()),
        "no scripts/latest_script.json paths": not any("scripts/latest_script.json" in v["input"] + v["output"] for v in skills.values()),
    }
    for label, ok in checks.items():
        if not ok:
            errors.append("regression: " + label)

    final_consumers = [
        "bug-finder", "platform-compliance-checker", "accessibility-safety-checker",
        "handover", "cross-platform-repurposer", "preview-frame-extractor",
        "format-converter", "thumbnail-designer", "av-sync-checker",
        "pipeline-health-checker", "red-team", "ruthless-team",
    ]
    for name in final_consumers:
        if FINAL not in skills[name]["input"]:
            errors.append(f"{name}: does not use canonical final-video.mp4")

    print(f"Chain walk: {len(ORDER)} skills in dependency order")
    if errors:
        print(f"FAIL: {len(errors)} chain mismatch(es)")
        for error in errors:
            print(" - " + error)
        return 1
    print("PASS: exact paths, no duplicate outputs, every input produced upstream")
    return 0


if __name__ == "__main__":
    sys.exit(main())
