---
name: world-cup-predict-skill
description: World Cup and football betting workflow for Codex. Use when the user sends fixture screenshots or result screenshots and wants match analysis, exact-score predictions, China sports-lottery style single-bet slips, odds/ROI reasoning, bankroll risk control, shop-owner order tables, Markdown record creation, or post-match settlement with returns and profit/loss. Browse for current odds, team news, injuries, recent form, travel fatigue, and public morale signals before making recommendations.
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

2. Browse for current information because sports data changes:
   - China sports-lottery related odds or 500.com style odds when accessible.
   - Correct-score SP odds.
   - 胜平负 / 让球胜平负 availability and whether 单关 is open.
   - 总进球数 odds and availability.
   - Team news, injuries, suspensions, likely lineups, and coach comments.
   - Recent form and scoring profile.
   - Travel, venue, time-zone, weather, rest-day, and arrival reports.
   - Public morale signals from official accounts, press conferences, reliable sports outlets, and training reports.

3. Separate facts from inference:
   - Use `可确认...` for confirmed information.
   - Use `公开报道显示...` for sourced reports.
   - Use `我推断...` for analysis.
   - Use `没有可靠公开信息支持...` when a claim cannot be verified.

4. Build predictions from:
   - Team strength and tactical matchup.
   - Expected scoring intensity and score distribution.
   - Odds and implied probabilities.
   - Injury and lineup effects.
   - Travel/rest/fatigue effects.
   - Public morale and motivation.
   - User's budget and risk preference.

## Risk-Optimized Strategy

Do not optimize for buying many outcomes. Optimize for positive expected value, controlled drawdown, and lower correlation.

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
- In national-team tournaments, weigh current availability, rest, travel, and motivation more than old historical form.

## Slip Construction Rules

Default:

- Every row is `2元` unless the user says otherwise.
- All bets are single bets unless the user explicitly asks for parlays.
- If a market is not open for 单关, do not include it in the single-bet shop-owner slip.
- If the shop owner says a market is unavailable, rebuild the slip with the same budget when possible.

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
2. `今日订单`
3. `店主下单内容`
4. `推荐标记`
5. `综合分析`
6. `新闻/旅途/精神状态`
7. `检查记录`
8. `今日战果`
9. `今日总结`
10. `参考信息`

Use Markdown tables.

When odds are known, include:

`场次 | 比分/玩法 | 投注内容 | 金额 | 参考赔率 | 命中回报`

For `新闻/旅途/精神状态`, use:

`场次 | 近期新闻 | 旅途/休整 | 精神状态判断 | 对比分影响`

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
- Use public sources only.
- Encourage budget control and loss caps.
- Follow local laws and platform rules.
