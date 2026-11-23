#!/usr/bin/env python3
"""Free-source trend discovery for the trend-finder skill.

Sources:
  1. YouTube Data API v3 mostPopular chart for the configured region.
  2. Google Trends through the optional pytrends package.
  3. YouTube search autosuggest for five niche keywords.
  4. Manual exports in research/trend-inputs/.

The helper never invents a metric. If a source is unavailable it is recorded
in the report with status "unavailable" or "warn" and the run continues.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skill_lib as lib  # noqa: E402

ROOT = lib.ROOT
TREND_CACHE = ROOT / "research" / "trend-cache"
TREND_INPUTS = ROOT / "research" / "trend-inputs"
OUTPUT = TREND_CACHE / "trend-report.json"
QUOTA_LOG = TREND_CACHE / "quota-log.jsonl"

YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_SUGGEST_URL = "https://suggestqueries.google.com/complete/search"

MANUAL_SUFFIXES = {".csv", ".json", ".md", ".txt"}
STOP_WORDS = {"the", "and", "for", "with", "your", "from", "into", "that", "this"}


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def read_env_value(name: str) -> str:
    """Read a key from the environment or .env without printing its value."""
    value = os.environ.get(name, "").strip()
    if value:
        return value
    path = ROOT / ".env"
    if not path.is_file():
        return ""
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        if key.strip() != name:
            continue
        raw_value = raw_value.strip()
        if len(raw_value) >= 2 and raw_value[0] == raw_value[-1] and raw_value[0] in "'\"":
            raw_value = raw_value[1:-1]
        return raw_value
    return ""


def region_code(location: str) -> str:
    low = location.lower()
    if "bangladesh" in low or "bangla" in low:
        return "BD"
    return "US"


def _niche_parts(niche: str) -> list[str]:
    parts = [part.strip() for part in re.split(r"[/,|&+]|\band\b", niche) if part.strip()]
    return parts or [niche.strip()]


def niche_keywords(niche: str, language: str, *, limit: int = 5) -> list[str]:
    """Build five search seeds from the configured niche; no fixed topic list."""
    parts = _niche_parts(niche)
    suffixes = ["ideas", "tips", "shorts", str(datetime.now().year)]
    if language == "bn":
        suffixes.append("bangla")
    else:
        suffixes.append("trends")

    keywords: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        cleaned = " ".join(value.split()).strip()
        if not cleaned or cleaned.lower() in seen:
            return
        seen.add(cleaned.lower())
        keywords.append(cleaned)

    for part in parts:
        add(part)
    for suffix in suffixes:
        for part in parts:
            add(f"{part} {suffix}")
    return keywords[:limit]


def niche_tokens(niche: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z\u0980-\u09FF]+", niche.lower())
    return [token for token in tokens if len(token) > 2 and token not in STOP_WORDS]


def http_get_json(url: str, *, timeout: float = 20.0) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "shorts-generator-system/1.0 (trend-finder; free-source research)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _source(name: str, status: str, detail: str, items: int = 0) -> dict[str, Any]:
    return {"name": name, "status": status, "detail": detail, "items": items}


def _int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (TypeError, ValueError):
        return None


def _float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def _date(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    match = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if match:
        return match.group(0)
    match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
    if match:
        day, month, year = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return fallback


def score_from_views(views: int | None, rank: int) -> float:
    if views is None:
        base = 50.0
    else:
        base = 20.0 + 15.0 * math.log10(max(views, 1))
    base -= min(15.0, max(0, rank - 1) * 0.5)
    return round(max(0.0, min(100.0, base)), 1)


def score_from_rank(rank: int) -> float:
    return round(max(30.0, 90.0 - (rank - 1) * 10.0), 1)


def score_from_interest(interest: float | None) -> float:
    if interest is None:
        return 50.0
    return round(max(0.0, min(100.0, interest * 4.0)), 1)


def _manual_item(
    row: dict[str, Any],
    path: Path,
    *,
    fallback_date: str,
) -> dict[str, Any] | None:
    lower = {str(key).strip().lower(): value for key, value in row.items() if key is not None}

    def first(*keys: str) -> Any:
        for key in keys:
            value = lower.get(key)
            if value is not None and str(value).strip() not in ("", "none", "null"):
                return value
        return None

    keyword = first("keyword", "topic", "query", "title", "name", "trend", "search term")
    if not keyword:
        return None
    keyword = " ".join(str(keyword).split()).strip()
    if len(keyword) < 3:
        return None

    observed = _date(first("date", "observed_on", "published", "published_at", "day"), fallback_date)
    views = _int(first("views", "view count", "video views", "impressions"))
    raw_score = _float(first("score", "interest", "viral score", "search volume", "volume", "rank"))

    if raw_score is None:
        score = score_from_views(views, 1)
        confidence = 0.55 if views is None else 0.75
    elif raw_score <= 5:
        score = round(max(0.0, min(100.0, raw_score * 20.0)), 1)
        confidence = 0.8
    else:
        score = round(max(0.0, min(100.0, raw_score)), 1)
        confidence = 0.8

    signals: dict[str, Any] = {"input_file": lib.relative(path)}
    if views is not None:
        signals["views"] = views
    if raw_score is not None:
        signals["source_score"] = raw_score

    return {
        "source": f"manual:{path.name}",
        "sources": [f"manual:{path.name}"],
        "date": observed,
        "keyword": keyword,
        "topic": keyword,
        "score": score,
        "confidence": confidence,
        "platform": "manual-export",
        "signals": signals,
        "source_file": lib.relative(path),
    }


def _rows_from_json(path: Path, fallback_date: str) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("trends") or data.get("items") or data.get("rows") or []
    if not isinstance(data, list):
        return []
    rows: list[dict[str, Any]] = []
    for entry in data:
        if isinstance(entry, dict):
            rows.append(entry)
        elif isinstance(entry, str) and entry.strip():
            rows.append({"keyword": entry.strip(), "date": fallback_date})
    return rows


def _rows_from_text(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "//")):
            continue
        if "|" in line:
            parts = [part.strip() for part in line.lstrip("-*+ ").split("|")]
            rows.append({
                "keyword": parts[0],
                "score": parts[1] if len(parts) > 1 else "",
                "date": parts[2] if len(parts) > 2 else "",
            })
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            if key.strip().lower() in {"keyword", "topic", "trend", "query", "title"}:
                rows.append({"keyword": value.strip()})
            continue
        if re.match(r"^(?:[-*+]|\d+[.)])\s+", line):
            rows.append({"keyword": re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", line).strip()})
    return rows


def read_manual_inputs(
    input_dir: Path = TREND_INPUTS,
    *,
    fallback_date: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    fallback = fallback_date or today_iso()
    if not input_dir.is_dir():
        return [], _source(
            "manual-inputs", "unavailable",
            f"{lib.relative(input_dir)} not found; create it and add exports",
        )

    files = sorted(
        path for path in input_dir.rglob("*")
        if path.is_file() and not path.name.startswith(".") and path.suffix.lower() in MANUAL_SUFFIXES
    )
    if not files:
        return [], _source(
            "manual-inputs", "empty",
            f"no {', '.join(sorted(MANUAL_SUFFIXES))} exports in {lib.relative(input_dir)}",
        )

    items: list[dict[str, Any]] = []
    for path in files:
        try:
            if path.suffix.lower() == ".csv":
                with path.open("r", encoding="utf-8-sig", newline="") as handle:
                    rows = list(csv.DictReader(handle))
            elif path.suffix.lower() == ".json":
                rows = _rows_from_json(path, fallback)
            else:
                rows = _rows_from_text(path)
        except (OSError, csv.Error, json.JSONDecodeError) as exc:
            continue
        for row in rows:
            item = _manual_item(row, path, fallback_date=fallback)
            if item:
                items.append(item)

    if not items:
        return [], _source(
            "manual-inputs", "warn",
            f"{len(files)} file(s) found but no parseable keyword rows",
        )
    return items, _source(
        "manual-inputs", "ok",
        f"{len(items)} row(s) merged from {len(files)} manual file(s)",
        len(items),
    )


def fetch_youtube_most_popular(
    api_key: str,
    *,
    region: str,
    niche: str,
    get_json: Callable[[str], Any] = http_get_json,
    fallback_date: str | None = None,
) -> list[dict[str, Any]]:
    fallback = fallback_date or today_iso()
    params = urllib.parse.urlencode({
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": 25,
        "key": api_key,
    })
    payload = get_json(f"{YOUTUBE_VIDEOS_URL}?{params}")
    videos = payload.get("items") if isinstance(payload, dict) else []
    tokens = niche_tokens(niche)

    items: list[dict[str, Any]] = []
    for rank, video in enumerate(videos or [], 1):
        snippet = video.get("snippet") or {}
        title = " ".join(str(snippet.get("title") or "").split())
        if not title:
            continue
        haystack = " ".join([
            title,
            str(snippet.get("description") or ""),
            " ".join(str(tag) for tag in (snippet.get("tags") or [])),
        ]).lower()
        if tokens and not any(token in haystack for token in tokens):
            continue

        views = _int((video.get("statistics") or {}).get("viewCount"))
        item = {
            "source": "youtube-most-popular",
            "sources": ["youtube-most-popular"],
            "date": _date(snippet.get("publishedAt"), fallback),
            "keyword": title,
            "topic": title,
            "score": score_from_views(views, rank),
            "confidence": 0.9 if views is not None else 0.7,
            "platform": "youtube-shorts",
            "signals": {
                "views": views,
                "rank": rank,
                "video_id": video.get("id"),
            },
            "source_file": f"youtube-api:mostPopular?regionCode={region}",
        }
        items.append(item)
    return items


def fetch_youtube_autosuggest(
    keywords: list[str],
    *,
    region: str,
    language: str,
    get_json: Callable[[str], Any] = http_get_json,
    fallback_date: str | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    fallback = fallback_date or today_iso()
    hl = "bn" if language == "bn" else "en"
    items: list[dict[str, Any]] = []
    errors: list[str] = []

    for seed in keywords:
        params = urllib.parse.urlencode({
            "client": "firefox",
            "ds": "yt",
            "hl": hl,
            "gl": region,
            "q": seed,
        })
        try:
            payload = get_json(f"{YOUTUBE_SUGGEST_URL}?{params}")
        except Exception as exc:  # noqa: BLE001 - optional source must not stop the run
            errors.append(f"{seed}: {type(exc).__name__}")
            continue
        suggestions = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        for rank, suggestion in enumerate(suggestions[:3], 1):
            keyword = " ".join(str(suggestion).split()).strip()
            if not keyword or len(keyword) < 3:
                continue
            items.append({
                "source": "youtube-autosuggest",
                "sources": ["youtube-autosuggest"],
                "date": fallback,
                "keyword": keyword,
                "topic": keyword,
                "score": score_from_rank(rank),
                "confidence": 0.45,
                "platform": "youtube-shorts",
                "signals": {"seed_keyword": seed, "rank": rank},
                "source_file": f"youtube-autosuggest?q={urllib.parse.quote(seed)}",
            })
    return items, errors


def fetch_google_trends(
    keywords: list[str],
    *,
    region: str,
    pytrends_factory: Callable[[], Any] | None = None,
    fallback_date: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    fallback = fallback_date or today_iso()
    if pytrends_factory is None:
        try:
            from pytrends.request import TrendReq  # type: ignore
        except Exception as exc:  # noqa: BLE001 - optional dependency
            return [], _source(
                "google-trends", "warn",
                f"pytrends not installed; optional source skipped ({type(exc).__name__})",
            )
        factory = lambda: TrendReq(hl="en-US", tz=360)  # noqa: E731
    else:
        factory = pytrends_factory

    try:
        client = factory()
        client.build_payload(keywords[:5], timeframe="now 7-d", geo=region)
        data = client.interest_over_time()
    except Exception as exc:  # noqa: BLE001 - optional source must not stop the run
        return [], _source(
            "google-trends", "warn",
            f"Google Trends failed; optional source skipped ({type(exc).__name__})",
        )

    items: list[dict[str, Any]] = []
    for keyword in keywords:
        try:
            series = data[keyword]
        except (KeyError, TypeError):
            continue
        try:
            mean = float(series.mean())
        except (AttributeError, TypeError, ValueError):
            values = [float(value) for value in series if value is not None]
            mean = sum(values) / len(values) if values else 0.0
        if mean <= 0:
            continue
        items.append({
            "source": "google-trends",
            "sources": ["google-trends"],
            "date": fallback,
            "keyword": keyword,
            "topic": keyword,
            "score": score_from_interest(mean),
            "confidence": 0.65,
            "platform": "google-trends",
            "signals": {"interest": round(mean, 1)},
            "source_file": f"google-trends:pytrends?geo={region}",
        })
    if not items:
        return [], _source("google-trends", "warn", "Google Trends returned no positive interest")
    return items, _source(
        "google-trends", "ok",
        f"{len(items)} keyword(s) from Google Trends",
        len(items),
    )


def merge_items(items: list[dict[str, Any]], *, limit: int = 50) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        key = str(item.get("keyword") or "").strip().lower()
        if key:
            grouped.setdefault(key, []).append(item)

    merged: list[dict[str, Any]] = []
    for group in grouped.values():
        group.sort(key=lambda item: (item.get("confidence", 0), item.get("score", 0)), reverse=True)
        best = dict(group[0])
        sources = sorted({str(item.get("source")) for item in group if item.get("source")})
        best["sources"] = sources
        best["source"] = sources[0] if sources else best.get("source", "unknown")
        base_confidence = max(float(item.get("confidence", 0)) for item in group)
        best["confidence"] = round(min(0.99, base_confidence + 0.03 * max(0, len(sources) - 1)), 2)
        best["score"] = round(max(float(item.get("score", 0)) for item in group), 1)
        merged.append(best)

    merged.sort(key=lambda item: (item.get("score", 0), item.get("confidence", 0), item.get("keyword", "")), reverse=True)
    return merged[:limit]


def append_quota_log(path: Path, *, date: str, units: int, report_path: Path) -> None:
    lib.ensure(path)
    entry = {
        "date": date,
        "source": "youtube-most-popular",
        "units": units,
        "report": lib.relative(report_path),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run(
    output_path: Path | None = None,
    input_dir: Path | None = None,
    *,
    api_key: str | None = None,
    http_get: Callable[[str], Any] = http_get_json,
    pytrends_factory: Callable[[], Any] | None = None,
    quota_log: Path | None = QUOTA_LOG,
    fallback_date: str | None = None,
) -> dict[str, Any]:
    output_path = output_path or OUTPUT
    input_dir = input_dir or TREND_INPUTS
    fallback = fallback_date or today_iso()

    channel = lib.load_channel()
    niche = channel["niche"]
    language = channel["language"]
    region = region_code(channel["audience_location"])
    keywords = niche_keywords(niche, language)
    if len(keywords) < 5:
        raise lib.SkillError("could not build 5 niche keywords from config/channel.json")

    if api_key is None:
        api_key = read_env_value("YOUTUBE_API_KEY")

    sources: list[dict[str, Any]] = []
    all_items: list[dict[str, Any]] = []
    youtube_units = 0

    if api_key:
        youtube_units = 1
        try:
            youtube_items = fetch_youtube_most_popular(
                api_key, region=region, niche=niche, get_json=http_get, fallback_date=fallback,
            )
            all_items += youtube_items
            status = "ok" if youtube_items else "warn"
            detail = (
                f"{len(youtube_items)} niche-matched item(s) from mostPopular"
                if youtube_items else
                "mostPopular succeeded but no item matched the niche tokens"
            )
            sources.append(_source("youtube-most-popular", status, detail, len(youtube_items)))
        except Exception as exc:  # noqa: BLE001 - report source failure and continue
            sources.append(_source(
                "youtube-most-popular", "warn",
                f"YouTube Data API failed; source skipped ({type(exc).__name__})",
            ))
    else:
        sources.append(_source(
            "youtube-most-popular", "unavailable",
            "YOUTUBE_API_KEY is not set in .env; source skipped (no key value was read into the report)",
        ))

    try:
        suggestion_items, suggestion_errors = fetch_youtube_autosuggest(
            keywords, region=region, language=language, get_json=http_get, fallback_date=fallback,
        )
        all_items += suggestion_items
        if suggestion_items:
            status = "ok"
            detail = f"{len(suggestion_items)} suggestion(s) from {len(keywords)} niche keyword(s)"
            if suggestion_errors:
                detail += f"; {len(suggestion_errors)} keyword(s) failed"
        elif suggestion_errors:
            status = "warn"
            detail = "YouTube autosuggest failed for every keyword"
        else:
            status = "empty"
            detail = "YouTube autosuggest returned no suggestions"
        sources.append(_source("youtube-autosuggest", status, detail, len(suggestion_items)))
    except Exception as exc:  # noqa: BLE001 - optional source must not stop the run
        sources.append(_source(
            "youtube-autosuggest", "warn",
            f"YouTube autosuggest failed; source skipped ({type(exc).__name__})",
        ))

    trend_items, trend_source = fetch_google_trends(
        keywords, region=region, pytrends_factory=pytrends_factory, fallback_date=fallback,
    )
    all_items += trend_items
    sources.append(trend_source)

    manual_items, manual_source = read_manual_inputs(input_dir, fallback_date=fallback)
    all_items += manual_items
    sources.append(manual_source)

    merged = merge_items(all_items)
    warnings = [
        f"{source['name']}: {source['detail']}"
        for source in sources
        if source["status"] not in {"ok"}
    ]
    source_files = sorted({
        item["source_file"]
        for item in all_items
        if item.get("source_file")
    })
    quota = {
        "youtube_units": youtube_units,
        "autosuggest_units": 0,
        "google_trends_units": 0,
        "total_units": youtube_units,
    }
    if quota_log is not None and youtube_units:
        append_quota_log(quota_log, date=fallback, units=youtube_units, report_path=output_path)
        quota["log_file"] = lib.relative(quota_log)

    report = {
        "region": channel["audience_location"],
        "generated_on": fallback,
        "niche": niche,
        "language": language,
        "keywords": keywords,
        "source_files": source_files,
        "sources": sources,
        "trends": merged,
        "warnings": warnings,
        "quota": quota,
        "status": "PASS" if merged and not warnings else "WARN",
    }
    lib.write_json(output_path, report)
    lib.validate_schema("trend-report", output_path)

    if report["status"] == "PASS":
        print(
            f"PASS trend-finder: {len(merged)} merged trend item(s), "
            f"{sum(1 for source in sources if source['status'] == 'ok')} active source(s) -> "
            f"{lib.relative(output_path)}"
        )
    else:
        detail = "; ".join(warnings[:2]) if warnings else "no trend items were available"
        print(
            f"WARN trend-finder: {len(merged)} merged trend item(s); {detail} -> "
            f"{lib.relative(output_path)}"
        )
    return report


def self_test() -> int:
    """Offline test with fake YouTube, autosuggest and pytrends responses."""
    base = ROOT / ".tmp" / "self-test" / "trend-finder"
    shutil.rmtree(base, ignore_errors=True)
    input_dir = base / "trend-inputs"
    output = base / "trend-report.json"
    quota = base / "quota-log.jsonl"
    input_dir.mkdir(parents=True, exist_ok=True)

    (input_dir / "studio-research.csv").write_text(
        "keyword,views,date\n"
        "side hustle ideas,120000,2026-11-20\n"
        "personal finance tips,45000,2026-11-21\n",
        encoding="utf-8",
    )
    (input_dir / "facebook-notes.md").write_text(
        "- side hustle ideas | 80 | 2026-11-22\n"
        "- personal finance bangla | 65 | 2026-11-22\n",
        encoding="utf-8",
    )
    (input_dir / "vidiq-notes.txt").write_text(
        "keyword: personal finance\n",
        encoding="utf-8",
    )

    fake_youtube = {
        "items": [
            {
                "id": "fake-video-1",
                "snippet": {
                    "title": "Side hustle idea for students",
                    "description": "A small personal finance experiment.",
                    "tags": ["side hustle", "finance"],
                    "publishedAt": "2026-11-20T10:00:00Z",
                },
                "statistics": {"viewCount": "120000"},
            },
            {
                "id": "fake-video-2",
                "snippet": {
                    "title": "Cooking recipe with rice",
                    "description": "Not related to the configured niche.",
                    "tags": ["cooking"],
                    "publishedAt": "2026-11-21T10:00:00Z",
                },
                "statistics": {"viewCount": "999999"},
            },
        ]
    }

    def fake_http(url: str) -> Any:
        if "youtube/v3/videos" in url:
            return fake_youtube
        if "suggestqueries" in url:
            query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("q", [""])[0]
            return [query, [f"{query} idea", f"{query} tips"]]
        raise RuntimeError("unexpected URL in self-test")

    class FakeTrends:
        def build_payload(self, *_args: Any, **_kwargs: Any) -> None:
            return None

        def interest_over_time(self) -> dict[str, list[int]]:
            return {
                "personal finance": [20, 30, 40],
                "side hustles": [10, 20, 30],
            }

    report = run(
        output,
        input_dir,
        api_key="fake-key-not-a-secret",
        http_get=fake_http,
        pytrends_factory=FakeTrends,
        quota_log=quota,
        fallback_date="2026-11-23",
    )

    assert report["status"] == "PASS", report["status"]
    assert len(report["keywords"]) == 5, report["keywords"]
    assert report["quota"]["youtube_units"] == 1, report["quota"]
    assert report["quota"]["log_file"].endswith("quota-log.jsonl"), report["quota"]
    assert quota.is_file() and len(quota.read_text(encoding="utf-8").splitlines()) == 1

    all_sources = {source for item in report["trends"] for source in item.get("sources", [])}
    for expected in ("youtube-most-popular", "youtube-autosuggest", "google-trends"):
        assert expected in all_sources, (expected, all_sources)
    assert any(source.startswith("manual:") for source in all_sources), all_sources
    assert all(0 <= item["confidence"] <= 1 for item in report["trends"])
    assert all(0 <= item["score"] <= 100 for item in report["trends"])
    assert all("Cooking recipe" not in item["keyword"] for item in report["trends"])
    assert any("side hustle" in item["keyword"].lower() for item in report["trends"])

    lib.validate_schema("trend-report", output)

    # Second fixture: every source unavailable. The report must stay valid,
    # list the exact reasons and contain no fabricated trend rows.
    warn_output = base / "trend-report-no-sources.json"
    warn_inputs = base / "empty-trend-inputs"
    warn_inputs.mkdir(parents=True, exist_ok=True)

    def failing_http(_url: str) -> Any:
        raise RuntimeError("offline in self-test")

    def failing_trends() -> Any:
        raise RuntimeError("pytrends unavailable in self-test")

    warn_report = run(
        warn_output,
        warn_inputs,
        api_key="",
        http_get=failing_http,
        pytrends_factory=failing_trends,
        quota_log=None,
        fallback_date="2026-11-23",
    )
    assert warn_report["status"] == "WARN", warn_report["status"]
    assert warn_report["trends"] == [], warn_report["trends"]
    assert any(
        source["name"] == "youtube-most-popular" and source["status"] == "unavailable"
        for source in warn_report["sources"]
    )
    assert warn_report["warnings"], warn_report
    lib.validate_schema("trend-report", warn_output)

    print(
        "PASS trend-finder: fake YouTube API, autosuggest, pytrends and manual merge "
        "verified (quota=1, 5 keywords); missing-source WARN verified (0 fabricated rows)"
    )
    return 0


if __name__ == "__main__":
    try:
        run()
    except lib.SkillError as exc:
        print(f"FAIL trend-finder: {exc}")
        sys.exit(1)
