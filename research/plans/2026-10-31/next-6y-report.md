# Next-6y single changes, 2016-2021 in-sample: rotation exits and regime, VCP trail

Owner go 2026-10-31. Diagnostic runs on m3 at main `f1c8472` (run.json format 1.6), window 2016-01-01
to 2021-12-31 with the normal warm-up, NIFTY500_PIT, stocks only, ₹10L, database read-only. No
hold-out read (nothing after 2021). Benchmark: NIFTY 500 TRI, `benchmark_cagr_pct` **15.66%** in
every run. Each run is one change against its baseline, through the strategy's own config key; nothing
else was tuned and no engine code was changed. Short IDs are the first 8 characters of the run ID.

**Baselines reused.** B1 and B2 ran at `b3f057c` (combo-6y). The commits `b3f057c..f1c8472` change
reporting only, so B1/B2 are the baselines as they stand. Their format-1.6 metrics (invested, size,
zero-position days, CAGR per invested, profit factor, payoffs, MFE capture) are recomputed from their
`trades.csv` and `equity.csv` with the engine's own `standard.book_metrics`. The recompute matches the
written `run.json` metrics exactly on all five format-1.6 runs below, so B1/B2 are like-for-like.

| Run | Change (portfolio file, `set`) | Run ID |
| --- | --- | --- |
| B1 | G3 p5 rotation alone (`combo-6y/b1-rotation.yaml`) | `01a19039-9a2c-75f7-87eb-9c4dbdba02b3` |
| R1 | B1 + `rotation.reweight=false` (no monthly trim/top-up of holdings) | `01a1909b-b199-7149-b07e-1edf70446c82` |
| R2 | B1 + `rotation.buffer_rank=60` (from 40) | `01a1909c-c813-7534-bd4b-5ec058c8648a` |
| R3 | B1 + `rotation.market_filter=true` (NIFTY 500 close above SMA200, `rising_days` 0) | `01a1909e-3198-7255-ab87-686e48f28745` |
| R4 | rotation 1.0 + VCP 0.3 in one account | **not run: the engine refuses it** (§5) |
| B2 | G3 p2 old VCP alone (`combo-6y/b2-oldvcp.yaml`) | `01a1903c-9ff5-7335-a7ec-b5cd7a377ce4` |
| R5 | B2 with `exits[trailing_swing_low].enabled=false` (SMA50 close exit kept) | `01a1909f-47b1-74fb-825c-c77bbb8153ed` |
| R6 | B2 with `exits[trailing_swing_low].lookback_days=40` (from 20) | `01a190ab-a49b-7624-a894-640d9b8ee224` |

Files, logs, the stats script (`next6y_stats.py`) and its output (`stats.json`) are on m3 in
`/data/workspace/backtests/next-6y/`. Audits: all `warn`, none fail. Every run warns
`data_audit_warn`, as the baselines do. R5 and R6 also warn `top5_concentrated`, as B2 does.

## Verdict

- **Deployment is unchanged by every change except R3.** R1 and R2 stay fully invested, like B1:
  99.5 / 99.4% = 19.99 positions × 4.98 / 4.97%, with 0.07% zero-position days (`01a1909b`,
  `01a1909c`; B1 99.4%). R3's market filter takes the book to cash for **27.5% of sessions**, so it
  is 72.1% invested at 14.5 positions × 4.97% (`01a1909e`). R5 and R6 deploy the same as B2: 53.6%
  = 4.00 × 13.81%, with 17.2% zero-position days (`01a1909f`; B2 52.4%).
- **Rotation: no single change improves both return and drawdown.**
  - **R1 (no reweight):** best return of the three. CAGR **27.76 vs 26.88**, profit factor 3.44 vs
    3.02, MFE capture 0.36 vs 0.26. But max DD is **37.8 vs 35.3**, Calmar 0.74 vs 0.76, and 2018 is
    **−13.2% vs −5.6%** (`01a1909b`). It concentrates the book: the top 5 trades make 48.7% of P&L
    (B1 38.1%), and CAGR without them is 18.13 vs 19.86. Sharpe is 1.24 vs 1.22. This is a trade-off
    that rides 2017 and 2021, not a clean gain.
  - **R2 (buffer 60):** CAGR flat at 26.80, max DD worse at **39.6**, Calmar 0.68 (`01a1909c`).
    Holding longer adds 2021 (+100.1% vs +77.4%) and gives it back in 2018-2019. Reject.
  - **R3 (market filter):** CAGR **20.36** (−6.5 pts), max DD 34.5 (−0.8), Calmar 0.59, and the
    longest drawdown is 723 sessions vs 356 (`01a1909e`). It does what it is meant to in 2020: the
    book went to cash on 2020-03-02, and 2020's in-year DD is **7.6% vs 35.3%**. But it whipsaws:
    filter sales on 7 days (2017-01, 2018-04/07/10, 2019-08, 2020-03), cash in the 2016 rally start,
    and 2018 at −22.6% vs −5.6%. Per unit invested it is the best rotation (CAGR per invested 28.25
    vs 27.05), so the loss is idle time, not worse picks. Reject as is.
