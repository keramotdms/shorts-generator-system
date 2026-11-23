#!/usr/bin/env python3
"""Basic repository health check. Stdlib only; no external packages."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".opencode" / "skills"
CONTRACTS_PATH = ROOT / "config" / "skill-contracts.json"

sys.path.insert(0, str(ROOT / "scripts"))
import skill_lib as lib  # noqa: E402

REQUIRED_DIRS = [
    ".opencode/skills",
    "config",
    "projects/_template",
    "assets/characters",
    "assets/scenes",
    "research/trend-cache",
    "tests/fixtures",
    "scripts",
    "docs",
]

REQUIRED_FILES = [
    ".gitignore",
    ".env.example",
    "requirements.txt",
    "AGENTS.md",
    "projects/_template/project.json",
    "docs/ROADMAP.md",
    "docs/SKILL-INDEX.md",
    "config/channel.json",
    "config/skill-contracts.json",
    "docs/lessons.md",
    "scripts/generate_audio.py",
    "scripts/generate_skill_scaffolds.py",
    "scripts/generate_skill_contents.py",
    "scripts/skill_lib.py",
    "scripts/skill_tools.py",
    "scripts/svg_scene_builder.py",
    "scripts/orchestrator.py",
    "config/defaults.json",
    "tests/test_skills.py",
    "tests/smoke/run_dummy_pipeline.py",
    "tests/fixtures/latest_script.json",
    "tests/fixtures/captions.json",
    "assets/characters/creator-01-neutral.svg",
    "assets/characters/creator-01-neutral.png",
    "assets/characters/creator-01-smile.svg",
    "assets/characters/creator-01-smile.png",
    "assets/characters/creator-01-surprised.svg",
    "assets/characters/creator-01-surprised.png",
    "assets/scenes/warm-desk-background.svg",
    "assets/scenes/warm-desk-background.png",
    "assets/scenes/scene-warm-desk-smile.svg",
    "assets/scenes/scene-warm-desk-smile.png",
    "docs/HOW-TO-USE.md",
]

results: list[tuple[str, str]] = []


def report(status: str, message: str) -> None:
    results.append((status, message))
    print(f"[{status}] {message}")


def check_python() -> None:
    if sys.version_info >= (3, 9):
        report("PASS", f"Python {sys.version.split()[0]}")
    else:
        report("FAIL", "Python 3.9+ is required")


def check_ffmpeg() -> None:
    """Verify the configured ffmpeg actually executes (FFMPEG_PATH is honored)."""
    status, detail = lib.ffmpeg_status()
    if status == "OK":
        report("PASS", f"ffmpeg runs: {detail}")
    else:
        report("WARN", f"ffmpeg {status}: {detail}")

    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        report("WARN", "ffprobe not on PATH (the venv imageio-ffmpeg binary provides ffmpeg only)")
        return
    try:
        result = subprocess.run(
            [ffprobe, "-version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            first_line = result.stdout.splitlines()[0] if result.stdout else "no output"
            report("PASS", f"ffprobe runs: {first_line}")
        else:
            report("WARN", f"ffprobe exited with code {result.returncode}")
    except (OSError, subprocess.SubprocessError) as exc:
        report("WARN", f"ffprobe found but cannot run: {exc}")


def ffmpeg_usable() -> tuple[bool, str]:
    """True only when the configured ffmpeg actually executes."""
    return lib.ffmpeg_status()


def check_blocked_skills() -> None:
    """Report ffmpeg-dependent skills as BLOCKED, never FAIL."""
    requires: list[str] = []
    if SKILLS_DIR.is_dir():
        for folder in sorted(SKILLS_DIR.iterdir()):
            skill_md = folder / "SKILL.md"
            if not folder.is_dir() or not skill_md.is_file():
                continue
            fields, _ = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
            if fields.get("requires", "").lower() == "ffmpeg":
                requires.append(folder.name)
    if not requires:
        return
    usable, detail = ffmpeg_usable()
    if usable:
        report("PASS", f"FFmpeg-required skills available: {len(requires)}")
        return
    report("BLOCKED", f"{len(requires)} skills require ffmpeg and are BLOCKED (not FAIL): {detail}")
    report("BLOCKED", "Blocked skills: " + ", ".join(requires))


def check_dirs() -> None:
    for item in REQUIRED_DIRS:
        if (ROOT / item).is_dir():
            report("PASS", f"Folder exists: {item}")
        else:
            report("FAIL", f"Missing folder: {item}")


def check_files() -> None:
    for item in REQUIRED_FILES:
        if (ROOT / item).is_file():
            report("PASS", f"File exists: {item}")
        else:
            report("FAIL", f"Missing file: {item}")


def check_json() -> None:
    for item in ["config/channel.json", "config/defaults.json", "config/skill-contracts.json"]:
        path = ROOT / item
        if not path.is_file():
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
            report("PASS", f"Valid JSON: {item}")
        except json.JSONDecodeError as exc:
            report("FAIL", f"Invalid JSON: {item} ({exc})")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return simple frontmatter fields and the body text."""
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
    return fields, text[end + 4 :]


