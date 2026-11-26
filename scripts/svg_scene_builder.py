#!/usr/bin/env python3
"""Build flat 2D SVG characters and scenes, then rasterize them to PNG.

No Python packages are installed. SVG is written with the standard library and
PNG conversion uses the already-installed Microsoft Edge headless renderer.
"""

from __future__ import annotations

import argparse
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skill_lib as lib

ROOT = lib.ROOT
WIDTH = 1080
HEIGHT = 1920
SAMPLE_CHARACTER = ROOT / "assets" / "characters" / "creator-01" / "character.json"
SAMPLE_SOURCE = ROOT / "tests" / "fixtures" / "valid" / "character.json"

EXPRESSION_ALIASES = {
    "neutral": "neutral",
    "smile": "smile",
    "smiling": "smile",
    "happy": "smile",
    "surprised": "surprised",
    "shock": "surprised",
    "worried": "worried",
    "concerned": "worried",
    "thinking": "thinking",
    "think": "thinking",
}
POSE_ALIASES = {
    "idle": "idle",
    "stand": "idle",
    "wave": "wave",
    "waving": "wave",
    "point": "point",
    "pointing": "point",
    "think": "think",
    "thinking": "think",
}

HAIR_COLORS = {
    "black": "#111827", "dark": "#111827", "brown": "#7C2D12",
    "blonde": "#F59E0B", "red": "#B91C1C", "white": "#E5E7EB",
}
SHIRT_COLORS = {
    "blue": "#2563EB", "green": "#10B981", "red": "#EF4444",
    "yellow": "#F59E0B", "amber": "#F59E0B", "orange": "#F97316",
    "white": "#F9FAFB", "black": "#111827", "purple": "#7C3AED",
}
BACKGROUND_COLORS = {
    "warm": "#FEF3C7", "amber": "#FDE68A", "green": "#D1FAE5",
    "mint": "#D1FAE5", "blue": "#DBEAFE", "sky": "#DBEAFE",
    "night": "#111827", "dark": "#1F2937", "gray": "#F3F4F6",
}
EDGE_CANDIDATES = [
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
]


def find_color(text: str, mapping: dict[str, str], fallback: str) -> str:
    lowered = text.lower()
    for word, color in mapping.items():
        if word in lowered:
            return color
    return fallback


def normalize_choice(value: str | None, aliases: dict[str, str], default: str) -> str:
    if not value:
        return default
    return aliases.get(value.strip().lower(), default)


def infer_expression(description: str) -> str:
    lowered = description.lower()
    if any(word in lowered for word in ("surpris", "shock", "wow", "অবাক")):
        return "surprised"
    if any(word in lowered for word in ("worried", "problem", "empty", "চিন্তা")):
        return "worried"
    if any(word in lowered for word in ("idea", "plan", "notebook", "ধাপ", "পরিকল্পনা")):
        return "thinking"
    if any(word in lowered for word in ("smile", "happy", "success", "start", "খুশি")):
        return "smile"
    return "neutral"


def infer_pose(description: str) -> str:
    lowered = description.lower()
    if any(word in lowered for word in ("wave", "hello", "স্বাগত")):
        return "wave"
    if any(word in lowered for word in ("point", "show", "দেখানো", "নির্দেশ")):
        return "point"
    if any(word in lowered for word in ("think", "phone", "notebook", "চিন্তা", "খাতা")):
        return "think"
    return "idle"


def wrap_svg(content: str, width: int = WIDTH, height: int = HEIGHT) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        f"{content}\n"
        "</svg>\n"
    )


def palette_of(character: dict[str, Any]) -> list[str]:
    palette = character.get("appearance", {}).get("palette", [])
    return [str(color) for color in palette if isinstance(color, str) and color.startswith("#")]


def face_markup(expression: str, outline: str) -> str:
    eye = f'<circle cx="475" cy="585" r="12" fill="{outline}"/>'
    eye += f'<circle cx="605" cy="585" r="12" fill="{outline}"/>'
    if expression == "surprised":
        eye = f'<circle cx="475" cy="585" r="22" fill="{outline}"/>'
        eye += f'<circle cx="605" cy="585" r="22" fill="{outline}"/>'
        return eye + f'<ellipse cx="540" cy="675" rx="34" ry="44" fill="{outline}"/>'
    if expression == "smile":
        return eye + (
            f'<path d="M485 655 Q540 715 595 655" fill="none" '
            f'stroke="{outline}" stroke-width="14" stroke-linecap="round"/>'
        )
    if expression == "worried":
        return eye + (
            f'<path d="M445 535 L505 550" stroke="{outline}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M635 535 L575 550" stroke="{outline}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M495 685 Q540 655 585 685" fill="none" '
            f'stroke="{outline}" stroke-width="12" stroke-linecap="round"/>'
        )
    if expression == "thinking":
        return (
            f'<circle cx="475" cy="585" r="12" fill="{outline}"/>'
            f'<path d="M575 585 Q605 565 635 585" fill="none" '
            f'stroke="{outline}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M450 535 L500 525" stroke="{outline}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M510 670 Q540 690 570 670" fill="none" '
            f'stroke="{outline}" stroke-width="12" stroke-linecap="round"/>'
        )
    return eye + (
        f'<path d="M500 670 L580 670" stroke="{outline}" stroke-width="12" stroke-linecap="round"/>'
    )


