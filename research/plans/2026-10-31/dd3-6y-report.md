# Drawdown round 3, 2016-2021 in-sample: the S2 stack, overlap with VCP, industry cap, scale-down

Owner go 2026-10-31. Ten diagnostic runs on m3, one at a time (F1-F3, G1-G4, and H1-H3 in §H). F1-F3 ran at main `7dc96ff` (the
overlap convention, #346). G1-G4 and H1-H3 ran at main `a672820` (`rotation.max_per_industry`,
`unknown_industry`, `scale_down`, #347). m3 was pulled only after F3 had finished. Window 2016-01-01
to 2021-12-31 with the normal warm-up, NIFTY500_PIT, stocks only, ₹10L, database read-only. No
hold-out read. No engine code changed. Benchmark NIFTY 500 TRI `benchmark_cagr_pct` **15.66%** in
every run. Short IDs are the first 8 characters of the run ID.

| Run | Change | Against | Run ID |
| --- | --- | --- | --- |
| B1 | G3 p5 rotation alone | — | `01a19039-9a2c-75f7-87eb-9c4dbdba02b3` |
| E2 | B1 + `rotation.vol_sessions=63` | B1 | `01a190de-9a34-7289-888d-02df4e2247fb` |
| E6 | B1 + `market_filter=true` + regime `breadth_above` 30, smooth 5 | R3 | `01a190e4-079c-7737-adc5-dbe8434a38e6` |
| C1 | rotation 0.7 + old VCP 0.3 (combo-6y, no overlap) | — | `01a19057-3390-75bf-b3bd-593b77a217e2` |
| R5 | old VCP alone, no swing-low trail, SMA50 close exit kept | B2 | `01a1909f-47b1-74fb-825c-c77bbb8153ed` |
| **F1** | S2 = E2 + E6 (`vol_sessions=63`, `market_filter=true`, breadth ≥30 smooth 5), no overlay | E2, E6 | `01a190e9-1bec-7064-9282-00c318debd03` |
| **F2** | `overlap: true`: rotation E2 at weight 1.0 + VCP R5 at weight 0.3, account keys as C1 | E2, C1 | `01a190ea-285d-72b7-a58a-cc20bbc59225` |
| **F3** | as F2 with rotation = F1 | F1, F2 | `01a190f7-118f-72e7-b395-131aa9f82072` |
| **G1** | E2 + `rotation.max_per_industry=4` (`unknown_industry` free) | E2 | `01a19104-7400-761d-a38b-346831b18ce7` |
| **G2** | E2 + `max_per_industry=4`, `unknown_industry=bucket` | E2 | `01a19105-82ff-7651-b867-8a640487e00f` |
| **G3** | E2 + `scale_down` {NIFTY 500 close > SMA50 (`rising_days` 0); any_off; keep 0.5} | E2 | `01a19106-8db3-705c-962f-0bc7fdabe28e` |
| **G4** | E2 + `scale_down` {`breadth_above` 30, smooth 5; any_off; keep 0.5} | E2 | `01a19107-ab5e-70ae-b032-e33221a14d7c` |

Files on m3 in `/data/workspace/backtests/dd3-6y/`: the seven portfolio files, logs, `run_all.sh`,
`progress.log`, and read-only scripts with their output:
- `dd3_stats.py` → `stats-f.json`, `stats-g.json`: every metric, recomputed with the engine's `standard.book_metrics`.
- `dd3_windows.py` → `windows-f.json`, `windows-g.json`: each run inside B1's five drawdown windows.
- `dd3_overlap.py` → `overlap.json`: funding sales, VCP refusals, sleeve shares.
- `dd3_levers.py` → `levers.json`: scale-down trims and industry counts.
- `dd3_dump.py`: prints the tables.

All seven runs completed with audit `warn`, as did every earlier run. Overlap runs record
`overlap: {funding: rotation_sells_weakest_rank_first, rotation_capital:
weight_x_equity_less_open_funded_at_mark}` in their conventions.

## Verdict

- **Round H (stacks) and the ranking of every candidate are in §H.5. Recommended: H3** (E2 +
  industry cap 4 + breadth scale-down keep 0.75, `01a1910e`): 91.6% invested, never flat, CAGR 29.55,
  max DD 25.26, Calmar 1.17. The bullets below are rounds F and G as first reported.
- **Deployment first.** Fully invested: G1/G2 99.25% (0.07% zero days) and F2 95.7% (0.07%). Partial
  but never flat: G4 **84.0%** and G3 76.6% (both 0.07% zero days). Idle: F1 76.0% with **23.4%** zero
  days, the same exposure as E6; F3 74.6% with 10.6% zero days.
- **G1 (industry cap 4) is the best single change so far, and it costs nothing in deployment.**
  Against E2: CAGR **32.37** vs 27.98 (+4.39), max DD **31.74** vs 34.19 (−2.45), avg DD 2.94 vs 3.12,
  Sharpe 1.46, Sortino 2.03, Calmar **1.02** (E2 0.82), profit factor 4.11, CAGR ex top-5 25.36
  (`01a19104`). It cuts episodes 1, 3 and 4 by 1.3-2.5 pts, and 2020 is +65.87 vs +37.23. It does
  not help the 2018-19 grind: episode 2 is 23.33, 0.72 pts deeper than E2. **Keep.**
- **G2 is the same run as G1, number for number** (`01a19105`). No run ever held more than 3
  unknown-industry names at once, so with a cap of 4 the `bucket` rule never binds. The
  survivorship caveat is in §G.
- **G4 (breadth scale-down to 0.5) cuts the most drawdown of any run that never goes flat.** Max DD
  **23.86** vs E2 34.19 (−10.33), avg DD 2.86, Calmar 0.99, at 84.0% invested with 0.07% zero days
  (`01a19107`). The cost is CAGR 23.75 vs 27.98 (−4.23), 12 trim days and +107 top-ups. **Keep as
  the exposure lever** in place of the all-cash market filter.
- **G3 (SMA50 scale-down): reject.** It trimmed on 21 days. CAGR is 17.74 at 76.6% invested, MFE
  capture 0.11, and its max DD of 28.18 is worse than G4's (`01a19106`).
- **F1 (E2 + E6) is the best risk-adjusted run so far, but it holds idle cash.** CAGR **29.40**, max
  DD **24.54**, Sharpe **1.62**, Sortino 2.25, Calmar **1.20**, CAGR per invested 38.68
  (`01a190e9`). It has the same 23.4% zero-position days as E6. E2 and E6 stacked better than
  additive: against E6, CAGR is +4.55 and max DD −4.01.
- **F2 (overlap, E2 + VCP 0.3) keeps the book invested but does not earn its keep.** Invested is
  95.7% (C1 85.1%), max DD 30.36 (E2 34.19, C1 27.87), but CAGR is **23.29**: −4.69 vs E2, +1.00 vs C1.
  Calmar is 0.77, below E2's 0.82 and C1's 0.80 (`01a190ea`). The rotation funded VCP **241 times
  (87 sells + 154 trims), ₹72.1L on 130 days**. VCP was **never refused for cash** (C1: 136
  `size_zero_cash` + 179 `size_below_min`), but it was refused **428 times for slots**
  (`max_positions`; C1 162). The VCP sleeve averaged **19.2%** of equity (23.3% on days it held
  anything, 80.6% of days), against C1's 15.2%. Episode 5 (2018-01) is 21.02, worse than E2 by
  5.6 pts.
- **F3 does not confirm the idea that VCP fills the gated-off months.** On the 23.4% of days the
  rotation is flat, F3 is only **6.3% invested**: VCP held anything on just 54.6% of those days, at
  5.4% of equity on average. Zero-position days fall from 23.4% (F1) to **10.6%**, and invested is
  74.6%, slightly *lower* than F1's 76.0%, because funding sales shrink the rotation while it is
  on. Against F1, CAGR is 22.21 vs 29.40 and max DD 27.56 vs 24.54 (`01a190f7`). VCP breakouts dry
  up in the same weak-breadth months. **Reject.**
- **Proposed stack (not run):**
  1. **H1 = E2 + G1 + G4**: `vol_sessions=63`, `max_per_industry=4`, `scale_down` breadth ≥30
     smooth 5, keep 0.5. Three separate mechanisms (selection, concentration, exposure), each a
     win on its own, and none ever goes all-cash. Expect ~84% invested with ~0% zero days.
  2. **H2 = F1 + G1**, only if the owner accepts ~23% zero days for the best Calmar.
  3. If H1's 84% is too low, a single follow-up on H1 is `keep_fraction` 0.75.
  4. Not stackable: G3; F2/F3 overlap with this VCP (it dilutes CAGR and adds the 2018-01 loss).

## 1. Deployment and headline (lead table)

From `stats-f.json` / `stats-g.json` (`book_metrics` recomputed; equal to run.json). Size = mean
over sessions with a position of value ÷ equity ÷ positions. Avg DD = mean drawdown over all
sessions. TRI CAGR 15.66.

| Run | Invested % | Avg positions | Avg size % | Zero-pos days % | CAGR % | vs TRI | Max DD % | Avg DD % | Longest DD (sessions) | Sharpe | Sortino | Calmar | CAGR per invested |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 `01a19039` | 99.38 | 19.99 | 4.97 | 0.07 | 26.88 | +11.22 | 35.34 | 3.54 | 356 (2018-08-31 → 2020-02-12) | 1.22 | 1.67 | 0.76 | 27.05 |
| E2 `01a190de` | 99.31 | 19.97 | 4.97 | 0.07 | 27.98 | +12.32 | 34.19 | 3.12 | 352 (2018-08-31 → 2020-02-06) | 1.28 | 1.75 | 0.82 | 28.18 |
| E6 `01a190e4` | 76.02 | 15.29 | 4.97 | 23.42 | 24.85 | +9.19 | 28.55 | 3.53 | 622 (2018-01-23 → 2020-08-04) | 1.39 | 1.92 | 0.87 | 32.69 |
| C1 `01a19057` | 85.12 | 24.02 | 3.54 | 0.07 | 22.29 | +6.63 | 27.87 | 3.10 | 511 (2018-01-23 → 2020-02-19) | 1.25 | 1.70 | 0.80 | 26.18 |
| R5 `01a1909f` | 53.56 | 4.00 | 13.81 | 17.16 | 14.01 | −1.65 | 32.86 | 2.76 | 813 (2018-01-24 → 2021-05-12) | 0.98 | 1.37 | 0.43 | 26.16 |
| **F1** `01a190e9` | 76.02 | 15.29 | 4.97 | 23.42 | 29.40 | +13.74 | 24.54 | 2.80 | 600 (2018-01-10 → 2020-06-22) | **1.62** | **2.25** | **1.20** | **38.68** |
| **F2** `01a190ea` | 95.69 | 23.93 | 4.07 | 0.07 | 23.29 | +7.63 | 30.36 | 3.16 | 352 (2018-08-31 → 2020-02-06) | 1.19 | 1.62 | 0.77 | 24.33 |
| **F3** `01a190f7` | 74.59 | 19.34 | 4.02 | 10.63 | 22.21 | +6.55 | 27.56 | **2.75** | 636 (2018-01-23 → 2020-08-24) | 1.40 | 1.90 | 0.81 | 29.78 |
| **G1** `01a19104` | 99.25 | 19.97 | 4.97 | 0.07 | **32.37** | +16.71 | 31.74 | 2.94 | 337 (2018-08-31 → 2020-01-17) | 1.46 | 2.03 | 1.02 | 32.62 |
| **G2** `01a19105` | 99.25 | 19.97 | 4.97 | 0.07 | 32.37 | +16.71 | 31.74 | 2.94 | 337 (2018-08-31 → 2020-01-17) | 1.46 | 2.03 | 1.02 | 32.62 |
| **G3** `01a19106` | 76.61 | 19.99 | 3.83 | 0.07 | 17.74 | +2.08 | 28.18 | 2.82 | 660 (2018-01-10 → 2020-09-14) | 1.16 | 1.60 | 0.63 | 23.15 |
| **G4** `01a19107` | 84.02 | 19.97 | 4.21 | 0.07 | 23.75 | +8.09 | **23.86** | 2.86 | 633 (2018-01-10 → 2020-08-06) | 1.32 | 1.81 | 0.99 | 28.26 |

Every longest drawdown recovered in the window. Max-DD episodes (`windows-*.json`, own top 3): F1
2018-01-10 → 2019-05-13; F2 2020-02-19 → 2020-03-24; F3 2018-01-23 → 2019-05-13; G1/G2 2020-02-19 →
2020-03-23; G3 and G4 2018-01-10 → 2020-03-24.

## 2. Trade efficiency and turnover

Whole trades (legs summed). The rotation's R is return on cost; VCP's is stop-based, so R mixes in
the combined runs. Compare on profit factor and % payoff. Fees and cost share are the whole
account.

| Run | Trades | Profit factor | Win % | Avg win % | Avg loss % | Payoff | MFE capture | Max consec losses | CAGR ex top-5 % | Top-5 share % | Fees ₹ | Cost share % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 `01a19039` | 328 | 3.02 | 51.2 | +28.4 | −11.3 | 2.53 | 0.26 | 9 | 19.86 | 38.1 | 86,172 | 2.64 |
| E2 `01a190de` | 342 | 3.34 | 54.7 | +26.2 | −11.3 | 2.32 | 0.27 | 15 | 21.02 | 36.9 | 88,651 | 2.54 |
| E6 `01a190e4` | 371 | 3.13 | 50.9 | +24.4 | −9.3 | 2.62 | 0.28 | 11 | 17.89 | 39.6 | 80,373 | 2.80 |
| C1 `01a19057` | 567 | 2.66 | 42.9 | +25.2 | −7.8 | 3.22 | 0.19 | 12 | 17.42 | 30.8 | 95,308 | 3.91 |
| R5 `01a1909f` | 214 | 2.28 | 30.8 | +20.7 | −4.3 | 4.82 | 0.21 | 12 | 6.49 | 61.7 | 80,570 | 6.31 |
| F1 `01a190e9` | 373 | 3.89 | 55.2 | +24.0 | −9.2 | 2.61 | **0.31** | 10 | 22.09 | 37.5 | 90,242 | 2.38 |
| F2 `01a190ea` | 641 | 2.63 | 44.9 | +20.6 | −7.4 | 2.77 | 0.18 | 15 | 18.34 | 30.5 | 114,421 | 4.36 |
| F3 `01a190f7` | 664 | 2.75 | 44.7 | +19.4 | −6.6 | 2.93 | 0.19 | 12 | 17.39 | 30.7 | 107,807 | 4.42 |
| G1/G2 `01a19104` | 348 | **4.11** | 52.3 | +28.7 | −10.2 | 2.80 | 0.29 | 16 | **25.36** | 34.2 | 94,752 | **2.12** |
| G3 `01a19106` | 343 | 2.67 | 48.4 | +16.5 | −8.2 | 2.02 | 0.11 | 15 | 12.26 | 39.8 | 90,026 | 5.13 |
| G4 `01a19107` | 342 | 3.27 | 50.9 | +22.1 | −9.8 | 2.25 | 0.19 | 18 | 17.13 | 38.9 | 86,507 | 3.23 |

Rotation turnover (`rebalances.csv`, filled orders; VCP orders are not in it):

| Run | Order days | Buys / sales / trims / top-ups | Sales: out / not eligible / filter / funding | Rotation traded ₹L |
| --- | --- | --- | --- | --- |
| E2 `01a190de` | 72 | 342 / 322 / 464 / 389 | 253 / 69 / 0 / 0 | 617.5 |
| F1 `01a190e9` | 64 | 373 / 353 / 300 / 268 | 153 / 40 / 160 / 0 | 650.1 |
| F2 `01a190ea` | 198 | 383 / 363 / 445 / 596 | 207 / 69 / 0 / 87 | 486.6 |
| F3 `01a190f7` | 174 | 406 / 386 / 293 / 440 | 118 / 38 / 157 / 73 | 463.4 |
| G1/G2 `01a19104` | 72 | 348 / 328 / 455 / 380 | 260 / 68 / 0 / 0 | 663.1 |
| G3 `01a19106` | 93 | 343 / 323 / 719 / 584 | 254 / 69 / 0 / 0 | 616.2 |
| G4 `01a19107` | 84 | 342 / 322 / 613 / 496 | 253 / 69 / 0 / 0 | 599.7 |

## 3. Per year: return % / invested % / in-year max DD %

From run.json `by_year` and equity.csv. TRI in-year max DD from `dd-6y-report.md` §3.

| Year | TRI ret (in-yr DD) | E2 `01a190de` | C1 `01a19057` | F1 `01a190e9` | F2 `01a190ea` | F3 `01a190f7` | G1/G2 `01a19104` | G3 `01a19106` | G4 `01a19107` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2016 | +5.12 (13.8) | −8.08 / 99.6 / 20.5 | −2.64 / 80.4 / 17.2 | +0.13 / 74.2 / 18.8 | −7.73 / 96.2 / 20.5 | +0.48 / 70.8 / 17.1 | −7.09 / 99.5 / 19.2 | −0.68 / 75.1 / **12.6** | −10.30 / 83.9 / 17.6 |
| 2017 | +37.65 (4.8) | +80.78 / 99.1 / 7.9 | +66.96 / 94.6 / 6.7 | +60.99 / 90.7 / 7.9 | +67.09 / 94.9 / 6.6 | +52.42 / 88.2 / 6.6 | +74.83 / 99.1 / 7.9 | +41.69 / 84.5 / 8.2 | +66.62 / 92.8 / 7.9 |
| 2018 | −2.14 (15.6) | −11.10 / 99.4 / 22.5 | −10.58 / 80.3 / 20.5 | −17.60 / 49.3 / 21.3 | −11.89 / 95.1 / 21.0 | −20.85 / 51.5 / 25.0 | −10.17 / 99.2 / 23.3 | −18.58 / 66.2 / 21.7 | −16.15 / 69.1 / **21.0** |
| 2019 | +8.97 (11.5) | +14.99 / 99.5 / 13.6 | +7.96 / 76.9 / 10.5 | +13.82 / 58.6 / 7.1 | +10.98 / 96.6 / 13.6 | +8.76 / 58.8 / **6.5** | +15.65 / 99.3 / 11.7 | +6.81 / 74.2 / 11.0 | +9.65 / 72.7 / 8.8 |
| 2020 | +17.89 (38.1) | +37.23 / 99.3 / 34.2 | +25.57 / 84.0 / 27.9 | +64.68 / 83.8 / **9.1** | +34.86 / 96.3 / 30.4 | +46.47 / 82.7 / 10.4 | **+65.87** / 99.3 / 31.7 | +42.08 / 78.6 / 17.5 | +47.40 / 90.9 / 20.5 |
| 2021 | +31.60 (9.8) | +88.57 / 99.1 / 8.1 | +69.74 / 94.4 / 8.1 | +88.65 / 99.0 / 8.1 | +72.76 / 95.1 / 9.2 | +72.59 / 95.1 / 9.2 | **+92.28** / 99.0 / 6.7 | +53.21 / 80.9 / 8.1 | +77.32 / 94.5 / 8.1 |

- 2018 is still the hard year: every run loses more than TRI (−2.14), and the least is G1's −10.17.
- G1 beats TRI in 4 years (2017, 2019, 2020, 2021), as E2 does, and beats E2 in every year but 2017.
- F1 beats TRI in 4 years (2017, 2019, 2020, 2021), and it loses 2016 by only 5 pts against E2's 13.
- G4's 2016 (−10.30) is worse than E2's. It scaled down on 2016-01-21, after most of the January
  fall, and restored at the next rebalance.

## 4. B1's five drawdown episodes: depth in each run

Max drawdown inside B1's peak → recovery window (`dd-6y-report.md` Part B dates), from each run's
own running peak inside the window. Δ is vs B1. In brackets: average invested % in the window, where
it is below ~95.

| # | B1 window | B1 `01a19039` | E2 `01a190de` | C1 `01a19057` | F1 `01a190e9` | F2 `01a190ea` | F3 `01a190f7` | G1/G2 `01a19104` | G3 `01a19106` | G4 `01a19107` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2020-02-19 → 2020-09-14 | 35.34 | 34.19 (−1.15) | 27.87 (−7.47) [80] | **9.07** (−26.27) [71] | 30.36 (−4.98) | 10.36 (−24.98) [72] | 31.74 (−3.60) | 17.53 (−17.81) [75] | 20.47 (−14.87) [84] |
| 2 | 2018-08-31 → 2020-02-12 | 23.36 | 22.61 (−0.75) | **17.76** (−5.60) [77] | 23.49 (+0.13) [60] | 20.83 (−2.53) | 20.42 (−2.94) [60] | 23.33 (−0.03) | 21.69 (−1.67) [70] | 21.28 (−2.08) [75] |
| 3 | 2016-10-25 → 2017-03-16 | 21.71 | 20.28 (−1.43) | 17.19 (−4.52) [84] | 18.81 (−2.90) [55] | 18.33 (−3.38) [94] | 14.09 (−7.62) [55] | 17.82 (−3.89) | **11.60** (−10.11) [66] | 17.58 (−4.13) [73] |
| 4 | 2016-01-01 → 2016-07-27 | 20.06 | 20.49 (+0.43) | 14.27 (−5.79) [76] | 17.15 (−2.91) [71] | 20.49 (+0.43) | 17.15 (−2.91) [70] | 19.22 (−0.84) | **11.26** (−8.80) [79] | 17.59 (−2.47) [83] |
| 5 | 2018-01-23 → 2018-07-11 | 16.62 | 15.42 (−1.20) | 20.50 (+3.88) [82] | **13.70** (−2.92) [40] | 21.02 (+4.40) [94] | 19.58 (+2.96) [45] | 15.11 (−1.51) | 18.50 (+1.88) [62] | 13.77 (−2.85) [60] |

- **Episode 5 (2018-01)** gets worse whenever VCP is in the book: C1 +3.9, F2 +4.4 and F3 +3.0 pts
  vs B1. R5 alone lost 31.69 in this window, at 47% invested. Its breakouts of late 2017 failed together.
- **Episode 2 (the 2018-19 grind)** is still not cut by more than 3 pts by any rotation-only run.
  Only C1's lower rotation weight gets it to 17.8.
- **G4 vs F1:** they are about equal in episodes 3-5. F1 is far better in the 2020 crash (9.1 vs 20.5)
  because it was in cash, not half invested. G4 is better in 2018-19 (21.3 vs 23.5) because
  half-size whipsaws cost less than all-cash ones.

## F. Overlap detail (`overlap.json`, `dd3_overlap.py`)

Rotation funding sales are `rebalances.csv` rows with the reason `rotation_funding`. The VCP sleeve
share is each open VCP trade's shares × the raw close (`bars_daily_raw`, scaled to the trade's
adjusted entry price; a symbol fallback is used where the early bars sit under an older
instrument), over equity. 34 of 1,486 sessions have no mark and are left out of the means.
"Rotation flat" = equity.csv `open_positions` minus the VCP trades open that session is 0.

