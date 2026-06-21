---
name: world-cup-predict-skill
description: World Cup and football betting workflow for Codex. Use when the user sends fixture screenshots or result screenshots and wants match analysis, exact-score predictions, China sports-lottery style single-bet slips, odds/ROI reasoning, bankroll risk control, shop-owner order tables, Markdown record creation, or post-match settlement with returns and profit/loss. Browse for China sports-lottery availability and single-bet status, current odds, team news, injuries, recent form, historical World Cup/team records, club and player form, travel fatigue, and public morale signals before making recommendations.
---

# World Cup Predict Skill

This skill turns one daily football screenshot into a practical betting-analysis workflow:

- Before matches: extract fixtures, research current signals, build a risk-controlled slip, output a shop-owner table, and create/update a daily Markdown record.
- After matches: extract final scores, compare them with recorded bets, calculate return/profit/loss, and update the Markdown record.

This skill is for analysis and record keeping. Never promise profit, certainty, or guaranteed hit rates.

## Scope

Use this workflow when the user:

- Sends a fixture screenshot and asks for predictions.
- Sends a result screenshot and asks to update performance.
- Mentions 世界杯, 体彩, 竞彩足球, 比分, 胜平负, 总进球数, 回本, 盈亏, 店主清单, 单关, 不串关, or 同步 md.
- Wants a betting slip that can be pasted to a shop owner.
- Wants a daily Markdown record of bets, odds, reasoning, and settlement.

If the screenshot shows future kickoff times, fixture cards, odds, predicted-score chips, or win/draw/loss percentages, treat it as **pre-match prediction**.

If the screenshot shows final scores, FT/完场/completed status, or match results, treat it as **post-match settlement**.

## Storage

Ask for or infer the user's notes folder once. Then keep using it in the same thread.

Use daily files named:

`YYYY-MM-DD-世界杯押注.md`

If the screenshot date is unclear, ask for the exact date. If the user says "今天", "昨天", or "明天", clarify with an absolute date when there is any risk of confusion.

## Pre-Match Workflow

1. Extract from the screenshot:
   - Match date.
   - Kickoff time.
   - Home and away teams.
   - Venue when visible.
   - Visible predicted scores.
   - Visible win/draw/loss percentages.
   - Visible Codex/odds hints if present.

2. Check China sports-lottery availability before choosing bets:
   - Read `references/lottery-availability-check.md`.
   - Query official China Sports Lottery / 中国竞彩网 football schedule pages first.
   - Confirm each fixture's `开售状态` and each market's availability: 胜平负, 让球胜平负, 比分, 总进球数, 半全场胜平负.
   - Confirm whether each intended market is open for 单关. If only 过关 is open, do not place it in the default single-bet slip.
   - If official pages are inaccessible, use reliable secondary sources such as 500.com only as a provisional check, then mark the market as `待店主确认`.
   - Do not recommend a 胜平负 row, even for a strong favorite, unless the fixture is confirmed open for that market and usable as 单关.

3. Browse for current information because sports data changes:
   - China sports-lottery related odds or 500.com style odds when accessible.
   - Correct-score SP odds.
   - 胜平负 / 让球胜平负 availability and whether 单关 is open.
   - 总进球数 odds and availability.
   - Team news, injuries, suspensions, likely lineups, and coach comments.
   - Recent form and scoring profile.
   - Historical World Cup record, tournament goal profile, and relevant head-to-head results.
   - Recent competitive national-team matches from World Cup qualifiers, continental tournaments, Nations League, Copa America, AFCON, Asian Cup, friendlies, or other reliable match logs.
   - Key-player club form, minutes load, goals/assists/xG/xA when available, goalkeeper form, defensive absences, and bench depth.
   - Travel, venue, time-zone, weather, rest-day, and arrival reports.
   - Public morale signals from official accounts, press conferences, reliable sports outlets, and training reports.

