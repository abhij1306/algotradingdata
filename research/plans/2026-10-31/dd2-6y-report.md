# Drawdown round 2, 2016-2021 in-sample: six single changes on B1

Owner focus 2026-10-31: reduce drawdowns without idle cash. Six diagnostic runs on m3 at main
`f1c8472` (run.json format 1.6), one at a time, exactly the C2 list of `dd-6y-report.md`. Window
2016-01-01 to 2021-12-31 with the normal warm-up, NIFTY500_PIT, stocks only, ₹10L, database
read-only. No hold-out read. No engine code changed. Benchmark NIFTY 500 TRI `benchmark_cagr_pct`
**15.66%** (identical in every run). Short IDs are the first 8 characters of the run ID.

| Run | Single change | Against | Run ID |
| --- | --- | --- | --- |
| B1 | G3 p5 rotation alone (`combo-6y/b1-rotation.yaml`) | — | `01a19039-9a2c-75f7-87eb-9c4dbdba02b3` |
| R3 | `rotation.market_filter=true` (NIFTY 500 close > SMA200) | B1 | `01a1909e-3198-7255-ab87-686e48f28745` |
| E1 | `rotation.top_n=30` | B1 | `01a190dd-82c1-76b6-b2b7-a5b9d6b12cc8` |
| E2 | `rotation.vol_sessions=63` | B1 | `01a190de-9a34-7289-888d-02df4e2247fb` |
| E3 | `rotation.buffer_rank=30` | B1 | `01a190df-aa4f-714e-b0a1-aac6fb358b7d` |
| E4 | `rotation.rebalance=fortnight` | B1 | `01a190e0-b8ba-7459-a804-1ea70022c5d5` |
| E5 | `conventions: {regime_mult: policy}` | B1 | `01a190e2-e872-7068-9903-643cf0f7a786` |
| E6 | R3 + `regime={"index":"NIFTY 500","rule":"breadth_above","params":{"min_pct":30,"smooth_days":5}}` | R3 | `01a190e4-079c-7737-adc5-dbe8434a38e6` |