| | C1 `01a19057` (no overlap, 0.7 + 0.3) | F2 `01a190ea` (E2 1.0 + VCP 0.3) | F3 `01a190f7` (F1 1.0 + VCP 0.3) |
| --- | --- | --- | --- |
| Funding sales (sells + trims) | — | **241** (87 + 154) on 130 days | **205** (73 + 132) on 114 days |
| Funding value | — | **₹72.1L** | **₹58.9L** |
| VCP trades | 239 | 258 | 258 |
| VCP refused: cash (`size_zero_cash` + `size_below_min`) | **315** (136 + 179) | **0** | **0** |
| VCP refused: slots (`max_positions`) | 162 | **428** | **428** |
| VCP refused: other (`size_zero_risk`, `max_chase`) | 10 | 10 | 10 |
| VCP net P&L ₹ | 3.78L | 4.84L | 4.67L |
| VCP sleeve share of equity, avg / when held / days held | 15.2 / 18.5 / 80.5% | **19.2** / 23.3 / 80.6% | **19.3** / 23.4 / 80.6% |
| Rotation share of equity (invested − VCP) | 69.9 | 76.4 | 54.8 |
| Rotation flat days % | 0.1 | 0.1 | **23.4** |
| On rotation-flat days: invested % / VCP share % / days VCP held anything | — | — | **6.3 / 5.4 / 54.6%** |
| Zero-position days % | 0.07 | 0.07 | **10.63** (F1 23.42) |

