#!/usr/bin/env python3
"""Generate edge-tts voiceover audio and word-level caption timing metadata."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts is not installed. Install it with: pip install edge-tts")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCRIPT = ROOT / "scripts" / "latest_script.json"
FALLBACK_SCRIPT = ROOT / "projects" / "_template" / "02-script" / "latest_script.json"

VOICES = {
    "bn": {"male": "bn-BD-PradeepNeural", "female": "bn-BD-NabanitaNeural"},
    "en": {"male": "en-US-AndrewNeural", "female": "en-US-AvaNeural"},
}

WORD_RE = re.compile(r"\S+")
TRIM_RE = re.compile(r"^[\s\.,!?;:'\"()\[\]{}।،—–-]+|[\s\.,!?;:'\"()\[\]{}।،—–-]+$")


def normalize(token: str) -> str:
    return TRIM_RE.sub("", token).casefold()


def load_script(path: Path) -> tuple[dict[str, Any], Path]:
    """Load the script, falling back to the script-writer output if needed."""
    if not path.exists() and FALLBACK_SCRIPT.exists():
        path = FALLBACK_SCRIPT
    if not path.exists():
        sys.exit(f"Script not found: {path} (also tried {FALLBACK_SCRIPT})")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("scenes"), list):
        sys.exit("Invalid script: expected an object with a 'scenes' array.")
    return data, path


def build_segments(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Turn the hook and scene narrations into ordered spoken segments."""
    segments: list[dict[str, Any]] = []

    hook = str(data.get("hook", "")).strip()
    if hook:
        segments.append({"scene_number": 0, "label": "hook", "text": hook})

    for index, scene in enumerate(data["scenes"], start=1):
        narration = str(scene.get("narration", "")).strip()
        if not narration:
            continue
        scene_number = int(scene.get("scene_number", index))
        segments.append(
            {
                "scene_number": scene_number,
                "label": f"scene_{scene_number}",
                "text": narration,
            }
        )

    if not segments:
        sys.exit("No narration text found in the script.")
    return segments


def build_expected_words(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expected: list[dict[str, Any]] = []
    for segment in segments:
        for word in WORD_RE.findall(segment["text"]):
            expected.append(
                {
                    "norm": normalize(word),
                    "scene_number": segment["scene_number"],
                }
            )
    return expected


def scene_for_boundary(
    boundary_text: str, expected: list[dict[str, Any]], pointer: int
) -> tuple[int, int]:
    """Map an ordered WordBoundary event to a scene, advancing the word pointer."""
    needle = normalize(boundary_text)
    if needle:
        for offset in range(pointer, min(pointer + 12, len(expected))):
            candidate = expected[offset]["norm"]
            if candidate == needle or (len(needle) > 2 and needle in candidate):
                return expected[offset]["scene_number"], offset + 1

    if pointer < len(expected):
        return expected[pointer]["scene_number"], pointer + 1
    if expected:
        return expected[-1]["scene_number"], pointer
    return 0, pointer


async def synthesize(
    text: str,
    voice: str,
    expected: list[dict[str, Any]],
    audio_path: Path,
) -> list[dict[str, Any]]:
    """Stream audio to disk and collect WordBoundary caption events."""
    try:
        communicate = edge_tts.Communicate(text, voice, boundary="WordBoundary")
    except TypeError:
        communicate = edge_tts.Communicate(text, voice)

    captions: list[dict[str, Any]] = []
    pointer = 0
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    with audio_path.open("wb") as audio_file:
        async for chunk in communicate.stream():
            chunk_type = chunk.get("type")
            if chunk_type == "audio":
                audio_file.write(chunk["data"])
            elif chunk_type in {"WordBoundary", "SentenceBoundary"}:
                offset = int(chunk["offset"]) / 10_000_000
                duration = int(chunk["duration"]) / 10_000_000
                token = str(chunk.get("text", "")).strip()
                scene_number, pointer = scene_for_boundary(token, expected, pointer)
                captions.append(
                    {
                        "text": token,
                        "start": round(offset, 3),
                        "end": round(offset + duration, 3),
                        "scene_number": scene_number,
                    }
                )

    return captions


def mp3_duration_seconds(path: Path) -> float:
    """Compute duration by walking MPEG audio frame headers (no extra deps)."""
    data = path.read_bytes()
    if not data:
        return 0.0

    index = 0
    if data[:3] == b"ID3" and len(data) >= 10:
        tag_size = (
            ((data[6] & 0x7F) << 21)
            | ((data[7] & 0x7F) << 14)
            | ((data[8] & 0x7F) << 7)
            | (data[9] & 0x7F)
        )
        index = 10 + tag_size

    bitrates = {
        3: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0],
        2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0],
        0: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0],
    }
    sample_rates = {
        3: [44100, 48000, 32000],
        2: [22050, 24000, 16000],
        0: [11025, 12000, 8000],
    }

    duration = 0.0
    while index < len(data) - 4:
        if data[index] == 0xFF and (data[index + 1] & 0xE0) == 0xE0:
            version = (data[index + 1] >> 3) & 0x03
            layer = (data[index + 1] >> 1) & 0x03
            if layer != 1 or version not in bitrates:
                index += 1
                continue

            bitrate_index = (data[index + 2] >> 4) & 0x0F
            sample_index = (data[index + 2] >> 2) & 0x03
            padding = (data[index + 2] >> 1) & 0x01
            if sample_index == 3:
                index += 1
                continue

            bitrate = bitrates[version][bitrate_index]
            sample_rate = sample_rates[version][sample_index]
            if not bitrate or not sample_rate:
                index += 1
                continue

            if version == 3:
                frame_length = int(144000 * bitrate / sample_rate) + padding
                samples_per_frame = 1152
            else:
                frame_length = int(72000 * bitrate / sample_rate) + padding
                samples_per_frame = 576

            if frame_length <= 4:
                index += 1
                continue

            duration += samples_per_frame / sample_rate
            index += frame_length
        else:
            index += 1

    return duration


