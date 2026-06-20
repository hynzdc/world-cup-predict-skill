#!/usr/bin/env python3
"""Build recency-weighted World Cup history features for a team.

The script uses OpenFootball worldcup.json files when network access is
available. It avoids making old history decisive; the output is meant to be a
small model input for the betting-analysis skill.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


WORLD_CUP_YEARS = [
    1930,
    1934,
    1938,
    1950,
    1954,
    1958,
    1962,
    1966,
    1970,
    1974,
    1978,
    1982,
    1986,
    1990,
    1994,
    1998,
    2002,
    2006,
    2010,
    2014,
    2018,
    2022,
]

SOURCE_TEMPLATE = (
    "https://raw.githubusercontent.com/openfootball/worldcup.json/master/"
    "{year}/worldcup.json"
)

ALIASES = {
    "usa": "usa",
    "u s a": "usa",
    "united states": "usa",
    "united states of america": "usa",
    "korea republic": "south korea",
    "republic of korea": "south korea",
    "cote d ivoire": "ivory coast",
    "czechia": "czech republic",
    "serbia and montenegro": "serbia",
}


@dataclass(frozen=True)
class TeamMatch:
    year: int
    team: str
    opponent: str
    gf: int
    ga: int
    round_name: str
    date: str


def normalize_name(name: str) -> str:
    ascii_name = (
        unicodedata.normalize("NFKD", name)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    clean = "".join(ch.lower() if ch.isalnum() else " " for ch in ascii_name)
    clean = " ".join(clean.split())
    return ALIASES.get(clean, clean)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def fetch_json(year: int, timeout: float, cache_dir: Path | None) -> dict[str, Any]:
    cache_path = cache_dir / f"{year}.json" if cache_dir else None
    if cache_path and cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    url = SOURCE_TEMPLATE.format(year=year)
    request = urllib.request.Request(url, headers={"User-Agent": "codex-skill/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))

    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def iter_matches(data: dict[str, Any], year: int) -> list[dict[str, Any]]:
    matches = list(data.get("matches", []))
    for group in data.get("groups", []):
        matches.extend(group.get("matches", []))
    for round_block in data.get("rounds", []):
        matches.extend(round_block.get("matches", []))

    normalized = []
    seen = set()
    for match in matches:
        key = (
            match.get("date"),
            match.get("team1"),
            match.get("team2"),
            json.dumps(match.get("score", {}), sort_keys=True),
        )
        if key in seen:
            continue
        seen.add(key)
        score = match.get("score", {}).get("ft")
        if not score or len(score) != 2:
            continue
        normalized.append(
            {
                "year": year,
                "date": match.get("date", ""),
                "round": match.get("round", ""),
                "team1": match.get("team1", ""),
                "team2": match.get("team2", ""),
                "score": score,
            }
        )
    return normalized


def load_worldcups(
    years: list[int], timeout: float, cache_dir: Path | None
) -> tuple[list[dict[str, Any]], list[str]]:
    matches: list[dict[str, Any]] = []
    errors: list[str] = []
    for year in years:
        try:
            data = fetch_json(year, timeout, cache_dir)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            errors.append(f"{year}: {exc}")
            continue
        matches.extend(iter_matches(data, year))
    return matches, errors


def team_matches(matches: list[dict[str, Any]], team_query: str) -> list[TeamMatch]:
    target = normalize_name(team_query)
    output: list[TeamMatch] = []
    for match in matches:
        team1 = match["team1"]
        team2 = match["team2"]
        score1, score2 = match["score"]
        if normalize_name(team1) == target:
            output.append(
                TeamMatch(
                    year=match["year"],
                    team=team1,
                    opponent=team2,
                    gf=int(score1),
                    ga=int(score2),
                    round_name=match["round"],
                    date=match["date"],
                )
            )
        elif normalize_name(team2) == target:
            output.append(
                TeamMatch(
                    year=match["year"],
                    team=team2,
                    opponent=team1,
                    gf=int(score2),
                    ga=int(score1),
                    round_name=match["round"],
                    date=match["date"],
                )
            )
    return output


def summarize_team(
    rows: list[TeamMatch],
    all_matches: list[dict[str, Any]],
    opponent_query: str | None,
) -> dict[str, Any]:
    if not rows:
        return {"matches": 0, "error": "No World Cup matches found for team."}

    latest_year = max(row.year for row in rows)
    total_goals = sum(int(m["score"][0]) + int(m["score"][1]) for m in all_matches)
    avg_team_match_goals = total_goals / max(1, len(all_matches) * 2)

    wins = sum(1 for row in rows if row.gf > row.ga)
    draws = sum(1 for row in rows if row.gf == row.ga)
    losses = sum(1 for row in rows if row.gf < row.ga)
    gf = sum(row.gf for row in rows)
    ga = sum(row.ga for row in rows)

    weighted_matches = 0.0
    weighted_gf = 0.0
    weighted_ga = 0.0
    weighted_points = 0.0
    weighted_total_goals = 0.0
    by_year: dict[int, dict[str, float]] = {}
    for row in rows:
        # One World Cup cycle older means about 45% less influence.
        cycles_old = max(0, (latest_year - row.year) / 4)
        weight = 0.55**cycles_old
        points = 3 if row.gf > row.ga else 1 if row.gf == row.ga else 0
        weighted_matches += weight
        weighted_gf += row.gf * weight
        weighted_ga += row.ga * weight
        weighted_points += points * weight
        weighted_total_goals += (row.gf + row.ga) * weight
        bucket = by_year.setdefault(
            row.year, {"matches": 0, "gf": 0, "ga": 0, "points": 0}
        )
        bucket["matches"] += 1
        bucket["gf"] += row.gf
        bucket["ga"] += row.ga
        bucket["points"] += points

    wgfm = weighted_gf / max(weighted_matches, 1e-9)
    wgam = weighted_ga / max(weighted_matches, 1e-9)
    wppm = weighted_points / max(weighted_matches, 1e-9)
    wtempo = weighted_total_goals / max(weighted_matches, 1e-9)

    attack_ratio = wgfm / max(avg_team_match_goals, 1e-9)
    defense_ratio = avg_team_match_goals / max(wgam, 0.25)
    tempo_ratio = wtempo / max(avg_team_match_goals * 2, 1e-9)

    attack_score = clamp(50 + 25 * (attack_ratio - 1), 0, 100)
    defense_score = clamp(50 + 25 * (defense_ratio - 1), 0, 100)
    tempo_score = clamp(50 + 25 * (tempo_ratio - 1), 0, 100)
    reliability_score = clamp(50 + 20 * (wppm - 1.33), 0, 100)
    confidence = clamp(math.sqrt(weighted_matches / 6), 0, 1)

    h2h = []
    if opponent_query:
        opponent = normalize_name(opponent_query)
        h2h = [row for row in rows if normalize_name(row.opponent) == opponent]

    return {
        "source": "OpenFootball worldcup.json",
        "source_url": "https://github.com/openfootball/worldcup.json",
        "latest_year_in_sample": latest_year,
        "summary": {
            "matches": len(rows),
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": gf,
            "goals_against": ga,
            "goals_for_per_match": round(gf / len(rows), 3),
            "goals_against_per_match": round(ga / len(rows), 3),
            "points_per_match": round((wins * 3 + draws) / len(rows), 3),
            "clean_sheet_rate": round(
                sum(1 for row in rows if row.ga == 0) / len(rows), 3
            ),
            "failed_to_score_rate": round(
                sum(1 for row in rows if row.gf == 0) / len(rows), 3
            ),
        },
        "recent_weighted": {
            "weighted_matches": round(weighted_matches, 3),
            "goals_for_per_match": round(wgfm, 3),
            "goals_against_per_match": round(wgam, 3),
            "points_per_match": round(wppm, 3),
            "team_match_goal_tempo": round(wtempo, 3),
            "world_cup_average_team_goals_per_match": round(avg_team_match_goals, 3),
        },
        "model_inputs": {
            "world_cup_attack": round(attack_score, 1),
            "world_cup_defense": round(defense_score, 1),
            "world_cup_goal_tempo": round(tempo_score, 1),
            "world_cup_reliability": round(reliability_score, 1),
            "history_confidence": round(confidence, 2),
        },
        "tournaments": [
            {"year": year, **{key: int(value) for key, value in stats.items()}}
            for year, stats in sorted(by_year.items())
        ],
        "head_to_head": {
            "opponent": opponent_query,
            "matches": len(h2h),
            "rows": [
                {
                    "year": row.year,
                    "date": row.date,
                    "round": row.round_name,
                    "opponent": row.opponent,
                    "score_for": row.gf,
                    "score_against": row.ga,
                }
                for row in h2h
            ],
        },
    }


def render_text(team: str, result: dict[str, Any], errors: list[str]) -> str:
    if result.get("error"):
        return f"{team}: {result['error']}"

    summary = result["summary"]
    weighted = result["recent_weighted"]
    inputs = result["model_inputs"]
    lines = [
        f"World Cup history features: {team}",
        f"Source: {result['source']} ({result['source_url']})",
        (
            "All-time: "
            f"{summary['matches']} matches, {summary['wins']}W-"
            f"{summary['draws']}D-{summary['losses']}L, "
            f"GF {summary['goals_for']} / GA {summary['goals_against']}"
        ),
        (
            "Recent-weighted: "
            f"GF/m {weighted['goals_for_per_match']}, "
            f"GA/m {weighted['goals_against_per_match']}, "
            f"PPM {weighted['points_per_match']}, "
            f"tempo {weighted['team_match_goal_tempo']}"
        ),
        (
            "Model inputs (0-100): "
            f"attack {inputs['world_cup_attack']}, "
            f"defense {inputs['world_cup_defense']}, "
            f"tempo {inputs['world_cup_goal_tempo']}, "
            f"reliability {inputs['world_cup_reliability']}, "
            f"confidence {inputs['history_confidence']}"
        ),
    ]
    h2h = result.get("head_to_head", {})
    if h2h.get("opponent"):
        lines.append(f"World Cup H2H vs {h2h['opponent']}: {h2h['matches']} matches")
        for row in h2h.get("rows", [])[:6]:
            lines.append(
                "  "
                f"{row['year']} {row['round']}: "
                f"{team} {row['score_for']}-{row['score_against']} "
                f"{row['opponent']}"
            )
    if errors:
        lines.append(f"Skipped {len(errors)} tournaments because data could not load.")
    return "\n".join(lines)


def parse_years(value: str | None) -> list[int]:
    if not value:
        return WORLD_CUP_YEARS
    years = []
    for part in value.split(","):
        part = part.strip()
        if part:
            years.append(int(part))
    return years


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team", required=True, help="Team name, e.g. Argentina")
    parser.add_argument("--opponent", help="Optional opponent for World Cup H2H")
    parser.add_argument("--years", help="Comma-separated World Cup years")
    parser.add_argument("--timeout", type=float, default=12.0)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    matches, errors = load_worldcups(parse_years(args.years), args.timeout, args.cache_dir)
    result = summarize_team(team_matches(matches, args.team), matches, args.opponent)

    if args.format == "json":
        payload = {"team": args.team, "errors": errors, **result}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_text(args.team, result, errors))
    return 0 if matches else 2


if __name__ == "__main__":
    sys.exit(main())
