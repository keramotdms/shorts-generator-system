#!/usr/bin/env python3
"""Minimal PNG reader + bd-explainer rubric metrics (standard library only)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import zlib
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skill_lib as lib  # noqa: E402

ROOT = lib.ROOT
STYLE_PATH = ROOT / "config" / "style-bible.json"


def read_png(path: Path) -> tuple[int, int, list[tuple[int, int, int, int]]]:
    raw = path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise lib.SkillError(f"{path.name} is not a PNG")
    pos = 8
    width = height = 0
    bit_depth = colour_type = 0
    idat = bytearray()
    while pos < len(raw):
        length = struct.unpack(">I", raw[pos : pos + 4])[0]
        kind = raw[pos + 4 : pos + 8]
        data = raw[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, colour_type, _, _, interlace = struct.unpack(">IIBBBBB", data)
            if bit_depth != 8 or colour_type not in (2, 6) or interlace:
                raise lib.SkillError(
                    f"unsupported PNG (depth {bit_depth}, colour {colour_type}, interlace {interlace})"
                )
        elif kind == b"IDAT":
            idat.extend(data)
        elif kind == b"IEND":
            break
    channels = 3 if colour_type == 2 else 4
    stride = width * channels
    pixels: list[tuple[int, int, int, int]] = []
    previous = bytearray(stride)
    decompressed = zlib.decompress(bytes(idat))
    offset = 0
    for _ in range(height):
        filter_type = decompressed[offset]
        offset += 1
        line = bytearray(decompressed[offset : offset + stride])
        offset += stride
        if filter_type == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif filter_type == 2:
            for i in range(stride):
                line[i] = (line[i] + previous[i]) & 0xFF
        elif filter_type == 3:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((left + previous[i]) >> 1)) & 0xFF
        elif filter_type == 4:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                up = previous[i]
                upleft = previous[i - channels] if i >= channels else 0
                p = left + up - upleft
                pa, pb, pc = abs(p - left), abs(p - up), abs(p - upleft)
                pred = left if pa <= pb and pa <= pc else (up if pb <= pc else upleft)
                line[i] = (line[i] + pred) & 0xFF
        elif filter_type != 0:
            raise lib.SkillError(f"bad PNG filter {filter_type}")
        previous = line
        if channels == 4:
            pixels.extend(
                (line[i], line[i + 1], line[i + 2], line[i + 3]) for i in range(0, stride, 4)
            )
        else:
            pixels.extend(
                (line[i], line[i + 1], line[i + 2], 255) for i in range(0, stride, 3)
            )
    return width, height, pixels


def is_skin(r: int, g: int, b: int) -> bool:
    return r > 90 and r > g > b and r - b >= 32 and r - b <= 120 and g - b >= 12


def skin_percentiles(
    width: int, height: int, pixels: list[tuple[int, int, int, int]]
) -> dict[str, str]:
    """Sample only the face ellipse, where grey hair and cream beard are excluded."""
    values: list[tuple[int, int, int]] = []
    cx, cy, rx, ry = 540, 752, 205, 280
    for y in range(cy - ry, cy + ry, 2):
        if not 0 <= y < height:
            continue
        dy = (y - cy) / ry
        row = y * width
        for x in range(cx - rx, cx + rx, 2):
            if not 0 <= x < width or (x - cx) ** 2 / rx**2 + dy**2 > 1:
                continue
            r, g, b, a = pixels[row + x]
            if a > 200 and is_skin(r, g, b):
                values.append((r, g, b))
    if not values:
        raise lib.SkillError("no face skin pixels found")
    values.sort(key=lambda rgb: rgb[0] * 3 + rgb[1] * 2 + rgb[2])

    def pick(pct: float) -> str:
        index = min(len(values) - 1, max(0, round(pct / 100 * (len(values) - 1))))
        r, g, b = values[index]
        return f"#{r:02X}{g:02X}{b:02X}"

    return {"p20": pick(20), "median": pick(50), "p80": pick(80), "samples": str(len(values))}


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def colour_distance(first: str, second: str) -> float:
    a, b = hex_to_rgb(first), hex_to_rgb(second)
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def face_width_pct(svg_text: str) -> float:
    """Measure the rendered face from the character's declared geometry."""
    face = re.search(r'data-face-width="(\d+)"', svg_text)
    scale = re.search(r'data-frame-scale="([0-9.]+)"', svg_text)
    if not face or not scale:
        raise lib.SkillError("SVG has no bd-character face geometry")
    return int(face.group(1)) * float(scale.group(1)) / 1080 * 100


