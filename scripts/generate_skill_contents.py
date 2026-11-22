#!/usr/bin/env python3
"""Generate real SKILL.md content for all 93 skills, one batch at a time.

Uses the skill table in generate_skill_scaffolds.py as the single source of truth
for name, category, subcategory, purpose, input, output and dependency line.
Existing hand-written skills are patched (never overwritten).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_skill_scaffolds import SKILLS, ROOT, SKILLS_DIR, meta

CONTRACTS = ROOT / "config" / "skill-contracts.json"
INDEX = ROOT / "docs" / "SKILL-INDEX.md"

BATCHES = {
    1: {"orchestrator", "project-memory", "asset-manager", "task-tracker",
        "error-log-keeper", "pipeline-health-checker"},
    2: {"book-finder", "trend-finder", "competitor-analyzer",
        "audience-persona-builder", "fact-checker", "content-calendar"},
    3: {"story-thinker", "story-organizer", "hook-writer", "script-writer",
        "retention-pacing-optimizer", "loop-cta-designer", "script-tester",
        "script-user-tester", "localization"},
    4: {"voiceover-organizer", "pronunciation-emotion-director",
        "voiceover-generator", "voiceover-tester", "music-sfx-selector",
        "audio-mixer", "voiceover-captions"},
    5: {"character-thinker-counter", "character-organizer", "character-designer",
        "character-setup-manager", "expression-pose-library", "consistency-guardian",
        "character-qa-tester", "element-designer", "element-organizer",
        "scenario-designer"},
    6: {"script-voice-character-collector", "lipsync-motion-planner",
        "video-maker", "video-quality-checker"},
    7: {"script-video-voice-collector", "rough-cut-assembler", "video-editor",
        "animator", "motion-graphic-editor", "branding-manager", "cut-rhythm-editor",
        "pattern-interrupt-inserter", "hook-visual-editor", "seamless-loop-editor",
        "virtual-camera-planner", "transition-designer", "color-grading-keeper",
        "broll-variety-planner", "caption-maker", "kinetic-text-animator",
        "emphasis-sticker-placer", "intro-outro-manager", "watermark-logo-placer",
        "beat-sync-editor", "audio-ducking-controller", "sfx-timing-placer",
        "av-sync-checker", "template-preset-manager", "safe-zone-checker",
        "preview-frame-extractor", "format-converter", "thumbnail-designer",
        "render-export-optimizer", "variant-batch-renderer", "stock-asset-finder"},
    8: {"red-team", "ruthless-team", "bug-finder", "solver",
        "copyright-policy-checker", "platform-compliance-checker",
        "accessibility-safety-checker", "handover", "description-maker", "copywriter",
        "seo-specialist", "marketing-specialist", "youtube-seo-specialist",
        "youtube-analyst", "analytics-feedback-loop", "scheduler-publisher",
        "cross-platform-repurposer", "comment-community-manager", "ab-tester",
        "monetization-tracker"},
}

CHECKERS = {
    "pipeline-health-checker", "safe-zone-checker", "video-quality-checker",
    "av-sync-checker", "voiceover-tester", "character-qa-tester",
    "consistency-guardian", "bug-finder", "copyright-policy-checker",
    "platform-compliance-checker", "accessibility-safety-checker", "script-tester",
}

SCRIPT_BACKED = {
    "project-memory", "asset-manager", "task-tracker", "error-log-keeper",
    "caption-maker", "script-voice-character-collector", "handover",
    "orchestrator", "voiceover-generator", "video-maker", "rough-cut-assembler",
    "video-editor", "animator", "motion-graphic-editor", "branding-manager",
    "cut-rhythm-editor", "pattern-interrupt-inserter", "hook-visual-editor",
    "seamless-loop-editor", "transition-designer", "color-grading-keeper",
    "broll-variety-planner", "kinetic-text-animator", "emphasis-sticker-placer",
    "intro-outro-manager", "watermark-logo-placer", "beat-sync-editor",
    "audio-ducking-controller", "sfx-timing-placer", "preview-frame-extractor",
    "format-converter", "thumbnail-designer", "render-export-optimizer",
    "variant-batch-renderer", "audio-mixer",
}

REQUIRES_FFMPEG = {
    "video-maker", "video-quality-checker", "av-sync-checker", "rough-cut-assembler",
    "video-editor", "animator", "motion-graphic-editor", "branding-manager",
    "cut-rhythm-editor", "pattern-interrupt-inserter", "hook-visual-editor",
    "seamless-loop-editor", "transition-designer", "color-grading-keeper",
    "broll-variety-planner", "kinetic-text-animator", "emphasis-sticker-placer",
    "intro-outro-manager", "watermark-logo-placer", "beat-sync-editor",
    "audio-ducking-controller", "sfx-timing-placer", "preview-frame-extractor",
    "format-converter", "thumbnail-designer", "render-export-optimizer",
    "variant-batch-renderer", "audio-mixer",
}

REAL_SKILLS = {"orchestrator", "script-writer", "script-tester", "voiceover-captions"}
BATCH_OF = {name: number for number, names in BATCHES.items() for name in names}


def skill_type(name: str) -> str:
    if name in CHECKERS:
        return "checker"
    if name in SCRIPT_BACKED:
        return "script-backed"
    return "prompt-only"


def parse_frontmatter(text: str) -> tuple[list[str], str]:
    if not text.startswith("---"):
        return [], text
    end = text.find("\n---", 3)
    if end == -1:
        return [], text
    return text[3:end].strip().splitlines(), text[end + 4:]


def set_field(lines: list[str], key: str, value: str) -> None:
    prefix = key + ":"
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = f"{key}: {value}"
            return
    lines.append(f"{key}: {value}")


def build_body(name: str, purpose: str, input_text: str, output: str, depends: str,
               kind: str) -> str:
    short_purpose = purpose.rstrip(".").lower()
    run_line = (
        f"Run `python scripts/skill_tools.py {name} run` with `PROJECT=<project>`; "
        "the helper reads context through `scripts/skill_lib.py::style_context()`."
        if kind in {"script-backed", "checker"} else
        f"Follow this skill's prompt instructions to {short_purpose}, using only the "
        "context loaded in step 1."
    )
    ffmpeg_step = (
        f"6. If `requires: ffmpeg` is set, call `scripts/skill_lib.py::require_ffmpeg()` "
        f"which reads `FFMPEG_PATH`; on `BLOCKED` print `BLOCKED {name}: ffmpeg ...` and "
        "exit 0 without a FAIL."
        if name in REQUIRES_FFMPEG else ""
    )
    test_line = (
        f"`python scripts/skill_tools.py {name} --self-test` → expected `PASS {name}: ...`"
        + (" or `BLOCKED ...: ffmpeg ...` while Smart App Control is active"
           if name in REQUIRES_FFMPEG else "")
        + f". Then confirm `{output}` exists and is non-empty after a real run."
        if kind in {"script-backed", "checker"} else
        f"Type: `Use the {name} skill with PROJECT=<project>`. Expected: `{output}` "
        "exists, parses cleanly, and contains no hardcoded niche or language value."
    )
    lines = [
        f"> Context is always loaded via project-memory; all generated data lives under projects/<project>/.",
        "",
        "# When to use",
        "",
        f"Use when {short_purpose} for a video in `projects/<project>/`.",
        "",
        "# Purpose",
        "",
        purpose,
        "",
        "# Input",
        "",
        f"- `{input_text}`",
        "- `config/channel.json` and `config/style-bible.json`, read through project-memory",
        "- `PROJECT` environment variable (defaults to `_template`)",
        "",
        "# Output",
        "",
        f"- `{output}`",
        "- A `status`, `skill`, `project` and `generated_at` record inside the output where the format allows it",
        "",
        "# Steps",
        "",
        "1. Read niche, language, location and style through project-memory (or `scripts/skill_lib.py::style_context()` from `config/channel.json`); never hardcode them.",
        f"2. Validate the input at `{input_text}`; if it is missing or malformed, follow Failure handling and stop.",
        f"3. {run_line}",
        f"4. Write the result to `{output}` under `projects/<project>/`; create parent folders first.",
        f"5. Re-open `{output}` and verify it is valid and non-empty; record any problem via error-log-keeper at `projects/<project>/08-final-test/error-log.jsonl`.",
    ]
    if ffmpeg_step:
        lines.append(ffmpeg_step)
    lines += [
        "",
        "# How to test",
        "",
        f"- {test_line}",
        "- Checklist: context came from project-memory; input validated; output path is exact; no placeholder steps remain.",
        "",
        "# Depends on / feeds into",
        "",
        depends,
        "",
        "# Failure handling",
        "",
        "If a required input is missing or invalid, stop without writing a partial output, log the reason to `projects/<project>/08-final-test/error-log.jsonl` via error-log-keeper, and report the exact missing path. If the output fails validation, delete it and re-run after fixing the input. For FFmpeg-required skills, report `BLOCKED: ffmpeg` with the `FFMPEG_PATH` hint instead of FAIL; do not change Windows application-control settings.",
        "",
    ]
    return "\n".join(lines)


def patch_real(name: str, purpose: str, input_text: str, output: str, depends: str,
               kind: str) -> str:
    """Add standard fields/sections to an existing hand-written skill."""
    path = SKILLS_DIR / name / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    header, body = parse_frontmatter(text)
    set_field(header, "category", dict((n, c) for n, c, _s, _p, _i, _o, _d in SKILLS)[name])
    set_field(header, "status", "legacy" if name == "voiceover-captions" else "implemented")
    set_field(header, "phase", meta(name)[1])
    set_field(header, "type", kind)
    set_field(header, "batch", str(BATCH_OF[name]))
    if name in REQUIRES_FFMPEG:
        set_field(header, "requires", "ffmpeg")
    if name == "voiceover-captions":
        set_field(header, "note", "legacy pointer to voiceover-generator and caption-maker")

    standard = build_body(name, purpose, input_text, output, depends, kind)
    existing_lower = body.lower()
    for heading in ("When to use", "Purpose", "Input", "Output", "Steps",
                    "How to test", "Depends on / feeds into", "Failure handling"):
        if f"# {heading.lower()}" not in existing_lower:
            section = standard.split(f"# {heading}", 1)[1].split("\n# ", 1)[0]
            body = body.rstrip() + f"\n\n# {heading}\n" + section.rstrip() + "\n"
    if "projects/<project>/" not in body:
        body = "> All generated data lives under projects/<project>/.\n\n" + body
    return "---\n" + "\n".join(header) + "\n---\n" + body


def write_skill(name: str, category: str, subcategory: str, purpose: str,
                input_text: str, output: str, depends: str) -> Path:
    folder = SKILLS_DIR / name
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "SKILL.md"
    kind = skill_type(name)
    status, phase = meta(name)

    if name in REAL_SKILLS and path.is_file():
        text = patch_real(name, purpose, input_text, output, depends, kind)
    else:
        header = [
            f"name: {name}",
            f"description: {purpose}",
            f"category: {category}",
        ]
        if subcategory:
            header.append(f"subcategory: {subcategory}")
        final_status = "legacy" if name == "voiceover-captions" else "implemented"
        header += [f"status: {final_status}", f"phase: {phase}", f"type: {kind}",
                   f"batch: {BATCH_OF[name]}"]
        if name in REQUIRES_FFMPEG:
            header.append("requires: ffmpeg")
        if name == "voiceover-captions":
            header.append("note: legacy pointer to voiceover-generator and caption-maker")
        text = "---\n" + "\n".join(header) + "\n---\n\n" + build_body(
            name, purpose, input_text, output, depends, kind
        )
    path.write_text(text, encoding="utf-8")
    return path


def update_registry(names: list[str]) -> None:
    """Sync contracts and index for the given skills without losing other entries."""
    contracts = json.loads(CONTRACTS.read_text(encoding="utf-8"))
    skills = contracts.get("skills", {})
    for name in names:
        if name in skills:
            skills[name]["status"] = "legacy" if name == "voiceover-captions" else "implemented"
            skills[name]["type"] = skill_type(name)
            skills[name]["batch"] = BATCH_OF[name]
            if name in REQUIRES_FFMPEG:
                skills[name]["requires"] = "ffmpeg"
    CONTRACTS.write_text(json.dumps(contracts, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")

    index_lines = INDEX.read_text(encoding="utf-8").splitlines()
    for pos, line in enumerate(index_lines):
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and cells[0] in names:
            cells[3] = "legacy" if cells[0] == "voiceover-captions" else "implemented"
            index_lines[pos] = "| " + " | ".join(cells) + " |"
    INDEX.write_text("\n".join(index_lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, required=True)
    args = parser.parse_args()
    names = sorted(BATCHES[args.batch])
    for row in SKILLS:
        name, category, subcategory, purpose, input_text, output, depends = row
        if name in names:
            path = write_skill(name, category, subcategory, purpose,
                               input_text, output, depends)
            print(f"wrote {path.relative_to(ROOT)}")
    update_registry(names)
    blocked = [n for n in names if n in REQUIRES_FFMPEG]
    print(f"\nBatch {args.batch}: {len(names)} skills written | "
          f"{len(blocked)} require ffmpeg (BLOCKED reported by health check)")


if __name__ == "__main__":
    main()