4. Add the historical/player strength layer:
   - Read `references/historical-strength-model.md` when pre-match analysis needs historical World Cup records, recent non-World-Cup matches, or player/club form.
   - Use `scripts/worldcup_history_features.py` to collect repeatable World Cup history features when the teams have past World Cup data.
   - Use `scripts/strength_fusion.py` when enough numeric evidence exists to combine current ratings, recent national-team form, historical World Cup traits, player availability, and tactical matchup into a score distribution.
   - Treat this layer as a correction to current odds/news, not a replacement for them.

5. Separate facts from inference:
   - Use `可确认...` for confirmed information.
   - Use `公开报道显示...` for sourced reports.
   - Use `我推断...` for analysis.
   - Use `没有可靠公开信息支持...` when a claim cannot be verified.

6. Build predictions from:
   - Team strength and tactical matchup.
   - Expected scoring intensity and score distribution.
   - Odds and implied probabilities.
   - China sports-lottery market availability and single-bet constraints.
   - Injury and lineup effects.
   - Historical World Cup attack/defense profile and tournament scoring habits.
   - Recent national-team performance across competitive matches.
   - Key-player club form, minutes, availability, and role importance.
   - Travel/rest/fatigue effects.
   - Public morale and motivation.
   - User's budget and risk preference.

## Risk-Optimized Strategy

Do not optimize for buying many outcomes. Optimize for positive expected value, controlled drawdown, and lower correlation.

### Lottery Availability Gate

Always run this gate before finalizing a shop-owner order:

1. Build a market availability table for every fixture:
   - `场次 | 比赛 | 开售状态 | 胜平负单关 | 让球胜平负单关 | 比分单关 | 总进球数单关 | 处理`
2. Treat `开售单关` and `开售单关+过关` as usable for default single-bet slips.
3. Treat `仅开售过关`, `未开售此游戏`, blank, suspended, hidden, or unclear status as not usable for default single-bet slips.
4. If the user says the shop owner cannot place a market, immediately remove that market, preserve budget when possible, and rebuild only with confirmed-open single-bet markets.
5. If no suitable market is confirmed open for a match, skip that match in the shop-owner order and optionally list it under `备选观察`.
6. Never fill unavailable stake by adding more exact-score bets blindly. Reallocate first to confirmed-open, lower-variance markets that agree with the score model.

### Expected-Value Gate

For decimal odds:

`breakeven_probability = 1 / odds`

Only mark a bet as value when:

`estimated_probability * odds > 1`

Use a margin of safety:

- 胜平负 / 让球 / 总进球数: require about `+5%` edge before calling it a value bet.
- 比分: require about `+10%` edge because exact-score variance is much higher.

When probability is uncertain, reduce exposure instead of adding more rows.

### Portfolio Allocation

Default daily plan unless the user says otherwise:

- Total budget: `24-30元`, usually `28元`.
- Unit stake: `2元`.
- 比分单: `20-30%` of budget, usually `3-4注`.
- 胜平负 / 让球胜平负: `30-45%` of budget when 单关 is open.
- 总进球数: `30-45%` of budget when it aligns with the score distribution.
- Cap one match near `40%` of the daily budget unless the user explicitly wants a focus bet.

Avoid correlated overexposure. Example: `2:1`, `3球`, and `主胜` all rely on a similar match story. It can be valid to combine them, but do not overbuy the same story.

### Staking

- Prefer flat `2元` units for shop-owner workflow.
- Use fractional Kelly logic only as a thinking tool for larger bankrolls; never recommend full Kelly because model probabilities are noisy.
- Do not use martingale.
- Do not chase losses.
- Do not increase stakes only because the previous day lost.

### Score Modeling

Use Poisson/Dixon-Coles style reasoning:

- Estimate each team's scoring intensity.
- Think in score clusters, not isolated guesses.
- Link exact scores to total-goals selections.
- Treat low-score draws like `0:0` and `1:1` carefully; add them only when tactics and odds support them.
- Let historical scoring records adjust expected goals only within a controlled band unless current squads/coaches strongly overlap with the historical sample.
- In national-team tournaments, weigh current availability, rest, travel, motivation, and current-player club form more than old historical form.
- If a team's long-run World Cup profile repeatedly shows above-average goals for, do not ignore it; use it as a small positive attack prior, then verify with current squad quality and recent matches.