def build_scene_boundaries(
    segments: list[dict[str, Any]], captions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    boundaries: list[dict[str, Any]] = []
    for segment in segments:
        hits = [item for item in captions if item["scene_number"] == segment["scene_number"]]
        boundaries.append(
            {
                "scene_number": segment["scene_number"],
                "label": segment["label"],
                "text": segment["text"],
                "start": hits[0]["start"] if hits else None,
                "end": hits[-1]["end"] if hits else None,
            }
        )
    return boundaries


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate voiceover MP3 and word-level caption JSON from the latest Shorts script."
    )
    parser.add_argument("--gender", choices=("male", "female"), default="male")
    parser.add_argument("--script", type=Path, default=DEFAULT_SCRIPT)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    parser.add_argument(
        "--project",
        default=None,
        help="Write voiceover.mp3 and captions.json into projects/<project>/03-voice/",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    script_path = args.script
    output_dir: Path = args.output_dir
    if args.project:
        script_path = (
            ROOT / "projects" / args.project / "02-script" / "latest_script.json"
            if script_path == DEFAULT_SCRIPT else script_path
        )
        output_dir = ROOT / "projects" / args.project / "03-voice"

    import schema_validator

    schema_errors = schema_validator.validate_file("latest_script", script_path)
    if schema_errors:
        sys.exit(
            f"FAIL latest_script schema for {script_path}: " + "; ".join(schema_errors)
        )

    data, script_path = load_script(script_path)

    language = str(data.get("language", "bn")).strip().lower()
    if language not in VOICES:
        sys.exit(f"Unsupported language: {language!r}. Expected 'bn' or 'en'.")

    voice = VOICES[language][args.gender]
    segments = build_segments(data)
    expected = build_expected_words(segments)
    combined_text = " ".join(segment["text"] for segment in segments)

    audio_path = output_dir / "voiceover.mp3"
    captions_path = output_dir / "captions.json"

    captions = asyncio.run(synthesize(combined_text, voice, expected, audio_path))

    total_duration = mp3_duration_seconds(audio_path)
    if total_duration <= 0 and captions:
        total_duration = max(item["end"] for item in captions)

    payload = {
        "language": language,
        "gender": args.gender,
        "voice": voice,
        "script_file": display_path(script_path),
        "audio_file": display_path(audio_path),
        "total_duration_sec": round(total_duration, 3),
        "segments": segments,
        "scene_boundaries": build_scene_boundaries(segments, captions),
        "captions": captions,
    }

    schema_errors = schema_validator.validate(
        payload, schema_validator.load_schema("captions")
    )
    if schema_errors:
        sys.exit("FAIL captions schema: " + "; ".join(schema_errors))

    output_dir.mkdir(parents=True, exist_ok=True)
    with captions_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"Voice: {voice} ({language}, {args.gender})")
    print(f"Audio: {audio_path}")
    print(f"Captions: {captions_path}")
    print(f"Caption events: {len(captions)}")
    print(f"Total audio duration: {total_duration:.3f} seconds")


if __name__ == "__main__":
    main()