def svg_metrics(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    widths = [float(value) for value in re.findall(r'stroke-width="([0-9.]+)"', text)]
    return {
        "max_stroke": max(widths) if widths else 0.0,
        "gradients": text.count("<linearGradient") + text.count("<radialGradient"),
        "bytes": path.stat().st_size,
        "layer_ids": len(re.findall(r'id="bd-[a-z0-9-]+"', text)),
        "text": text,
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def style_targets() -> dict[str, Any]:
    style = lib.read_json(STYLE_PATH)
    return style["style_profiles"]["bd-explainer"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--png", required=True)
    parser.add_argument("--svg", required=True)
    parser.add_argument("--repeat", help="second render used for the determinism check")
    parser.add_argument("--seconds", type=float, help="measured render time")
    args = parser.parse_args()

    png_path = ROOT / args.png
    svg_path = ROOT / args.svg
    width, height, pixels = read_png(png_path)
    targets = style_targets()
    svg = svg_metrics(svg_path)
    skin = skin_percentiles(width, height, pixels)
    face_pct = face_width_pct(svg["text"])
    svg.pop("text")
    seconds = args.seconds
    if seconds is None:
        timing_path = ROOT / ".tmp" / "stage1-render-time.json"
        if timing_path.exists():
            seconds = float(lib.read_json(timing_path)["seconds"])
    svg["render_seconds"] = round(seconds, 3) if seconds is not None else None
    repeat_ok = bool(args.repeat) and sha256(png_path) == sha256(ROOT / args.repeat)

    checks = {
        "face_width": (
            38 <= face_pct <= 50,
            f"{face_pct:.1f}% (target 38-50%)",
        ),
        "max_stroke": (
            svg["max_stroke"] <= 2,
            f"{svg['max_stroke']:g}px (max 2px)",
        ),
        "gradients": (
            svg["gradients"] >= 8,
            f"{svg['gradients']} (min 6 character + 2 scene)",
        ),
        "skin_p20": (
            colour_distance(skin["p20"], targets["skin_targets"]["p20"]) <= 26,
            f"{skin['p20']} vs {targets['skin_targets']['p20']}",
        ),
        "skin_median": (
            colour_distance(skin["median"], targets["skin_targets"]["median"]) <= 26,
            f"{skin['median']} vs {targets['skin_targets']['median']}",
        ),
        "skin_p80": (
            colour_distance(skin["p80"], targets["skin_targets"]["p80"]) <= 26,
            f"{skin['p80']} vs {targets['skin_targets']['p80']}",
        ),
        "deterministic": (
            repeat_ok,
            "byte-identical re-render" if repeat_ok else "repeat missing or differs",
        ),
        "render_time": (
            seconds is not None and seconds < 5.0,
            f"{seconds:.2f}s (target < 5s)" if seconds is not None else "not measured",
        ),
    }
    print("| Check | Result | Detail |")
    print("| --- | --- | --- |")
    failed = 0
    for name, (ok, detail) in checks.items():
        print(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")
        failed += 0 if ok else 1
    print(json.dumps({"skin": skin, "svg": svg, "face_pct": face_pct}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except lib.SkillError as exc:
        print(f"FAIL bd-rubric: {exc}")
        raise SystemExit(1)
