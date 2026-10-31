# Hold-out read 2021-2025: the frozen top 5 (H3, G1, H1, F1, E2)

Owner-approved hold-out read (owner 2026-10-31). The five configs frozen in `plans/top5-frozen.md`
were each run once on 2021-01-01 to 2025-12-31 (both years included, normal warm-up), on m3 at main
`a6728207345ea86e1f5dfc626fbc1991f8bc058a` (`a672820`, clean tree). The runs were one at a time,
with 6.9-7.1 GB available at each start, in the frozen order H3, G1, H1, F1, E2. No tuning and no
reruns. NIFTY500_PIT, stocks only, no ETF overlay, ₹10L, database read-only. Short IDs are the first
8 characters of the run ID.

| Run | Config (unchanged from in-sample) | In-sample run (2016-2021) | Hold-out run (2021-2025) |
| --- | --- | --- | --- |
| **H3** | `vol_sessions=63`, `max_per_industry=4`, `scale_down` breadth ≥30 smooth 5, keep 0.75 | `01a1910e` | `01a19114-b1c7-74d3-95af-3b0aa49405ce` |
| **G1** | `vol_sessions=63`, `max_per_industry=4` | `01a19104` | `01a19115-f6a3-736d-82dd-3f711a851d85` |
| **H1** | as H3 with keep 0.5 | `01a1910c` | `01a19117-47ba-75b2-8d73-1d0a032e39aa` |
| **F1** | `vol_sessions=63` + breadth `market_filter` (all-cash gate) | `01a190e9` | `01a19118-8eac-726f-a47a-8143bc39d184` |
| **E2** | `vol_sessions=63` (plain rotation reference) | `01a190de` | `01a19119-b973-77b3-ae02-5d474722a98e` |

**Freeze and data.** All files are on m3 in `/data/workspace/backtests/oos-2125/`.
- **Freeze.** Each portfolio file is its in-sample file with only the `window` line changed (checked
  by `diff`: one line each). The files are made read-only. `FROZEN.txt` records the sha256 of each
  source and frozen file, the commit and the in-sample commits. It was written before the first
  run, and its own sha256 is `a7938334…5dcc`.
- **Data coverage.** Checked before any run with `coverage.py` → `coverage.txt`. NIFTY 500 and
  NIFTY 500 TRI index closes, `breadth_daily` and EQ daily bars are present for every NIFTY 500
  session 2020-2025: 0 missing, data to 2026-10-29. The NIFTY 500 membership record covers
  2016-01-01 → 2026-10-30, with 500-501 members at every check date through 2025-12-31.
- **Runs.** All five completed with audit `warn`, as did every in-sample run.

**Scripts and outputs.**
- `oos_stats.py` → `stats.json`. Every metric uses the engine's `standard.book_metrics`. The full
  window equals run.json on every metric checked. 2022-2025 is the same computation on the
  2022-01-03 → 2025-12-31 sessions, starting from the 2021-12-31 close, with the trades entered in
  that span.
- `oos_episodes.py` → `episodes.json` (drawdown episodes).
- `dd3-6y/dd3_levers.py` → `levers.json` (scale-down trims, industry counts).

**TRI.** NIFTY 500 TRI CAGR is **16.88%** for 2021-2025 (run.json `benchmark_cagr_pct`) and
**13.46%** for 2022-2025 (equity.csv `benchmark_tri`, from the 2021-12-31 close). TRI max DD is
18.59% in both.

**2021 overlaps the in-sample window** (2016-2021), so it is not unseen. It is shown, and every
headline is also given for **2022-2025**. Per `top5-frozen.md`, the base rotation (G3 p5, with
ETF overlay) was run on 2016-2024 earlier, so 2022-2024 is not fully unseen for the base. 2025 is
fresh for all five.

## Verdict

- **Deployment held exactly.** Invested %, positions, size and zero-position days match
  in-sample for every config:
  - H3: 92.2% vs 91.6% in-sample.
  - H1: 85.0% vs 84.0%.
  - G1 and E2: 99.2%.
  - F1: 78.2% invested with **21.2%** zero-position days (in-sample 23.4%). In 2025 F1 had zero
    positions on 41% of days.
