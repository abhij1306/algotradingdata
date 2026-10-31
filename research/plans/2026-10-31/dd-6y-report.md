# Drawdown focus, 2016-2021 in-sample: rotation filter stacks, B1 drawdown anatomy, levers

Owner go 2026-10-31. Two diagnostic runs on m3 at main `f1c8472` (run.json format 1.6). Window
2016-01-01 to 2021-12-31 with the normal warm-up, NIFTY500_PIT, stocks only, ₹10L, database
read-only. No hold-out read. Benchmark: NIFTY 500 TRI, `benchmark_cagr_pct` **15.66%**. No engine code
was changed and nothing was tuned beyond the one stated change per run. Short IDs are the first 8
characters of the run ID.

| Run | Change on B1 (portfolio file, `set`) | Run ID |
| --- | --- | --- |
| B1 | G3 p5 rotation alone (`combo-6y/b1-rotation.yaml`) | `01a19039-9a2c-75f7-87eb-9c4dbdba02b3` |
| R1 | `rotation.reweight=false` | `01a1909b-b199-7149-b07e-1edf70446c82` |
| R3 | `rotation.market_filter=true` (NIFTY 500 close above SMA200, `rising_days` 0) | `01a1909e-3198-7255-ab87-686e48f28745` |
| **D1** | `rotation.reweight=false` + `rotation.market_filter=true` (the R1+R3 stack) | `01a190cd-a63a-715f-aa4e-3e8a599cea0e` |
| **D2** | `rotation.market_filter=true` + `regime.params.rising_days=20` (close above an SMA200 that is also above its value 20 sessions earlier) | `01a190ce-c2ec-72fd-a034-fc13823b4ce0` |

**Why `rising_days` 20.** The gate is read only on the rebalance close, once a month (about 21
sessions). With 20, the SMA200 must be higher than it was at about the previous decision close, so
the slope test covers one rebalance interval. With 10 it covers half an interval, which is mostly
noise in a 200-session average. Afterwards I checked the month-end gate readings in the store
(`gates.json`): 10 and 20 switch the gate off on the same 27 of 72 month-ends, so in this window the
choice between them made no difference.

Files on m3 in `/data/workspace/backtests/dd-6y/`: the two portfolio files, logs, `run_all.sh`, and
four read-only scripts with their output. `dd6y_stats.py` → `stats.json` gives every metric, using the engine's
`standard.book_metrics` (recomputed values equal run.json). `dd6y_anatomy.py` →
`anatomy-b1.json` is Part B. `dd6y_windows.py` → `windows.json` gives each run inside B1's drawdown
windows. `dd6y_gates.py` → `gates.json` gives the gate readings at month-ends (Part C). Audits: D1 `warn`
(concentration, data), D2 `warn` (data). B1/R1/R3 as in the next-6y report. Both runs completed.

## Verdict

- **Deployment first. Both stacks fail it.** D1 is **72.3%** invested = 14.50 positions × 4.99%,
  with **27.5%** zero-position days (`01a190cd`). D2 is **61.9%** = 12.45 × 4.97%, with **37.6%**
  zero-position days (`01a190ce`). B1 is 99.4% = 19.99 × 4.97% at 0.07% (`01a19039`).
- **D1 (R1+R3) adds no drawdown protection.** Max DD **36.24** is worse than B1 (35.34) and R3
  (34.53). CAGR is 22.30 vs 26.88, Calmar 0.62 vs 0.76, and the longest DD is 727 sessions vs 356
  (`01a190cd`). Per unit invested it is the best rotation so far: CAGR per invested 30.86, Sharpe
  1.26, Sortino 1.76, profit factor 3.08. But it keeps R3's idle time (27.5% zero days) and adds R1's
  concentration: top-5 trades are 50.1% of P&L, and 2018 is −23.9%. The two effects did not offset.
  **Reject.**
