#!/usr/bin/env python3
"""Fuse football strength signals into expected goals and score clusters.

Input metrics are 0-100 values, where 50 is neutral/average and higher is
better for the named team. Missing metrics are treated as neutral.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Any


DEFAULT_WEIGHTS = {
    "rating": 0.24,
    "recent_attack": 0.16,
    "recent_defense": 0.14,
    "player_attack": 0.11,
    "player_defense": 0.09,
    "tactical_fit": 0.11,
    "world_cup_attack": 0.08,
    "world_cup_defense": 0.05,
    "h2h": 0.02,
}

OFFENSE_WEIGHTS = {
    "rating": 0.22,
    "recent_attack": 0.25,
    "player_attack": 0.20,
    "tactical_fit": 0.15,
    "world_cup_attack": 0.13,
    "h2h": 0.05,
}

DEFENSE_WEIGHTS = {
    "rating": 0.22,
    "recent_defense": 0.27,
    "player_defense": 0.22,
    "tactical_fit": 0.12,
    "world_cup_defense": 0.14,
    "h2h": 0.03,
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def metric(team: dict[str, Any], key: str) -> float:
    try:
        return clamp(float(team.get(key, 50)), 0, 100)
    except (TypeError, ValueError):
        return 50.0


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, float(value)) for value in weights.values())
    if total <= 0:
        raise ValueError("weights must have positive total")
    return {key: max(0.0, float(value)) / total for key, value in weights.items()}


def weighted_score(team: dict[str, Any], weights: dict[str, float]) -> float:
    weights = normalize_weights(weights)
    return sum(metric(team, key) * weight for key, weight in weights.items())


def confidence(team: dict[str, Any]) -> float:
    present = sum(1 for key in DEFAULT_WEIGHTS if key in team)
    declared = team.get("confidence")
    try:
        declared_float = float(declared)
    except (TypeError, ValueError):
        declared_float = 1.0
    completeness = present / len(DEFAULT_WEIGHTS)
    return clamp(0.45 + 0.55 * completeness, 0, 1) * clamp(declared_float, 0, 1)


def poisson(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def score_matrix(home_lambda: float, away_lambda: float, max_goals: int) -> list[dict[str, Any]]:
    rows = []
    for home_goals in range(max_goals + 1):
        hp = poisson(home_goals, home_lambda)
        for away_goals in range(max_goals + 1):
            prob = hp * poisson(away_goals, away_lambda)
            rows.append(
                {
                    "score": f"{home_goals}-{away_goals}",
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                    "probability": prob,
                }
            )
    return rows


def build_projection(payload: dict[str, Any]) -> dict[str, Any]:
    fixture = payload.get("fixture", {})
    home = payload.get("home", {})
    away = payload.get("away", {})
    weights = dict(DEFAULT_WEIGHTS)
    weights.update(payload.get("weights", {}))

    home_strength = weighted_score(home, weights)
    away_strength = weighted_score(away, weights)
    home_offense = weighted_score(home, OFFENSE_WEIGHTS)
    away_offense = weighted_score(away, OFFENSE_WEIGHTS)
    home_defense = weighted_score(home, DEFENSE_WEIGHTS)
    away_defense = weighted_score(away, DEFENSE_WEIGHTS)

    avg_conf = (confidence(home) + confidence(away)) / 2
    neutral = bool(fixture.get("neutral_site", True))
    home_advantage_score = 0.0 if neutral else 4.0
    total_goals = clamp(float(fixture.get("market_total_goals", 2.55)), 1.4, 4.2)

    # Split the total-goals prior by relative attack vs opponent defense.
    home_goal_edge = (
        (home_offense - away_defense) * 0.70
        + (home_strength - away_strength) * 0.30
        + home_advantage_score
    )
    away_goal_edge = (
        (away_offense - home_defense) * 0.70
        + (away_strength - home_strength) * 0.30
    )
    share = 1 / (1 + math.exp(-(home_goal_edge - away_goal_edge) / 24))
    damped_share = 0.5 + (share - 0.5) * avg_conf
    home_lambda = clamp(total_goals * damped_share, 0.15, 4.0)
    away_lambda = clamp(total_goals - home_lambda, 0.15, 4.0)

    max_goals = int(fixture.get("max_goals", 7))
    matrix = score_matrix(home_lambda, away_lambda, max_goals)
    mass = sum(row["probability"] for row in matrix)
    for row in matrix:
        row["probability"] /= mass

    home_win = sum(
        row["probability"] for row in matrix if row["home_goals"] > row["away_goals"]
    )
    draw = sum(
        row["probability"] for row in matrix if row["home_goals"] == row["away_goals"]
    )
    away_win = sum(
        row["probability"] for row in matrix if row["home_goals"] < row["away_goals"]
    )
    totals = {}
    for row in matrix:
        goals = row["home_goals"] + row["away_goals"]
        if goals <= 1:
            bucket = "0-1"
        elif goals == 2:
            bucket = "2"
        elif goals == 3:
            bucket = "3"
        else:
            bucket = "4+"
        totals[bucket] = totals.get(bucket, 0.0) + row["probability"]

    top_scores = sorted(matrix, key=lambda row: row["probability"], reverse=True)[:8]
    return {
        "fixture": {
            "home": fixture.get("home", "Home"),
            "away": fixture.get("away", "Away"),
            "neutral_site": neutral,
            "market_total_goals": total_goals,
        },
        "confidence": round(avg_conf, 3),
        "composite_strength": {
            "home": round(home_strength, 2),
            "away": round(away_strength, 2),
            "edge_home_minus_away": round(home_strength - away_strength, 2),
        },
        "subscores": {
            "home_offense": round(home_offense, 2),
            "away_offense": round(away_offense, 2),
            "home_defense": round(home_defense, 2),
            "away_defense": round(away_defense, 2),
        },
        "expected_goals": {
            "home": round(home_lambda, 3),
            "away": round(away_lambda, 3),
            "total": round(home_lambda + away_lambda, 3),
        },
        "win_draw_loss": {
            "home": round(home_win, 4),
            "draw": round(draw, 4),
            "away": round(away_win, 4),
        },
        "total_goals": {key: round(value, 4) for key, value in totals.items()},
        "top_scores": [
            {"score": row["score"], "probability": round(row["probability"], 4)}
            for row in top_scores
        ],
    }


def load_payload(path: str) -> dict[str, Any]:
    if path == "-":
        return json.loads(sys.stdin.read())
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def render_text(result: dict[str, Any]) -> str:
    fixture = result["fixture"]
    wdl = result["win_draw_loss"]
    xg = result["expected_goals"]
    strength = result["composite_strength"]
    scores = ", ".join(
        f"{row['score']} ({row['probability']:.1%})" for row in result["top_scores"][:5]
    )
    totals = ", ".join(
        f"{key}: {value:.1%}" for key, value in sorted(result["total_goals"].items())
    )
    return "\n".join(
        [
            f"Strength fusion: {fixture['home']} vs {fixture['away']}",
            (
                "Composite strength: "
                f"{fixture['home']} {strength['home']}, "
                f"{fixture['away']} {strength['away']} "
                f"(edge {strength['edge_home_minus_away']:+.2f})"
            ),
            (
                "Expected goals: "
                f"{fixture['home']} {xg['home']}, "
                f"{fixture['away']} {xg['away']}, total {xg['total']}"
            ),
            (
                "W/D/L: "
                f"{fixture['home']} {wdl['home']:.1%}, "
                f"Draw {wdl['draw']:.1%}, "
                f"{fixture['away']} {wdl['away']:.1%}"
            ),
            f"Total-goals clusters: {totals}",
            f"Top exact scores: {scores}",
            f"Input confidence: {result['confidence']:.2f}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to JSON input, or '-' for stdin")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    try:
        result = build_projection(load_payload(args.input))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"strength_fusion error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