def check_skills() -> None:
    """Validate skill folders against contracts and count statuses."""
    if not SKILLS_DIR.is_dir():
        report("FAIL", "Missing .opencode/skills folder")
        return

    contracts: dict = {}
    if CONTRACTS_PATH.is_file():
        try:
            contracts = json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            contracts = {}

    contract_skills = contracts.get("skills", {})
    if not isinstance(contract_skills, dict):
        report("FAIL", "skill-contracts.json: 'skills' must be an object")
        contract_skills = {}

    for name in sorted(contract_skills):
        folder = SKILLS_DIR / name
        if not folder.is_dir():
            report("FAIL", f"Contract skill has no folder: {name}")
        elif not (folder / "SKILL.md").is_file():
            report("FAIL", f"Contract skill has no SKILL.md: {name}")

    known_statuses = ("mvp", "planned", "implemented", "legacy")
    status_counts: Counter[str] = Counter()
    real_content = 0
    total = 0
    for folder in sorted(SKILLS_DIR.iterdir()):
        if not folder.is_dir():
            continue
        total += 1
        skill_md = folder / "SKILL.md"
        if not skill_md.is_file():
            report("FAIL", f"Skill folder has no SKILL.md: {folder.name}")
            continue

        fields, body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        frontmatter_name = fields.get("name", "")
        if frontmatter_name != folder.name:
            report(
                "FAIL",
                f"Frontmatter name '{frontmatter_name}' does not match folder '{folder.name}'",
            )

        status = fields.get("status", "unknown")
        status_counts[status] += 1
        if status != "legacy" and "TODO" not in body:
            real_content += 1

    parts = [f"{total} total"]
    for status in known_statuses:
        parts.append(f"{status_counts.get(status, 0)} {status}")
    report("PASS", "Skills by status: " + " | ".join(parts))
    report("PASS", f"Implemented with real content (non-legacy): {real_content}")

    unknown = sorted(set(status_counts) - set(known_statuses))
    if unknown:
        report("WARN", f"Unrecognized skill statuses: {', '.join(unknown)}")


def check_gitignore() -> None:
    path = ROOT / ".gitignore"
    if not path.is_file():
        report("FAIL", "Missing .gitignore")
        return
    content = path.read_text(encoding="utf-8")
    required = [".env", "*.mp4", "*.mp3", "output/", "projects/*/0[3-8]-*/*.mp4"]
    missing = [pattern for pattern in required if pattern not in content]
    if missing:
        report("FAIL", f".gitignore missing patterns: {', '.join(missing)}")
    else:
        report("PASS", ".gitignore covers secrets and large media")


def main() -> None:
    print("=== Shorts project health check ===")
    check_python()
    check_ffmpeg()
    check_dirs()
    check_files()
    check_json()
    check_skills()
    check_blocked_skills()
    check_gitignore()

    passes = sum(1 for status, _ in results if status == "PASS")
    warns = sum(1 for status, _ in results if status == "WARN")
    blocked = sum(1 for status, _ in results if status == "BLOCKED")
    fails = sum(1 for status, _ in results if status == "FAIL")
    print()
    print(f"Summary: {passes} PASS | {warns} WARN | {blocked} BLOCKED | {fails} FAIL")

    if fails:
        sys.exit(1)


if __name__ == "__main__":
    main()