Files on m3 in `/data/workspace/backtests/dd2-6y/`: the six portfolio files, logs, `run_all.sh`,
`progress.log`, and two read-only scripts copied from dd-6y: `dd2_stats.py` → `stats.json` (every
metric, recomputed from trades.csv/equity.csv with the engine's `standard.book_metrics`) and
`dd2_windows.py` → `windows.json` (each run inside B1's five drawdown windows from
`dd-6y/anatomy-b1.json`). All six runs completed. Audit `warn` in all six, the same data-audit
digest as B1 for E1-E4 and E6. E5 recorded `regime_mult: "policy"` and rebalanced on all 72
month-ends, like B1, so no night lacked regime inputs.

## Verdict

- **Deployment first.** E1-E4 stay fully invested: 99.2-99.4% invested, 19.97-29.94 positions,
  0.07% zero-position days, the same as B1 (99.38%). E5 is **66.6%** invested: 19.99 positions at
  3.33% each. It never goes flat, but it sits under 40% invested on 26.1% of days (`01a190e2`). E6 is
  **76.0%** invested with **23.4%** zero-position days (`01a190e4`). That is better than R3 (72.1% /
  27.5%) but still idle about a quarter of the time.
- **Only E2 (`vol_sessions=63`) cuts drawdown while staying fully invested.** Max DD is 34.19 vs 35.34
  (−1.15), avg DD 3.12 vs 3.54, and CAGR is *higher*: 27.98 vs 26.88. Sharpe is 1.28, Sortino 1.75
  and Calmar 0.82, all the best of the deployment-neutral runs (`01a190de`). It cuts 4 of B1's 5
  episodes by 0.75-1.43 pts. Episode 4 is 0.43 pts deeper. The gain is real but small. Costs: 2016 is
  −8.08 vs −5.97, 2018 is −11.10 vs −5.57, and the longest losing streak is 15 trades vs 9. **Keep.**
- **E1, E3 and E4 do not cut max DD. Reject all three.**
  - E1 (`top_n=30`) has the lowest avg DD of the four, 3.10, and trims every episode slightly
    (0.02-1.84 pts). But its 2018-08 and 2020 falls merge into one 36.33% drawdown, and CAGR drops
    2.9 pts to 23.94 with 80% more trades (590). The weight per name was not what drove the losses.
  - E3 (`buffer_rank=30`) makes max DD 37.57 and episode 2 25.73 (+2.37): with a tighter buffer it
    churns into the same falling leaders sooner.
  - E4 (fortnight) cuts the 2020 crash by 1.66 pts but deepens episode 2 by 3.86 pts (27.22), from
    whipsaw. Max DD is 37.54 and fees are the highest, ₹105.4k.
- **E5 (policy regime multiplier) buys depth with return.** Max DD is 28.83 (−6.51) and the 2020 and
  2016-Q1 episodes are 20.76 and 5.27. But CAGR is 15.93, which is TRI (15.66). Calmar 0.55 is the
  worst here, MFE capture is 0.10, and 2018 is still −20.06 (`01a190e2`). The live table runs at
  0.25 for long spells, such as the five month-ends 2018-10 → 2019-02, and the month-end readings
  sit at 22-28% invested on 19 of 72. It is a costly de-risk that does not prevent the losses. **Reject.**
- **E6 (breadth gate instead of SMA200) is the best risk-adjusted rotation so far, but it is not fully
  invested.** Against R3, its single change: max DD is **28.55** vs 34.53 (−5.98), CAGR **24.85** vs
  20.36, invested 76.0 vs 72.1, Sharpe **1.39**, Sortino **1.92**, Calmar **0.87** (B1 0.76), CAGR
  per invested **32.69** and profit factor 3.13 (`01a190e4`). It cuts the 2020 crash to 7.96 and
  2016-Q4 to 19.66, but it bought the starting book in 2016-01 (episode 4: 16.83, R3 3.38). It did
  not catch 2018-01 (16.60, the same as B1), and 2018 is still −20.28. It fails the owner rule on
  idle cash: 23.4% zero-position days.
- **Stack proposal (not run):**
  1. **S1 = E2 alone as the new fully-invested baseline** (B1 + `vol_sessions=63`). It is the only
     tested change that passes the deployment rule and improves CAGR, max DD, avg DD, Sharpe and
     Calmar together.
  2. **S2 = E2 + E6** (`vol_sessions=63` + `market_filter=true` + breadth ≥30 smooth 5). The two
     mechanisms are separate, selection versus exposure, so the 1-1.5 pt cuts E2 made inside
     episodes 2, 3 and 5, which the gate did not catch, should add to E6's 2020 and 2016-Q4 cuts.
     Expect ~76% invested, so run it only together with a way to fill the gated-off months, such as
     the existing ETF overlay (`overlay: {sleeve: regime}`), which was excluded from this round.
  3. Not stackable: E1, E3, E4 (no max-DD gain) and E5 (CAGR at TRI). The episodes no knob reached
     are 2018-01 (all runs 14.6-17.2 except R3 19.6) and 2018-19 (best 21.5). They still point at
     the code levers in `dd-6y-report.md` §C3: a sector cap, a mid-month check, a beta cap.

## 1. Deployment and headline (lead table)

From `stats.json` (`book_metrics` recomputed; equal to run.json). Size = mean over sessions with a
position of value ÷ equity ÷ positions. Avg DD = mean drawdown over all sessions. TRI CAGR 15.66
for every run.

| Run | Invested % | Avg positions | Avg size % | Zero-pos days % | CAGR % | vs TRI | Max DD % | Avg DD % | Longest DD (sessions) | Sharpe | Sortino | Calmar | CAGR per invested |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 `01a19039` | 99.38 | 19.99 | 4.97 | 0.07 | 26.88 | +11.22 | 35.34 | 3.54 | 356 (2018-08-31 → 2020-02-12) | 1.22 | 1.67 | 0.76 | 27.05 |
| R3 `01a1909e` | 72.08 | 14.50 | 4.97 | 27.46 | 20.36 | +4.70 | 34.53 | 3.33 | 723 (2018-01-23 → 2020-12-28) | 1.19 | 1.66 | 0.59 | 28.25 |
| E1 `01a190dd` | 99.18 | 29.94 | 3.31 | 0.07 | 23.94 | +8.28 | 36.33 | 3.10 | 476 (2018-08-31 → 2020-08-10) | 1.15 | 1.55 | 0.66 | 24.14 |
| **E2** `01a190de` | 99.31 | 19.97 | 4.97 | 0.07 | **27.98** | +12.32 | **34.19** | 3.12 | 352 (2018-08-31 → 2020-02-06) | 1.28 | 1.75 | 0.82 | 28.18 |
| E3 `01a190df` | 99.37 | 19.99 | 4.97 | 0.07 | 26.95 | +11.29 | 37.57 | 3.30 | 501 (2018-08-31 → 2020-09-14) | 1.23 | 1.68 | 0.72 | 27.13 |
| E4 `01a190e0` | 99.36 | 19.98 | 4.97 | 0.07 | 25.81 | +10.15 | 37.54 | 3.44 | 501 (2018-08-31 → 2020-09-14) | 1.19 | 1.64 | 0.69 | 25.98 |
| E5 `01a190e2` | 66.64 | 19.99 | 3.33 | 0.07 | 15.93 | +0.27 | 28.83 | **2.83** | 725 (2018-01-23 → 2020-12-30) | 1.06 | 1.45 | 0.55 | 23.91 |
| **E6** `01a190e4` | 76.02 | 15.29 | 4.97 | 23.42 | 24.85 | +9.19 | **28.55** | 3.53 | 622 (2018-01-23 → 2020-08-04) | **1.39** | **1.92** | **0.87** | **32.69** |

Every longest drawdown recovered in the window. Max-DD episodes (`windows.json` own top 3): E1, E3
and E4 2018-08-31 → 2020-03-23 (the 2018-19 grind and the 2020 crash merge); E2 2020-02-19 →
2020-03-24; E5 2018-01-23 → 2020-03-23; E6 2018-01-23 → 2019-05-13.

E5 invested-% distribution (`01a190e2` equity.csv): p10 25.1, p25 27.7, median 74.2, p75 99.4. 26.1%
of days are under 40% and 47.1% under 60%.

## 2. Trade efficiency and turnover

Whole trades (legs summed). The rotation has no stop, so R is return on cost. Planned R:R n/a.

| Run | Trades | Profit factor | Win % | Avg win % | Avg loss % | Payoff | MFE capture | Max consec losses | CAGR ex top-5 % | Top-5 share % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 `01a19039` | 328 | 3.02 | 51.2 | +28.4 | −11.3 | 2.53 | 0.26 | 9 | 19.86 | 38.1 |
| R3 `01a1909e` | 331 | 2.68 | 48.9 | +25.0 | −9.4 | 2.65 | 0.26 | 9 | 13.95 | 41.7 |
| E1 `01a190dd` | 590 | 2.60 | 49.0 | +25.6 | −10.6 | 2.42 | 0.24 | 11 | 18.93 | 30.3 |
| E2 `01a190de` | 342 | **3.34** | **54.7** | +26.2 | −11.3 | 2.32 | 0.27 | 15 | **21.02** | 36.9 |
| E3 `01a190df` | 398 | 2.72 | 51.0 | +25.7 | −10.8 | 2.38 | 0.25 | 10 | 20.09 | 37.3 |
| E4 `01a190e0` | 383 | 2.59 | 48.3 | +25.7 | −10.6 | 2.42 | 0.22 | 13 | 19.00 | 38.0 |
| E5 `01a190e2` | 328 | 2.46 | 46.3 | +19.4 | −10.2 | 1.90 | 0.10 | 9 | 10.05 | 45.6 |
| E6 `01a190e4` | 371 | 3.13 | 50.9 | +24.4 | −9.3 | 2.62 | **0.28** | 11 | 17.89 | 39.6 |

Turnover (`rebalances.csv`, filled orders) and fees:

| Run | Rebalance days | Buys / sales / trims / top-ups | Sales: out / not eligible / filter | Traded ₹L | Fees ₹ | Cost share % |
| --- | --- | --- | --- | --- | --- | --- |
| B1 `01a19039` | 72 | 328 / 308 / 475 / 395 | 231 / 77 / 0 | 597.6 | 86,172 | 2.64 |
| R3 `01a1909e` | 59 | 331 / 311 / 293 / 266 | 149 / 42 / 120 | 490.4 | 69,806 | 3.31 |
| E1 `01a190dd` | 72 | 590 / 560 / 683 / 486 | 419 / 141 / 0 | 626.2 | 97,267 | 3.57 |
| E2 `01a190de` | 72 | 342 / 322 / 464 / 389 | 253 / 69 / 0 | 617.5 | 88,651 | 2.54 |
| E3 `01a190df` | 72 | 398 / 378 / 469 / 335 | 294 / 84 / 0 | 714.2 | 100,505 | 3.06 |
| E4 `01a190e0` | 145 | 383 / 363 / 877 / 884 | 253 / 110 / 0 | 697.2 | 105,367 | 3.43 |
| E5 `01a190e2` | 72 | 328 / 308 / 539 / 402 | 231 / 77 / 0 | 458.2 | 68,602 | 4.58 |
| E6 `01a190e4` | 64 | 371 / 351 / 287 / 281 | 150 / 41 / 160 | 572.7 | 80,373 | 2.80 |

E5 makes the same buys and sales as B1 (328 / 308): the multiplier only resizes the book, with
trims worth ₹95.7L vs B1's ₹47.2L. E6 sold on the filter on 9 days (2016-02-01, 2016-12-01,
2018-03-01, 2018-06-01, 2018-10-01, 2018-10-03, 2019-02-01, 2019-07-01, 2020-03-02); R3 sold on 7
(2017-01-02, 2018-04-02, 2018-07-02, 2018-10-01, 2018-10-03, 2019-08-01, 2020-03-02). The breadth
gate exits a month earlier in 2016-Q4, 2018-Q1/Q2 and 2019, and it re-enters sooner, hence the
higher invested %.

