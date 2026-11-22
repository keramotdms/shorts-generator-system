#!/usr/bin/env python3
"""Run the whole 93-skill pipeline against a dummy 5-second project.

Marks every skill PASS / FAIL / BLOCKED. No installs, no security changes.
FFmpeg-dependent skills are BLOCKED (not FAIL) while ffmpeg.exe is blocked.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import skill_lib as lib  # noqa: E402
from test_skills import parse, validate  # noqa: E402

DUMMY = ROOT / "projects" / "dummy"
FIXTURES = ROOT / "tests" / "fixtures"
REPORT = FIXTURES / "dummy_pipeline" / "report.json"


def setup_dummy() -> None:
    if DUMMY.exists():
        shutil.rmtree(DUMMY)
    for stage in lib.STAGE_DIRS.values():
        (DUMMY / stage).mkdir(parents=True, exist_ok=True)
    shutil.copy2(FIXTURES / "latest_script.json", DUMMY / "02-script" / "latest_script.json")
    shutil.copy2(FIXTURES / "captions.json", DUMMY / "03-voice" / "captions.json")
    (DUMMY / "03-voice" / "voiceover.mp3").write_bytes(b"")
    scenes = DUMMY / "06-video" / "scenes"
    scenes.mkdir(parents=True, exist_ok=True)
    (scenes / "scene_001.mp4").write_bytes(b"")
    lib.write_json(DUMMY / "project.json", {
        "name": "dummy",
        "duration_sec": 5,
        "source": "tests/fixtures/latest_script.json",
        "aspect_ratio": "9:16",
    })


def run_skill(name: str, fields: dict[str, str], skill_md: Path) -> tuple[str, str]:
    errors = validate(skill_md)
    if errors:
        return "FAIL", "; ".join(errors[:3])

    if fields.get("requires", "").lower() == "ffmpeg":
        status, detail = lib.ffmpeg_status()
        if status != "OK":
            return "BLOCKED", f"ffmpeg {status}: {detail}"

    if fields.get("type") in {"script-backed", "checker"}:
        env = os.environ.copy()
        env["PROJECT"] = "dummy"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "skill_tools.py"), name, "--self-test"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        output = result.stdout.strip()
        if "BLOCKED" in output:
            return "BLOCKED", output.splitlines()[-1]
        if result.returncode != 0 or "PASS" not in output:
            return "FAIL", output or result.stderr.strip()[:200]
        return "PASS", output.splitlines()[-1]

    return "PASS", "prompt-only skill validated; exact I/O paths present"


def main() -> int:
    setup_dummy()
    os.environ["PROJECT"] = "dummy"
    contracts = json.loads((ROOT / "config" / "skill-contracts.json").read_text(encoding="utf-8"))
    names = sorted(contracts.get("skills", {}))

    results: list[dict[str, str]] = []
    for name in names:
        skill_md = ROOT / ".opencode" / "skills" / name / "SKILL.md"
        if not skill_md.is_file():
            results.append({"skill": name, "status": "FAIL", "detail": "missing SKILL.md"})
            continue
        fields, _ = parse(skill_md.read_text(encoding="utf-8"))
        status, detail = run_skill(name, fields, skill_md)
        results.append({"skill": name, "status": status, "detail": detail})
        print(f"[{status}] {name}: {detail}")

    counts = {key: sum(1 for item in results if item["status"] == key)
              for key in ("PASS", "FAIL", "BLOCKED")}
    lib.write_json(REPORT, {
        "project": "projects/dummy",
        "fixture": "tests/fixtures/latest_script.json",
        "counts": counts,
        "results": results,
    })
    print()
    print(f"Dummy pipeline: {counts['PASS']} PASS | {counts['FAIL']} FAIL | "
          f"{counts['BLOCKED']} BLOCKED")
    print(f"Report: {lib.relative(REPORT)}")
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