def arms_markup(pose: str, skin: str, outline: str) -> str:
    common = f'fill="none" stroke="{skin}" stroke-width="48" stroke-linecap="round"'
    edge = f'fill="none" stroke="{outline}" stroke-width="8" stroke-linecap="round"'
    if pose == "wave":
        return (
            f'<path d="M390 900 Q300 800 315 640" {common}/>'
            f'<path d="M390 900 Q300 800 315 640" {edge}/>'
            f'<circle cx="315" cy="630" r="34" fill="{skin}" stroke="{outline}" stroke-width="8"/>'
            f'<path d="M690 900 Q760 1050 720 1170" {common}/>'
            f'<path d="M690 900 Q760 1050 720 1170" {edge}/>'
        )
    if pose == "point":
        return (
            f'<path d="M390 900 Q320 1050 350 1150" {common}/>'
            f'<path d="M390 900 Q320 1050 350 1150" {edge}/>'
            f'<path d="M690 900 Q830 890 920 810" {common}/>'
            f'<path d="M690 900 Q830 890 920 810" {edge}/>'
            f'<circle cx="930" cy="800" r="32" fill="{skin}" stroke="{outline}" stroke-width="8"/>'
        )
    if pose == "think":
        return (
            f'<path d="M390 900 Q320 1050 350 1150" {common}/>'
            f'<path d="M390 900 Q320 1050 350 1150" {edge}/>'
            f'<path d="M690 900 Q790 830 705 730" {common}/>'
            f'<path d="M690 900 Q790 830 705 730" {edge}/>'
            f'<circle cx="700" cy="720" r="30" fill="{skin}" stroke="{outline}" stroke-width="8"/>'
        )
    return (
        f'<path d="M390 900 Q320 1050 350 1150" {common}/>'
        f'<path d="M390 900 Q320 1050 350 1150" {edge}/>'
        f'<path d="M690 900 Q760 1050 720 1170" {common}/>'
        f'<path d="M690 900 Q760 1050 720 1170" {edge}/>'
    )


def character_markup(character: dict[str, Any], expression: str, pose: str) -> str:
    if isinstance(character.get("parts"), dict):
        import character_designer

        return character_designer.character_markup(character, expression, pose)
    appearance = character.get("appearance", {})
    palette = palette_of(character)
    outline = palette[0] if palette else "#111827"
    accent = palette[3] if len(palette) > 3 else (palette[2] if len(palette) > 2 else "#10B981")
    fallback_shirt = palette[2] if len(palette) > 2 else "#2563EB"
    skin = "#F2C6A0"
    hair = find_color(str(appearance.get("hair", "")), HAIR_COLORS, outline)
    shirt = find_color(str(appearance.get("clothing", "")), SHIRT_COLORS, fallback_shirt)

    return (
        '  <g id="character">\n'
        f'    <rect x="430" y="1200" width="90" height="330" rx="45" fill="{outline}"/>\n'
        f'    <rect x="560" y="1200" width="90" height="330" rx="45" fill="{outline}"/>\n'
        f'    {arms_markup(pose, skin, outline)}\n'
        f'    <rect x="505" y="765" width="70" height="100" rx="25" fill="{skin}"/>\n'
        f'    <rect x="350" y="830" width="380" height="440" rx="130" fill="{shirt}" '
        f'stroke="{outline}" stroke-width="14"/>\n'
        f'    <path d="M350 980 Q540 1040 730 980" fill="none" stroke="{accent}" '
        f'stroke-width="20" stroke-linecap="round"/>\n'
        f'    <circle cx="540" cy="590" r="195" fill="{skin}" stroke="{outline}" stroke-width="14"/>\n'
        f'    <path d="M350 570 Q360 360 540 365 Q720 360 730 570 Q650 470 540 485 '
        f'Q430 470 350 570 Z" fill="{hair}"/>\n'
        f'    {face_markup(expression, outline)}\n'
        "  </g>"
    )


