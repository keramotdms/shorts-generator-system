#!/usr/bin/env python3
"""Shared helpers for all Shorts skills. Stdlib only, no side effects on import."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROJECT = "_template"
CONFIG_DIR = ROOT / "config"
CHANNEL_PATH = CONFIG_DIR / "channel.json"
DEFAULTS_PATH = CONFIG_DIR / "defaults.json"
STYLE_BIBLE_PATH = CONFIG_DIR / "style-bible.json"

STAGE_DIRS = {
    1: "01-research",
    2: "02-script",
    3: "03-voice",
    4: "04-character",
    5: "05-scene",
    6: "06-video",
    7: "07-edit",
    8: "08-final-test",
    9: "09-description",
    10: "10-publish",
}


class SkillError(RuntimeError):
    """Raised when required input is missing or invalid."""


def project_name() -> str:
    return os.environ.get("PROJECT", DEFAULT_PROJECT)


def project_dir() -> Path:
    return ROOT / "projects" / project_name()


def stage(stage_number: int, *parts: str) -> Path:
    if stage_number not in STAGE_DIRS:
        raise SkillError(f"Unknown stage number: {stage_number}")
    base = project_dir() / STAGE_DIRS[stage_number]
    return base.joinpath(*parts) if parts else base


def ensure(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def validate_schema(schema_name: str, path: Path) -> None:
    """Validate a JSON file against config/schemas/<schema_name>.json."""
    import schema_validator

    errors = schema_validator.validate_file(schema_name, path)
    if errors:
        raise SkillError(
            f"Schema validation failed for {relative(path)}: " + "; ".join(errors)
        )


def read_json(path: Path, *, required: bool = True) -> Any:
    if not path.is_file():
        if required:
            raise SkillError(f"Missing input file: {relative(path)}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SkillError(f"Invalid JSON in {relative(path)}: {exc}") from exc


def write_json(path: Path, data: Any) -> Path:
    ensure(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path


def write_text(path: Path, text: str) -> Path:
    ensure(path).write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    return path


def json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def json_loads(text: str) -> Any:
    return json.loads(text)


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_channel() -> dict[str, Any]:
    """Always read niche/language/location through project-memory's source file."""
    data = read_json(CHANNEL_PATH)
    if not isinstance(data, dict):
        raise SkillError("config/channel.json must contain a JSON object")
    for key in ("niche", "language", "audience_location"):
        if data.get(key) in (None, "", "TO BE DECIDED"):
            raise SkillError(
                f"config/channel.json has a null '{key}'. Ask the user once, then save "
                "it through project-memory before running any other skill."
            )
    return data


def load_style_bible(*, required: bool = True) -> dict[str, Any]:
    data = read_json(STYLE_BIBLE_PATH, required=required)
    if data is None:
        if required:
            raise SkillError("Missing config/style-bible.json — run project-memory first")
        return {}
    return data


def style_context() -> dict[str, Any]:
    """Niche/language/location/style; the only approved source for these values."""
    channel = load_channel()
    bible = load_style_bible(required=False)
    return {
        "niche": channel["niche"],
        "language": channel["language"],
        "audience_location": channel["audience_location"],
        "video": channel.get("video", {}),
        "style": bible.get("style", {}),
        "characters": bible.get("characters", {}),
        "voice": bible.get("voice", {}),
    }


def ffmpeg_executable() -> Path | None:
    """FFMPEG_PATH setting first, then defaults.json, then PATH."""
    candidates: list[str] = []
    env_value = os.environ.get("FFMPEG_PATH", "").strip()
    if env_value:
        candidates.append(env_value)
    defaults = read_json(DEFAULTS_PATH, required=False) or {}
    config_value = defaults.get("ffmpeg_path")
    if config_value:
        candidates.append(str(config_value))
    found = shutil.which("ffmpeg")
    if found:
        candidates.append(found)
    for value in candidates:
        path = Path(value)
        if path.is_file():
            return path
    return None


def ffmpeg_status() -> tuple[str, str]:
    """Return ('OK'|'BLOCKED'|'MISSING', detail)."""
    executable = ffmpeg_executable()
    if executable is None:
        return "MISSING", "ffmpeg not found (set FFMPEG_PATH)"
    try:
        result = subprocess.run(
            [str(executable), "-version"],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return "BLOCKED", str(exc)
    if result.returncode == 0:
        return "OK", result.stdout.splitlines()[0] if result.stdout else "ffmpeg -version OK"
    return "BLOCKED", f"exit code {result.returncode}: {result.stderr.strip()[:200]}"


def require_ffmpeg() -> Path:
    status, detail = ffmpeg_status()
    if status != "OK":
        raise SkillError(
            f"FFmpeg is {status}: {detail}. Skill output is BLOCKED; set FFMPEG_PATH "
            "after the Windows application-control policy is resolved."
        )
    return ffmpeg_executable()


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def append_jsonl(path: Path, entry: dict[str, Any]) -> Path:
    ensure(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path


def ok(skill: str, message: str, output: Path | None = None) -> None:
    print(f"PASS {skill}: {message}")
    if output is not None:
        print(f"OUTPUT {relative(output)}")