- Overlap did what it is built to do: no VCP entry was refused for cash. The binding limit moved
  to VCP's slots, with 428 `max_positions` refusals.
- **F3's question: does VCP keep capital working when breadth sends the rotation to cash?
  Mostly no.** On those days the book is 6.3% invested, and on 45% of them it holds nothing at
  all. VCP's 0.3 weight and its few slots cap it at roughly a fifth of the book even when signals
  exist, and in weak breadth the signals are scarce.
- `rotation_funding_fills` (the price-source counts) is computed by the loop
  (`loop.py`, the `self.funder` branch) but is not present in either overlap run's run.json. That
  looks like a reporting gap worth a look; nothing was changed here.

## G. Industry cap and scale-down detail (`levers.json`, `dd3_levers.py`)

**Industry cap (G1, G2).** The cap binds: B1 held up to **12** names in one known industry
(2016-11-01) and E2 up to 11 (2017-06-01). G1 never holds more than 4. Unknown industry (a blank
`industry` in trades.csv):

| Run | Unknown-industry trades / all | Their net P&L ₹ | Most unknown names held at once |
| --- | --- | --- | --- |
| B1 `01a19039` | 14 / 328 | −53.5k | 2 |
| E2 `01a190de` | 14 / 342 | −74.0k | 3 |
| G1 `01a19104` (free) | 16 / 348 | −47.6k | 3 |
| G2 `01a19105` (bucket) | 16 / 348 | −47.6k | 3 |