def props_markup(description: str, accent: str, outline: str, light: str = "#F9FAFB") -> str:
    """Render the reusable prop library when a scene description names a prop."""
    parts_path = ROOT / "assets" / "character-parts" / "parts.json"
    data = lib.read_json(parts_path, required=False)
    library = data.get("props", {}) if isinstance(data, dict) else {}
    lowered = description.lower()
    words = {
        "wallet": ("wallet", "পার্স", "মানিব্যাগ"),
        "phone": ("phone", "মোবাইল"),
        "notebook": ("notebook", "খাতা", "checklist", "তালিকা"),
        "coin": ("coin", "taka", "টাকা", "মুদ্রা"),
        "bar-graph": ("bar graph", "bar-graph", "chart", "growth", "লাভ", "বৃদ্ধি"),
    }
    positions = {
        "wallet": (840, 1420),
        "phone": (820, 1360),
        "notebook": (820, 1400),
        "coin": (860, 1460),
        "bar-graph": (810, 1340),
    }
    props = ""
    for name, triggers in words.items():
        if not any(trigger in lowered for trigger in triggers):
            continue
        template = library.get(name)
        if not template:
            continue
        values = {
            "{accent}": accent,
            "{outline}": outline,
            "{light}": light,
            "{outfit}": accent,
        }
        for key, value in values.items():
            template = str(template).replace(key, value)
        x, y = positions[name]
        props += f'<g transform="translate({x},{y})">{template}</g>'
    return f"  <g id=\"props\">{props}</g>" if props else ""


def background_markup(description: str, palette: list[str]) -> str:
    fallback = palette[1] if len(palette) > 1 else "#FEF3C7"
    accent = palette[2] if len(palette) > 2 else "#F59E0B"
    outline = palette[0] if palette else "#111827"
    background = find_color(description, BACKGROUND_COLORS, fallback)
    floor = "#E5E7EB" if background not in ("#111827", "#1F2937") else "#374151"
    return (
        '  <g id="background">\n'
        f'    <rect width="{WIDTH}" height="{HEIGHT}" fill="{background}"/>\n'
        f'    <rect x="0" y="1320" width="{WIDTH}" height="{HEIGHT - 1320}" fill="{floor}"/>\n'
        f'    <rect x="80" y="180" width="260" height="260" rx="28" fill="#F9FAFB" '
        f'stroke="{outline}" stroke-width="12"/>\n'
        f'    <path d="M210 180 L210 440 M80 310 L340 310" stroke="{outline}" stroke-width="10"/>\n'
        f'    <circle cx="900" cy="330" r="120" fill="{accent}" opacity="0.45"/>\n'
        f'    <rect x="90" y="1240" width="900" height="70" rx="24" fill="{accent}" '
        f'stroke="{outline}" stroke-width="12"/>\n'
        f'    {props_markup(description, accent, outline)}\n'
        "  </g>"
    )


def character_svg(character: dict[str, Any], expression: str, pose: str) -> str:
    return wrap_svg(character_markup(character, expression, pose))


def background_svg(description: str, palette: list[str]) -> str:
    return wrap_svg(background_markup(description, palette))


def scene_svg(character: dict[str, Any], description: str, expression: str, pose: str) -> str:
    palette = palette_of(character)
    return wrap_svg(
        background_markup(description, palette) + "\n" + character_markup(character, expression, pose)
    )