- **The return edge did not hold after 2021.** Over 2021-2025 every config beats TRI (CAGR 20.5-26.0
  vs 16.88), but 2021 alone returned +78 to +89%. Over **2022-2025, only E2 beats TRI** (14.64 vs
  13.46, +1.18). G1 is level (−0.29), and H3 (−2.03), F1 (−3.61) and H1 (−4.10) trail it. Sharpe is
  0.57-0.72 and Calmar 0.33-0.41 for all five. Profit factor fell from 3.3-4.1 in-sample to **1.5**,
  and CAGR excluding the top 5 trades to **2.5-6.3%**: outside a handful of winners there is
  little left.
- **The drawdown levers still cut drawdown relative to E2, but they cost more return than they
  saved, and the in-sample ranking inverted.**
  - Max DD over 2021-2025: H1 25.79, H3 28.89, F1 29.52, G1 33.43, E2 35.61. This is nearly the
    in-sample order; only H3 and F1 swap.
  - All five are far deeper than TRI's 18.59.
  - 2022-2025 CAGR runs the opposite way: E2 14.64 > G1 13.17 > H3 11.43 > F1 9.85 > H1 9.36.
  - The industry cap's in-sample gain (+4.4 CAGR, −2.5 max DD) shrank to −0.55 CAGR and −2.18
    max DD.
- **2025 is the worst year for every config, and it is the one fully fresh year:** −15.9 to −20.6%
  against TRI's +7.76%. Every run is in a drawdown that has not recovered by 2025-12-31, from a
  2024-10-15/16 peak to a 2025-04-07 trough: E2 35.61, G1 33.43, H3 28.89, F1 26.16, H1 23.95,
  against TRI's −14.8% over the same dates.
  - The breadth scale-down fired on 2024-10-25 and 2025-01-14. Against G1, the same config
    without it, keep 0.75 took 4.5 pts off the depth and keep 0.5 took 9.5.
  - F1's all-cash gate sold on 2025-02-01, after most of the fall.
- **Degradation, in-sample → 2022-2025:**

| Run | CAGR | Excess over TRI | Max DD | Calmar | Sharpe | Profit factor |
| --- | --- | --- | --- | --- | --- | --- |
| H3 | 29.55 → 11.43 | +13.89 → −2.03 | 25.26 → 28.89 | 1.17 → 0.40 | 1.49 → 0.64 | 3.99 → 1.47 |
| G1 | 32.37 → 13.17 | +16.71 → −0.29 | 31.74 → 33.43 | 1.02 → 0.39 | 1.46 → 0.67 | 4.11 → 1.47 |
| H1 | 26.83 → 9.36 | +11.17 → −4.10 | 22.48 → 25.79 | 1.19 → 0.36 | 1.48 → 0.58 | 3.81 → 1.46 |
| F1 | 29.40 → 9.85 | +13.74 → −3.61 | 24.54 → 29.52 | 1.20 → 0.33 | 1.62 → 0.57 | 3.89 → 1.48 |
| E2 | 27.98 → 14.64 | +12.32 → +1.18 | 34.19 → 35.61 | 0.82 → 0.41 | 1.28 → 0.72 | 3.34 → 1.51 |

- **Reading.** None of the five passes a hold-out on 2022-2025. They all roughly match TRI on
  return, with 1.4-1.9× its drawdown.
  - Every lever added on top of E2 (the industry cap, the scale-downs, the all-cash gate) lost
    more CAGR than E2 did (17.5-19.6 pts vs 13.3). Their in-sample edge was largely fit to
    2016-2021, notably 2020.
  - The drawdown ordering is the one in-sample result that survived: lower keep fractions do cut
    depth. But in 2022-2025 the return they cost exceeds the drawdown they save.
  - On this evidence I would not take any of the five live as-is. That decision is the owner's.

## 1. Deployment and headline (lead table)

### 2021-2025 (2021 overlaps in-sample)

TRI CAGR 16.88, TRI max DD 18.59.

