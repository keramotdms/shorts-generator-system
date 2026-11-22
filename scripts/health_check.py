#!/usr/bin/env python3
"""Basic repository health check. Stdlib only; no external packages."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

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
    "config/channel.json",
    "config/skill-contracts.json",
    "docs/lessons.md",
    "scripts/generate_audio.py",
    "scripts/orchestrator.py",
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
    """Verify ffmpeg/ffprobe are on PATH AND can actually execute."""
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        report("WARN", "FFmpeg/ffprobe not found on PATH (need approval before installing)")
        return

    for name, executable in (("ffmpeg", ffmpeg), ("ffprobe", ffprobe)):
        try:
            result = subprocess.run(
                [executable, "-version"],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if result.returncode == 0:
                first_line = result.stdout.splitlines()[0] if result.stdout else "no output"
                report("PASS", f"{name} runs: {first_line}")
            else:
                report("WARN", f"{name} found but exited with code {result.returncode}")
        except (OSError, subprocess.SubprocessError) as exc:
            report("WARN", f"{name} found but cannot run: {exc}")


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
    for item in ["config/channel.json", "config/skill-contracts.json"]:
        path = ROOT / item
        if not path.is_file():
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
            report("PASS", f"Valid JSON: {item}")
        except json.JSONDecodeError as exc:
            report("FAIL", f"Invalid JSON: {item} ({exc})")


def check_skill_naming() -> None:
    skills_dir = ROOT / ".opencode" / "skills"
    if not skills_dir.is_dir():
        report("FAIL", "Missing .opencode/skills folder")
        return

    bad = []
    placeholders = []
    checked = 0
    for folder in sorted(skills_dir.iterdir()):
        if not folder.is_dir():
            continue
        checked += 1
        if folder.name.startswith("shorts-"):
            bad.append(folder.name)
        if not (folder / "SKILL.md").is_file():
            placeholders.append(folder.name)

    if placeholders:
        report(
            "WARN",
            f"Placeholder skill folders (no SKILL.md yet, {len(placeholders)}): "
            + ", ".join(placeholders),
        )

    if bad:
        report("FAIL", f"Old 'shorts-' prefix still used: {', '.join(bad)}")
    else:
        report("PASS", f"Skill naming OK ({checked} skills checked)")


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
    check_skill_naming()
    check_gitignore()

    passes = sum(1 for status, _ in results if status == "PASS")
    warns = sum(1 for status, _ in results if status == "WARN")
    fails = sum(1 for status, _ in results if status == "FAIL")
    print()
    print(f"Summary: {passes} PASS | {warns} WARN | {fails} FAIL")

    if fails:
        sys.exit(1)


if __name__ == "__main__":
    main()
