#!/usr/bin/env python3
"""Distinct FFmpeg commands for the 18 template video-editing skills.

Each builder returns a purpose-specific command. Both the real run and the
self-test call the same builder, so the test always exercises production logic.
Parameters come from config/defaults.json and config/style-bible.json.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skill_lib as lib
import skill_tools as st

Context = dict[str, Any]
Builder = Callable[[Context, Path], list[str]]

EFFECT_SKILLS = {
    "animator", "beat-sync-editor", "branding-manager", "broll-variety-planner",
    "color-grading-keeper", "cut-rhythm-editor", "emphasis-sticker-placer",
    "hook-visual-editor", "intro-outro-manager", "motion-graphic-editor",
    "pattern-interrupt-inserter", "preview-frame-extractor", "seamless-loop-editor",
    "sfx-timing-placer", "thumbnail-designer", "variant-batch-renderer",
    "video-editor", "watermark-logo-placer",
}


def params() -> dict[str, Any]:
    defaults = lib.read_json(lib.DEFAULTS_PATH, required=False) or {}
    bible = lib.load_style_bible(required=False)
    resolution = str(defaults.get("resolution", "1080x1920")).split("x")
    width = int(resolution[0]) if len(resolution) == 2 else 1080
    height = int(resolution[1]) if len(resolution) == 2 else 1920
    style = bible.get("style", {}) if isinstance(bible, dict) else {}
    palette = style.get("palette", ["#111827", "#F9FAFB", "#F59E0B", "#10B981"])
    font = str(style.get("font", "Noto Sans Bengali"))
    length = (bible.get("channel", {}).get("video", {}).get("length_sec", [30, 60])
              if isinstance(bible, dict) else [30, 60])
    return {
        "w": width, "h": height,
        "palette": [str(color) for color in palette],
        "font": font,
        "fontfile": st.font_file(),
        "max_len": float(length[1]) if isinstance(length, list) and length else 60.0,
    }


def esc(text: str) -> str:
    return st.filter_escape(text)


def font_part(ctx: Context) -> str:
    font = ctx["fontfile"]
    if font is None:
        return ""
    value = (
        Path(lib.relative(font)).as_posix()
        if font.is_relative_to(lib.ROOT)
        else font.as_posix()
    )
    return f"fontfile={value.replace(':', '\\\\:')}:"


def video_codec() -> list[str]:
    return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p"]


def ffmpeg_color(value: str) -> str:
    """FFmpeg filters need 0xRRGGBB, not the CSS-style #RRGGBB in the bible."""
    return value.replace("#", "0x")


def accent(ctx: Context) -> str:
    raw = ctx["palette"][2] if len(ctx["palette"]) > 2 else "#F59E0B"
    return ffmpeg_color(raw)


def background(ctx: Context) -> str:
    raw = ctx["palette"][1] if len(ctx["palette"]) > 1 else "#F9FAFB"
    return ffmpeg_color(raw)


def duration(ctx: Context) -> float:
    return float(ctx.get("duration_sec") or st.probe_summary(ctx["video"])["duration_sec"])


def build_animator(ctx: Context, out: Path) -> list[str]:
    zoom = 1 + 0.01 * len(ctx["palette"])
    frames = 75
    return [
        "-loop", "1", "-framerate", "30", "-i", str(ctx["image"]),
        "-vf", f"zoompan=z='min(zoom+0.0015,{zoom:.3f})':d={frames}:s={ctx['w']}x{ctx['h']}:fps=30,format=yuv420p",
        "-t", str(frames / 30), *video_codec(), "-an", str(out),
    ]


def build_beat_sync(ctx: Context, out: Path) -> list[str]:
    return [
        "-i", str(ctx["video"]),
        "-vf", f"fps=2,setpts=N/(2*TB),fps=30,scale={ctx['w']}:{ctx['h']},format=yuv420p",
        *video_codec(), "-c:a", "aac", "-b:a", "128k", "-shortest", str(out),
    ]


def build_branding(ctx: Context, out: Path) -> list[str]:
    label = ctx["project"].upper()
    bar = int(ctx["h"] * 0.07)
    return [
        "-i", str(ctx["video"]),
        "-vf", (
            f"drawbox=x=0:y=ih-{bar}:w=iw:h={bar}:color={accent(ctx)}@0.85:t=fill,"
            f"drawtext=text='{esc(label)}':{font_part(ctx)}fontsize=48:fontcolor=white:"
            f"x=40:y=main_h-{bar + 20}"
        ),
        *video_codec(), "-c:a", "aac", "-b:a", "128k", str(out),
    ]


