# Combined portfolios, 2016-2021 in-sample: rotation, old VCP, Darvas

Owner go 2026-10-31. Six diagnostic runs on m3 at main `b3f057c` (the not_in_universe fix, #344; no
runtime patch), window 2016-01-01 to 2021-12-31 with the normal warm-up, NIFTY500_PIT, stocks only
(no ETF overlay anywhere), ₹10L, database read-only. No hold-out read. Benchmark: NIFTY 500 TRI, each
run's `benchmark_cagr_pct` **15.66%** over the window (per-year TRI from `run.json` `by_year`).
Every number carries its run ID; short IDs below are the first 8 characters.

| Run | Portfolio file | Run ID |
| --- | --- | --- |
| B1 | `b1-rotation.yaml`: G3 p5 rotation alone, o1 settings | `01a19039-9a2c-75f7-87eb-9c4dbdba02b3` |
| B2 | `b2-oldvcp.yaml`: G3 p2 old VCP alone, o2 settings | `01a1903c-9ff5-7335-a7ec-b5cd7a377ce4` |
| B3 | `b3-darvas.yaml`: Darvas seed alone on p2 account settings, o3 settings | `01a1904d-8d90-726d-b31a-c6e5265a4f53` |
| C1 | `c1-rot70-vcp30.yaml`: rotation 0.7 + VCP 0.3 | `01a19057-3390-75bf-b3bd-593b77a217e2` |
| C2 | `c2-rot50top10-vcp50.yaml`: rotation 0.5 with `rotation.top_n=10` + VCP 0.5 (declared bundle against C1) | `01a19064-262f-7152-876b-301c82a5abea` |
| C3 | `c3-rot60-vcp20-darvas20.yaml`: rotation 0.6 + VCP 0.2 + Darvas 0.2 | `01a19072-5b1e-7506-9601-1b5bd23978b9` |

Files, logs, the stats script (`combo6y_stats.py`) and its output (`stats.json`) are on m3 in
`/data/workspace/backtests/combo-6y/`.

## Verdict

- **Deployment first.** Rotation alone is fully deployed: **99.4%** invested = 20.0 positions × 4.97%,
  zero-position days 0.07% (`01a19039`). Every combo is less invested: C1 **85.1%** (24.0 × 3.54%),
  C2 **75.9%** (14.0 × 5.42%), C3 **79.5%** (28.0 × 2.84%). Zero-position days are 0.07% in all three.
  The gap is the setup sleeves. They use only about 45% of their allotment: VCP 13.5 of 30 pts in C1 and
  22.5 of 50 in C2; VCP and Darvas together 17.7 of 40 in C3. The cash they leave idle is the first
  thing to fix. Alone, VCP is 52.4% invested (4.06 × 12.93%, 17.2% zero-position days, `01a1903c`) and
  Darvas 42.8% (3.77 × 11.36%, 27.8% zero-position days, `01a1904d`).
- **On return, no combo beats rotation alone.** CAGR: B1 **26.88** against C1 22.29, C2 20.08 and
  C3 18.22 (TRI 15.66). Per unit invested the combos come close (CAGR ÷ invested: B1 27.05, C1 26.18,
  C2 26.47), so most of the gap is idle cash, not worse picks.
- **On drawdown, every combo is shallower, but none is a clear risk-adjusted win.** Max DD: B1
  35.3% against C1 27.9%, C2 31.2% and C3 26.4%. Only C1 edges B1 on risk-adjusted terms: Calmar
  0.80 vs 0.76, Sharpe 1.25 vs 1.22, Sortino 1.70 vs 1.67. That is within noise. Every combo is
  under water longer than B1: 511, 654 and 652 sessions against 356. The combos' 2018-01 drawdown
  lasted until 2020, while B1's did not start until 2018-08. VCP lost −22.5% in 2018 alone
  (`01a1903c`), and it made C1's 2018 worse than B1's (−10.6% vs −5.6%).
- **VCP's six-year edge is real but modest and concentrated**, nothing like its 2017: 0.51 R,
  profit factor 2.04, CAGR 12.57 (below TRI), 5.92 without its top 5 trades, and 60% of P&L
  in the top 5 trades (`01a1903c`). It captures 20% of its MFE.
- **Darvas has no edge over six years**: CAGR −0.82, −0.01 R, profit factor 0.95 (`01a1904d`).
  In C3 its sleeve made −0.28 pts of capital on 235 trades (`01a19072`). It only dilutes the
  combination. Drop it.