| Run | Invested % | Avg positions | Avg size % | Zero-pos days % | CAGR % | vs TRI | Max DD % | Avg DD % | Longest DD (sessions) | Sharpe | Sortino | Calmar | CAGR per invested |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H3 `01a19114` | 92.19 | 19.98 | 4.61 | 0.08 | 23.10 | +6.22 | 28.89 | 3.34 | 303 (2022-04-11 → 2023-07-03) | 1.14 | 1.51 | 0.80 | 25.06 |
| G1 `01a19115` | 99.20 | 19.98 | 4.96 | 0.08 | 25.43 | +8.55 | 33.43 | 3.65 | 300 (2024-10-16 → 2025-12-31, open) | 1.16 | 1.54 | 0.76 | 25.64 |
| H1 `01a19117` | 85.01 | 19.98 | 4.25 | 0.08 | 20.51 | +3.63 | **25.79** | 3.34 | 309 (2022-04-11 → 2023-07-11) | 1.09 | 1.44 | 0.80 | 24.13 |
| F1 `01a19118` | 78.19 | 15.76 | 4.96 | **21.21** | 21.76 | +4.88 | 29.52 | 3.39 | 380 (2022-01-14 → 2023-07-28) | 1.08 | 1.42 | 0.74 | 27.83 |
| E2 `01a19119` | 99.22 | 19.98 | 4.96 | 0.08 | **25.98** | +9.10 | 35.61 | 3.36 | 301 (2024-10-15 → 2025-12-31, open) | 1.16 | 1.54 | 0.73 | 26.19 |

### 2022-2025 (no overlap)

TRI CAGR 13.46, TRI max DD 18.59.

| Run | Invested % | Avg positions | Avg size % | Zero-pos days % | CAGR % | vs TRI | Max DD % | Avg DD % | Longest DD (sessions) | Sharpe | Sortino | Calmar | CAGR per invested |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H3 `01a19114` | 91.04 | 19.98 | 4.56 | 0.10 | 11.43 | −2.03 | 28.89 | 4.34 | 303 (2022-04-11 → 2023-07-03) | 0.64 | 0.83 | 0.40 | 12.55 |
| G1 `01a19115` | 99.20 | 19.98 | 4.97 | 0.10 | 13.17 | −0.29 | 33.43 | 4.82 | 300 (2024-10-16 → 2025-12-31, open) | 0.67 | 0.88 | 0.39 | 13.27 |
| H1 `01a19117` | 82.68 | 19.98 | 4.14 | 0.10 | 9.36 | −4.10 | **25.79** | 4.49 | 309 (2022-04-11 → 2023-07-11) | 0.58 | 0.74 | 0.36 | 11.32 |
| F1 `01a19118` | 72.93 | 14.70 | 4.96 | **26.51** | 9.85 | −3.61 | 29.52 | 4.38 | 380 (2022-01-14 → 2023-07-28) | 0.57 | 0.73 | 0.33 | 13.50 |
| E2 `01a19119` | 99.21 | 19.98 | 4.97 | 0.10 | **14.64** | **+1.18** | 35.61 | 4.11 | 301 (2024-10-15 → 2025-12-31, open) | **0.72** | **0.94** | **0.41** | 14.76 |

**Deepest drawdowns** (`episodes.json`; TRI = its move over the same peak → trough):

| Run | 1st: peak → trough (recovery) | Depth | TRI | 2nd | Depth | TRI |
| --- | --- | --- | --- | --- | --- | --- |
| H3 `01a19114` | 2024-10-16 → 2025-04-07 (open) | 28.89 | −14.79 | 2022-04-11 → 2022-06-20 (2023-07-03) | 28.01 | −15.15 |
| G1 `01a19115` | 2024-10-16 → 2025-04-07 (open) | 33.43 | −14.79 | 2022-04-11 → 2022-06-20 (2023-06-20) | 30.47 | −15.15 |
| H1 `01a19117` | 2022-04-11 → 2022-06-20 (2023-07-11) | 25.79 | −15.15 | 2024-10-16 → 2025-04-07 (open) | 23.95 | −14.79 |
| F1 `01a19118` | 2022-01-14 → 2022-05-25 (2023-07-28) | 29.52 | −13.28 | 2024-10-15 → 2025-01-28 (open) | 26.16 | −11.68 |
| E2 `01a19119` | 2024-10-15 → 2025-04-07 (open) | 35.61 | −15.01 | 2022-04-11 → 2022-06-20 (2023-06-16) | 30.31 | −15.15 |

