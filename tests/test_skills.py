#!/usr/bin/env python3
"""Validate SKILL.md standards and run deterministic self-tests."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".opencode" / "skills"

REQUIRED_HEADINGS = [
    "When to use",
    "Purpose",
    "Input",
    "Output",
    "Steps",
    "How to test",
    "Depends on / feeds into",
    "Failure handling",
]
REQUIRED_FIELDS = ["name", "description", "category", "status", "phase", "type", "batch"]


def parse(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields, text[end + 4 :]


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    fields, body = parse(text)
    name = path.parent.name

    for field in REQUIRED_FIELDS:
        if field not in fields:
            errors.append(f"{name}: missing frontmatter field '{field}'")
    if fields.get("name") != name:
        errors.append(f"{name}: frontmatter name is '{fields.get('name')}'")
    if "TODO" in text:
        errors.append(f"{name}: TODO remains")

    for heading in REQUIRED_HEADINGS:
        if f"# {heading}" not in body:
            errors.append(f"{name}: missing section '# {heading}'")

    if "projects/<project>/" not in body:
        errors.append(f"{name}: no exact projects/<project>/ path")
    steps = body.split("# Steps", 1)[-1].split("# How to test", 1)[0]
    numbered = [line for line in steps.splitlines() if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6."))]
    if len(numbered) < 3:
        errors.append(f"{name}: fewer than 3 numbered steps")

    if fields.get("type") not in {"prompt-only", "script-backed", "checker"}:
        errors.append(f"{name}: invalid type '{fields.get('type')}'")

    if name != "voiceover-captions" and fields.get("status") != "implemented":
        errors.append(f"{name}: status is '{fields.get('status')}', expected implemented")
    return errors


def test_schemas() -> list[str]:
    """Check every schema has at least one conforming fixture."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import schema_validator

    errors: list[str] = []
    valid = ROOT / "tests" / "fixtures" / "valid"
    for name in (
        "story", "hook", "latest_script", "captions", "collection", "character"
    ):
        target = valid / f"{name}.json"
        problems = schema_validator.validate_file(name, target)
        if problems:
            errors.append(f"schema fixture {name}: " + "; ".join(problems))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int)
    args = parser.parse_args()

    errors: list[str] = test_schemas()
    checked = 0
    script_backed: list[str] = []
    passed = 0
    blocked = 0

    def record_result(output: str) -> None:
        nonlocal passed, blocked
        results = [line.strip() for line in output.splitlines()
                   if line.strip().startswith(("PASS ", "BLOCKED "))]
        if not results:
            return
        if results[-1].startswith("PASS "):
            passed += 1
        else:
            blocked += 1

    for folder in sorted(SKILLS.iterdir()):
        if not folder.is_dir():
            continue
        md = folder / "SKILL.md"
        if not md.is_file():
            errors.append(f"{folder.name}: missing SKILL.md")
            continue
        fields, _ = parse(md.read_text(encoding="utf-8"))
        if args.batch is not None and fields.get("batch") != str(args.batch):
            continue
        checked += 1
        errors += validate(md)
        if fields.get("type") in {"script-backed", "checker"}:
            script_backed.append(folder.name)

    for skill in script_backed:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "skill_tools.py"), skill, "--self-test"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        output = result.stdout.strip()
        print(output)
        record_result(output)
        if result.returncode != 0 and "BLOCKED" not in output:
            errors.append(f"{skill}: self-test failed: {output or result.stderr.strip()}")

    svg_test = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "svg_scene_builder.py"), "--self-test"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    svg_output = svg_test.stdout.strip()
    print(svg_output)
    record_result(svg_output)
    if svg_test.returncode != 0 and "BLOCKED" not in svg_output:
        errors.append(f"svg-scene-builder: self-test failed: {svg_output or svg_test.stderr.strip()}")

    expected_results = len(script_backed) + 1
    if passed + blocked != expected_results:
        errors.append(f"self-test result count: expected {expected_results} final results, got {passed} PASS + {blocked} BLOCKED")

    print()
    if errors:
        print(f"FAIL: {len(errors)} problem(s) in {checked} skills")
        for error in errors:
            print(" - " + error)
        return 1
    print(f"PASS: {checked} skills validated, {passed} self-tests passed, {blocked} blocked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