- **Best of the three: C1.** It trades 4.6 pts of CAGR for 7.5 pts less max DD and a marginally
  better Calmar and Sharpe. It is not a reason to add VCP until the idle sleeve cash is put to work.

## 1. Deployment (lead table)

From `equity.csv` (`invested_pct`, `open_positions` per session; size = Σ invested ÷ Σ positions, so
invested = positions × size holds exactly).

| Run | Invested % | Positions | Size % | Zero-pos days % | CAGR % | TRI CAGR % | Max DD % | Trades | Exp R | CAGR ex top-5 % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 rotation `01a19039` | 99.38 | 19.99 | 4.97 | 0.07 | 26.88 | 15.66 | 35.34 | 328 | 0.09¹ | 19.86 |
| B2 old VCP `01a1903c` | 52.44 | 4.06 | 12.93 | 17.23 | 12.57 | 15.66 | 33.65 | 230 | 0.51 | 5.92 |
| B3 Darvas `01a1904d` | 42.81 | 3.77 | 11.36 | 27.79 | −0.82 | 15.66 | 29.01 | 245 | −0.01 | −4.16 |
| C1 rot 0.7 + VCP 0.3 `01a19057` | 85.12 | 24.02 | 3.54 | 0.07 | 22.29 | 15.66 | 27.87 | 567 | 0.24² | 17.42 |
| C2 rot 0.5 top10 + VCP 0.5 `01a19064` | 75.87 | 13.99 | 5.42 | 0.07 | 20.08 | 15.66 | 31.17 | 375 | 0.33² | 13.99 |
| C3 rot 0.6 + VCP 0.2 + Darvas 0.2 `01a19072` | 79.45 | 27.97 | 2.84 | 0.07 | 18.22 | 15.66 | 26.43 | 821 | 0.15² | 13.97 |

¹ The rotation has no stop: its R is the trade's return as a fraction (0.09 = +9% per trade).
² A combo's run-level R mixes rotation "R" (return fraction) with VCP/Darvas R (risk units), so it
is not meaningful. Read the sleeve rows (§3).