Every config fell 1.7-2.4× as far as TRI in both the 2022 and the 2024-25 corrections. All
were about 99% invested at both peaks: the breadth checks fired only after the falls had started.

## 2. Trade efficiency and fees

Whole trades (legs summed). The rotation's R is return on cost; compare on profit factor and %
payoff. Fees and cost share are for the slice.

### 2021-2025

| Run | Trades | Profit factor | Win % | Avg win % | Avg loss % | Payoff | MFE capture | Max consec losses | CAGR ex top-5 % | Top-5 share % | Fees ₹ | Cost share % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H3 `01a19114` | 337 | 1.80 | 47.5 | +23.6 | −10.1 | 2.34 | 0.18 | 10 | 16.74 | 36.1 | 104,689 | 5.42 |
| G1 `01a19115` | 337 | 1.80 | 47.2 | +27.3 | −10.3 | 2.65 | 0.23 | 15 | 18.75 | 35.3 | 109,945 | 4.96 |
| H1 `01a19117` | 337 | 1.78 | 46.0 | +21.0 | −9.7 | 2.18 | 0.14 | 10 | 14.40 | 37.7 | 99,027 | 6.04 |
| F1 `01a19118` | 349 | 1.78 | 48.1 | +24.1 | −10.2 | 2.35 | 0.23 | 17 | 15.73 | 35.8 | 95,377 | 5.38 |
| E2 `01a19119` | 336 | 1.78 | 47.6 | +28.5 | −11.3 | 2.53 | 0.23 | 13 | 18.50 | 38.5 | 108,482 | 4.75 |

### 2022-2025

| Run | Trades | Profit factor | Win % | Avg win % | Avg loss % | Payoff | MFE capture | Max consec losses | CAGR ex top-5 % | Top-5 share % | Fees ₹ | Cost share % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H3 `01a19114` | 266 | 1.47 | 45.1 | +20.6 | −10.5 | 1.96 | 0.14 | 10 | 4.36 | 65.8 | 87,671 | 8.14 |
| G1 `01a19115` | 266 | 1.47 | 44.7 | +23.2 | −10.8 | 2.16 | 0.18 | 15 | 5.91 | 62.5 | 94,590 | 7.57 |
| H1 `01a19117` | 266 | 1.46 | 44.0 | +18.7 | −10.0 | 1.86 | 0.10 | 10 | 2.47 | 71.4 | 80,458 | 8.99 |
| F1 `01a19118` | 275 | 1.48 | 46.2 | +20.8 | −10.6 | 1.96 | 0.17 | 17 | 3.09 | 64.2 | 80,405 | 7.92 |
| E2 `01a19119` | 262 | 1.51 | 45.8 | +25.4 | −12.0 | 2.13 | 0.19 | 13 | 6.29 | 62.1 | 92,801 | 6.51 |

- In 2022-2025 the top 5 trades are 62-71% of the P&L (in-sample 34-38%).
- The scale-down trims cost the most here. H3 and H1 trimmed on the same 10 days
  (2021-08-27, 2021-12-03, 2022-02-21, 2022-05-12, 2023-01-31, 2024-03-14, 2024-10-25,
  2025-01-14, 2025-08-11 and 2025-11-25): 199 orders each.
  - H3 trimmed ₹55.2L, with trim-leg fees ₹14.9k.
  - H1 trimmed ₹103.3L, with fees ₹25.6k.
- F1's filter sold the book on 8 days (2022-03-02, 2022-06-01, 2023-02-01, 2024-04-01, 2024-11-01,
  2025-02-01, 2025-09-01 and 2025-12-01).
- Rotation traded value (`rebalances.csv`): H3 ₹802.8L, G1 ₹858.6L, H1 ₹761.8L, F1 ₹774.8L, E2
  ₹844.3L.