- **Survivorship caveat** (`docs/decisions.md`): before ~2021 an unknown industry marks mostly names
  that later left the index. Of the 122 NIFTY 500 members without one at 2016-12-31, none is a member
  today; 225 of the 379 known are. Unknowns were 24% of members in 2016, falling to 9% in 2021.
  - `free` lets the cap miss concentration among them.
  - `bucket` tilts selection towards survivors, a look-ahead in effect.
- **In these runs the bias is small and runs against G1, not for it.** Only 14-16 trades (4-5%) had
  an unknown industry, those trades lost money in every run, and at most 3 were held at once. With
  a cap of 4 the bucket never filled, so G2 = G1 exactly. A tighter cap (≤3) would make the choice
  matter.

**Scale-down (G3, G4).** Trims are `rebalances.csv` rows with the reason `rotation_scale_down`.
Their cost is the trim legs' fees plus the top-ups that restore the book at the next rebalance.

| Run | Trim days (fires) | Trim orders | Value trimmed | Trim-leg fees ₹ | Trim-leg net P&L ₹ | Top-ups vs E2 | CAGR vs E2 | Max DD vs E2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G3 `01a19106` (SMA50) | **21** | 415 | ₹136.3L | 37,529 | +6.38L | 584 vs 389 (+195) | −10.24 | −6.01 |
| G4 `01a19107` (breadth 30) | **12** | 239 | ₹91.2L | 24,033 | +6.55L | 496 vs 389 (+107) | −4.23 | **−10.33** |