Per-sleeve deployment in the combos. The setup sleeves are computed from `trades.csv` at cost basis
(qty × entry price on each session held ÷ that session's equity). The rotation is the account's
invested share minus the setup sleeves. Each sleeve's size = invested ÷ positions.

| Run | Sleeve (weight) | Invested % of account | Share of its allotment | Positions | Size % |
| --- | --- | --- | --- | --- | --- |
| C1 `01a19057` | rotation (0.7) | 71.6 | 102% | 19.99 | 3.58 |
| | VCP (0.3) | 13.5 | 45% | 4.03 | 3.35 |
| C2 `01a19064` | rotation (0.5, top 10) | 53.4 | 107% | 9.99 | 5.34 |
| | VCP (0.5) | 22.5 | 45% | 4.00 | 5.63 |
| C3 `01a19072` | rotation (0.6) | 61.8 | 103% | 19.99 | 3.09 |
| | VCP (0.2) | 10.3 | 52% | 4.39 | 2.35 |
| | Darvas (0.2) | 7.4 | 37% | 3.59 | 2.06 |

Rotation shares a little over 100% are the mark-to-market gain above cost that the residual
assigns to it.

## 2. Efficiency and risk/reward

Sources: **R** = `run.json` `metrics` (Sharpe, Sortino, `mar` = Calmar, which I checked equals CAGR ÷ max DD; win %,
exp R, avg win/loss R, avg MFE R, hold sessions, max consecutive losses, longest DD).
**T** = computed from `trades.csv` (legs of a trade summed): profit factor = Σ winning net ₹ ÷ |Σ
losing net ₹|, avg win/loss % = net ÷ (qty × entry price), payoff = avg win ÷ |avg loss|.
**E** = computed from `equity.csv` plus `run.json`: CAGR ÷ (avg invested ÷ 100).
MFE capture = exp R ÷ avg MFE R (R).

| Run | Sharpe R | Sortino R | Calmar R | CAGR per invested E | Profit factor T | Win % R | Avg win % T | Avg loss % T | Payoff % T | Avg win R R | Avg loss R R | Payoff R | Exp R R | Planned R:R | MFE capture | Hold win / loss (sessions) R | Max consec losses R | Time under water (sessions) R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 `01a19039` | 1.22 | 1.67 | 0.76 | 27.05 | 3.02 | 51.2 | +28.4 | −11.3 | 2.53 | 0.28¹ | −0.11¹ | 2.55 | 0.09¹ | n/a³ | 0.26 | 124.2 / 55.2 | 9 | 356 (2018-08-31 → 2020-02-12) |
| B2 `01a1903c` | 0.91 | 1.25 | 0.37 | 23.98 | 2.04 | 33.0 | +18.0 | −4.4 | 4.10 | 2.92 | −0.68 | 4.29 | 0.51 | n/a³ | 0.20 | 57.9 / 10.6 | 11 | 816 (2018-01-24 → 2021-05-18) |
| B3 `01a1904d` | −0.02 | −0.03 | −0.03 | −1.91 | 0.95 | 36.3 | +9.2 | −5.5 | 1.68 | 1.37 | −0.80 | 1.71 | −0.01 | n/a³ | −0.01 | 39.8 / 13.2 | 16 | 984 (2018-01-09 → not recovered) |
| C1 `01a19057` | 1.25 | 1.70 | 0.80 | 26.18 | 2.66 | 42.9 | +25.2 | −7.8 | 3.22 | 1.09² | −0.40² | 2.73² | 0.24² | n/a³ | 0.19² | 103.8 / 32.3 | 12 | 511 (2018-01-23 → 2020-02-19) |
| C2 `01a19064` | 1.22 | 1.67 | 0.64 | 26.47 | 2.72 | 39.2 | +24.9 | −6.6 | 3.75 | 1.61² | −0.51² | 3.16² | 0.33² | n/a³ | 0.19² | 96.4 / 29.1 | 13 | 654 (2018-01-23 → 2020-09-17) |
| C3 `01a19072` | 1.15 | 1.56 | 0.69 | 22.94 | 2.28 | 41.2 | +20.5 | −7.1 | 2.89 | 1.12² | −0.54² | 2.07² | 0.15² | n/a³ | 0.11² | 85.8 / 26.0 | 13 | 652 (2018-01-23 → 2020-09-15) |

³ **Planned reward:risk is n/a for all three strategies: none has a target.** From each run's
`config.json` enabled exits: VCP has a hard stop, a 20-day swing-low trail and an SMA50 close exit,
with `partial_at_r` at 3R disabled. Darvas has a hard stop and a 10-day swing-low trail. The
rotation has no stop and no target; it exits on rank (buffer 40) or eligibility.

### Per sleeve, in the combos

Everything here is from `trades.csv` (T), split by the trade's `playbook` (`strategy:playbook`).
Sleeve P&L sums exactly to the run's. A sleeve has no equity curve of its own (one shared
account), so **Sharpe, Sortino, Calmar, max DD and time under water are n/a per sleeve**.
"P&L per invested" = the sleeve's net ₹ ÷ start capital ÷ 6.0 years ÷ (its invested share of the
account ÷ 100). It is simple, not compounded, so compare it across the sleeves of one run only.
Max consecutive losses here count net ≤ 0 by exit date. That rule is not `run.json`'s: on B2 it gives
14 against `run.json`'s 11.

| Run | Sleeve | Trades | Net P&L ₹ | Pts of capital | P&L per invested (pts/yr) | Profit factor | Win % | Avg win % | Avg loss % | Payoff % | Avg win R | Avg loss R | Payoff R | Exp R | Avg MFE R | MFE capture | Hold win / loss | Max consec losses | Fees ₹ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 `01a19057` | rotation | 328 | 19,67,012 | +196.7 | 45.8 | 2.96 | 51.2 | +28.6 | −11.2 | 2.55 | 0.29¹ | −0.11¹ | 2.55 | 0.09¹ | 0.35¹ | 0.26 | 124.7 / 54.7 | 13 | 59,448 |
| | VCP | 239 | 3,77,971 | +37.8 | 46.7 | 1.93 | 31.4 | +17.6 | −4.5 | 3.89 | 2.90 | −0.69 | 4.23 | 0.44 | 2.48 | 0.18 | 57.1 / 10.4 | 14 | 35,860 |
| C2 `01a19064` | rotation (top 10) | 143 | 13,84,224 | +138.4 | 43.2 | 3.34 | 50.3 | +32.7 | −11.5 | 2.86 | 0.33¹ | −0.11¹ | 2.86 | 0.11¹ | 0.40¹ | 0.27 | 137.2 / 70.1 | 6 | 33,185 |
| | VCP | 232 | 6,14,536 | +61.5 | 45.5 | 2.07 | 32.3 | +17.5 | −4.5 | 3.90 | 2.85 | −0.68 | 4.18 | 0.46 | 2.53 | 0.18 | 57.2 / 10.5 | 14 | 49,901 |
| C3 `01a19072` | rotation | 328 | 15,20,875 | +152.1 | 41.0 | 2.89 | 51.2 | +28.6 | −11.2 | 2.56 | 0.29¹ | −0.11¹ | 2.56 | 0.09¹ | 0.35¹ | 0.26 | 124.7 / 54.7 | 13 | 50,449 |
| | VCP | 258 | 2,12,975 | +21.3 | 34.5 | 1.75 | 32.6 | +16.0 | −4.7 | 3.42 | 2.64 | −0.71 | 3.70 | 0.38 | 2.39 | 0.16 | 56.3 / 10.3 | 14 | 26,360 |
| | Darvas | 235 | −2,797 | −0.3 | −0.6 | 0.99 | 36.6 | +8.9 | −5.5 | 1.62 | 1.28 | −0.79 | 1.62 | −0.03 | 1.57 | −0.02 | 38.8 / 13.4 | 11 | 21,748 |

