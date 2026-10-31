# 10-year in-sample walk-forward, 2012-07-02 → 2021-12-31 (wf10)

Owner pre-approved 2026-10-31. Eight momentum-rotation configs, each run once on m3 (main ad75552 /
ae94742; #354 only renamed an unused key), NIFTY500_PIT (membership from 2011-06-22, #350), stocks only,
₹10L, hat_live read-only. Configs fixed before any result: `plans/wf10-work/configs/`; numbers:
`plans/wf10-work/stats.json` (script `wf10_stats.py`; run folders on m3 under `wf10/`).
2012 is a half year (from July). 2022–2025 is a spent hold-out and was not read.

| Run | Config (base = E2 rotation, vol 63) |
| --- | --- |
| ref | E2 as before: ₹10 cr turnover floor, no realism |
| c0 | base: refuse buys near the upper band, size-aware impact (100 bps·√(order/ADV)), relative liquidity floor (top 70% to buy, top 90% to hold) |
| c1 | c0 + 1/beta weights (252 sessions, floor 0.5) |
| c2 | c0 + 4 staggered tranches, 4 sessions apart |
| c3 | c0 + score skips the last 21 sessions |
| c4 | c1 + c2 (1/beta + tranches) |
| c5 | c1 + c3 (1/beta + skip) |
| c6 | c2 + c3 (tranches + skip) |

## Verdict

- **Deployment is not the problem:** every config is 98.6–99.5% invested, 0.04% zero-position days,
  20 positions (80 tranche sub-positions in c2/c4/c6).
- **The momentum core beats the index over 10 years:** c0 31.9% CAGR vs NIFTY 500 TRI 15.7%, Sharpe
  1.52, profit factor 3.6, CAGR ex top-5 trades 27.1%. Realism (band refusal, impact) and the relative
  floor did not hurt: c0 is +2.6 CAGR over ref.
- **Walk-forward pass rule** (beats TRI in most test years 2015–2021, worst test year no worse than c0):
  only **c1 (1/beta weights) passes**: beats TRI in 5 of 7 test years, worst year 2016 −9.6 vs c0 −9.8,
  best risk-adjusted numbers (Sharpe 1.59, Sortino 2.20, MAR 0.92, PF 3.96, avg DD 2.79). Tranches and
  the 21-session skip each made 2018 much worse (−10.9 to −12.0 vs c0 −3.6) → rejected.
- **Drawdowns are still the weak point:** max DD 34–39% (2020, TRI 38%), and in ordinary down years
  the book falls ~1.3–1.5× the TRI (2016 in-year DD 20% vs 14%; 2018 19–24% vs 16%). Years that trail
  the TRI by a lot: 2016 (−6 to −12 pts in every config) and 2018 (−2.5 to −12).
- **The edge is lumpy:** 2014, 2017, 2020 and 2021 carry most of it; 2013, 2016, 2018 and 2019 are at
  or below the index. Tranches cut the top-5-trade share from ~32% to ~10% but raised the drawdowns.

## Per year: excess return over NIFTY 500 TRI (points)

| Year | TRI % | ref | c0 | **c1** | c2 | c3 | c4 | c5 | c6 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2012 (H2) | 14.1 | −6.4 | −0.7 | 0.1 | 2.7 | −0.5 | 4.1 | 0.8 | 1.7 |
| 2013 | 4.8 | 8.2 | −2.3 | −1.2 | 1.0 | −2.3 | 1.8 | −0.2 | −2.8 |
| 2014 | 39.3 | 39.0 | 48.6 | 42.7 | 52.7 | 37.7 | 46.6 | 34.3 | 42.0 |
| 2015 | 0.2 | 17.9 | 18.6 | 21.1 | 13.5 | 22.0 | 15.6 | 21.0 | 10.5 |
| 2016 | 5.1 | −11.6 | −9.8 | −9.6 | −6.2 | −8.3 | −5.9 | −9.9 | −7.9 |
| 2017 | 37.7 | 43.9 | 49.3 | 40.6 | 44.5 | 35.4 | 35.9 | 31.3 | 34.1 |
| 2018 | −2.1 | −9.0 | −3.6 | −2.5 | −11.0 | −11.5 | −11.1 | −12.0 | −10.3 |
| 2019 | 9.0 | 6.1 | 4.4 | 3.1 | −0.4 | 6.2 | −2.4 | 6.1 | 6.2 |
| 2020 | 17.9 | 19.6 | 29.0 | 30.5 | 20.9 | 28.3 | 20.6 | 27.9 | 30.9 |
| 2021 | 31.6 | 57.1 | 61.0 | 70.6 | 59.0 | 68.1 | 64.5 | 74.2 | 57.7 |

In-year max DD, c1 vs TRI: 2013 20.0/15.9, 2016 20.0/13.8, 2018 19.4/15.6, 2020 35.0/38.1.

## Full window (lead metrics first)

| | ref | c0 | **c1** | c2 | c3 | c4 | c5 | c6 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Invested % | 99.5 | 99.3 | 99.2 | 98.8 | 99.1 | 98.7 | 99.1 | 98.6 |
| Avg positions | 20 | 20 | 20 | 80 | 20 | 80 | 20 | 80 |
| Avg position size % | 5.0 | 5.0 | 5.0 | 1.2 | 5.0 | 1.2 | 5.0 | 1.2 |
| CAGR % (TRI 15.73) | 29.34 | 31.92 | **32.17** | 30.03 | 30.14 | 29.55 | 29.89 | 29.00 |
| Max DD % | 34.2 | 36.4 | 35.0 | 38.9 | 35.7 | 37.3 | 34.1 | 36.3 |
| Avg DD % | 3.20 | 2.94 | 2.79 | 2.97 | 2.78 | 2.97 | 2.54 | 2.95 |
| Longest DD (sessions) | 352 | 343 | 342 | 501 | 356 | 502 | 503 | 344 |
| Sharpe / Sortino | 1.37/1.90 | 1.52/2.09 | **1.59/2.20** | 1.45/1.98 | 1.44/1.97 | 1.50/2.05 | 1.50/2.06 | 1.42/1.94 |
| Calmar (MAR) | 0.86 | 0.88 | **0.92** | 0.77 | 0.84 | 0.79 | 0.88 | 0.80 |
| Profit factor | 3.48 | 3.64 | **3.96** | 3.00 | 3.49 | 3.12 | 3.57 | 3.23 |
| Win % / payoff (%) | 56/2.45 | 54/2.72 | 54/2.60 | 51/2.81 | 55/2.48 | 51/2.69 | 55/2.43 | 55/2.40 |
| Expectancy R | 0.10 | 0.11 | 0.10 | 0.11 | 0.09 | 0.10 | 0.09 | 0.09 |
| MFE capture | 0.28 | 0.28 | 0.26 | 0.27 | 0.30 | 0.25 | 0.29 | 0.30 |
| CAGR ex top-5 trades | 24.9 | 27.1 | 27.0 | 28.8 | 25.9 | 27.7 | 25.1 | 27.7 |
| Top-5 trades P&L share % | 31 | 32 | 34 | 10 | 29 | 14 | 33 | 10 |
| Fees ₹ | 2.54L | 2.70L | 2.76L | 3.34L | 2.74L | 3.38L | 2.77L | 3.27L |

## Walk-forward (pick = best Calmar over the prior 3 years; criterion fixed before results)

| Test year | Pick | Return % | TRI % | Excess | c0 excess |
| --- | --- | --- | --- | --- | --- |
| 2015 | c4 | 15.8 | 0.2 | 15.6 | 18.6 |
| 2016 | c4 | −0.8 | 5.1 | −5.9 | −9.8 |
| 2017 | c2 | 82.1 | 37.7 | 44.5 | 49.3 |
| 2018 | c1 | −4.6 | −2.1 | −2.5 | −3.6 |
| 2019 | c0 | 13.4 | 9.0 | 4.4 | 4.4 |
| 2020 | c1 | 48.4 | 17.9 | 30.5 | 29.0 |
| 2021 | c1 | 102.2 | 31.6 | 70.6 | 61.0 |

The selection beats the TRI in 5 of 7 test years and lands on c1 from 2018 on. Selecting among
variants adds little over c0; the core signal does the work.

## Next (proposal)

1. **Carry c1 (base + 1/beta) as the momentum core.** Drop tranches and the 21-session skip.
2. **Drawdown is the open problem:** the book loses 1.3–1.5× the TRI in ordinary down years (2016,
   2018). Candidates with a clear rationale, to test in-sample 2012–2021 only: a quality/value filter
   on the candidate list (needs the fundamentals backfill, #352), sector-neutral momentum, and holding
   more names in down markets (wider book instead of cash).
3. **Universe cross-check:** rerun c0/c1 on a rule-based top-500-by-traded-value universe (needs a
   small engine option).
4. **Final check (owner agreement needed):** 2026-01-01 → latest, once for the frozen candidate, plus
   paper trading.
