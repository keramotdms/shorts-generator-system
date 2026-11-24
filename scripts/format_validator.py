#!/usr/bin/env python3
"""Validate a file against one declared output format profile.

Profiles live in ``config/output-formats.json``. Media checks use ffprobe;
text, SVG and PNG checks use the Python standard library. Nothing is installed
by this script. If ffprobe is unavailable on an office PC the media check is
reported as INFO instead of FAIL.

Usage:
    python scripts/format_validator.py <file> <profile>
    python scripts/format_validator.py --all
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skill_lib as lib  # noqa: E402

ROOT = lib.ROOT
PROFILES_PATH = ROOT / "config" / "output-formats.json"
CONTRACTS_PATH = ROOT / "config" / "skill-contracts.json"
BOM = b"\xef\xbb\xbf"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def pc_role() -> str:
    """PC_ROLE from the environment, then .env, then safe default 'office'.

    Only the PC_ROLE key is read from .env; no other values are loaded or
    printed, so secrets are never exposed here.
    """
    value = os.environ.get("PC_ROLE", "").strip().lower()
    if not value:
        env_file = ROOT / ".env"
        if env_file.is_file():
            for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
                text = line.strip()
                if text.startswith("PC_ROLE="):
                    value = text.split("=", 1)[1].strip().strip('"').strip("'").lower()
                    break
    return value if value in {"home", "office"} else "office"


def load_profiles() -> dict[str, dict[str, Any]]:
    data = lib.read_json(PROFILES_PATH)
    profiles = data.get("profiles") if isinstance(data, dict) else None
    if not isinstance(profiles, dict):
        raise lib.SkillError(f"{lib.relative(PROFILES_PATH)} has no profiles object")
    return profiles


def ffprobe_executable() -> Path | None:
    return lib.ffprobe_executable()


def probe(path: Path) -> dict[str, Any]:
    executable = ffprobe_executable()
    if executable is None:
        raise lib.SkillError("ffprobe not found")
    result = subprocess.run(
        [str(executable), "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise lib.SkillError(f"ffprobe failed: {result.stderr.strip()[:200]}")
    return json.loads(result.stdout)


def _streams(data: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    return [item for item in data.get("streams", []) if item.get("codec_type") == kind]


def _duration(data: dict[str, Any]) -> float:
    for source in (data.get("format", {}), *data.get("streams", [])):
        try:
            value = float(source.get("duration", 0))
        except (TypeError, ValueError):
            continue
        if value > 0:
            return value
    return 0.0


def _fps(stream: dict[str, Any]) -> float:
    for key in ("r_frame_rate", "avg_frame_rate"):
        value = str(stream.get(key, ""))
        if "/" in value:
            top, _, bottom = value.partition("/")
            try:
                result = float(top) / float(bottom)
                if result > 0:
                    return round(result, 3)
            except (ValueError, ZeroDivisionError):
                continue
    return 0.0


def _container(data: dict[str, Any]) -> set[str]:
    value = str(data.get("format", {}).get("format_name", ""))
    return {part.strip() for part in value.split(",") if part.strip()}


def _faststart(path: Path) -> bool | None:
    """True when the top-level moov box precedes mdat (faststart)."""
    total = path.stat().st_size
    position = 0
    with path.open("rb") as handle:
        while position + 8 <= total:
            handle.seek(position)
            header = handle.read(8)
            if len(header) < 8:
                break
            size = int.from_bytes(header[:4], "big")
            box_type = header[4:8].decode("latin1")
            if size == 1:
                size = int.from_bytes(handle.read(8), "big")
            elif size == 0:
                size = total - position
            if box_type == "moov":
                return True
            if box_type == "mdat":
                return False
            if size < 8:
                break
            position += size
    return None


def _text(path: Path, errors: list[str], *, check_bom: bool, check_utf8: bool) -> str | None:
    raw = path.read_bytes()
    if check_bom and raw.startswith(BOM):
        errors.append("UTF-8 BOM is forbidden")
        raw = raw[len(BOM):]
    if check_utf8:
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"not valid UTF-8: {exc}")
            return None
    return raw.decode("utf-8", errors="replace")


def _check_json(path: Path, errors: list[str]) -> None:
    text = _text(path, errors, check_bom=True, check_utf8=True)
    if text is None:
        return
    try:
        json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON: {exc}")


def _check_jsonl(path: Path, errors: list[str]) -> None:
    text = _text(path, errors, check_bom=True, check_utf8=True)
    if text is None:
        return
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {number} is not valid JSON: {exc}")


def _check_csv(path: Path, errors: list[str]) -> None:
    text = _text(path, errors, check_bom=True, check_utf8=True)
    if text is None:
        return
    try:
        rows = list(csv.reader(io.StringIO(text)))
    except csv.Error as exc:
        errors.append(f"invalid CSV: {exc}")
        return
    widths = {len(row) for row in rows if row}
    if len(widths) > 1:
        errors.append(f"inconsistent CSV column counts: {sorted(widths)}")


def _check_srt(path: Path, errors: list[str]) -> None:
    text = _text(path, errors, check_bom=True, check_utf8=True)
    if text is None:
        return
    if not re.search(r"(?m)^\d\d:\d\d:\d\d,\d\d\d\s+-->\s+\d\d:\d\d:\d\d,\d\d\d", text):
        errors.append("no SRT timestamp cue found")


def _check_svg(path: Path, checks: dict[str, Any], errors: list[str]) -> None:
    text = _text(path, errors, check_bom=bool(checks.get("no_bom")), check_utf8=True)
    if text is None:
        return
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as exc:
        errors.append(f"invalid XML/SVG: {exc}")
        return
    if checks.get("root_svg") and not root.tag.lower().endswith("svg"):
        errors.append(f"root element is {root.tag!r}, expected svg")
    minimum = int(checks.get("layer_groups_min", 0))
    if minimum:
        groups = [item for item in root.iter() if item.tag.lower().endswith("g") and item.get("id")]
        if len(groups) < minimum:
            errors.append(f"only {len(groups)} layer group(s), expected at least {minimum}")


def _check_png(path: Path, checks: dict[str, Any], errors: list[str]) -> None:
    raw = path.read_bytes()
    if checks.get("png_signature") and not raw.startswith(PNG_SIGNATURE):
        errors.append("missing PNG signature")
        return
    if len(raw) < 26:
        errors.append("PNG is too short to contain an IHDR header")
        return
    width = int.from_bytes(raw[16:20], "big")
    height = int.from_bytes(raw[20:24], "big")
    color_type = raw[25]
    if "width" in checks and width != int(checks["width"]):
        errors.append(f"width {width}, expected {checks['width']}")
    if "width_min" in checks and width < int(checks["width_min"]):
        errors.append(f"width {width} below minimum {checks['width_min']}")
    if "height" in checks and height != int(checks["height"]):
        errors.append(f"height {height}, expected {checks['height']}")
    if "height_min" in checks and height < int(checks["height_min"]):
        errors.append(f"height {height} below minimum {checks['height_min']}")
    allowed = checks.get("color_type_in")
    if allowed is not None and color_type not in {int(value) for value in allowed}:
        errors.append(f"PNG color type {color_type} not in {list(allowed)}")


def _check_font(path: Path, errors: list[str]) -> None:
    raw = path.read_bytes()[:4]
    if raw not in {b"\x00\x01\x00\x00", b"OTTO", b"ttcf", b"true"}:
        errors.append("missing TrueType/OpenType font signature")


def _check_media(path: Path, profile: str, checks: dict[str, Any], errors: list[str], infos: list[str]) -> None:
    if not checks.get("ffprobe"):
        return
    if ffprobe_executable() is None:
        message = "ffprobe not available; media parameters not checked"
        if pc_role() == "office":
            infos.append(message + " (INFO on office PC)")
        else:
            errors.append(message + " (required on home PC)")
        return
    try:
        data = probe(path)
    except (lib.SkillError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
        return

    containers = _container(data)
    expected_container = checks.get("container")
    if expected_container and expected_container not in containers:
        errors.append(f"container {sorted(containers)}, expected {expected_container}")
    allowed_containers = checks.get("container_in")
    if allowed_containers and not containers.intersection({str(v) for v in allowed_containers}):
        errors.append(f"container {sorted(containers)}, expected one of {list(allowed_containers)}")

    videos = _streams(data, "video")
    audios = _streams(data, "audio")
    if profile.startswith("mp4"):
        if not videos:
            errors.append("no video stream")
            return
        video = videos[0]
        expected_codec = checks.get("video_codec")
        if expected_codec and video.get("codec_name") != expected_codec:
            errors.append(f"video codec {video.get('codec_name')}, expected {expected_codec}")
        expected_profile = checks.get("video_profile")
        if expected_profile and video.get("profile") != expected_profile:
            errors.append(f"video profile {video.get('profile')}, expected {expected_profile}")
        expected_pix = checks.get("pixel_format")
        if expected_pix and video.get("pix_fmt") != expected_pix:
            errors.append(f"pixel format {video.get('pix_fmt')}, expected {expected_pix}")
        expected_width = checks.get("width")
        if expected_width and video.get("width") != int(expected_width):
            errors.append(f"width {video.get('width')}, expected {expected_width}")
        expected_height = checks.get("height")
        if expected_height and video.get("height") != int(expected_height):
            errors.append(f"height {video.get('height')}, expected {expected_height}")
        expected_fps = checks.get("fps")
        if expected_fps and _fps(video) != float(expected_fps):
            errors.append(f"fps {_fps(video)}, expected {expected_fps}")
        allowed_audio = checks.get("audio_codec_in")
        if allowed_audio is not None:
            actual = audios[0].get("codec_name", "none") if audios else "none"
            if actual not in {str(v) for v in allowed_audio}:
                errors.append(f"audio codec {actual}, expected one of {list(allowed_audio)}")
        expected_audio = checks.get("audio_codec")
        if expected_audio:
            actual = audios[0].get("codec_name") if audios else None
            if actual != expected_audio:
                errors.append(f"audio codec {actual}, expected {expected_audio}")
        expected_rate = checks.get("audio_sample_rate")
        if expected_rate:
            actual = audios[0].get("sample_rate") if audios else None
            if str(actual) != str(expected_rate):
                errors.append(f"audio sample rate {actual}, expected {expected_rate}")
        if checks.get("faststart") and _faststart(path) is not True:
            errors.append("moov atom is not before mdat (faststart required)")
    if profile in {"mp3_voice", "wav_mix"}:
        if not audios:
            errors.append("no audio stream")
            return
        audio = audios[0]
        expected_codec = checks.get("audio_codec")
        if expected_codec and audio.get("codec_name") != expected_codec:
            errors.append(f"audio codec {audio.get('codec_name')}, expected {expected_codec}")
        allowed_codecs = checks.get("audio_codec_in")
        if allowed_codecs and audio.get("codec_name") not in {str(v) for v in allowed_codecs}:
            errors.append(f"audio codec {audio.get('codec_name')}, expected one of {list(allowed_codecs)}")
        rates = checks.get("sample_rate_in")
        if rates and int(audio.get("sample_rate", 0)) not in {int(v) for v in rates}:
            errors.append(f"sample rate {audio.get('sample_rate')}, expected one of {list(rates)}")
        expected_rate = checks.get("sample_rate")
        if expected_rate and str(audio.get("sample_rate")) != str(expected_rate):
            errors.append(f"sample rate {audio.get('sample_rate')}, expected {expected_rate}")
        channels_max = checks.get("channels_max")
        if channels_max and int(audio.get("channels", 0)) > int(channels_max):
            errors.append(f"{audio.get('channels')} channels, maximum {channels_max}")

    maximum = checks.get("max_duration_sec")
    if maximum:
        duration = _duration(data)
        limit = float(maximum)
        if duration > limit or (profile == "mp4_final" and checks.get("max_duration_exclusive") and duration >= limit):
            errors.append(f"duration {duration:.2f}s exceeds {limit:g}s")


def validate_file(path: Path, profile: str) -> tuple[list[str], list[str]]:
    """Return (errors, infos) for one file and one profile."""
    profiles = load_profiles()
    if profile not in profiles:
        return [f"unknown profile {profile!r}"], []
    entry = profiles[profile]
    checks = entry.get("checks", {})
    errors: list[str] = []
    infos: list[str] = []
    if not path.is_file():
        return [f"missing file: {lib.relative(path)}"], []
    expected = entry.get("extension")
    if expected and path.suffix.lower() != expected:
        errors.append(f"extension {path.suffix or '<none>'}, expected {expected}")
    if checks.get("valid_json"):
        _check_json(path, errors)
    if checks.get("valid_jsonl"):
        _check_jsonl(path, errors)
    if checks.get("valid_csv"):
        _check_csv(path, errors)
    if checks.get("valid_srt"):
        _check_srt(path, errors)
    if checks.get("valid_xml") or checks.get("root_svg"):
        _check_svg(path, checks, errors)
    if checks.get("png_signature"):
        _check_png(path, checks, errors)
    if checks.get("font_signature"):
        _check_font(path, errors)
    if "non_empty" in checks and path.stat().st_size == 0:
        errors.append("file is empty")
    if checks.get("no_bom") and not (checks.get("valid_json") or checks.get("valid_jsonl") or checks.get("valid_csv") or checks.get("valid_srt") or checks.get("valid_xml")):
        _text(path, errors, check_bom=True, check_utf8=False)
    _check_media(path, profile, checks, errors, infos)
    return errors, infos


def declared_outputs() -> list[tuple[str, str, str]]:
    """(skill, exact path, profile) for every declared output."""
    data = lib.read_json(CONTRACTS_PATH)
    rows: list[tuple[str, str, str]] = []
    for name, entry in data.get("skills", {}).items():
        formats = entry.get("format", {})
        if not isinstance(formats, dict):
            continue
        for path, profile in formats.items():
            rows.append((name, str(path), str(profile)))
    return rows


def _existing(rows: list[tuple[str, str, str]]) -> list[tuple[str, Path, str]]:
    resolved: list[tuple[str, Path, str]] = []
    for skill, path, profile in rows:
        if "<" in path:
            continue
        target = Path(path)
        if not target.is_absolute():
            target = ROOT / target
        if target.is_file():
            resolved.append((skill, target, profile))
    return resolved


def validate_skill_outputs(skill: str) -> dict[str, Any]:
    rows = [(name, path, profile) for name, path, profile in declared_outputs() if name == skill]
    errors: list[str] = []
    infos: list[str] = []
    for _, path, profile in _existing(rows):
        found, notes = validate_file(path, profile)
        errors.extend(f"{lib.relative(path)} [{profile}]: {item}" for item in found)
        infos.extend(notes)
    return {"checked": len(_existing(rows)), "errors": errors, "infos": infos}


def validate_all_existing() -> dict[str, Any]:
    errors: list[str] = []
    infos: list[str] = []
    existing = _existing(declared_outputs())
    for _, path, profile in existing:
        found, notes = validate_file(path, profile)
        errors.extend(f"{lib.relative(path)} [{profile}]: {item}" for item in found)
        infos.extend(notes)
    return {"checked": len(existing), "errors": errors, "infos": infos}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="file to validate")
    parser.add_argument("profile", nargs="?", help="profile name from config/output-formats.json")
    parser.add_argument("--all", action="store_true", help="validate every declared output that exists")
    args = parser.parse_args()

    if args.all:
        summary = validate_all_existing()
        if summary["errors"]:
            for error in summary["errors"]:
                print("FAIL " + error)
            return 1
        for note in sorted(set(summary["infos"])):
            print("INFO " + note)
        print(f"PASS format-validator: {summary['checked']} declared output file(s) match their profiles")
        return 0

    if not args.path or not args.profile:
        parser.error("provide both PATH and PROFILE, or use --all")

    path = Path(args.path)
    if not path.is_absolute():
        path = ROOT / path
    errors, infos = validate_file(path, args.profile)
    for note in infos:
        print("INFO " + note)
    if errors:
        for error in errors:
            print("FAIL " + error)
        return 1
    print(f"PASS format-validator: {lib.relative(path)} matches {args.profile}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except lib.SkillError as exc:
        print(f"FAIL format-validator: {exc}")
        sys.exit(1)