def load_character(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise lib.SkillError(f"Missing character file: {lib.relative(path)}")
    lib.validate_schema("character", path)
    data = lib.read_json(path)
    assert isinstance(data, dict)
    return data


def edge_executable() -> Path | None:
    which = shutil.which("msedge")
    if which:
        return Path(which)
    return next((path for path in EDGE_CANDIDATES if path.is_file()), None)


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise lib.SkillError(f"Not a PNG file: {lib.relative(path)}")
    return struct.unpack(">II", data[16:24])


def write_svg(path: Path, content: str) -> Path:
    lib.ensure(path)
    ElementTree.fromstring(content)
    path.write_text(content, encoding="utf-8")
    return path


def svg_to_png(svg_path: Path, png_path: Path) -> Path:
    edge = edge_executable()
    if edge is None:
        raise lib.SkillError(
            "No installed SVG-to-PNG converter found. Ask the user before installing one."
        )
    temp_root = ROOT / ".tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="svg-builder-", dir=str(temp_root)))
    png_absolute = png_path.resolve()
    lib.ensure(png_absolute)
    try:
        result = subprocess.run([
            str(edge), "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--no-first-run", "--disable-extensions", "--force-device-scale-factor=1",
            f"--user-data-dir={profile}",
            f"--screenshot={png_absolute}",
            f"--window-size={WIDTH},{HEIGHT}",
            svg_path.resolve().as_uri(),
        ], capture_output=True, text=True, timeout=120)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    if result.returncode != 0 or not png_path.is_file():
        detail = (result.stderr or result.stdout).strip()[-300:]
        raise lib.SkillError(f"SVG to PNG conversion failed: {detail}")
    size = png_size(png_path)
    if size != (WIDTH, HEIGHT):
        raise lib.SkillError(f"Unexpected PNG size {size}, expected {(WIDTH, HEIGHT)}")
    return png_path


def emit_pair(svg_path: Path, content: str, label: str) -> tuple[Path, Path]:
    svg = write_svg(svg_path, content)
    png = svg_to_png(svg, svg_path.with_suffix(".png"))
    lib.ok("svg-scene-builder", label, svg)
    print(f"OUTPUT {lib.relative(png)}")
    return svg, png


def cmd_character(args: argparse.Namespace) -> int:
    character = load_character(Path(args.character))
    expression = normalize_choice(args.expression, EXPRESSION_ALIASES, "neutral")
    pose = normalize_choice(args.pose, POSE_ALIASES, "idle")
    emit_pair(
        Path(args.out).with_suffix(".svg"),
        character_svg(character, expression, pose),
        f"character {character['id']} expression={expression} pose={pose}",
    )
    return 0


def cmd_scene(args: argparse.Namespace) -> int:
    character = load_character(Path(args.character))
    expression = normalize_choice(
        args.expression, EXPRESSION_ALIASES, infer_expression(args.description)
    )
    pose = normalize_choice(args.pose, POSE_ALIASES, infer_pose(args.description))
    palette = palette_of(character)
    if args.background_out:
        emit_pair(
            Path(args.background_out).with_suffix(".svg"),
            background_svg(args.description, palette),
            "background",
        )
    emit_pair(
        Path(args.out).with_suffix(".svg"),
        scene_svg(character, args.description, expression, pose),
        f"scene expression={expression} pose={pose}",
    )
    return 0


def cmd_sample(args: argparse.Namespace) -> int:
    if not SAMPLE_CHARACTER.is_file():
        lib.ensure(SAMPLE_CHARACTER)
        shutil.copy2(SAMPLE_SOURCE, SAMPLE_CHARACTER)
    character = load_character(SAMPLE_CHARACTER)
    characters_dir = ROOT / "assets" / "characters"
    scenes_dir = ROOT / "assets" / "scenes"

    for expression in ("neutral", "smile", "surprised"):
        emit_pair(
            characters_dir / f"{character['id']}-{expression}.svg",
            character_svg(character, expression, "idle"),
            f"sample character expression={expression}",
        )

    description = "warm desk corner, notebook and amber accent"
    emit_pair(
        scenes_dir / "warm-desk-background.svg",
        background_svg(description, palette_of(character)),
        "sample background",
    )
    emit_pair(
        scenes_dir / "scene-warm-desk-smile.svg",
        scene_svg(character, description, "smile", "point"),
        "sample scene character on background",
    )
    return 0


def self_test() -> int:
    print("SELF-TEST svg-scene-builder")
    if edge_executable() is None:
        print("BLOCKED svg-scene-builder: no installed SVG-to-PNG converter; ask before installing")
        return 0

    target = ROOT / ".tmp" / "svg-scene-builder-self-test"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    character = load_character(SAMPLE_SOURCE)

    for expression in ("neutral", "smile", "surprised"):
        svg = write_svg(
            target / f"{expression}.svg",
            character_svg(character, expression, "idle"),
        )
        ElementTree.parse(svg)
    background = write_svg(target / "background.svg", background_svg("warm desk", palette_of(character)))
    scene = write_svg(
        target / "scene.svg",
        scene_svg(character, "warm desk, notebook", "smile", "point"),
    )
    png = svg_to_png(scene, target / "scene.png")
    assert png_size(png) == (WIDTH, HEIGHT)
    assert infer_expression("worried about empty wallet") == "worried"
    assert infer_pose("point at a notebook") == "point"
    print("PASS svg-scene-builder: 3 expressions, background and scene validated")
    print(f"PASS svg-scene-builder: PNG {WIDTH}x{HEIGHT} rendered with installed Edge")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="validate SVG and PNG generation")
    sub = parser.add_subparsers(dest="command")

    character = sub.add_parser("character", help="draw one character expression")
    character.add_argument("--character", required=True)
    character.add_argument("--expression", default="neutral")
    character.add_argument("--pose", default="idle")
    character.add_argument("--out", required=True, help="output base path without extension")

    scene = sub.add_parser("scene", help="draw a character on a described background")
    scene.add_argument("--character", required=True)
    scene.add_argument("--description", required=True)
    scene.add_argument("--expression")
    scene.add_argument("--pose")
    scene.add_argument("--out", required=True, help="output base path without extension")
    scene.add_argument("--background-out", help="also write a background-only pair here")

    sub.add_parser("sample", help="write the sample assets into assets/")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.command == "character":
        return cmd_character(args)
    if args.command == "scene":
        return cmd_scene(args)
    if args.command == "sample":
        return cmd_sample(args)
    parser.error("a command or --self-test is required")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except lib.SkillError as exc:
        print(f"FAIL svg-scene-builder: {exc}")
        sys.exit(1)