- G4's trim days: 2016-01-21, 2016-11-18, 2017-08-16, 2018-02-07, 2018-05-21, 2018-09-26,
  2019-01-28, 2019-05-09, 2019-06-18, **2020-02-28** (7 sessions after the 2020-02-19 peak), 2021-08-27
  and 2021-12-03.
- G3 trimmed on 9 more days, 2017 among them (4 trims in a +38% TRI year), and its 2017 return of
  +41.69 shows the whipsaw cost.
- The trim legs themselves sold at a profit (+₹6.4-6.6L). The cost is the half-size book on the
  rebound and the fees: total cost share is 3.23% for G4 and 5.13% for G3, against E2's 2.54%.

## H. The stacks (H1, H3, H2) and the ranking of all candidates

Three runs on m3 at main `a672820`, one at a time, same window and rules. Scripts and outputs are as
above, in `stats-h.json`, `windows-h.json` and `levers-h.json`.

| Run | Change | Run ID |
| --- | --- | --- |
| **H1** | E2 + G1 + G4: `vol_sessions=63`, `max_per_industry=4`, `scale_down` breadth ≥30 smooth 5, keep 0.5 | `01a1910c-f66f-75f4-9a0e-b884675a6a23` |
| **H3** | H1 with `keep_fraction` 0.75 | `01a1910e-1402-731f-b837-966b54bcc954` |
| **H2** | F1 + G1: E2 + breadth `market_filter` + `max_per_industry=4` (reference only: idle cash) | `01a1910f-2828-7407-8ebb-7e1f6cf10f55` |

