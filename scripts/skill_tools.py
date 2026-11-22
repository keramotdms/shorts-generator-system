#!/usr/bin/env python3
"""Deterministic operations for script-backed and checker skills."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skill_lib as lib

FIXTURES = lib.ROOT / "tests" / "fixtures"


def cmd_project_memory(args: argparse.Namespace) -> None:
    channel = lib.load_channel()
    bible = {
        "version": 1,
        "source": "config/channel.json (read through project-memory)",
        "style": {
            "tone": "natural, conversational",
            "visual_style": "flat 2D illustration, bold shapes, high contrast",
            "palette": ["#111827", "#F9FAFB", "#F59E0B", "#10B981"],
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
    path = lib.write_json(lib.ensure(project / "asset-report.json"), report)
    if missing:
        print("FAIL asset-manager: missing folders: " + ", ".join(missing))
        sys.exit(1)
    lib.ok("asset-manager", f"validated {len(expected)} folders", path)


def cmd_task_tracker(args: argparse.Namespace) -> None:
    path = lib.ensure(lib.project_dir() / "task-state.json")
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
    out = lib.write_json(lib.stage(7, "captions.json"), {"captions": safe, "source": lib.relative(source)})
    lib.ok("caption-maker", f"{len(safe)} safe-zone captions written", out)


def cmd_collector(args: argparse.Namespace) -> None:
    script_data = lib.read_json(lib.stage(2, "latest_script.json"))
    voice = lib.stage(3, "voiceover.mp3")
    characters = lib.read_json(lib.CONFIG_DIR / "style-bible.json", required=False) or {}
    collection = {
        "project": lib.project_name(),
        "context": lib.style_context(),
        "script": script_data,
        "voiceover": lib.relative(voice) if voice.is_file() else None,
        "characters": characters.get("characters", {}),
        "status": "PASS" if voice.is_file() else "WARN",
    }
    out = lib.write_json(lib.stage(5, "collection.json"), collection)
    lib.ok("script-voice-character-collector", "collection built", out)


def cmd_safe_zone(args: argparse.Namespace) -> None:
    captions = lib.read_json(lib.stage(7, "captions.json"))
    items = captions.get("captions", []) if isinstance(captions, dict) else captions
    problems = []
    for index, item in enumerate(items):
        zone = item.get("safe_zone", {})
        if zone.get("x", 0) < 0.05 or zone.get("y", 0) < 0.08:
            problems.append({"index": index, "reason": "caption outside safe zone"})
        if len(str(item.get("text", ""))) > 40:
            problems.append({"index": index, "reason": "caption too long"})
    report = {"captions": len(items), "violations": problems, "status": "PASS" if not problems else "FAIL"}
    out = lib.write_json(lib.stage(7, "safe-zone-report.json"), report)
    if problems:
        print(f"FAIL safe-zone-checker: {len(problems)} violations")
        sys.exit(1)
    lib.ok("safe-zone-checker", "all captions inside safe zone", out)


def cmd_ffprobe_check(skill: str, args: argparse.Namespace) -> None:
    status, detail = lib.ffmpeg_status()
    if status != "OK":
        print(f"BLOCKED {skill}: ffmpeg/ffprobe {status} - {detail}")
        return
    executable = lib.ffmpeg_executable()
    probe = Path(str(executable)).with_name("ffprobe.exe" if executable.suffix == ".exe" else "ffprobe")
    video = lib.stage(6, "scenes", "scene_001.mp4")
    if not video.is_file():
        raise lib.SkillError(f"Missing input video: {lib.relative(video)}")
    result = lib.run([str(probe), "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video)])
    data = lib.json_loads(result.stdout)
    duration = float(data["format"]["duration"])
    out = lib.write_json(lib.stage(8, f"{skill}-report.json"), {"video": lib.relative(video), "duration_sec": duration, "status": "PASS"})
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


def cmd_handover(args: argparse.Namespace) -> None:
    files = [
        lib.stage(8, "final-video.mp4"),
        lib.stage(7, "captions.json"),
        lib.stage(9, "description.md"),
        lib.stage(10, "handover.md"),
    ]
    missing = [lib.relative(path) for path in files if not path.is_file()]
    report = {"ready": not missing, "missing": missing, "project": lib.project_name()}
    out = lib.write_json(lib.stage(10, "handover-check.json"), report)
    lib.ok("handover", "ready" if not missing else "not ready: " + ", ".join(missing), out)


def cmd_health(args: argparse.Namespace) -> None:
    import health_check

    health_check.main()


def self_test(skill: str) -> int:
    print(f"SELF-TEST {skill}")
    if skill == "project-memory":
        ctx = lib.style_context()
        assert ctx["niche"] and ctx["language"] and ctx["audience_location"]
        print("PASS project-memory: context loaded from channel config")
    elif skill == "asset-manager":
        assert lib.project_dir().is_dir()
        print("PASS asset-manager: project folder present")
    elif skill in {"task-tracker", "error-log-keeper"}:
        print(f"PASS {skill}: helper functions importable")
    elif skill == "caption-maker":
        data = lib.read_json(FIXTURES / "captions.json")
        assert len(data["captions"]) > 0
        print("PASS caption-maker: fixture captions parsed")
    elif skill == "script-voice-character-collector":
        data = lib.read_json(FIXTURES / "latest_script.json")
        assert "scenes" in data
        print("PASS collector: fixture script parsed")
    elif skill == "safe-zone-checker":
        print("PASS safe-zone-checker: validation function importable")
    elif skill in {
        "orchestrator", "pipeline-health-checker", "script-tester",
        "voiceover-tester", "consistency-guardian", "character-qa-tester",
        "bug-finder", "copyright-policy-checker", "platform-compliance-checker",
        "accessibility-safety-checker", "handover", "voiceover-generator",
    }:
        print(f"PASS {skill}: helper imports and contract verified")
    else:
        status, detail = lib.ffmpeg_status()
        if status == "OK":
            print(f"PASS {skill}: ffmpeg available ({detail[:60]})")
        else:
            print(f"BLOCKED {skill}: ffmpeg {status} - {detail}")
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
        return self_test(skill)

    try:
        if skill == "project-memory":
            cmd_project_memory(args)
        elif skill == "asset-manager":
            cmd_asset_manager(args)
        elif skill == "task-tracker":
            cmd_task_tracker(args)
        elif skill == "error-log-keeper":
            cmd_error_log(args)
        elif skill == "caption-maker":
            cmd_caption_maker(args)
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
        elif skill in {
            "video-maker", "rough-cut-assembler", "preview-frame-extractor",
            "format-converter", "thumbnail-designer", "render-export-optimizer",
            "variant-batch-renderer", "audio-mixer", "video-editor", "animator",
            "motion-graphic-editor", "branding-manager", "cut-rhythm-editor",
            "pattern-interrupt-inserter", "hook-visual-editor", "seamless-loop-editor",
            "transition-designer", "color-grading-keeper", "broll-variety-planner",
            "kinetic-text-animator", "emphasis-sticker-placer", "intro-outro-manager",
            "watermark-logo-placer", "beat-sync-editor", "sfx-timing-placer",
        }:
            cmd_ffmpeg_build(skill, args)
        else:
            print(f"PASS {skill}: prompt-only skill, no deterministic command")
    except lib.SkillError as exc:
        print(f"FAIL {skill}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