## 3. Per year: return % / invested % / in-year max DD %

From run.json `by_year` and equity.csv. TRI in-year max DD from `dd-6y-report.md` §3 (`benchmark_tri`).

| Year | TRI ret (in-yr DD) | B1 `01a19039` | R3 `01a1909e` | E1 `01a190dd` | E2 `01a190de` | E3 `01a190df` | E4 `01a190e0` | E5 `01a190e2` | E6 `01a190e4` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2016 | +5.12 (13.8) | −5.97 / 99.6 / 21.7 | +2.80 / 67.7 / 22.5 | −8.28 / 99.5 / 21.0 | −8.08 / 99.6 / 20.5 | −4.31 / 99.6 / 21.2 | −5.17 / 99.3 / 22.4 | +4.27 / 71.1 / 19.6 | −1.31 / 74.3 / 19.8 |
| 2017 | +37.65 (4.8) | +76.38 / 99.5 / 8.4 | +58.08 / 91.0 / 8.4 | +66.11 / 98.6 / 8.2 | +80.78 / 99.1 / 7.9 | +78.86 / 99.4 / 7.3 | +70.76 / 99.4 / 8.1 | +44.63 / 77.1 / 8.4 | +56.21 / 90.7 / 8.5 |
| 2018 | −2.14 (15.6) | −5.57 / 99.5 / 23.1 | −22.62 / 57.5 / 25.9 | −10.16 / 99.1 / 21.5 | −11.10 / 99.4 / 22.5 | −9.91 / 99.5 / 22.6 | −6.00 / 99.5 / 22.9 | −20.06 / 51.9 / 24.7 | −20.28 / 49.3 / 25.4 |
| 2019 | +8.97 (11.5) | +14.58 / 99.5 / 13.3 | −1.06 / 58.4 / 13.6 | +9.62 / 99.6 / 12.0 | +14.99 / 99.5 / 13.6 | +11.31 / 99.6 / 13.3 | +6.73 / 99.6 / 15.1 | +9.69 / 56.0 / 7.4 | +8.94 / 58.4 / 7.8 |
| 2020 | +17.89 (38.1) | +31.14 / 99.2 / 35.3 | +37.87 / 58.8 / 7.6 | +38.88 / 99.3 / 35.1 | +37.23 / 99.3 / 34.2 | +34.60 / 99.2 / 36.2 | +36.45 / 99.4 / 33.7 | +19.59 / 62.7 / 20.8 | **+59.43** / 83.8 / 8.0 |
| 2021 | +31.60 (9.8) | +77.38 / 99.0 / 6.6 | +77.31 / 98.9 / 6.6 | +74.00 / 99.0 / 8.1 | +88.57 / 99.1 / 8.1 | +81.31 / 99.0 / 7.1 | +78.98 / 99.0 / 8.4 | +53.57 / 80.9 / 6.5 | +77.46 / 99.0 / 6.6 |

