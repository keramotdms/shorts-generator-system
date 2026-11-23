#!/usr/bin/env python3
"""Rewrite audited TEMPLATE skills into REAL skills, one batch at a time.

Every spec below carries skill-specific criteria, a filled example, quality
rules and unique Steps. Running a batch writes the SKILL.md files and syncs
skill-contracts.json and docs/SKILL-INDEX.md. It never touches .env.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_skill_scaffolds import SKILLS, ROOT, SKILLS_DIR, meta

CONTRACTS = ROOT / "config" / "skill-contracts.json"
INDEX = ROOT / "docs" / "SKILL-INDEX.md"
META = {row[0]: row for row in SKILLS}
STAMP_TIME = "2026-11-23T10:00:00Z"


def scored(*rows: tuple[str, float, str]) -> list[dict]:
    return [{"name": name, "score": score, "evidence": evidence} for name, score, evidence in rows]


def actions(*rows: tuple[int, str, float, float, str]) -> list[dict]:
    return [
        {"id": i, "action": action, "start_sec": start, "end_sec": end, "reason": reason}
        for i, action, start, end, reason in rows
    ]


def candidates(*rows: tuple[str, float, str]) -> list[dict]:
    return [{"id": cid, "score": score, "reason": reason} for cid, score, reason in rows]


def entries(*rows: tuple[str, int, str, str]) -> list[dict]:
    return [
        {"path": path, "version": version, "purpose": purpose, "state": state}
        for path, version, purpose, state in rows
    ]


def stamp(spec: dict) -> dict:
    data = {
        "status": "PASS",
        "skill": spec["name"],
        "project": "_template",
        "generated_at": STAMP_TIME,
        "language": "bn",
    }
    data.update(spec["example"])
    return data


def render(spec: dict) -> str:
    name = spec["name"]
    _n, category, subcategory, purpose, _input_text, output, depends = META[name]
    _status, phase = meta(name)
    kind = "script-backed" if spec.get("ffmpeg") else "prompt-only"
    batch = BATCH_OF[name]

    header = [
        "---",
        f"name: {name}",
        f"description: {spec['description']}",
        f"category: {category}",
    ]
    if subcategory:
        header.append(f"subcategory: {subcategory}")
    header += [
        f"status: implemented",
        f"phase: {phase}",
        f"type: {kind}",
        f"batch: {batch}",
        f"schema: {spec['schema']}",
    ]
    if spec.get("ffmpeg"):
        header.append("requires: ffmpeg")
    if spec.get("api_needed"):
        header.append("api_needed: later")
        header.append("data_source: manual-file")
    header.append("---")

    body: list[str] = [
        "> Context is always loaded via project-memory; all generated data lives under projects/<project>/.",
        "",
        "# When to use",
        "",
        spec["when"],
        "",
        "# Purpose",
        "",
        spec["purpose"],
        "",
        "# Input",
        "",
    ]
    for item in spec["inputs"]:
        body.append(item if item.startswith("- ") else f"- {item}")
    body += [
        "- `config/channel.json` and `config/style-bible.json`, read through project-memory",
        "- `PROJECT` environment variable (defaults to `_template`)",
        "",
        "# Output",
        "",
        f"- `{output}`",
        "- `status`, `skill`, `project` and `generated_at` are written into the JSON output",
        "",
        spec.get("criteria_heading", "# Selection/scoring criteria"),
        "",
    ]
    for index, item in enumerate(spec["criteria"], start=1):
        body.append(f"{index}. {item}")
    body += [
        "",
        "# Output format (short example)",
        "",
        f"Schema: `config/schemas/{spec['schema']}.json`",
        "",
        "```json",
        json.dumps(stamp(spec), ensure_ascii=False, indent=2),
        "```",
        "",
        "# Quality rules",
        "",
    ]
    for index, rule in enumerate(spec["quality"], start=1):
        body.append(f"{index}. {rule}")
    body += ["", "# Steps", ""]
    for index, step in enumerate(spec["steps"], start=1):
        body.append(f"{index}. {step}")
    body += [
        "",
        "# How to test",
        "",
        f"- {spec['test']}",
        "- Run `python tests/test_no_template.py` and confirm this skill is not listed.",
        f"- The filled example above is validated against `config/schemas/{spec['schema']}.json` by `tests/test_no_template.py`.",
        "",
        "# Depends on / feeds into",
        "",
        depends,
        "",
        "# Failure handling",
        "",
        spec["failure"],
        "",
    ]
    return "\n".join(header + [""] + body)


def sync_registry(names: list[str]) -> None:
    contracts = json.loads(CONTRACTS.read_text(encoding="utf-8"))
    skills = contracts.get("skills", {})
    for name in names:
        if name not in skills:
            continue
        row = META[name]
        spec = SPECS[name]
        skills[name]["status"] = "implemented"
        skills[name]["type"] = "script-backed" if spec.get("ffmpeg") else "prompt-only"
        skills[name]["batch"] = BATCH_OF[name]
        skills[name]["schema"] = spec["schema"]
        if spec.get("ffmpeg"):
            skills[name]["requires"] = "ffmpeg"
        if spec.get("api_needed"):
            skills[name]["api_needed"] = "later"
            skills[name]["input"] = (
                f"projects/<project>/10-publish/inputs/ (manual export; no API access)"
            )
    CONTRACTS.write_text(json.dumps(contracts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = INDEX.read_text(encoding="utf-8").splitlines()
    for pos, line in enumerate(lines):
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and cells[0] in names:
            cells[3] = "implemented"
            lines[pos] = "| " + " | ".join(cells) + " |"
    INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


BATCHES: dict[str, list[str]] = {
    "A": [
        "story-organizer", "retention-pacing-optimizer", "script-user-tester",
        "voiceover-organizer", "pronunciation-emotion-director", "music-sfx-selector",
        "character-thinker-counter", "character-organizer", "expression-pose-library",
        "element-designer", "element-organizer", "lipsync-motion-planner",
        "cut-rhythm-editor", "broll-variety-planner", "red-team",
    ],
    "B": [
        "audience-persona-builder", "competitor-analyzer", "content-calendar",
        "fact-checker", "localization", "loop-cta-designer",
        "character-setup-manager", "script-video-voice-collector",
    ],
    "C": [
        "animator", "beat-sync-editor", "branding-manager", "color-grading-keeper",
        "emphasis-sticker-placer", "hook-visual-editor", "intro-outro-manager",
        "motion-graphic-editor", "pattern-interrupt-inserter", "preview-frame-extractor",
        "seamless-loop-editor", "sfx-timing-placer", "stock-asset-finder",
        "template-preset-manager", "thumbnail-designer", "variant-batch-renderer",
        "video-editor", "virtual-camera-planner", "watermark-logo-placer",
    ],
    "D": [
        "ruthless-team", "solver", "copywriter", "marketing-specialist",
        "seo-specialist", "ab-tester", "analytics-feedback-loop",
        "comment-community-manager", "cross-platform-repurposer",
        "monetization-tracker", "scheduler-publisher", "youtube-analyst",
        "youtube-seo-specialist",
    ],
}

SPECS: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Batch A — script, voice, character, scene and early edit
# ---------------------------------------------------------------------------

SPECS["story-organizer"] = {
    "name": "story-organizer",
    "description": "Turns story beats into timed 9:16 scenes with one job each.",
    "purpose": "Convert a loose story concept into a timed beat sheet where every scene has a single job and fits the 30–60 second Short format.",
    "when": "Use after story-thinker when the concept exists but nobody has decided which beat goes where or how many seconds each beat gets.",
    "inputs": ["- `projects/<project>/02-script/story.json`", "- `config/channel.json` video length range"],
    "schema": "plan",
    "criteria_heading": "# Beat timing criteria",
    "criteria": [
        "Use at most 4 beats for a 30-second video and at most 6 beats for a 60-second video.",
        "Give each beat 5–12 seconds; no beat may be shorter than 5 seconds.",
        "Assign exactly one job per beat: hook, problem, turn, payoff or closure.",
        "Sum every `start_sec`/`end_sec` pair to the channel's 30–60 second target.",
        "Describe each beat with one visual idea that the SVG scene builder can draw with flat shapes.",
    ],
    "example": {
        "items": actions(
            (1, "Coffee price joke", 0, 7, "hook in the first 3 seconds"),
            (2, "Monthly total appears", 7, 18, "raise the money problem"),
            (3, "Side hustle notebook", 18, 34, "show the turn"),
            (4, "First ৳500 saved", 34, 45, "payoff and loop back"),
        ),
        "constraints": ["flat 2D shapes only", "Bangla narration", "vertical 9:16"],
        "summary": "Four beats totalling 45 seconds, each with one visual job.",
    },
    "quality": [
        "Every item has a unique id and both timing fields present.",
        "No beat duration is under 5 or over 12 seconds.",
        "The constraints include the language read from project-memory, never a hardcoded language word.",
    ],
    "steps": [
        "Load niche, language and the 30–60 second range through project-memory before reading the story file.",
        "Validate `projects/<project>/02-script/story.json` against `config/schemas/story.json` and stop on any schema error.",
        "Rebuild the beat list from `story.json`, giving each beat one job and a 5–12 second window.",
        "Check the total against the channel video-length range; merge or split beats until it fits.",
        "Write the timed plan to `projects/<project>/02-script/story-organizer.json` with status and project metadata.",
        "Validate the written file against `config/schemas/plan.json` and log any failure via error-log-keeper.",
    ],
    "test": "Run `python tests/test_skills.py --batch 3` then `python tests/test_no_template.py`; expect this skill absent from the template list.",
    "failure": "If the story file is missing or fails its schema, stop without writing a beat sheet and report the exact path. If the beats cannot fit 30–60 seconds, return a WARN with the overrun in seconds instead of inventing timings.",
}

SPECS["retention-pacing-optimizer"] = {
    "name": "retention-pacing-optimizer",
    "description": "Tightens script pacing with timed cut targets for Shorts.",
    "purpose": "Score a draft script for attention decay and return a timed re-cut plan that removes dead air without changing the script's meaning.",
    "when": "Use after script-writer when the script is complete but the first 3 seconds feel slow or scenes run too long for a Short.",
    "inputs": ["- `projects/<project>/02-script/latest_script.json`", "- `config/channel.json` length_sec range"],
    "schema": "plan",
    "criteria_heading": "# Pacing score criteria",
    "criteria": [
        "The hook must land by 2.5 seconds; if it starts later, score that criterion 0/10.",
        "No more than 4 consecutive seconds may pass without a new visual or text change.",
        "Score each line 0–10 for novelty, stakes and clarity; any line below 6 is a cut candidate.",
        "Target 2.8–3.5 words per second for Bangla narration measured from the script duration fields.",
        "Keep the final 5 seconds for a loop or call to action; never delete it.",
    ],
    "example": {
        "items": actions(
            (1, "Move the salary number into the hook", 0, 2, "hook originally started at 4.2 seconds"),
            (2, "Trim the greeting line", 2, 6, "no new information for 4 seconds"),
            (3, "Add a wallet graphic on the totals line", 6, 14, "visual change every 4 seconds"),
        ),
        "constraints": ["hook by 2.5 seconds", "Bangla speech rate 2.8-3.5 words/sec", "loop kept in final 5 seconds"],
        "summary": "Three timed edits lift the hook forward and add one visual change; total 45 seconds preserved.",
    },
    "quality": [
        "Each item names the exact line number from the source script.",
        "The sum of kept durations stays inside the channel length range.",
        "No rule hardcodes English; word-rate guidance is written for Bangla.",
    ],
    "steps": [
        "Read language and target duration through project-memory, then load `projects/<project>/02-script/latest_script.json`.",
        "Validate the draft with `python scripts/schema_validator.py latest_script projects/<project>/02-script/latest_script.json`.",
        "Score every scene line on novelty, stakes and clarity using the 0–10 scale.",
        "Locate gaps longer than 4 seconds and propose a visual change or a trim for each one.",
        "Write the timed edit list to `projects/<project>/02-script/retention-pacing-optimizer.json`.",
        "Re-check the total runtime and validate the file against `config/schemas/plan.json`.",
    ],
    "test": "Run `python scripts/schema_validator.py plan projects/_template/02-script/retention-pacing-optimizer.json` after a real run, then `python tests/test_no_template.py`.",
    "failure": "If the script has no duration fields, return WARN and ask for timings instead of guessing a word rate. On schema failure, stop and name the invalid scene index.",
}

SPECS["script-user-tester"] = {
    "name": "script-user-tester",
    "description": "Runs a manual viewer feedback round on a draft script.",
    "purpose": "Collect structured feedback from at least five manually recruited viewers and turn it into a scored script usability report before voice recording.",
    "when": "Use when a script is ready for a small human read-through and you have collected viewer answers into a local JSON file.",
    "inputs": [
        "- `projects/<project>/02-script/inputs/viewer-feedback.json` (manual; min 5 viewers, fields: viewer, understood_hook, confusion, would_watch)",
        "- `projects/<project>/02-script/latest_script.json`",
    ],
    "schema": "analysis",
    "criteria_heading": "# Viewer scoring criteria",
    "criteria": [
        "Require at least 5 responses; fewer than 5 is a WARN, not a PASS.",
        "At least 4 of 5 viewers must answer `understood_hook: true`, otherwise the hook fails.",
        "Average `would_watch` must be 4 or higher on a 1–5 scale.",
        "Group every `confusion` string by scene and flag any scene named by 2 or more viewers.",
        "Quote Bangla feedback verbatim; do not translate it into another language in the report.",
    ],
    "example": {
        "source_file": "projects/<project>/02-script/inputs/viewer-feedback.json",
        "criteria": scored(
            ("hook understood", 8, "4 of 5 viewers answered true"),
            ("would watch", 8, "average 4.2 out of 5"),
            ("scene clarity", 6, "scene 3 named by 2 viewers"),
        ),
        "findings": ["Scene 3 lists three numbers at once; split it.", "Bangla hook line was understood without explanation."],
        "summary": "Five manual viewers tested; hook passes, scene 3 needs one simplification.",
    },
    "quality": [
        "The report states the exact number of responses used.",
        "Every score is between 0 and 10 and has a quoted evidence string.",
        "The report never claims automated or API-based viewer collection.",
    ],
    "steps": [
        "Confirm the manual export exists at `projects/<project>/02-script/inputs/viewer-feedback.json`.",
        "Validate the draft script with the latest_script schema before reading feedback about it.",
        "Count responses and refuse to score if fewer than five are present.",
        "Compute hook understanding, average would_watch and per-scene confusion counts.",
        "Write the scored report to `projects/<project>/02-script/script-user-tester.json`.",
        "Validate the report against `config/schemas/analysis.json` and preserve Bangla quotes.",
    ],
    "test": "Save five sample responses in `projects/_template/02-script/inputs/viewer-feedback.json`, run the skill, then `python tests/test_no_template.py`.",
    "failure": "Never fabricate viewer responses. If the input file is missing, report its exact path and stop with WARN instead of producing a fake report.",
}

SPECS["voiceover-organizer"] = {
    "name": "voiceover-organizer",
    "description": "Plans narrator gender, scene order and line lengths.",
    "purpose": "Produce a voice plan that fixes the narrator, speaking order and per-scene word budget before any audio is generated.",
    "when": "Use after the script is locked and before voiceover-generator, when the narrator voice and scene reading order are still undecided.",
    "inputs": ["- `projects/<project>/02-script/latest_script.json`", "- `config/style-bible.json` voice.default_gender"],
    "schema": "plan",
    "criteria_heading": "# Voice plan criteria",
    "criteria": [
        "Use exactly one narrator for the whole Short; a second voice requires a new project.",
        "Take gender from `voice.default_gender` in the style bible instead of choosing it here.",
        "Keep each scene to at most 18 Bangla words so it fits one breath.",
        "Order scenes by the script's beat order, never by file name.",
        "Reserve the last scene for the loop line and mark it as the final item.",
    ],
    "example": {
        "items": actions(
            (1, "Narrate hook: one coffee costs ৳120", 0, 6, "12 Bangla words, under 18"),
            (2, "Narrate monthly total", 6, 18, "16 Bangla words"),
            (3, "Narrate loop line", 38, 45, "reserved final 7 seconds"),
        ),
        "constraints": ["one narrator", "gender from style bible", "max 18 Bangla words per scene"],
        "summary": "Single male narrator reads three grouped scenes in beat order with a reserved loop line.",
    },
    "quality": [
        "The gender string matches the style bible value exactly.",
        "No item contains more than 18 words when split on whitespace.",
        "Items follow the numeric order of script scenes.",
    ],
    "steps": [
        "Read the voice block from `config/style-bible.json` through project-memory.",
        "Validate `projects/<project>/02-script/latest_script.json` against its schema.",
        "Count words per scene and group adjoining short scenes into one reading unit.",
        "Assign the style-bible gender to the single narrator and mark the last scene as the loop line.",
        "Write the plan to `projects/<project>/03-voice/voiceover-organizer.json`.",
        "Validate against `config/schemas/plan.json` and report any scene over 18 words.",
    ],
    "test": "Run `python scripts/schema_validator.py plan projects/_template/03-voice/voiceover-organizer.json` then `python tests/test_no_template.py`.",
    "failure": "If the style bible has no voice.default_gender, stop and ask project-memory to regenerate it. Never default to a gender based on the creator's name.",
}

SPECS["pronunciation-emotion-director"] = {
    "name": "pronunciation-emotion-director",
    "description": "Adds Bangla pronunciation and emotion cues per line.",
    "purpose": "Attach pronunciation, emphasis and emotion notes to every spoken line so the voiceover sounds natural in Bangla.",
    "when": "Use after voiceover-organizer and before voiceover-generator when numbers, loanwords or emotionally flat lines need reading notes.",
    "inputs": ["- `projects/<project>/03-voice/voiceover-organizer.json`", "- `projects/<project>/02-script/latest_script.json`"],
    "schema": "plan",
    "criteria_heading": "# Delivery criteria",
    "criteria": [
        "Write every pronunciation note in Bangla script for Bangla lines; use Latin only for brand names.",
        "Spell out currency and numbers as words, for example ৳120 as 'একশ কুড়ি টাকা'.",
        "Assign exactly one emotion per line from: calm, curious, worried, hopeful.",
        "Mark at most one emphasized word per sentence to avoid a shouty delivery.",
        "Keep the emotion of the final line consistent with the loop plan.",
    ],
    "example": {
        "items": actions(
            (1, "Read ৳120 as একশ কুড়ি টাকা", 0, 6, "number would otherwise be mispronounced"),
            (2, "Emotion worried on the debt line", 6, 18, "sets up the problem"),
            (3, "Emotion hopeful on the saving line", 38, 45, "matches the loop ending"),
        ),
        "constraints": ["Bangla script for pronunciation", "one emotion per line", "one emphasized word maximum"],
        "summary": "Three delivery notes cover number reading, a worried turn and a hopeful loop line.",
    },
    "quality": [
        "Every `action` string contains either a Bangla word or an allowed brand name.",
        "No line carries two emotion labels.",
        "The plan uses the same scene ids as the voice plan.",
    ],
    "steps": [
        "Load language from project-memory and confirm it is Bangla before writing Bangla script notes.",
        "Open `projects/<project>/03-voice/voiceover-organizer.json` and the validated script.",
        "Rewrite every number and currency amount as spoken Bangla words.",
        "Choose one emotion from the allowed four and one emphasis word per sentence.",
        "Write the delivery notes to `projects/<project>/03-voice/pronunciation-emotion-director.json`.",
        "Validate against `config/schemas/plan.json` and flag any line with two emotions.",
    ],
    "test": "Run `python tests/test_skills.py --batch 4`, then validate `projects/_template/03-voice/pronunciation-emotion-director.json` with the plan schema.",
    "failure": "If the script language is not Bangla, stop and report that this skill only covers Bangla delivery. Never transliterate Bangla lines into Latin text.",
}

SPECS["music-sfx-selector"] = {
    "name": "music-sfx-selector",
    "description": "Chooses licensed-safe music and SFX cues.",
    "purpose": "Select a background music track and a short sound-effect list that fit the scene mood while staying inside the mixer's gain budget.",
    "when": "Use after the scene plan exists and before audio-mixer, when the video needs a music bed and a few accent sounds.",
    "inputs": ["- `projects/<project>/05-scene/scenario-designer.json`", "- `assets/music/` (local files you already own)"],
    "schema": "selection",
    "criteria_heading": "# Selection criteria",
    "criteria": [
        "Choose at most one music bed and at most three SFX cues for a 60-second Short.",
        "Only list files that exist in `assets/music/` or `assets/sfx/`; never invent a file name.",
        "Reject any track whose license is unknown; write `license: unknown` as a FAIL reason.",
        "Keep music under 0.2 relative gain so narration stays intelligible.",
        "Place SFX at most 2 per 10 seconds to avoid clutter.",
    ],
    "example": {
        "candidates": candidates(
            ("assets/music/soft-tabla.mp3", 9, "owned track, calm mood, 42 seconds"),
            ("assets/music/loud-drums.mp3", 3, "no license note; rejected"),
            ("assets/sfx/coin.mp3", 8, "owned cue for the saving payoff"),
        ),
        "chosen_id": "assets/music/soft-tabla.mp3",
        "rationale": "Owned calm tabla bed plus one coin cue fits the 0.2 gain budget and the scene mood.",
    },
    "quality": [
        "Every candidate id is an existing local path.",
        "The chosen id appears in the candidate list.",
        "The rationale names the relative gain budget from the criteria.",
    ],
    "steps": [
        "Read the scene mood from `config/style-bible.json` through project-memory.",
        "List files actually present in `assets/music/` and `assets/sfx/`.",
        "Score each file against mood, licence clarity and the 0.2 gain budget.",
        "Cap the shortlist at one bed and three cues and pick the highest scoring bed.",
        "Write the selection to `projects/<project>/05-scene/music-sfx-selector.json`.",
        "Validate against `config/schemas/selection.json` and confirm every id is a local file.",
    ],
    "test": "Place one owned mp3 in `assets/music/`, run the skill, then `python tests/test_no_template.py`.",
    "failure": "If no licensed local file exists, write a WARN selection with an empty shortlist and tell the user to add an owned file. Never download or stream music in this skill.",
}

SPECS["character-thinker-counter"] = {
    "name": "character-thinker-counter",
    "description": "Brainstorms and scores character ideas before design.",
    "purpose": "Generate five character concepts from the script and style bible, then shortlist three using a fixed score so design work starts with a clear choice.",
    "when": "Use after the script and voice plan are ready and before character-designer, when you need exactly one creator character to draw.",
    "inputs": ["- `config/style-bible.json`", "- `projects/<project>/02-script/latest_script.json`"],
    "schema": "selection",
    "criteria_heading": "# Character score criteria",
    "criteria": [
        "Produce exactly five candidates before scoring; shortlist exactly three.",
        "Score on 0–10 for recognisable silhouette, flat-shape simplicity and audience fit.",
        "Reject any candidate that needs fine detail, gradients or photo texture.",
        "Keep the default character from the style bible as one candidate.",
        "Give every candidate a stable id in the form `creator-01` without spaces.",
    ],
    "example": {
        "candidates": candidates(
            ("creator-01", 9, "style-bible default; round face, simple shirt"),
            ("creator-02", 7, "glasses add detail but still flat"),
            ("creator-03", 5, "needs hair texture; rejected"),
            ("creator-04", 8, "distinct cap silhouette"),
            ("creator-05", 6, "too close to creator-01"),
        ),
        "chosen_id": "creator-01",
        "rationale": "Highest score on silhouette and flat-shape simplicity; matches the style-bible default.",
    },
    "quality": [
        "There are exactly five candidates and the chosen id is one of them.",
        "Every id matches the lowercase-kebab pattern.",
        "No reason mentions photorealism or gradient shading.",
    ],
    "steps": [
        "Load the character block and palette from `config/style-bible.json` via project-memory.",
        "Read the narrator description from the validated script.",
        "Draft five distinct silhouettes using only flat shapes from the palette.",
        "Score each candidate on silhouette, simplicity and audience fit.",
        "Write the shortlist to `projects/<project>/04-character/character-thinker-counter.json`.",
        "Validate against `config/schemas/selection.json` and check id format.",
    ],
    "test": "Run `python tests/test_skills.py --batch 5`, then validate the written selection with the selection schema.",
    "failure": "If the style bible has no character block, stop and ask project-memory to regenerate it rather than inventing a look. If fewer than five ideas exist, report WARN with the count.",
}

SPECS["character-organizer"] = {
    "name": "character-organizer",
    "description": "Indexes character JSON files and their references.",
    "purpose": "Keep one canonical JSON file per character id and produce an inventory that maps every file to its purpose and version.",
    "when": "Use after character-thinker-counter and before character-designer, when several character files and PNG sheets start accumulating in assets/characters/.",
    "inputs": ["- `assets/characters/*.json`", "- `projects/<project>/04-character/character-thinker-counter.json`"],
    "schema": "inventory",
    "criteria_heading": "# Naming and version rules",
    "criteria": [
        "One JSON file per character id; duplicate ids are a FAIL.",
        "File name must equal the `id` field plus `.json`, in lowercase-kebab-case.",
        "Every expression PNG must be named `<id>-<expression>.png` with expression from neutral, smile or surprised.",
        "Increment `version` only when the character JSON changes, not when a PNG is regenerated.",
        "Mark superseded files as `archive`, never delete them silently.",
    ],
    "example": {
        "entries": entries(
            ("assets/characters/creator-01.json", 1, "canonical look from the shortlist", "active"),
            ("assets/characters/creator-01-smile.png", 1, "smile expression sheet", "active"),
            ("assets/characters/creator-00.json", 1, "old draft kept for reference", "archive"),
        ),
        "summary": "Three character files indexed; one active id and one archived draft.",
    },
    "quality": [
        "Each path exists on disk at the time of the run.",
        "Version numbers are positive integers.",
        "No two active entries share the same character id.",
    ],
    "steps": [
        "Load the shortlist ids from `projects/<project>/04-character/character-thinker-counter.json`.",
        "List every JSON and PNG under `assets/characters/` without following links.",
        "Compare each file name to its `id` field and record mismatches as FAIL entries.",
        "Assign version numbers from the existing file metadata or start at 1.",
        "Write the inventory to `projects/<project>/04-character/character-organizer.json`.",
        "Validate against `config/schemas/inventory.json` and report duplicate ids.",
    ],
    "test": "Run `python scripts/svg_scene_builder.py sample`, then `python tests/test_no_template.py` to check the inventory output.",
    "failure": "If two files claim the same character id, write a FAIL inventory listing both exact paths and stop before character-designer runs.",
}

SPECS["expression-pose-library"] = {
    "name": "expression-pose-library",
    "description": "Defines reusable expressions and poses for SVG rendering.",
    "purpose": "Publish the exact expression and pose vocabulary that scripts/svg_scene_builder.py can draw, so scene prompts never ask for unsupported art.",
    "when": "Use after character-organizer and before scenario-designer, when scene prompts need to name a facial expression or body pose.",
    "inputs": ["- `assets/characters/<character-id>.json`", "- `scripts/svg_scene_builder.py`"],
    "schema": "inventory",
    "criteria_heading": "# Library rules",
    "criteria": [
        "Exactly three expressions are supported: neutral, smile, surprised.",
        "Exactly four poses are supported: idle, wave, point, think.",
        "Each entry path must point to an SVG or PNG produced by the SVG builder.",
        "Reject any entry whose name needs fine detail such as fingers or eyebrow texture.",
        "Record the builder script version as the entry purpose prefix.",
    ],
    "example": {
        "entries": entries(
            ("assets/characters/creator-01-neutral.png", 1, "svg-builder expression neutral", "active"),
            ("assets/characters/creator-01-smile.png", 1, "svg-builder expression smile", "active"),
            ("assets/characters/creator-01-surprised.png", 1, "svg-builder expression surprised", "active"),
            ("assets/scenes/pose-point-preview.png", 1, "svg-builder pose point", "active"),
        ),
        "summary": "Three expressions and one pose preview registered for the scene prompt writer.",
    },
    "quality": [
        "Only the seven allowed expression and pose names appear.",
        "Every entry path ends in .svg or .png.",
        "The library never lists an expression that the builder cannot render.",
    ],
    "steps": [
        "Read the palette and character id from `assets/characters/<character-id>.json` after schema validation.",
        "Query the builder's expression and pose alias tables by reading `scripts/svg_scene_builder.py`.",
        "Generate one PNG per expression with the builder if the file is missing.",
        "Register each generated file with its builder version and state.",
        "Write the library to `projects/<project>/04-character/expression-pose-library.json`.",
        "Validate against `config/schemas/inventory.json` and reject unknown names.",
    ],
    "test": "Run `python scripts/svg_scene_builder.py sample`, then validate `projects/_template/04-character/expression-pose-library.json` with the inventory schema.",
    "failure": "If a requested expression is not one of the three supported names, report the unsupported name and substitute neutral with a WARN instead of failing the render.",
}

SPECS["element-designer"] = {
    "name": "element-designer",
    "description": "Designs flat reusable scene elements.",
    "purpose": "Define a small set of flat 2D scene elements drawn from the style-bible palette so every scene can reuse them without new art.",
    "when": "Use after the character is approved and before scenario-designer, when a scene needs a desk, wallet, phone or notebook prop.",
    "inputs": ["- `config/style-bible.json` palette", "- `projects/<project>/02-script/latest_script.json`"],
    "schema": "inventory",
    "criteria_heading": "# Element design rules",
    "criteria": [
        "Design at most 6 elements for one Short.",
        "Use only the four palette colours from the style bible plus white and gray for floors.",
        "Draw with rect, circle and path only; no gradient, blur or image texture.",
        "Each element must be recognisable at 1080x1920 and occupy at least 100 pixels on one axis.",
        "Name elements in lowercase-kebab-case such as `warm-desk-notebook`.",
    ],
    "example": {
        "entries": entries(
            ("assets/scenes/warm-desk-background.svg", 1, "desk and wall, flat palette shapes", "active"),
            ("assets/scenes/warm-desk-notebook.svg", 1, "notebook prop from the SVG builder", "active"),
            ("assets/scenes/wallet-prop.svg", 1, "wallet prop, draft", "draft"),
        ),
        "summary": "Three flat elements registered; two active and one draft awaiting script use.",
    },
    "quality": [
        "Every entry path is an .svg file under assets/scenes/.",
        "No entry description contains the word gradient or photo.",
        "The number of active entries is 6 or fewer.",
    ],
    "steps": [
        "Read the palette from `config/style-bible.json` through project-memory.",
        "Scan the validated script for prop words such as notebook, wallet or phone.",
        "Map each prop word to an existing SVG builder prop or describe a new flat-shape element.",
        "Check size and colour limits against the rules above.",
        "Write the element list to `projects/<project>/05-scene/element-designer.json`.",
        "Validate against `config/schemas/inventory.json` and count active entries.",
    ],
    "test": "Run `python scripts/svg_scene_builder.py sample`, then validate `projects/_template/05-scene/element-designer.json` with the inventory schema.",
    "failure": "If a prop needs texture or fine detail, record it as `draft` with the reason and substitute a simple flat shape rather than blocking the scene.",
}

SPECS["element-organizer"] = {
    "name": "element-organizer",
    "description": "Versions and indexes scene elements.",
    "purpose": "Assign versions to scene elements and keep one active index so scenario-designer always picks the current file.",
    "when": "Use after element-designer and before scenario-designer, when an element has been edited more than once or lives in several folders.",
    "inputs": ["- `projects/<project>/05-scene/element-designer.json`", "- `assets/scenes/*.svg`"],
    "schema": "inventory",
    "criteria_heading": "# Versioning rules",
    "criteria": [
        "Only one entry per element name may have state `active`.",
        "Bump version by 1 when the SVG bytes change; otherwise keep the existing number.",
        "Archive older files instead of deleting them so renders stay reproducible.",
        "Record the exact relative path, never an absolute Windows path.",
        "Sort entries by element name so the index is deterministic.",
    ],
    "example": {
        "entries": entries(
            ("assets/scenes/warm-desk-background.svg", 2, "active version after palette fix", "active"),
            ("assets/scenes/warm-desk-background-v1.svg", 1, "previous palette kept for rollback", "archive"),
            ("assets/scenes/warm-desk-notebook.svg", 1, "unchanged notebook prop", "active"),
        ),
        "summary": "Three versions indexed; one active background at version 2 and one archived original.",
    },
    "quality": [
        "No element name has two active entries.",
        "Every path starts with assets/scenes/.",
        "Version numbers increase by exactly 1 between successive states of one element.",
    ],
    "steps": [
        "Open `projects/<project>/05-scene/element-designer.json` and list current active files.",
        "Hash each SVG file and compare it with the recorded version to decide whether to bump.",
        "Rename superseded copies to a `-v<number>` suffix and mark them archive.",
        "Sort the resulting entries by name and write `projects/<project>/05-scene/element-organizer.json`.",
        "Validate against `config/schemas/inventory.json` and assert one active entry per name.",
        "Report any path that is absolute or missing from disk.",
    ],
    "test": "Run `python tests/test_skills.py --batch 5`, then validate `projects/_template/05-scene/element-organizer.json` with the inventory schema.",
    "failure": "If an SVG file is missing, keep its last known entry as archive and write a WARN with the path. Never invent a replacement file.",
}

SPECS["lipsync-motion-planner"] = {
    "name": "lipsync-motion-planner",
    "description": "Plans simple mouth and body motion from word timings.",
    "purpose": "Turn caption word timings into a minimal lip-sync and motion plan that the flat SVG character can actually perform.",
    "when": "Use after the collector and before video-maker, when a static character needs timed mouth opening and one simple body move per scene.",
    "inputs": ["- `projects/<project>/03-voice/captions.json`", "- `projects/<project>/05-scene/collection.json`"],
    "schema": "plan",
    "criteria_heading": "# Motion constraints",
    "criteria": [
        "Allow only two mouth states: open and closed; no phoneme-level shapes.",
        "Open the mouth only during a word interval from captions.json; never between words.",
        "Allow one body motion per scene from idle, wave, point or think.",
        "Keep motion events at least 1.5 seconds apart to stay readable at 9:16.",
        "Use the pose names from expression-pose-library exactly as written.",
    ],
    "example": {
        "items": actions(
            (1, "Mouth open onেকশ in scene 1", 0.4, 0.9, "word interval from captions"),
            (2, "Pose wave during the greeting scene", 2.0, 5.0, "one body motion per scene"),
            (3, "Mouth open on the saving line", 36.0, 37.2, "final payoff word"),
        ),
        "constraints": ["mouth states open/closed only", "poses idle/wave/point/think", "1.5 seconds between motions"],
        "summary": "Three timed cues derived from caption intervals and the supported pose list.",
    },
    "quality": [
        "Every cue start and end matches a caption interval in the source file.",
        "No unsupported pose name appears in any action.",
        "Body motions are at least 1.5 seconds apart.",
    ],
    "steps": [
        "Load language from project-memory and validate `projects/<project>/03-voice/captions.json`.",
        "Read the collection file to learn which character and scenes exist.",
        "Map caption word intervals to open-mouth windows, one per word.",
        "Choose one supported pose per scene and space body motions by at least 1.5 seconds.",
        "Write the plan to `projects/<project>/06-video/lipsync-motion-planner.json`.",
        "Validate against `config/schemas/plan.json` and cross-check every interval with captions.",
    ],
    "test": "Validate `projects/_template/06-video/lipsync-motion-planner.json` with the plan schema, then run `python tests/test_no_template.py`.",
    "failure": "If captions are missing or word timings are absent, report BLOCKED for motion planning and render the character in idle pose instead of guessing mouth movement.",
}

SPECS["cut-rhythm-editor"] = {
    "name": "cut-rhythm-editor",
    "description": "Re-times rough cuts for tighter rhythm.",
    "purpose": "Shorten a rough cut by trimming two halves of the source video and concatenating them, producing a tighter edit without re-encoding the whole scene set.",
    "when": "Use after rough-cut-assembler when the timeline is too slow but the scene order is correct.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `config/defaults.json` resolution and `config/style-bible.json` video length"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Rhythm parameters",
    "criteria": [
        "Read output width and height from `config/defaults.json` resolution, not from a hardcoded string.",
        "Trim the source at its measured midpoint, keeping the first 45% and the segment starting at 50%.",
        "Target an output duration of about 90% of the input duration.",
        "Re-encode with libx264 preset veryfast and pixel format yuv420p for Shorts compatibility.",
        "Verify the result with ffprobe and require duration between 1 and 60 seconds.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/cut-rhythm-editor.mp4",
        "duration_sec": 40.5,
        "width": 1080,
        "height": 1920,
        "has_audio": False,
        "parameters": {"trim_a": "0-20.25", "trim_b": "22.5-42.75", "target_ratio": 0.9, "video_codec": "libx264"},
        "summary": "Rough cut re-timed from 45 to 40.5 seconds using two trims and a concat filter.",
    },
    "quality": [
        "Output duration is between 85% and 95% of input duration.",
        "ffprobe confirms the resolution from defaults.json.",
        "No audio is silently dropped without being recorded in the report.",
    ],
    "steps": [
        "Load resolution from `config/defaults.json` and length limits from `config/style-bible.json` via project-memory.",
        "Require ffmpeg with `FFMPEG_PATH`; print BLOCKED and exit 0 if it is unavailable.",
        "Probe `projects/<project>/07-edit/rough-cut.mp4` for its exact duration.",
        "Build a two-trim concat filter using 45% and 50% offsets of that duration.",
        "Run the ffmpeg command and verify the result with ffprobe.",
        "Write the report to `projects/<project>/07-edit/cut-rhythm-editor.json` and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py cut-rhythm-editor --self-test` generates a tiny video, runs the trim-concat command and checks duration with ffprobe.",
    "failure": "If ffprobe reports a duration shorter than 2 seconds, skip the trims and copy the source with a WARN. On ffmpeg BLOCKED, report the FFMPEG_PATH hint and do not change Windows settings.",
}

SPECS["broll-variety-planner"] = {
    "name": "broll-variety-planner",
    "description": "Adds a flat B-roll overlay to a rough cut.",
    "purpose": "Place one local flat-shape image over a short window of the rough cut so a talking-head scene gains visual variety without stock footage.",
    "when": "Use after the scene plan and before final edit, when a scene stays visually static for more than 5 seconds.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `assets/scenes/*.png` local flat images"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# B-roll rules",
    "criteria": [
        "Use only images already present under assets/scenes/; never fetch stock footage.",
        "Scale the overlay to 270x480, which is one quarter of the 1080x1920 frame.",
        "Show the overlay for at most 40% of the video length.",
        "Position it at x=w-300 and y=120 so captions at the bottom stay clear.",
        "Verify with ffprobe that the output keeps the input resolution and duration.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/broll-variety-planner.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": True,
        "parameters": {"overlay": "assets/scenes/warm-desk-background.png", "scale": "270x480", "position": "w-300:120", "window_sec": 1.2},
        "summary": "One local flat image overlaid for 1.2 seconds on a 3 second test clip.",
    },
    "quality": [
        "The overlay path is a local PNG under assets/scenes/.",
        "Window length is 40% or less of the probed duration.",
        "ffprobe shows the same width and height as the input.",
    ],
    "steps": [
        "Read palette and resolution from project-memory sources `config/style-bible.json` and `config/defaults.json`.",
        "Require ffmpeg and stop with BLOCKED if `FFMPEG_PATH` is unavailable.",
        "Pick the first local PNG in `assets/scenes/` and probe the rough cut duration.",
        "Build an overlay filter that scales the image to 270x480 and enables it for 40% of the duration.",
        "Run ffmpeg with libx264 veryfast and keep the audio stream.",
        "Write the ffprobe summary to `projects/<project>/07-edit/broll-variety-planner.json`.",
    ],
    "test": "`python scripts/skill_tools.py broll-variety-planner --self-test` uses a generated PNG, runs the overlay command and probes width, height and duration.",
    "failure": "If no local PNG exists, report WARN and copy the input unchanged rather than downloading an image. On ffmpeg BLOCKED, print the FFMPEG_PATH hint only.",
}

SPECS["red-team"] = {
    "name": "red-team",
    "description": "Attacks the video to find weaknesses before release.",
    "purpose": "Challenge the final video from three hostile angles and return a scored weakness report with the strongest objection stated first.",
    "when": "Use after the final edit and before bug-finder, when you want an adversarial review rather than a friendly check.",
    "inputs": ["- `projects/<project>/08-final-test/final-video.mp4`", "- `projects/<project>/02-script/latest_script.json`"],
    "schema": "analysis",
    "criteria_heading": "# Attack criteria",
    "criteria": [
        "Attack exactly three angles: hook, trust and pacing.",
        "Score each angle 0–10 where 10 means the video fully resists that attack.",
        "Any angle scoring below 6 must have at least one concrete finding.",
        "Quote the exact second where the hook first makes sense.",
        "Write findings in the project language from project-memory, which is Bangla for this channel.",
    ],
    "example": {
        "criteria": scored(
            ("hook", 4, "the money figure appears at 4.2 seconds, after the required 3 seconds"),
            ("trust", 8, "every number is attributed to a stated saving example"),
            ("pacing", 6, "one 5-second static stretch at second 20"),
        ),
        "findings": ["Move the ৳120 figure into the first 2 seconds.", "Replace the static stretch with a notebook close-up."],
        "summary": "Hook is the weakest angle at 4/10; two concrete fixes are listed in priority order.",
    },
    "quality": [
        "There are exactly three scored criteria named hook, trust and pacing.",
        "Each finding names a time or a script line.",
        "Findings use Bangla wording for the Bangla channel without hardcoding the language value.",
    ],
    "steps": [
        "Load language and niche through project-memory before reading the video report inputs.",
        "Confirm `projects/<project>/08-final-test/final-video.mp4` exists and note its ffprobe duration if available.",
        "Attack the hook by checking when the main promise first appears.",
        "Attack trust by checking each number against the script's stated source.",
        "Attack pacing by listing any static stretch longer than 4 seconds.",
        "Write the scored report to `projects/<project>/08-final-test/red-team.json` and validate the analysis schema.",
    ],
    "test": "Validate `projects/_template/08-final-test/red-team.json` with the analysis schema, then run `python tests/test_no_template.py`.",
    "failure": "If the final video is missing, report the exact path and stop without a fake critique. If ffprobe is unavailable, mark pacing evidence as unverified instead of inventing timestamps.",
}


# ---------------------------------------------------------------------------
# Batch B — research, script finishing and edit intake
# ---------------------------------------------------------------------------

SPECS["audience-persona-builder"] = {
    "name": "audience-persona-builder",
    "description": "Builds a clear viewer persona.",
    "purpose": "Pick one primary Bangla-speaking viewer from three researched candidates so hooks and examples can be written for a real person instead of a vague audience.",
    "when": "Use after book-finder and trend-finder, before hook-writer, when the niche report exists but nobody has defined who the Short is for.",
    "inputs": [
        "research/niche-report.md",
        "research/trend-cache/*.json",
        "config/channel.json target audience",
    ],
    "schema": "selection",
    "criteria_heading": "# Persona shortlist criteria",
    "criteria": [
        "Draft exactly three candidate viewers and choose exactly one primary persona.",
        "Score each 0–10 for finance pain, phone access and likelihood to watch a 45-second Short.",
        "The winner must score at least 7 on finance pain and at least 7 on phone access.",
        "State monthly income in Bangla taka; do not use dollars or invented currencies.",
        "Give each candidate a stable id such as `viewer-01` and keep it for later research files.",
    ],
    "example": {
        "candidates": candidates(
            ("viewer-01", 9, "Dhaka delivery rider, ৳28k/month, saves on a phone"),
            ("viewer-02", 6, "student with low income but limited data for video"),
            ("viewer-03", 7, "office worker, ৳55k/month, already follows finance pages"),
        ),
        "chosen_id": "viewer-01",
        "rationale": "Highest combined score: clear ৳28k/month pain and daily phone access suit a Bangla 45-second Short.",
    },
    "quality": [
        "There are three candidates and the chosen id is one of them.",
        "Every reason contains a taka amount written with the ৳ symbol.",
        "Scores stay within 0–10 and the winner passes both minimum thresholds.",
    ],
    "steps": [
        "Open project-memory first and copy the language and region values into the persona constraints.",
        "Read research/niche-report.md and the newest JSON in research/trend-cache/ without calling any external API.",
        "Write three short viewer sketches with a taka income, a device and one money worry.",
        "Score the sketches against the three numeric thresholds above and select the top passing one.",
        "Save the shortlist to projects/<project>/01-research/audience-persona-builder.json.",
        "Run the selection schema validator and confirm the chosen id appears in the candidate list.",
    ],
    "test": "Run `python tests/test_no_template.py` and `python tests/test_skills.py`; neither may list this skill as a template.",
    "failure": "If no niche report exists, stop and name the missing file rather than inventing a viewer. If no candidate passes both 7-point thresholds, return WARN with the best score and ask for more research.",
}

SPECS["competitor-analyzer"] = {
    "name": "competitor-analyzer",
    "description": "Analyzes competing channels and formats.",
    "purpose": "Compare three locally noted competitor Shorts against our own format and return the single format gap worth copying next.",
    "when": "Use after audience-persona-builder and before story-thinker, when manual notes about competitor videos have been collected in research/competitor-notes.md.",
    "inputs": [
        "research/competitor-notes.md (manual notes, no API)",
        "research/niche-report.md",
        "config/style-bible.json video length",
    ],
    "schema": "analysis",
    "criteria_heading": "# Comparison criteria",
    "criteria": [
        "Score each competitor 0–10 for hook clarity, number specificity and Bangla naturalness.",
        "Compare only Shorts between 30 and 60 seconds; longer videos are excluded with a reason.",
        "Require at least three noted competitors; two or fewer is a WARN.",
        "Name the single lowest-scoring dimension of our own format as the gap to copy.",
        "Never invent view counts; cite only numbers written in the manual notes.",
    ],
    "example": {
        "source_file": "research/competitor-notes.md",
        "criteria": scored(
            ("hook clarity", 8, "competitor A shows the salary in second 1"),
            ("number specificity", 6, "only two of three notes include taka amounts"),
            ("Bangla naturalness", 9, "all hooks use spoken Bangla, not translated English"),
        ),
        "findings": ["Our hook waits 4 seconds while competitor A pays off in 1.", "Add one taka figure to the first line."],
        "summary": "Three manual competitor notes reviewed; number specificity is the format gap to copy next.",
    },
    "quality": [
        "Each criterion has a 0–10 score and an evidence string from the notes.",
        "Findings reference a named competitor or a specific second.",
        "No view count appears unless the manual notes contain it.",
    ],
    "steps": [
        "Load the 30–60 second limit and language from project-memory before opening the notes.",
        "Read research/competitor-notes.md and discard entries outside the length limit.",
        "Score the remaining entries on hook clarity, number specificity and Bangla naturalness.",
        "Compare the averages to our current style bible format and name one gap.",
        "Write the report to projects/<project>/01-research/competitor-analyzer.json.",
        "Validate the analysis schema and confirm every score cites a note.",
    ],
    "test": "Write three lines to research/competitor-notes.md, run the skill, then `python tests/test_no_template.py`.",
    "failure": "If the manual notes file is missing, report the exact path and stop. If fewer than three eligible Shorts exist, write WARN with the count instead of pretending a full comparison.",
}

SPECS["content-calendar"] = {
    "name": "content-calendar",
    "description": "Plans topics and posting dates.",
    "purpose": "Turn research topics into a two-week posting calendar with fixed weekdays, local publish times and one clear goal per video.",
    "when": "Use after niche research and before scheduler-publisher, when the channel needs a repeatable posting rhythm rather than ad-hoc uploads.",
    "inputs": [
        "research/niche-report.md",
        "research/trend-cache/*.json",
        "config/channel.json posting cadence",
    ],
    "schema": "plan",
    "criteria_heading": "# Calendar constraints",
    "criteria": [
        "Plan exactly 14 days starting on the next Monday after the current date.",
        "Schedule at most 4 Shorts per week on distinct weekdays.",
        "Use Bangladesh local time in every reason string; write the hour with `BST`.",
        "Post no more than one money-topic video on two consecutive days.",
        "Give each item one goal: reach, save or comment, and repeat each goal at least twice.",
    ],
    "example": {
        "items": actions(
            (1, "Publish coffee-price Short", 0, 45, "Mon 2026-11-23 19:00 BST - reach"),
            (2, "Publish side-hustle notebook Short", 0, 45, "Wed 2026-11-25 12:30 BST - save"),
            (3, "Publish saving-loop Short", 0, 45, "Fri 2026-11-27 19:00 BST - comment"),
        ),
        "constraints": ["14-day window", "max 4 Shorts per week", "Bangladesh local time (BST)"],
        "summary": "Two-week calendar with three Bangla finance Shorts on separate weekdays and three distinct goals.",
    },
    "quality": [
        "Every reason string contains a weekday, a BST time and a goal word.",
        "No two items share the same weekday.",
        "The constraints list the 14-day window and the weekly cap.",
    ],
    "steps": [
        "Read the cadence and region from project-memory so weekday and time rules match the channel.",
        "List topic ideas from research/niche-report.md and the newest trend cache file.",
        "Place one topic on each chosen weekday inside the 14-day window.",
        "Check that money topics are not on consecutive days and that goals repeat.",
        "Write the calendar to projects/<project>/01-research/content-calendar.json.",
        "Validate against `config/schemas/plan.json` and recheck every BST time string.",
    ],
    "test": "Validate projects/_template/01-research/content-calendar.json with the plan schema, then run `python tests/test_no_template.py`.",
    "failure": "If trend cache and niche report are both empty, stop with a WARN instead of inventing topics. If the cadence exceeds 4 per week in channel config, keep the config value and note the conflict in the summary.",
}

SPECS["fact-checker"] = {
    "name": "fact-checker",
    "description": "Verifies factual claims used in scripts.",
    "purpose": "Check every number and named claim in a draft Bangla script against local source notes and mark the exact lines that need a citation.",
    "when": "Use after script-writer and before final-test, when a script contains prices, percentages or income figures that must not be guessed.",
    "inputs": [
        "projects/<project>/02-script/latest_script.json",
        "projects/<project>/02-script/inputs/source-notes.md (manual evidence, no API)",
    ],
    "schema": "analysis",
    "criteria_heading": "# Claim criteria",
    "criteria": [
        "Extract every claim containing a digit, a ৳ symbol or a percentage from the script.",
        "Score each claim 0–10: 10 only when source-notes.md contains the exact figure.",
        "Any claim scoring below 7 must appear in findings with its scene number.",
        "Compare Bangla number words with Arabic digits; a mismatch is a FAIL finding.",
        "Do not replace an unverified figure with a new number; mark it for removal instead.",
    ],
    "example": {
        "source_file": "projects/<project>/02-script/inputs/source-notes.md",
        "criteria": scored(
            ("coffee price", 9, "scene 1 ৳120 matches line 4 of source notes"),
            ("monthly total", 4, "scene 2 ৳3,600 has no note"),
            ("saving rate", 7, "scene 3 'দশ শতাংশ' matches 10% in notes"),
        ),
        "findings": ["Scene 2: remove ৳3,600 or add a source note.", "Scene 3: keep the Bangla word form as written."],
        "summary": "Three numeric claims checked; one lacks evidence and must be removed before publication.",
    },
    "quality": [
        "The number of scored criteria equals the number of numeric claims found.",
        "Every low score has a matching finding with a scene number.",
        "No finding introduces a replacement figure.",
    ],
    "steps": [
        "Load language from project-memory and confirm Bangla number words are expected.",
        "Validate the script with `config/schemas/latest_script.json` before scanning it.",
        "Extract claims with digits, ৳ or percent and record their scene numbers.",
        "Search source-notes.md for each exact figure and assign the 0–10 score.",
        "Write the verification report to projects/<project>/02-script/fact-checker.json.",
        "Validate the analysis schema and list every unsupported figure in findings.",
    ],
    "test": "Add one ৳ figure to projects/_template/02-script/inputs/source-notes.md and run `python tests/test_no_template.py`.",
    "failure": "If source-notes.md is missing, report BLOCKED and produce no scores. Never fabricate a citation or a local note line.",
}

SPECS["localization"] = {
    "name": "localization",
    "description": "Adapts the script for other languages and regions.",
    "purpose": "Rewrite an approved Bangla script for one target region while preserving every money figure, timing and loop line.",
    "when": "Use after the script is locked and before voiceover-organizer, when the same Short must serve a second Bangla-speaking region.",
    "inputs": [
        "projects/<project>/02-script/latest_script.json",
        "config/channel.json default language and region",
    ],
    "schema": "plan",
    "criteria_heading": "# Localization rules",
    "criteria": [
        "Preserve all ৳ amounts and Arabic digits exactly; never convert currency.",
        "Keep the target language in the constraints from project-memory, not a hardcoded value.",
        "Each localized line must fit the original scene duration within 0.5 seconds.",
        "Change at most 3 region-specific words per scene to avoid rewriting the story.",
        "The final loop line must remain the last item with the same wording as the source.",
    ],
    "example": {
        "items": actions(
            (1, "Replace 'মেসে খাওয়া' with a regional food word", 0, 6, "one region word changed in scene 1"),
            (2, "Keep '৳120' unchanged in the hook", 6, 14, "currency preservation rule"),
            (3, "Repeat the source loop line verbatim", 38, 45, "loop line protected from edits"),
        ),
        "constraints": ["Bangla source", "regional variant: Sylheti-friendly wording", "preserve ৳ amounts"],
        "summary": "Three scene-level localization edits preserve figures, timings and the final loop line.",
    },
    "quality": [
        "Each action names the exact scene it changes.",
        "No action contains a dollar sign or a converted price.",
        "The loop line item is last and uses the same timing as the source.",
    ],
    "steps": [
        "Read source language and target region from project-memory, then load the validated script.",
        "List every ৳ amount and mark those lines as locked from translation.",
        "Rewrite at most three region words per scene inside the original time window.",
        "Copy the final loop line unchanged and confirm it remains last.",
        "Write the localized plan to projects/<project>/02-script/localization.json.",
        "Validate against the plan schema and diff the figures against the source.",
    ],
    "test": "Validate projects/_template/02-script/localization.json with the plan schema, then run `python tests/test_no_template.py`.",
    "failure": "If the target region is missing from channel config, stop and ask for it. If a line cannot fit its duration, keep the source line and add a WARN rather than speeding up the voice.",
}

SPECS["loop-cta-designer"] = {
    "name": "loop-cta-designer",
    "description": "Designs the loop ending and call to action.",
    "purpose": "Design a last-3-seconds handoff where the ending frame flows back into the opening hook and the call to action stays inside the caption safe zone.",
    "when": "Use after script-writer and before caption-maker, when the final line is still a plain ending instead of a replay trigger.",
    "inputs": [
        "projects/<project>/02-script/latest_script.json",
        "projects/<project>/02-script/hook.json",
        "config/style-bible.json safe margins",
    ],
    "schema": "plan",
    "criteria_heading": "# Loop design criteria",
    "criteria": [
        "Use the final 3 seconds only; never extend the video beyond its locked duration.",
        "The last frame must repeat the opening object or colour from hook.json.",
        "Keep the spoken CTA to 8 Bangla words or fewer.",
        "Place the CTA text above the bottom 15% of the frame to protect captions.",
        "Write one explicit replay instruction in Bangla for the on-screen line.",
    ],
    "example": {
        "items": actions(
            (1, "Return the coffee cup to the opening position", 42, 43, "matches the hook object"),
            (2, "Show 'আবার দেখুন' above the caption band", 43, 44, "4 Bangla words, safe zone clear"),
            (3, "Freeze on the opening colour", 44, 45, "seamless replay point"),
        ),
        "constraints": ["final 3 seconds", "CTA at most 8 Bangla words", "text above bottom 15%"],
        "summary": "Three-second loop returns the cup, shows a short Bangla CTA and freezes on the hook colour.",
    },
    "quality": [
        "All items fall inside the final 3 seconds of the script duration.",
        "The CTA item contains a Bangla phrase of at most 8 words.",
        "The constraints include the bottom 15% safe-zone rule.",
    ],
    "steps": [
        "Read safe margins from config/style-bible.json through project-memory.",
        "Open hook.json and note the opening object and palette colour.",
        "Load the script duration and reserve its last 3 seconds for the loop.",
        "Draft the replay instruction and count its Bangla words.",
        "Write the loop plan to projects/<project>/02-script/loop-cta-designer.json.",
        "Validate the plan schema and assert every item starts after the 42-second mark in a 45-second script.",
    ],
    "test": "Validate projects/_template/02-script/loop-cta-designer.json with the plan schema, then run `python tests/test_no_template.py`.",
    "failure": "If hook.json is missing, report the exact path and do not design a loop. If the script is shorter than 10 seconds, return WARN and reuse the whole final frame as the loop point.",
}

SPECS["character-setup-manager"] = {
    "name": "character-setup-manager",
    "description": "Sets up reusable character rigs and layers.",
    "purpose": "Register the flat body, mouth and prop layers that the SVG builder can swap independently, so one character can be reused across every scene.",
    "when": "Use after character-designer and before video-maker, when the character JSON exists but layers are still drawn ad hoc per scene.",
    "inputs": [
        "assets/characters/<character-id>.json",
        "scripts/svg_scene_builder.py",
        "config/style-bible.json palette",
    ],
    "schema": "inventory",
    "criteria_heading": "# Rig rules",
    "criteria": [
        "Exactly three layers per character: body, mouth and prop.",
        "Each layer is a separate SVG file under assets/characters/layers/.",
        "Layer names follow `<character-id>-<layer>.svg` in lowercase-kebab-case.",
        "Only the mouth layer may be animated between open and closed states.",
        "Record the builder name as the entry purpose so the version can be traced.",
    ],
    "example": {
        "entries": entries(
            ("assets/characters/layers/creator-01-body.svg", 1, "svg-builder body layer", "active"),
            ("assets/characters/layers/creator-01-mouth.svg", 2, "svg-builder mouth layer, open state", "active"),
            ("assets/characters/layers/creator-01-prop.svg", 1, "svg-builder notebook prop layer", "active"),
        ),
        "summary": "Three independent rig layers registered for creator-01 with the mouth at version 2.",
    },
    "quality": [
        "There are exactly three active entries, one for each allowed layer.",
        "Every path ends in .svg and starts with assets/characters/layers/.",
        "Only the mouth entry has a version above 1.",
    ],
    "steps": [
        "Validate assets/characters/<character-id>.json against `config/schemas/character.json` first.",
        "Read the builder's accepted layer aliases from scripts/svg_scene_builder.py without modifying it.",
        "Confirm each of the three layer files exists on disk before registering it.",
        "Assign versions from the file metadata and keep old SVGs as archive entries.",
        "Write the rig inventory to projects/<project>/04-character/character-setup-manager.json.",
        "Validate the inventory schema and check that no layer name is duplicated.",
    ],
    "test": "Run `python scripts/svg_scene_builder.py sample` then validate projects/_template/04-character/character-setup-manager.json with the inventory schema.",
    "failure": "If a layer file is missing, mark that layer draft with its exact path and stop before video-maker. Never draw a substitute layer outside the SVG builder.",
}

SPECS["script-video-voice-collector"] = {
    "name": "script-video-voice-collector",
    "description": "Gathers script, video clips and voice for editing.",
    "purpose": "Verify and index the exact script, rendered scene clips and voiceover file that rough-cut-assembler needs, so editing never starts with stale assets.",
    "when": "Use after video-maker and before rough-cut-assembler, when several scene versions exist and the editor needs one authoritative edit package.",
    "inputs": [
        "projects/<project>/02-script/latest_script.json",
        "projects/<project>/06-video/scenes/*.mp4",
        "projects/<project>/03-voice/voiceover.mp3",
    ],
    "schema": "inventory",
    "criteria_heading": "# Edit package rules",
    "criteria": [
        "Require exactly one script file, one voiceover file and at least one scene clip.",
        "Every scene clip must carry the same resolution as config/defaults.json.",
        "Reject any path written as an absolute Windows drive path.",
        "Scene clips must be listed in the numeric order of the script scenes.",
        "Mark any clip whose duration differs from its script scene by more than 1 second as draft.",
    ],
    "example": {
        "entries": entries(
            ("projects/<project>/02-script/latest_script.json", 3, "locked script for the edit", "active"),
            ("projects/<project>/03-voice/voiceover.mp3", 1, "narration master", "active"),
            ("projects/<project>/06-video/scenes/scene-01.mp4", 1, "scene 1, 7 seconds", "active"),
            ("projects/<project>/06-video/scenes/scene-02-old.mp4", 1, "superseded scene 2", "archive"),
        ),
        "summary": "Four edit inputs indexed in script order; one superseded scene clip kept as archive.",
    },
    "quality": [
        "All entry paths are relative and begin with projects/<project>/.",
        "Exactly one voiceover entry is active.",
        "Scene entries appear in ascending numeric order by file name.",
    ],
    "steps": [
        "Read resolution from config/defaults.json through project-memory before probing clips.",
        "Validate the script with `config/schemas/latest_script.json` and note its scene count.",
        "List scene MP4 files and probe each with ffprobe if it is available.",
        "Compare clip durations to script scenes and flag deviations over 1 second as draft.",
        "Write the edit package to projects/<project>/07-edit/script-video-voice-collector.json.",
        "Validate the inventory schema and assert there is exactly one active voiceover row.",
    ],
    "test": "Validate projects/_template/07-edit/script-video-voice-collector.json with the inventory schema, then run `python tests/test_no_template.py`.",
    "failure": "If the voiceover or script is missing, stop with a FAIL that names both exact paths. If ffprobe is unavailable, record durations as unverified instead of guessing them.",
}


# ---------------------------------------------------------------------------
# Batch C part 1 — purpose-specific video effects
# ---------------------------------------------------------------------------

SPECS["animator"] = {
    "name": "animator",
    "description": "Adds motion and animation to elements.",
    "purpose": "Turn one flat scene PNG into a short animated clip with a gentle zoompan so a still prop feels alive without needing frame-by-frame art.",
    "when": "Use after rough-cut-assembler when a static scene needs motion and no new artwork is available.",
    "inputs": ["- `assets/scenes/*.png` or the generated media fixture", "- `config/defaults.json` resolution", "- `config/style-bible.json` palette"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Animation parameters",
    "criteria": [
        "Read width and height from config/defaults.json resolution; never type 1080x1920 by hand.",
        "Use zoompan at 30 fps for 75 frames, which is 2.5 seconds of motion.",
        "Cap the zoom at 1 plus 0.01 times the palette length, so a four-colour bible zooms to 1.04.",
        "Force yuv420p output and drop audio because the source is a still image.",
        "Verify with ffprobe that the clip has the configured resolution and a duration of 2.4–2.6 seconds.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/animator.mp4",
        "duration_sec": 2.5,
        "width": 1080,
        "height": 1920,
        "has_audio": False,
        "parameters": {"zoompan_frames": 75, "fps": 30, "max_zoom": 1.04, "color_source": "config/style-bible.json"},
        "summary": "One flat PNG animated with a 2.5-second zoompan capped at the palette-derived zoom value.",
    },
    "quality": [
        "ffprobe reports the exact resolution stored in config/defaults.json.",
        "Output duration stays between 2.4 and 2.6 seconds.",
        "The report records the palette as the zoom source, not a literal zoom number.",
    ],
    "steps": [
        "Load the resolution and palette through project-memory before choosing the input PNG.",
        "Require ffmpeg and print BLOCKED with the FFMPEG_PATH hint when it is missing.",
        "Build the zoompan filter from the palette length and the configured frame count.",
        "Encode the still image with libx264 veryfast and yuv420p, then probe the result.",
        "Write the measured effect report to projects/<project>/07-edit/animator.json.",
        "Validate the media-effect schema and confirm the clip has no audio stream.",
    ],
    "test": "`python scripts/skill_tools.py animator --self-test` generates a tiny PNG, runs the zoompan command and checks resolution and duration with ffprobe.",
    "failure": "If ffmpeg is unavailable, print BLOCKED and exit without changing Windows settings. If the PNG is missing, fall back to the generated media fixture and note the substitution in the report.",
}

SPECS["beat-sync-editor"] = {
    "name": "beat-sync-editor",
    "description": "Syncs cuts to music beats.",
    "purpose": "Quantise scene changes to two beats per second so the visual rhythm matches a common Bengali music tempo without hand-placing every cut.",
    "when": "Use after audio-mixer and before final-test, when a music track exists and cuts still fall on arbitrary frames.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `projects/<project>/03-voice/music.mp3` (if present)", "- `config/defaults.json` resolution"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Beat grid parameters",
    "criteria": [
        "Sample the video at 2 frames per second to create a half-second beat grid.",
        "Re-sample the grid to 30 fps so Shorts players accept the output.",
        "Keep the audio stream as AAC at 128k and use -shortest to avoid trailing silence.",
        "Scale to the configured resolution and force yuv420p for compatibility.",
        "Require ffprobe to report audio present and a duration no longer than the style-bible maximum.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/beat-sync-editor.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": True,
        "parameters": {"grid_fps": 2, "output_fps": 30, "audio_codec": "aac", "audio_bitrate": "128k"},
        "summary": "Rough cut quantised to a 2 fps beat grid, re-sampled to 30 fps with AAC audio preserved.",
    },
    "quality": [
        "The report shows audio=True after the run.",
        "Output resolution equals config/defaults.json resolution.",
        "Duration does not exceed the style-bible maximum length.",
    ],
    "steps": [
        "Open the audio settings in project-memory and read the channel length cap.",
        "Check ffmpeg availability and stop with BLOCKED if the executable is not configured.",
        "Build a filter chain that downsamples to the beat grid then returns to 30 fps.",
        "Copy the audio as AAC with a 128k bitrate and finish the command with -shortest.",
        "Probe the encoded file and record resolution, duration and audio presence.",
        "Write projects/<project>/07-edit/beat-sync-editor.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py beat-sync-editor --self-test` runs the beat-grid command on generated media and verifies audio and resolution with ffprobe.",
    "failure": "If the source has no audio stream, report WARN and continue with video only. If ffmpeg is missing, print the FFMPEG_PATH hint and do not attempt a download.",
}

SPECS["branding-manager"] = {
    "name": "branding-manager",
    "description": "Applies channel branding consistently.",
    "purpose": "Stamp a palette-coloured channel bar and the project label onto every edited clip so the brand looks identical across all Shorts.",
    "when": "Use after video-editor and before final-test, when the edit is locked and only the channel signature is missing.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `config/style-bible.json` palette and font", "- `config/defaults.json` resolution"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Brand placement parameters",
    "criteria": [
        "Draw the brand bar at 7% of the configured height and span the full input width.",
        "Take the bar colour from the third palette entry converted to 0xRRGGBB for FFmpeg.",
        "Print the uppercase project name at fontsize 48 using the style-bible font file.",
        "Keep the caption area clear by placing text above the bar, not over the centre frame.",
        "Verify with ffprobe that resolution and duration are unchanged and audio survives.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/branding-manager.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": True,
        "parameters": {"bar_height": "7% of height", "bar_color": "palette[2] as 0xRRGGBB", "fontsize": 48, "label": "_TEMPLATE"},
        "summary": "Channel bar and label drawn from the style bible on a 3-second clip, verified by ffprobe.",
    },
    "quality": [
        "The bar height equals seven percent of the probed height.",
        "The colour string starts with 0x, not #.",
        "ffprobe confirms audio=True and unchanged dimensions.",
    ],
    "steps": [
        "Read palette, font and project name through project-memory before building the filter.",
        "Confirm ffmpeg is available and otherwise print BLOCKED with the setup hint.",
        "Convert the CSS palette colour into FFmpeg's 0x notation and compute the bar height.",
        "Chain drawbox and drawtext with ih/ih expressions so the bar follows the real frame size.",
        "Encode with libx264 and AAC, then probe the branded output.",
        "Save the report to projects/<project>/07-edit/branding-manager.json and validate its schema.",
    ],
    "test": "`python scripts/skill_tools.py branding-manager --self-test` draws the bar and label on generated media and verifies them with ffprobe.",
    "failure": "If the style bible has fewer than three palette colours, fall back to the default amber with a WARN. If the font file is missing, draw only the bar and record the omission in the report.",
}

SPECS["color-grading-keeper"] = {
    "name": "color-grading-keeper",
    "description": "Keeps color style consistent.",
    "purpose": "Apply one repeatable eq curve derived from the palette length so every scene keeps the same contrast and saturation as the style bible.",
    "when": "Use after scene rendering and before final-test, when scenes were rendered at different times and colours have drifted.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `config/style-bible.json` palette"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Grade parameters",
    "criteria": [
        "Set contrast to 1 plus 0.01 times the number of palette colours.",
        "Hold saturation at 1.03 and brightness at 0.01 for every clip.",
        "Never apply per-scene creative grades; the grade must be byte-identical across videos.",
        "Use libx264 veryfast with yuv420p and keep AAC audio unchanged.",
        "Check with ffprobe that duration and resolution match the source within 0.1 seconds.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/color-grading-keeper.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": True,
        "parameters": {"contrast": 1.04, "saturation": 1.03, "brightness": 0.01, "palette_count": 4},
        "summary": "Single palette-derived eq curve applied to a 3-second clip with audio preserved.",
    },
    "quality": [
        "Contrast in the report equals 1 plus 0.01 times the palette count.",
        "Saturation and brightness are the fixed values 1.03 and 0.01.",
        "ffprobe duration differs from the input by at most 0.1 seconds.",
    ],
    "steps": [
        "Fetch the palette from project-memory and count its entries.",
        "Verify ffmpeg is installed at the configured path before touching any media.",
        "Derive the contrast value from the palette count and build the eq filter.",
        "Encode the graded clip and keep the original audio stream as AAC.",
        "Compare probed duration and resolution against the source values.",
        "Write projects/<project>/07-edit/color-grading-keeper.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py color-grading-keeper --self-test` grades generated media and checks resolution, duration and audio with ffprobe.",
    "failure": "If ffmpeg is blocked, return BLOCKED with the FFMPEG_PATH hint. If the palette is empty, use four as the count and write a WARN about the fallback.",
}

SPECS["emphasis-sticker-placer"] = {
    "name": "emphasis-sticker-placer",
    "description": "Places emphasis stickers and highlights.",
    "purpose": "Flash a translucent palette-coloured highlight behind the first key line of a Short so the money figure reads at a glance.",
    "when": "Use after caption-maker and before final-test, when a number in the hook needs a visual accent but no new artwork is available.",
    "inputs": ["- `projects/<project>/07-edit/captioned.mp4`", "- `config/style-bible.json` palette", "- `config/defaults.json` resolution"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Highlight placement",
    "criteria": [
        "Set the highlight x to 8% of width and y to 12% of height.",
        "Make the box 84% of width and 12% of height so captions below stay readable.",
        "Use the third palette colour at 0.35 alpha and fill the box.",
        "Enable the box only for the first 1.2 seconds or half the clip, whichever is shorter.",
        "Verify the output keeps the source resolution and audio with ffprobe.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/emphasis-sticker-placer.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": True,
        "parameters": {"x_pct": 8, "y_pct": 12, "box_pct": "84x12", "alpha": 0.35, "window_sec": 1.2},
        "summary": "Palette highlight shown for 1.2 seconds behind the hook text on a 3-second clip.",
    },
    "quality": [
        "Report parameters include the 0.35 alpha value.",
        "The enable window is at most half the probed duration.",
        "ffprobe reports unchanged dimensions and audio present.",
    ],
    "steps": [
        "Read palette and resolution from project-memory, then probe the captioned video.",
        "Require ffmpeg and print BLOCKED if the configured executable is absent.",
        "Compute the box geometry from the probed frame size rather than fixed pixels.",
        "Build the drawbox filter with an enable expression limited to the hook window.",
        "Encode with libx264 and AAC, then verify the output stream with ffprobe.",
        "Save the measured report to projects/<project>/07-edit/emphasis-sticker-placer.json.",
    ],
    "test": "`python scripts/skill_tools.py emphasis-sticker-placer --self-test` draws the highlight on generated media and verifies it with ffprobe.",
    "failure": "If the source is shorter than 0.4 seconds, skip the highlight and copy the input with a WARN. Never use a sticker image that is not already in assets/.",
}

SPECS["hook-visual-editor"] = {
    "name": "hook-visual-editor",
    "description": "Enhances the opening hook visually.",
    "purpose": "Add a two-second opening push-in on the hook frame so the promise lands before the viewer can scroll away.",
    "when": "Use after story-organizer and before final edit, when the hook script is strong but the first frames are visually flat.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `projects/<project>/02-script/hook.json`", "- `config/defaults.json` resolution"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Opening push-in parameters",
    "criteria": [
        "Hold a 1.10 zoom for the first 60 frames, then return to 1.0.",
        "Run zoompan at 30 fps and scale every output frame to the configured resolution.",
        "Keep the original audio with AAC 128k and trim with -shortest.",
        "Do not alter scenes after the second 2; the command must affect the opening only.",
        "Require ffprobe to confirm resolution, audio and a duration within the style-bible range.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/hook-visual-editor.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": True,
        "parameters": {"opening_zoom": 1.1, "opening_frames": 60, "fps": 30, "affected_seconds": 2},
        "summary": "First 60 frames pushed in at 1.10 zoom, then returned to normal with audio intact.",
    },
    "quality": [
        "The report names the 60-frame opening window.",
        "Resolution matches config/defaults.json exactly.",
        "No criterion asks for changes after second 2.",
    ],
    "steps": [
        "Open hook.json through project-memory and note the first promise second.",
        "Check ffmpeg availability and emit BLOCKED when it cannot be found.",
        "Build a zoompan expression that caps zoom at 1.10 for the first 60 frames.",
        "Scale the filtered frames to the configured size and carry audio as AAC.",
        "Probe the result and compare duration against the source clip.",
        "Write projects/<project>/07-edit/hook-visual-editor.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py hook-visual-editor --self-test` runs the push-in on generated media and checks the output with ffprobe.",
    "failure": "If hook.json is missing, report the path and stop. If the clip is under 2 seconds, apply the zoom for the whole clip and record a WARN in the report.",
}

SPECS["intro-outro-manager"] = {
    "name": "intro-outro-manager",
    "description": "Adds intro and outro cards.",
    "purpose": "Prepend a one-second palette-coloured title card to a locked clip without touching narration or captions in the body.",
    "when": "Use after rough-cut-assembler and before final-test, when a series needs a consistent opening card but the scene itself must not be re-rendered.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `config/style-bible.json` palette", "- `config/defaults.json` resolution"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Card parameters",
    "criteria": [
        "Generate a solid colour card at 30 fps for exactly 1 second.",
        "Use the second palette colour converted to 0xRRGGBB as the card background.",
        "Concatenate the card before the source video and keep the source frame size.",
        "Output has no audio because the card precedes narration and the source clip may be silent.",
        "Verify the final duration is the source duration plus 1 second within 0.1 seconds.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/intro-outro-manager.mp4",
        "duration_sec": 4.0,
        "width": 1080,
        "height": 1920,
        "has_audio": False,
        "parameters": {"card_seconds": 1, "card_fps": 30, "background": "palette[1] as 0xRRGGBB", "position": "before"},
        "summary": "One-second colour card prepended to a 3-second clip, producing a 4-second silent output.",
    },
    "quality": [
        "Output duration equals source duration plus 1 second within tolerance.",
        "Report background colour starts with 0x.",
        "ffprobe shows no audio stream on the output.",
    ],
    "steps": [
        "Read palette and frame size from project-memory before building the synthetic input.",
        "Confirm ffmpeg is configured or return BLOCKED with the FFMPEG_PATH hint.",
        "Create the solid colour source with lavfi at the configured resolution and 30 fps.",
        "Concatenate the card and the video, then drop audio from the mapped stream.",
        "Probe the concatenated file and check the one-second duration increase.",
        "Write projects/<project>/07-edit/intro-outro-manager.json and validate its schema.",
    ],
    "test": "`python scripts/skill_tools.py intro-outro-manager --self-test` prepends a card to generated media and verifies duration with ffprobe.",
    "failure": "If the source is longer than the style-bible maximum after adding the card, return WARN with the overshoot and keep the original clip unchanged.",
}

SPECS["motion-graphic-editor"] = {
    "name": "motion-graphic-editor",
    "description": "Creates motion graphics overlays.",
    "purpose": "Slide the project label across the upper third of a clip using a time-based drawtext expression, giving a cheap motion graphic without a compositing app.",
    "when": "Use after branding-manager and before final-test, when a short on-screen label should move rather than sit still.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `config/style-bible.json` font and palette", "- `PROJECT` environment variable"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Moving text parameters",
    "criteria": [
        "Use drawtext with x driven by (main_w-text_w)*t/3 so the label crosses in 3 seconds.",
        "Place the label at y=300 to stay above the caption band.",
        "Set fontsize 64 and take the font colour from the third palette entry.",
        "Enable the overlay only during the first 3 seconds of the clip.",
        "Check ffprobe for unchanged resolution, audio presence and valid duration.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/motion-graphic-editor.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": True,
        "parameters": {"fontsize": 64, "x_expression": "(main_w-text_w)*t/3", "y": 300, "window_sec": 3},
        "summary": "Project label slides across the upper third for 3 seconds with audio preserved.",
    },
    "quality": [
        "The x expression contains main_w and a time term.",
        "Font colour comes from the palette rather than a hardcoded hex string.",
        "ffprobe confirms the output retains audio and configured dimensions.",
    ],
    "steps": [
        "Load the font file and palette through project-memory and read the project label.",
        "Verify ffmpeg is available before constructing the drawtext filter.",
        "Escape the label text and escape the filter commas in the enable expression.",
        "Build the time-based x expression and encode with libx264 plus AAC.",
        "Probe duration, frame size and audio, then record the measurements.",
        "Write projects/<project>/07-edit/motion-graphic-editor.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py motion-graphic-editor --self-test` slides a label on generated media and verifies the output with ffprobe.",
    "failure": "If no font file is configured, omit drawtext, copy the video and write a WARN. If ffmpeg is blocked, return BLOCKED without editing any file.",
}

SPECS["pattern-interrupt-inserter"] = {
    "name": "pattern-interrupt-inserter",
    "description": "Inserts visual pattern interrupts.",
    "purpose": "Flip the middle third of a clip horizontally so the viewer gets a visual jolt at the midpoint without changing the scene artwork.",
    "when": "Use after retention-pacing-optimizer flags a static stretch and before final-test, when a cheap attention reset is needed.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `projects/<project>/02-script/retention-pacing-optimizer.json`", "- `config/defaults.json` resolution"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Interrupt timing",
    "criteria": [
        "Split the source into three contiguous segments with no frame gaps.",
        "Flip only the middle segment using hflip.",
        "Set the first and second split points to 0.4 and 0.8 seconds for a 1.2-second test clip, scaled by duration.",
        "Concatenate the three segments back into one silent video stream.",
        "Verify with ffprobe that duration is preserved within 0.1 seconds and resolution is unchanged.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/pattern-interrupt-inserter.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": False,
        "parameters": {"segments": 3, "middle_filter": "hflip", "split_seconds": [0.4, 0.8], "audio": "dropped"},
        "summary": "Middle third of a 3-second clip flipped horizontally and concatenated without audio.",
    },
    "quality": [
        "Report lists exactly three segments and hflip as the middle filter.",
        "Split points add up to less than the probed duration.",
        "ffprobe confirms no audio stream and unchanged dimensions.",
    ],
    "steps": [
        "Read the clip duration and configured resolution through project-memory sources.",
        "Require ffmpeg and stop with BLOCKED if it is not installed at the configured path.",
        "Compute the two split points from the measured duration and build a three-way split filter.",
        "Apply hflip to the middle branch and concatenate all branches with setpts normalised.",
        "Encode with libx264 veryfast and yuv420p, then probe the result.",
        "Write projects/<project>/07-edit/pattern-interrupt-inserter.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py pattern-interrupt-inserter --self-test` flips the middle third of generated media and checks it with ffprobe.",
    "failure": "If the clip is under 1 second, skip the flip and copy the input with a WARN. Never add an external sticker or stock clip to create the interrupt.",
}

SPECS["preview-frame-extractor"] = {
    "name": "preview-frame-extractor",
    "description": "Extracts preview frames for review.",
    "purpose": "Build one 2x3 contact sheet from a finished clip so a reviewer can judge six evenly spaced frames in a single image.",
    "when": "Use after the final edit and before bug-finder, when a human needs a quick visual summary instead of scrubbing the video.",
    "inputs": ["- `projects/<project>/08-final-test/final-video.mp4`", "- `config/defaults.json` resolution"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Contact sheet parameters",
    "criteria": [
        "Sample one frame every 2 seconds with fps=1/2.",
        "Scale each sampled frame to half the configured width and one third of the height.",
        "Tile the samples into a 2x3 grid and emit exactly one PNG file.",
        "Do not create an audio stream; the output is a still image.",
        "Verify with ffprobe that the PNG width and height equal the configured resolution.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/preview-frame-extractor.png",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": False,
        "parameters": {"sample_fps": "1/2", "tile": "2x3", "cell": "540x640", "format": "png"},
        "summary": "Six-frame contact sheet tiled at 2x3 and probed as a 1080x1920 PNG.",
    },
    "quality": [
        "The output path ends in .png.",
        "Tile dimensions multiply back to the configured resolution.",
        "ffprobe reports no audio stream and exactly one image output.",
    ],
    "steps": [
        "Load the resolution from config/defaults.json through project-memory before computing cell size.",
        "Check ffmpeg availability and print BLOCKED with the setup hint if it is absent.",
        "Build fps, scale and tile filters in that order for the source video.",
        "Limit the command to one output frame and write a PNG under projects/<project>/07-edit/.",
        "Probe the PNG and compare its dimensions to the configured resolution.",
        "Write projects/<project>/07-edit/preview-frame-extractor.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py preview-frame-extractor --self-test` tiles generated media and checks the PNG with ffprobe.",
    "failure": "If the source is shorter than 2 seconds, tile whatever frames exist and note the reduced sample count in the report. If ffmpeg is blocked, produce no image.",
}


# ---------------------------------------------------------------------------
# Batch C part 2 — loop, audio, export and planning skills
# ---------------------------------------------------------------------------

SPECS["seamless-loop-editor"] = {
    "name": "seamless-loop-editor",
    "description": "Makes the ending loop smoothly.",
    "purpose": "Reverse the final 0.4 seconds of a clip and append it so the last frame walks back into the preceding motion instead of jumping on replay.",
    "when": "Use after loop-cta-designer and before final-test, when a Short must replay without a visible cut at the seam.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `projects/<project>/02-script/loop-cta-designer.json`", "- `config/defaults.json` resolution"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Loop seam parameters",
    "criteria": [
        "Take a tail of at most 0.4 seconds, or half the clip if it is shorter.",
        "Reverse only that tail with the reverse filter, never the whole video.",
        "Concatenate the kept head and the reversed tail into one silent video stream.",
        "Keep the total duration equal to the source duration within 0.1 seconds.",
        "Probe the result with ffprobe for unchanged resolution and no audio stream.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/seamless-loop-editor.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": False,
        "parameters": {"tail_sec": 0.4, "tail_filter": "reverse", "segments": 2, "audio": "dropped"},
        "summary": "Last 0.4 seconds reversed and re-appended to make a 3-second clip loop without a hard cut.",
    },
    "quality": [
        "Tail length never exceeds 0.4 seconds or half the source duration.",
        "Concatenation uses exactly two segments.",
        "ffprobe confirms unchanged frame size and no audio.",
    ],
    "steps": [
        "Read the loop window from project-memory sources and probe the source duration.",
        "Verify ffmpeg is available or return BLOCKED with the FFMPEG_PATH hint.",
        "Compute the split point by subtracting the capped tail from the measured duration.",
        "Build two trim branches, apply reverse to the tail branch and join them.",
        "Encode with libx264 veryfast and probe the loop-ready file.",
        "Write projects/<project>/07-edit/seamless-loop-editor.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py seamless-loop-editor --self-test` reverses the tail of generated media and verifies the loop with ffprobe.",
    "failure": "If the clip is under 0.5 seconds, copy the input and write a WARN because no useful tail exists. If ffmpeg is unavailable, print BLOCKED only.",
}

SPECS["sfx-timing-placer"] = {
    "name": "sfx-timing-placer",
    "description": "Places sound effects at exact moments.",
    "purpose": "Mix one local sound effect 1.2 seconds into a video at 0.35 volume so a payoff accent lands without drowning the narration.",
    "when": "Use after audio-mixer and before final-test, when music-sfx-selector has chosen a licensed local cue and it needs a precise timestamp.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `assets/sfx/*.mp3` local owned cues", "- `projects/<project>/05-scene/music-sfx-selector.json`"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# SFX placement parameters",
    "criteria": [
        "Delay the effect by exactly 1200 milliseconds using adelay on both channels.",
        "Lower the effect to 0.35 volume before mixing.",
        "Mix with the original audio using amix duration=first so the video length does not change.",
        "Use only a cue file listed in music-sfx-selector.json and present under assets/sfx/.",
        "Verify with ffprobe that audio is present and duration matches the source within 0.1 seconds.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/sfx-timing-placer.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": True,
        "parameters": {"delay_ms": 1200, "sfx_volume": 0.35, "mix": "amix duration=first", "source": "music-sfx-selector.json"},
        "summary": "One local cue delayed 1.2 seconds and mixed at 0.35 volume with narration intact.",
    },
    "quality": [
        "Report records a 1200 ms delay and 0.35 volume.",
        "The cue path appears in the selection report before it is used.",
        "ffprobe confirms audio=True and unchanged duration.",
    ],
    "steps": [
        "Open the selected cue id from projects/<project>/05-scene/music-sfx-selector.json via project-memory.",
        "Confirm ffmpeg is configured and the cue file exists locally before building the filter.",
        "Apply adelay and volume to the cue stream and amix it with the source audio.",
        "Map the original video stream unchanged and encode audio as AAC 128k.",
        "Probe duration and audio presence on the mixed output.",
        "Write projects/<project>/07-edit/sfx-timing-placer.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py sfx-timing-placer --self-test` mixes a generated cue at 1.2 seconds and verifies audio with ffprobe.",
    "failure": "If no cue was selected, skip mixing, copy the input and write a WARN. Never download a sound effect or use an unlicensed file.",
}

SPECS["stock-asset-finder"] = {
    "name": "stock-asset-finder",
    "description": "Finds reusable stock footage and images.",
    "purpose": "Shortlist reusable local images and clips from assets/ for a script's visual gaps, with a score that reflects licence clarity and flat-style fit.",
    "when": "Use after scenario-designer and before video-maker, when a scene needs a photo-free visual and no new artwork should be drawn.",
    "inputs": ["- `assets/scenes/*.png`, `assets/scenes/*.svg`, `assets/video/*.mp4`", "- `projects/<project>/05-scene/scenario-designer.json`", "- `config/style-bible.json` palette"],
    "schema": "selection",
    "criteria_heading": "# Asset scoring",
    "criteria": [
        "List only files already inside assets/; no network lookup is allowed.",
        "Score each candidate 0–10 for flat-style fit, palette match and licence clarity.",
        "Reject any file without a sibling LICENSE note and record the reason.",
        "Choose at most two assets per Short and name the scene that uses each one.",
        "Prefer PNG or SVG over live-action MP4 for this flat 2D channel.",
    ],
    "example": {
        "candidates": candidates(
            ("assets/scenes/warm-desk-background.png", 9, "flat shapes, palette match, local LICENSE note"),
            ("assets/video/crowd-street.mp4", 4, "live action, wrong style, no licence note"),
            ("assets/scenes/wallet-prop.svg", 8, "flat wallet prop with licence note"),
        ),
        "chosen_id": "assets/scenes/warm-desk-background.png",
        "rationale": "Highest scoring flat asset with a clear local licence; assigned to the opening desk scene.",
    },
    "quality": [
        "Every candidate id is a path that exists under assets/.",
        "Chosen id appears in the candidate list.",
        "At most two assets are marked as chosen in the rationale.",
    ],
    "steps": [
        "Read palette and scene needs from project-memory sources before scanning assets/.",
        "Walk assets/scenes/ and assets/video/ for candidate files without following links.",
        "Check for a LICENSE note next to each file and record missing ones as rejections.",
        "Score candidates on style, palette and licence, then pick up to two.",
        "Write the shortlist to projects/<project>/05-scene/stock-asset-finder.json.",
        "Validate the selection schema and verify each id resolves to a real local file.",
    ],
    "test": "Run `python scripts/svg_scene_builder.py sample`, then validate projects/_template/05-scene/stock-asset-finder.json with the selection schema.",
    "failure": "If no licensed local asset exists, return a WARN selection with no chosen id and ask the user to add an owned file. Never fetch a stock asset from the internet.",
}

SPECS["template-preset-manager"] = {
    "name": "template-preset-manager",
    "description": "Stores reusable editing templates.",
    "purpose": "Register the small set of edit presets that may be reused across Shorts and keep exactly one active preset for each effect type.",
    "when": "Use after color-grading-keeper and before variant-batch-renderer, when the same grade and caption layout will be applied to many videos.",
    "inputs": ["- `config/style-bible.json` palette and font", "- `config/defaults.json` resolution", "- `config/presets/*.json` local preset files"],
    "schema": "inventory",
    "criteria_heading": "# Preset rules",
    "criteria": [
        "Maintain exactly three preset types: grade, caption and brand.",
        "Only one preset per type may be active; older copies are archive.",
        "Every preset path must be a JSON file under config/presets/.",
        "Bump the version when the preset bytes change and keep the previous file as archive.",
        "Record the resolution source as config/defaults.json in every preset purpose.",
    ],
    "example": {
        "entries": entries(
            ("config/presets/grade-warm.json", 2, "grade preset, defaults.json resolution source", "active"),
            ("config/presets/grade-warm-v1.json", 1, "previous grade preset", "archive"),
            ("config/presets/caption-bangla.json", 1, "caption preset, defaults.json resolution source", "active"),
            ("config/presets/brand-bar.json", 1, "brand preset, defaults.json resolution source", "active"),
        ),
        "summary": "Three active preset types registered with one archived earlier grade version.",
    },
    "quality": [
        "There is exactly one active entry for each of the three preset types.",
        "All paths start with config/presets/ and end in .json.",
        "Archived versions have a lower version number than their active counterpart.",
    ],
    "steps": [
        "Load the palette, font and resolution through project-memory before reading preset files.",
        "List JSON files under config/presets/ and group them by preset type.",
        "Compare file bytes with the last known version to decide which entry stays active.",
        "Rename older copies with a -v suffix and mark them archive instead of deleting them.",
        "Write the preset inventory to projects/<project>/07-edit/template-preset-manager.json.",
        "Validate the inventory schema and assert one active entry per preset type.",
    ],
    "test": "Validate projects/_template/07-edit/template-preset-manager.json with the inventory schema, then run `python tests/test_no_template.py`.",
    "failure": "If a preset type has no file, list it as draft with the expected path and stop before variant-batch-renderer. Never copy a preset from another project.",
}

SPECS["thumbnail-designer"] = {
    "name": "thumbnail-designer",
    "description": "Designs a clickable thumbnail.",
    "purpose": "Grab one representative frame from the finished Short and stamp the uppercase project title on it as a single PNG thumbnail.",
    "when": "Use after the final edit and before description-maker, when the video needs a still image that matches its title.",
    "inputs": ["- `projects/<project>/08-final-test/final-video.mp4`", "- `config/style-bible.json` font", "- `PROJECT` environment variable"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Thumbnail parameters",
    "criteria": [
        "Select frame 75 or the last available frame for shorter clips.",
        "Scale the selected frame to the configured resolution before drawing text.",
        "Draw the uppercase project title at fontsize 72 with x=60 and y=120.",
        "Write exactly one PNG and no audio stream.",
        "Verify with ffprobe that the PNG has the configured width and height.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/thumbnail-designer.png",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": False,
        "parameters": {"frame": 74, "fontsize": 72, "text_position": [60, 120], "format": "png"},
        "summary": "Frame 74 of a 3-second clip scaled to 1080x1920 with the project title at the top.",
    },
    "quality": [
        "Output path ends in .png and ffprobe reports one image.",
        "Frame index stays within the probed frame count of the source.",
        "Title text is uppercase and taken from the PROJECT value.",
    ],
    "steps": [
        "Read the title from the PROJECT value and the font from project-memory.",
        "Require ffmpeg and print BLOCKED with the FFMPEG_PATH hint when absent.",
        "Compute a safe frame index from the probed duration and fps.",
        "Build select, scale and drawtext filters in that order and limit output to one frame.",
        "Probe the PNG dimensions and confirm the file exists under projects/<project>/07-edit/.",
        "Write projects/<project>/07-edit/thumbnail-designer.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py thumbnail-designer --self-test` extracts a titled PNG from generated media and checks it with ffprobe.",
    "failure": "If the source video is missing, report the exact path and stop. If no font is configured, draw no text and write a WARN about the plain thumbnail.",
}

SPECS["variant-batch-renderer"] = {
    "name": "variant-batch-renderer",
    "description": "Renders multiple variants in batch.",
    "purpose": "Render three hue-shifted copies of one clip in a single FFmpeg run so title and thumbnail tests can compare visual variants cheaply.",
    "when": "Use after template-preset-manager and before ab-tester, when three visual variants must exist from the same source video.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `config/style-bible.json` palette", "- `config/presets/*.json` active presets"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Variant parameters",
    "criteria": [
        "Produce exactly three outputs named with -v1, -v2 and -v3 suffixes.",
        "Use hue 0 for the first copy and plus or minus 10 degrees per palette colour for the others.",
        "Split the input once and map each filtered branch to its own output file.",
        "Drop audio from all variants to keep the test focused on visuals.",
        "Probe every output with ffprobe and require identical configured resolution.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/variant-batch-renderer-v1.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": False,
        "parameters": {"variant_count": 3, "hue_step_deg": 40, "suffixes": ["v1", "v2", "v3"], "palette_count": 4},
        "summary": "Three silent variants rendered with hue 0, +40 and -40 degrees from a four-colour palette.",
    },
    "quality": [
        "Report parameters list three suffixes and a hue step derived from palette count.",
        "Every variant path exists after the run.",
        "All probed resolutions equal config/defaults.json resolution.",
    ],
    "steps": [
        "Read the palette count and resolution through project-memory before choosing hue offsets.",
        "Check ffmpeg availability and emit BLOCKED if the executable is missing.",
        "Build a three-way split with a hue filter on each branch.",
        "Map each branch to a separate output with libx264 veryfast and no audio.",
        "Probe all three files and collect their durations and dimensions.",
        "Write projects/<project>/07-edit/variant-batch-renderer.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py variant-batch-renderer --self-test` renders three variants and probes each with ffprobe.",
    "failure": "If fewer than three presets are active, render the neutral variant only and write a WARN listing the missing presets. Do not reuse another project's presets.",
}

SPECS["video-editor"] = {
    "name": "video-editor",
    "description": "Applies final edits and trims.",
    "purpose": "Remove a small lead-in and tail from a rough cut using matched video and audio trims so the final clip starts and ends cleanly.",
    "when": "Use after rough-cut-assembler and before final-test, when the scenes are correct but the first and last fractions of a second need trimming.",
    "inputs": ["- `projects/<project>/07-edit/rough-cut.mp4`", "- `projects/<project>/02-script/retention-pacing-optimizer.json`", "- `config/defaults.json` resolution"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Trim parameters",
    "criteria": [
        "Trim the same number of seconds from the head and tail of both video and audio.",
        "Set the trim length to 25% of the source duration, capped at 0.3 seconds.",
        "Normalise timestamps with setpts and asetpts after trimming.",
        "Re-encode video with libx264 veryfast and audio with AAC 128k.",
        "Confirm output duration is the source duration minus twice the trim, within 0.1 seconds.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/video-editor.mp4",
        "duration_sec": 2.5,
        "width": 1080,
        "height": 1920,
        "has_audio": True,
        "parameters": {"trim_head_sec": 0.25, "trim_tail_sec": 0.25, "video_codec": "libx264", "audio_codec": "aac"},
        "summary": "A 3-second rough cut trimmed by 0.25 seconds at each end to produce a 2.5-second final clip.",
    },
    "quality": [
        "Head and trim values in the report are equal.",
        "Output duration matches the expected subtraction within tolerance.",
        "ffprobe reports audio=True and configured resolution.",
    ],
    "steps": [
        "Open the pacing notes from project-memory and probe the rough cut duration.",
        "Verify ffmpeg is configured before building any trim filter.",
        "Compute the capped trim length and apply it to both video and audio branches.",
        "Reset both timestamp streams and map them to the output file.",
        "Probe the edited clip and compare its duration to the calculated target.",
        "Write projects/<project>/07-edit/video-editor.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py video-editor --self-test` trims generated media and verifies duration and audio with ffprobe.",
    "failure": "If the source is shorter than 1 second, copy it unchanged with a WARN. If ffmpeg is unavailable, print BLOCKED and make no edit.",
}

SPECS["virtual-camera-planner"] = {
    "name": "virtual-camera-planner",
    "description": "Plans virtual camera moves.",
    "purpose": "Write a timed camera plan that tells the SVG renderer when to pan or zoom a flat scene while keeping every caption inside the safe zone.",
    "when": "Use after scenario-designer and before video-maker, when a static layout needs controlled movement instead of random animation.",
    "inputs": ["- `projects/<project>/05-scene/scenario-designer.json`", "- `config/style-bible.json` safe margins", "- `config/defaults.json` resolution"],
    "schema": "plan",
    "criteria_heading": "# Camera move constraints",
    "criteria": [
        "Allow at most two camera moves per scene.",
        "Keep each move between 2 and 5 seconds.",
        "Cap zoom changes at 8% so flat art does not pixelate.",
        "Never pan the bottom 15% of the frame where captions sit.",
        "Give each move an explicit reason tied to the scene's visual job.",
    ],
    "example": {
        "items": actions(
            (1, "Zoom 4% toward the coffee cup", 0, 3, "draws attention to the hook object"),
            (2, "Pan right across the notebook", 8, 12, "reveals the side-hustle prop"),
            (3, "Hold camera steady", 38, 45, "keeps the loop line readable"),
        ),
        "constraints": ["max 2 moves per scene", "zoom change at most 8%", "bottom 15% protected"],
        "summary": "Three timed camera decisions with modest zoom and a protected caption band.",
    },
    "quality": [
        "No item duration is under 2 or over 5 seconds except an explicit hold.",
        "Every action names a zoom or pan direction and a magnitude.",
        "Constraints include the bottom 15% protection rule.",
    ],
    "steps": [
        "Read safe margins and resolution from project-memory before opening the scene layout.",
        "Validate projects/<project>/05-scene/scenario-designer.json and list its scenes.",
        "Assign at most two moves per scene with durations between 2 and 5 seconds.",
        "Check each zoom against the 8% cap and each pan against the caption band.",
        "Write the camera plan to projects/<project>/05-scene/virtual-camera-planner.json.",
        "Validate the plan schema and report any scene that exceeds the move limit.",
    ],
    "test": "Validate projects/_template/05-scene/virtual-camera-planner.json with the plan schema, then run `python tests/test_no_template.py`.",
    "failure": "If the scene layout is missing, stop and name the path. If a move would violate the caption band, replace it with a hold and add a WARN instead of shifting captions.",
}

SPECS["watermark-logo-placer"] = {
    "name": "watermark-logo-placer",
    "description": "Places the channel watermark or logo.",
    "purpose": "Overlay a small local logo in the top-right corner of every edited clip so the channel is visible without covering captions or the hook object.",
    "when": "Use after branding-manager and before handover, when a logo file exists and must appear consistently on all outputs.",
    "inputs": ["- `assets/brand/*.png` or `assets/scenes/*.png` local logo", "- `projects/<project>/07-edit/rough-cut.mp4`", "- `config/defaults.json` resolution"],
    "schema": "media-effect",
    "ffmpeg": True,
    "criteria_heading": "# Watermark parameters",
    "criteria": [
        "Scale the logo to exactly 120 by 120 pixels.",
        "Place it at x = width minus 150 and y = 40 to keep clear of the caption band.",
        "Use the overlay filter with format=auto so transparent PNGs composite correctly.",
        "Keep the source audio when present and encode it as AAC 128k.",
        "Verify with ffprobe that resolution and duration are unchanged and audio survives when the source had it.",
    ],
    "example": {
        "video": "projects/<project>/07-edit/watermark-logo-placer.mp4",
        "duration_sec": 3.0,
        "width": 1080,
        "height": 1920,
        "has_audio": True,
        "parameters": {"logo_size": "120x120", "overlay": "x=w-150:y=40", "format": "auto", "source": "local PNG"},
        "summary": "Local logo scaled to 120px and overlaid in the top-right corner with audio preserved.",
    },
    "quality": [
        "Overlay expression uses w-150 and y=40.",
        "Logo path is local and ends in .png.",
        "ffprobe confirms configured resolution and unchanged duration.",
    ],
    "steps": [
        "Read the resolution from config/defaults.json through project-memory and locate a local logo PNG.",
        "Confirm ffmpeg is available or return BLOCKED with the FFMPEG_PATH hint.",
        "Scale the logo input to 120x120 and overlay it using width-relative coordinates.",
        "Map the original audio when available and encode with libx264 plus AAC.",
        "Probe the watermarked file and compare it with the source metadata.",
        "Write projects/<project>/07-edit/watermark-logo-placer.json and validate the media-effect schema.",
    ],
    "test": "`python scripts/skill_tools.py watermark-logo-placer --self-test` overlays a generated logo and verifies the output with ffprobe.",
    "failure": "If no local logo exists, use the first scene PNG as a temporary mark and write a WARN with its path. Never download a channel logo.",
}


# ---------------------------------------------------------------------------
# Batch D — critique, marketing and growth (manual-input skills use no APIs)
# ---------------------------------------------------------------------------

SPECS["ruthless-team"] = {
    "name": "ruthless-team",
    "description": "Gives a harsh quality critique.",
    "purpose": "Deliver an unkind but evidence-based critique of the final Short so weak hooks and vague numbers are caught before publication.",
    "when": "Use after red-team and before bug-finder, when friendly review has gone soft and a blunt second opinion is needed.",
    "inputs": ["- `projects/<project>/08-final-test/final-video.mp4`", "- `projects/<project>/08-final-test/red-team.json`", "- `projects/<project>/02-script/latest_script.json`"],
    "schema": "analysis",
    "criteria_heading": "# Harsh critique criteria",
    "criteria": [
        "Score exactly four dimensions: hook, trust, originality and call to action.",
        "A score of 5 or lower requires a finding written in plain Bangla with no softener words.",
        "Quote the exact second of the worst moment in each finding.",
        "Do not repeat a red-team finding unless the video still shows the same problem.",
        "Praise is not allowed; findings must only name defects and fixes.",
    ],
    "example": {
        "criteria": scored(
            ("hook", 3, "money figure appears at 4.2 seconds, far too late"),
            ("trust", 5, "monthly total has no source in the script"),
            ("originality", 7, "coffee example is common but the loop is fresh"),
            ("call to action", 4, "no replay instruction anywhere in the final 3 seconds"),
        ),
        "findings": ["Steam roller: put ৳120 in second 1, not second 5.", "The ৳3,600 claim is unsupported; cut it."],
        "summary": "Four dimensions scored; hook and call to action are the two worst and need fixes before release.",
    },
    "quality": [
        "There are exactly four scored criteria with the required names.",
        "Every finding includes a second or a script line.",
        "No finding contains reassuring words such as 'good' or 'nice'.",
    ],
    "steps": [
        "Load language and niche from project-memory so the blunt wording stays in Bangla.",
        "Read red-team.json first and mark which problems are already reported.",
        "Watch the final video metadata and score hook, trust, originality and call to action.",
        "Write one harsh finding per dimension scoring 5 or below, each with a timestamp.",
        "Save the critique to projects/<project>/08-final-test/ruthless-team.json.",
        "Validate the analysis schema and check that no finding merely repeats red-team.json.",
    ],
    "test": "Validate projects/_template/08-final-test/ruthless-team.json with the analysis schema, then run `python tests/test_no_template.py`.",
    "failure": "If the final video is absent, name the path and stop. If red-team.json is absent, continue but record the missing context in the summary instead of inventing prior findings.",
}

SPECS["solver"] = {
    "name": "solver",
    "description": "Proposes fixes for reported bugs.",
    "purpose": "Turn each confirmed bug into one small, ordered fix that can be applied and re-tested without re-rendering the whole Short.",
    "when": "Use after bug-finder and before final render, when the defect list is known but nobody has decided which fix comes first.",
    "inputs": ["- `projects/<project>/08-final-test/bug-finder.json`", "- `projects/<project>/08-final-test/ruthless-team.json`", "- `config/style-bible.json` constraints"],
    "schema": "plan",
    "criteria_heading": "# Fix ordering rules",
    "criteria": [
        "Create at most five fixes and order them by severity, highest first.",
        "Every fix must name the exact bug id it resolves.",
        "Give each fix an effort window of 30 to 300 seconds.",
        "Never propose a fix that changes the locked script duration.",
        "Prefer a trim, label change or local re-render over rebuilding every scene.",
    ],
    "example": {
        "items": actions(
            (1, "Move the ৳120 label to second 1", 0, 90, "fixes bug-01 hook delay"),
            (2, "Remove the unsupported ৳3,600 line", 90, 150, "fixes bug-02 missing source"),
            (3, "Add the replay CTA to the last frame", 150, 240, "fixes bug-03 weak ending"),
        ),
        "constraints": ["max 5 fixes", "effort 30-300 seconds each", "locked duration unchanged"],
        "summary": "Three ordered fixes mapped to bug ids, all achievable without re-rendering the full video.",
    },
    "quality": [
        "No two items reference the same bug id.",
        "Each effort window is between 30 and 300 seconds.",
        "The constraints include the locked-duration rule.",
    ],
    "steps": [
        "Read style constraints through project-memory, then load the confirmed bug list.",
        "Validate projects/<project>/08-final-test/bug-finder.json and extract bug ids.",
        "Rank bugs by severity and keep only the top five.",
        "Write one concrete fix per bug with a 30–300 second effort window.",
        "Save the fix plan to projects/<project>/08-final-test/solver.json.",
        "Validate the plan schema and assert no bug id is used twice.",
    ],
    "test": "Validate projects/_template/08-final-test/solver.json with the plan schema, then run `python tests/test_no_template.py`.",
    "failure": "If no bug report exists, stop and name the missing file. If more than five bugs are confirmed, keep the five highest severity and list the rest in the summary as deferred.",
}

SPECS["copywriter"] = {
    "name": "copywriter",
    "description": "Writes marketing copy for the video.",
    "purpose": "Choose one Bangla copy angle for the Short and produce the one-line pitch, description opening and hashtag set that match the audience persona.",
    "when": "Use after final-test and before description-maker, when the video is approved but the supporting words are still missing.",
    "inputs": ["- `projects/<project>/02-script/latest_script.json`", "- `projects/<project>/01-research/audience-persona-builder.json`", "- `config/channel.json` tone"],
    "schema": "selection",
    "criteria_heading": "# Copy angle scoring",
    "criteria": [
        "Draft exactly three angles and pick one.",
        "Score each 0–10 for persona fit, clarity of money benefit and Bangla naturalness.",
        "Keep the pitch line under 60 Bangla characters.",
        "Use at most three hashtags, all written in Bangla.",
        "Never promise a guaranteed income or use words implying get-rich-quick results.",
    ],
    "example": {
        "candidates": candidates(
            ("angle-01", 9, "one coffee equals ৳120, under 60 characters"),
            ("angle-02", 6, "too vague about the saving benefit"),
            ("angle-03", 7, "good benefit but over 60 characters"),
        ),
        "chosen_id": "angle-01",
        "rationale": "Highest persona fit and clarity; pitch stays under 60 Bangla characters with three Bangla hashtags.",
    },
    "quality": [
        "There are three candidates and one chosen id from that list.",
        "No rationale contains an income guarantee.",
        "All hashtag examples are written in Bangla script.",
    ],
    "steps": [
        "Read tone and language from project-memory before opening the persona shortlist.",
        "Validate the final script and extract its single money benefit.",
        "Draft three short Bangla angles and score them against the numeric rules.",
        "Select the winner and write a pitch line, description opening and three hashtags.",
        "Save the copy choice to projects/<project>/09-description/copywriter.json.",
        "Validate the selection schema and count the pitch characters.",
    ],
    "test": "Validate projects/_template/09-description/copywriter.json with the selection schema, then run `python tests/test_no_template.py`.",
    "failure": "If the persona shortlist is missing, report the path and stop. If no angle reaches 7 points, return WARN with the best angle instead of inventing a stronger claim.",
}

SPECS["marketing-specialist"] = {
    "name": "marketing-specialist",
    "description": "Plans promotion across channels.",
    "purpose": "Build a three-channel promotion plan with fixed posting windows so one Short can be promoted without spamming the same audience everywhere.",
    "when": "Use after handover and before scheduler-publisher, when the final assets are ready and promotion still needs a plan.",
    "inputs": ["- `projects/<project>/10-publish/handover.md`", "- `projects/<project>/01-research/audience-persona-builder.json`", "- `config/channel.json` platform list"],
    "schema": "plan",
    "criteria_heading": "# Promotion constraints",
    "criteria": [
        "Use at most three channels from config/channel.json.",
        "Stagger the first two posts by at least 60 minutes.",
        "Give each channel one job: discovery, saves or community.",
        "Write every on-screen or caption line in Bangla for this channel.",
        "Do not promise cross-posting to a platform absent from the channel config.",
    ],
    "example": {
        "items": actions(
            (1, "Post the Short to YouTube", 0, 45, "discovery job at 19:00 BST"),
            (2, "Share a still to Facebook at 20:15", 60, 75, "community job, 75-minute stagger"),
            (3, "Pin a Bangla comment with the saving tip", 90, 100, "saves job"),
        ),
        "constraints": ["max 3 channels", "60-minute minimum stagger", "Bangla copy only"],
        "summary": "Three promotion actions across YouTube and Facebook with a staggered schedule and distinct jobs.",
    },
    "quality": [
        "Every action names a channel present in config/channel.json.",
        "The first two posting items differ by at least 60 minutes.",
        "The constraints list the Bangla copy rule.",
    ],
    "steps": [
        "Load platform list and language from project-memory before reading the handover file.",
        "Confirm projects/<project>/10-publish/handover.md exists and lists the final assets.",
        "Assign one job to each of at most three configured channels.",
        "Stagger posting windows by at least 60 minutes and write Bangla copy notes.",
        "Save the promotion plan to projects/<project>/09-description/marketing-specialist.json.",
        "Validate the plan schema and check every channel name against the config.",
    ],
    "test": "Validate projects/_template/09-description/marketing-specialist.json with the plan schema, then run `python tests/test_no_template.py`.",
    "failure": "If handover.md is missing, stop and report the path. If fewer than two platforms are configured, plan a single channel and write a WARN about the reduced reach.",
}

SPECS["seo-specialist"] = {
    "name": "seo-specialist",
    "description": "Optimizes keywords and metadata.",
    "purpose": "Score the description's keyword choices against local search notes and return the three concrete metadata edits with the highest expected payoff.",
    "when": "Use after description-maker and before growth, when the title and description exist but keyword placement is still guesswork.",
    "inputs": ["- `projects/<project>/09-description/description.md`", "- `research/keyword-notes.md` (manual notes, no API)", "- `config/channel.json` language"],
    "schema": "analysis",
    "criteria_heading": "# Keyword criteria",
    "criteria": [
        "Score exactly three dimensions: title match, first-line match and Bangla spelling.",
        "A dimension scores 10 only when the keyword from keyword-notes.md appears verbatim.",
        "Require the main keyword in the first 60 characters of the description.",
        "Reject any English keyword that displaces an equivalent Bangla term.",
        "Every finding must quote the exact phrase to add or move.",
    ],
    "example": {
        "source_file": "research/keyword-notes.md",
        "criteria": scored(
            ("title match", 8, "সাইড হুস্টল appears in the title"),
            ("first-line match", 4, "keyword first appears at character 91"),
            ("Bangla spelling", 9, "spelling matches the manual note"),
        ),
        "findings": ["Move 'সাইড হুস্টল' into the first 60 characters.", "Do not replace it with the English word 'side hustle'."],
        "summary": "Three keyword dimensions scored; first-line placement is the single metadata fix needed.",
    },
    "quality": [
        "There are exactly three scored criteria with the required names.",
        "Each finding quotes a phrase from the manual notes.",
        "No suggested keyword is written only in Latin script.",
    ],
    "steps": [
        "Read language through project-memory and open research/keyword-notes.md.",
        "Load the generated description and measure where the main keyword first appears.",
        "Score title match, first-line match and Bangla spelling on the 0–10 scale.",
        "Write each metadata fix as a finding that quotes the exact phrase.",
        "Save the review to projects/<project>/09-description/seo-specialist.json.",
        "Validate the analysis schema and confirm no finding invents a keyword.",
    ],
    "test": "Add one Bangla keyword to research/keyword-notes.md, run the skill, then `python tests/test_no_template.py`.",
    "failure": "If keyword-notes.md is missing, report BLOCKED and produce no scores. Never query a search API or invent search volume for this skill.",
}

SPECS["ab-tester"] = {
    "name": "ab-tester",
    "description": "Runs A/B tests on titles and thumbnails.",
    "purpose": "Compare two manually exported title or thumbnail variants and declare a winner only when both arms have enough impressions.",
    "when": "Use after analytics export is available in 10-publish/inputs/ and before analytics-feedback-loop, when a title or thumbnail choice must be made from evidence.",
    "inputs": [
        "projects/<project>/10-publish/inputs/ab-results.json (manual export; no API access)",
        "projects/<project>/09-description/description.md",
    ],
    "schema": "manual-input",
    "api_needed": True,
    "criteria_heading": "# Test validity rules",
    "criteria": [
        "Require at least 100 impressions in each arm before declaring a winner.",
        "Compute click-through rate as clicks divided by impressions, rounded to two decimals.",
        "Declare a winner only when the CTR gap is at least 0.02.",
        "Compare exactly two variants: A and B; ignore any third row.",
        "Never call a platform API or generate missing export rows.",
    ],
    "example": {
        "api_needed": "later",
        "source_file": "projects/<project>/10-publish/inputs/ab-results.json",
        "rows": [
            {"variant": "A", "impressions": 1200, "clicks": 96, "ctr": 0.08},
            {"variant": "B", "impressions": 1180, "clicks": 71, "ctr": 0.06},
        ],
        "summary": "Manual export has 1200 and 1180 impressions; variant A wins by 0.02 CTR with a valid sample.",
    },
    "quality": [
        "Rows contain exactly two variants named A and B.",
        "Both impression counts are at least 100.",
        "Summary names the winner only if the CTR gap meets 0.02.",
    ],
    "steps": [
        "Confirm the manual export exists at projects/<project>/10-publish/inputs/ab-results.json.",
        "Read both rows and reject any variant label other than A or B.",
        "Check the 100-impression minimum on each arm before computing rates.",
        "Calculate both CTR values and their absolute gap.",
        "Write the comparison to projects/<project>/10-publish/ab-tester.json.",
        "Validate the manual-input schema and record api_needed as later.",
    ],
    "test": "Save two A/B rows under projects/_template/10-publish/inputs/ and run `python tests/test_no_template.py`.",
    "failure": "If the export is missing, report the exact path and stop; never fabricate impressions. If either arm is under 100 impressions, write INCONCLUSIVE in the summary and declare no winner.",
}

SPECS["analytics-feedback-loop"] = {
    "name": "analytics-feedback-loop",
    "description": "Feeds results back into research.",
    "purpose": "Convert a manually exported performance report into three research notes that the next story-thinker run can actually use.",
    "when": "Use after youtube-analyst and before the next research phase, when the team needs to change its topic choices based on past results.",
    "inputs": ["- `projects/<project>/10-publish/inputs/analytics-report.json` (manual export; no API access)", "- `research/niche-report.md`"],
    "schema": "manual-input",
    "api_needed": True,
    "criteria_heading": "# Feedback rules",
    "criteria": [
        "Use at least 5 published videos from the export before drawing a conclusion.",
        "Rank videos by save rate, not by raw views, because this niche is educational.",
        "Write exactly three research notes in the summary.",
        "Each note must name a topic or format from research/niche-report.md.",
        "Never infer demographics that are absent from the export.",
    ],
    "example": {
        "api_needed": "later",
        "source_file": "projects/<project>/10-publish/inputs/analytics-report.json",
        "rows": [
            {"video": "coffee-price", "views": 4200, "saves": 310, "save_rate": 0.074},
            {"video": "side-hustle", "views": 2800, "saves": 260, "save_rate": 0.093},
        ],
        "summary": "Top save rate is the side-hustle format; add two more side-hustle topics and keep the coffee hook style in the next research round.",
    },
    "quality": [
        "Summary contains exactly three research notes.",
        "Each note mentions a topic present in the niche report.",
        "No row contains a demographic field that was not exported.",
    ],
    "steps": [
        "Check that projects/<project>/10-publish/inputs/analytics-report.json exists before reading anything.",
        "Count rows and stop with WARN when fewer than five videos are present.",
        "Rank the exported videos by save rate and note the top format.",
        "Compare that format with topics listed in research/niche-report.md.",
        "Write three concrete research notes into the summary.",
        "Save the feedback file to projects/<project>/10-publish/analytics-feedback-loop.json and validate its schema.",
    ],
    "test": "Export five sample rows under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.",
    "failure": "If the manual analytics export is missing, name the path and stop. Never call a YouTube API or invent view and save numbers.",
}

SPECS["comment-community-manager"] = {
    "name": "comment-community-manager",
    "description": "Manages comments and community replies.",
    "purpose": "Sort a manual comment export into questions, praise and objections, then draft Bangla replies for the questions and objections only.",
    "when": "Use after a video is published and its comments have been exported to 10-publish/inputs/, before the next research round.",
    "inputs": ["- `projects/<project>/10-publish/inputs/comments-export.json` (manual export; no API access)", "- `config/channel.json` tone"],
    "schema": "manual-input",
    "api_needed": True,
    "criteria_heading": "# Reply rules",
    "criteria": [
        "Require at least 5 exported comments before drafting any reply.",
        "Classify every row as question, praise or objection.",
        "Draft replies only for questions and objections.",
        "Write each reply in Bangla and keep it under 120 characters.",
        "Never promise a personal finance outcome or ask for private financial details.",
    ],
    "example": {
        "api_needed": "later",
        "source_file": "projects/<project>/10-publish/inputs/comments-export.json",
        "rows": [
            {"id": 1, "text": "এই টাকা কীভাবে বাঁচাব?", "type": "question", "reply": "প্রতিদিন ২০ টাকা আলাদা রাখুন, তারপর মাসে যোগ করুন।"},
            {"id": 2, "text": "ভালো ভিডিও", "type": "praise", "reply": ""},
        ],
        "summary": "Two exported comments sorted; one Bangla reply drafted for the question, praise left unanswered by design.",
    },
    "quality": [
        "Every row has exactly one of the three allowed types.",
        "Praise rows have an empty reply string.",
        "All drafted replies are under 120 characters and written in Bangla.",
    ],
    "steps": [
        "Confirm projects/<project>/10-publish/inputs/comments-export.json exists and read the tone from project-memory.",
        "Validate that every exported row has text and an id.",
        "Label each row as question, praise or objection.",
        "Draft short Bangla replies for non-praise rows and leave praise replies empty.",
        "Write the reply set to projects/<project>/10-publish/comment-community-manager.json.",
        "Validate the manual-input schema and check reply character counts.",
    ],
    "test": "Export five sample comments under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.",
    "failure": "If the export is missing, report the path and stop. Never invent a viewer comment or reply as if it came from a real user.",
}

SPECS["cross-platform-repurposer"] = {
    "name": "cross-platform-repurposer",
    "description": "Adapts videos for other platforms.",
    "purpose": "Plan local crops and caption adjustments for reposting one finished Short to two additional platforms without new scripting or API calls.",
    "when": "Use after handover and before scheduler-publisher, when the same video must serve Facebook and another configured platform.",
    "inputs": ["- `projects/<project>/08-final-test/final-video.mp4`", "- `config/channel.json` platform list", "- `config/defaults.json` resolution"],
    "schema": "plan",
    "criteria_heading": "# Repurposing constraints",
    "criteria": [
        "Plan at most two additional platforms beyond the primary one.",
        "Keep the 9:16 layout for Reels-style feeds and never stretch to 16:9.",
        "Move captions inward by 5% of width for platforms with right-side controls.",
        "Keep the original 30–60 second duration; do not add intro cards.",
        "List only platforms present in config/channel.json.",
    ],
    "example": {
        "items": actions(
            (1, "Export 9:16 copy for Facebook Reels", 0, 45, "same frame size, caption inset 5%"),
            (2, "Export square crop preview for the feed", 0, 45, " centred crop keeps the hook object visible"),
            (3, "Replace the CTA with a Bangla follow line", 42, 45, "platform-specific ending, same duration"),
        ),
        "constraints": ["max 2 extra platforms", "no 16:9 stretch", "original duration preserved"],
        "summary": "Two local export plans and one CTA swap, all using the finished video without external services.",
    },
    "quality": [
        "Every item names a configured platform or a local crop action.",
        "No action increases the video duration.",
        "Constraints include the no-16:9-stretch rule.",
    ],
    "steps": [
        "Read the platform list and resolution from project-memory before opening the final video path.",
        "Confirm projects/<project>/08-final-test/final-video.mp4 exists locally.",
        "Choose at most two configured platforms and state the crop rule for each.",
        "Adjust caption inset by 5% in the plan for platforms with overlays.",
        "Write the repurposing plan to projects/<project>/10-publish/cross-platform-repurposer.json.",
        "Validate the plan schema and confirm no platform name is invented.",
    ],
    "test": "Validate projects/_template/10-publish/cross-platform-repurposer.json with the plan schema, then run `python tests/test_no_template.py`.",
    "failure": "If the final video is missing, name the path and stop. If only one platform is configured, return WARN with a single-platform plan instead of inventing a destination.",
}

SPECS["monetization-tracker"] = {
    "name": "monetization-tracker",
    "description": "Tracks revenue and monetization.",
    "purpose": "Summarise a manually exported revenue file in Bangla taka and flag any row where the amount and views do not agree with the stated rate.",
    "when": "Use after a video earns revenue and its statement has been exported to 10-publish/inputs/, before the next planning round.",
    "inputs": ["- `projects/<project>/10-publish/inputs/revenue-export.json` (manual export; no API access)", "- `config/channel.json` currency"],
    "schema": "manual-input",
    "api_needed": True,
    "criteria_heading": "# Revenue checks",
    "criteria": [
        "Require at least 3 exported rows before reporting a trend.",
        "Keep every amount in Bangla taka; never convert to another currency.",
        "Flag a row when amount divided by views differs from the stated rate by more than 20%.",
        "Report totals as whole taka with no decimal paise.",
        "Never estimate revenue for a video missing from the export.",
    ],
    "example": {
        "api_needed": "later",
        "source_file": "projects/<project>/10-publish/inputs/revenue-export.json",
        "rows": [
            {"video": "coffee-price", "views": 4200, "amount_taka": 1260, "rate": 0.3},
            {"video": "side-hustle", "views": 2800, "amount_taka": 700, "rate": 0.3},
        ],
        "summary": "Two exported rows total 1960 taka; neither row deviates from its stated rate by more than 20 percent.",
    },
    "quality": [
        "Every amount field is named amount_taka and is an integer.",
        "The summary contains a whole-taka total.",
        "No row has an estimated or invented view count.",
    ],
    "steps": [
        "Confirm the manual revenue export exists under projects/<project>/10-publish/inputs/.",
        "Read the currency from project-memory and reject any row using another currency symbol.",
        "Count rows and compute the whole-taka total.",
        "Compare each amount with views times rate and flag deviations over 20 percent.",
        "Write the tracker output to projects/<project>/10-publish/monetization-tracker.json.",
        "Validate the manual-input schema and confirm every amount is an integer.",
    ],
    "test": "Export three sample revenue rows under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.",
    "failure": "If the export is missing, report the path and stop. Never call a monetization API or guess earnings for a video absent from the export.",
}

SPECS["scheduler-publisher"] = {
    "name": "scheduler-publisher",
    "description": "Schedules and publishes videos.",
    "purpose": "Produce a validated publishing schedule from a manual request file; this skill never contacts a platform and never marks a video as actually published.",
    "when": "Use after handover and marketing-specialist, when posting times are agreed and a human will perform the upload.",
    "inputs": [
        "projects/<project>/10-publish/inputs/schedule-requests.json (manual export; no API access)",
        "projects/<project>/01-research/content-calendar.json",
        "projects/<project>/10-publish/handover.md",
    ],
    "schema": "manual-input",
    "api_needed": True,
    "criteria_heading": "# Schedule checks",
    "criteria": [
        "Require the handover file to exist before accepting any request row.",
        "Allow at most one upload per platform per calendar day.",
        "Keep every posted time in Bangladesh local time and label it BST.",
        "Compare each request with the content calendar and flag unplanned videos.",
        "Mark every row as planned only; never write published or live as a status.",
    ],
    "example": {
        "api_needed": "later",
        "source_file": "projects/<project>/10-publish/inputs/schedule-requests.json",
        "rows": [
            {"platform": "youtube", "video": "coffee-price", "when": "2026-11-23 19:00 BST", "status": "planned"},
            {"platform": "facebook", "video": "coffee-price", "when": "2026-11-23 20:15 BST", "status": "planned"},
        ],
        "summary": "Two planned uploads validated against the calendar; a human must perform the actual publishing.",
    },
    "quality": [
        "Every row status is exactly planned.",
        "No platform has two rows on the same date.",
        "Each when value ends with BST.",
    ],
    "steps": [
        "Verify projects/<project>/10-publish/handover.md exists and read the calendar through project-memory.",
        "Load the manual schedule requests from projects/<project>/10-publish/inputs/schedule-requests.json.",
        "Reject duplicate platform-and-day pairs and unplanned video names.",
        "Normalise every timestamp to a BST-labelled string.",
        "Write the validated schedule to projects/<project>/10-publish/scheduler-publisher.json.",
        "Validate the manual-input schema and assert no row claims a published state.",
    ],
    "test": "Save two schedule rows under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.",
    "failure": "If handover.md is missing, stop and name the path. This skill cannot publish; if the user expects a live upload, tell them to use GitHub Desktop sign-in or `gh auth login` for a future API-enabled version.",
}

SPECS["youtube-analyst"] = {
    "name": "youtube-analyst",
    "description": "Analyzes channel performance.",
    "purpose": "Summarise a manual YouTube analytics export into three scored dimensions that describe retention, reach and saving behaviour.",
    "when": "Use after videos are published and the analytics file has been exported to 10-publish/inputs/, before analytics-feedback-loop.",
    "inputs": ["- `projects/<project>/10-publish/inputs/youtube-analytics-export.json` (manual export; no API access)", "- `config/channel.json` length target"],
    "schema": "manual-input",
    "api_needed": True,
    "criteria_heading": "# Analysis dimensions",
    "criteria": [
        "Require at least 5 exported videos before scoring a dimension.",
        "Score retention from average view duration divided by the video length, capped at 10.",
        "Score reach from impressions relative to the median of the exported set.",
        "Score saves from the save count relative to views, multiplied by 100 and capped at 10.",
        "Never report a metric that is absent from the export; write unavailable instead.",
    ],
    "example": {
        "api_needed": "later",
        "source_file": "projects/<project>/10-publish/inputs/youtube-analytics-export.json",
        "rows": [
            {"video": "coffee-price", "views": 4200, "avg_view_sec": 31, "video_sec": 45, "impressions": 9000, "saves": 310},
            {"video": "side-hustle", "views": 2800, "avg_view_sec": 38, "video_sec": 45, "impressions": 5200, "saves": 260},
        ],
        "summary": "Five exported videos scored: retention 7/10, reach 6/10, saves 8/10; saving behaviour is the strongest signal.",
    },
    "quality": [
        "Summary reports exactly three scores in the form n/10.",
        "No row contains a metric missing from the export.",
        "Scores never exceed 10.",
    ],
    "steps": [
        "Confirm the manual export exists under projects/<project>/10-publish/inputs/.",
        "Read the target length from project-memory and count exported rows.",
        "Compute retention, reach and save scores using only exported fields.",
        "Write the three scores and their evidence into the summary.",
        "Save the report to projects/<project>/10-publish/youtube-analyst.json.",
        "Validate the manual-input schema and mark api_needed as later.",
    ],
    "test": "Export five sample analytics rows under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.",
    "failure": "If fewer than five rows are exported, write INSUFFICIENT DATA in the summary. Never call the YouTube API or fabricate impressions, views or saves.",
}

SPECS["youtube-seo-specialist"] = {
    "name": "youtube-seo-specialist",
    "description": "Optimizes for YouTube search and Shorts.",
    "purpose": "Rank manually exported keywords for a Bangla Short and choose the one phrase that should lead the title and first caption line.",
    "when": "Use after seo-specialist and before publishing, when a keyword export exists in 10-publish/inputs/ and the title needs a final choice.",
    "inputs": ["- `projects/<project>/10-publish/inputs/keyword-export.json` (manual export; no API access)", "- `projects/<project>/09-description/description.md`"],
    "schema": "manual-input",
    "api_needed": True,
    "criteria_heading": "# Keyword ranking rules",
    "criteria": [
        "Require at least 5 exported keywords before choosing a leader.",
        "Score each keyword as volume divided by competition, capped at 10.",
        "Prefer Bangla-script keywords when two candidates tie.",
        "Reject any keyword that does not appear in the script or description.",
        "Never invent search volume or query a search API.",
    ],
    "example": {
        "api_needed": "later",
        "source_file": "projects/<project>/10-publish/inputs/keyword-export.json",
        "rows": [
            {"keyword": "সাইড হুস্টল", "volume": 1200, "competition": 150, "score": 8},
            {"keyword": "টাকা বাঁচানো", "volume": 900, "competition": 120, "score": 7.5},
        ],
        "summary": "Five manual keywords ranked; 'সাইড হুস্টল' leads the title and the first Bangla caption line.",
    },
    "quality": [
        "Every score equals volume divided by competition, capped at 10.",
        "The leading keyword appears in the description file.",
        "No row contains a keyword absent from the manual export.",
    ],
    "steps": [
        "Check projects/<project>/10-publish/inputs/keyword-export.json exists before reading the description.",
        "Count rows and stop with WARN when fewer than five keywords are exported.",
        "Compute each score from volume and competition using exported numbers only.",
        "Filter out keywords missing from the script or description, then pick the top scorer.",
        "Write the ranking to projects/<project>/10-publish/youtube-seo-specialist.json.",
        "Validate the manual-input schema and confirm api_needed is set to later.",
    ],
    "test": "Export five sample keywords under projects/_template/10-publish/inputs/ then run `python tests/test_no_template.py`.",
    "failure": "If the keyword export is missing, report the exact path and stop. Never fabricate a search volume, a competition score, or an API result.",
}


BATCH_OF = {name: number for number, names in BATCHES.items() for name in names}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, choices=sorted(BATCHES))
    args = parser.parse_args()
    names = BATCHES[args.batch]
    missing = [name for name in names if name not in SPECS]
    if missing:
        print(f"FAIL batch {args.batch}: missing specs for {', '.join(missing)}")
        return 1
    for name in names:
        path = SKILLS_DIR / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(SPECS[name]), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    sync_registry(names)
    print(f"Batch {args.batch}: {len(names)} skills rewritten to REAL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