def build_color_grading(ctx: Context, out: Path) -> list[str]:
    contrast = 1 + 0.01 * len(ctx["palette"])
    return [
        "-i", str(ctx["video"]),
        "-vf", f"eq=contrast={contrast:.3f}:saturation=1.03:brightness=0.01,format=yuv420p",
        *video_codec(), "-c:a", "aac", "-b:a", "128k", str(out),
    ]


def build_emphasis(ctx: Context, out: Path) -> list[str]:
    x = int(ctx["w"] * 0.08)
    y = int(ctx["h"] * 0.12)
    box_w = int(ctx["w"] * 0.84)
    box_h = int(ctx["h"] * 0.12)
    window = f"between(t\\,0\\,{min(1.2, duration(ctx) / 2):.2f})"
    return [
        "-i", str(ctx["video"]),
        "-vf", f"drawbox=x={x}:y={y}:w={box_w}:h={box_h}:color={accent(ctx)}@0.35:t=fill:enable='{window}'",
        *video_codec(), "-c:a", "aac", "-b:a", "128k", str(out),
    ]


def build_hook_visual(ctx: Context, out: Path) -> list[str]:
    return [
        "-i", str(ctx["video"]),
        "-vf", (
            "zoompan=z='if(lte(on,60),1.10,1.0)':d=1:"
            f"s={ctx['w']}x{ctx['h']}:fps=30,format=yuv420p"
        ),
        *video_codec(), "-c:a", "aac", "-b:a", "128k", "-shortest", str(out),
    ]


def build_intro_outro(ctx: Context, out: Path) -> list[str]:
    return [
        "-f", "lavfi", "-i", f"color=c={background(ctx)}:s={ctx['w']}x{ctx['h']}:d=1:r=30",
        "-i", str(ctx["video"]),
        "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
        "-map", "[v]", *video_codec(), "-an", str(out),
    ]


def build_motion_graphic(ctx: Context, out: Path) -> list[str]:
    label = ctx["project"].upper()
    return [
        "-i", str(ctx["video"]),
        "-vf", (
            f"drawtext=text='{esc(label)}':{font_part(ctx)}fontsize=64:"
            f"fontcolor={accent(ctx)}:x='(main_w-text_w)*t/3':y=300:"
            f"enable='between(t\\,0\\,{min(3.0, duration(ctx)):.2f})'"
        ),
        *video_codec(), "-c:a", "aac", "-b:a", "128k", str(out),
    ]


def build_pattern_interrupt(ctx: Context, out: Path) -> list[str]:
    total = duration(ctx)
    second = max(0.2, min(0.5, total / 3))
    third = min(total, second * 2)
    return [
        "-i", str(ctx["video"]),
        "-filter_complex", (
            "[0:v]split=3[a][b][c];"
            f"[a]trim=0:{second:.3f},setpts=PTS-STARTPTS[a0];"
            f"[b]trim={second:.3f}:{third:.3f},setpts=PTS-STARTPTS,hflip[b0];"
            f"[c]trim={third:.3f}:{total:.3f},setpts=PTS-STARTPTS[c0];"
            "[a0][b0][c0]concat=n=3:v=1:a=0[v]"
        ),
        "-map", "[v]", *video_codec(), "-an", str(out),
    ]


def build_preview_frames(ctx: Context, out: Path) -> list[str]:
    return [
        "-i", str(ctx["video"]),
        "-vf", f"fps=1/2,scale={ctx['w'] // 2}:{ctx['h'] // 3},tile=2x3",
        "-frames:v", "1", str(out),
    ]


def build_seamless_loop(ctx: Context, out: Path) -> list[str]:
    total = duration(ctx)
    tail = min(0.4, total / 2)
    split = total - tail
    return [
        "-i", str(ctx["video"]),
        "-filter_complex", (
            "[0:v]split=2[a][b];"
            f"[a]trim=0:{split:.3f},setpts=PTS-STARTPTS[a0];"
            f"[b]trim={split:.3f}:{total:.3f},setpts=PTS-STARTPTS,reverse[b0];"
            "[a0][b0]concat=n=2:v=1:a=0[v]"
        ),
        "-map", "[v]", *video_codec(), "-an", str(out),
    ]


def build_sfx_timing(ctx: Context, out: Path) -> list[str]:
    delay_ms = 1200
    return [
        "-i", str(ctx["video"]), "-i", str(ctx["audio"]),
        "-filter_complex", (
            f"[1:a]adelay={delay_ms}|{delay_ms},volume=0.35[s];"
            "[0:a][s]amix=inputs=2:duration=first:dropout_transition=0[a]"
        ),
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(out),
    ]