- Every run's in-year DD is deeper than TRI's in 2016, 2017 and 2018. The 2020 in-year DD is under
  TRI's 38.1 only in the gated or scaled runs: R3 7.6, E6 8.0, E5 20.8.
- E2 beats TRI in 4 years (2017, 2019, 2020, 2021), like B1, and misses in 2016 and 2018 by more than
  B1. E6 beats TRI in 3 (2017, 2020, 2021); it misses 2019 by 0.03 pt, and 2016 and 2018.

## 4. B1's five drawdown episodes: depth in each run

Max drawdown inside B1's peak → recovery window (Part B dates), from each run's own running peak
inside the window (`windows.json`). Δ is vs B1, and for E6 also vs R3. In brackets: the run's average invested % in the window.

| # | B1 window | B1 `01a19039` | R3 `01a1909e` | E1 `01a190dd` | E2 `01a190de` | E3 `01a190df` | E4 `01a190e0` | E5 `01a190e2` | E6 `01a190e4` (Δ vs R3) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2020-02-19 → 2020-09-14 | 35.34 | 6.65 (−28.69) [27] | 35.09 (−0.25) | 34.19 (−1.15) | 36.21 (+0.87) | 33.68 (−1.66) | 20.76 (−14.58) [48] | **7.96** (−27.38; +1.31) [72] |
| 2 | 2018-08-31 → 2020-02-12 | 23.36 | 26.98 (+3.62) [54] | **21.52** (−1.84) | 22.61 (−0.75) | 25.73 (+2.37) | 27.22 (+3.86) | 21.58 (−1.78) [55] | 24.05 (+0.69; −2.93) [60] |
| 3 | 2016-10-25 → 2017-03-16 | 21.71 | 22.39 (+0.68) [79] | 20.96 (−0.75) | 20.28 (−1.43) | 21.23 (−0.48) | 22.40 (+0.69) | **19.59** (−2.12) [73] | 19.66 (−2.05; −2.73) [56] |
| 4 | 2016-01-01 → 2016-07-27 | 20.06 | **3.38** (−16.68) [44] | 19.48 (−0.58) | 20.49 (+0.43) | 20.06 (0.00) | 19.10 (−0.96) | 5.27 (−14.79) [58] | 16.83 (−3.23; +13.45) [71] |
| 5 | 2018-01-23 → 2018-07-11 | 16.62 | 19.64 (+3.02) [75] | 16.60 (−0.02) | 15.42 (−1.20) | 17.00 (+0.38) | 17.18 (+0.56) | **14.62** (−2.00) [55] | 16.60 (−0.02; −3.04) [40] |