- **VCP: dropping the swing-low trail (R5) improves on B2 in both return and drawdown, modestly.**
  CAGR **14.01 vs 12.57**, max DD **32.9 vs 33.7**, Sharpe 0.98 vs 0.91, Calmar 0.43 vs 0.37,
  exp R 0.58 vs 0.51, MFE capture 0.21 vs 0.20 (`01a1909f`). The gain is almost all 2021 (+69.6% vs
  +57.9%). It is still below TRI (15.66), and still concentrated: 61.7% of P&L in the top 5 trades,
  6.49 without them.
- **R6 is R5.** The 40-day trail is configured and enabled in R6's `config.json`, but it never fired.
  The SMA50 close exit always exits first. R6's `trades.csv` and `equity.csv` are row-for-row identical
  to R5's, apart from the run ID. In B2 the 20-day trail fired on 19 of 230 trades (`01a1903c`). At 40
  days it does nothing, so "widen to 40" and "drop it" are the same strategy.
- **Stackability.** None of R1-R3 is a clean improvement, so no rotation stack is clearly worth
  running. The one candidate is R1 + R3 (proposal only, not run), because their effects run in
  opposite directions. R1 adds return and concentration, and makes 2018 worse. R3 cuts the 2020 crash
  but costs 6.5 pts of CAGR in whipsaw. R2 should not be stacked: it adds drawdown and no return.
  R5 is independent of the rotation, and it is the VCP config to carry into any later combo.
- **R4 cannot run without engine work** (§5). The engine refuses weights summing above 1. Lifting
  that check alone would not give the borrowing behaviour either. Two more engine changes are needed.

## 1. Deployment and headline (lead table)

Sources: **R** = `run.json` `metrics` for R1-R6. **C** = the same metrics recomputed with
`standard.book_metrics` for B1/B2 (identical to `run.json` where both exist). Size = mean over sessions
with a position of value ÷ equity ÷ positions.

| Run | Invested % | Avg positions | Avg size % | Zero-pos days % | CAGR % | TRI CAGR % | Max DD % | Sharpe | Sortino | Calmar | CAGR per invested | Longest DD (sessions) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 `01a19039` C | 99.38 | 19.99 | 4.97 | 0.07 | 26.88 | 15.66 | 35.34 | 1.22 | 1.67 | 0.76 | 27.05 | 356 (2018-08-31 → 2020-02-12) |
| R1 no reweight `01a1909b` | 99.52 | 19.99 | 4.98 | 0.07 | **27.76** | 15.66 | 37.77 | 1.24 | 1.69 | 0.74 | 27.90 | 501 (2018-08-31 → 2020-09-14) |
| R2 buffer 60 `01a1909c` | 99.39 | 19.99 | 4.97 | 0.07 | 26.80 | 15.66 | 39.62 | 1.23 | 1.69 | 0.68 | 26.96 | 502 (2018-08-31 → 2020-09-15) |
| R3 market filter `01a1909e` | 72.08 | 14.50 | 4.97 | 27.46 | 20.36 | 15.66 | **34.53** | 1.19 | 1.66 | 0.59 | **28.25** | 723 (2018-01-23 → 2020-12-28) |
| B2 `01a1903c` C | 52.44 | 4.06 | 13.36 | 17.23 | 12.57 | 15.66 | 33.65 | 0.91 | 1.25 | 0.37 | 23.98 | 816 (2018-01-24 → 2021-05-18) |
| R5 no trail `01a1909f` | 53.56 | 4.00 | 13.81 | 17.16 | **14.01** | 15.66 | **32.86** | 0.98 | 1.37 | 0.43 | 26.16 | 813 (2018-01-24 → 2021-05-12) |
| R6 trail 40 `01a190ab` | 53.56 | 4.00 | 13.81 | 17.16 | 14.01 | 15.66 | 32.86 | 0.98 | 1.37 | 0.43 | 26.16 | 813 (2018-01-24 → 2021-05-12) |

Every longest drawdown above recovered within the window. B2's size here is 13.36%. The combo report
gave 12.93%, from Σ invested ÷ Σ positions; the engine's per-session mean is used here for like-for-like.

