#!/usr/bin/env python3
"""Tiny stdlib-only pipeline state manager for the Shorts production system."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "projects" / "_template" / "pipeline-state.json"

STAGES = [
    ("research", "Research", "book-finder / trend-finder"),
    ("script", "Script", "story-thinker / hook-writer / shorts-script-writer"),
    ("voice", "Voice", "shorts-voiceover-captions"),
    ("character", "Character", "character-designer"),
    ("scene", "Scene", "collector"),
    ("video", "Video", "video-maker"),
    ("edit", "Edit", "rough-cut-assembler / caption-maker / safe-zone-checker"),
    ("final_test", "Final Test", "bug-finder / pipeline-health-checker"),
    ("description", "Description / SEO", "description-maker"),
    ("publish", "Publish", "handover"),
]


def new_state() -> dict[str, Any]:
    return {
        "project": "_template",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "current_stage": "research",
        "stages": [
            {
                "id": stage_id,
                "name": name,
                "skill": skill,
                "status": "current" if index == 0 else "pending",
            }
            for index, (stage_id, name, skill) in enumerate(STAGES)
        ],
    }


def load_state() -> dict[str, Any] | None:
    if not STATE_PATH.exists():
        return None
    with STATE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def cmd_init() -> None:
    if STATE_PATH.exists():
        print(f"State already exists: {STATE_PATH.relative_to(ROOT)}")
        return
    save_state(new_state())
    print(f"State created: {STATE_PATH.relative_to(ROOT)}")


def cmd_status() -> int:
    state = load_state()
    if state is None:
        print("No state file. Run: python scripts/orchestrator.py init")
        return 1

    print(f"Project: {state['project']}")
    print(f"Current stage: {state['current_stage']}")
    print()
    for stage in state["stages"]:
        status = stage["status"]
        if status == "current":
            marker = "[>]"
        elif status == "done":
            marker = "[x]"
        else:
            marker = "[ ]"
        print(f"{marker} {stage['id']:<12} {stage['name']:<18} skill: {stage['skill']}")
    return 0


def cmd_complete(stage_id: str) -> int:
    state = load_state()
    if state is None:
        print("No state file. Run: python scripts/orchestrator.py init")
        return 1

    if state["current_stage"] == "done":
        print("Pipeline is already complete. Use reset to start over.")
        return 1

    if stage_id != state["current_stage"]:
        print(
            f"Cannot complete '{stage_id}'. Current stage is "
            f"'{state['current_stage']}'. Finish the current stage first."
        )
        return 1

    for stage in state["stages"]:
        if stage["id"] == stage_id:
            stage["status"] = "done"
            break

    next_stage = None
    for stage in state["stages"]:
        if stage["status"] == "pending":
            stage["status"] = "current"
            next_stage = stage["id"]
            break

    state["current_stage"] = next_stage if next_stage else "done"
    save_state(state)
    print(f"Completed: {stage_id}")
    print(f"Current stage: {state['current_stage']}")
    return 0


def cmd_reset() -> None:
    if STATE_PATH.exists():
        STATE_PATH.unlink()
        print("State reset. Run init to start again.")
    else:
        print("No state file to reset.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Shorts pipeline state manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create the pipeline state file")
    subparsers.add_parser("status", help="Show current pipeline status")

    complete_parser = subparsers.add_parser("complete", help="Mark the current stage done")
    complete_parser.add_argument("stage_id", help="Stage id to complete")

    subparsers.add_parser("reset", help="Delete the pipeline state file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "init":
        cmd_init()
    elif args.command == "status":
        sys.exit(cmd_status())
    elif args.command == "complete":
        sys.exit(cmd_complete(args.stage_id))
    elif args.command == "reset":
        cmd_reset()


if __name__ == "__main__":
    main()