E1-E4 sit at 98.2-99.7% invested in every window.

Reading:
- **Deployment-neutral knobs cut no episode by more than 1.84 pts.** Among E1-E4, E2 is the only one that lowers max DD and
  raises CAGR, and it is better in 4 of 5 episodes (by 0.75-1.43); E1 is better in all 5, but only by 0.02-1.84. E3 and E4 deepen
  episode 2, the 2018-19 grind, by 2.4-3.9 pts: a faster exit sells into a falling momentum
  market and rebuys the next fading leaders.
- **The exposure knobs work only in episodes 1 and 4,** and E6 only in 1 and 3. No run cuts episode 5
  (2018-01, 9 sessions, gate on) by more than 2 pts. Episode 2 never falls below 21.5, whatever the
  invested level.
- **E6 vs R3, episode by episode:** better in 2, 3 and 5 by 2.7-3.0 pts, slightly worse in the 2020
  crash (+1.3), and much worse in 2016-Q1 (+13.5). Breadth read on at 2015-12-31, so E6 bought the
  starting book and sold it at 2016-02-01 after most of the fall. R3's SMA200 was already off.

Rules kept: venv python on m3, `PGOPTIONS default_transaction_read_only=on`, one run at a time with
the ≥2.5 GB check (7.0 GB available at each start), no `.env` access, no commits, no engine change,
nothing on m1, no hold-out.
