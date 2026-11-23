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
        body.append(f"- {item}")
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
    "B": [],
    "C": [],
    "D": [],
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
