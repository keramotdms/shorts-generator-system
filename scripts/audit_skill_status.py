#!/usr/bin/env python3
"""Full 94-skill audit: count REAL vs TEMPLATE skills and print category totals.

A skill is TEMPLATE when any of these is true:
  * its Steps still contain the generator's generic prompt wording
  * it has fewer than 3 numbered Steps
  * it has no concrete output path under projects/<project>/, config/, assets/ or scripts/

Everything else is REAL. The separate tests/test_no_template.py applies the
stricter anti-fake rules to the 55 skills rewritten in batches A-D.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".opencode" / "skills"
GENERIC = "Follow this skill's prompt instructions"
OUTPUT_HINT = re.compile(r"(projects/<project>/|config/|assets/|scripts/)")


def classify(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8")
    name = path.parent.name
    category = "unknown"
    for line in text.splitlines():
        if line.startswith("category: "):
            category = line.split(":", 1)[1].strip()
            break
    steps = text.split("# Steps", 1)[-1].split("# How to test", 1)[0]
    numbered = [line for line in steps.splitlines() if re.match(r"^\s*\d+\.", line)]
    reasons: list[str] = []
    if GENERIC in steps:
        reasons.append("generic prompt wording")
    if len(numbered) < 3:
        reasons.append("fewer than 3 numbered steps")
    if not OUTPUT_HINT.search(steps):
        reasons.append("no concrete output path in Steps")
    return ("TEMPLATE" if reasons else "REAL", category, "; ".join(reasons))


def main() -> int:
    total = Counter()
    by_category: dict[str, Counter] = {}
    failures: list[tuple[str, str]] = []
    for folder in sorted(SKILLS.iterdir()):
        if not folder.is_dir() or not (folder / "SKILL.md").is_file():
            continue
        status, category, reason = classify(folder / "SKILL.md")
        total[status] += 1
        by_category.setdefault(category, Counter())[status] += 1
        if status == "TEMPLATE":
            failures.append((folder.name, reason))

    print(f"FULL SKILL AUDIT: {sum(total.values())} skills")
    print(f"REAL: {total['REAL']} | TEMPLATE: {total['TEMPLATE']}")
    print()
    print(f"{'category':<16} {'REAL':>5} {'TEMPLATE':>9}")
    for category in sorted(by_category):
        row = by_category[category]
        print(f"{category:<16} {row['REAL']:>5} {row['TEMPLATE']:>9}")
    for name, reason in failures:
        print(f" - {name}: {reason}")
    if total["TEMPLATE"] == 0 and total["REAL"] == 94:
        print("PASS: 94 REAL / 0 TEMPLATE")
        return 0
    print("FAIL: expected 94 REAL / 0 TEMPLATE")
    return 1


if __name__ == "__main__":
    sys.exit(main())
