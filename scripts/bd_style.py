#!/usr/bin/env python3
"""bd-explainer art style: framing, face system, soft shading and stage-one sheets.

The style is drawn from scratch with parametric SVG shapes. It does not trace,
sample or copy any reference video, character, logo or watermark. All geometry
below is original code built from the project's own part library.

No third-party packages are installed. PNG conversion reuses
``scripts/svg_scene_builder.py`` and the installed Microsoft Edge renderer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skill_lib as lib  # noqa: E402

ROOT = lib.ROOT
PARTS_PATH = ROOT / "assets" / "character-parts" / "parts.json"
STYLE_PATH = ROOT / "config" / "style-bible.json"
CHARACTERS_DIR = ROOT / "assets" / "characters"
SCENES_DIR = ROOT / "assets" / "scenes"
PROFILE = "bd-explainer"
EXPRESSIONS = ["neutral", "happy", "worried", "surprised", "thinking"]
TEARY = "teary"
ALL_EXPRESSIONS = EXPRESSIONS + [TEARY]
BD_LAYER_IDS = [
    "bd-body", "bd-outfit", "bd-outfit-details", "bd-arms", "bd-neck",
    "bd-head", "bd-head-shading", "bd-ears", "bd-hair", "bd-face",
    "bd-hands", "bd-accessory",
]
BD_FACE_IDS = [
    "bd-brows", "bd-eyes-sclera", "bd-iris", "bd-pupils", "bd-eye-highlights",
    "bd-eyelids", "bd-nose", "bd-cheek-tint", "bd-mouth",
]
HEAD_WIDTHS = {
    "head-oval": 300, "head-square": 270, "head-round": 330,
    "head-heart": 300, "head-long": 280, "head-diamond": 300,
}
HEAD_HEIGHTS = {
    "head-oval": 356, "head-square": 310, "head-round": 330,
    "head-heart": 376, "head-long": 380, "head-diamond": 378,
}
FRAMING = {
    "closeup": {"scale": 2.2, "translate_y": -620, "face": (55, 70)},
    "medium": {"scale": 1.7, "translate_y": -200, "face": (38, 50)},
    "full": {"scale": 0.9, "translate_y": 150, "face": (20, 30)},
}
BD_LINE = "#5A3A2A"
CREAM = "#E3DED4"
WHITE = "#F7F3EA"
GREY_HAIR = "#C9C4B8"
BEARD = "#E4DFD4"
MOUTH = "#8E4A45"
CHEEK = "#C96A5A"
GLASSES = "#47211B"


def load_parts() -> dict[str, Any]:
    data = lib.read_json(PARTS_PATH)
    if not isinstance(data, dict):
        raise lib.SkillError(f"{lib.relative(PARTS_PATH)} must contain a JSON object")
    return data


def load_style() -> dict[str, Any]:
    data = lib.read_json(STYLE_PATH)
    if not isinstance(data, dict):
        raise lib.SkillError(f"{lib.relative(STYLE_PATH)} must contain a JSON object")
    return data


def profile_of(style: dict[str, Any]) -> dict[str, Any]:
    profiles = style.get("style_profiles", {})
    profile = profiles.get(PROFILE) if isinstance(profiles, dict) else None
    if not isinstance(profile, dict):
        raise lib.SkillError("config/style-bible.json has no style_profiles.bd-explainer block")
    return profile


def slug_of(design: dict[str, Any]) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", str(design.get("id") or "character").lower()).strip("-")
    return slug or "character"


def gradient_ids(design: dict[str, Any]) -> dict[str, str]:
    slug = slug_of(design)
    return {
        kind: f"bd-grad-{kind}-{slug}"
        for kind in (
            "skin", "skin-shadow", "skin-light", "hair", "hair-shadow",
            "outfit", "outfit-shadow", "iris", "sclera", "cheek",
        )
    }


def _hex_rgb(color: str) -> tuple[int, int, int]:
    value = color.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def mix_color(first: str, second: str, amount: float) -> str:
    first_rgb, second_rgb = _hex_rgb(first), _hex_rgb(second)
    channels = [
        round(a + (b - a) * amount) for a, b in zip(first_rgb, second_rgb)
    ]
    return "#" + "".join(f"{max(0, min(255, channel)):02X}" for channel in channels)


def gradient_defs(design: dict[str, Any]) -> str:
    ids = gradient_ids(design)
    parts = design["parts"]
    skin = str(parts["skin"])
    hair = str(parts["hair_color"])
    outfit = str(parts["outfit_color"])
    eye = str(parts.get("eye_color") or "#47211B")

    def linear(identifier: str, base: str, light: float, dark: float) -> str:
        return (
            f'<linearGradient id="{identifier}" x1="0" y1="0" x2="0.62" y2="1">'
            f'<stop offset="0%" stop-color="{mix_color(base, "#FFFFFF", light)}"/>'
            f'<stop offset="52%" stop-color="{base}"/>'
            f'<stop offset="100%" stop-color="{mix_color(base, "#2A160F", dark)}"/>'
            "</linearGradient>"
        )

    def radial(identifier: str, base: str) -> str:
        return (
            f'<radialGradient id="{identifier}" cx="0.34" cy="0.28" r="0.8">'
            f'<stop offset="0%" stop-color="{mix_color(base, "#FFFFFF", 0.45)}"/>'
            f'<stop offset="100%" stop-color="{base}"/>'
            "</radialGradient>"
        )

    return (
        "<defs>"
        + linear(ids["skin"], skin, 0.22, 0.20)
        + linear(ids["skin-shadow"], mix_color(skin, "#47211B", 0.30), 0.08, 0.16)
        + radial(ids["skin-light"], mix_color(skin, "#FFFFFF", 0.30))
        + linear(ids["hair"], hair, 0.18, 0.22)
        + linear(ids["hair-shadow"], mix_color(hair, "#141E24", 0.32), 0.05, 0.14)
        + linear(ids["outfit"], outfit, 0.16, 0.24)
        + linear(ids["outfit-shadow"], mix_color(outfit, "#141E24", 0.34), 0.05, 0.16)
        + radial(ids["iris"], eye)
        + radial(ids["sclera"], WHITE)
        + radial(ids["cheek"], CHEEK)
        + f'<filter id="bd-soft-{slug_of(design)}" x="-30%" y="-30%" width="160%" height="160%">'
        + '<feGaussianBlur stdDeviation="12"/></filter>'
        + "</defs>"
    )


def resolve(markup: str, design: dict[str, Any]) -> str:
    ids = gradient_ids(design)
    parts = design["parts"]
    skin = str(parts["skin"])
    outline = str(parts["outline"])
    hair = str(parts["hair_color"])
    outfit = str(parts["outfit_color"])
    accent = str(parts["accent"])
    light = str(parts["light"])
    values = {
        "{skin}": f"url(#{ids['skin']})",
        "{skin_shadow}": f"url(#{ids['skin-shadow']})",
        "{skin_light}": f"url(#{ids['skin-light']})",
        "{skin_flat}": skin,
        "{skin_shadow_flat}": mix_color(skin, "#47211B", 0.30),
        "{skin_light_flat}": mix_color(skin, "#FFFFFF", 0.30),
        "{outline}": outline,
        "{hair}": f"url(#{ids['hair']})",
        "{hair_shadow}": f"url(#{ids['hair-shadow']})",
        "{hair_flat}": hair,
        "{outfit}": f"url(#{ids['outfit']})",
        "{outfit_shadow}": f"url(#{ids['outfit-shadow']})",
        "{outfit_flat}": outfit,
        "{accent}": accent,
        "{light}": light,
        "{cream}": CREAM,
        "{bd_line}": BD_LINE,
        "{brown_dark}": "#47211B",
        "{iris}": f"url(#{ids['iris']})",
        "{sclera}": f"url(#{ids['sclera']})",
        "{cheek}": f"url(#{ids['cheek']})",
        "{eye}": str(parts.get("eye_color") or outline),
    }
    for key, value in values.items():
        markup = markup.replace(key, value)
    return markup


def strip_strokes(markup: str) -> str:
    markup = re.sub(r'\sstroke="[^"]*"', "", markup)
    markup = re.sub(r'\sstroke-width="[^"]*"', "", markup)
    markup = re.sub(r'\sstroke-linejoin="[^"]*"', "", markup)
    markup = re.sub(r'\sstroke-linecap="[^"]*"', "", markup)
    markup = re.sub(r'\sstroke-dasharray="[^"]*"', "", markup)
    markup = re.sub(r'\sstroke-opacity="[^"]*"', "", markup)
    return markup


def soft_strokes(markup: str, width: int = 2) -> str:
    markup = re.sub(r'stroke="[^"]*"', f'stroke="{BD_LINE}"', markup)
    markup = re.sub(r'stroke-width="[^"]*"', f'stroke-width="{width}"', markup)
    if "stroke=" not in markup:
        return markup
    return f'<g stroke-opacity="0.32">{markup}</g>'


def outline_policy(markup: str, style: str, *, line: bool = False) -> str:
    if style == "thick":
        return markup
    if style == "soft":
        return soft_strokes(markup, 2)
    if line:
        return soft_strokes(markup, 2)
    return strip_strokes(markup)


def outline_style_of(design: dict[str, Any], style: dict[str, Any]) -> str:
    value = str(design.get("outline_style") or profile_of(style).get("outline_style") or "none")
    return value if value in {"none", "soft", "thick"} else "none"


def framing_of(design: dict[str, Any], style: dict[str, Any]) -> str:
    value = str(design.get("framing") or profile_of(style).get("framing") or "medium")
    return value if value in FRAMING else "medium"


def face_width(design: dict[str, Any]) -> int:
    return HEAD_WIDTHS.get(str(design["parts"]["head"]), 300)


def face_height(design: dict[str, Any]) -> int:
    return HEAD_HEIGHTS.get(str(design["parts"]["head"]), 356)


def head_shape(design: dict[str, Any]) -> str:
    head = str(design["parts"]["head"])
    if head == "head-square":
        return '<rect x="405" y="405" width="270" height="310" rx="72" fill="{skin}"/>'
    if head == "head-round":
        return '<circle cx="540" cy="560" r="165" fill="{skin}"/>'
    return '<ellipse cx="540" cy="560" rx="150" ry="178" fill="{skin}"/>'


def capsule(x1: float, y1: float, x2: float, y2: float, width: float, fill: str = "{skin}") -> str:
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    angle = -math.degrees(math.atan2(dx, dy))
    return (
        f'<rect x="{-width / 2:.1f}" y="0" width="{width:.1f}" height="{length:.1f}" '
        f'rx="{width / 2:.1f}" transform="translate({x1:.1f},{y1:.1f}) rotate({angle:.2f})" '
        f'fill="{fill}"/>'
    )


def wrist_positions(design: dict[str, Any], pose: str) -> tuple[tuple[int, int], tuple[int, int]]:
    width = int(design["proportions"]["shoulder_width"])
    left = 540 - width // 2
    right = 540 + width // 2
    if pose == "wave":
        right_pos = (right + 92, 668)
    elif pose == "point":
        right_pos = (right + 260, 810)
    elif pose == "think":
        right_pos = (right + 62, 720)
    else:
        right_pos = (right + 20, 1200)
    return (left - 20, 1200), right_pos


def hand_template(parts: dict[str, Any], name: str = "open") -> str:
    template = parts["detail"]["pro"]["hands"].get(name) or parts["detail"]["pro"]["hands"]["open"]
    return strip_strokes(str(template))


def hands_markup(
    design: dict[str, Any],
    pose: str,
    parts: dict[str, Any],
    *,
    skip_right: bool = False,
) -> str:
    template = hand_template(parts, "point" if pose == "point" else "open")
    left_pos, right_pos = wrist_positions(design, pose)
    left = f'<g transform="translate({left_pos[0]},{left_pos[1]})">{template}</g>'
    right = (
        ""
        if skip_right
        else (
            f'<g transform="translate({right_pos[0]},{right_pos[1]}) rotate(-8) scale(-1,1)">'
            f"{template}</g>"
        )
    )
    crease = (
        f'<g transform="translate({left_pos[0]},{left_pos[1]})">'
        '<path d="M-18 10 Q0 4 18 10 M-18 24 Q0 18 18 24" fill="none" '
        'stroke="{bd_line}" stroke-width="2" opacity="0.28"/></g>'
    )
    if not skip_right:
        crease += (
            f'<g transform="translate({right_pos[0]},{right_pos[1]}) scale(-1,1)">'
            '<path d="M-18 10 Q0 4 18 10 M-18 24 Q0 18 18 24" fill="none" '
            'stroke="{bd_line}" stroke-width="2" opacity="0.28"/></g>'
        )
    return left + right + crease


def arm_joints(design: dict[str, Any], pose: str, action: str) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]:
    """Return (left shoulder, left wrist, right shoulder, right wrist/elbow) in design units."""
    width = int(design["proportions"]["shoulder_width"])
    left = 540 - width // 2
    right = 540 + width // 2
    if action == "wiping_eye":
        right_elbow = (right + 56, 1032)
    elif pose == "wave":
        right_elbow = (right + 84, 900)
    elif pose == "point":
        right_elbow = (right + 150, 940)
    elif pose == "think":
        right_elbow = (right + 56, 950)
    else:
        right_elbow = (right + 18, 1040)
    return (left, 872), (left - 18, 1188), (right, 872), right_elbow


def arms_markup(design: dict[str, Any], pose: str, parts: dict[str, Any], *, action: str = "") -> str:
    left_shoulder, left_wrist, right_shoulder, right_elbow = arm_joints(design, pose, action)
    left_arm = (
        f'<circle cx="{left_shoulder[0]}" cy="{left_shoulder[1]}" r="30" fill="{{skin}}"/>'
        + capsule(*left_shoulder, *left_wrist, 44)
    )
    right_arm = (
        f'<circle cx="{right_shoulder[0]}" cy="{right_shoulder[1]}" r="30" fill="{{skin}}"/>'
        + capsule(*right_shoulder, *right_elbow, 44)
    )
    if action == "wiping_eye":
        right_arm += capsule(*right_elbow, 660, 650, 42)
    elif pose == "wave":
        right_arm += capsule(*right_elbow, right_elbow[0] + 30, 690, 42)
    elif pose == "point":
        right_arm += capsule(*right_elbow, right_elbow[0] + 110, 830, 42)
    elif pose == "think":
        right_arm += capsule(*right_elbow, right_elbow[0] + 10, 742, 42)
    shade = (
        f'<path d="M{left_shoulder[0] - 10} 900 Q{left_shoulder[0] - 26} 1040 {left_shoulder[0] - 14} 1170" '
        'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.25"/>'
        f'<path d="M{right_shoulder[0] + 10} 900 Q{right_shoulder[0] + 26} 1040 {right_shoulder[0] + 14} 1170" '
        'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.25"/>'
    )
    return left_arm + right_arm + shade


def sleeves_markup(design: dict[str, Any], pose: str, *, action: str = "") -> str:
    left_shoulder, _, right_shoulder, right_elbow = arm_joints(design, pose, action)
    left = capsule(*left_shoulder, left_shoulder[0] - 12, 962, 66, fill="{outfit}")
    right = capsule(*right_shoulder, right_elbow[0], 958, 66, fill="{outfit}")
    hems = (
        f'<path d="M{left_shoulder[0] - 44} 946 Q{left_shoulder[0] - 16} 972 {left_shoulder[0] + 14} 950" '
        'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.3"/>'
        f'<path d="M{right_shoulder[0] - 16} 946 Q{right_elbow[0] + 8} 972 {right_elbow[0] + 38} 950" '
        'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.3"/>'
    )
    return left + right + hems


def action_hand_markup(design: dict[str, Any], parts: dict[str, Any], action: str) -> str:
    if action != "wiping_eye":
        return ""
    template = str(parts["bd"]["hands"]["tissue"])
    return (
        '<g id="bd-action-hand" transform="translate(660,606) rotate(10) scale(-1,1)">'
        + template
        + "</g>"
    )


def head_shading(design: dict[str, Any]) -> str:
    fw = face_width(design)
    fh = face_height(design)
    cx, cy = 540, 560
    ry = fh / 2
    slug = slug_of(design)
    shadow = (
        f'<path d="M{cx + 0.34 * fw:.0f} {cy - 0.86 * ry:.0f} '
        f'Q{cx + 0.62 * fw:.0f} {cy:.0f} {cx + 0.34 * fw:.0f} {cy + 0.86 * ry:.0f} '
        f'L{cx + 0.62 * fw:.0f} {cy + 0.86 * ry:.0f} '
        f'L{cx + 0.62 * fw:.0f} {cy - 0.86 * ry:.0f} Z" '
        'fill="{skin_shadow}" opacity="0.55"/>'
    )
    highlight = (
        f'<ellipse cx="{cx - 0.24 * fw:.0f}" cy="{cy - 0.46 * ry:.0f}" '
        f'rx="{0.16 * fw:.0f}" ry="{0.12 * ry:.0f}" fill="{{skin_light}}" opacity="0.6"/>'
    )
    return (
        f'<g filter="url(#bd-soft-{slug})">' + shadow + highlight + "</g>"
    )


def ears_markup(design: dict[str, Any]) -> str:
    fw = face_width(design)
    fh = face_height(design)
    cx, cy = 540, 560
    r = 0.10 * fw
    ry = fh / 2
    left_x, right_x = cx - fw / 2 - 4, cx + fw / 2 + 4
    return (
        f'<circle cx="{left_x:.0f}" cy="{cy + 0.02 * ry:.0f}" r="{r:.0f}" fill="{{skin}}"/>'
        f'<circle cx="{right_x:.0f}" cy="{cy + 0.02 * ry:.0f}" r="{r:.0f}" fill="{{skin}}"/>'
        f'<path d="M{left_x - r * 0.35:.0f} {cy - r * 0.45:.0f} '
        f'Q{left_x + r * 0.25:.0f} {cy:.0f} {left_x - r * 0.20:.0f} {cy + r * 0.45:.0f}" '
        'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.3"/>'
        f'<path d="M{right_x + r * 0.35:.0f} {cy - r * 0.45:.0f} '
        f'Q{right_x - r * 0.25:.0f} {cy:.0f} {right_x + r * 0.20:.0f} {cy + r * 0.45:.0f}" '
        'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.3"/>'
    )


def hair_markup(design: dict[str, Any], parts: dict[str, Any]) -> str:
    age = design.get("age_features", {})
    fw = face_width(design)
    fh = face_height(design)
    cx, cy = 540, 560
    ry = fh / 2
    if age.get("bald_side"):
        grey = str(age.get("beard_color") or GREY_HAIR)
        rx, ry = fw / 2, fh / 2
        inner_rx, inner_ry = rx * 0.94, ry * 0.92
        drop = 0.58 * ry
        outer = (
            f'M{cx - rx:.0f} {cy:.0f} A{rx:.0f} {ry:.0f} 0 1 0 {cx + rx:.0f} {cy:.0f} '
            f'A{rx:.0f} {ry:.0f} 0 1 0 {cx - rx:.0f} {cy:.0f} Z'
        )
        opening = (
            f'M{cx - inner_rx:.0f} {cy + drop:.0f} '
            f'A{inner_rx:.0f} {inner_ry:.0f} 0 1 0 {cx + inner_rx:.0f} {cy + drop:.0f} '
            f'A{inner_rx:.0f} {inner_ry:.0f} 0 1 0 {cx - inner_rx:.0f} {cy + drop:.0f} Z'
        )
        cap = (
            f'<path fill-rule="evenodd" fill="{grey}" d="{outer} {opening}"/>'
        )
        strands = (
            f'<path d="M{cx - 0.36 * fw:.0f} {cy - 0.30 * ry:.0f} '
            f'Q{cx - 0.18 * fw:.0f} {cy - 0.46 * ry:.0f} {cx - 0.02 * fw:.0f} {cy - 0.42 * ry:.0f} '
            f'M{cx + 0.04 * fw:.0f} {cy - 0.42 * ry:.0f} '
            f'Q{cx + 0.20 * fw:.0f} {cy - 0.46 * ry:.0f} {cx + 0.36 * fw:.0f} {cy - 0.30 * ry:.0f}" '
            'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.22"/>'
        )
        return cap + strands
    template = str(parts["hairs"][design["parts"]["hair"]])
    return template


def eye_centers(design: dict[str, Any]) -> tuple[float, float, float]:
    fw = face_width(design)
    fh = face_height(design)
    return 540 - 0.22 * fw, 540 + 0.22 * fw, 560 + 0.10 * (fh / 2)


def eye_metrics(design: dict[str, Any], expression: str) -> dict[str, float]:
    fw = face_width(design)
    rx = 0.09 * fw
    ry = 0.045 * fw
    if expression == "surprised":
        ry *= 1.15
    elif expression == "happy":
        ry *= 0.78
    shift = 0.018 * fw if expression == "thinking" else 0.0
    return {
        "rx": rx,
        "ry": ry,
        "iris": 0.055 * fw,
        "pupil": 0.028 * fw,
        "highlight": 0.013 * fw,
        "shift": shift,
    }


def eyes_markup(design: dict[str, Any], expression: str) -> dict[str, str]:
    """Return the eye layers split into their own SVG groups."""
    left_x, right_x, y = eye_centers(design)
    m = eye_metrics(design, expression)
    rx, ry = m["rx"], m["ry"]
    iris_r, pupil_r, highlight_r = m["iris"], m["pupil"], m["highlight"]
    shift = m["shift"]
    sclera: list[str] = []
    iris: list[str] = []
    pupils: list[str] = []
    highlights: list[str] = []
    eyelids: list[str] = []
    for x in (left_x, right_x):
        sclera.append(
            f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="{{sclera}}"/>'
        )
        iris.append(
            f'<circle cx="{x + shift:.0f}" cy="{y + 0.02 * ry:.0f}" r="{iris_r:.0f}" fill="{{iris}}"/>'
        )
        pupils.append(
            f'<circle cx="{x + shift:.0f}" cy="{y + 0.02 * ry:.0f}" r="{pupil_r:.0f}" fill="{{brown_dark}}"/>'
        )
        highlights.append(
            f'<circle cx="{x + shift - highlight_r * 0.8:.0f}" '
            f'cy="{y - highlight_r * 0.8:.0f}" r="{highlight_r:.0f}" fill="{WHITE}"/>'
        )
        lid_y = y - ry * 0.55
        eyelids.append(
            f'<path d="M{x - rx:.0f} {lid_y:.0f} Q{x:.0f} {y - ry * 1.15:.0f} '
            f'{x + rx:.0f} {lid_y:.0f}" fill="none" stroke="{{bd_line}}" '
            'stroke-width="2" opacity="0.62"/>'
        )
        if expression == "happy":
            eyelids.append(
                f'<path d="M{x - rx * 0.7:.0f} {y + ry * 0.55:.0f} '
                f'Q{x:.0f} {y + ry * 1.15:.0f} {x + rx * 0.7:.0f} {y + ry * 0.55:.0f}" '
                'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.45"/>'
            )
        if expression == "teary":
            tear_x = x + rx * 0.55
            highlights.append(
                f'<path d="M{tear_x:.0f} {y + ry * 0.8:.0f} '
                f'Q{tear_x + 8:.0f} {y + ry * 1.8:.0f} {tear_x:.0f} {y + ry * 2.1:.0f} '
                f'Q{tear_x - 8:.0f} {y + ry * 1.8:.0f} {tear_x:.0f} {y + ry * 0.8:.0f} Z" '
                'fill="#9CC7D8" opacity="0.85"/>'
            )
            highlights.append(
                f'<circle cx="{x + shift - highlight_r * 0.6:.0f}" '
                f'cy="{y + ry * 0.5:.0f}" r="{highlight_r * 0.7:.0f}" fill="{WHITE}" opacity="0.8"/>'
            )
    return {
        "bd-eyes-sclera": "".join(sclera),
        "bd-iris": "".join(iris),
        "bd-pupils": "".join(pupils),
        "bd-eye-highlights": "".join(highlights),
        "bd-eyelids": "".join(eyelids),
    }


def brows_markup(design: dict[str, Any], expression: str) -> str:
    fw = face_width(design)
    fh = face_height(design)
    left_x, right_x, eye_y = eye_centers(design)
    y = eye_y - 0.20 * (fh / 2)
    half = 0.10 * fw
    thick = 0.04 * fw
    lift = {"happy": -0.10, "surprised": -0.22, "worried": 0.10, "teary": 0.08, "thinking": 0.04}.get(expression, 0.0)
    inner_lift = {"worried": -0.22, "teary": -0.20}.get(expression, 0.0)
    left = (
        f'<path d="M{left_x - half:.0f} {y + lift * thick:.0f} '
        f'Q{left_x - half * 0.2:.0f} {y - thick * 0.9 + inner_lift * thick:.0f} '
        f'{left_x + half:.0f} {y + lift * thick:.0f} '
        f'L{left_x + half:.0f} {y + thick * 0.9 + lift * thick:.0f} '
        f'Q{left_x - half * 0.2:.0f} {y + thick * 0.1 + inner_lift * thick:.0f} '
        f'{left_x - half:.0f} {y + thick * 0.9 + lift * thick:.0f} Z" fill="{{hair_flat}}"/>'
    )
    right = (
        f'<path d="M{right_x - half:.0f} {y + lift * thick:.0f} '
        f'Q{right_x + half * 0.2:.0f} {y - thick * 0.9 + inner_lift * thick:.0f} '
        f'{right_x + half:.0f} {y + lift * thick:.0f} '
        f'L{right_x + half:.0f} {y + thick * 0.9 + lift * thick:.0f} '
        f'Q{right_x + half * 0.2:.0f} {y + thick * 0.1 + inner_lift * thick:.0f} '
        f'{right_x - half:.0f} {y + thick * 0.9 + lift * thick:.0f} Z" fill="{{hair_flat}}"/>'
    )
    return left + right


def nose_markup(design: dict[str, Any]) -> str:
    fw = face_width(design)
    fh = face_height(design)
    cx, cy = 540, 560
    ry = fh / 2
    x = cx + 0.035 * fw
    return (
        f'<path d="M{x:.0f} {cy - 0.06 * ry:.0f} Q{x + 0.06 * fw:.0f} {cy + 0.12 * ry:.0f} '
        f'{x - 0.01 * fw:.0f} {cy + 0.22 * ry:.0f}" fill="none" stroke="{{bd_line}}" '
        'stroke-width="2" opacity="0.38"/>'
        f'<ellipse cx="{x + 0.01 * fw:.0f}" cy="{cy + 0.24 * ry:.0f}" '
        f'rx="{0.035 * fw:.0f}" ry="{0.012 * ry:.0f}" fill="{{skin_shadow_flat}}" opacity="0.45"/>'
    )


def mouth_markup(design: dict[str, Any], expression: str) -> str:
    fw = face_width(design)
    fh = face_height(design)
    cx, cy = 540, 560
    ry = fh / 2
    y = cy + 0.36 * ry
    half = 0.10 * fw
    if expression == "happy":
        return (
            f'<path d="M{cx - half:.0f} {y - 4:.0f} Q{cx:.0f} {y + 0.16 * ry:.0f} '
            f'{cx + half:.0f} {y - 4:.0f} Q{cx:.0f} {y + 0.05 * ry:.0f} '
            f'{cx - half:.0f} {y - 4:.0f} Z" fill="{MOUTH}"/>'
            f'<path d="M{cx - half * 0.7:.0f} {y + 2:.0f} Q{cx:.0f} {y + 0.10 * ry:.0f} '
            f'{cx + half * 0.7:.0f} {y + 2:.0f}" fill="none" stroke="{WHITE}" '
            'stroke-width="2" opacity="0.55"/>'
        )
    if expression == "worried" or expression == "teary":
        return (
            f'<path d="M{cx - half:.0f} {y + 6:.0f} Q{cx:.0f} {y - 0.08 * ry:.0f} '
            f'{cx + half:.0f} {y + 6:.0f}" fill="none" stroke="{MOUTH}" '
            'stroke-width="2" stroke-linecap="round"/>'
        )
    if expression == "surprised":
        return (
            f'<ellipse cx="{cx}" cy="{y + 4}" rx="{0.055 * fw:.0f}" ry="{0.075 * ry:.0f}" '
            f'fill="{MOUTH}"/>'
        )
    if expression == "thinking":
        return (
            f'<path d="M{cx - half * 0.7:.0f} {y + 2:.0f} Q{cx + half * 0.2:.0f} {y - 4:.0f} '
            f'{cx + half:.0f} {y + 4:.0f}" fill="none" stroke="{MOUTH}" '
            'stroke-width="2" stroke-linecap="round"/>'
        )
    return (
        f'<path d="M{cx - half * 0.7:.0f} {y:.0f} Q{cx:.0f} {y + 0.05 * ry:.0f} '
        f'{cx + half * 0.7:.0f} {y:.0f}" fill="none" stroke="{MOUTH}" '
        'stroke-width="2" stroke-linecap="round"/>'
    )


def cheek_markup(design: dict[str, Any]) -> str:
    fw = face_width(design)
    fh = face_height(design)
    cx, cy = 540, 560
    ry = fh / 2
    return (
        f'<ellipse cx="{cx - 0.30 * fw:.0f}" cy="{cy + 0.22 * ry:.0f}" '
        f'rx="{0.12 * fw:.0f}" ry="{0.07 * ry:.0f}" fill="{{cheek}}" opacity="0.22"/>'
        f'<ellipse cx="{cx + 0.30 * fw:.0f}" cy="{cy + 0.22 * ry:.0f}" '
        f'rx="{0.12 * fw:.0f}" ry="{0.07 * ry:.0f}" fill="{{cheek}}" opacity="0.22"/>'
    )


def age_features_of(design: dict[str, Any]) -> dict[str, Any]:
    age = design.get("age_features", {})
    return age if isinstance(age, dict) else {}


def beard_markup(design: dict[str, Any]) -> str:
    """Jaw-hugging beard drawn behind the mouth so the lips stay readable."""
    age = age_features_of(design)
    if not age.get("beard"):
        return ""
    fw = face_width(design)
    fh = face_height(design)
    cx, cy = 540, 560
    ry = fh / 2
    beard = str(age.get("beard_color") or BEARD)
    slug = slug_of(design)
    shape = (
        f'M{cx - 0.36 * fw:.0f} {cy + 0.20 * ry:.0f} '
        f'Q{cx - 0.38 * fw:.0f} {cy + 0.76 * ry:.0f} {cx:.0f} {cy + 0.90 * ry:.0f} '
        f'Q{cx + 0.38 * fw:.0f} {cy + 0.76 * ry:.0f} {cx + 0.36 * fw:.0f} {cy + 0.20 * ry:.0f} '
        f'Q{cx + 0.30 * fw:.0f} {cy + 0.46 * ry:.0f} {cx + 0.18 * fw:.0f} {cy + 0.50 * ry:.0f} '
        f'Q{cx:.0f} {cy + 0.60 * ry:.0f} {cx - 0.18 * fw:.0f} {cy + 0.50 * ry:.0f} '
        f'Q{cx - 0.30 * fw:.0f} {cy + 0.46 * ry:.0f} {cx - 0.36 * fw:.0f} {cy + 0.20 * ry:.0f} Z'
    )
    return (
        f'<g filter="url(#bd-soft-{slug})" transform="translate(0,5)">'
        f'<path d="{shape}" fill="{{skin_shadow}}" opacity="0.75"/></g>'
        f'<path d="{shape}" fill="{beard}"/>'
        f'<path d="M{cx - 0.18 * fw:.0f} {cy + 0.70 * ry:.0f} '
        f'Q{cx:.0f} {cy + 0.80 * ry:.0f} {cx + 0.18 * fw:.0f} {cy + 0.70 * ry:.0f}" '
        'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.2"/>'
    )


def mustache_markup(design: dict[str, Any]) -> str:
    age = age_features_of(design)
    if not age.get("mustache"):
        return ""
    fw = face_width(design)
    fh = face_height(design)
    cx, cy = 540, 560
    ry = fh / 2
    colour = str(age.get("beard_color") or BEARD)
    y = cy + 0.27 * ry
    return (
        f'<path d="M{cx - 0.01 * fw:.0f} {y:.0f} Q{cx - 0.10 * fw:.0f} {y - 0.06 * ry:.0f} '
        f'{cx - 0.20 * fw:.0f} {y + 0.00 * ry:.0f} Q{cx - 0.10 * fw:.0f} {y + 0.05 * ry:.0f} '
        f'{cx - 0.01 * fw:.0f} {y + 0.02 * ry:.0f} Z" fill="{colour}"/>'
        f'<path d="M{cx + 0.01 * fw:.0f} {y:.0f} Q{cx + 0.10 * fw:.0f} {y - 0.06 * ry:.0f} '
        f'{cx + 0.20 * fw:.0f} {y + 0.00 * ry:.0f} Q{cx + 0.10 * fw:.0f} {y + 0.05 * ry:.0f} '
        f'{cx + 0.01 * fw:.0f} {y + 0.02 * ry:.0f} Z" fill="{colour}"/>'
    )


def age_markup(design: dict[str, Any]) -> str:
    age = age_features_of(design)
    if not age.get("wrinkles"):
        return ""
    fw = face_width(design)
    fh = face_height(design)
    cx, cy = 540, 560
    ry = fh / 2
    left_x, right_x, eye_y = eye_centers(design)
    out: list[str] = []
    for offset in (0.36, 0.44, 0.52):
        out.append(
            f'<path d="M{cx - 0.14 * fw:.0f} {cy - offset * ry:.0f} '
            f'Q{cx:.0f} {cy - (offset + 0.04) * ry:.0f} {cx + 0.14 * fw:.0f} '
            f'{cy - offset * ry:.0f}" fill="none" stroke="{{bd_line}}" '
            'stroke-width="2" opacity="0.22"/>'
        )
    for x in (left_x, right_x):
        out.append(
            f'<path d="M{x - 0.12 * fw:.0f} {eye_y:.0f} L{x - 0.17 * fw:.0f} {eye_y + 0.03 * ry:.0f} '
            f'M{x - 0.12 * fw:.0f} {eye_y + 0.05 * ry:.0f} L{x - 0.17 * fw:.0f} {eye_y + 0.08 * ry:.0f}" '
            'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.24"/>'
        )
    out.append(
        f'<path d="M{cx - 0.12 * fw:.0f} {cy + 0.14 * ry:.0f} '
        f'Q{cx - 0.16 * fw:.0f} {cy + 0.28 * ry:.0f} {cx - 0.12 * fw:.0f} {cy + 0.38 * ry:.0f}" '
        'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.24"/>'
        f'<path d="M{cx + 0.12 * fw:.0f} {cy + 0.14 * ry:.0f} '
        f'Q{cx + 0.16 * fw:.0f} {cy + 0.28 * ry:.0f} {cx + 0.12 * fw:.0f} {cy + 0.38 * ry:.0f}" '
        'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.24"/>'
    )
    return "".join(out)


def glasses_markup(design: dict[str, Any]) -> str:
    fw = face_width(design)
    left_x, right_x, y = eye_centers(design)
    lens_w, lens_h = 0.22 * fw, 0.13 * fw
    glare = (
        f'<path d="M{left_x - lens_w * 0.28:.0f} {y + lens_h * 0.22:.0f} '
        f'L{left_x + lens_w * 0.05:.0f} {y - lens_h * 0.30:.0f} '
        f'M{right_x - lens_w * 0.28:.0f} {y + lens_h * 0.22:.0f} '
        f'L{right_x + lens_w * 0.05:.0f} {y - lens_h * 0.30:.0f}" '
        'fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.55"/>'
    )
    return (
        f'<rect x="{left_x - lens_w / 2:.0f}" y="{y - lens_h / 2:.0f}" '
        f'width="{lens_w:.0f}" height="{lens_h:.0f}" rx="{lens_h * 0.38:.0f}" '
        f'fill="none" stroke="{GLASSES}" stroke-width="2" opacity="0.85"/>'
        f'<rect x="{right_x - lens_w / 2:.0f}" y="{y - lens_h / 2:.0f}" '
        f'width="{lens_w:.0f}" height="{lens_h:.0f}" rx="{lens_h * 0.38:.0f}" '
        f'fill="none" stroke="{GLASSES}" stroke-width="2" opacity="0.85"/>'
        f'<path d="M{left_x + lens_w / 2:.0f} {y:.0f} L{right_x - lens_w / 2:.0f} {y:.0f}" '
        f'fill="none" stroke="{GLASSES}" stroke-width="2" opacity="0.85"/>'
        f'<path d="M{left_x - lens_w / 2:.0f} {y - 2:.0f} L{540 - fw / 2 - 2:.0f} {y - 6:.0f} '
        f'M{right_x + lens_w / 2:.0f} {y - 2:.0f} L{540 + fw / 2 + 2:.0f} {y - 6:.0f}" '
        f'fill="none" stroke="{GLASSES}" stroke-width="2" opacity="0.7"/>'
        + glare
    )


def outfit_details(design: dict[str, Any]) -> str:
    outfit = str(design["parts"]["outfit"])
    width = int(design["proportions"]["shoulder_width"])
    left, right = 540 - width // 2, 540 + width // 2
    if outfit in {"outfit-panjabi", "outfit-kurta", "outfit-salwar-kameez"}:
        return (
            f'<path d="M{540 - 0.10 * width:.0f} 820 L540 890 L{540 + 0.10 * width:.0f} 820" '
            'fill="none" stroke="{cream}" stroke-width="2" opacity="0.75"/>'
            f'<path d="M540 895 L540 1260" fill="none" stroke="{{cream}}" stroke-width="2" opacity="0.7"/>'
            f'<circle cx="540" cy="950" r="5" fill="{{cream}}"/>'
            f'<circle cx="540" cy="1030" r="5" fill="{{cream}}"/>'
            f'<circle cx="540" cy="1110" r="5" fill="{{cream}}"/>'
            f'<path d="M{left + 20} 900 Q{left + 8} 1040 {left + 18} 1200" fill="none" '
            'stroke="{bd_line}" stroke-width="2" opacity="0.22"/>'
            f'<path d="M{right - 20} 900 Q{right - 8} 1040 {right - 18} 1200" fill="none" '
            'stroke="{bd_line}" stroke-width="2" opacity="0.22"/>'
        )
    return (
        f'<path d="M{540 - 0.11 * width:.0f} 820 L540 890 L{540 + 0.11 * width:.0f} 820" '
        'fill="none" stroke="{cream}" stroke-width="2" opacity="0.7"/>'
        f'<path d="M540 895 L540 1240" fill="none" stroke="{{bd_line}}" stroke-width="2" opacity="0.35"/>'
        f'<circle cx="540" cy="960" r="4" fill="{{accent}}"/>'
        f'<circle cx="540" cy="1030" r="4" fill="{{accent}}"/>'
        f'<circle cx="540" cy="1100" r="4" fill="{{accent}}"/>'
        f'<path d="M{left + 24} 910 Q{left + 10} 1040 {left + 22} 1180" fill="none" '
        'stroke="{bd_line}" stroke-width="2" opacity="0.2"/>'
        f'<path d="M{right - 24} 910 Q{right - 10} 1040 {right - 22} 1180" fill="none" '
        'stroke="{bd_line}" stroke-width="2" opacity="0.2"/>'
    )


def neck_markup(design: dict[str, Any], parts: dict[str, Any]) -> str:
    fw = face_width(design)
    fh = face_height(design)
    cx, cy = 540, 560
    top = cy + fh / 2 - 30
    half_top, half_bottom = 0.19 * fw, 0.19 * fw
    slug = slug_of(design)
    return (
        f'<path d="M{cx - half_top:.0f} {top:.0f} L{cx + half_top:.0f} {top:.0f} '
        f'L{cx + half_bottom:.0f} 872 L{cx - half_bottom:.0f} 872 Z" fill="{{skin}}"/>'
        f'<g filter="url(#bd-soft-{slug})">'
        f'<path d="M{cx - half_top - 4:.0f} {top + 6:.0f} '
        f'Q{cx:.0f} {top + 44:.0f} {cx + half_top + 4:.0f} {top + 6:.0f} '
        f'L{cx + half_top + 4:.0f} {top + 40:.0f} '
        f'Q{cx:.0f} {top + 74:.0f} {cx - half_top - 4:.0f} {top + 40:.0f} Z" '
        'fill="{skin_shadow}" opacity="0.55"/></g>'
        f'<path d="M{cx - half_bottom + 10:.0f} 852 Q{cx:.0f} 866 {cx + half_bottom - 10:.0f} 852" '
        'fill="none" stroke="{bd_line}" stroke-width="2" opacity="0.22"/>'
    )


def face_group(design: dict[str, Any], expression: str) -> str:
    tilt = float(design.get("head_tilt") or 0.0)
    tilt = max(-8.0, min(8.0, tilt))
    yaw = float(design.get("yaw") or 0.0)
    yaw = max(-20.0, min(20.0, yaw))
    fw = face_width(design)
    shift = yaw / 20.0 * 0.06 * fw
    age = design.get("age_features", {})
    eyes = eyes_markup(design, expression)
    parts = [f'<g id="bd-beard">{beard_markup(design)}</g>']
    parts.append(f'<g id="bd-brows">{brows_markup(design, expression)}</g>')
    parts.extend(f'<g id="{layer_id}">{markup}</g>' for layer_id, markup in eyes.items())
    parts.extend(
        [
            f'<g id="bd-nose">{nose_markup(design)}</g>',
            f'<g id="bd-cheek-tint">{cheek_markup(design)}</g>',
            f'<g id="bd-mouth">{mouth_markup(design, expression)}</g>',
            f'<g id="bd-mustache">{mustache_markup(design)}</g>',
            f'<g id="bd-age">{age_markup(design)}</g>',
        ]
    )
    if isinstance(age, dict) and (age.get("glasses_glare") or design["parts"].get("accessory") == "accessory-glasses"):
        parts.append(f'<g id="bd-glasses">{glasses_markup(design)}</g>')
    return (
        f'<g id="bd-face" transform="translate({shift:.1f},0) rotate({tilt:.1f},540,560)">'
        + "".join(parts)
        + "</g>"
    )


def bd_layers(
    design: dict[str, Any],
    expression: str,
    pose: str,
    parts: dict[str, Any],
    style: dict[str, Any],
    *,
    framing: str | None = None,
) -> list[tuple[str, str]]:
    outline_style = outline_style_of(design, style)
    age = design.get("age_features", {})
    action = str(design.get("action") or "")
    expression = expression if expression in ALL_EXPRESSIONS else "neutral"
    raw: list[tuple[str, str]] = [
        ("bd-body", outline_policy(str(parts["bodies"][design["parts"]["body"]]), outline_style)),
        ("bd-outfit", outline_policy(str(parts["outfits"][design["parts"]["outfit"]]), outline_style)),
        ("bd-outfit-details", outline_policy(outfit_details(design), outline_style, line=True)),
        ("bd-arms", arms_markup(design, pose, parts, action=action)),
        ("bd-sleeves", outline_policy(sleeves_markup(design, pose, action=action), outline_style)),
        ("bd-neck", outline_policy(neck_markup(design, parts), outline_style, line=True)),
        ("bd-head", head_shape(design)),
        ("bd-head-shading", head_shading(design)),
        ("bd-ears", ears_markup(design)),
        ("bd-hair", outline_policy(hair_markup(design, parts), outline_style)),
        ("bd-face", face_group(design, expression)),
        ("bd-hands", hands_markup(design, pose, parts, skip_right=action == "wiping_eye")),
        ("bd-accessory", ""),
    ]
    if action == "wiping_eye":
        raw.append(("bd-action-hand", action_hand_markup(design, parts, action)))
    return [(layer_id, resolve(markup, design)) for layer_id, markup in raw]


def bd_character_markup(
    design: dict[str, Any],
    expression: str,
    pose: str,
    parts: dict[str, Any],
    style: dict[str, Any],
    *,
    framing: str | None = None,
) -> str:
    level_framing = framing or framing_of(design, style)
    config = FRAMING[level_framing]
    scale = config["scale"]
    translate_y = config["translate_y"]
    translate_x = 540 - 540 * scale
    fw = face_width(design)
    body = "\n".join(
        f'  <g id="{layer_id}">{markup}</g>'
        for layer_id, markup in bd_layers(design, expression, pose, parts, style, framing=level_framing)
    )
    return (
        f'  <g id="bd-character" data-skin="{design["parts"]["skin"]}" '
        f'data-face-width="{fw}" data-frame-scale="{scale}" '
        f'data-outline-style="{outline_style_of(design, style)}">\n'
        f'    {gradient_defs(design)}\n'
        f'    <g id="bd-framing" transform="translate({translate_x:.2f},{translate_y}) scale({scale})">\n'
        f"{body}\n"
        "    </g>\n"
        "  </g>"
    )


def background_markup(design: dict[str, Any]) -> str:
    palette = load_parts().get("bd", {}).get("scene_palette", {})
    tan = str(palette.get("warm_tan") or "#AC7D56")
    cream = str(palette.get("cream") or CREAM)
    return (
        '  <g id="bd-background">\n'
        '    <defs>\n'
        f'      <linearGradient id="bd-bg-base-{slug_of(design)}" x1="0" y1="0" x2="0.4" y2="1">\n'
        f'        <stop offset="0%" stop-color="{mix_color(tan, "#FFFFFF", 0.28)}"/>\n'
        f'        <stop offset="55%" stop-color="{tan}"/>\n'
        f'        <stop offset="100%" stop-color="{mix_color(cream, "#47211B", 0.18)}"/>\n'
        "      </linearGradient>\n"
        f'      <radialGradient id="bd-bg-glow-{slug_of(design)}" cx="0.28" cy="0.18" r="0.75">\n'
        f'        <stop offset="0%" stop-color="{cream}" stop-opacity="0.75"/>\n'
        f'        <stop offset="100%" stop-color="{cream}" stop-opacity="0"/>\n'
        "      </radialGradient>\n"
        "    </defs>\n"
        f'    <rect width="1080" height="1920" fill="url(#bd-bg-base-{slug_of(design)})"/>\n'
        f'    <rect width="1080" height="1920" fill="url(#bd-bg-glow-{slug_of(design)})"/>\n'
        "  </g>"
    )


def bd_scene_svg(
    design: dict[str, Any],
    expression: str,
    pose: str,
    parts: dict[str, Any],
    style: dict[str, Any],
) -> str:
    import svg_scene_builder

    return svg_scene_builder.wrap_svg(
        background_markup(design) + "\n" + bd_character_markup(design, expression, pose, parts, style)
    )


def creator_design(style: dict[str, Any]) -> dict[str, Any]:
    path = CHARACTERS_DIR / "creator-01" / "character.json"
    design = lib.read_json(path)
    if not isinstance(design, dict):
        raise lib.SkillError("creator-01/character.json must contain a JSON object")
    design["style_profile"] = PROFILE
    design["outline_style"] = "none"
    design["framing"] = "medium"
    design["head_tilt"] = 0
    design["yaw"] = 0
    design.setdefault("age_features", {})
    return design


def elder_design(style: dict[str, Any], parts: dict[str, Any]) -> dict[str, Any]:
    profile = profile_of(style)
    skin = str(profile.get("skin_targets", {}).get("median") or "#A27350")
    return {
        "id": "elder-01",
        "name": "আব্দুল করিম",
        "style_source": "config/style-bible.json",
        "style_profile": PROFILE,
        "outline_style": "none",
        "framing": "medium",
        "head_tilt": -3,
        "yaw": 0,
        "age_features": {
            "wrinkles": True,
            "beard": True,
            "beard_color": BEARD,
            "mustache": True,
            "bald_side": True,
            "grey_hair": True,
            "glasses_glare": True,
        },
        "action": "wiping_eye",
        "brief": {
            "role": "teacher",
            "role_label": "শিক্ষক",
            "age": 68,
            "gender": "male",
            "personality": "calm",
            "niche": "Personal finance / side hustles",
            "language": "bn",
        },
        "parts": {
            "head": "head-oval",
            "hair": "hair-short-crop",
            "eyes": "eyes-round",
            "brows": "brows-soft",
            "mouth": "mouth-neutral",
            "body": "body-average",
            "outfit": "outfit-panjabi",
            "accessory": "accessory-glasses",
            "skin": skin,
            "hair_color": GREY_HAIR,
            "eye_color": "#47211B",
            "outfit_color": "#742C2A",
            "accent": "#E3DED4",
            "outline": "#47211B",
            "light": "#F5E9DC",
        },
        "proportions": {
            "head_height": HEAD_HEIGHTS["head-oval"],
            "total_height": 1300,
            "head_to_body": round(HEAD_HEIGHTS["head-oval"] / 1300, 3),
            "shoulder_width": 210,
        },
        "appearance": {
            "body": "body-average",
            "hair": "hair-square-grey",
            "clothing": "outfit-panjabi",
            "palette": ["#47211B", "#E3DED4", "#742C2A", "#AC7D56", skin],
        },
        "voice": {"gender": "male", "tone": "calm and reassuring"},
        "expressions": list(ALL_EXPRESSIONS),
        "poses": ["idle", "wave", "point"],
        "mouth_shapes": ["closed", "open", "wide", "smile"],
        "detail_level": "pro",
        "locked": True,
    }


def compare_pro_vs_bd_svg(design: dict[str, Any], parts: dict[str, Any], style: dict[str, Any]) -> str:
    import svg_scene_builder
    import character_designer

    light = "#F5E9DC"
    outline = "#47211B"
    tiles: list[str] = [f'  <g id="compare-pro-bd-background"><rect width="1080" height="1920" fill="{light}"/></g>']
    tiles.append("  " + character_designer.gradient_defs(design))
    tiles.append("  " + gradient_defs(design))
    for row, expression in enumerate(EXPRESSIONS):
        for column, mode in enumerate(("pro", "bd-explainer")):
            x, y = column * 540, row * 384
            tiles.append(f'  <g id="compare-pro-bd-{mode}-{expression}">')
            tiles.append(
                f'    <rect x="{x}" y="{y}" width="540" height="384" fill="{light}" '
                f'stroke="{outline}" stroke-width="2" opacity="0.25"/>'
            )
            tiles.append(f'    <g transform="translate({x + 167},{y + 2}) scale(0.19)">')
            if mode == "pro":
                for layer_id, markup in character_designer.layers(
                    design, expression, "idle", prefix=f"pro{row:02d}-", detail_level="pro"
                ):
                    tiles.append(f'      <g id="{layer_id}">{markup}</g>')
            else:
                bd_design = json.loads(json.dumps(design))
                bd_design["style_profile"] = PROFILE
                bd_design["outline_style"] = "none"
                bd_design["framing"] = "medium"
                bd_design["head_tilt"] = 0
                bd_design["yaw"] = 0
                for layer_id, markup in bd_layers(
                    bd_design, expression, "idle", parts, style, framing="full"
                ):
                    tiles.append(f'      <g id="{layer_id}">{markup}</g>')
            tiles.append("    </g>")
            tiles.append(
                f'    <rect x="{x}" y="{y + 350}" width="540" height="34" fill="{outline}" opacity="0.82"/>'
            )
            label = "pro" if mode == "pro" else "bd-explainer"
            tiles.append(
                f'    <text x="{x + 12}" y="{y + 374}" font-family="sans-serif" font-size="20" '
                f'fill="{light}">{label} / {expression}</text>'
            )
            tiles.append("  </g>")
    return svg_scene_builder.wrap_svg("\n".join(tiles))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_stage1() -> dict[str, Any]:
    import svg_scene_builder

    style = load_style()
    parts = load_parts()
    creator = creator_design(style)
    elder = elder_design(style, parts)

    SCENES_DIR.mkdir(parents=True, exist_ok=True)
    elder_svg_path = SCENES_DIR / "stage1-elder-medium.svg"
    elder_png_path = SCENES_DIR / "stage1-elder-medium.png"
    svg_scene_builder.write_svg(
        elder_svg_path, bd_scene_svg(elder, TEARY, "idle", parts, style)
    )
    start = time.perf_counter()
    svg_scene_builder.svg_to_png(elder_svg_path, elder_png_path)
    elapsed = time.perf_counter() - start
    timing_path = ROOT / ".tmp" / "stage1-render-time.json"
    timing_path.parent.mkdir(parents=True, exist_ok=True)
    timing_path.write_text(json.dumps({"seconds": round(elapsed, 3)}), encoding="utf-8")

    repeat_png = ROOT / ".tmp" / "stage1-elder-medium-repeat.png"
    repeat_png.parent.mkdir(parents=True, exist_ok=True)
    svg_scene_builder.svg_to_png(elder_svg_path, repeat_png)

    compare_svg_path = CHARACTERS_DIR / "creator-01" / "compare-pro-vs-bd.svg"
    compare_png_path = CHARACTERS_DIR / "creator-01" / "compare-pro-vs-bd.png"
    svg_scene_builder.write_svg(compare_svg_path, compare_pro_vs_bd_svg(creator, parts, style))
    svg_scene_builder.svg_to_png(compare_svg_path, compare_png_path)

    lib.ok(
        "bd-style",
        "stage 1 elder medium and creator-01 pro-vs-bd compare rendered",
        elder_png_path,
    )
    print(f"OUTPUT {lib.relative(elder_png_path)}")
    print(f"OUTPUT {lib.relative(compare_png_path)}")
    return {
        "elder_svg": elder_svg_path,
        "elder_png": elder_png_path,
        "elder_repeat_png": repeat_png,
        "compare_svg": compare_svg_path,
        "compare_png": compare_png_path,
        "elapsed": elapsed,
        "elder": elder,
        "creator": creator,
    }


def self_test() -> int:
    import svg_scene_builder

    if svg_scene_builder.edge_executable() is None:
        print("BLOCKED bd-style: no installed SVG-to-PNG converter; ask before installing")
        return 0

    style = load_style()
    parts = load_parts()
    elder = elder_design(style, parts)
    target = ROOT / ".tmp" / "self-test" / "bd-style"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)

    svg_text = bd_scene_svg(elder, TEARY, "idle", parts, style)
    svg_path = target / "elder.svg"
    svg_scene_builder.write_svg(svg_path, svg_text)
    png = svg_scene_builder.svg_to_png(svg_path, target / "elder.png")
    assert svg_scene_builder.png_size(png) == (1080, 1920)
    for layer_id in BD_LAYER_IDS:
        assert f'id="{layer_id}"' in svg_text, layer_id
    for layer_id in BD_FACE_IDS:
        assert f'id="{layer_id}"' in svg_text, layer_id
    assert svg_text.count("<linearGradient") + svg_text.count("<radialGradient") >= 6
    widths = [float(value) for value in re.findall(r'stroke-width="([0-9.]+)"', svg_text)]
    assert max(widths) <= 2, max(widths)
    scale = FRAMING["medium"]["scale"]
    face_pct = face_width(elder) * scale / 1080 * 100
    assert 38 <= face_pct <= 50, face_pct
    print(
        f"PASS bd-style: elder medium, {len(BD_LAYER_IDS)} body layers, "
        f"{face_pct:.1f}% face width, max stroke {max(widths):g}px"
    )
    print("PASS bd-style: 10 character gradients and no heavy outline in the default style")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage1", action="store_true", help="render the stage 1 outputs")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.stage1:
        build_stage1()
        return 0
    parser.error("use --stage1 or --self-test")
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except lib.SkillError as exc:
        print(f"FAIL bd-style: {exc}")
        raise SystemExit(1)