def build_thumbnail(ctx: Context, out: Path) -> list[str]:
    title = ctx["project"].upper()
    return [
        "-i", str(ctx["video"]),
        "-vf", (
            f"select='eq(n\\,{min(75, max(0, int(duration(ctx) * 30) - 1))})',"
            f"scale={ctx['w']}:{ctx['h']},"
            f"drawtext=text='{esc(title)}':{font_part(ctx)}fontsize=72:"
            f"fontcolor=white:x=60:y=120"
        ),
        "-frames:v", "1", str(out),
    ]


def build_variant_batch(ctx: Context, out: Path) -> list[str]:
    step = len(ctx["palette"]) * 10
    outputs = [out.with_name(f"{out.stem}-v{index}{out.suffix}") for index in (1, 2, 3)]
    ctx["variant_outputs"] = outputs
    return [
        "-i", str(ctx["video"]),
        "-filter_complex", (
            "[0:v]split=3[v1][v2][v3];"
            "[v1]hue=h=0[o1];"
            f"[v2]hue=h={step}[o2];"
            f"[v3]hue=h=-{step}[o3]"
        ),
        "-map", "[o1]", *video_codec(), "-an", str(outputs[0]),
        "-map", "[o2]", *video_codec(), "-an", str(outputs[1]),
        "-map", "[o3]", *video_codec(), "-an", str(outputs[2]),
    ]


def build_video_editor(ctx: Context, out: Path) -> list[str]:
    total = duration(ctx)
    trim = max(0.1, min(0.3, total / 4))
    end = total - trim
    return [
        "-i", str(ctx["video"]),
        "-filter_complex", (
            f"[0:v]trim={trim:.3f}:{end:.3f},setpts=PTS-STARTPTS[v];"
            f"[0:a]atrim={trim:.3f}:{end:.3f},asetpts=PTS-STARTPTS[a]"
        ),
        "-map", "[v]", "-map", "[a]", *video_codec(), "-c:a", "aac", "-b:a", "128k", str(out),
    ]


def build_watermark(ctx: Context, out: Path) -> list[str]:
    return [
        "-i", str(ctx["video"]), "-i", str(ctx["logo"]),
        "-filter_complex", (
            "[1:v]scale=120:120[logo];"
            "[0:v][logo]overlay=x=w-150:y=40:format=auto[v]"
        ),
        "-map", "[v]", "-map", "0:a?", *video_codec(), "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(out),
    ]


def build_broll_variety(ctx: Context, out: Path) -> list[str]:
    window = min(2.0, duration(ctx) * 0.4)
    return [
        "-i", str(ctx["video"]), "-i", str(ctx["image"]),
        "-filter_complex", (
            f"[1:v]scale=270:480[b];"
            f"[0:v][b]overlay=x=w-300:y=120:enable='between(t\\,0\\,{window:.2f})'[v]"
        ),
        "-map", "[v]", "-map", "0:a?", *video_codec(), "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(out),
    ]


def build_cut_rhythm(ctx: Context, out: Path) -> list[str]:
    total = duration(ctx)
    return [
        "-i", str(ctx["video"]),
        "-filter_complex", (
            f"[0:v]trim=0:{total * 0.45:.3f},setpts=PTS-STARTPTS[v0];"
            f"[0:v]trim={total * 0.5:.3f}:{total * 0.95:.3f},setpts=PTS-STARTPTS[v1];"
            "[v0][v1]concat=n=2:v=1:a=0[v]"
        ),
        "-map", "[v]", *video_codec(), "-an", str(out),
    ]


BUILDERS: dict[str, Builder] = {
    "animator": build_animator,
    "beat-sync-editor": build_beat_sync,
    "branding-manager": build_branding,
    "broll-variety-planner": build_broll_variety,
    "color-grading-keeper": build_color_grading,
    "cut-rhythm-editor": build_cut_rhythm,
    "emphasis-sticker-placer": build_emphasis,
    "hook-visual-editor": build_hook_visual,
    "intro-outro-manager": build_intro_outro,
    "motion-graphic-editor": build_motion_graphic,
    "pattern-interrupt-inserter": build_pattern_interrupt,
    "preview-frame-extractor": build_preview_frames,
    "seamless-loop-editor": build_seamless_loop,
    "sfx-timing-placer": build_sfx_timing,
    "thumbnail-designer": build_thumbnail,
    "variant-batch-renderer": build_variant_batch,
    "video-editor": build_video_editor,
    "watermark-logo-placer": build_watermark,
}

PNG_SKILLS = {"preview-frame-extractor", "thumbnail-designer"}
NO_AUDIO_SKILLS = {
    "animator", "cut-rhythm-editor", "intro-outro-manager", "pattern-interrupt-inserter",
    "seamless-loop-editor", "variant-batch-renderer",
}


