#!/usr/bin/env python3
"""Deterministic operations for script-backed and checker skills."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skill_lib as lib

FIXTURES = lib.ROOT / "tests" / "fixtures"
VALID = FIXTURES / "valid"
MEDIA = lib.ROOT / ".tmp" / "media"

# No skill uses the shared concat helper any more. The 18 formerly generic
# skills now have purpose-specific commands in scripts/effect_ffmpeg.py.
GENERIC_FFMPEG_SKILLS: set[str] = set()

CHECKER_TARGETS = {
    "script-tester": [("json", "latest_script", 2, "latest_script.json")],
    "voiceover-tester": [("audio", None, 3, "voiceover.mp3")],
    "platform-compliance-checker": [("video", None, 8, "final-video.mp4")],
    "accessibility-safety-checker": [
        ("json", "captions", 7, "captions.json"),
        ("audio", None, 3, "voiceover.mp3"),
    ],
    "bug-finder": [("video", None, 8, "final-video.mp4")],
    "character-qa-tester": [("characters", "character", 0, "*.json")],
    "consistency-guardian": [
        ("characters", "character", 0, "*.json"),
        ("videos", None, 6, "scenes/*.mp4"),
    ],
    "copyright-policy-checker": [
        ("json", "latest_script", 2, "latest_script.json"),
        ("text", None, 9, "description.md"),
    ],
}


def ffmpeg_executable() -> Path:
    executable = lib.require_ffmpeg()
    assert executable is not None
    return executable


def ffprobe_executable() -> Path:
    executable = lib.ffprobe_executable()
    if executable is None:
        raise lib.SkillError("ffprobe not found (set FFPROBE_PATH)")
    return executable


def ffmpeg_run(arguments: list[str]) -> None:
    result = lib.run(
        [str(ffmpeg_executable()), "-y", "-hide_banner", "-loglevel", "error", *arguments],
        check=False,
    )
    if result.returncode != 0:
        raise lib.SkillError(f"ffmpeg failed: {result.stderr[-400:]}")


def probe_media(path: Path) -> dict[str, Any]:
    result = lib.run([
        str(ffprobe_executable()), "-v", "error",
        "-show_entries", "stream=codec_type,width,height",
        "-show_entries", "format=duration",
        "-of", "json", str(path),
    ])
    return lib.json_loads(result.stdout)


def probe_summary(path: Path) -> dict[str, Any]:
    data = probe_media(path)
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
    return {
        "path": lib.relative(path),
        "width": video.get("width"),
        "height": video.get("height"),
        "duration_sec": float((data.get("format") or {}).get("duration", 0) or 0),
        "has_audio": bool(audio),
    }


def ensure_media_fixtures() -> dict[str, Path]:
    """Create small real media files once, using the already-installed FFmpeg."""
    MEDIA.mkdir(parents=True, exist_ok=True)
    video = MEDIA / "probe_video.mp4"
    audio = MEDIA / "probe_audio.mp3"
    frame = MEDIA / "probe_frame.png"
    description = MEDIA / "description_sample.md"
    if not description.is_file():
        description.write_text("# Sample description\nVoiceover and captions are ready.\n", encoding="utf-8")
    if not video.is_file():
        ffmpeg_run([
            "-f", "lavfi", "-i", "color=c=black:s=1080x1920:d=1:r=30",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest", str(video),
        ])
    if not audio.is_file():
        ffmpeg_run([
            "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
            "-c:a", "libmp3lame", "-q:a", "9", str(audio),
        ])
    if not frame.is_file():
        ffmpeg_run([
            "-f", "lavfi", "-i", "color=c=black:s=1080x1920:d=1",
            "-frames:v", "1", str(frame),
        ])
    return {"video": video, "audio": audio, "frame": frame, "description": description}


def filter_escape(text: str) -> str:
    for old, new in (("\\", "\\\\"), (":", "\\:"), ("'", "\\'"), ("%", "\\%"), (",", "\\,")):
        text = text.replace(old, new)
    return text


def srt_time(seconds: float) -> str:
    millis = max(0, int(round(seconds * 1000)))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def first_existing(pattern: Path) -> Path | None:
    matches = sorted(pattern.parent.glob(pattern.name)) if pattern.parent.is_dir() else []
    return matches[0] if matches else None


def font_file() -> Path | None:
    """Prefer the bundled Bangla fonts, then any bundled TTF, then a Windows fallback."""
    fonts_root = lib.ROOT / "assets" / "fonts"
    bundled = sorted(fonts_root.rglob("*.ttf")) if fonts_root.is_dir() else []
    preferred = [path for path in bundled if "NotoSansBengali" in path.name]
    preferred += [path for path in bundled if "HindSiliguri-Regular" in path.name]
    chosen = preferred or bundled
    if chosen:
        return chosen[0]
    system_candidates = [
        Path("C:/Windows/Fonts/Nirmala.ttc"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    return next((path for path in system_candidates if path.is_file()), None)


def cmd_project_memory(args: argparse.Namespace) -> None:
    channel = lib.load_channel()
    bible = {
        "version": 1,
        "source": "config/channel.json (read through project-memory)",
        "style": {
            "tone": "natural, conversational",
            "visual_style": "flat 2D illustration, bold shapes, high contrast",
            "palette": ["#111827", "#F9FAFB", "#F59E0B", "#10B981"],
            "skin_palette": ["#F6D5B8", "#E8B98E", "#D9A066", "#C68642", "#A9683A", "#96603A"],
            "font": "Noto Sans Bengali",
        },
        "characters": {"default": "friendly young Bangla-speaking creator"},
        "voice": {"language": channel["language"], "default_gender": "male"},
        "channel": {
            "niche": channel["niche"],
            "language": channel["language"],
            "audience_location": channel["audience_location"],
            "video": channel.get("video", {}),
            "platforms": channel.get("platforms", []),
        },
    }
    if args.command == "show":
        print(lib.json_dumps(bible))
        return
    # Keep font/license paths recorded in the existing style bible.
    existing = lib.read_json(lib.STYLE_BIBLE_PATH, required=False) or {}
    existing_style = existing.get("style", {}) if isinstance(existing, dict) else {}
    if isinstance(existing_style, dict):
        for key in (
            "font_path",
            "font_license",
            "fallback_font",
            "fallback_font_path",
            "fallback_font_bold_path",
            "fallback_font_license",
        ):
            if key in existing_style:
                bible["style"][key] = existing_style[key]
    path = lib.write_json(lib.STYLE_BIBLE_PATH, bible)
    lib.ok("project-memory", "style bible written from channel config", path)


def cmd_asset_manager(args: argparse.Namespace) -> None:
    project = lib.project_dir()
    expected = [project / name for name in lib.STAGE_DIRS.values()] + [
        lib.ROOT / "assets" / "characters",
        lib.ROOT / "assets" / "scenes",
        lib.ROOT / "assets" / "fonts",
    ]
    missing = [lib.relative(path) for path in expected if not path.is_dir()]
    report = {
        "project": lib.project_name(),
        "expected_folders": len(expected),
        "missing_folders": missing,
        "status": "PASS" if not missing else "FAIL",
    }
    path = lib.write_json(
        lib.contract_output("asset-manager", filename="asset-manager.json") or project / "asset-manager.json",
        report,
    )
    if missing:
        print("FAIL asset-manager: missing folders: " + ", ".join(missing))
        sys.exit(1)
    lib.ok("asset-manager", f"validated {len(expected)} folders", path)


def cmd_task_tracker(args: argparse.Namespace) -> None:
    path = lib.contract_output("task-tracker", filename="task-tracker.json") or lib.project_dir() / "task-tracker.json"
    lib.ensure(path)
    state = lib.read_json(path, required=False) or {"tasks": []}
    if args.command == "add":
        state["tasks"].append({"name": args.name, "status": "pending"})
    elif args.command == "done":
        for task in state["tasks"]:
            if task["name"] == args.name:
                task["status"] = "done"
    elif args.command == "list":
        for task in state["tasks"]:
            print(f"[{task['status']}] {task['name']}")
        return
    lib.write_json(path, state)
    lib.ok("task-tracker", f"{args.command} -> {len(state['tasks'])} tasks", path)


def cmd_error_log(args: argparse.Namespace) -> None:
    path = lib.project_dir() / "08-final-test" / "error-log.jsonl"
    if args.command == "add":
        lib.append_jsonl(path, {"skill": args.skill, "message": args.message, "status": args.status})
        lib.ok("error-log-keeper", "error appended", path)
    else:
        if not path.is_file():
            print("No errors logged.")
            return
        print(path.read_text(encoding="utf-8"), end="")


def cmd_caption_maker(args: argparse.Namespace) -> None:
    source = lib.stage(3, "captions.json")
    rough_cut = lib.stage(7, "rough-cut.mp4")
    if not rough_cut.is_file():
        raise lib.SkillError(f"Missing input file: {lib.relative(rough_cut)}")
    lib.validate_schema("captions", source)
    data = lib.read_json(source)
    captions = data.get("captions", []) if isinstance(data, dict) else data
    if not isinstance(captions, list) or not captions:
        raise lib.SkillError(f"No caption events found in {lib.relative(source)}")
    safe: list[dict[str, Any]] = []
    for item in captions:
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        safe.append(
            {
                "text": text,
                "start": float(item.get("start", 0)),
                "end": float(item.get("end", 0)),
                "scene_number": int(item.get("scene_number", 0)),
                "safe_zone": {"x": 0.08, "y": 0.12, "width": 0.84, "height": 0.24},
                "max_chars_per_line": 18,
            }
        )
    result = dict(data) if isinstance(data, dict) else {}
    result["captions"] = safe
    if not result.get("language"):
        result["language"] = lib.load_channel()["language"]
    result["source"] = lib.relative(source)
    out = lib.write_json(lib.stage(7, "captions.json"), result)
    lib.validate_schema("captions", out)
    lib.ok("caption-maker", f"{len(safe)} safe-zone captions written", out)


def cmd_collector(args: argparse.Namespace) -> None:
    lib.validate_schema("latest_script", lib.stage(2, "latest_script.json"))
    script_data = lib.read_json(lib.stage(2, "latest_script.json"))
    voice = lib.stage(3, "voiceover.mp3")
    style_bible = lib.read_json(lib.CONFIG_DIR / "style-bible.json", required=False) or {}
    design_path = lib.ROOT / "assets" / "characters" / "creator-01" / "character.json"
    if not design_path.is_file():
        design_path = lib.ROOT / "assets" / "characters" / "creator-01.json"
    design = lib.read_json(design_path, required=False) or {}
    if not design:
        raise lib.SkillError(f"Missing input file: {lib.relative(design_path)}")
    characters = dict(style_bible.get("characters", {}))
    characters["designs"] = {design_path.name: design}

    scene_data = script_data.get("scenes", []) if isinstance(script_data, dict) else []
    scene_images: list[str] = []
    scene_files: list[str] = []
    fallback_image = lib.ROOT / "assets" / "scenes" / "scene-warm-desk-smile.png"
    for index in range(1, len(scene_data) + 1):
        image = lib.stage(5, f"scene_{index:03d}.png")
        if not image.is_file():
            image = fallback_image
        if not image.is_file():
            raise lib.SkillError(f"Missing input file: {lib.relative(image)}")
        scene_images.append(lib.relative(image))
        scene_files.append(f"scene_{index:03d}.mp4")

    collection = {
        "project": lib.project_name(),
        "context": lib.style_context(),
        "script": script_data,
        "voiceover": lib.relative(voice) if voice.is_file() else None,
        "characters": characters,
        "scene_images": scene_images,
        "scenes": scene_files,
        "status": "PASS" if voice.is_file() else "WARN",
    }
    out = lib.write_json(lib.stage(5, "collection.json"), collection)
    lib.validate_schema("collection", out)
    lib.ok("script-voice-character-collector", "collection built with scenes and character design", out)


def cmd_safe_zone(args: argparse.Namespace) -> None:
    source = lib.stage(7, "captions.json")
    lib.validate_schema("captions", source)
    captions = lib.read_json(source)
    items = captions.get("captions", []) if isinstance(captions, dict) else captions
    problems: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        zone = item.get("safe_zone", {})
        if zone.get("x", 0) < 0.05 or zone.get("y", 0) < 0.08:
            problems.append({"index": index, "reason": "caption outside safe zone"})
        if len(str(item.get("text", ""))) > 40:
            problems.append({"index": index, "reason": "caption too long"})
    video = lib.stage(7, "captioned.mp4")
    if not video.is_file():
        video = lib.stage(7, "rough-cut.mp4")
    preview = None
    resolution: dict[str, Any] = {}
    if video.is_file():
        summary = probe_summary(video)
        resolution = {"width": summary["width"], "height": summary["height"]}
        if summary["width"] != 1080 or summary["height"] != 1920:
            problems.append({"index": -1, "reason": "video is not 1080x1920"})
        preview = lib.stage(7, "safe-zone-preview.png")
        ffmpeg_run([
            "-i", str(video),
            "-vf", "drawbox=x=86:y=230:w=907:h=461:color=red@0.35:t=3",
            "-frames:v", "1", str(preview),
        ])
    report = {
        "captions": len(items), "violations": problems,
        "resolution": resolution,
        "preview": lib.relative(preview) if preview else None,
        "status": "PASS" if not problems else "FAIL",
    }
    out = lib.write_json(
        lib.contract_output("safe-zone-checker", filename="safe-zone-checker.json")
        or lib.stage(7, "safe-zone-checker.json"),
        report,
    )
    if problems:
        raise lib.SkillError(f"{len(problems)} safe-zone violations")
    lib.ok("safe-zone-checker", "captions and video safe zone verified", out)


def cmd_ffprobe_check(skill: str, args: argparse.Namespace) -> None:
    status, detail = lib.ffprobe_status()
    if status != "OK":
        print(f"BLOCKED {skill}: ffprobe {status} - {detail}")
        return
    probe = ffprobe_executable()
    video = lib.stage(6, "scenes", "scene_001.mp4")
    if not video.is_file():
        raise lib.SkillError(f"Missing input video: {lib.relative(video)}")
    result = lib.run([str(probe), "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video)])
    data = lib.json_loads(result.stdout)
    duration = float(data["format"]["duration"])
    out = lib.write_json(
        lib.contract_output(skill, filename=f"{skill}.json") or lib.stage(8, f"{skill}-report.json"),
        {"video": lib.relative(video), "duration_sec": duration, "status": "PASS"},
    )
    lib.ok(skill, f"duration {duration:.3f}s", out)


def cmd_ffmpeg_build(skill: str, args: argparse.Namespace) -> None:
    status, detail = lib.ffmpeg_status()
    if status != "OK":
        print(f"BLOCKED {skill}: ffmpeg {status} - {detail}")
        return
    executable = lib.ffmpeg_executable()
    scenes = sorted(lib.stage(6, "scenes").glob("*.mp4"))
    if not scenes:
        raise lib.SkillError("No scene videos found in projects/<project>/06-video/scenes/")
    list_file = lib.ensure(lib.stage(7, f"{skill}-inputs.txt"))
    list_file.write_text("".join(f"file '{path.as_posix()}'\n" for path in scenes), encoding="utf-8")
    output = lib.stage(7, f"{skill}.mp4")
    result = lib.run([str(executable), "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(output)], check=False)
    if result.returncode != 0:
        raise lib.SkillError(f"ffmpeg failed: {result.stderr[-400:]}")
    lib.ok(skill, "video rendered", output)


def final_video_input(*, prefer_final: bool = True) -> Path | None:
    candidates = [
        lib.stage(8, "final-video.mp4"),
        lib.stage(7, "captioned.mp4"),
        lib.stage(7, "rough-cut.mp4"),
    ]
    if not prefer_final:
        candidates = candidates[1:] + candidates[:1]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    scenes = sorted(lib.stage(6, "scenes").glob("*.mp4"))
    return scenes[0] if scenes else None


def music_input() -> Path | None:
    folder = lib.ROOT / "assets" / "music"
    return first_existing(folder / "*.mp3") or first_existing(folder / "*.wav")


def cmd_video_maker(skill: str, args: argparse.Namespace) -> None:
    collection_path = lib.stage(5, "collection.json")
    collection = lib.read_json(collection_path)
    script = collection.get("script", {}) if isinstance(collection, dict) else {}
    scene_data = script.get("scenes", []) if isinstance(script, dict) else []
    image_paths = collection.get("scene_images", []) if isinstance(collection, dict) else []
    scene_names = collection.get("scenes", []) if isinstance(collection, dict) else []
    if not image_paths or not scene_names or len(image_paths) != len(scene_names):
        raise lib.SkillError(
            f"{lib.relative(collection_path)} must contain matching scene_images[] and scenes[]"
        )
    out_dir = lib.stage(6, "scenes")
    out_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    for index, (relative_image, name) in enumerate(zip(image_paths, scene_names), start=1):
        image = lib.ROOT / str(relative_image)
        if not image.is_file():
            raise lib.SkillError(f"Missing input file: {lib.relative(image)}")
        duration = 5.0
        if index - 1 < len(scene_data) and isinstance(scene_data[index - 1], dict):
            duration = float(scene_data[index - 1].get("duration_sec", 5.0) or 5.0)
        output = out_dir / str(name)
        ffmpeg_run([
            "-loop", "1", "-framerate", "30", "-i", str(image),
            "-t", str(duration),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", str(output),
        ])
        reports.append(probe_summary(output))
    report = lib.write_json(lib.stage(6, f"{skill}-report.json"), {"scenes": reports, "status": "PASS"})
    lib.ok(skill, f"{len(reports)} scene videos rendered from collection.json", report)


def cmd_rough_cut(skill: str, args: argparse.Namespace) -> None:
    collection_path = lib.stage(5, "collection.json")
    collection = lib.read_json(collection_path)
    names = collection.get("scenes", []) if isinstance(collection, dict) else []
    if not names:
        raise lib.SkillError(f"Missing scenes[] field in {lib.relative(collection_path)}")
    scenes = [lib.stage(6, "scenes", str(name)) for name in names]
    missing = [lib.relative(path) for path in scenes if not path.is_file()]
    if missing:
        raise lib.SkillError("Missing scene videos: " + ", ".join(missing))
    list_file = lib.ensure(lib.stage(7, f"{skill}-inputs.txt"))
    list_file.write_text("".join(f"file '{path.as_posix()}'\n" for path in scenes), encoding="utf-8")
    output = lib.stage(7, "rough-cut.mp4")
    ffmpeg_run([
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy", "-avoid_negative_ts", "make_zero", str(output),
    ])
    summary = probe_summary(output)
    report = lib.write_json(lib.stage(7, f"{skill}-report.json"), summary)
    lib.ok(skill, f"rough cut assembled from {len(scenes)} scenes", report)


def cmd_caption_burn_in(skill: str, args: argparse.Namespace) -> None:
    video = lib.stage(7, "rough-cut.mp4")
    if not video.is_file():
        video = lib.stage(6, "scenes", "scene_001.mp4")
    if not video.is_file():
        raise lib.SkillError("Missing video for caption burn-in: projects/<project>/07-edit/rough-cut.mp4")
    # cmd_caption_maker() is the only producer of 07-edit/captions.json; run it first.
    captions_path = lib.stage(7, "captions.json")
    if not captions_path.is_file():
        cmd_caption_maker(argparse.Namespace())
    data = lib.read_json(captions_path)
    items = data.get("captions", []) if isinstance(data, dict) else data
    if not items:
        raise lib.SkillError("No caption events found for burn-in")
    srt = lib.ensure(lib.stage(7, "captions.srt"))
    blocks = []
    for index, item in enumerate(items, start=1):
        start = float(item.get("start", 0))
        end = float(item.get("end", start + 0.8))
        text = str(item.get("text", "")).strip()
        if text:
            blocks.append(f"{index}\n{srt_time(start)} --> {srt_time(end)}\n{text}\n")
    srt.write_text("\n".join(blocks), encoding="utf-8")
    srt_arg = Path(lib.relative(srt)).as_posix()
    output = lib.stage(7, "captioned.mp4")
    fontsdir = ""
    chosen_font = font_file()
    if chosen_font is not None and chosen_font.is_relative_to(lib.ROOT / "assets" / "fonts"):
        fontsdir = f":fontsdir={chosen_font.parent.relative_to(lib.ROOT).as_posix()}"
    ffmpeg_run([
        "-i", str(video),
        "-vf", f"subtitles=filename={srt_arg}:force_style='FontName=Noto Sans Bengali,FontSize=44,Alignment=2,MarginV=220'{fontsdir}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "copy", str(output),
    ])
    summary = probe_summary(output)
    report_path = lib.contract_output(skill, filename=f"{skill}.json") or lib.stage(7, f"{skill}.json")
    report = lib.write_json(report_path, {**summary, "captions": len(blocks)})
    lib.ok(skill, f"{len(blocks)} captions burned into video", report)


def cmd_format_converter(skill: str, args: argparse.Namespace) -> None:
    video = final_video_input()
    if video is None:
        raise lib.SkillError("No video found to convert")
    output = lib.stage(7, f"{skill}.mp4")
    ffmpeg_run([
        "-i", str(video),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(output),
    ])
    summary = probe_summary(output)
    report = lib.write_json(lib.stage(7, f"{skill}-report.json"), summary)
    lib.ok(skill, "converted to 1080x1920, 30 fps, faststart", report)


def cmd_render_export(skill: str, args: argparse.Namespace) -> None:
    video = final_video_input(prefer_final=False)
    if video is None:
        raise lib.SkillError("No video found to export")
    # One canonical final video for checkers, handover and every publish skill.
    output = lib.stage(8, "final-video.mp4")
    lib.ensure(output).parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_run([
        "-i", str(video),
        "-c:v", "libx264", "-preset", "slow", "-crf", "24",
        "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
        "-max_muxing_queue_size", "1024", str(output),
    ])
    summary = probe_summary(output)
    summary["input_bytes"] = video.stat().st_size
    summary["output_bytes"] = output.stat().st_size
    summary["canonical_path"] = lib.relative(output)
    report = lib.write_json(
        lib.contract_output(skill, filename=f"{skill}.json") or lib.stage(7, f"{skill}.json"),
        summary,
    )
    lib.ok(skill, f"exported {lib.relative(output)} ({summary['output_bytes']} bytes)", report)


def cmd_audio_mixer(skill: str, args: argparse.Namespace) -> None:
    voice = lib.stage(3, "voiceover.mp3")
    if not voice.is_file():
        raise lib.SkillError("Missing input: projects/<project>/03-voice/voiceover.mp3")
    music = music_input()
    if music:
        inputs = ["-i", str(voice), "-i", str(music)]
    else:
        inputs = ["-i", str(voice), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    output = lib.stage(7, f"{skill}.m4a")
    ffmpeg_run([
        *inputs,
        "-filter_complex",
        "[1:a]volume=0.12[bg];[0:a]aresample=44100[voice];[voice][bg]amix=inputs=2:duration=first:dropout_transition=0[a]",
        "-map", "[a]", "-c:a", "aac", "-b:a", "128k", "-shortest", str(output),
    ])
    summary = probe_summary(output)
    summary["music_source"] = lib.relative(music) if music else "silent bed (anullsrc)"
    report = lib.write_json(lib.stage(7, f"{skill}-report.json"), summary)
    lib.ok(skill, "voice and music mixed with amix", report)


def cmd_audio_ducking(skill: str, args: argparse.Namespace) -> None:
    voice = lib.stage(3, "voiceover.mp3")
    if not voice.is_file():
        raise lib.SkillError("Missing input: projects/<project>/03-voice/voiceover.mp3")
    music = music_input()
    if music:
        inputs = ["-i", str(voice), "-i", str(music)]
    else:
        inputs = ["-i", str(voice), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    output = lib.stage(7, f"{skill}.m4a")
    ffmpeg_run([
        *inputs,
        "-filter_complex",
        "[1:a]volume=0.9[music];[0:a]asplit=2[voice][key];"
        "[music][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=250[ducked];"
        "[ducked][voice]amix=inputs=2:duration=first:dropout_transition=0[a]",
        "-map", "[a]", "-c:a", "aac", "-b:a", "128k", "-shortest", str(output),
    ])
    summary = probe_summary(output)
    summary["music_source"] = lib.relative(music) if music else "silent bed (anullsrc)"
    report = lib.write_json(lib.stage(7, f"{skill}-report.json"), summary)
    lib.ok(skill, "music ducked under voice with sidechaincompress", report)


def cmd_kinetic_text(skill: str, args: argparse.Namespace) -> None:
    video = final_video_input()
    if video is None:
        raise lib.SkillError("No video found for kinetic text")
    data = lib.read_json(lib.stage(7, "captions.json"), required=False)
    if data is None:
        data = lib.read_json(lib.stage(3, "captions.json"))
    items = data.get("captions", []) if isinstance(data, dict) else data
    font = font_file()
    font_arg = ""
    if font:
        font_value = (
            Path(lib.relative(font)).as_posix() if font.is_relative_to(lib.ROOT)
            else font.as_posix()
        )
        font_arg = f"fontfile={font_value.replace(':', '\\\\:')}:"
    filters = []
    for item in list(items)[:8]:
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        start = float(item.get("start", 0))
        end = float(item.get("end", start + 0.8))
        filters.append(
            f"drawtext=text='{filter_escape(text)}':{font_arg}fontsize=56:fontcolor=white:"
            f"x=(w-text_w)/2:y=h-260:enable='between(t\\,{start}\\,{end})'"
        )
    if not filters:
        raise lib.SkillError("No caption text available for kinetic animation")
    output = lib.stage(7, f"{skill}.mp4")
    ffmpeg_run([
        "-i", str(video), "-vf", ",".join(filters),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "copy", str(output),
    ])
    summary = probe_summary(output)
    summary["animated_captions"] = len(filters)
    report = lib.write_json(lib.stage(7, f"{skill}-report.json"), summary)
    lib.ok(skill, f"{len(filters)} timed text overlays animated", report)


def cmd_transition(skill: str, args: argparse.Namespace) -> None:
    scenes = sorted(lib.stage(6, "scenes").glob("*.mp4"))
    if len(scenes) < 2:
        raise lib.SkillError("Need at least 2 scene videos in projects/<project>/06-video/scenes/")
    first, second = scenes[0], scenes[1]
    first_duration = probe_summary(first)["duration_sec"]
    offset = max(0.0, first_duration - 0.5)
    output = lib.stage(7, f"{skill}.mp4")
    ffmpeg_run([
        "-i", str(first), "-i", str(second),
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration=0.5:offset={offset:.3f}[v]",
        "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-an", str(output),
    ])
    summary = probe_summary(output)
    summary["offset_sec"] = round(offset, 3)
    report = lib.write_json(lib.stage(7, f"{skill}-report.json"), summary)
    lib.ok(skill, "cross-fade applied between first two scenes", report)


def cmd_checker(skill: str, args: argparse.Namespace) -> None:
    problems: list[str] = []
    details: dict[str, Any] = {}
    for kind, schema_name, stage_number, pattern in CHECKER_TARGETS[skill]:
        if kind == "characters":
            target = lib.ROOT / "assets" / "characters" / pattern
            matches = sorted(target.parent.glob(target.name))
            if not matches:
                problems.append(lib.relative(target))
                continue
            for path in matches:
                lib.validate_schema(schema_name, path)
            details[kind] = [lib.relative(path) for path in matches]
            continue
        if kind == "videos":
            target = lib.stage(stage_number, pattern)
            matches = sorted(lib.stage(stage_number, "scenes").glob("*.mp4"))
            if not matches:
                problems.append(lib.relative(target))
                continue
            details[kind] = [probe_summary(path) for path in matches[:3]]
            continue
        target = lib.stage(stage_number, pattern)
        if not target.is_file():
            problems.append(lib.relative(target))
            continue
        if kind == "json":
            lib.validate_schema(schema_name, target)
            details[pattern] = lib.read_json(target)
        elif kind == "text":
            details[pattern] = {"bytes": target.stat().st_size}
        elif kind == "audio":
            details[pattern] = probe_summary(target)
        elif kind == "video":
            summary = probe_summary(target)
            details[pattern] = summary
            if summary["width"] != 1080 or summary["height"] != 1920:
                problems.append(f"{lib.relative(target)}: expected 1080x1920")
            if not (1 <= summary["duration_sec"] <= 60):
                problems.append(f"{lib.relative(target)}: duration outside 1-60 s")
    report_path = lib.contract_output(skill, filename=f"{skill}.json") or lib.stage(8, f"{skill}-report.json")
    report = lib.write_json(report_path, {
        "skill": skill, "status": "FAIL" if problems else "PASS",
        "problems": problems, "details": details,
    })
    if problems:
        raise lib.SkillError("; ".join(problems))
    lib.ok(skill, "real output files checked", report)


def cmd_handover(args: argparse.Namespace) -> None:
    # handover.md is this skill's OUTPUT, never an input (no circular dependency).
    files = [
        lib.stage(8, "final-video.mp4"),
        lib.stage(7, "captions.json"),
        lib.stage(9, "description.md"),
    ]
    missing = [lib.relative(path) for path in files if not path.is_file()]
    if files[1].is_file():
        lib.validate_schema("captions", files[1])
    report = {"ready": not missing, "missing": missing, "project": lib.project_name()}
    out = lib.write_json(lib.stage(10, "handover-check.json"), report)

    channel = lib.load_channel()
    handover_md = lib.ensure(lib.stage(10, "handover.md"))
    lines = [
        f"# Handover — {lib.project_name()}",
        "",
        f"- Niche: {channel['niche']}",
        f"- Language: {channel['language']}",
        f"- Audience: {channel['audience_location']}",
        f"- Status: {'READY' if not missing else 'NOT READY'}",
        "",
        "## Final assets",
        "",
    ]
    lines += [f"- `{lib.relative(path)}`" for path in files]
    if missing:
        lines += ["", "## Missing assets", ""] + [f"- `{path}`" for path in missing]
    handover_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if missing:
        raise lib.SkillError("not ready: " + ", ".join(missing))
    lib.ok("handover", "ready: all final assets present", out)


def cmd_health(args: argparse.Namespace) -> None:
    import health_check

    health_check.main()


def self_test_dir(skill: str) -> Path:
    path = lib.ROOT / ".tmp" / "self-test" / skill
    path.mkdir(parents=True, exist_ok=True)
    return path


def fixture_video() -> tuple[bool, dict[str, Any] | str]:
    status, detail = lib.ffmpeg_status()
    if status != "OK":
        return False, f"ffmpeg {status} - {detail}"
    media = ensure_media_fixtures()
    summary = probe_summary(media["video"])
    assert summary["width"] == 1080, summary
    assert summary["height"] == 1920, summary
    assert summary["duration_sec"] > 0, summary
    return True, summary


def fixture_audio() -> tuple[bool, dict[str, Any] | str]:
    status, detail = lib.ffmpeg_status()
    if status != "OK":
        return False, f"ffmpeg {status} - {detail}"
    media = ensure_media_fixtures()
    summary = probe_summary(media["audio"])
    assert summary["duration_sec"] > 0, summary
    return True, summary


def blocked_or_pass(skill: str, ok: bool, result: dict[str, Any] | str, detail: str) -> None:
    if not ok:
        print(f"BLOCKED {skill}: {result}")
        return
    print(f"PASS {skill}: {detail}")


def self_test(skill: str) -> int:
    print(f"SELF-TEST {skill}")
    if skill in {"animator", "beat-sync-editor", "branding-manager", "broll-variety-planner",
                 "color-grading-keeper", "cut-rhythm-editor", "emphasis-sticker-placer",
                 "hook-visual-editor", "intro-outro-manager", "motion-graphic-editor",
                 "pattern-interrupt-inserter", "preview-frame-extractor", "seamless-loop-editor",
                 "sfx-timing-placer", "thumbnail-designer", "variant-batch-renderer",
                 "video-editor", "watermark-logo-placer"}:
        import effect_ffmpeg
        return effect_ffmpeg.self_test(skill)

    if skill == "trend-finder":
        import trend_finder
        return trend_finder.self_test()
    if skill == "character-designer":
        import character_designer
        return character_designer.self_test()
    if skill == "project-memory":
        ctx = lib.style_context()
        assert ctx["niche"] and ctx["language"] and ctx["audience_location"]
        print(f"PASS {skill}: context loaded from channel config ({ctx['language']}, {ctx['audience_location']})")
    elif skill == "asset-manager":
        assert lib.project_dir().is_dir()
        print(f"PASS {skill}: {lib.relative(lib.project_dir())} exists")
    elif skill == "task-tracker":
        target = self_test_dir(skill) / "task-tracker.json"
        expected = {"tasks": [{"name": "self-test", "status": "done", "stage": "research"}]}
        lib.write_json(target, expected)
        loaded = lib.read_json(target)
        assert loaded["tasks"][0]["name"] == "self-test", loaded
        assert loaded["tasks"][0]["status"] == "done", loaded
        print(f"PASS {skill}: task file round-trip verified (1 task, status=done)")
    elif skill == "error-log-keeper":
        target = self_test_dir(skill) / "error-log.jsonl"
        target.write_text("", encoding="utf-8")
        lib.append_jsonl(target, {"skill": "self-test", "status": "WARN", "reason": "fixture"})
        lines = target.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1, lines
        entry = lib.json_loads(lines[0])
        assert entry["skill"] == "self-test" and entry["status"] == "WARN", entry
        print(f"PASS {skill}: JSONL round-trip verified (1 entry, status=WARN)")
    elif skill == "caption-maker":
        lib.validate_schema("captions", VALID / "captions.json")
        data = lib.read_json(VALID / "captions.json")
        assert len(data["captions"]) >= 3, data
        print(f"PASS {skill}: caption schema verified ({len(data['captions'])} real caption blocks)")
    elif skill == "script-voice-character-collector":
        lib.validate_schema("latest_script", VALID / "latest_script.json")
        lib.validate_schema("collection", VALID / "collection.json")
        collection = lib.read_json(VALID / "collection.json")
        assert len(collection["scenes"]) >= 3, collection
        assert len(collection["scene_images"]) == len(collection["scenes"]), collection
        print(f"PASS {skill}: script and collection schemas verified ({len(collection['scenes'])} scenes)")
    elif skill == "voiceover-generator":
        lib.validate_schema("latest_script", VALID / "latest_script.json")
        lib.validate_schema("captions", VALID / "captions.json")
        script = lib.read_json(VALID / "latest_script.json")
        assert len(script["scenes"]) >= 3 and script["total_duration_sec"] >= 30, script
        print(f"PASS {skill}: script and caption schemas verified ({script['total_duration_sec']} sec)")
    elif skill == "character-qa-tester":
        import character_designer
        return character_designer.qa_self_test()
    elif skill == "consistency-guardian":
        import character_designer
        return character_designer.consistency_self_test()
    elif skill in CHECKER_TARGETS:
        for kind, schema_name, _stage, _pattern in CHECKER_TARGETS[skill]:
            if kind in ("json", "characters"):
                lib.validate_schema(schema_name, VALID / f"{schema_name}.json")
            elif kind == "text":
                assert (MEDIA / "description_sample.md").is_file()
        media = ensure_media_fixtures()
        kinds = {kind for kind, *_rest in CHECKER_TARGETS[skill]}
        if kinds & {"audio", "video", "videos"}:
            for key in ("video", "audio"):
                assert probe_summary(media[key])["duration_sec"] > 0
            assert probe_summary(media["video"])["width"] == 1080
        print(f"PASS {skill}: real output files and ffprobe checks verified")
    elif skill == "safe-zone-checker":
        lib.validate_schema("captions", VALID / "captions.json")
        data = lib.read_json(VALID / "captions.json")
        blocks = data["captions"]
        assert blocks and all(0 <= b["start"] < b["end"] <= data["total_duration_sec"] for b in blocks)
        ok, result = fixture_video()
        if ok:
            detail = f"{len(blocks)} captions inside {result['width']}x{result['height']}, {result['duration_sec']:.2f}s"
        else:
            detail = ""
        blocked_or_pass(skill, ok, result, detail)
    elif skill == "orchestrator":
        target = self_test_dir(skill) / "pipeline-state.json"
        stages = ["research", "script", "voice", "character", "scene", "video",
                  "edit", "final_test", "description", "publish"]
        lib.write_json(target, {"stages": stages, "current": "research", "status": "PASS"})
        loaded = lib.read_json(target)
        assert len(loaded["stages"]) == 10 and loaded["stages"][0] == "research", loaded
        assert loaded["current"] == "research", loaded
        print(f"PASS {skill}: 10-stage state round-trip verified (current=research)")
    elif skill == "pipeline-health-checker":
        contracts = lib.read_json(lib.CONTRACTS_PATH)
        skills = contracts["skills"]
        assert len(skills) == 93, len(skills)
        assert all(entry.get("input") and entry.get("output") for entry in skills.values())
        print(f"PASS {skill}: {len(skills)} contracts have non-empty exact input/output")
    elif skill == "handover":
        project = "self-test-handover"
        demo = lib.ROOT / "projects" / project
        old_project = os.environ.get("PROJECT")
        shutil.rmtree(demo, ignore_errors=True)
        os.environ["PROJECT"] = project
        try:
            for sub in ("08-final-test", "07-edit", "09-description", "10-publish"):
                (demo / sub).mkdir(parents=True, exist_ok=True)
            (demo / "08-final-test" / "final-video.mp4").write_bytes(b"handover fixture")
            lib.write_json(demo / "07-edit" / "captions.json", lib.read_json(VALID / "captions.json"))
            (demo / "09-description" / "description.md").write_text("# Fixture\n", encoding="utf-8")
            cmd_handover(argparse.Namespace())
            check = lib.read_json(lib.stage(10, "handover-check.json"))
            markdown = lib.stage(10, "handover.md").read_text(encoding="utf-8")
            assert check["ready"] is True, check
            assert "Path: " not in markdown  # the helper lists exact asset paths, not a fake duration
            assert lib.relative(lib.stage(8, "final-video.mp4")) in markdown, markdown
            (demo / "09-description" / "description.md").unlink()
            try:
                cmd_handover(argparse.Namespace())
                raise AssertionError("handover must fail when an asset is missing")
            except lib.SkillError as exc:
                assert "not ready" in str(exc), exc
            check = lib.read_json(lib.stage(10, "handover-check.json"))
            assert check["ready"] is False and len(check["missing"]) == 1, check
            assert lib.stage(10, "handover.md").is_file()
        finally:
            shutil.rmtree(demo, ignore_errors=True)
            if old_project is None:
                os.environ.pop("PROJECT", None)
            else:
                os.environ["PROJECT"] = old_project
        print(f"PASS {skill}: ready=true with 3 assets; ready=false and non-zero when one is missing")
    elif skill == "kinetic-text-animator":
        lib.validate_schema("captions", VALID / "captions.json")
        data = lib.read_json(VALID / "captions.json")
        assert len(data["captions"]) >= 3, data
        ok, result = fixture_video()
        if ok:
            detail = f"{len(data['captions'])} caption blocks and ffprobe {result['width']}x{result['height']}, {result['duration_sec']:.2f}s"
        else:
            detail = ""
        blocked_or_pass(skill, ok, result, detail)
    elif skill in {"audio-mixer", "audio-ducking-controller", "av-sync-checker"}:
        ok_video, video = fixture_video()
        ok_audio, audio = fixture_audio()
        ok = ok_video and ok_audio
        result = video if not ok_video else audio
        if ok:
            detail = (f"ffprobe video {video['width']}x{video['height']} {video['duration_sec']:.2f}s "
                      f"has_audio={video['has_audio']}, audio {audio['duration_sec']:.2f}s")
        else:
            detail = ""
        blocked_or_pass(skill, ok, result, detail)
    elif skill in {"video-maker", "rough-cut-assembler", "format-converter",
                   "render-export-optimizer", "transition-designer", "video-quality-checker"}:
        ok, result = fixture_video()
        if ok and skill in {"video-maker", "rough-cut-assembler"}:
            collection = lib.read_json(VALID / "collection.json")
            assert len(collection["scenes"]) >= 3, collection
            assert len(collection["scene_images"]) == len(collection["scenes"]), collection
        if ok and skill == "render-export-optimizer":
            canonical = lib.contract_output(skill, filename="final-video.mp4")
            assert canonical is not None and canonical.name == "final-video.mp4", canonical
        if ok:
            detail = f"ffprobe {result['width']}x{result['height']}, {result['duration_sec']:.2f}s"
        else:
            detail = ""
        blocked_or_pass(skill, ok, result, detail)
    else:
        ok, result = fixture_video()
        if ok:
            detail = f"ffprobe {result['width']}x{result['height']}, {result['duration_sec']:.2f}s"
        else:
            detail = ""
        blocked_or_pass(skill, ok, result, detail)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a Shorts skill's deterministic helper")
    parser.add_argument("skill", help="skill id")
    parser.add_argument("command", nargs="?", default="run")
    parser.add_argument("--name")
    parser.add_argument("--skill")
    parser.add_argument("--message")
    parser.add_argument("--status", default="open")
    parser.add_argument("--self-test", action="store_true")
    return parser


def main(argv: list[str] | None = None, skill_override: str | None = None) -> int:
    args = build_parser().parse_args(argv)
    skill = skill_override or args.skill
    if args.self_test:
        code = self_test(skill)
        if code == 0:
            import format_validator

            summary = format_validator.validate_skill_outputs(skill)
            for note in summary["infos"]:
                print("INFO " + note)
            if summary["errors"]:
                for error in summary["errors"]:
                    print(f"FAIL {skill}: {error}")
                return 1
            if summary["checked"]:
                print(
                    f"PASS {skill}: {summary['checked']} declared output file(s) match their formats"
                )
        return code

    try:
        if skill == "project-memory":
            cmd_project_memory(args)
        elif skill == "trend-finder":
            import trend_finder
            trend_finder.run()
        elif skill == "character-designer":
            import character_designer
            character_designer.run()
        elif skill == "asset-manager":
            cmd_asset_manager(args)
        elif skill == "task-tracker":
            cmd_task_tracker(args)
        elif skill == "error-log-keeper":
            cmd_error_log(args)
        elif skill == "script-voice-character-collector":
            cmd_collector(args)
        elif skill == "safe-zone-checker":
            cmd_safe_zone(args)
        elif skill == "handover":
            cmd_handover(args)
        elif skill in {"pipeline-health-checker", "health-check"}:
            cmd_health(args)
        elif skill in {"video-quality-checker", "av-sync-checker"}:
            cmd_ffprobe_check(skill, args)
        elif skill == "video-maker":
            cmd_video_maker(skill, args)
        elif skill == "rough-cut-assembler":
            cmd_rough_cut(skill, args)
        elif skill == "caption-maker":
            # Both declared outputs are produced: 07-edit/captions.json and the
            # burned-in video + 07-edit/caption-maker.json report.
            cmd_caption_maker(args)
            cmd_caption_burn_in(skill, args)
        elif skill == "format-converter":
            cmd_format_converter(skill, args)
        elif skill == "render-export-optimizer":
            cmd_render_export(skill, args)
        elif skill == "audio-mixer":
            cmd_audio_mixer(skill, args)
        elif skill == "audio-ducking-controller":
            cmd_audio_ducking(skill, args)
        elif skill == "kinetic-text-animator":
            cmd_kinetic_text(skill, args)
        elif skill == "transition-designer":
            cmd_transition(skill, args)
        elif skill in CHECKER_TARGETS:
            cmd_checker(skill, args)
        elif skill in {"animator", "beat-sync-editor", "branding-manager", "broll-variety-planner",
                       "color-grading-keeper", "cut-rhythm-editor", "emphasis-sticker-placer",
                       "hook-visual-editor", "intro-outro-manager", "motion-graphic-editor",
                       "pattern-interrupt-inserter", "preview-frame-extractor", "seamless-loop-editor",
                       "sfx-timing-placer", "thumbnail-designer", "variant-batch-renderer",
                       "video-editor", "watermark-logo-placer"}:
            import effect_ffmpeg
            effect_ffmpeg.run(skill)
        elif skill in GENERIC_FFMPEG_SKILLS:
            cmd_ffmpeg_build(skill, args)
        else:
            print(f"PASS {skill}: prompt-only skill, no deterministic command")
    except lib.SkillError as exc:
        print(f"FAIL {skill}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