### H.1 Deployment and headline

| Run | Invested % | Avg positions | Avg size % | Zero-pos days % | CAGR % | vs TRI | Max DD % | Avg DD % | Longest DD (sessions) | Sharpe | Sortino | Calmar | CAGR per invested |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E2 `01a190de` | 99.31 | 19.97 | 4.97 | 0.07 | 27.98 | +12.32 | 34.19 | 3.12 | 352 (2018-08-31 → 2020-02-06) | 1.28 | 1.75 | 0.82 | 28.18 |
| G1 `01a19104` | 99.25 | 19.97 | 4.97 | 0.07 | 32.37 | +16.71 | 31.74 | 2.94 | 337 (2018-08-31 → 2020-01-17) | 1.46 | 2.03 | 1.02 | 32.62 |
| G4 `01a19107` | 84.02 | 19.97 | 4.21 | 0.07 | 23.75 | +8.09 | 23.86 | 2.86 | 633 (2018-01-10 → 2020-08-06) | 1.32 | 1.81 | 0.99 | 28.26 |
| F1 `01a190e9` | 76.02 | 15.29 | 4.97 | 23.42 | 29.40 | +13.74 | 24.54 | 2.80 | 600 (2018-01-10 → 2020-06-22) | 1.62 | 2.25 | 1.20 | 38.68 |
| **H1** `01a1910c` | 84.01 | 19.96 | 4.21 | 0.07 | 26.83 | +11.17 | **22.48** | **2.71** | 601 (2018-01-10 → 2020-06-23) | 1.48 | 2.06 | 1.19 | 31.93 |
| **H3** `01a1910e` | **91.62** | 19.96 | 4.59 | 0.07 | **29.55** | +13.89 | 25.26 | 3.03 | 350 (2018-08-31 → 2020-02-04) | 1.49 | 2.07 | 1.17 | 32.25 |
| **H2** `01a1910f` | 75.98 | 15.29 | 4.97 | 23.42 | 28.38 | +12.72 | 27.56 | 2.85 | 629 (2018-01-10 → 2020-07-31) | 1.60 | 2.24 | 1.03 | 37.35 |

Max-DD episodes: H1 2018-01-10 → 2019-08-05; H3 2020-02-19 → 2020-03-23; H2 2018-01-10 →
2019-05-13 (`windows-h.json`). Every longest drawdown recovered in the window.

