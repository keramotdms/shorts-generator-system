#!/usr/bin/env python3
"""Deterministic 2D character design for the character-designer skill.

The part library lives in ``assets/character-parts/parts.json``. Every design is
built by explicit rules from ``projects/<project>/04-character/character-brief.json``
and the palette in ``config/style-bible.json``. Rendering reuses
``scripts/svg_scene_builder.py`` so scenes and previews use one renderer.

No Python packages are installed. SVG parsing uses the standard library and PNG
conversion uses the already-installed Microsoft Edge renderer.
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
CHARACTERS_DIR = ROOT / "assets" / "characters"
EXPRESSIONS = ["neutral", "happy", "worried", "surprised", "thinking"]
POSES = ["idle", "wave", "point"]
DETAIL_LEVELS = ("basic", "standard", "rich")
DEFAULT_DETAIL_LEVEL = "rich"
BASE_LAYER_IDS = [
    "body", "outfit", "arms", "neck", "head", "hair",
    "brows", "eyes", "mouth", "accessory",
]
STANDARD_LAYER_IDS = [
    "ears", "jaw_shadow", "hairline_shadow", "hair_strands", "hair_highlight",
    "brow_detail", "iris", "pupils", "eye_highlights", "eyelids", "lashes",
    "nose", "blush",
]
RICH_LAYER_IDS = [
    "ground_shadow", "shoes", "folds", "belt", "collar", "placket", "cuffs",
    "hands",
]
OUTLINE_WIDTH = 10
DETAIL_WIDTH = 4
ARM_WIDTH = 44
ALLOWED_STROKE_WIDTHS = {float(OUTLINE_WIDTH), float(DETAIL_WIDTH), float(ARM_WIDTH)}
MAX_SVG_BYTES = 200 * 1024
MAX_RENDER_SECONDS = 5.0
BASE_NECK = '<rect x="505" y="712" width="70" height="118" rx="26" fill="{skin}" stroke="{outline}" stroke-width="10"/>'
MIN_CONTRAST = 3.0
MIN_PALETTE_COLORS = 3
MIN_RATIO = 0.18
MAX_RATIO = 0.30

HEAD_HEIGHTS = {
    "head-round": 330, "head-oval": 356, "head-square": 310,
    "head-heart": 376, "head-long": 380, "head-diamond": 378,
}
BODY_HEIGHTS = {
    "body-slim": 1290, "body-average": 1300, "body-sturdy": 1320,
    "body-tall": 1380, "body-petite": 1230,
}
SHOULDER_WIDTHS = {
    "body-slim": 170, "body-average": 210, "body-sturdy": 260,
    "body-tall": 190, "body-petite": 150,
}

ROLE_OUTFITS = {
    "teacher": ["outfit-shirt-vest", "outfit-formal", "outfit-panjabi"],
    "student": ["outfit-hoodie", "outfit-t-shirt", "outfit-shirt"],
    "freelancer": ["outfit-t-shirt", "outfit-hoodie", "outfit-shirt"],
    "shop-owner": ["outfit-apron", "outfit-panjabi", "outfit-kurta"],
    "office": ["outfit-formal", "outfit-shirt-vest", "outfit-shirt"],
    "creator": ["outfit-shirt", "outfit-t-shirt", "outfit-panjabi"],
}
ROLE_ACCESSORIES = {
    "teacher": ["accessory-glasses", "accessory-lanyard", "accessory-watch"],
    "student": ["accessory-cap", "accessory-bag", "accessory-earrings"],
    "freelancer": ["accessory-bag", "accessory-glasses", "accessory-watch"],
    "shop-owner": ["accessory-watch", "accessory-lanyard", "accessory-scarf"],
    "office": ["accessory-tie", "accessory-glasses", "accessory-watch"],
    "creator": ["accessory-glasses", "accessory-earrings", "accessory-watch"],
}
ROLE_NAMES = {
    "teacher": "শিক্ষক", "student": "শিক্ষার্থী", "freelancer": "ফ্রিল্যান্সার",
    "shop-owner": "দোকানদার", "office": "চাকরিজীবী", "creator": "কনটেন্ট ক্রিয়েটর",
}
PERSONALITY_MOUTHS = {
    "warm": ["mouth-smile", "mouth-neutral", "mouth-grin"],
    "serious": ["mouth-closed", "mouth-neutral", "mouth-frown"],
    "energetic": ["mouth-open", "mouth-grin", "mouth-wide"],
    "calm": ["mouth-neutral", "mouth-closed", "mouth-smile"],
    "worried": ["mouth-frown", "mouth-thinking", "mouth-closed"],
    "thoughtful": ["mouth-thinking", "mouth-neutral", "mouth-closed"],
}
PERSONALITY_BROWS = {
    "warm": ["brows-soft", "brows-raised", "brows-soft"],
    "serious": ["brows-straight", "brows-worried", "brows-straight"],
    "energetic": ["brows-raised", "brows-soft", "brows-raised"],
    "calm": ["brows-soft", "brows-straight", "brows-soft"],
    "worried": ["brows-worried", "brows-soft", "brows-worried"],
    "thoughtful": ["brows-soft", "brows-worried", "brows-straight"],
}


def load_parts() -> dict[str, Any]:
    data = lib.read_json(PARTS_PATH)
    if not isinstance(data, dict):
        raise lib.SkillError(f"{lib.relative(PARTS_PATH)} must contain a JSON object")
    return data


def _clamp_age(value: Any) -> int:
    try:
        age = int(value)
    except (TypeError, ValueError):
        age = 30
    return max(12, min(80, age))


def normalize_role(value: Any) -> str:
    text = str(value or "").strip().lower()
    for role, words in {
        "teacher": ("teacher", "mentor", "educator", "trainer", "শিক্ষক"),
        "student": ("student", "school", "college", "university", "শিক্ষার্থী"),
        "freelancer": ("freelance", "freelancer", "creator", "youtuber", "ফ্রিল্যান্স"),
        "shop-owner": ("shop", "seller", "business", "store", "দোকান"),
        "office": ("office", "manager", "employee", "banker", "চাকরি"),
    }.items():
        if any(word in text for word in words):
            return role
    return "creator"


def normalize_personality(value: Any) -> str:
    text = str(value or "").strip().lower()
    for key in PERSONALITY_MOUTHS:
        if key in text:
            return key
    if any(word in text for word in ("friendly", "kind", "warm", "বন্ধু")):
        return "warm"
    if any(word in text for word in ("serious", "strict", "গম্ভীর")):
        return "serious"
    if any(word in text for word in ("energy", "lively", "fun", "প্রাণবন্ত")):
        return "energetic"
    if any(word in text for word in ("think", "analytical", "চিন্তা")):
        return "thoughtful"
    return "calm"


def load_brief(path: Path | None = None) -> dict[str, Any]:
    target = path or lib.stage(4, "character-brief.json")
    data = lib.read_json(target)
    if not isinstance(data, dict):
        raise lib.SkillError(f"{lib.relative(target)} must contain a JSON object")
    role = normalize_role(data.get("role"))
    personality = normalize_personality(data.get("personality"))
    return {
        "project": str(data.get("project") or lib.project_name()),
        "role": role,
        "role_label": ROLE_NAMES[role],
        "age": _clamp_age(data.get("age", 30)),
        "gender": str(data.get("gender") or "male").strip().lower(),
        "personality": personality,
        "niche": str(data.get("niche") or lib.load_channel()["niche"]),
        "language": str(data.get("language") or lib.load_channel()["language"]),
        "name": str(data.get("name") or "অনিক"),
        "character_id": str(data.get("character_id") or "creator-01"),
    }


def contrast_ratio(first: str, second: str) -> float:
    def luminance(color: str) -> float:
        value = color.lstrip("#")
        if len(value) != 6:
            return 0.0
        channels = [int(value[index:index + 2], 16) / 255.0 for index in (0, 2, 4)]
        linear = [
            channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def style_colors(style: dict[str, Any], parts: dict[str, Any]) -> dict[str, str]:
    palette = [str(color) for color in style.get("style", {}).get("palette", []) if str(color).startswith("#")]
    if len(palette) < 4:
        raise lib.SkillError("config/style-bible.json style.palette must hold at least 4 hex colours")
    return {
        "outline": palette[0],
        "light": palette[1],
        "accent": palette[2],
        "outfit": palette[3],
        "all": palette,
    }


def skin_palette(style: dict[str, Any], parts: dict[str, Any], outline: str) -> list[str]:
    values = [str(color) for color in style.get("style", {}).get("skin_palette", []) if str(color).startswith("#")]
    if not values:
        values = [str(color) for color in parts.get("palettes", {}).get("skin", []) if str(color).startswith("#")]
    passing = [color for color in values if contrast_ratio(color, outline) >= MIN_CONTRAST]
    return passing or sorted(values, key=lambda color: contrast_ratio(color, outline), reverse=True)[:2]


def _pick(values: list[str], index: int) -> str:
    return values[(index - 1) % len(values)]


def _hex_rgb(color: str) -> tuple[int, int, int]:
    value = color.lstrip("#")
    if len(value) != 6:
        return (0, 0, 0)
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))  # type: ignore[return-value]


def mix_color(first: str, second: str, amount: float) -> str:
    """Deterministic linear mix; amount 0 keeps first, 1 returns second."""
    ratio = max(0.0, min(1.0, float(amount)))
    a = _hex_rgb(first)
    b = _hex_rgb(second)
    return "#" + "".join(f"{round(a[index] + (b[index] - a[index]) * ratio):02X}" for index in range(3))


def gradient_ids(design: dict[str, Any]) -> dict[str, str]:
    slug = re.sub(r"[^a-z0-9-]+", "-", str(design.get("id") or "character").lower()).strip("-")
    slug = slug or "character"
    return {kind: f"grad-{kind}-{slug}" for kind in ("skin", "hair", "outfit", "iris")}


def gradient_defs(design: dict[str, Any]) -> str:
    """Linear gradients with a fixed top-left light direction; no random values."""
    ids = gradient_ids(design)
    parts = design["parts"]
    eye = str(parts.get("eye_color") or parts["outline"])

    def gradient(identifier: str, base: str, light: float, dark: float) -> str:
        return (
            f'<linearGradient id="{identifier}" x1="0" y1="0" x2="0.65" y2="1">'
            f'<stop offset="0%" stop-color="{mix_color(base, "#FFFFFF", light)}"/>'
            f'<stop offset="55%" stop-color="{base}"/>'
            f'<stop offset="100%" stop-color="{mix_color(base, "#000000", dark)}"/>'
            "</linearGradient>"
        )

    return (
        "<defs>"
        + gradient(ids["skin"], str(parts["skin"]), 0.18, 0.12)
        + gradient(ids["hair"], str(parts["hair_color"]), 0.22, 0.10)
        + gradient(ids["outfit"], str(parts["outfit_color"]), 0.16, 0.14)
        + gradient(ids["iris"], eye, 0.35, 0.0)
        + "</defs>"
    )


def detail_level_of(design: dict[str, Any], override: str | None = None) -> str:
    value = str(override if override is not None else design.get("detail_level") or "basic").strip().lower()
    return value if value in DETAIL_LEVELS else "basic"


def normalize_strokes(markup: str) -> str:
    """Map every stroke width to the documented scale: 10 outline, 4 detail.

    Exactly two widths survive, so a detail render is visually consistent and
    the self-test can assert the whole document uses only the documented scale.
    """
    def replace(match: re.Match[str]) -> str:
        value = float(match.group(1))
        width = OUTLINE_WIDTH if value >= 8 else DETAIL_WIDTH
        return f'stroke-width="{width}"'

    return re.sub(r'stroke-width="([0-9.]+)"', replace, markup)


def required_layer_ids(level: str) -> list[str]:
    ids = list(BASE_LAYER_IDS)
    if level in {"standard", "rich"}:
        ids += STANDARD_LAYER_IDS
    if level == "rich":
        ids += RICH_LAYER_IDS
    return ids


def _head_for(age: int, variant: int) -> str:
    if age < 25:
        choices = ["head-round", "head-oval", "head-heart"]
    elif age < 40:
        choices = ["head-oval", "head-square", "head-heart"]
    elif age < 55:
        choices = ["head-square", "head-oval", "head-diamond"]
    else:
        choices = ["head-square", "head-long", "head-diamond"]
    return _pick(choices, variant)


def _hair_for(gender: str, age: int, variant: int) -> str:
    if gender == "female":
        choices = ["hair-bun", "hair-long", "hair-braids", "hair-bob", "hair-curly"]
    elif gender == "male":
        choices = ["hair-short-crop", "hair-side-part", "hair-fade", "hair-curly"]
    else:
        choices = ["hair-side-part", "hair-bob", "hair-curly", "hair-braids"]
    if age >= 55 and gender != "female":
        choices = ["hair-short-crop", "hair-fade", "hair-side-part"]
    return _pick(choices, variant)


def _eyes_for(personality: str, variant: int) -> str:
    choices = {
        "warm": ["eyes-round", "eyes-happy", "eyes-round"],
        "serious": ["eyes-narrow", "eyes-round", "eyes-narrow"],
        "energetic": ["eyes-wide", "eyes-round", "eyes-happy"],
        "calm": ["eyes-round", "eyes-narrow", "eyes-happy"],
        "worried": ["eyes-worried", "eyes-round", "eyes-worried"],
        "thoughtful": ["eyes-thinking", "eyes-narrow", "eyes-round"],
    }[personality]
    return _pick(choices, variant)


def _body_for(age: int, gender: str, personality: str, variant: int) -> str:
    if age < 22:
        choices = ["body-petite", "body-slim", "body-petite"]
    elif age < 35:
        choices = ["body-slim", "body-average", "body-tall"]
    elif age < 50:
        choices = ["body-average", "body-sturdy", "body-slim"]
    else:
        choices = ["body-sturdy", "body-average", "body-sturdy"]
    if personality == "energetic":
        choices = ["body-slim", choices[0], "body-average"]
    if gender == "female" and age < 45:
        choices = ["body-petite" if age < 25 else "body-slim", choices[0], "body-average"]
    return _pick(choices, variant)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def build_design(
    brief: dict[str, Any],
    style: dict[str, Any],
    parts: dict[str, Any],
    variant: int,
    detail_level: str = DEFAULT_DETAIL_LEVEL,
) -> dict[str, Any]:
    colors = style_colors(style, parts)
    skins = skin_palette(style, parts, colors["outline"])
    skin = _pick(skins, variant)
    role = brief["role"]
    personality = brief["personality"]
    outfit_choices = ROLE_OUTFITS[role]
    accessory_choices = ROLE_ACCESSORIES[role]

    head = _head_for(brief["age"], variant)
    hair = _hair_for(brief["gender"], brief["age"], variant)
    eyes = _eyes_for(personality, variant)
    brows = _pick(PERSONALITY_BROWS[personality], variant)
    mouth = _pick(PERSONALITY_MOUTHS[personality], variant)
    body_type = _body_for(brief["age"], brief["gender"], personality, variant)
    outfit = _pick(outfit_choices, variant)
    accessory = _pick(accessory_choices, variant)
    outfit_color = [colors["outfit"], colors["accent"], colors["light"]][(variant - 1) % 3]
    if contrast_ratio(outfit_color, colors["outline"]) < 2.0:
        outfit_color = colors["outfit"]

    head_height = HEAD_HEIGHTS[head]
    total_height = BODY_HEIGHTS[body_type]
    ratio = round(head_height / total_height, 3)
    palette = _unique([colors["outline"], colors["light"], colors["accent"], outfit_color, skin])
    design = {
        "id": f"{brief['character_id']}-candidate-{variant:02d}",
        "name": brief["name"] if variant == 1 else f"{brief['name']} ({variant})",
        "style_source": "config/style-bible.json",
        "brief": {
            "role": role,
            "role_label": brief["role_label"],
            "age": brief["age"],
            "gender": brief["gender"],
            "personality": personality,
            "niche": brief["niche"],
            "language": brief["language"],
        },
        "parts": {
            "head": head,
            "hair": hair,
            "eyes": eyes,
            "brows": brows,
            "mouth": mouth,
            "body": body_type,
            "outfit": outfit,
            "accessory": accessory,
            "skin": skin,
            "hair_color": colors["outline"],
            "eye_color": colors["outline"],
            "outfit_color": outfit_color,
            "accent": colors["accent"],
            "outline": colors["outline"],
            "light": colors["light"],
        },
        "proportions": {
            "head_height": head_height,
            "total_height": total_height,
            "head_to_body": ratio,
            "shoulder_width": SHOULDER_WIDTHS[body_type],
        },
        "appearance": {
            "body": body_type,
            "hair": hair,
            "clothing": outfit,
            "palette": palette,
        },
        "voice": {
            "gender": "female" if brief["gender"] == "female" else "male",
            "tone": {
                "warm": "warm and conversational",
                "serious": "calm and factual",
                "energetic": "upbeat and fast",
                "calm": "calm and reassuring",
                "worried": "concerned and gentle",
                "thoughtful": "measured and clear",
            }[personality],
        },
        "expressions": list(EXPRESSIONS),
        "poses": list(POSES),
        "mouth_shapes": ["closed", "open", "wide", "smile"],
        "detail_level": detail_level if detail_level in DETAIL_LEVELS else DEFAULT_DETAIL_LEVEL,
        "locked": False,
    }
    design["fit_score"] = _fit_score(design)
    return design


def _fit_score(design: dict[str, Any]) -> int:
    brief = design["brief"]
    score = 50
    if design["parts"]["outfit"] == ROLE_OUTFITS[brief["role"]][0]:
        score += 15
    if design["parts"]["accessory"] == ROLE_ACCESSORIES[brief["role"]][0]:
        score += 10
    if design["parts"]["mouth"] == PERSONALITY_MOUTHS[brief["personality"]][0]:
        score += 10
    if design["parts"]["brows"] == PERSONALITY_BROWS[brief["personality"]][0]:
        score += 5
    if contrast_ratio(design["parts"]["skin"], design["parts"]["outline"]) >= 4.0:
        score += 5
    if MIN_RATIO <= design["proportions"]["head_to_body"] <= MAX_RATIO:
        score += 5
    return score


def signature(design: dict[str, Any]) -> str:
    keys = ("head", "hair", "eyes", "brows", "mouth", "body", "outfit", "accessory", "skin")
    return "|".join(str(design["parts"][key]) for key in keys)


def build_designs(
    brief: dict[str, Any],
    style: dict[str, Any],
    parts: dict[str, Any],
    detail_level: str = DEFAULT_DETAIL_LEVEL,
) -> list[dict[str, Any]]:
    designs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for variant in (1, 2, 3):
        design = build_design(brief, style, parts, variant, detail_level)
        attempts = 0
        while signature(design) in seen and attempts < 8:
            variant = variant + 3
            design = build_design(brief, style, parts, variant, detail_level)
            attempts += 1
        seen.add(signature(design))
        designs.append(design)
    if len({signature(design) for design in designs}) != 3:
        raise lib.SkillError("could not build 3 distinct character candidates from the brief")
    return designs


def choose_design(designs: Iterable[dict[str, Any]]) -> dict[str, Any]:
    return sorted(designs, key=lambda item: (-int(item.get("fit_score", 0)), item["id"]))[0]


def resolve(markup: str, design: dict[str, Any], detail_level: str = "basic") -> str:
    parts = design["parts"]
    level = detail_level_of(design, detail_level)
    skin = str(parts["skin"])
    outline = str(parts["outline"])
    hair = str(parts["hair_color"])
    outfit = str(parts["outfit_color"])
    accent = str(parts["accent"])
    light = str(parts["light"])
    eye = str(parts.get("eye_color") or outline)
    extras = {
        "{iris}": eye,
        "{skin_shadow}": mix_color(skin, outline, 0.22),
        "{blush}": mix_color(skin, accent, 0.35),
        "{hair_highlight}": mix_color(hair, light, 0.30),
        "{cloth_shadow}": mix_color(outfit, outline, 0.22),
    }
    if level == "basic":
        replacements = {
            "{skin}": skin,
            "{outline}": outline,
            "{hair}": hair,
            "{outfit}": outfit,
            "{accent}": accent,
            "{light}": light,
            "{eye}": eye,
            **extras,
        }
    else:
        ids = gradient_ids(design)
        replacements = {
            "{skin}": f"url(#{ids['skin']})",
            "{outline}": outline,
            "{hair}": f"url(#{ids['hair']})",
            "{outfit}": f"url(#{ids['outfit']})",
            "{accent}": accent,
            "{light}": light,
            "{eye}": eye,
            "{iris}": f"url(#{ids['iris']})",
            "{skin_shadow}": extras["{skin_shadow}"],
            "{blush}": extras["{blush}"],
            "{hair_highlight}": extras["{hair_highlight}"],
            "{cloth_shadow}": extras["{cloth_shadow}"],
        }
    for key, value in replacements.items():
        markup = markup.replace(key, value)
    return markup


def part_markup(parts: dict[str, Any], category: str, part_id: str) -> str:
    try:
        return str(parts[category][part_id])
    except KeyError as exc:
        raise lib.SkillError(f"Unknown {category} part: {part_id}") from exc


def wrist_positions(design: dict[str, Any], pose: str) -> tuple[tuple[int, int], tuple[int, int]]:
    width = int(design["proportions"]["shoulder_width"])
    left = 540 - width // 2
    right = 540 + width // 2
    left_pos = (left - 20, 1200)
    if pose == "wave":
        right_pos = (right + 92, 668)
    elif pose == "point":
        right_pos = (right + 260, 810)
    elif pose == "think":
        right_pos = (right + 62, 720)
    else:
        right_pos = (right + 20, 1200)
    return left_pos, right_pos


def arms_markup(design: dict[str, Any], pose: str, *, with_hands: bool = True) -> str:
    parts = design["parts"]
    skin = parts["skin"]
    outline = parts["outline"]
    width = int(design["proportions"]["shoulder_width"])
    left = 540 - width // 2
    right = 540 + width // 2
    common = f'fill="none" stroke="{skin}" stroke-width="{ARM_WIDTH}" stroke-linecap="round"'
    edge = f'fill="none" stroke="{outline}" stroke-width="{OUTLINE_WIDTH}" stroke-linecap="round"'
    left_path = f'<path d="M{left} 870 Q{left - 50} 1040 {left - 20} 1190" {common}/><path d="M{left} 870 Q{left - 50} 1040 {left - 20} 1190" {edge}/>'
    idle_right_path = f'<path d="M{right} 870 Q{right + 50} 1040 {right + 20} 1190" {common}/><path d="M{right} 870 Q{right + 50} 1040 {right + 20} 1190" {edge}/>'
    if with_hands:
        left_hand = f'<circle cx="{left - 20}" cy="1200" r="25" fill="{skin}" stroke="{outline}" stroke-width="{DETAIL_WIDTH}"/>'
        idle_right_hand = f'<circle cx="{right + 20}" cy="1200" r="25" fill="{skin}" stroke="{outline}" stroke-width="{DETAIL_WIDTH}"/>'
    else:
        left_hand = ""
        idle_right_hand = ""
    if pose == "wave":
        arm = f'<path d="M{right} 870 Q{right + 120} 800 {right + 90} 680" {common}/><path d="M{right} 870 Q{right + 120} 800 {right + 90} 680" {edge}/>'
        hand = f'<circle cx="{right + 92}" cy="668" r="29" fill="{skin}" stroke="{outline}" stroke-width="{DETAIL_WIDTH}"/>' if with_hands else ""
        return left_path + left_hand + arm + hand
    if pose == "point":
        arm = f'<path d="M{right} 870 Q{right + 150} 880 {right + 250} 820" {common}/><path d="M{right} 870 Q{right + 150} 880 {right + 250} 820" {edge}/>'
        hand = f'<circle cx="{right + 260}" cy="810" r="28" fill="{skin}" stroke="{outline}" stroke-width="{DETAIL_WIDTH}"/>' if with_hands else ""
        return left_path + left_hand + arm + hand
    if pose == "think":
        arm = f'<path d="M{right} 870 Q{right + 95} 800 {right + 65} 730" {common}/><path d="M{right} 870 Q{right + 95} 800 {right + 65} 730" {edge}/>'
        hand = f'<circle cx="{right + 62}" cy="720" r="27" fill="{skin}" stroke="{outline}" stroke-width="{DETAIL_WIDTH}"/>' if with_hands else ""
        return left_path + left_hand + arm + hand
    return left_path + left_hand + idle_right_path + idle_right_hand


def hands_markup(design: dict[str, Any], pose: str) -> str:
    hands = load_parts()["detail"]["hands"]
    left_pos, right_pos = wrist_positions(design, pose)
    left = f'<g transform="translate({left_pos[0]},{left_pos[1]})">{hands["open"]}</g>'
    if pose == "point":
        template, rotation = hands["point"], -90
    elif pose == "think":
        template, rotation = hands["hold"], 0
    elif pose == "wave":
        template, rotation = hands["open"], -15
    else:
        template, rotation = hands["open"], 0
    right = (
        f'<g transform="translate({right_pos[0]},{right_pos[1]}) rotate({rotation}) scale(-1,1)">'
        f"{template}</g>"
    )
    return left + right


def cuffs_markup(design: dict[str, Any], pose: str) -> str:
    cuff = load_parts()["detail"]["outfit"]["cuff"]
    left_pos, right_pos = wrist_positions(design, pose)
    rotation = {"wave": -15, "point": -90}.get(pose, 0)
    return (
        f'<g transform="translate({left_pos[0]},{left_pos[1] - 4})">{cuff}</g>'
        f'<g transform="translate({right_pos[0]},{right_pos[1] - 4}) rotate({rotation})">{cuff}</g>'
    )


def layers(
    design: dict[str, Any],
    expression: str,
    pose: str,
    *,
    prefix: str = "",
    detail_level: str | None = None,
) -> list[tuple[str, str]]:
    parts = load_parts()
    detail = parts.get("detail", {})
    level = detail_level_of(design, detail_level)
    detailed = level in {"standard", "rich"}
    full = level == "rich"
    parts_data = design["parts"]
    expression = {
        "smile": "happy", "smiling": "happy", "shock": "surprised",
        "surprised": "surprised", "think": "thinking", "thinking": "thinking",
        "worried": "worried", "concerned": "worried",
    }.get(expression, expression if expression in EXPRESSIONS else "neutral")
    pose = pose if pose in POSES or pose == "think" else "idle"
    expression_map = parts.get("expressions", {}).get(expression, {})

    def group(name: str) -> dict[str, Any]:
        value = detail.get(name, {})
        return value if isinstance(value, dict) else {}

    def detail_part(category: str, key: str) -> str:
        return str(group(category).get(key, ""))

    def detail_map(category: str, key: str, name: str) -> str:
        value = group(category).get(key, {})
        if isinstance(value, dict):
            return str(value.get(name, ""))
        return str(value or "")

    raw: list[tuple[str, str]] = []
    if full:
        raw.append(("ground_shadow", detail_map("body", "ground_shadow", parts_data["body"])))
    raw.append(("body", part_markup(parts, "bodies", parts_data["body"])))
    if full:
        raw.append(("shoes", detail_map("body", "shoes", parts_data["body"])))
    raw.append(("outfit", part_markup(parts, "outfits", parts_data["outfit"])))
    if full:
        raw.extend([
            ("folds", detail_part("outfit", "folds")),
            ("belt", detail_part("outfit", "belt")),
            ("collar", detail_part("outfit", "collar")),
            ("placket", detail_part("outfit", "placket")),
        ])
    raw.append(("arms", arms_markup(design, pose, with_hands=not full)))
    if full:
        raw.append(("cuffs", cuffs_markup(design, pose)))
        raw.append(("hands", hands_markup(design, pose)))
    raw.append(("neck", detail_part("face", "neck") if detailed else BASE_NECK))
    raw.append(("head", part_markup(parts, "heads", parts_data["head"])))
    if detailed:
        raw.extend([
            ("ears", detail_part("face", "ears")),
            ("jaw_shadow", detail_part("face", "jaw_shadow")),
            ("hairline_shadow", detail_part("hair", "hairline_shadow")),
        ])
    raw.append(("hair", part_markup(parts, "hairs", parts_data["hair"])))
    if detailed:
        raw.extend([
            ("hair_strands", detail_part("hair", "strands")),
            ("hair_highlight", detail_part("hair", "highlight")),
        ])
    if detailed:
        raw.append(("brows", detail_map("face", "brows", expression)))
        raw.append(("brow_detail", detail_part("face", "brow_detail")))
    else:
        brows = expression_map.get("brows") or parts_data["brows"]
        raw.append(("brows", part_markup(parts, "brows", brows)))
    if detailed:
        raw.extend([
            ("eyes", detail_part("face", "eyes_base")),
            ("iris", detail_part("face", "iris")),
            ("pupils", detail_part("face", "pupils")),
            ("eye_highlights", detail_part("face", "eye_highlights")),
            ("eyelids", detail_map("face", "eyelids", expression)),
            ("lashes", detail_map("face", "lashes", expression)),
        ])
    else:
        eyes = expression_map.get("eyes") or parts_data["eyes"]
        raw.append(("eyes", part_markup(parts, "eyes", eyes)))
    if detailed:
        raw.append(("nose", detail_part("face", "nose")))
        raw.append(("blush", detail_map("face", "blush", expression)))
        raw.append(("mouth", detail_map("face", "mouths", expression)))
    else:
        mouth = expression_map.get("mouth") or parts_data["mouth"]
        raw.append(("mouth", part_markup(parts, "mouths", mouth)))
    raw.append(("accessory", part_markup(parts, "accessories", parts_data["accessory"])))
    return [
        (
            f"{prefix}{layer_id}",
            resolve(normalize_strokes(markup) if detailed else markup, design, level),
        )
        for layer_id, markup in raw
    ]


def character_markup(
    design: dict[str, Any],
    expression: str,
    pose: str,
    *,
    detail_level: str | None = None,
) -> str:
    level = detail_level_of(design, detail_level)
    defs = ""
    if level in {"standard", "rich"}:
        defs = "  " + gradient_defs(design) + "\n"
    body = "\n".join(
        f'  <g id="{layer_id}">{markup}</g>'
        for layer_id, markup in layers(design, expression, pose, detail_level=level)
    )
    return f'  <g id="character">\n{defs}{body}\n  </g>'


def layered_svg(
    design: dict[str, Any],
    expression: str = "neutral",
    pose: str = "idle",
    *,
    detail_level: str | None = None,
) -> str:
    import svg_scene_builder

    return svg_scene_builder.wrap_svg(
        character_markup(design, expression, pose, detail_level=detail_level)
    )


def preview_svg(
    design: dict[str, Any],
    expression: str = "neutral",
    pose: str = "idle",
    *,
    detail_level: str | None = None,
) -> str:
    import svg_scene_builder

    light = design["parts"]["light"]
    return svg_scene_builder.wrap_svg(
        f'  <g id="preview-background"><rect width="1080" height="1920" fill="{light}"/></g>\n'
        + character_markup(design, expression, pose, detail_level=detail_level)
    )


def preview_sheet_svg(design: dict[str, Any], *, detail_level: str | None = None) -> str:
    import svg_scene_builder

    level = detail_level_of(design, detail_level)
    light = design["parts"]["light"]
    outline = design["parts"]["outline"]
    tiles: list[str] = [f'  <g id="sheet-background"><rect width="1080" height="1920" fill="{light}"/></g>']
    if level in {"standard", "rich"}:
        tiles.append("  " + gradient_defs(design))
    index = 0
    for expression in EXPRESSIONS:
        for pose in POSES:
            index += 1
            row, column = divmod(index - 1, 3)
            x, y = column * 360, row * 384
            tiles.append(f'  <g id="tile-{index:02d}">')
            tiles.append(f'    <rect x="{x}" y="{y}" width="360" height="384" fill="{light}" stroke="{outline}" stroke-width="4"/>')
            tiles.append(f'    <g transform="translate({x + 77},{y + 2}) scale(0.19)">')
            for layer_id, markup in layers(
                design, expression, pose, prefix=f"t{index:02d}-", detail_level=level
            ):
                tiles.append(f'      <g id="{layer_id}">{markup}</g>')
            tiles.append("    </g>")
            tiles.append(
                f'    <text x="{x + 10}" y="{y + 374}" font-family="sans-serif" font-size="14" '
                f'fill="{outline}">{expression}/{pose}</text>'
            )
            tiles.append("  </g>")
    return svg_scene_builder.wrap_svg("\n".join(tiles))


def compare_svg(design: dict[str, Any]) -> str:
    """Basic vs rich, five expressions, in one deterministic 1080x1920 sheet."""
    import svg_scene_builder

    light = design["parts"]["light"]
    outline = design["parts"]["outline"]
    tiles: list[str] = [f'  <g id="compare-background"><rect width="1080" height="1920" fill="{light}"/></g>']
    tiles.append("  " + gradient_defs(design))
    for row, expression in enumerate(EXPRESSIONS):
        for column, level in enumerate(("basic", "rich")):
            x, y = column * 540, row * 384
            tiles.append(f'  <g id="compare-{level}-{expression}">')
            tiles.append(
                f'    <rect x="{x}" y="{y}" width="540" height="384" fill="{light}" '
                f'stroke="{outline}" stroke-width="4"/>'
            )
            tiles.append(f'    <g transform="translate({x + 167},{y + 2}) scale(0.19)">')
            for layer_id, markup in layers(
                design, expression, "idle", prefix=f"{level[0]}{row:02d}-", detail_level=level
            ):
                tiles.append(f'      <g id="{layer_id}">{markup}</g>')
            tiles.append("    </g>")
            tiles.append(
                f'    <rect x="{x}" y="{y + 350}" width="540" height="34" fill="{outline}" opacity="0.78"/>'
            )
            tiles.append(
                f'    <text x="{x + 12}" y="{y + 374}" font-family="sans-serif" font-size="20" '
                f'fill="{light}">{level} / {expression}</text>'
            )
            tiles.append("  </g>")
    return svg_scene_builder.wrap_svg("\n".join(tiles))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_design(
    design: dict[str, Any],
    directory: Path,
    *,
    include_sheet: bool = False,
    include_compare: bool = False,
    render: bool = True,
) -> dict[str, Path]:
    import svg_scene_builder

    directory.mkdir(parents=True, exist_ok=True)
    character_path = lib.write_json(directory / "character.json", design)
    layered = directory / "layered.svg"
    preview = directory / "preview.png"
    svg_scene_builder.write_svg(layered, layered_svg(design))
    paths = {"character": character_path, "layered": layered}
    if render:
        svg_scene_builder.svg_to_png(layered, directory / "layered.png")
        svg_scene_builder.write_svg(directory / "preview.svg", preview_svg(design))
        svg_scene_builder.svg_to_png(directory / "preview.svg", preview)
        paths["preview"] = preview
    if include_sheet:
        sheet_svg = directory / "preview-sheet.svg"
        svg_scene_builder.write_svg(sheet_svg, preview_sheet_svg(design))
        sheet_png = directory / "preview-sheet.png"
        if render:
            svg_scene_builder.svg_to_png(sheet_svg, sheet_png)
            paths["sheet"] = sheet_png
    if include_compare:
        compare_source = directory / "compare.svg"
        svg_scene_builder.write_svg(compare_source, compare_svg(design))
        compare_png = directory / "compare.png"
        if render:
            svg_scene_builder.svg_to_png(compare_source, compare_png)
            paths["compare"] = compare_png
    return paths


def _render_twice(design: dict[str, Any], target: Path) -> tuple[Path, Path]:
    import svg_scene_builder

    target.mkdir(parents=True, exist_ok=True)
    first = target / "render-01.svg"
    second = target / "render-02.svg"
    svg_scene_builder.write_svg(first, preview_svg(design))
    svg_scene_builder.write_svg(second, preview_svg(design))
    if first.read_bytes() != second.read_bytes():
        raise lib.SkillError("character SVG is not deterministic between two renders")
    first_png = svg_scene_builder.svg_to_png(first, target / "render-01.png")
    second_png = svg_scene_builder.svg_to_png(second, target / "render-02.png")
    if _sha256(first_png) != _sha256(second_png):
        raise lib.SkillError("character PNG is not byte-identical between two renders")
    return first_png, second_png


def check_character(path: Path, *, require_png: bool = True) -> dict[str, Any]:
    import svg_scene_builder
    from xml.etree import ElementTree

    lib.validate_schema("character", path)
    design = lib.read_json(path)
    parts = load_parts()
    expected_counts = {
        "heads": 6, "hairs": 8, "eyes": 6, "brows": 4,
        "mouths": 8, "bodies": 5, "outfits": 8, "accessories": 8,
    }
    for category, minimum in expected_counts.items():
        if len(parts.get(category, {})) < minimum:
            raise lib.SkillError(f"part library {category} has fewer than {minimum} entries")

    for category, key in (
        ("heads", "head"), ("hairs", "hair"), ("eyes", "eyes"), ("brows", "brows"),
        ("mouths", "mouth"), ("bodies", "body"), ("outfits", "outfit"),
        ("accessories", "accessory"),
    ):
        if design["parts"][key] not in parts[category]:
            raise lib.SkillError(f"unknown {category} part: {design['parts'][key]}")

    palette = _unique([str(color) for color in design["appearance"]["palette"]])
    if len(palette) < MIN_PALETTE_COLORS:
        raise lib.SkillError(f"palette has fewer than {MIN_PALETTE_COLORS} distinct colours")
    contrast = contrast_ratio(design["parts"]["skin"], design["parts"]["outline"])
    if contrast < MIN_CONTRAST:
        raise lib.SkillError(f"skin/outline contrast {contrast:.2f} is below {MIN_CONTRAST}")

    ratio = float(design["proportions"]["head_to_body"])
    if not MIN_RATIO <= ratio <= MAX_RATIO:
        raise lib.SkillError(f"head-to-body ratio {ratio} outside {MIN_RATIO}-{MAX_RATIO}")

    level = detail_level_of(design)
    required = required_layer_ids(level)
    svg_text = layered_svg(design)
    tree = ElementTree.fromstring(svg_text)
    ids = {element.get("id") for element in tree.iter() if element.get("id")}
    missing = [layer_id for layer_id in required if layer_id not in ids]
    if missing:
        raise lib.SkillError("missing layer id(s): " + ", ".join(missing))

    if len(svg_text.encode("utf-8")) > MAX_SVG_BYTES:
        raise lib.SkillError(
            f"layered SVG is {len(svg_text.encode('utf-8'))} bytes, over the {MAX_SVG_BYTES} byte limit"
        )

    if level in {"standard", "rich"}:
        expected_gradients = set(gradient_ids(design).values())
        found_gradients = {
            str(element.get("id")) for element in tree.iter()
            if element.tag.lower().endswith("lineargradient")
        }
        missing_gradients = sorted(expected_gradients - found_gradients)
        if missing_gradients:
            raise lib.SkillError("missing gradient def(s): " + ", ".join(missing_gradients))
        widths = {
            float(element.get("stroke-width"))
            for element in tree.iter() if element.get("stroke-width")
        }
        unexpected = sorted(widths - ALLOWED_STROKE_WIDTHS)
        if unexpected:
            raise lib.SkillError(
                "unexpected stroke width(s): "
                + ", ".join(f"{value:g}" for value in unexpected)
                + f"; expected only {sorted(ALLOWED_STROKE_WIDTHS)}"
            )

    if require_png:
        directory = path.parent
        for name in ("preview.png", "preview-sheet.png", "compare.png"):
            image = directory / name
            if image.is_file():
                size = svg_scene_builder.png_size(image)
                if size != (svg_scene_builder.WIDTH, svg_scene_builder.HEIGHT):
                    raise lib.SkillError(f"{lib.relative(image)} is {size}, expected 1080x1920")
    return {
        "id": design["id"],
        "detail_level": level,
        "layers": len(required),
        "svg_bytes": len(svg_text.encode("utf-8")),
        "palette_colors": len(palette),
        "contrast": round(contrast, 2),
        "head_to_body": ratio,
    }


def write_legacy_views(design: dict[str, Any]) -> list[Path]:
    """Regenerate the three legacy expression views from the locked design."""
    import svg_scene_builder

    outputs: list[Path] = []
    for expression in ("neutral", "smile", "surprised"):
        svg_path = CHARACTERS_DIR / f"{design['id']}-{expression}.svg"
        svg_scene_builder.write_svg(svg_path, layered_svg(design, expression, "idle"))
        png_path = svg_scene_builder.svg_to_png(svg_path, svg_path.with_suffix(".png"))
        outputs.append(png_path)
    return outputs


def run(
    brief_path: Path | None = None,
    out_root: Path | None = None,
    report_path: Path | None = None,
    *,
    render: bool = True,
    detail_level: str = DEFAULT_DETAIL_LEVEL,
) -> dict[str, Any]:
    brief = load_brief(brief_path)
    style = lib.load_style_bible()
    parts = load_parts()
    designs = build_designs(brief, style, parts, detail_level)
    out_root = out_root or CHARACTERS_DIR
    report_path = report_path or lib.stage(4, "character-design-set.json")

    candidates: list[dict[str, Any]] = []
    for design in designs:
        directory = out_root / design["id"]
        paths = write_design(design, directory, render=render)
        candidates.append({
            "id": design["id"],
            "approach": ROLE_NAMES[brief["role"]],
            "signature": signature(design),
            "fit_score": design["fit_score"],
            "skin_tone": design["parts"]["skin"],
            "head_to_body": design["proportions"]["head_to_body"],
            "character": lib.relative(paths["character"]),
            "layered_svg": lib.relative(paths["layered"]),
            "preview_png": lib.relative(paths.get("preview", directory / "preview.png")),
        })

    winner = choose_design(designs)
    locked = json.loads(json.dumps(winner))
    locked["id"] = brief["character_id"]
    locked["name"] = brief["name"]
    locked["locked"] = True
    locked_dir = out_root / locked["id"]
    locked_paths = write_design(
        locked, locked_dir, include_sheet=True, include_compare=True, render=render
    )
    checked = check_character(locked_paths["character"], require_png=render)
    if render:
        write_legacy_views(locked)

    report = {
        "project": lib.project_name(),
        "brief": brief,
        "style_source": "config/style-bible.json",
        "candidates": candidates,
        "chosen": {
            "id": locked["id"],
            "from_candidate": winner["id"],
            "signature": signature(locked),
            "fit_score": winner["fit_score"],
            "character": lib.relative(locked_paths["character"]),
            "layered_svg": lib.relative(locked_paths["layered"]),
            "preview_png": lib.relative(locked_paths.get("preview", locked_dir / "preview.png")),
            "preview_sheet_png": lib.relative(locked_paths.get("sheet", locked_dir / "preview-sheet.png")),
            "compare_png": lib.relative(locked_paths.get("compare", locked_dir / "compare.png")),
            "detail_level": checked["detail_level"],
        },
        "locked": True,
        "criteria": {
            "detail_level": checked["detail_level"],
            "head_to_body": checked["head_to_body"],
            "min_contrast": MIN_CONTRAST,
            "contrast": checked["contrast"],
            "min_palette_colors": MIN_PALETTE_COLORS,
            "palette_colors": checked["palette_colors"],
            "layers": required_layer_ids(checked["detail_level"]),
            "svg_bytes": checked["svg_bytes"],
            "max_svg_bytes": MAX_SVG_BYTES,
            "stroke_widths": sorted(ALLOWED_STROKE_WIDTHS),
        },
    }
    lib.write_json(report_path, report)
    lib.ok(
        "character-designer",
        f"3 candidates, locked {locked['id']} at {checked['detail_level']} detail with "
        f"{checked['layers']} layers (ratio {checked['head_to_body']}, contrast {checked['contrast']})",
        locked_paths["character"],
    )
    print(f"OUTPUT {lib.relative(report_path)}")
    return report


def _sample_design(parts: dict[str, Any], style: dict[str, Any], target: Path, *, sheet: bool = False) -> dict[str, Any]:
    brief = {
        "project": "character-self-test",
        "role": "teacher",
        "role_label": ROLE_NAMES["teacher"],
        "age": 29,
        "gender": "male",
        "personality": "warm",
        "niche": lib.load_channel()["niche"],
        "language": lib.load_channel()["language"],
        "name": "রাফি",
        "character_id": "creator-01",
    }
    design = build_design(brief, style, parts, 1)
    design["locked"] = True
    directory = target / design["id"]
    write_design(design, directory, include_sheet=sheet)
    return design


def self_test() -> int:
    import svg_scene_builder

    if svg_scene_builder.edge_executable() is None:
        print("BLOCKED character-designer: no installed SVG-to-PNG converter; ask before installing")
        return 0

    target = ROOT / ".tmp" / "self-test" / "character-designer"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)

    brief = {
        "project": "character-self-test",
        "role": "teacher",
        "age": 34,
        "gender": "female",
        "personality": "warm",
        "niche": lib.load_channel()["niche"],
        "language": lib.load_channel()["language"],
        "name": "নুসরাত",
        "character_id": "creator-01",
    }
    brief_path = lib.write_json(target / "character-brief.json", brief)
    style = lib.load_style_bible()
    parts = load_parts()
    for category, minimum in {
        "heads": 6, "hairs": 8, "eyes": 6, "brows": 4,
        "mouths": 8, "bodies": 5, "outfits": 8, "accessories": 8,
    }.items():
        assert len(parts[category]) >= minimum, (category, len(parts[category]))

    designs = build_designs(load_brief(brief_path), style, parts)
    assert len(designs) == 3
    assert len({signature(design) for design in designs}) == 3
    assert all(design["detail_level"] == "rich" for design in designs)

    for design in designs:
        paths = write_design(design, target / design["id"], render=True)
        checked = check_character(paths["character"])
        assert checked["detail_level"] == "rich", checked
        assert checked["layers"] == len(required_layer_ids("rich")), checked
        assert checked["svg_bytes"] <= MAX_SVG_BYTES, checked
        assert checked["palette_colors"] >= MIN_PALETTE_COLORS, checked
        assert checked["contrast"] >= MIN_CONTRAST, checked
        assert MIN_RATIO <= checked["head_to_body"] <= MAX_RATIO, checked

    winner = choose_design(designs)
    print(
        f"PASS character-designer: 3 distinct candidates, "
        f"{len(required_layer_ids('rich'))} layers each, schema valid"
    )

    rich_svg = layered_svg(winner)
    assert all(f'id="{identifier}"' in rich_svg for identifier in gradient_ids(winner).values())
    assert rich_svg.count("<linearGradient") >= 4
    print("PASS character-designer: 4 linear gradients and the 10/4/44 stroke scale are present")

    first, second = _render_twice(winner, target / "determinism")
    size = svg_scene_builder.png_size(first)
    assert size == (svg_scene_builder.WIDTH, svg_scene_builder.HEIGHT), size
    assert _sha256(first) == _sha256(second)
    print("PASS character-designer: two renders are byte-identical at 1080x1920")

    start = time.perf_counter()
    timing_svg = target / "timing.svg"
    svg_scene_builder.write_svg(timing_svg, preview_svg(winner))
    svg_scene_builder.svg_to_png(timing_svg, target / "timing.png")
    elapsed = time.perf_counter() - start
    assert elapsed < MAX_RENDER_SECONDS, elapsed
    print(f"PASS character-designer: rich PNG render took {elapsed:.2f}s (limit {MAX_RENDER_SECONDS:.0f}s)")

    layer_sets = {expression: dict(layers(winner, expression, "idle")) for expression in EXPRESSIONS}
    for layer_id in ("brows", "eyelids", "mouth", "blush"):
        values = {layer_sets[expression][layer_id] for expression in EXPRESSIONS}
        assert len(values) == len(EXPRESSIONS), (layer_id, len(values))
    print("PASS character-designer: 5 expressions change brows, eyelids, mouth and cheeks together")

    basic = json.loads(json.dumps(winner))
    basic["detail_level"] = "basic"
    basic_paths = write_design(basic, target / "basic" / basic["id"], render=False)
    basic_checked = check_character(basic_paths["character"], require_png=False)
    assert basic_checked["detail_level"] == "basic", basic_checked
    assert basic_checked["layers"] == len(BASE_LAYER_IDS), basic_checked
    assert "<linearGradient" not in layered_svg(basic)
    assert "iris" not in {layer_id for layer_id, _ in layers(basic, "neutral", "idle")}
    print("PASS character-designer: basic detail level still renders with 10 base layers")

    sheet = target / "creatorsheet"
    sheet.mkdir(parents=True, exist_ok=True)
    sheet_svg = sheet / "preview-sheet.svg"
    svg_scene_builder.write_svg(sheet_svg, preview_sheet_svg(winner))
    sheet_png = svg_scene_builder.svg_to_png(sheet_svg, sheet / "preview-sheet.png")
    assert svg_scene_builder.png_size(sheet_png) == (svg_scene_builder.WIDTH, svg_scene_builder.HEIGHT)
    assert len(EXPRESSIONS) == 5 and len(POSES) == 3
    print("PASS character-designer: 5 expressions x 3 poses preview sheet rendered")

    compare = target / "compare"
    compare.mkdir(parents=True, exist_ok=True)
    compare_source = compare / "compare.svg"
    svg_scene_builder.write_svg(compare_source, compare_svg(winner))
    compare_text = compare_source.read_text(encoding="utf-8")
    assert "compare-basic-neutral" in compare_text and "compare-rich-neutral" in compare_text
    compare_png = svg_scene_builder.svg_to_png(compare_source, compare / "compare.png")
    assert svg_scene_builder.png_size(compare_png) == (svg_scene_builder.WIDTH, svg_scene_builder.HEIGHT)
    print("PASS character-designer: basic vs rich compare sheet rendered")
    return 0


def qa_self_test() -> int:
    import svg_scene_builder

    if svg_scene_builder.edge_executable() is None:
        print("BLOCKED character-qa-tester: no installed SVG-to-PNG converter; ask before installing")
        return 0

    target = ROOT / ".tmp" / "self-test" / "character-qa-tester"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    design = _sample_design(load_parts(), lib.load_style_bible(), target, sheet=True)
    path = target / design["id"] / "character.json"
    checked = check_character(path)
    assert checked["layers"] == len(required_layer_ids(checked["detail_level"])), checked
    assert checked["palette_colors"] >= MIN_PALETTE_COLORS, checked
    print(
        f"PASS character-qa-tester: schema, {checked['layers']} {checked['detail_level']} layer ids, "
        f"palette ({checked['palette_colors']}) and 1080x1920 PNGs verified"
    )
    return 0


def consistency_self_test() -> int:
    import svg_scene_builder

    if svg_scene_builder.edge_executable() is None:
        print("BLOCKED consistency-guardian: no installed SVG-to-PNG converter; ask before installing")
        return 0

    target = ROOT / ".tmp" / "self-test" / "consistency-guardian"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    design = _sample_design(load_parts(), lib.load_style_bible(), target)
    path = target / design["id"] / "character.json"
    first, second = _render_twice(design, target / "repeat")
    assert _sha256(first) == _sha256(second)
    checked = check_character(path)
    assert checked["id"] == design["id"]
    print(
        "PASS consistency-guardian: identical part ids/colors/proportions and "
        "byte-identical renders across two scenes"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", help="character brief JSON")
    parser.add_argument("--out-root", help="assets/characters directory")
    parser.add_argument("--report", help="character-design-set.json path")
    parser.add_argument(
        "--detail-level",
        choices=DETAIL_LEVELS,
        default=DEFAULT_DETAIL_LEVEL,
        help="basic, standard or rich detail (default: rich)",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    run(
        Path(args.brief) if args.brief else None,
        Path(args.out_root) if args.out_root else None,
        Path(args.report) if args.report else None,
        detail_level=args.detail_level,
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except lib.SkillError as exc:
        print(f"FAIL character-designer: {exc}")
        sys.exit(1)