## 3. Per year: return and invested vs TRI

Return and TRI are from `run.json` `breakdowns.by_year`; invested is from `equity.csv`.

| Year | TRI % | B1 ret / inv `01a19039` | B2 ret / inv `01a1903c` | B3 ret / inv `01a1904d` | C1 ret / inv `01a19057` | C2 ret / inv `01a19064` | C3 ret / inv `01a19072` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2016 | +5.12 | −5.97 / 99.6 | +4.31 / 36.6 | +0.17 / 29.9 | −2.64 / 80.4 | −6.02 / 67.7 | −1.14 / 73.9 |
| 2017 | +37.65 | +76.38 / 99.5 | +54.71 / 85.2 | +13.38 / 68.3 | +66.96 / 94.6 | +67.34 / 92.0 | +56.66 / 92.3 |
| 2018 | −2.14 | −5.57 / 99.5 | −22.52 / 36.3 | −13.49 / 32.2 | −10.58 / 80.3 | −19.20 / 67.5 | −9.77 / 74.2 |
| 2019 | +8.97 | +14.58 / 99.5 | −6.51 / 23.4 | −8.15 / 18.6 | +7.96 / 76.9 | +4.14 / 61.7 | +5.35 / 68.1 |
| 2020 | +17.89 | +31.14 / 99.2 | +10.31 / 48.9 | −3.14 / 40.9 | +25.57 / 84.0 | +31.56 / 74.1 | +20.16 / 77.7 |
| 2021 | +31.60 | +77.38 / 99.0 | +57.86 / 83.9 | +8.88 / 66.7 | +69.74 / 94.4 | +72.25 / 92.0 | +54.39 / 90.4 |

Max DD within the year (`by_year`): B1 21.7 / 8.4 / 23.1 / 13.3 / 35.3 / 6.6. C1 17.2 / 6.7 / 20.5 / 10.5 /
27.9 / 8.1. The combos' smaller 2020 drawdown comes from the VCP sleeve being stopped out into cash
in the crash.

- Rotation alone beats the TRI in 4 of 6 years and loses in 2016 (−11.1 pts) and 2018 (−3.4 pts).
- VCP adds return only in the strong years (2017, 2021), when it deploys about 85%. In 2018-2019 it
  is 23-36% invested and loses. No combo fixes rotation's 2016/2018. C1 and C2 make 2018 worse.
- The 6-year B1 shows 2017 at +76.4%, against +68.9% for the 2017-only o1 run (`01a18fee`). The
  6-year run enters 2017 already holding the 2016 book, while o1 started from cash.

## 4. Blocking: refusals and rotation cash scaling

Setup-sleeve refusals are from `refusals.csv` (totals equal `run.json` `refusals`).
`refusals.csv` has no strategy column, so in C3 the split uses `setup_type`. VCP rows carry `vcp`
and their contraction fields; Darvas rows carry neither. In `trades.csv` this tag disagrees with the
playbook on 1 trade of each sleeve, so the split may be off by a few rows.

| Run | Sleeve | max_positions (slots) | size_zero_cash (cash) | size_below_min (size < 2% min) | size_zero_risk | max_chase | Total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B2 `01a1903c` | VCP alone | 93 | 181 | 225 | 0 | 1 | 500 |
| B3 `01a1904d` | Darvas alone | 28 | 63 | 86 | 0 | 1 | 178 |
| C1 `01a19057` | VCP 0.3 | 162 | 136 | 179 | 9 | 1 | 487 |
| C2 `01a19064` | VCP 0.5 | 143 | 155 | 195 | 0 | 1 | 494 |
| C3 `01a19072` | VCP 0.2 | 321 | 41 | 66 | 9 | 1 | 438 |
| | Darvas 0.2 | 44 | 71 | 76 | 0 | 1 | 192 |