### H.2 Trade efficiency and turnover

| Run | Trades | Profit factor | Win % | Avg win % | Avg loss % | Payoff | MFE capture | Max consec losses | CAGR ex top-5 % | Top-5 share % | Fees ₹ | Cost share % | Rotation traded ₹L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 `01a1910c` | 347 | 3.81 | 47.8 | +24.6 | −9.0 | 2.74 | 0.20 | 18 | 20.26 | 36.0 | 89,473 | 2.75 | 623.8 |
| H3 `01a1910e` | 347 | 3.99 | 50.7 | +26.2 | −9.7 | 2.71 | 0.24 | 17 | 22.77 | 35.0 | 92,808 | 2.43 | 637.2 |
| H2 `01a1910f` | 384 | 3.76 | 53.1 | +24.4 | −9.3 | 2.62 | 0.31 | 11 | 21.58 | 35.9 | 85,725 | 2.41 | 611.7 |

**Scale-down trims and their cost** (`levers-h.json`). H1 and H3 fired on the same 12 closes as G4.
The industry cap does not change the breadth reading: 2016-01-21, 2016-11-18, 2017-08-16,
2018-02-07, 2018-05-21, 2018-09-26, 2019-01-28, 2019-05-09, 2019-06-18, 2020-02-28, 2021-08-27
and 2021-12-03.

| Run | Trim days | Trim orders | Value trimmed | Trim-leg fees ₹ | Trim-leg net P&L ₹ | Top-ups vs G1 (no scale-down) | CAGR vs G1 | Max DD vs G1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 `01a1910c` (keep 0.5) | 12 | 239 | ₹94.3L | 24,542 | +8.01L | 494 vs 380 (+114) | −5.54 | −9.26 |
| H3 `01a1910e` (keep 0.75) | 12 | 236 | ₹50.6L | 14,949 | +5.27L | 490 vs 380 (+110) | −2.82 | −6.48 |

Industry cap in all three: at most 4 names in one known industry and at most 3 unknown names held
at once. Unknown-industry trades: H1 16 of 347 (−₹38.4k), H3 16 of 347 (−₹42.5k), H2 18 of 384
(−₹27.6k). The §G survivorship caveat applies unchanged.

### H.3 Per year: return % / invested % / in-year max DD %

| Year | TRI ret (in-yr DD) | G1 `01a19104` | G4 `01a19107` | F1 `01a190e9` | H1 `01a1910c` | H3 `01a1910e` | H2 `01a1910f` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2016 | +5.12 (13.8) | −7.09 / 99.5 / 19.2 | −10.30 / 83.9 / 17.6 | +0.13 / 74.2 / 18.8 | −10.65 / 83.4 / 17.2 | −8.86 / 91.3 / 18.1 | −0.72 / 74.1 / 17.2 |
| 2017 | +37.65 (4.8) | +74.83 / 99.1 / 7.9 | +66.62 / 92.8 / 7.9 | +60.99 / 90.7 / 7.9 | +60.93 / 92.6 / 7.9 | +67.36 / 95.6 / 7.9 | +54.60 / 90.6 / 7.9 |
| 2018 | −2.14 (15.6) | −10.17 / 99.2 / 23.3 | −16.15 / 69.1 / 21.0 | −17.60 / 49.3 / 21.3 | −15.25 / 69.0 / **20.8** | −12.83 / 84.4 / 21.1 | −20.69 / 49.3 / 24.7 |
| 2019 | +8.97 (11.5) | +15.65 / 99.3 / 11.7 | +9.65 / 72.7 / 8.8 | +13.82 / 58.6 / 7.1 | +9.69 / 72.9 / 7.6 | +12.58 / 86.6 / 9.6 | +9.40 / 58.4 / **5.7** |
| 2020 | +17.89 (38.1) | +65.87 / 99.3 / 31.7 | +47.40 / 90.9 / 20.5 | +64.68 / 83.8 / 9.1 | +72.17 / 91.3 / 18.9 | +69.31 / 94.9 / 25.3 | **+74.85** / 83.9 / **8.2** |
| 2021 | +31.60 (9.8) | +92.28 / 99.0 / 6.7 | +77.32 / 94.5 / 8.1 | +88.65 / 99.0 / 8.1 | +80.93 / 94.4 / 6.7 | +86.55 / 96.8 / 6.7 | +92.34 / 99.0 / 6.7 |

H1 and H3 beat TRI in 4 years (2017, 2019, 2020, 2021), as G1 does, and they miss 2016 and 2018.

### H.4 B1's five drawdown episodes

Same method as §4. Δ is vs B1. In brackets: average invested % in the window.