## Slip Construction Rules

Default:

- Every row is `2元` unless the user says otherwise.
- All bets are single bets unless the user explicitly asks for parlays.
- If a market is not confirmed open for 单关, do not include it in the single-bet shop-owner slip.
- If the shop owner says a market is unavailable, rebuild the slip with the same budget when possible.
- Put unavailable but analytically attractive markets in a separate `未开/待确认，不下单` note, not in the order table.

For exact-score bets:

- Prefer `1-2` scores for clear favorites.
- Prefer `2-3` scores for close or tactical matches.
- Use high-odds draws only when the match profile supports them.
- Do not let exact-score bets dominate the day.

For total-goals bets:

- Tie them to the score cluster.
- Prefer totals that cover multiple plausible scores.
- Do not add totals that conflict with the main match read.

Before finalizing:

- Check no duplicate score for the same match.
- Check no odd-number stake amount when the user dislikes odd amounts.
- Recalculate rows and total stake.
- State the breakeven line.
- State that all bets are single bets if that is the plan.

## Output Format

For a shop-owner order, output clean tables that can be pasted directly.

### 比分单

`场次 | 比分 | 金额`

### 胜平负 / 让球单

`场次 | 玩法 | 投注内容 | 金额`

### 总进球数单

`场次 | 玩法 | 投注内容 | 金额`

End with:

`全部合计 | N注 | X元`

Also write:

`全部单关，不要串关。`

## Markdown Record Format

Daily Markdown files should include:

1. `今日总览`
2. `体彩开售检查`
3. `今日订单`
4. `店主下单内容`
5. `推荐标记`
6. `综合分析`
7. `历史战绩/球员状态`
8. `新闻/旅途/精神状态`
9. `检查记录`
10. `今日战果`
11. `今日总结`
12. `参考信息`

Use Markdown tables.

When odds are known, include:

`场次 | 比分/玩法 | 投注内容 | 金额 | 参考赔率 | 命中回报`

For `体彩开售检查`, use:

`场次 | 比赛 | 开售状态 | 胜平负单关 | 让球胜平负单关 | 比分单关 | 总进球数单关 | 处理`

For `新闻/旅途/精神状态`, use:

`场次 | 近期新闻 | 旅途/休整 | 精神状态判断 | 对比分影响`

For `历史战绩/球员状态`, use:

`场次 | 世界杯历史进球倾向 | 近年国家队战绩 | 关键球员俱乐部状态 | 综合实力修正`

## Updating Existing Daily Files

When the user changes a slip:

1. Read the existing daily file first.
2. Treat the newest user instruction as authoritative.
3. Replace affected order tables.
4. Recalculate:
   - 注数
   - 总投入
   - 每场投入
   - 回本线
   - 检查记录
5. Read the file back after editing to verify.

## Post-Match Settlement

When the user provides results or a result screenshot:

1. Extract final scores.
2. Locate the matching daily Markdown file.
3. Compare actual scores with all recorded bets.
4. Use recorded odds to calculate returns.
5. If odds are missing, mark return as `待填写` or ask for the missing odds.
6. Calculate:
   - Match-level input, return, and profit/loss.
   - Daily total input, total return, and profit/loss.
   - Hit count by market type.
7. Update `今日战果`, `今日总结`, and add `命中明细` when helpful.
8. Track ROI by market type:
   - 比分
   - 胜平负 / 让球
   - 总进球数

If exact-score ROI is consistently poor after several days, reduce the exact-score bucket first.

## Safety And Honesty

- State clearly that betting is high variance.
- Never claim certain profit.
- Never fabricate team news, injuries, flight data, or mental-state information.
- Never fabricate historical records, player statistics, or club form. If data cannot be verified, mark it unknown and lower confidence.
- Never fabricate China sports-lottery market availability, 单关 status, or odds. If availability cannot be verified, mark `待店主确认` and keep it out of the default shop-owner order.
- Do not overfit old head-to-head records when coaches, squads, competition context, or player ages have changed.
- Use public sources only.
- Encourage budget control and loss caps.
- Follow local laws and platform rules.
