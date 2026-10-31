# wf10b: universe cross-check and two drawdown levers, 2012-07-02 → 2021-12-31

Follow-up to `wf10-report.md`, same window, rules and stats script (`plans/wf10b-work/stats.json`,
configs in `plans/wf10b-work/configs/`). m3 at main 7fe0ddeb (#356). Each config run once; configs
fixed before results. 2022–2025 not read.

| Run | Config |
| --- | --- |
| d0 | c1 (momentum core + 1/beta weights) on NIFTY500_PIT: replay check |
| d1 | c1 on TOP_TRADED (rule-based top 500 by traded value) |
| d2 | c1 + `industry_relative` (score vs own industry) |
| d3 | c1 + `wide_book` (30 names when breadth ≤ 40%; fired on 41 rebalances) |
| d4 | c1 + both |

## Verdict

- **Replay is exact:** d0 = c1 to the rupee (32.17% CAGR, 522 trades). The new engine options are inert when off.
- **The momentum signal holds on a rule-based universe:** d1 31.1% CAGR vs TRI 15.7, PF 3.0, top-5-trade
  share 28% (vs 34%). But its drawdowns are worse (max DD 38.9, 2016 −22 pts vs TRI with in-year DD 25%)
  → NIFTY500_PIT stays the universe.
- **Neither drawdown lever earns its place.** Industry-relative cuts 2016 (−6.0 vs −9.6) but worsens 2013
  (−6.0) and 2018 (in-year DD 21.9 vs 19.4) and costs 1.5 CAGR. Wide book in weak breadth barely moves
  drawdowns (2016 DD 20.1, 2018 20.9 vs 19.4) and costs 1.5 CAGR. Both together is worst (28.1%, MAR 0.74).
- **c1 stays the momentum core.** Down-year drawdown (1.3–1.5× TRI in 2016/2018) is still open; price-only
  levers are now exhausted (stops, intra-month exits, tranches, skip, sector-relative, wider book all
  tried). The remaining lever with a rationale is the quality/value screen, which needs the parked
  fundamentals backfill (#352).

## Full window

| | c1/d0 | d1 TOP_TRADED | d2 ind-rel | d3 wide | d4 both |
| --- | --- | --- | --- | --- | --- |
| Invested % | 99.2 | 98.7 | 99.1 | 99.0 | 99.0 |
| Avg positions / size % | 20 / 5.0 | 20 / 4.9 | 20 / 5.0 | 23.5 / 4.4 | 23.6 / 4.4 |
| CAGR % (TRI 15.73) | **32.17** | 31.11 | 30.62 | 30.70 | 28.12 |
| Max DD % | 35.0 | 38.9 | 35.8 | 34.7 | 37.9 |
| Avg DD % / longest (sessions) | 2.79 / 342 | 3.16 / 475 | 2.87 / 327 | 2.79 / 361 | 3.00 / 353 |
| Sharpe / Sortino | **1.59 / 2.20** | 1.44 / 1.96 | 1.53 / 2.11 | 1.55 / 2.13 | 1.44 / 1.96 |
| MAR / PF | **0.92 / 3.96** | 0.80 / 3.00 | 0.85 / 3.89 | 0.88 / 3.60 | 0.74 / 3.09 |
| CAGR ex top-5 trades | 27.0 | 27.1 | 25.1 | 25.8 | 23.1 |
| Trades | 522 | 553 | 543 | 632 | 659 |

## Per year: excess over NIFTY 500 TRI (pts) / in-year max DD % (TRI DD)

| Year | TRI % | c1 | d1 | d2 | d3 | d4 |
| --- | --- | --- | --- | --- | --- | --- |
| 2012 H2 | 14.1 | 0.1 / 3.6 (5.4) | 13.4 / 4.5 | 1.6 / 3.8 | 0.4 / 3.6 | 0.7 / 3.8 |
| 2013 | 4.8 | −1.2 / 20.0 (15.9) | 4.4 / 18.6 | −6.0 / 22.7 | 3.5 / 16.7 | −1.7 / 18.3 |
| 2014 | 39.3 | 42.7 / 8.9 (6.7) | 50.9 / 7.9 | 25.6 / 9.2 | 44.5 / 8.9 | 30.0 / 9.2 |
| 2015 | 0.2 | 21.1 / 14.5 (13.3) | 16.6 / 15.9 | 20.9 / 14.2 | 20.7 / 13.2 | 15.6 / 14.2 |
| 2016 | 5.1 | −9.6 / 20.0 (13.8) | −22.1 / 25.5 | −6.0 / 18.9 | −8.1 / 20.1 | −4.6 / 18.2 |
| 2017 | 37.7 | 40.6 / 7.2 (4.8) | 52.1 / 9.2 | 27.0 / 7.9 | 35.3 / 7.2 | 27.3 / 8.6 |
| 2018 | −2.1 | −2.5 / 19.4 (15.6) | −7.2 / 21.9 | −5.4 / 21.9 | −6.8 / 20.9 | −7.7 / 24.4 |
| 2019 | 9.0 | 3.1 / 14.2 (11.5) | −2.4 / 12.5 | 9.7 / 11.5 | −0.5 / 12.7 | 3.4 / 12.7 |
| 2020 | 17.9 | 30.5 / 35.0 (38.1) | 48.0 / 34.5 | 39.2 / 35.8 | 30.5 / 34.7 | 33.3 / 37.9 |
| 2021 | 31.6 | 70.6 / 7.6 (9.8) | 36.1 / 11.7 | 66.7 / 7.1 | 57.4 / 8.8 | 48.3 / 9.3 |

## Next (proposal)

1. Freeze c1 on NIFTY500_PIT as the momentum core candidate.
2. Drawdown: resume the fundamentals backfill (#352, owner go needed) and test a quality screen
   (ROCE, debt, CFO > 0) and an expensive-quintile exclusion inside c1, 2012–2021 only.
3. Final check 2026-01-01 → latest plus paper trading only after step 2 (owner agreement).
