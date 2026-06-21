# China Sports Lottery Availability Check

Read this reference before finalizing any shop-owner order.

## Goal

Confirm whether the user can actually place each intended market through China sports lottery / 竞彩 before recommending the slip. A strong prediction is not useful if the shop owner cannot issue that market.

## Source Order

1. Official China Sports Lottery / 中国竞彩网 pages:
   - 中国体彩网 football schedule: `https://www.lottery.gov.cn/football/match_list.jspx`
   - 竞彩网 football schedule: `https://www.sporttery.cn/jc/zqszsc/`
   - 竞彩足球胜平负 page: `https://www.sporttery.cn/jc/jsq/zqspf/`
2. If official pages fail or are blocked, use secondary sources such as 500.com or 足彩网 only as provisional evidence.
3. If official and secondary sources conflict, trust the official source or mark the market `待店主确认`.
4. If no reliable source confirms the market, keep it out of the default shop-owner order.

## Fields To Check

For every fixture, record:

- `赛事编号`
- `联赛`
- `主队 vs 客队`
- `比赛开始时间`
- `开售状态`
- `胜平负`
- `让球胜平负`
- `比分`
- `总进球数`
- `半全场胜平负`
- `特别提示`

## Availability Rules

- `开售单关`: usable in the default single-bet slip.
- `开售单关+过关`: usable in the default single-bet slip.
- `仅开售过关`: not usable in the default single-bet slip unless the user explicitly asks for parlays.
- `未开售此游戏`: not usable.
- Blank, hidden, suspended, unavailable, or unclear status: treat as not usable until confirmed.
- If kickoff is close, re-check because sales can stop before the match.

## Workflow

1. Extract all fixtures from the screenshot.
2. Query official schedule pages for the same date.
3. Match fixtures by team names, kickoff time, and competition. Be careful with translated names.
4. Build this table before the recommendation:

`场次 | 比赛 | 开售状态 | 胜平负单关 | 让球胜平负单关 | 比分单关 | 总进球数单关 | 处理`

5. Only construct order rows from markets confirmed usable for 单关.
6. If a strong direction market is unavailable, do not force it into the slip. Reallocate to:
   - the same match's confirmed-open total-goals market if it agrees with the score cluster;
   - another match's confirmed-open lower-variance direction market;
   - or reduce the total stake if no clean replacement exists.
7. Keep unavailable ideas in `未开/待确认，不下单`.

## Response Pattern

Use concise language:

- `体彩开售检查：#34 厄瓜多尔 vs 库拉索 胜平负未确认单关，所以不放入胜平负单。`
- `店主反馈未开后，已移除该市场并用总进球数/其他确认单关市场补足预算。`
- `官方页面不可访问时，此项标为待店主确认，不进入默认下单表。`