## 2. Trade efficiency

Trades are whole trades (a rotation trade's trim legs summed, as `run.json` counts them). The
rotation has no stop: its R is net P&L over the shares bought at the entry price (return on cost), so
its R columns are fractions, not risk units. Payoff = avg win ÷ |avg loss|. MFE capture = Σ R ÷ Σ MFE R.
Planned R:R is n/a for all: neither strategy has a target (`planned_rr` null).

| Run | Trades | Profit factor | Win % | Avg win % | Avg loss % | Payoff % | Avg win R | Avg loss R | Payoff R | Exp R | Avg MFE R | MFE capture | Hold win / loss (sessions) | Max consec losses | CAGR ex top-5 % | Top-5 share of P&L % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 `01a19039` C | 328 | 3.02 | 51.2 | +28.4 | −11.3 | 2.53 | 0.28 | −0.11 | 2.53 | 0.091 | 0.35 | 0.26 | 124.2 / 55.2 | 9 | 19.86 | 38.1 |
| R1 `01a1909b` | 328 | 3.44 | 50.3 | +37.2 | −12.0 | 3.09 | 0.37 | −0.12 | 3.09 | 0.127 | 0.35 | 0.36 | 122.6 / 58.2 | 9 | 18.13 | 48.7 |
| R2 `01a1909c` | 256 | 3.46 | 55.9 | +31.9 | −13.3 | 2.40 | 0.32 | −0.13 | 2.40 | 0.120 | 0.43 | 0.28 | 152.6 / 69.7 | 9 | 19.98 | 37.2 |
| R3 `01a1909e` | 331 | 2.68 | 48.9 | +25.0 | −9.4 | 2.65 | 0.25 | −0.09 | 2.65 | 0.074 | 0.29 | 0.26 | 86.2 / 44.8 | 9 | 13.95 | 41.7 |
| B2 `01a1903c` C | 230 | 2.04 | 33.0 | +18.0 | −4.4 | 4.10 | 2.92 | −0.68 | 4.31 | 0.511 | 2.60 | 0.20 | 57.9 / 10.6 | 11 | 5.92 | 60.2 |
| R5 `01a1909f` | 214 | 2.28 | 30.8 | +20.7 | −4.3 | 4.82 | 3.36 | −0.66 | 5.14 | 0.585 | 2.75 | 0.21 | 64.3 / 11.5 | 12 | 6.49 | 61.7 |
| R6 `01a190ab` | 214 | 2.28 | 30.8 | +20.7 | −4.3 | 4.82 | 3.36 | −0.66 | 5.14 | 0.585 | 2.75 | 0.21 | 64.3 / 11.5 | 12 | 6.49 | 61.7 |

R1's R is not the same quantity as B1's. B1's trims sell part of a winner at a profit, and its
top-ups buy more at higher prices, both of which pull its R toward zero. R1 has neither. Compare the
rotation runs on profit factor, % payoffs and CAGR, not on R.

VCP exits (`trades.csv` `exit_reason`): B2 had SMA50 close 167, initial stop 42, swing-low trail 19,
demerger 1 and period end 1 (`01a1903c`). R5 and R6 had SMA50 close 175, initial stop 37, demerger 1
and period end 1 (`01a1909f`, `01a190ab`). Without the trail, VCP holds winners about 6 sessions
longer, avg win R rises from 2.92 to 3.36, and it takes 16 fewer trades. Refusals: B2 had slot 93,
`size_zero_cash` 181, `size_below_min` 225 and max chase 1. R5 had slot 27, 182, 322 and 1. Longer
holds keep cash tied up, so more late signals size under the 2% minimum instead of hitting the slot cap.

## 3. Rotation turnover (R1-R3)

From `rebalances.csv` (orders that traded, qty > 0) and `run.json` `fees`. "Cash-scaled" = buy or
top-up rows the cash cut down or out (reason `cash`). Traded value is the sum of order values in ₹ lakh.

| Run | Rebalance days | Buys | Top-ups | Trims | Sales (out of buffer / not eligible / market filter) | Cash-scaled buys (days) | Traded ₹L | Trimmed ₹L | Fees ₹ | Cost share % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 `01a19039` | 72 | 328 | 395 | 475 | 308 (231 / 77 / 0) | 149 (14) | 597.6 | 47.2 | 86,172 | 2.64 |
| R1 `01a1909b` | 72 | 328 | 0 | 0 | 308 (231 / 77 / 0) | 279 (58) | 459.8 | 0 | 62,327 | 1.83 |
| R2 `01a1909c` | 72 | 256 | 449 | 480 | 236 (174 / 62 / 0) | 140 (14) | 455.2 | 44.4 | 68,859 | 2.13 |
| R3 `01a1909e` | 59 | 331 | 266 | 293 | 311 (149 / 42 / 120) | 131 (12) | 490.4 | 27.2 | 69,806 | 3.31 |

- R1 trades the same 328 names on the same days as B1. Only the sizing differs. Dropping trims and
  top-ups cuts fees by 28% (₹23,845). A new buy then gets only the cash a sale freed, so 279 buys are
  cash-scaled, on 58 of 72 rebalance days: each new name enters below its equal-weight share, while
  the winners stay oversized. That is where its extra concentration and 2018 loss come from.
- R2 makes 72 fewer round trips but keeps the monthly trim and top-up churn (929 rows vs 870).
- R3 has 59 rebalance days with a row. In the other 13 month-ends the gate was off and the book was
  already in cash. 120 of its sales are filter sales.

## 4. Per year: return / invested vs TRI

Return and TRI from `run.json` `breakdowns.by_year`; invested is the mean of `equity.csv` `invested_pct`.
In-year max DD in brackets.

| Year | TRI % | B1 `01a19039` | R1 `01a1909b` | R2 `01a1909c` | R3 `01a1909e` | B2 `01a1903c` | R5 = R6 `01a1909f` / `01a190ab` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2016 | +5.12 | −5.97 / 99.6 (21.7) | −5.77 / 99.8 (22.1) | −8.10 / 99.5 (22.5) | +2.80 / 67.7 (22.5) | +4.31 / 36.6 (7.2) | +4.31 / 36.6 (7.2) |
| 2017 | +37.65 | +76.38 / 99.5 (8.4) | +81.04 / 99.7 (8.7) | +83.36 / 99.4 (7.9) | +58.08 / 91.0 (8.4) | +54.71 / 85.2 (4.8) | +54.56 / 85.4 (5.6) |
| 2018 | −2.14 | −5.57 / 99.5 (23.1) | −13.24 / 99.7 (25.1) | −12.21 / 99.5 (22.5) | −22.62 / 57.5 (25.9) | −22.52 / 36.3 (31.5) | −21.17 / 41.7 (31.7) |
| 2019 | +8.97 | +14.58 / 99.5 (13.3) | +15.10 / 99.7 (13.1) | +6.99 / 99.6 (14.0) | −1.06 / 58.4 (13.6) | −6.51 / 23.4 (8.6) | −7.18 / 23.5 (9.1) |
| 2020 | +17.89 | +31.14 / 99.2 (35.3) | +36.55 / 99.4 (36.8) | +31.22 / 99.3 (35.4) | +37.87 / 58.8 (7.6) | +10.31 / 48.9 (11.2) | +9.78 / 49.0 (11.5) |
| 2021 | +31.60 | +77.38 / 99.0 (6.6) | +87.04 / 98.9 (7.2) | +100.15 / 99.0 (7.5) | +77.31 / 98.9 (6.6) | +57.86 / 83.9 (12.6) | +69.62 / 84.8 (10.6) |

- Against TRI: B1 and R1 beat it in 4 of 6 years and miss in 2016 and 2018. R2 beats it in 3 and
  also misses 2019 (+6.99 vs +8.97). R3 beats it in 3
  (2017, 2020, 2021) and misses in 2016, 2018 and 2019. R5 beats it in 2 (2017, 2021), the same as B2.
- R1's gains are 2017, 2020 and 2021; its loss is 2018 (−7.7 pts vs B1). R2's are 2017 and 2021; its
  losses are 2016, 2018 and 2019.
- R3's 2020 is its one clear win: +37.9% at 58.8% invested with a 7.6% DD, against B1's +31.1% with a
  35.3% DD. Its 2018 is the worst rotation year here: it sold in April, July and October and bought
  back between.
- R5's gain over B2 is 2021 (+11.8 pts) and 2018 (+1.4 pts). It gives up 0.5-0.7 pts in 2019 and 2020.

## 5. R4: rotation 1.0 + VCP 0.3 in one account (not run)

Checked in the code at `f1c8472`. The engine does not allow it, and lifting the refusal alone would
not give the intended behaviour.

1. **Refused at spec time.** `backtest/spec.py` `RunSpec.__post_init__` (the co-sleeve check, line ~454):
   `if not all(0 < w <= cap for w in weights) or sum(weights) > 1: raise BacktestError("backtest_bad_sleeve_weight")`.
   With the policy's `cluster_cap` 1.00 each weight passes alone, but 1.3 in all is refused before the run starts.
2. **The allocator would undo the overlap anyway.** Each night `backtest/loop.py` `_Sleeve.allocate`
   runs the live allocator (`engine/portfolio/allocator.py`). Its `_capped` holds each cluster to
   `cluster_cap` and then the whole book to 1 (`_scale_down(weights, Decimal(1))`, proportional,
   rounded down). Rotation 1.0 + VCP 0.3 would come out as about **0.769 + 0.230**, which is C1's
   split again (0.7/0.3), not borrowing.
3. **Cash order: the rotation spends first and VCP gets what is left.** The rotation rebalances at
   09:20 on the month's first session (`loop._rotate_book`). It sizes each name at sleeve capital ÷
   `top_n` (`engine/rotation.order_diff`) and pays from the account's free cash
   (`Market.cash` = `_free_cash()` plus any overlay credit). When the cash cannot pay every buy,
   `RotationBook._buy_all` scales them all down by `rotation.buy_share(outlay, cash)` (cash ÷ outlay,
   whole shares, rounded down) and then cuts each to what is left (`fills.affordable`). It never
   sells anything to make room. A VCP entry is sized by `evaluate_signal` on its sleeve's allocation:
   risk 0.75% of the sleeve's capital, capped by `p_max`, then floored to the account's free cash
   (`free_cash=self._free_cash()`). It is refused `size_zero_cash` or `size_below_min` when that cash
   is short. At rotation weight 1.0 the account is about 99.4% invested after each rebalance
   (B1 `01a19039`), so between rebalances VCP would see about 0.6% free cash plus whatever the
   rotation's own sales free. At the next rebalance the rotation would size on full equity and be
   cash-scaled by whatever VCP holds. VCP would be starved, not funded.

**What the engine change would need** (proposal; not made):

- `backtest/spec.py` `RunSpec.__post_init__`: accept a weight sum above 1 only when declared, through a
  new run convention such as `overlap: true` recorded in `recorded_conventions`, and only when exactly one
  leg is a rotation. Refuse everything else as today.
- `engine/portfolio/allocator.py` `_capped` (or `backtest/loop.py` `_Sleeve.allocate` passing a flag):
  under `overlap`, leave out the rotation leg when holding the book to 1, so the setup sleeves keep
  their own weight and the rotation keeps 1.0. The live allocator is shared with live sizing, so this
  should be a backtest-only flag until the owner decides it for live.
- Priority and funding, which is the real behaviour change. Pick one:
  - (a) **Setup first, rotation funds it.** When a setup entry's size exceeds free cash, sell rotation
    holdings to cover the shortfall, at the same fill rules as a rotation sale. The ETF overlay already
    does this for its sleeve (`overlay.fund(day, funded, -free_cash)` / `credit_for`), and that is the
    model to copy. A new `RotationBook.fund(day, amount, market)` would sell pro rata across holdings,
    or the lowest-ranked first, and `_free_cash` for setup entries would include it as credit.
  - (b) **Rotation sizes on the residual.** In `loop._rotate_book`, size the book on `equity ×
    rotation weight − value of the setup sleeves' open positions` (and their pending entries), so it
    buys back only the cash the setups are not using. This alone leaves VCP short between rebalances,
    so it needs (a) or a cash reserve as well.
- The rebalance and result files would need a reason for a funding sale (for example
  `rotation_funding`) so turnover stays auditable. `rotation_live.py` would need the same rule before
  shadow could follow it.

## 6. Next steps (proposals only, nothing run)

1. **Carry R5's VCP exits (SMA50 close, no swing-low trail) as VCP's default** in any further combo.
   It beats B2 on CAGR, DD, Sharpe and Calmar with the same deployment (`01a1909f`). Treat it as one
   more in-sample trial, not a validated gain. Retire the 40-day trail variant: it is inert (`01a190ab`).
2. **Rotation stack, diagnostic only: R1 + R3** (`reweight=false`, `market_filter=true`) on B1. It
   tests whether the filter's crash protection offsets R1's extra concentration and 2018 loss. Do not
   stack R2.
3. **A filter that whipsaws less** (one change each on B1): `regime.params.rising_days` > 0 so the
   SMA200 must also be rising, or a slower check (`rotation.rebalance` stays monthly; only the gate
   changes). The 2020 exit worked. The 2018-2019 round trips (5 filter-sale days) are the cost.
4. **R4 needs the engine work in §5** before it can be tested. Option (a), the rotation funding setup
   entries, is the one that matches "VCP borrows the rotation's idle cash". Until then the closest
   runnable test is the combo report's proposal 1(a): the ETF overlay on C1.
