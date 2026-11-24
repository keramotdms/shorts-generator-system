#!/usr/bin/env python3
"""Fail if any skill output is missing a format, uses an unknown profile,
disagrees with another skill about the same file, or is undocumented.

Run with the other repository tests.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "config" / "skill-contracts.json"
FORMATS = ROOT / "config" / "output-formats.json"
SKILLS = ROOT / ".opencode" / "skills"


def split_paths(value: str) -> list[str]:
    return [part.strip() for part in value.split(" + ") if part.strip()]


def main() -> int:
    errors: list[str] = []
    contracts = json.loads(CONTRACTS.read_text(encoding="utf-8"))
    registry = json.loads(FORMATS.read_text(encoding="utf-8"))
    profiles = registry.get("profiles", {})
    skills = contracts.get("skills", {})
    if not isinstance(profiles, dict) or not profiles:
        print("FAIL: config/output-formats.json has no profiles")
        return 1

    declarations: list[tuple[str, str, str]] = []
    total_outputs = 0

    for name, entry in skills.items():
        outputs = split_paths(entry.get("output", ""))
        declared = entry.get("format")
        total_outputs += len(outputs)
        if not isinstance(declared, dict) or not declared:
            errors.append(f"{name}: no format declared for any output")
            continue
        if set(declared) != set(outputs):
            errors.append(
                f"{name}: format paths do not match output paths "
                f"(missing={sorted(set(outputs) - set(declared))}, "
                f"extra={sorted(set(declared) - set(outputs))})"
            )
        for path, profile in declared.items():
            declarations.append((name, str(path), str(profile)))
            if profile not in profiles:
                errors.append(f"{name}: unknown profile {profile!r} for {path}")
                continue
            extension = profiles[profile].get("extension")
            if extension and not path.endswith("/") and not path.lower().endswith(str(extension)):
                errors.append(
                    f"{name}: {path} uses profile {profile} which requires {extension}"
                )
            md = SKILLS / name / "SKILL.md"
            if not md.is_file():
                errors.append(f"{name}: missing SKILL.md")
                continue
            body = md.read_text(encoding="utf-8")
            all_format_lines = [
                line for line in body.splitlines() if line.startswith("- Format `")
            ]
            if len(all_format_lines) != len(outputs):
                errors.append(
                    f"{name}: SKILL.md has {len(all_format_lines)} format lines "
                    f"for {len(outputs)} declared outputs"
                )
            matches = [
                line for line in body.splitlines()
                if line.startswith("- Format `") and profile in line and path in line
            ]
            if len(matches) != 1:
                errors.append(
                    f"{name}: SKILL.md has {len(matches)} format lines for "
                    f"{path} ({profile}), expected exactly 1"
                )

    by_path: dict[str, set[str]] = defaultdict(set)
    for _name, path, profile in declarations:
        by_path[path].add(profile)
    for path, values in sorted(by_path.items()):
        if len(values) > 1:
            errors.append(f"conflicting formats for {path}: {sorted(values)}")

    print(f"Format audit: {len(skills)} skills, {total_outputs} outputs, {len(profiles)} profiles")
    if errors:
        print(f"FAIL: {len(errors)} format problem(s)")
        for error in errors:
            print(" - " + error)
        return 1
    print("PASS: every output has one known format, documents it and agrees with every writer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