- **The slot cap is per strategy** (`risk/decision._cap_reason` counts the bot's own positions).
  Each setup sleeve has its own 10 slots, and rotation holdings take none. At 0.2-0.3 weight each
  VCP position is small, so the 10 slots bind before cash does. VCP slot refusals: 93 alone, 162 in C1,
  321 in C3. Yet the sleeve still averages only about 4 positions. Its signals cluster: 10 slots
  are full in a breakout wave and empty in between. Refusals bunch in the strong stretches, and the
  45% average use comes from the quiet ones (2018-2019).
- **Rotation is never refused**: it bypasses the ledger caps by design. Its only constraint is cash
  scaling on rebalance days (`rebalances.csv` buy or top-up rows with reason `cash`). B1: 149 of 728
  buy orders scaled, on 14 of 72 rebalance days. C1: 123 of 698 on 11 days. C2: 55 of 353 on 9
  days. C3: 58 of 681 on 5 days. The setup sleeves do not starve the rotation. If anything, it is
  scaled less often in the combos.

## 5. Notes on the runs

- **Account keys are shared.** Risk, ladder, policy and conventions are account-wide in a portfolio
  file. The combos use p2's (risk 0.75%, flat ladder, open-risk cap 1, `p_max` 1 for VCP and in C3
  Darvas, daily entry bars, pessimistic ambiguous days, `rs` slot order). The rotation book reads
  none of the risk keys. `entry_bars: daily` changes only its 09:20 fill source on the 5-minute
  sessions (the store starts 2021-10-26), so for the last two months of 2021 the combos' rotation
  fills on the open-plus-median estimate, while B1 uses the 09:15 bar. Each strategy keeps its own
  `set` overrides. Rotation trade count is identical (328) in B1, C1 and C3.
- **C2 is a declared bundle** (weights 0.5/0.5 plus `top_n` 10), stated in its file header. A
  portfolio file has no `bundle` key and one-strategy sweeps cannot vary a co-sleeve, so it ran as
  a plain portfolio run.
- **Audits: all six `warn`, none fail.** All six warn on the data audit (`data_audit_warn`; `run.json`
  `data.verified` false). B2 also warns `top5_concentrated`. B3 and C3 warn `lookahead_hindsight`
  (Darvas's volume pace reads full-day volume on the daily estimate, which flatters Darvas) and B3
  `cost_share_high`.
- Darvas and VCP 2016-2021 are new trials of those families. Nothing was tuned, and no engine code
  was changed. The not_in_universe fix held: no run aborted.

## 6. What to test next (proposals only, not run)

1. **Put the setup sleeves' idle cash to work.** This is the first fix. About 55% of each VCP
   allotment sits in cash. Options:
   - (a) The ETF overlay (`overlay: {sleeve: liquid}`) on C1. It is one change, and it tests
     whether idle-cash yield closes the gap to B1.
   - (b) Overlapping weights, rotation 1.0 + VCP 0.3, if the engine allows weights summing above 1.
     Rotation then sizes on full equity, and VCP draws on rotation's cash only when it signals.
     This needs a check of how the rotation book scales when cash is short.
   - (c) Engine work: lend unused sleeve cash to the rotation at each rebalance. This is the
     owner's "replacement" idea seen from the other side.
2. **Wide exits on the winner (rotation).** Rotation captures 26% of MFE and trims winners every
   month (`reweight: true`: 475 trim orders in B1 `01a19039`). Test as single changes on B1:
   - `rotation.reweight=false`: let winners run instead of trimming back to equal weight;
   - `rotation.buffer_rank=60`: hold names longer before a rank sale.
3. **VCP exits.** It realises 0.51 R of 2.60 R MFE (B2 `01a1903c`). One change on B2: drop the
   20-day swing-low trail and keep the SMA50 close exit, or widen the trail to 40 days.
4. **Rotation's bad years (2016, 2018).** One change on B1: `rotation.market_filter=true` (the
   SMA200 regime it already carries, currently off). It is aimed at the 35% max DD in 2020 and the
   2018 drawdown.
5. **Drop Darvas** from further combos. It has no six-year edge (−0.01 R, profit factor 0.95 alone,
   −0.28 pts in C3), and its only positive year signal relied on the full-day-volume look-ahead.
