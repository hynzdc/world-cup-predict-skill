# Historical And Player Strength Model

Read this reference during pre-match prediction when historical World Cup records, recent national-team matches, or player/club form can improve the score forecast.

## Source Priority

Use current, verifiable sources first:

- Official FIFA match centre, FIFA rankings, national association releases, tournament pages, lineups, suspension reports, and press conferences.
- World Cup history: FIFA archive/stat pages, OpenFootball `worldcup.json`, worldfootball.net, RSSSF, 11v11, or other transparent match databases.
- Recent national-team form: last 8-15 matches, with competitive matches weighted above friendlies. Prefer World Cup qualifiers, continental tournaments, Nations League, Copa America, AFCON, Asian Cup, Euro, and official match logs.
- Player and club form: FBref, official league/club stats, Transfermarkt availability/minutes, reputable injury reports, ClubElo for club strength context, and reliable match reports.
- Betting markets and odds remain a strong crowd prior; do not double-count them as both "market" and "model" evidence.

If sources disagree, prefer official data for facts, then transparent databases, then reputable media. Treat unsourced social posts and forum claims as noise.

## Data Checklist

Collect these before making the final prediction:

- Historical World Cup profile: matches, wins/draws/losses, goals for/against, goals per match, clean sheets, failed-to-score rate, and recent tournament trend.
- Opponent-adjusted history: whether high scoring came against weak teams or held up against top opponents.
- Head-to-head: last relevant meetings only. Use low weight unless squad/core/coaches and competition context are similar.
- Recent national-team form: last 8-12 competitive matches where possible, with goals for/against, xG/xGA if available, shot quality, set-piece threat, and defensive errors.
- Player layer: likely XI, key attackers, creators, defensive anchors, goalkeeper, recent club minutes, goals/assists/xG/xA, injuries, fatigue, cards, and bench replacement quality.
- Club context: raise confidence when key players are performing at strong clubs; reduce it when form comes from lower-level leagues or limited minutes.

## Weighting Guide

Use this as the default contribution to the final read:

| Layer | Weight |
|---|---:|
| Current rating / market strength prior | 20-30% |
| Recent national-team form | 20-30% |
| Player availability and club form | 15-25% |
| Tactical matchup, venue, travel, rest, motivation | 15-20% |
| Historical World Cup profile | 8-15% |
| Head-to-head | 0-5% |

Adjust the historical World Cup weight:

- Use 12-15% when the same coach/core players, tournament style, or national team identity is still relevant.
- Use 8-10% for normal cases.
- Use 3-6% when the data is old, the squad changed heavily, or the team rarely reaches the World Cup.
- Use 0-3% for head-to-head that is mostly narrative and not structurally comparable.

## Feature Rules

Normalize features to a 0-100 scale before combining them:

- `rating`: current strength from FIFA ranking points, Elo-style ratings, market odds, or a blend. Average team is near 50.
- `recent_attack`: recent national-team scoring, xG, chance quality, set pieces, and opponent strength.
- `recent_defense`: recent goals conceded, xGA, shot suppression, goalkeeper form, and defensive error rate. Higher is better defense.
- `player_attack`: key attackers/creators club form, minutes, availability, and role fit.
- `player_defense`: center backs, fullbacks, defensive midfielders, goalkeeper, and replacement depth.
- `world_cup_attack`: World Cup goals-for tendency, recency-weighted.
- `world_cup_defense`: World Cup goals-against control, recency-weighted. Higher is better defense.
- `tactical_fit`: matchup-specific edge, including pressing resistance, set pieces, transition speed, aerial duels, and weather/venue.
- `h2h`: only use when recent and structurally relevant. Neutral is 50.

Use `scripts/worldcup_history_features.py` for the World Cup history inputs when OpenFootball data covers the team:

```bash
python scripts/worldcup_history_features.py --team Argentina --opponent France --format text
```

Use `scripts/strength_fusion.py` when enough inputs exist:

```bash
python scripts/strength_fusion.py fixture-input.json --format text
```

The fusion script expects 0-100 metrics and returns composite strength, expected goals, win/draw/loss probabilities, total-goals distribution, and top exact-score clusters.

## Score Adjustment Rules

Historical scoring traits should move expected goals carefully:

- Normal historical attack edge: adjust team expected goals by about `+0.03` to `+0.12`.
- Strong, current-supported historical attack edge: adjust by about `+0.12` to `+0.20`.
- Old or unsupported history: keep the adjustment below `+0.05`.
- Defensive injuries or missing attackers can erase a historical edge.

Never let history alone create a high-confidence bet. A good historical signal should agree with at least one of:

- Recent national-team form.
- Player/club form.
- Tactical matchup.
- Odds-implied value.

## Output Requirements

In `综合分析`, include a short paragraph that explains how history changed the score distribution.

In `历史战绩/球员状态`, include a table:

`场次 | 世界杯历史进球倾向 | 近年国家队战绩 | 关键球员俱乐部状态 | 综合实力修正`

Use phrasing like:

- `历史倾向支持小幅上调进球期望`
- `历史样本过旧，仅作弱参考`
- `近期阵容变化较大，历史优势降权`
- `关键前锋俱乐部状态支持进球端修正`

Always cite the source URLs or source names in `参考信息`.