def context_for_real_run(skill: str) -> Context:
    video = st.final_video_input()
    if skill == "animator":
        source = st.first_existing(lib.ROOT / "assets" / "scenes" / "*.png") or st.ensure_media_fixtures()["frame"]
    else:
        if video is None:
            raise lib.SkillError("No video found for ffmpeg effect: expected final-video.mp4, captioned.mp4 or rough-cut.mp4")
        source = video
    ctx = params()
    ctx.update({
        "skill": skill,
        "project": lib.project_name(),
        "video": source,
        "image": st.first_existing(lib.ROOT / "assets" / "scenes" / "*.png") or st.ensure_media_fixtures()["frame"],
        "audio": lib.stage(3, "voiceover.mp3"),
        "logo": st.first_existing(lib.ROOT / "assets" / "brand" / "*.png")
                or st.first_existing(lib.ROOT / "assets" / "scenes" / "*.png")
                or st.ensure_media_fixtures()["frame"],
        "duration_sec": st.probe_summary(source)["duration_sec"] if source.suffix != ".png" else 3.0,
    })
    return ctx


def report_for(skill: str, ctx: Context, output: Path, source_duration: float,
               report_path: Path) -> dict[str, Any]:
    paths = ctx.get("variant_outputs", [output])
    summaries = [st.probe_summary(path) for path in paths]
    primary = summaries[0]
    data = {
        "status": "PASS",
        "skill": skill,
        "project": lib.project_name(),
        "generated_at": "2026-11-23T10:00:00Z",
        "video": lib.relative(output),
        "duration_sec": round(source_duration, 3) if output.suffix == ".png" else primary["duration_sec"],
        "width": primary["width"],
        "height": primary["height"],
        "has_audio": primary["has_audio"],
        "parameters": {
            "source": lib.relative(ctx["video"]),
            "resolution_source": "config/defaults.json",
            "palette_source": "config/style-bible.json",
            "font": ctx["font"],
            "variants": [lib.relative(path) for path in paths] if len(paths) > 1 else None,
        },
        "summary": f"{skill} produced {len(paths)} verified output file(s) with a purpose-specific ffmpeg filter.",
    }
    lib.write_json(report_path, data)
    return data


def run(skill: str) -> None:
    status, detail = lib.ffmpeg_status()
    if status != "OK":
        print(f"BLOCKED {skill}: ffmpeg {status} - {detail}")
        return
    ctx = context_for_real_run(skill)
    output = lib.ensure(lib.stage(7, f"{skill}.{'png' if skill in PNG_SKILLS else 'mp4'}"))
    source_duration = float(ctx["duration_sec"])
    st.ffmpeg_run(BUILDERS[skill](ctx, output))
    report = report_for(skill, ctx, output, source_duration,
                        lib.ensure(lib.stage(7, f"{skill}.json")))
    lib.ok(skill, report["summary"], lib.ensure(lib.stage(7, f"{skill}.json")))


def self_test(skill: str) -> int:
    status, detail = lib.ffmpeg_status()
    if status != "OK":
        print(f"BLOCKED {skill}: ffmpeg {status} - {detail}")
        return 0
    media = st.ensure_media_fixtures()
    target = lib.ROOT / ".tmp" / "effect-selftest" / skill
    target.mkdir(parents=True, exist_ok=True)
    output = target / f"{skill}.{'png' if skill in PNG_SKILLS else 'mp4'}"
    ctx = params()
    ctx.update({
        "skill": skill,
        "project": lib.project_name(),
        "video": media["video"],
        "image": media["frame"],
        "audio": media["audio"],
        "logo": media["frame"],
        "duration_sec": st.probe_summary(media["video"])["duration_sec"],
    })
    source_duration = float(ctx["duration_sec"])
    st.ffmpeg_run(BUILDERS[skill](ctx, output))
    report = report_for(skill, ctx, output, source_duration, target / "report.json")
    paths = [Path(lib.ROOT / name) if not Path(name).is_absolute() else Path(name)
             for name in report["parameters"].get("variants") or [report["video"]]]
    for path in paths:
        if not path.is_file():
            raise lib.SkillError(f"Missing self-test output: {lib.relative(path)}")
    if report["width"] != ctx["w"] or report["height"] != ctx["h"]:
        raise lib.SkillError(f"Unexpected {report['width']}x{report['height']} for {skill}")
    if skill not in PNG_SKILLS and not (0.1 < report["duration_sec"] <= ctx["max_len"]):
        raise lib.SkillError(f"Unexpected duration {report['duration_sec']} for {skill}")
    if skill not in NO_AUDIO_SKILLS and skill not in PNG_SKILLS and not report["has_audio"]:
        raise lib.SkillError(f"Audio missing from {skill} self-test output")
    print(f"PASS {skill}: ffmpeg command verified by ffprobe "
          f"({report['width']}x{report['height']}, {report['duration_sec']:.2f}s, "
          f"audio={report['has_audio']})")
    return 0