- **D2 (rising SMA200) has the lowest max DD of any rotation run, at a cost that is too high.** Max
  DD is **30.54** (−4.8 pts vs B1), but CAGR is **17.30** (−9.6 pts, barely above TRI's 15.66),
  Calmar 0.57, Sharpe 1.11, and the longest DD is 768 sessions (`01a190ce`). The DD gain is
  not where it is needed. D2's worst drawdown is 2018-01 → 2019-05, which the filter did not stop
  (2018 −22.6%). The slope test kept the book in cash from 2020-03-02 through the 2020-10-30 decision close
  (back in on 2020-12-01), so 2020 is +9.55% at 25.7% invested vs B1's +31.14%. **Reject.**
- **Part B: B1's drawdowns are a high-beta, concentrated, mostly gap-driven book.** Outside the 2020
  crash, B1 falls **1.5-2.4× as far as NIFTY 500 TRI** over the same dates (16.6 vs 6.9, 20.1 vs 13.3,
  21.7 vs 10.8, 23.4 vs 11.6). At the peaks of those episodes the holding beta was 1.0-1.5 and up to
  half the book sat in one sector (Financial Services 50.4% before demonetisation, IT 35.4% in
  2018-08). Gap-downs of 2% or more account for **34.4 of 35.3 pts in 2020**, 11.3 of 16.6 in
  2018-01, 15.6 of 23.4 in 2018-19 and 10.1 of 21.7 in 2016-Q4. A stop cannot avoid a gap, so
  exposure has to be lower before the event. The monthly rotation reacted late
  in every fast episode: 17 of 20 peak holdings were still held at the 2020 trough.
- **No all-cash market filter on a monthly gate fixes this.** The SMA200 gate was on at both the peak
  and the trough of 2018-01, so it could not act. It turned off only after the 2016-Q4 trough, and R3
  sold on 2017-01-02 with B1 already down 16.3%. It worked once, in 2020, when the 2020-02-28 close
  happened to fall early in the crash.
- **Next round (Part C):** four deployment-neutral single changes first (more names, a shorter
  volatility window, a tighter hold buffer, fortnightly rebalance). Then two exposure scalers that
  cost deployment: the live regime multiplier as a partial de-risk, and a breadth gate. The levers
  that fit the anatomy best do not exist yet: a sector cap, a per-holding stop, a mid-month
  emergency check and a configurable de-risk table all need code (§C3).

## 1. Deployment and headline (lead table)

All numbers come from `stats.json`: run.json metrics, recomputed with `standard.book_metrics`. Size =
the mean, over sessions with a position, of value ÷ equity ÷ positions. Avg DD is the mean
drawdown over all sessions.

| Run | Invested % | Avg positions | Avg size % | Zero-pos days % | CAGR % | TRI CAGR % | Max DD % | Avg DD % | Longest DD (sessions) | Sharpe | Sortino | Calmar | CAGR per invested |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 `01a19039` | 99.38 | 19.99 | 4.97 | 0.07 | 26.88 | 15.66 | 35.34 | 3.54 | 356 (2018-08-31 → 2020-02-12) | 1.22 | 1.67 | 0.76 | 27.05 |
| R1 `01a1909b` | 99.52 | 19.99 | 4.98 | 0.07 | **27.76** | 15.66 | 37.77 | 3.54 | 501 (2018-08-31 → 2020-09-14) | 1.24 | 1.69 | 0.74 | 27.90 |
| R3 `01a1909e` | 72.08 | 14.50 | 4.97 | 27.46 | 20.36 | 15.66 | 34.53 | 3.33 | 723 (2018-01-23 → 2020-12-28) | 1.19 | 1.66 | 0.59 | 28.25 |
| **D1** `01a190cd` | 72.27 | 14.50 | 4.99 | 27.46 | 22.30 | 15.66 | 36.24 | 3.33 | 727 (2018-01-23 → 2021-01-01) | **1.26** | **1.76** | 0.62 | **30.86** |
| **D2** `01a190ce` | 61.92 | 12.45 | 4.97 | 37.62 | 17.30 | 15.66 | **30.54** | **3.24** | 768 (2018-01-23 → 2021-03-02) | 1.11 | 1.51 | 0.57 | 27.94 |

Every longest drawdown recovered within the window. Max DD dates: B1 and R1 2020-03-23 trough
(R1's from a 2018-08-31 peak); R3 and D1 2018-01-23 → 2019-10-04; D2 2018-01-23 → 2019-05-13
(`windows.json`).

## 2. Trade efficiency

Trades are whole trades (legs summed). The rotation has no stop, so its R is return on cost, a
fraction, not risk units. Compare runs on profit factor and % payoff. Planned R:R is n/a (no target).

| Run | Invested % | Avg pos | Size % | Zero % | Trades | Profit factor | Win % | Avg win % | Avg loss % | Payoff % | Avg win R | Avg loss R | Payoff R | Exp R | MFE capture | Max consec losses | CAGR ex top-5 % | Top-5 share % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 `01a19039` | 99.38 | 19.99 | 4.97 | 0.07 | 328 | 3.02 | 51.2 | +28.4 | −11.3 | 2.53 | 0.28 | −0.11 | 2.53 | 0.091 | 0.26 | 9 | 19.86 | 38.1 |
| R1 `01a1909b` | 99.52 | 19.99 | 4.98 | 0.07 | 328 | 3.44 | 50.3 | +37.2 | −12.0 | 3.09 | 0.37 | −0.12 | 3.09 | 0.127 | 0.36 | 9 | 18.13 | 48.7 |
| R3 `01a1909e` | 72.08 | 14.50 | 4.97 | 27.46 | 331 | 2.68 | 48.9 | +25.0 | −9.4 | 2.65 | 0.25 | −0.09 | 2.65 | 0.074 | 0.26 | 9 | 13.95 | 41.7 |
| **D1** `01a190cd` | 72.27 | 14.50 | 4.99 | 27.46 | 331 | 3.08 | 48.9 | +30.9 | −10.0 | 3.09 | 0.31 | −0.10 | 3.09 | 0.100 | 0.35 | 9 | 13.78 | 50.1 |
| **D2** `01a190ce` | 61.92 | 12.45 | 4.97 | 37.62 | 292 | 2.58 | 51.0 | +23.2 | −9.5 | 2.44 | 0.23 | −0.10 | 2.44 | 0.072 | 0.26 | 9 | 11.12 | 45.0 |

Turnover (`rebalances.csv`, filled orders): D1 had 59 rebalance days, 331 buys and 311 sales
(149 out of buffer, 42 not eligible, 120 market filter), no trims or top-ups. 203 buys were
cash-scaled, on 43 days. It traded ₹427.8L with fees ₹57,887 (cost share 2.41%). D2 had 52 rebalance
days, 292 buys, 235 top-ups, 240 trims and 272 sales (122 / 30 / 120). It traded ₹413.0L with fees
₹58,995 (3.55%). Filter-sale days: D1 has the same 7 as R3 (2017-01-02, 2018-04-02, 2018-07-02,
2018-10-01, 2018-10-03, 2019-08-01, 2020-03-02). D2 has the same days, except 2019-07-01 in place
of 2019-08-01: the slope test turned the gate off one month earlier. D2 is out of the market for more
months, not on more separate occasions.

## 3. Per year: return / invested / in-year max DD vs TRI

From run.json `by_year` and `equity.csv`. TRI in-year max DD from `equity.csv` `benchmark_tri`.

| Year | TRI ret % (in-yr DD) | B1 `01a19039` | R1 `01a1909b` | R3 `01a1909e` | D1 `01a190cd` | D2 `01a190ce` |
| --- | --- | --- | --- | --- | --- | --- |
| 2016 | +5.12 (13.8) | −5.97 / 99.6 / 21.7 | −5.76 / 99.8 / 22.1 | +2.80 / 67.7 / 22.5 | +3.37 / 67.9 / 22.8 | −0.81 / 50.0 / 22.5 |
| 2017 | +37.65 (4.8) | +76.38 / 99.5 / 8.4 | +81.04 / 99.7 / 8.7 | +58.08 / 91.0 / 8.4 | +65.39 / 91.3 / 8.5 | +56.49 / 90.7 / 8.4 |
| 2018 | −2.14 (15.6) | −5.57 / 99.5 / 23.1 | −13.24 / 99.7 / 25.1 | −22.62 / 57.5 / 25.9 | **−23.90** / 57.6 / 27.7 | −22.57 / 57.4 / 25.8 |
| 2019 | +8.97 (11.5) | +14.58 / 99.5 / 13.3 | +15.10 / 99.7 / 13.1 | −1.06 / 58.4 / 13.6 | −1.17 / 58.5 / 13.8 | +9.07 / 49.2 / **6.3** |
| 2020 | +17.89 (38.1) | +31.14 / 99.2 / 35.3 | +36.55 / 99.4 / 36.8 | +37.87 / 58.8 / 7.6 | **+39.50** / 59.0 / 7.7 | +9.55 / **25.7** / 8.0 |
| 2021 | +31.60 (9.8) | +77.38 / 99.0 / 6.6 | +87.04 / 98.9 / 7.2 | +77.31 / 98.9 / 6.6 | +86.64 / 99.2 / 8.2 | +81.43 / 99.0 / 6.6 |

- Against TRI, D1 beats it in 3 years (2017, 2020, 2021) and misses in 2016, 2018 and 2019, the same
  years as R3. D2 beats it in 3 (2017, 2019 by 0.1 pt, 2021) and misses in 2016, 2018 and 2020.
- Every filtered run has an in-year DD in 2018 as deep as or deeper than B1's (25.8-27.7 vs 23.1).
  The filter buys back after each whipsaw, and the April and July 2018 exits came after the falls.

## Part B. Anatomy of B1's five largest drawdowns (`01a19039`, no runs)

**Method** (`dd6y_anatomy.py`). Episodes come from `equity.csv`. The book is rebuilt each session
from `rebalances.csv`: each filled order's ₹ value, drifted by the raw open over NSE prev_close
(overnight) and the close over the open (intraday). A split or bonus ex-date is detected (an open
near a simple fraction of prev_close) and scaled out. Renamed names are joined by ISIN or symbol
(e.g. NIITTECH → COFORGE). The rebuilt position value matches the engine's `position_value`: median
error 0.03%, max 1.2%, with 0 missing name-days. Dividends are not added back. "Gap-down" means a
holding's overnight move of −2% or worse (≤ −5% also shown), summed in points of peak equity, peak
to trough. Holding beta is the value-weighted 252-session daily beta of each holding to the NIFTY
500 at the peak. Realised beta is the book's daily log return against NIFTY 500 TRI from peak to
recovery. The "top-loss list" is B1's 20 worst trades by net ₹ (AUBANK −₹49.6k … PFIZER −₹20.0k); a
match is a top-20 losing trade already open at the peak. Gate is the NIFTY 500 SMA200 test (R3's;
D2's rising-20 reading is the same at every peak and trough below).

### B.1 The five episodes

| # | Peak → trough → recovery | Depth % | Sessions (fall / recover / total) | TRI same dates: peak→trough % (max DD in window) | Invested at peak % / positions |
| --- | --- | --- | --- | --- | --- |
| 1 | 2020-02-19 → 2020-03-23 → 2020-09-14 | **35.34** | 21 / 119 / 140 | −37.23 (37.23) | 99.9 / 20 |
| 2 | 2018-08-31 → 2019-08-22 → 2020-02-12 | **23.36** | 238 / 118 / 356 | −11.64 (15.64) | 99.5 / 20 |
| 3 | 2016-10-25 → 2016-12-26 → 2017-03-16 | **21.71** | 43 / 55 / 98 | −10.77 (10.77) | 98.7 / 20 |
| 4 | 2016-01-01 → 2016-02-26 → 2016-07-27 | **20.06** | 39 / 101 / 140 | −13.26 (13.80) | 100.0 / 20 |
| 5 | 2018-01-23 → 2018-02-06 → 2018-07-11 | **16.62** | 9 / 106 / 115 | −6.93 (10.63) | 99.8 / 20 |

### B.2 What the book held, and where the loss came from

| # | Top sectors at peak (% of book) | Top-3 share / HHI | Holding beta at peak (range) | Realised beta vs TRI | Top-loss trades held at peak | Gap-downs ≤−2% (≤−5%) pts | Rest pts | Worst 5 names (pts of peak equity) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Financial Services 30.8, Consumer Durables 29.6, Chemicals 10.3 | 70.7 / 0.22 | 0.87 (0.45-1.55) | 0.82 | 3: AAVAS, ISEC, NAM-INDIA | **−34.4** (−22.8) | −0.9 | ISEC −2.7, BAJFINANCE −2.7, AUBANK −2.3, NAM-INDIA −2.3, AAVAS −2.3 (all Financial Services) |
| 2 | IT 35.4, Financial Services 15.5, FMCG 14.8 | 65.7 / 0.20 | **1.14** (0.18-2.31) | 0.92 | 0 | −15.6 (−4.6) | −8.9 | DHANI −2.3, HEG −1.5, BSOFT −1.5, JUBLFOOD −1.5, WIPRO −1.4 |
| 3 | **Financial Services 50.4**, Metals 9.9, unknown 9.7 | 70.0 / **0.29** | 1.01 (0.42-1.59) | **1.73** | 0 | −10.1 (−8.3) | −11.3 | MANAPPURAM −2.4, DELTACORP −1.8, DALMIABHA −1.8, ESCORTS −1.5, JMFINANCIL −1.4 |
| 4 | Healthcare 24.8, unknown 10.1, Oil & Gas 10.0 | 44.9 / 0.11 | **1.28** (0.62-2.28) | 1.15 | 0 | −4.5 (−0.6) | **−15.5** | MARKSANS −1.9, PIPAVAVDOC −1.8, JUBILANT −1.6, NIITLTD −1.5, GODFRYPHLP −1.4 |
| 5 | FMCG 20.6, Auto 18.0, unknown 9.2 | 47.8 / 0.11 | **1.48** (0.49-2.68) | **1.58** | 2: ADANITRANS, BBTC | −11.3 (−6.9) | −5.2 | **VAKRANGEE −3.5**, RADICO −1.2, RAIN −1.2, STRTECH −1.1, DHANI −1.0 |

"Rest" = the episode's summed contributions minus the gap-down part: intraday moves plus overnight
moves above −2%, gains included. The two columns sum to the rebuilt book's fall, which differs from
the equity fall by fees, cash and dividends: −35.3, −24.5, −21.4, −19.9 and −16.5 pts against
−35.3, −23.4, −21.7, −20.1 and −16.6. "Unknown" is the run's `industry_unknown_pct` (8.4%) bucket.
Sectors are NSE's industry field as `trades.csv` carries it.

### B.3 How fast the rotation reacted

| # | Gate at peak / trough | First rebalance after peak (sessions after) | Peak names still held at trough | Rebalances peak → recovery | Sales on those days |
| --- | --- | --- | --- | --- | --- |
| 1 | on / off | 2020-03-02 (7) | **17 of 20** | 7 | 3 at 2020-03-02, 8 at 2020-04-01 (after the trough), 3 / 0 / 6 / 7 / 5 |
| 2 | on / off | 2018-09-03 (1) | 1 of 20 | 18 | 3-9 a month; the book turned over completely and kept losing |
| 3 | on / off | 2016-11-01 (5) | 12 of 20 | 5 | 3 at 2016-11-01, 6 at 2016-12-01, 6 at 2017-01-02 |
| 4 | off / off | 2016-02-01 (20) | 14 of 20 | 6 | 6, 7, 1, 3, 7, 7 |
| 5 | on / on | 2018-02-01 (6) | 16 of 20 | 6 | 4 at 2018-02-01 (the fall was over by 02-06), 5, 1, 5, 6, 1 |

### B.4 Reading

1. **2020 (35.3%): a market crash with no excess over TRI** (35.3 vs 37.2). The book was not high-beta
   (0.87), but 60% of it sat in two sectors, and its five worst names were all financials (−12.3 pts
   together). Nearly all the loss came on gap-down opens (−34.4 pts). The one rebalance inside the fall
   (2020-03-02) sold 3 names. B1 recovered in 119 sessions, while TRI was still 4.1% under its
   2020-02-19 level. **Lever:** exposure before the fall. R3/D1/D2 cut this episode to 6.7/7.3/6.7%
   (`windows.json`), because the 2020-02-28 decision close came 6 sessions into the crash (B1 then 7.0% down).
2. **2018-08 → 2019-08 (23.4%): a year-long grind at twice TRI's depth** (−11.6). The book was IT
   heavy and high-beta (1.14, up to 2.31) at the peak. Then it rotated through new leaders that also
   fell: 19 of 20 names were replaced, 18 rebalances ran, and 15.6 of the points still came from
   gap-downs. This is the momentum reversal of the 2018-19 small/mid-cap bear market. **Lever:**
   lower beta and less concentration. A filter helps little: R3/D1/D2 still lost 27.0/27.7/22.5% inside
   this window, at 48-54% invested (`windows.json`), because their whipsaws added losses.
3. **2016-Q4 (21.7%): demonetisation hit a book that was half financials** (HHI 0.29, realised beta
   1.73). Half the loss was gap-downs (−10.1 pts, mostly ≤−5%). The SMA200 gate was still on at the
   2016-11-30 close and turned off only on 2016-12-30, after the trough. R3 then sold on 2017-01-02
   at the bottom, with B1 16.3% down that day. **Lever:** a sector cap (needs code).
   A breadth gate read the 2016-11-30 close as off (§C2).
4. **2016-01 → 02 (20.1%): the run's starting book in a falling market, gradual** (only −4.5 pts
   from gaps, −15.5 from intraday and small overnight moves). Holding beta was 1.28. The gate was
   already off: R3/D1 held ~44% and D2 ~13% invested in this window, and lost 3.4/3.4/0.9%. **Lever:** the market
   filter does work here. A per-holding stop would also have acted on this slow decline.
5. **2018-01 → 02 (16.6%): nine sessions, the highest-beta book** (1.48, up to 2.68; realised 1.58),
   and one name, VAKRANGEE, cost 3.5 pts in a run of lower-circuit gaps. The gate was on throughout,
   so no index filter can catch it (R3/D1/D2 lost 19.6/21.1/19.6% in this window). **Lever:** more
   names (smaller single-name weight), a lower-volatility selection and a gap or circuit exclusion
   (needs code).

Across the five, 5 of the 20 worst trades were already open at a peak: AAVAS, ISEC and NAM-INDIA
(2020), ADANITRANS and BBTC (2018-01). Most of the worst trades were bought after the peak: AUBANK
was bought on 2020-03-02, inside the crash.

## Part C. Drawdown levers

### C1. Every existing knob that could cut drawdown (overlay excluded)

"Deployment cost" is the expected effect on invested %. Gate figures are month-end readings in the
store, 2015-12 to 2021-11 (72 decision closes), through the engine's own `regime_allows_longs` and
regime functions (`gates.json`). They are not backtests.

| Key (portfolio file) | What it does to the rotation | Evidence / expected DD effect | Expected deployment cost |
| --- | --- | --- | --- |
| `set: rotation.market_filter=true` | Gate off on the rebalance close → the whole book is sold to cash | R3: max DD −0.8, 2020 DD 7.6 vs 35.3; 2018 worse | **High:** R3 72.1%, 27.5% zero days |
| `set: regime.params.rising_days=N` (with the filter) | The SMA must also be rising | D2: max DD 30.5; 10 and 20 identical here (27 of 72 month-ends off) | **Higher:** D2 61.9% |
| `set: regime.params.sma=N` (with the filter) | A shorter gate SMA | SMA100: 19 of 72 off, 15 flips (SMA200 20 / 13); off at 2016-11-30 and 2018-02-28, a month earlier | Like R3, ~26% off, more whipsaw |
| `set: regime.index=NIFTY SMALLCAP 250` | Gate on the small-cap index | Off on 55 of 72 month-ends | **Unusable:** ~76% off |
| `set: regime={"rule":"breadth_above",…}` (with the filter) | Gate on store breadth (% above SMA50), `min_pct`, `off_below_pct` hysteresis, `smooth_days` | ≥30, smooth 5: 17 of 72 off (23.6%), off at 2016-11-30, 2018-02-28 and 2020-02-28. ≥40 / off <30: 22 off. ≥50 / off <40: 33 off | 24-46% off by threshold |
| `set: regime={"rule":"sma_fast_above_slow_both_rising",…}` (with the filter) | Fast SMA over slow SMA, both rising | Not measured. Slower than a close-over-SMA test | Likely ≥ R3 |
| `conventions: {regime_mult: policy}` | The live regime engine's multiplier (bull quiet 1.0, bull volatile 0.75, correction 0.5, bear 0.25; 3-day confirm; ±0.25 a night) scales the sleeve's capital at each rebalance. With `reweight` true the holdings are trimmed to it. **A partial de-risk that never goes to all-cash** | Month-ends: 29 bull quiet, 9 bull volatile, 15 correction, 19 bear. 0.5 at 2016-11-30 and 2020-02-28, 0.25 from 2018-09-28 to 2019-02-28 | **Medium-high:** mean multiplier 0.67 → ~66% invested, never under ~25% |
| strategy `weight` < 1 | A static cut in sleeve capital | DD scales about 1:1 | 1:1, always idle |
| `set: rotation.top_n=30` (buffer 40 stays valid) | 30 names at ~3.3% each | Smaller single-name hits (VAKRANGEE 3.5 pts at 5%); a little less sector weight | **None** |
| `set: rotation.buffer_rank=30` | A held name is sold sooner when its rank fades | R2 (60) added 4.3 pts of max DD, so a tighter buffer is the untested direction | None; more turnover |
| `set: rotation.rebalance=fortnight` (or `weekly`) | Ranks, sales and the gate are read twice (or four times) a month | 2020: the first sale came 7 sessions in; 2016-Q4 sales came a month late | None; turnover and fees up with `reweight` |
| `set: rotation.vol_sessions=63` | The risk-adjusted score uses 3-month volatility instead of 12-month | Penalises recently volatile names, aimed at the 1.28-1.48 betas of episodes 4-5 | None |
| `set: rotation.score=…`, `short_sessions`, `long_sessions`, `skip_sessions` | Momentum definition | No direct DD link. A selection change | None |
| `set: rotation.reweight=true` (B1 already) | Trims winners monthly | R1 (false) added 2.4 pts of max DD | None |
| `set: universe[min_turnover].params.inr_cr=50` (or `min_price`) | A larger, more liquid universe | Probably lower beta and fewer circuit names, but fewer momentum leaders | None |
| Risk policy and account keys (`risk_pct`, `max_positions`, `max_per_industry`, `flat_ladder`, `policy_set` kill and health) | **No effect on the rotation.** The rotation bypasses the ledger caps, and the backtest does not simulate kill switches or health multipliers | n/a | n/a |

All `set` paths above validate against B1's config offline. I applied them with the backtest's
override parser and `StrategyConfig` validation; nothing was run. `regime_mult: policy` with a
rotation-only run is untested: the first run would show whether any night lacks regime inputs,
since a night without an allocation makes no rebalance.

### C2. Proposed next round: single changes on B1, in order (not run)

The order follows the anatomy and the owner's rule that idle cash is a failure. Deployment-neutral
changes come first, then the two exposure scalers.

1. **`rotation.top_n=30`**: concentration (episodes 1, 3, 5). No deployment cost. It tests whether
   a smaller weight per name and per sector cuts the gap losses without diluting the return too far.
2. **`rotation.vol_sessions=63`**: beta (episodes 2, 4, 5 at 1.14-1.48). No deployment cost.
3. **`rotation.buffer_rank=30`**: a faster exit for names that fade. The mirror of R2, which worsened DD.
   No deployment cost; more turnover.
4. **`rotation.rebalance=fortnight`**: faster reaction to rank and eligibility changes (17 of 20
   names were still held at the 2020 trough). No deployment cost; about twice the trims and top-ups.
5. **`conventions: {regime_mult: policy}`**: a partial de-risk instead of all-cash. Expected ~66%
   invested, so test it only if 1-4 fall short. It is the only existing way to scale the book
   instead of emptying it.
6. **R3 with a breadth gate**: `rotation.market_filter=true`, `regime={"index":"NIFTY 500","rule":"breadth_above","params":{"min_pct":30,"smooth_days":5}}`,
   as a single change against R3 (the gate rule). At the month-end closes it reads off a month earlier than the SMA200
   in 2016-Q4 and 2018-02. It is off at 23.6% of month-ends vs 27.8%, but flips 16 times vs 13.

### C3. Needs code (not runnable today)

- **Sector/industry cap in the rotation's selection.** `max_per_industry` does not reach the rotation.
  This is the direct fix for episodes 1 and 3 (60% in two sectors; 50% in one).
- **Per-holding stop or trailing exit for the rotation.** The rotation has no exit stack. It would
  help gradual declines (episode 4), not gaps.
- **A mid-month emergency check.** The gate and ranks are read only on the rebalance close. A daily
  or weekly breadth/index trigger that de-risks between rebalances would act on episodes 1 and 5.
- **A configurable de-risk table per run, or continuous scaling** (e.g. exposure = f(breadth)).
  Today `regime_mult: policy` uses the stored live table only.
- **A beta or volatility cap per holding or for the book**, and a **gap or circuit exclusion**
  (VAKRANGEE-style lower-circuit runs).
- **A quality filter in the rotation universe.** The universe stage offers only `series_in`,
  `min_turnover`, `min_price`, `price_band_allowed` and `adr_min`; there is no fundamentals
  criterion.