| # | B1 window | B1 `01a19039` | G1 `01a19104` | G4 `01a19107` | F1 `01a190e9` | H1 `01a1910c` | H3 `01a1910e` | H2 `01a1910f` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2020-02-19 → 2020-09-14 | 35.34 | 31.74 (−3.60) | 20.47 (−14.87) [84] | 9.07 (−26.27) [71] | 18.94 (−16.40) [85] | 25.26 (−10.08) [91] | **7.20** (−28.14) [72] |
| 2 | 2018-08-31 → 2020-02-12 | 23.36 | 23.33 (−0.03) | 21.28 (−2.08) [75] | 23.49 (+0.13) [60] | **20.89** (−2.47) [75] | 21.11 (−2.25) [88] | 23.60 (+0.24) [60] |
| 3 | 2016-10-25 → 2017-03-16 | 21.71 | 17.82 (−3.89) | 17.58 (−4.13) [73] | 18.81 (−2.90) [55] | **15.60** (−6.11) [72] | 16.70 (−5.01) [85] | 16.48 (−5.23) [55] |
| 4 | 2016-01-01 → 2016-07-27 | 20.06 | 19.22 (−0.84) | 17.59 (−2.47) [83] | **17.15** (−2.91) [71] | 17.22 (−2.84) [83] | 18.06 (−2.00) [91] | 17.22 (−2.84) [71] |
| 5 | 2018-01-23 → 2018-07-11 | 16.62 | 15.11 (−1.51) | 13.77 (−2.85) [60] | 13.70 (−2.92) [40] | **13.49** (−3.13) [60] | 14.26 (−2.36) [80] | 13.53 (−3.09) [40] |

- **H1 is shallower than B1 in all five episodes** and is the shallowest run in this table in episodes 2, 3 and 5 (C1 and G3 go lower in 2 and 3; §4).
  The cap and the scale-down add up in episode 3 (2016-Q4, half financials): G1 −3.89, G4 −4.13,
  H1 −6.11.
- H3 gives back about a third of H1's 2020 cut (25.26 vs 18.94) for 7.6 pts more invested. Elsewhere it is within 1.1 pts of H1.
- H2 vs F1: the cap cuts 2020 and 2016-Q4 further, but 2018 is worse (−20.69 vs −17.60) and max DD
  rises 24.54 → 27.56. The cap does not stack with the all-cash gate here.

### H.5 Ranking of all in-sample candidates

Ordered by deployment first (zero-position days, then invested %), then CAGR, max DD and Calmar.
Three deployment tiers.

| Rank | Run | Invested % | Zero-pos days % | CAGR % | Max DD % | Calmar | Reading |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Tier A: fully invested (≥95%)** | | | | | | | |
| 1 | **G1** `01a19104` | 99.25 | 0.07 | **32.37** | 31.74 | 1.02 | Best CAGR of any run; the DD cut is modest |
| 2 | E2 `01a190de` | 99.31 | 0.07 | 27.98 | 34.19 | 0.82 | Dominated by G1 |
| 3 | B1 `01a19039` | 99.38 | 0.07 | 26.88 | 35.34 | 0.76 | Dominated by E2 and G1 |
| 4 | F2 `01a190ea` | 95.69 | 0.07 | 23.29 | 30.36 | 0.77 | Overlap with VCP: lower DD than E2, but −4.7 CAGR |
| **Tier B: partial, never flat (84-92%)** | | | | | | | |
| 5 | **H3** `01a1910e` | **91.62** | 0.07 | **29.55** | 25.26 | 1.17 | Best balance: −8.9 max DD vs E2 with higher CAGR |
| 6 | C1 `01a19057` | 85.12 | 0.07 | 22.29 | 27.87 | 0.80 | Dominated by H1/H3 except 1 pt of invested |
| 7 | **H1** `01a1910c` | 84.01 | 0.07 | 26.83 | **22.48** | 1.19 | Lowest max DD of any run |
| 8 | G4 `01a19107` | 84.02 | 0.07 | 23.75 | 23.86 | 0.99 | Dominated by H1 (same exposure; the cap adds +3.1 CAGR) |
| **Tier C: idle cash (23.4% zero-position days)** | | | | | | | |
| 9 | F1 `01a190e9` | 76.02 | 23.42 | 29.40 | 24.54 | **1.20** | Best Calmar and Sharpe (1.62), but fails the idle-cash rule |
| 10 | H2 `01a1910f` | 75.98 | 23.42 | 28.38 | 27.56 | 1.03 | Dominated by F1; reference only |

**Verdict.**
- **H3 is the recommended in-sample candidate** (`01a1910e`). It is 91.6% invested and never flat,
  with CAGR 29.55 (+1.57 vs E2, −2.82 vs G1), max DD 25.26 (−8.93 vs E2, −10.08 vs B1), Calmar 1.17,
  Sharpe 1.49, Sortino 2.07. It is shallower than B1 in every one of the five episodes.
- **If the owner rule is strictly "fully invested" (≥95%), G1 is the pick** (`01a19104`): the highest
  CAGR, 32.37, but max DD 31.74.
- **If drawdown is the priority within "never flat", H1 is the pick** (`01a1910c`): max DD 22.48
  and Calmar 1.19 at 84% invested, CAGR 26.83.
- Not recommended: F1 and H2 (idle cash), C1 and F2 (dominated, and VCP deepens 2018-01), G4 (dominated by H1).
- The choice between H1, H3 and G1 is one knob, `keep_fraction` (0.5 / 0.75 / off), on the same
  E2 + industry-cap base. The next step is the owner's: pick the keep fraction, then a hold-out
  read of that one config.

Rules kept: venv python on m3, `PGOPTIONS default_transaction_read_only=on` for the runs, one run at
a time with the ≥2.5 GB check (6.8-7.0 GB available at each start), m3 pulled only after F3
finished, no `.env` access, no commits, no engine change, nothing on m1, no hold-out.
