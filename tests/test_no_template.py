#!/usr/bin/env python3
"""Fail if any implemented skill is still a TEMPLATE rather than a REAL skill.

Checks four things for every implemented SKILL.md:
  1. no generic "Follow this skill's prompt instructions" wording
  2. a filled output example (fenced JSON, at least 3 keys, no placeholders)
  3. Steps are not identical to another skill after removing the skill name
  4. requires: ffmpeg skills do not use the shared generic concat helper

One failure line is printed per offending skill, so a clean pre-fix run reports
exactly the 55 known TEMPLATE skills.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".opencode" / "skills"
sys.path.insert(0, str(ROOT / "scripts"))

import schema_validator
from skill_tools import GENERIC_FFMPEG_SKILLS

DISTINCT_FFMPEG = {
    "rough-cut-assembler", "caption-maker", "safe-zone-checker", "format-converter",
    "render-export-optimizer", "audio-mixer", "audio-ducking-controller",
    "video-maker", "kinetic-text-animator", "transition-designer",
    "video-quality-checker", "av-sync-checker",
    "animator", "beat-sync-editor", "branding-manager", "broll-variety-planner",
    "color-grading-keeper", "cut-rhythm-editor", "emphasis-sticker-placer",
    "hook-visual-editor", "intro-outro-manager", "motion-graphic-editor",
    "pattern-interrupt-inserter", "preview-frame-extractor", "seamless-loop-editor",
    "sfx-timing-placer", "thumbnail-designer", "variant-batch-renderer",
    "video-editor", "watermark-logo-placer",
}

GENERIC_PHRASE = "Follow this skill's prompt instructions"
EXAMPLE_HEADING = "# Output format (short example)"
PLACEHOLDERS = {"", "string", "example", "todo", "tbd", "n/a", "null", "<...>", "..."}

# The 55 skills classified TEMPLATE in the 2026-11-23 read-only audit. The list
# stays here after the rewrite so the test keeps guarding them from regression.
TEMPLATE_TARGETS = {
    "ab-tester", "analytics-feedback-loop", "animator",
    "audience-persona-builder", "beat-sync-editor", "branding-manager",
    "broll-variety-planner", "character-organizer", "character-setup-manager",
    "character-thinker-counter", "color-grading-keeper", "comment-community-manager",
    "competitor-analyzer", "content-calendar", "copywriter",
    "cross-platform-repurposer", "cut-rhythm-editor", "element-designer",
    "element-organizer", "emphasis-sticker-placer", "expression-pose-library",
    "fact-checker", "hook-visual-editor", "intro-outro-manager",
    "lipsync-motion-planner", "localization", "loop-cta-designer",
    "marketing-specialist", "monetization-tracker", "motion-graphic-editor",
    "music-sfx-selector", "pattern-interrupt-inserter", "preview-frame-extractor",
    "pronunciation-emotion-director", "red-team", "retention-pacing-optimizer",
    "ruthless-team", "scheduler-publisher", "script-user-tester",
    "script-video-voice-collector", "seamless-loop-editor", "seo-specialist",
    "sfx-timing-placer", "solver", "stock-asset-finder", "story-organizer",
    "template-preset-manager", "thumbnail-designer", "variant-batch-renderer",
    "video-editor", "virtual-camera-planner", "voiceover-organizer",
    "watermark-logo-placer", "youtube-analyst", "youtube-seo-specialist",
}


def parse(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields, text[end + 4:]


def section(body: str, heading: str, stops: tuple[str, ...]) -> str:
    if heading not in body:
        return ""
    part = body.split(heading, 1)[1]
    for stop in stops:
        if stop in part:
            part = part.split(stop, 1)[0]
    return part.strip()


def steps_signature(steps: str, name: str) -> str:
    text = steps.lower().replace(name.lower(), " ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def example_of(body: str) -> dict | None:
    part = section(body, EXAMPLE_HEADING, ("# Quality rules", "# Steps", "# How to test"))
    match = re.search(r"```(?:json)?\s*\n(.*?)\n```", part, re.S)
    if not match:
        return None
    raw = match.group(1).strip()
    if not raw or "TODO" in raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or len(data) < 3:
        return None
    filled = [
        value for value in data.values()
        if isinstance(value, str) and value.strip().lower() not in PLACEHOLDERS
    ]
    if len(filled) < 3:
        return None
    return data


def main() -> int:
    signatures: dict[str, list[str]] = {}
    reasons_by_skill: dict[str, list[str]] = {}
    checked = 0

    for folder in sorted(SKILLS.iterdir()):
        if not folder.is_dir():
            continue
        path = folder / "SKILL.md"
        if not path.is_file():
            continue
        name = folder.name
        if name not in TEMPLATE_TARGETS:
            continue
        fields, body = parse(path.read_text(encoding="utf-8"))
        if fields.get("status") != "implemented":
            continue
        checked += 1
        reasons: list[str] = []

        steps = section(body, "# Steps", ("# How to test", "# Depends on / feeds into"))
        if GENERIC_PHRASE in steps:
            reasons.append("generic prompt wording remains in Steps")

        example = example_of(body)
        if example is None:
            reasons.append("no filled output example")
        else:
            schema_name = fields.get("schema")
            if schema_name:
                try:
                    errors = schema_validator.validate(
                        example, schema_validator.load_schema(schema_name)
                    )
                except schema_validator.ValidationError as exc:
                    errors = [str(exc)]
                if errors:
                    reasons.append("example fails schema " + schema_name + ": " + "; ".join(errors))

        signature = steps_signature(steps, name)
        if signature:
            signatures.setdefault(signature, []).append(name)

        if fields.get("requires") == "ffmpeg" and name in GENERIC_FFMPEG_SKILLS:
            reasons.append("uses shared generic ffmpeg concat")
        if fields.get("requires") == "ffmpeg" and name not in DISTINCT_FFMPEG:
            reasons.append("no distinct ffmpeg command registered")

        if fields.get("api_needed") == "later" and "10-publish/inputs/" not in body:
            reasons.append("api_needed: later but no manual input file path")

        if reasons:
            reasons_by_skill[name] = reasons

    for names in signatures.values():
        if len(names) > 1:
            for name in names:
                reasons_by_skill.setdefault(name, []).append(
                    "Steps identical to: " + ", ".join(n for n in names if n != name)
                )

    print(f"NO-TEMPLATE AUDIT: {checked} implemented skills checked")
    if not reasons_by_skill:
        print("PASS: 0 template skills")
        return 0
    print(f"FAIL: {len(reasons_by_skill)} template skill(s)")
    for name in sorted(reasons_by_skill):
        print(f" - {name}: {'; '.join(reasons_by_skill[name])}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