- **Industry cap.** It binds: E2 held up to **12** names in one industry (2025-12-01), F1 up to 9,
  and the capped runs 4. The unknown-industry survivorship caveat (`docs/decisions.md`) is
  immaterial here: 1 unknown-industry trade in each run, never more than 1 held.

## 3. Per year: return % / invested % / in-year max DD % (zero-position days %)

From run.json `by_year` and equity.csv. TRI in-year max DD from equity.csv `benchmark_tri`.

| Year | TRI ret (in-yr DD) | H3 `01a19114` | G1 `01a19115` | H1 `01a19117` | F1 `01a19118` | E2 `01a19119` |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 *(overlaps in-sample)* | +31.60 (9.8) | +83.47 / 96.8 / 6.7 | +89.40 / 99.2 / 6.7 | +77.78 / 94.4 / 6.7 | +83.87 / 99.2 / 8.1 | +83.87 / 99.2 / 8.1 |
| 2022 | +4.25 (17.4) | −1.28 / 91.1 / 28.0 | +2.81 / 99.4 / 30.5 | −5.97 / 82.6 / 25.8 | −10.59 / 73.7 / 29.5 (25.8) | +2.16 / 99.5 / 30.3 |
| 2023 | +26.91 (8.6) | +54.64 / 93.3 / 12.6 | +57.25 / 99.3 / 13.9 | +51.75 / 87.3 / 11.3 | +54.83 / 76.0 / 9.0 (23.6) | **+62.17** / 99.3 / 13.7 |
| 2024 | +16.24 (10.8) | +23.40 / 93.6 / 14.1 | +27.76 / 99.1 / 14.2 | +19.13 / 88.3 / 15.7 | +27.85 / 83.5 / 14.7 (15.7) | **+29.01** / 99.1 / 14.9 |
| 2025 | +7.76 (12.7) | −18.22 / 86.1 / 25.5 | −20.64 / 99.1 / 30.0 | **−15.91** / 72.5 / 20.7 | −17.77 / 58.6 / 23.2 (**41.0**) | −19.25 / 98.9 / 31.8 |

Zero-position days are 0-0.4% in every year for H3, G1, H1 and E2.

- **2022-2025 against TRI, year by year:**
  - All five beat TRI in 2023 and 2024.
  - All five lose to TRI in 2025, by 24-28 pts.
  - In 2022, G1 and E2 lose to TRI by 1.4-2.1 pts; H3, H1 and F1 lose by 5.5-14.8 pts.
- **In-year drawdowns** are 1.5-2.5× TRI's in 2022 and 2025 for every config. The scale-down
  trims them by 2-11 pts vs E2.

## 4. In-sample vs hold-out (degradation), each config

In-sample = 2016-2021 (`dd3-6y-report.md`, TRI 15.66). Hold-out = 2021-2025 (TRI 16.88) and
2022-2025 (TRI 13.46). Each cell reads in-sample / 2021-2025 / 2022-2025.

| Metric | H3 | G1 | H1 | F1 | E2 |
| --- | --- | --- | --- | --- | --- |
| Run IDs | `01a1910e` / `01a19114` | `01a19104` / `01a19115` | `01a1910c` / `01a19117` | `01a190e9` / `01a19118` | `01a190de` / `01a19119` |
| Invested % | 91.6 / 92.2 / 91.0 | 99.3 / 99.2 / 99.2 | 84.0 / 85.0 / 82.7 | 76.0 / 78.2 / 72.9 | 99.3 / 99.2 / 99.2 |
| Zero-pos days % | 0.07 / 0.08 / 0.10 | 0.07 / 0.08 / 0.10 | 0.07 / 0.08 / 0.10 | 23.4 / 21.2 / 26.5 | 0.07 / 0.08 / 0.10 |
| CAGR % | 29.55 / 23.10 / 11.43 | 32.37 / 25.43 / 13.17 | 26.83 / 20.51 / 9.36 | 29.40 / 21.76 / 9.85 | 27.98 / 25.98 / 14.64 |
| Excess over TRI | +13.89 / +6.22 / −2.03 | +16.71 / +8.55 / −0.29 | +11.17 / +3.63 / −4.10 | +13.74 / +4.88 / −3.61 | +12.32 / +9.10 / +1.18 |
| Max DD % | 25.26 / 28.89 / 28.89 | 31.74 / 33.43 / 33.43 | 22.48 / 25.79 / 25.79 | 24.54 / 29.52 / 29.52 | 34.19 / 35.61 / 35.61 |
| Avg DD % | 3.03 / 3.34 / 4.34 | 2.94 / 3.65 / 4.82 | 2.71 / 3.34 / 4.49 | 2.80 / 3.39 / 4.38 | 3.12 / 3.36 / 4.11 |
| Calmar | 1.17 / 0.80 / 0.40 | 1.02 / 0.76 / 0.39 | 1.19 / 0.80 / 0.36 | 1.20 / 0.74 / 0.33 | 0.82 / 0.73 / 0.41 |
| Sharpe | 1.49 / 1.14 / 0.64 | 1.46 / 1.16 / 0.67 | 1.48 / 1.09 / 0.58 | 1.62 / 1.08 / 0.57 | 1.28 / 1.16 / 0.72 |
| Sortino | 2.07 / 1.51 / 0.83 | 2.03 / 1.54 / 0.88 | 2.06 / 1.44 / 0.74 | 2.25 / 1.42 / 0.73 | 1.75 / 1.54 / 0.94 |
| CAGR per invested | 32.25 / 25.06 / 12.55 | 32.62 / 25.64 / 13.27 | 31.93 / 24.13 / 11.32 | 38.68 / 27.83 / 13.50 | 28.18 / 26.19 / 14.76 |
| Profit factor | 3.99 / 1.80 / 1.47 | 4.11 / 1.80 / 1.47 | 3.81 / 1.78 / 1.46 | 3.89 / 1.78 / 1.48 | 3.34 / 1.78 / 1.51 |
| Win % | 50.7 / 47.5 / 45.1 | 52.3 / 47.2 / 44.7 | 47.8 / 46.0 / 44.0 | 55.2 / 48.1 / 46.2 | 54.7 / 47.6 / 45.8 |
| Payoff | 2.71 / 2.34 / 1.96 | 2.80 / 2.65 / 2.16 | 2.74 / 2.18 / 1.86 | 2.61 / 2.35 / 1.96 | 2.32 / 2.53 / 2.13 |
| MFE capture | 0.24 / 0.18 / 0.14 | 0.29 / 0.23 / 0.18 | 0.20 / 0.14 / 0.10 | 0.31 / 0.23 / 0.17 | 0.27 / 0.23 / 0.19 |
| CAGR ex top-5 % | 22.77 / 16.74 / 4.36 | 25.36 / 18.75 / 5.91 | 20.26 / 14.40 / 2.47 | 22.09 / 15.73 / 3.09 | 21.02 / 18.50 / 6.29 |
| Cost share % | 2.43 / 5.42 / 8.14 | 2.12 / 4.96 / 7.57 | 2.75 / 6.04 / 8.99 | 2.38 / 5.38 / 7.92 | 2.54 / 4.75 / 6.51 |
| **CAGR drop, IS → 2022-25** | **−18.12** | **−19.20** | **−17.47** | **−19.55** | **−13.34** |
| **Excess drop, IS → 2022-25** | **−15.92** | **−17.00** | **−15.27** | **−17.35** | **−11.14** |

- **Deployment is the only metric that held** for all five.
- **Return:** every config lost 13-20 pts of CAGR from in-sample to 2022-2025. E2, the simplest,
  lost the least and is the only one still above TRI.
- **Drawdown:** max DD worsened 1.4-5.0 pts. The order on depth is nearly kept (hold-out
  H1 < H3 < F1 < G1 < E2; in-sample H3 and F1 were the other way round), but not the order on
  return.
- **Edge:** profit factor halved or worse. CAGR without the top 5 trades fell to 2-6%, so the
  2022-2025 return depends on a few large winners.

Rules kept: venv python on m3, `PGOPTIONS default_transaction_read_only=on`, one run at a time with
the ≥2.5 GB check, data coverage confirmed and the files frozen (sha256 in `FROZEN.txt`) before the
first run, only the window changed, no tuning and no reruns, no `.env` access, no commits, no engine
change, nothing on m1.
