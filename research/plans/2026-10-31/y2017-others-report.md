# 2017 alone: the other strategies vs NIFTY 500 TRI

Owner, 2026-10-31. Each strategy was run alone, 2017-01-01 to 2017-12-31 with the normal warm-up, on NIFTY500_PIT,
stocks only, ₹10L, on m3 at main `bd503e9`, with the database read-only. Benchmark: NIFTY 500 TRI **+37.65%** (owner's
figure). The runs' own `benchmark_tri` column gives +37.27% from the 2017-01-02 close, and `run.json` gives a benchmark
CAGR of 37.93. Every number below comes from the run ID in its row or section heading.

## Verdict

- **Only the momentum rotation both deploys capital and has broad edge in 2017.** It ended **+68.9%** against
  +37.65% TRI, 98.7% invested (19.8 positions × 5.0%), with a max DD of 8.4%. It is still +32.8% CAGR without its top 5
  trades (`01a18fee`).
- **Old VCP deploys well. Its edge is one trade.** It was 84.9% invested (5.7 positions × 14.9%) and ended +55.3%, but
  VAKRANGEE alone added +40.9 pts of equity. Without it the year is +14.3%, below the TRI. CAGR without the top 5 trades
  is −5.3 (`01a19002`). The same config was 53% invested over 2022-24. In 2017 it was not idle: cash was its binding
  limit (122 cash or size refusals). The 2-7% idle-capital problem belongs to the book setups, not to VCP as such.
- **Darvas box and EMA pullback deploy 68-84% and still trail the TRI by 21-25 pts.** Darvas: +13.0%, 0.31 R
  (`01a19012`). Pullback: +16.3%, 0.17 R, 28.7% win (`01a18ffa`). Both are positive only through one or two trades
  (CAGR without the top 5 is −6.4 and −16.5). Both exit far too early: realised 0.31 and 0.17 R against an MFE of 1.75
  and 2.21 R. The pullback's 4.4% median stop is hit on 46 of 101 trades.
- **RSI-2 reversion has no edge here.** It ended **−20.8%** in a +37.65% year with a max DD of 24.4% (`01a19018`).
  Its 599 trades paid ₹1.09L in fees (10.9% of capital), and it lost about 10% even before fees. It was only 43%
  invested: the wide 3×ATR stop sizes each position at 7.5%.
- **Combining them.** The rotation is the core that deploys capital. VCP and Darvas are breakout scanners that
  occasionally catch a convex winner the monthly rotation holds late or never. In this year they add lumpy upside, not
  steady edge. The EMA pullback and RSI-2 should not get capital on this evidence. The three combined runs proposed are
  at the end. Not run.
- **Engine defect found (blocks every combined run).** A signal whose entry day falls after the stock left the PIT
  universe aborts the whole run with `TradeError: not_in_universe`: `entries._entry_policy` raises it and
  `loop._enter` does not catch it. It aborted o2 (`01a18ff0`), o3 (`01a18ff5`) and o5 (`01a18fff`). Those three were
  rerun with a runtime patch that skips such an entry (below). The fix is for the orchestrator to brief; I changed no
  engine code.

## Cross-strategy table

Invested ≈ positions × size holds exactly by construction (size = Σ invested / Σ positions over the 248 sessions).

| Strategy | Run | Invested % | Positions | Size % | Zero-pos days % | 2017 % | vs TRI (pts) | Trades | Win % | Exp R | Max DD % | Top-30 caught | Limited by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 Rotation (G3 p5) | `01a18fee` | 98.7 | 19.83 | 4.98 | 0.4 | +68.9 | +31.3 | 69 | 65.2 | 0.16¹ | 8.4 | 15/30 | design (top_n 20 × 5%) |
| 2 Old VCP (G3 p2) | `01a19002` | 84.9 | 5.71 | 14.87 | 2.8 | +55.3 | +17.7 | 50 | 40.0 | 1.38 | 4.8 | 2/30 | cash (size ~15%) |
| 3 Darvas box | `01a19012` | 67.9 | 5.90 | 11.50 | 7.7 | +13.0 | −24.6 | 60 | 45.0 | 0.31 | 8.2 | 5/30 | signals, then cash |
| 4 EMA pullback | `01a18ffa` | 83.9 | 5.53 | 15.16 | 7.7 | +16.3 | −21.3 | 101 | 28.7 | 0.17 | 15.3 | 19/30 | cash (size ~15%) |
| 5 RSI-2 reversion | `01a19018` | 43.3 | 5.80 | 7.47 | 6.5 | −20.8 | −58.5 | 599 | 55.6 | −0.05 | 24.4 | 21/30 | size (3×ATR stop) |

¹ The rotation has no stop, so its "R" is the trade's return as a fraction (0.16 = +16% per trade on average).

| Strategy | Return without its top trade | CAGR without its top 5 trades | Fees ₹ | Realised R vs MFE R | Median rise after exit (40 sessions) | Exits followed by ≥20% more |
| --- | --- | --- | --- | --- | --- | --- |
| Rotation `01a18fee` | +57.3% (RAIN) | +32.8 | 13,551 | 0.16 vs 0.35 | 9.7% | 26% |
| Old VCP `01a19002` | +14.3% (VAKRANGEE) | −5.3 | 17,531 | 1.38 vs 2.79 | 9.8% | 18% |
| Darvas `01a19012` | +7.4% (VAKRANGEE) | −6.4 | 16,920 | 0.31 vs 1.75 | 12.6% | 27% |
| Pullback `01a18ffa` | +3.9% (ESCORTS) | −16.5 | 40,226 | 0.17 vs 2.21 | 16.1% | 31% |
| RSI-2 `01a19018` | −21.8% (STAR) | −24.9 | 108,754 | −0.05 vs 0.23 | 12.3% | 28% |

## What was run

The portfolio files, runner scripts and logs are on m3 in `/data/workspace/backtests/y2017-others/`. The analysis
scripts are also there.

| # | File | Strategy version | Settings |
| --- | --- | --- | --- |
| o1 | `o1-rotation.yaml` | momentum-rotation v1 `c7d55ebe` | G3 `p5-rotation.yaml` without its `overlay: {sleeve: liquid}` (stocks only); weight 1; repo defaults (5m entry bars, `time` slot order, optimistic ambiguous days) |
| o2 | `o2-oldvcp.yaml` | stage2-contraction-breakout v2 `aac4fda7` | G3 `p2-vcp.yaml` unchanged except the window: the 8 `set`s (vcp contractions [2,6], dryup 1.0, depth_ratio_max 0.9, SMA50 close exit, 20-day swing-low trail, no time stop, partial or step trail), risk 0.75%, flat ladder, open-risk cap 1, `p_max` 1, daily entry bars, pessimistic, `rs` slot order |
| o3 | `o3-darvas.yaml` | darvas-box-breakout v1 `3b44c25e` (the seed) | the seed unchanged (its universe, regime SMA50 rising 10, `darvas_box` 252/3/60/8%, break of the box top on 1.5× volume pace, stop under the box low capped at 10%, 10-day swing-low trail), on p2's account settings: risk 0.75%, flat ladder, open-risk cap 1, `p_max.darvas-box-breakout=1`, weight 1, daily entry bars, pessimistic, `rs` |
| o4 | `o4-pullback.yaml` | trend-pullback-ema v1 `7bf435ff` (the seed) | the seed unchanged (RS ≥ 80, SMA50 > SMA200 both rising, `ema_pullback` 10/20 EMA, break of the pullback high, stop under the pullback low capped at 8%, breakeven at 2R, 10-day swing-low trail, SMA50 close exit), on p2's account settings as o3 |
| o5 | `o5-rsi2.yaml` | rsi2-uptrend-reversion v1 `bae9bc26` (the seed) | the seed unchanged (close > SMA200, RSI(2) < 10, entry back above the signal close, 3×ATR(14) stop, exit on a close above SMA5 or after 10 sessions, regime SMA200 rising 21), on p2's account settings as o3 |

- **Detector sourcing.** All three detectors have a registered seed version and none has an earlier run, sweep or
  `config.json`. I searched the repo, `algotradingdata`, the m3 g3-inputs and every run folder's `config.json`. So I
  used each seed as written: its own universe, regime and exits. Sizing is p2's, so it matches the old-VCP run. The
  seeds' policy footing (`p_max` 20%, base weight 0) would have run at 20% caps on a 0.5 research weight. p2 ran S1 at
  base weight 1.0 with `p_max` 1, so o3-o5 set the same. Nothing was tuned.
- **Policy.** Risk policy v3 is in force for all five runs: 10 open positions, 4 entries a day, a 2% minimum position,
  and a 1% ADV cap.
- **2017 has no 5-minute bars.** Every entry is decided on the daily estimate. Darvas's 1.5× volume pace therefore
  reads full-day volume, a known look-ahead. Its run audit warns `lookahead_hindsight` (254 `volume_pace_full_day`
  reads), which flatters Darvas.
- **Audits.** Every run's audit status is `warn`: the data audit warned, and o1-o4 have a `top5_concentrated`
  concentration warning (o2-o4 also `edge_in_top5`). No check failed.

### Deviation: the not_in_universe abort and the patched reruns

o2, o3 and o5 aborted at their first such entry (failed runs `01a18ff0`, `01a18ff5`, `01a18fff`). I could not change
the engine, so `run_skip_left_universe.py` runs the normal `python -m app.hat.backtest` command line with one runtime
patch. It catches that one `TradeError` in `loop._Run._enter` and skips the entry, which is what HAT-PORT-023 already
requires: leaving the universe stops new entries. `open_entry` raises before any write. Skipped entries:

- o2 `01a19002`: 2, both on 2017-12-29.
- o3 `01a19012`: 1, on 2017-12-29.
- o5 `01a19018`: 9. Eight are on 2017-12-29, the window's last session, which is presumably the reconstitution date.
  One is on 2017-05-25.

The effect on results is negligible, since entries on the last session are closed at period end. The run folders
record commit `bd503e9`, not the patch, so a `--rerun` of them aborts the same way. The engine fix belongs in a
builder brief: catch `not_in_universe` in `_enter` and record it as a skip or refusal.

### How the analysis was made

`y2017_others.py --portfolio P --run-id ID --out DIR` reads the run folder. It then loads the market for 2017 plus 40
sessions of 2018, both for the top-30 and for the move left after each exit. Finally it replays the run in memory
through `bt_truncation`'s spec and loop with an observer. For the setup strategies the observer records each night's
first failing gate (`scan._stopped_gate`) for the top-30 names. For the rotation it records each month-end's rank and
target. The replay must reproduce the run's final equity, and all five did. `y2017_render.py` prints the tables.

- **Top-30.** The 30 largest moves among the 553 stocks that were NIFTY 500 PIT members in 2017. A move is the
  largest low-to-later-high run-up (adjusted) over the sessions of 2017 the stock was a member.
- **Caught.** At least one trade in the stock in 2017.
- **Blocking rule.** For a missed name, the gate it most often failed first across the scanned (regime-on) nights.
  Where its setup passed, the signal's refusal from `signals.csv`/`refusals.csv`, or "trigger never fired".
- **The shared universe stage removes 5 of the 30 for every strategy.**
  - RCOM, GVKPIL, JPASSOCIAT and HFCL trade under ₹50 (`min_price`) all year.
  - RKFORGE's 20-day turnover is under ₹10 cr all year (`min_turnover`).
  - FLFL, DCMSHRIRAM, SUNTECK, SHILPI and MINDAIND fail turnover on 73-90% of days.

## Per strategy

Each section: the deployment identity, the results, the shortfall, then the top-30 table.

### Rotation (p5) — run `01a18fee-a0cd-7722-8994-5a6a580c9a3a`

- Invested 98.7% avg; 19.83 positions × 4.98% avg size = 98.7%; zero-position days 0.4%; most held 20.
- No stop (rotation); median position at entry 5.3% of equity.
- 2017 +68.9% vs TRI +37.65% (+31.3 pts); 69 trades, win 65.2%, expectancy 0.16 R, max DD 8.4%.
- Best trade RAIN 2017-03-01→2017-12-29: stock +188.9%, equity +10.25% (position 5.4%). Largest equity effect RAIN +10.25% (stock +188.9%).
- Exits: realised 0.16 R vs MFE 0.35 R avg; after exit the stock rose a median 9.7% more within 40 sessions, ≥20% more after 26% of exits.
- Refusals: {}; funnel {}, regime-off nights 0.
- **Where it falls short.** It does not fall short of the TRI.
  - Its limit is the monthly cadence. Realised return per trade is 0.16 against an MFE of 0.35, and after a
    rotation_out the stock rose a median 9.7% more, ≥20% more after 26% of exits.
  - Most of its missed top-30 names were ranked 21-25 at month ends (FLFL, JINDALSTEL, DCMSHRIRAM, JMFINANCIL), or
    were inside the top 20 on only one or two month ends while held names inside the 40-rank buffer kept their slots
    (KOLTEPATIL, EDELWEISS, JAICORPLTD).
  - Four were never ranked because the universe stage refuses them (under ₹50 or under ₹10 cr turnover).
  - The 20 equal slots also cap the convex winners: RAIN went +189% and added only +10.3% to equity.

Top-30 caught 15/30:

| # | Stock | Move % | Low → high | Caught / blocking rule |
| --- | --- | --- | --- | --- |
| 1 | RAIN | 652 | 01-06 → 11-13 | caught: 1 trade(s), stock +189%, equity +10.25%, first entry 2017-03-01 |
| 2 | BOMDYEING | 530 | 01-02 → 12-20 | caught: 1 trade(s), stock +106%, equity +5.49%, first entry 2017-09-01 |
| 3 | AVANTIFEED | 507 | 01-02 → 11-13 | caught: 1 trade(s), stock +67%, equity +3.51%, first entry 2017-06-01 |
| 4 | KOLTEPATIL | 382 | 01-02 → 11-29 | missed: best rank 15 (top_n 20) at month ends; in top 20 on 1 of 12 (book full: held names kept within buffer 40) |
| 5 | ADANITRANS | 340 | 01-02 → 12-22 | caught: 2 trade(s), stock +20%, equity +0.99%, first entry 2017-06-01 |
| 6 | RCOM | 318 | 11-15 → 12-29 | missed: never ranked (0/12 nights in the universe stage; min_bars 240 or universe) |
| 7 | FVIL | 302 | 01-02 → 12-27 | caught: 1 trade(s), stock +42%, equity +2.39%, first entry 2017-09-01 |
| 8 | SUNTECK | 300 | 01-02 → 12-19 | caught: 1 trade(s), stock +23%, equity +1.13%, first entry 2017-09-01 |
| 9 | GVKPIL | 292 | 05-25 → 11-01 | missed: never ranked (0/12 nights in the universe stage; min_bars 240 or universe) |
| 10 | JPASSOCIAT | 285 | 01-03 → 07-28 | missed: never ranked (0/12 nights in the universe stage; min_bars 240 or universe) |
| 11 | IBREALEST | 276 | 01-02 → 08-07 | caught: 1 trade(s), stock +0%, equity -0.01%, first entry 2017-08-01 |
| 12 | BBTC | 240 | 01-02 → 12-29 | caught: 1 trade(s), stock +2%, equity +0.07%, first entry 2017-11-01 |
| 13 | VIPIND | 238 | 01-02 → 11-28 | caught: 1 trade(s), stock -3%, equity -0.16%, first entry 2017-12-01 |
| 14 | EDELWEISS | 225 | 01-09 → 11-03 | missed: best rank 18 (top_n 20) at month ends; in top 20 on 2 of 12 (book full: held names kept within buffer 40) |
| 15 | VAKRANGEE | 223 | 01-06 → 12-27 | caught: 1 trade(s), stock +153%, equity +8.24%, first entry 2017-01-02 |
| 16 | FLFL | 214 | 01-02 → 11-24 | missed: best rank 25 (top_n 20) at month ends; in top 20 on 0 of 12 |
| 17 | MINDAIND | 212 | 04-13 → 12-21 | caught: 2 trade(s), stock +6%, equity +0.28%, first entry 2017-08-01 |
| 18 | MOTILALOFS | 209 | 01-06 → 12-22 | caught: 1 trade(s), stock +41%, equity +2.30%, first entry 2017-05-02 |
| 19 | DBL | 205 | 03-31 → 12-27 | caught: 1 trade(s), stock +59%, equity +3.12%, first entry 2017-09-01 |
| 20 | RKFORGE | 204 | 01-02 → 12-19 | missed: never ranked (0/12 nights in the universe stage; min_bars 240 or universe) |
| 21 | HFCL | 203 | 06-30 → 09-18 | missed: never ranked (0/12 nights in the universe stage; min_bars 240 or universe) |
| 22 | JAICORPLTD | 201 | 02-01 → 11-27 | missed: best rank 18 (top_n 20) at month ends; in top 20 on 1 of 12 (book full: held names kept within buffer 40) |
| 23 | JINDALSTEL | 200 | 01-02 → 12-29 | missed: best rank 25 (top_n 20) at month ends; in top 20 on 0 of 12 |
| 24 | DELTACORP | 198 | 01-02 → 12-26 | missed: best rank 47 (top_n 20) at month ends; in top 20 on 0 of 12 |
| 25 | DCMSHRIRAM | 198 | 01-02 → 12-19 | missed: best rank 21 (top_n 20) at month ends; in top 20 on 0 of 12 |
| 26 | RADICO | 190 | 04-19 → 11-22 | caught: 1 trade(s), stock +2%, equity +0.08%, first entry 2017-12-01 |
| 27 | JMFINANCIL | 189 | 01-02 → 10-16 | missed: best rank 22 (top_n 20) at month ends; in top 20 on 0 of 12 |
| 28 | SHILPI | 189 | 06-15 → 07-14 | missed: best rank 206 (top_n 20) at month ends; in top 20 on 0 of 12 |
| 29 | KEC | 184 | 01-02 → 12-22 | caught: 1 trade(s), stock +30%, equity +1.58%, first entry 2017-05-02 |
| 30 | 8KMILES | 182 | 09-27 → 11-29 | missed: best rank 92 (top_n 20) at month ends; in top 20 on 0 of 12 |

### Old VCP (p2) — run `01a19002-880a-717b-8d4d-5660d3a646b2`

- Invested 84.9% avg; 5.71 positions × 14.87% avg size = 84.9%; zero-position days 2.8%; most held 8.
- Median stop 5.9%, median position at entry 11.5% of equity.
- 2017 +55.3% vs TRI +37.65% (+17.7 pts); 50 trades, win 40.0%, expectancy 1.38 R, max DD 4.8%.
- Best trade VAKRANGEE 2017-01-12→2017-12-29: stock +201.8%, equity +40.87% (position 20.3%). Largest equity effect VAKRANGEE +40.87% (stock +201.8%).
- Exits: realised 1.38 R vs MFE 2.79 R avg; after exit the stock rose a median 9.8% more within 40 sessions, ≥20% more after 18% of exits.
- Refusals: {"size_below_min": 79, "size_zero_cash": 43}; funnel {"default": {"evaluated": 113216, "universe": 57908, "trend_template": 24120, "close_vs_pivot": 790, "setup": 790, "watchlist": 669, "trigger": 182, "breakout_volume": 182, "stop": 174, "max_chase": 174}}, regime-off nights 22.
- **Where it falls short.** Signal scarcity, not sizing.
  - Only 174 entries reached the trigger all year, and 2 of the top 30 were caught (VAKRANGEE, BBTC).
  - Most top-30 names failed `close_vs_pivot` night after night (RAIN 179, BOMDYEING 155, JINDALSTEL 168): they ran
    without forming a VCP base near a pivot.
  - Seven names formed a setup that never broke its pivot (VIPIND, EDELWEISS, DELTACORP, DBL, JMFINANCIL, 8KMILES,
    KOLTEPATIL).
  - The capital it had was well used: cash, not slots, was binding, with 43 `size_zero_cash` and 79 `size_below_min`
    refusals.
  - Exits leave about half the move. Winners realised 4.5 R against an MFE of 6.1 R, mostly on `sma50_close` (31 of 50).

Top-30 caught 2/30:

| # | Stock | Move % | Low → high | Caught / blocking rule |
| --- | --- | --- | --- | --- |
| 1 | RAIN | 652 | 01-06 → 11-13 | missed: no setup in 226 scanned nights; first failing gate close_vs_pivot 179, universe 33, trend_template 14 |
| 2 | BOMDYEING | 530 | 01-02 → 12-20 | missed: no setup in 226 scanned nights; first failing gate close_vs_pivot 155, universe 47, trend_template 24 |
| 3 | AVANTIFEED | 507 | 01-02 → 11-13 | missed: no setup in 226 scanned nights; first failing gate close_vs_pivot 124, universe 88, trend_template 14 |
| 4 | KOLTEPATIL | 382 | 01-02 → 11-29 | missed: setup passed 1 nights; trigger never fired (no break of the pivot) |
| 5 | ADANITRANS | 340 | 01-02 → 12-22 | missed: no setup in 226 scanned nights; first failing gate close_vs_pivot 111, universe 100, trend_template 15 |
| 6 | RCOM | 318 | 11-15 → 12-29 | missed: no setup in 226 scanned nights; first failing gate universe 226 |
| 7 | FVIL | 302 | 01-02 → 12-27 | missed: no setup in 226 scanned nights; first failing gate universe 153, close_vs_pivot 55, trend_template 18 |
| 8 | SUNTECK | 300 | 01-02 → 12-19 | missed: no setup in 226 scanned nights; first failing gate universe 174, close_vs_pivot 52 |
| 9 | GVKPIL | 292 | 05-25 → 11-01 | missed: no setup in 226 scanned nights; first failing gate universe 226 |
| 10 | JPASSOCIAT | 285 | 01-03 → 07-28 | missed: no setup in 226 scanned nights; first failing gate universe 226 |
| 11 | IBREALEST | 276 | 01-02 → 08-07 | missed: no setup in 226 scanned nights; first failing gate trend_template 126, close_vs_pivot 100 |
| 12 | BBTC | 240 | 01-02 → 12-29 | caught: 1 trade(s), stock -3%, equity -0.41%, first entry 2017-05-30 |
| 13 | VIPIND | 238 | 01-02 → 11-28 | missed: setup passed 5 nights; trigger never fired (no break of the pivot) |
| 14 | EDELWEISS | 225 | 01-09 → 11-03 | missed: setup passed 6 nights; trigger never fired (no break of the pivot) |
| 15 | VAKRANGEE | 223 | 01-06 → 12-27 | caught: 1 trade(s), stock +202%, equity +40.87%, first entry 2017-01-12 |
| 16 | FLFL | 214 | 01-02 → 11-24 | missed: no setup in 114 scanned nights; first failing gate universe 112, close_vs_pivot 1, trend_template 1 |
| 17 | MINDAIND | 212 | 04-13 → 12-21 | missed: no setup in 169 scanned nights; first failing gate universe 118, close_vs_pivot 51 |
| 18 | MOTILALOFS | 209 | 01-06 → 12-22 | missed: no setup in 226 scanned nights; first failing gate close_vs_pivot 127, universe 66, trend_template 33 |
| 19 | DBL | 205 | 03-31 → 12-27 | missed: setup passed 3 nights; trigger never fired (no break of the pivot) |
| 20 | RKFORGE | 204 | 01-02 → 12-19 | missed: no setup in 226 scanned nights; first failing gate universe 226 |
| 21 | HFCL | 203 | 06-30 → 09-18 | missed: no setup in 226 scanned nights; first failing gate universe 226 |
| 22 | JAICORPLTD | 201 | 02-01 → 11-27 | missed: no setup in 226 scanned nights; first failing gate universe 122, close_vs_pivot 70, trend_template 34 |
| 23 | JINDALSTEL | 200 | 01-02 → 12-29 | missed: no setup in 226 scanned nights; first failing gate close_vs_pivot 168, trend_template 58 |
| 24 | DELTACORP | 198 | 01-02 → 12-26 | missed: setup passed 6 nights; trigger never fired (no break of the pivot) |
| 25 | DCMSHRIRAM | 198 | 01-02 → 12-19 | missed: no setup in 226 scanned nights; first failing gate universe 190, close_vs_pivot 36 |
| 26 | RADICO | 190 | 04-19 → 11-22 | missed: no setup in 226 scanned nights; first failing gate close_vs_pivot 110, universe 103, trend_template 13 |
| 27 | JMFINANCIL | 189 | 01-02 → 10-16 | missed: setup passed 3 nights; trigger never fired (no break of the pivot) |
| 28 | SHILPI | 189 | 06-15 → 07-14 | missed: no setup in 128 scanned nights; first failing gate universe 107, trend_template 16, close_vs_pivot 5 |
| 29 | KEC | 184 | 01-02 → 12-22 | missed: no setup in 226 scanned nights; first failing gate close_vs_pivot 143, universe 63, trend_template 20 |
| 30 | 8KMILES | 182 | 09-27 → 11-29 | missed: setup passed 5 nights; trigger never fired (no break of the pivot) |

### Darvas box — run `01a19012-320f-71e0-9719-b51b8b0152b0`

- Invested 67.9% avg; 5.90 positions × 11.50% avg size = 67.9%; zero-position days 7.7%; most held 10.
- Median stop 6.8%, median position at entry 11.1% of equity.
- 2017 +13.0% vs TRI +37.65% (-24.6 pts); 60 trades, win 45.0%, expectancy 0.31 R, max DD 8.2%.
- Best trade VAKRANGEE 2017-10-17→2017-12-29: stock +61.3%, equity +5.42% (position 8.9%). Largest equity effect VAKRANGEE +5.42% (stock +61.3%).
- Exits: realised 0.31 R vs MFE 1.75 R avg; after exit the stock rose a median 12.6% more within 40 sessions, ≥20% more after 27% of exits.
- Refusals: {"max_chase": 1, "max_positions": 6, "size_below_min": 30, "size_zero_cash": 26}; funnel {"default": {"evaluated": 105701, "universe": 54723, "darvas_box": 2099, "setup": 2099, "watchlist": 1931, "trigger": 254, "breakout_volume": 124, "stop": 124, "max_chase": 123}}, regime-off nights 37.
- **Where it falls short.** Signals first, then exits.
  - 2,099 box setup-nights gave only 124 volume-confirmed breaks, and the book was 7.7% of days empty (37 regime-off
    nights).
  - Where it did set up on a top-30 name, cash was gone (RAIN, BBTC, JMFINANCIL, KEC: `size_zero_cash`).
  - Exits: the 10-day swing-low trail took 38 of 60 trades for 0.31 R realised against an MFE of 1.75 R, and 27% of
    exits were followed by another ≥20%.
  - The top-30 miss is mostly `darvas_box` itself. Big 2017 movers rarely paused 3 sessions under a 52-week high
    within 8% (BOMDYEING 178 nights, JINDALSTEL and IBREALEST every night).

Top-30 caught 5/30:

| # | Stock | Move % | Low → high | Caught / blocking rule |
| --- | --- | --- | --- | --- |
| 1 | RAIN | 652 | 01-06 → 11-13 | missed: setup passed 7 nights; refused size_zero_cash |
| 2 | BOMDYEING | 530 | 01-02 → 12-20 | missed: no setup in 211 scanned nights; first failing gate darvas_box 178, universe 33 |
| 3 | AVANTIFEED | 507 | 01-02 → 11-13 | caught: 2 trade(s), stock -12%, equity -1.48%, first entry 2017-08-01 |
| 4 | KOLTEPATIL | 382 | 01-02 → 11-29 | missed: no setup in 211 scanned nights; first failing gate universe 120, darvas_box 91 |
| 5 | ADANITRANS | 340 | 01-02 → 12-22 | missed: no setup in 211 scanned nights; first failing gate darvas_box 125, universe 86 |
| 6 | RCOM | 318 | 11-15 → 12-29 | missed: no setup in 211 scanned nights; first failing gate universe 211 |
| 7 | FVIL | 302 | 01-02 → 12-27 | missed: no setup in 211 scanned nights; first failing gate universe 139, darvas_box 72 |
| 8 | SUNTECK | 300 | 01-02 → 12-19 | missed: no setup in 211 scanned nights; first failing gate universe 159, darvas_box 52 |
| 9 | GVKPIL | 292 | 05-25 → 11-01 | missed: no setup in 211 scanned nights; first failing gate universe 211 |
| 10 | JPASSOCIAT | 285 | 01-03 → 07-28 | missed: no setup in 211 scanned nights; first failing gate universe 211 |
| 11 | IBREALEST | 276 | 01-02 → 08-07 | missed: no setup in 211 scanned nights; first failing gate darvas_box 211 |
| 12 | BBTC | 240 | 01-02 → 12-29 | missed: setup passed 4 nights; refused size_zero_cash |
| 13 | VIPIND | 238 | 01-02 → 11-28 | caught: 1 trade(s), stock +27%, equity +2.90%, first entry 2017-10-25 |
| 14 | EDELWEISS | 225 | 01-09 → 11-03 | missed: setup passed 3 nights; trigger never fired (no break of the pivot) |
| 15 | VAKRANGEE | 223 | 01-06 → 12-27 | caught: 2 trade(s), stock +89%, equity +10.37%, first entry 2017-03-17 |
| 16 | FLFL | 214 | 01-02 → 11-24 | missed: no setup in 99 scanned nights; first failing gate universe 98, darvas_box 1 |
| 17 | MINDAIND | 212 | 04-13 → 12-21 | missed: no setup in 168 scanned nights; first failing gate universe 117, darvas_box 51 |
| 18 | MOTILALOFS | 209 | 01-06 → 12-22 | missed: setup passed 5 nights; refused size_below_min |
| 19 | DBL | 205 | 03-31 → 12-27 | caught: 1 trade(s), stock +2%, equity +0.19%, first entry 2017-10-25 |
| 20 | RKFORGE | 204 | 01-02 → 12-19 | missed: no setup in 211 scanned nights; first failing gate universe 211 |
| 21 | HFCL | 203 | 06-30 → 09-18 | missed: no setup in 211 scanned nights; first failing gate universe 211 |
| 22 | JAICORPLTD | 201 | 02-01 → 11-27 | missed: setup passed 8 nights; refused size_below_min |
| 23 | JINDALSTEL | 200 | 01-02 → 12-29 | missed: no setup in 211 scanned nights; first failing gate darvas_box 211 |
| 24 | DELTACORP | 198 | 01-02 → 12-26 | missed: setup passed 3 nights; trigger never fired (no break of the pivot) |
| 25 | DCMSHRIRAM | 198 | 01-02 → 12-19 | missed: no setup in 211 scanned nights; first failing gate universe 175, darvas_box 36 |
| 26 | RADICO | 190 | 04-19 → 11-22 | caught: 1 trade(s), stock -7%, equity -0.20%, first entry 2017-09-08 |
| 27 | JMFINANCIL | 189 | 01-02 → 10-16 | missed: setup passed 18 nights; refused size_zero_cash |
| 28 | SHILPI | 189 | 06-15 → 07-14 | missed: no setup in 127 scanned nights; first failing gate universe 106, darvas_box 21 |
| 29 | KEC | 184 | 01-02 → 12-22 | missed: setup passed 1 nights; refused size_zero_cash |
| 30 | 8KMILES | 182 | 09-27 → 11-29 | missed: no setup in 211 scanned nights; first failing gate universe 138, darvas_box 73 |

### EMA pullback — run `01a18ffa-1198-7331-bba8-db7569699f45`

- Invested 83.9% avg; 5.53 positions × 15.16% avg size = 83.9%; zero-position days 7.7%; most held 8.
- Median stop 4.4%, median position at entry 12.8% of equity.
- 2017 +16.3% vs TRI +37.65% (-21.3 pts); 101 trades, win 28.7%, expectancy 0.17 R, max DD 15.3%.
- Best trade ESCORTS 2017-02-15→2017-06-23: stock +73.6%, equity +11.87% (position 16.2%). Largest equity effect ESCORTS +11.87% (stock +73.6%).
- Exits: realised 0.17 R vs MFE 2.21 R avg; after exit the stock rose a median 16.1% more within 40 sessions, ≥20% more after 31% of exits.
- Refusals: {"max_chase": 1, "max_positions": 2, "size_below_min": 347, "size_zero_cash": 453}; funnel {"default": {"evaluated": 105701, "universe": 54723, "rs_rank": 10273, "trend_template": 9250, "ema_pullback": 2653, "setup": 2653, "watchlist": 2142, "trigger": 1012, "breakout_volume": 1012, "stop": 904, "max_chase": 903}}, regime-off nights 37.
- **Where it falls short.** Entries and exits, not catch or deployment.
  - It traded 19 of the top 30, but 14 of those 19 lost money. The tight pullback-low stop (median 4.4%) ended 46 of
    101 trades at the initial stop. Winners realised 3.1 R against an MFE of 5.7 R.
  - The book was cash-bound at about 15% a position: 453 `size_zero_cash` and 347 `size_below_min` refusals.
  - Fees took ₹40k (`cost_share_pct` 19.8).

Top-30 caught 19/30:

| # | Stock | Move % | Low → high | Caught / blocking rule |
| --- | --- | --- | --- | --- |
| 1 | RAIN | 652 | 01-06 → 11-13 | caught: 5 trade(s), stock -9%, equity -1.36%, first entry 2017-03-22 |
| 2 | BOMDYEING | 530 | 01-02 → 12-20 | caught: 1 trade(s), stock -6%, equity -0.83%, first entry 2017-10-18 |
| 3 | AVANTIFEED | 507 | 01-02 → 11-13 | caught: 3 trade(s), stock -3%, equity -0.46%, first entry 2017-07-17 |
| 4 | KOLTEPATIL | 382 | 01-02 → 11-29 | caught: 2 trade(s), stock +36%, equity +5.44%, first entry 2017-11-16 |
| 5 | ADANITRANS | 340 | 01-02 → 12-22 | caught: 2 trade(s), stock -7%, equity -0.68%, first entry 2017-06-27 |
| 6 | RCOM | 318 | 11-15 → 12-29 | missed: no setup in 211 scanned nights; first failing gate universe 211 |
| 7 | FVIL | 302 | 01-02 → 12-27 | caught: 1 trade(s), stock -4%, equity -0.18%, first entry 2017-10-18 |
| 8 | SUNTECK | 300 | 01-02 → 12-19 | missed: setup passed 7 nights; refused size_zero_cash |
| 9 | GVKPIL | 292 | 05-25 → 11-01 | missed: no setup in 211 scanned nights; first failing gate universe 211 |
| 10 | JPASSOCIAT | 285 | 01-03 → 07-28 | missed: no setup in 211 scanned nights; first failing gate universe 211 |
| 11 | IBREALEST | 276 | 01-02 → 08-07 | caught: 2 trade(s), stock +28%, equity +2.65%, first entry 2017-05-19 |
| 12 | BBTC | 240 | 01-02 → 12-29 | caught: 1 trade(s), stock -5%, equity -0.73%, first entry 2017-12-01 |
| 13 | VIPIND | 238 | 01-02 → 11-28 | caught: 2 trade(s), stock +26%, equity +0.34%, first entry 2017-09-12 |
| 14 | EDELWEISS | 225 | 01-09 → 11-03 | caught: 2 trade(s), stock +60%, equity +5.85%, first entry 2017-03-09 |
| 15 | VAKRANGEE | 223 | 01-06 → 12-27 | caught: 4 trade(s), stock -5%, equity -1.07%, first entry 2017-07-27 |
| 16 | FLFL | 214 | 01-02 → 11-24 | missed: no setup in 99 scanned nights; first failing gate universe 98, ema_pullback 1 |
| 17 | MINDAIND | 212 | 04-13 → 12-21 | caught: 3 trade(s), stock +14%, equity +1.81%, first entry 2017-08-09 |
| 18 | MOTILALOFS | 209 | 01-06 → 12-22 | caught: 2 trade(s), stock -2%, equity -0.67%, first entry 2017-08-24 |
| 19 | DBL | 205 | 03-31 → 12-27 | caught: 2 trade(s), stock -8%, equity -1.23%, first entry 2017-09-19 |
| 20 | RKFORGE | 204 | 01-02 → 12-19 | missed: no setup in 211 scanned nights; first failing gate universe 211 |
| 21 | HFCL | 203 | 06-30 → 09-18 | missed: no setup in 211 scanned nights; first failing gate universe 211 |
| 22 | JAICORPLTD | 201 | 02-01 → 11-27 | missed: setup passed 23 nights; refused size_below_min, size_zero_cash |
| 23 | JINDALSTEL | 200 | 01-02 → 12-29 | caught: 3 trade(s), stock -13%, equity -1.49%, first entry 2017-03-09 |
| 24 | DELTACORP | 198 | 01-02 → 12-26 | caught: 1 trade(s), stock -5%, equity -0.54%, first entry 2017-11-27 |
| 25 | DCMSHRIRAM | 198 | 01-02 → 12-19 | missed: setup passed 8 nights; refused size_below_min, size_zero_cash |
| 26 | RADICO | 190 | 04-19 → 11-22 | caught: 1 trade(s), stock -6%, equity -0.83%, first entry 2017-12-01 |
| 27 | JMFINANCIL | 189 | 01-02 → 10-16 | caught: 3 trade(s), stock -6%, equity -0.77%, first entry 2017-05-19 |
| 28 | SHILPI | 189 | 06-15 → 07-14 | missed: no setup in 127 scanned nights; first failing gate universe 106, rs_rank 13, trend_template 8 |
| 29 | KEC | 184 | 01-02 → 12-22 | caught: 1 trade(s), stock -3%, equity -0.52%, first entry 2017-07-26 |
| 30 | 8KMILES | 182 | 09-27 → 11-29 | missed: setup passed 15 nights; refused size_below_min |

### RSI-2 reversion — run `01a19018-44d9-76d0-8aa3-bdd3f402a122`

- Invested 43.3% avg; 5.80 positions × 7.47% avg size = 43.3%; zero-position days 6.5%; most held 10.
- Median stop 10.3%, median position at entry 7.4% of equity.
- 2017 -20.8% vs TRI +37.65% (-58.5 pts); 599 trades, win 55.6%, expectancy -0.05 R, max DD 24.4%.
- Best trade AVANTIFEED 2017-08-11→2017-08-14: stock +19.9%, equity +1.04% (position 5.3%). Largest equity effect AVANTIFEED +1.04% (stock +19.9%).
- Exits: realised -0.05 R vs MFE 0.23 R avg; after exit the stock rose a median 12.3% more within 40 sessions, ≥20% more after 28% of exits.
- Refusals: {"max_chase": 73, "max_positions": 2782, "stopout_cap": 82}; funnel {"default": {"evaluated": 123235, "universe": 62926, "trend_template": 48643, "rsi_below": 4400, "setup": 4400, "watchlist": 3737, "trigger": 3545, "breakout_volume": 3545, "stop": 3545, "max_chase": 3472}}, regime-off nights 2.
- **Where it falls short.** No edge, made worse by costs.
  - Average win 0.18 R against average loss 0.34 R at a 55.6% win rate. Winners are held about 1.3 sessions.
  - Fees of ₹1.09L on 599 trades are about 11% of capital. Without them the year is still about −10%.
  - Deployment is size-bound: the 3×ATR stop (median 10.3%) sizes each position at 7.5%, so even 10 positions are 75%.
    The slot and entry caps refused 2,782 signals (`max_positions`).
  - It "caught" 21 of the top 30 only as short snap-back scalps (RAIN +15% over 6 trades, against a 652% move).

Top-30 caught 21/30:

| # | Stock | Move % | Low → high | Caught / blocking rule |
| --- | --- | --- | --- | --- |
| 1 | RAIN | 652 | 01-06 → 11-13 | caught: 6 trade(s), stock +15%, equity +0.60%, first entry 2017-04-10 |
| 2 | BOMDYEING | 530 | 01-02 → 12-20 | caught: 7 trade(s), stock +22%, equity +0.84%, first entry 2017-04-11 |
| 3 | AVANTIFEED | 507 | 01-02 → 11-13 | caught: 5 trade(s), stock +18%, equity +0.83%, first entry 2017-06-20 |
| 4 | KOLTEPATIL | 382 | 01-02 → 11-29 | caught: 2 trade(s), stock -3%, equity -0.14%, first entry 2017-09-27 |
| 5 | ADANITRANS | 340 | 01-02 → 12-22 | caught: 6 trade(s), stock -27%, equity -1.18%, first entry 2017-04-27 |
| 6 | RCOM | 318 | 11-15 → 12-29 | missed: no setup in 246 scanned nights; first failing gate universe 246 |
| 7 | FVIL | 302 | 01-02 → 12-27 | caught: 5 trade(s), stock +8%, equity +0.21%, first entry 2017-09-20 |
| 8 | SUNTECK | 300 | 01-02 → 12-19 | missed: no setup in 246 scanned nights; first failing gate universe 190, rsi_below 56 |
| 9 | GVKPIL | 292 | 05-25 → 11-01 | missed: no setup in 246 scanned nights; first failing gate universe 246 |
| 10 | JPASSOCIAT | 285 | 01-03 → 07-28 | missed: no setup in 246 scanned nights; first failing gate universe 246 |
| 11 | IBREALEST | 276 | 01-02 → 08-07 | caught: 4 trade(s), stock +14%, equity +0.55%, first entry 2017-05-24 |
| 12 | BBTC | 240 | 01-02 → 12-29 | caught: 6 trade(s), stock -2%, equity -0.25%, first entry 2017-04-07 |
| 13 | VIPIND | 238 | 01-02 → 11-28 | caught: 2 trade(s), stock +2%, equity +0.10%, first entry 2017-04-13 |
| 14 | EDELWEISS | 225 | 01-09 → 11-03 | caught: 8 trade(s), stock +17%, equity +0.64%, first entry 2017-04-18 |
| 15 | VAKRANGEE | 223 | 01-06 → 12-27 | caught: 7 trade(s), stock +6%, equity +0.28%, first entry 2017-01-09 |
| 16 | FLFL | 214 | 01-02 → 11-24 | missed: no setup in 122 scanned nights; first failing gate universe 115, rsi_below 7 |
| 17 | MINDAIND | 212 | 04-13 → 12-21 | caught: 5 trade(s), stock +2%, equity -0.03%, first entry 2017-06-13 |
| 18 | MOTILALOFS | 209 | 01-06 → 12-22 | caught: 9 trade(s), stock +13%, equity +0.61%, first entry 2017-05-23 |
| 19 | DBL | 205 | 03-31 → 12-27 | caught: 4 trade(s), stock -0%, equity -0.11%, first entry 2017-06-06 |
| 20 | RKFORGE | 204 | 01-02 → 12-19 | missed: no setup in 246 scanned nights; first failing gate universe 246 |
| 21 | HFCL | 203 | 06-30 → 09-18 | missed: no setup in 246 scanned nights; first failing gate universe 246 |
| 22 | JAICORPLTD | 201 | 02-01 → 11-27 | caught: 2 trade(s), stock +3%, equity +0.12%, first entry 2017-11-09 |
| 23 | JINDALSTEL | 200 | 01-02 → 12-29 | caught: 4 trade(s), stock -5%, equity -0.40%, first entry 2017-03-09 |
| 24 | DELTACORP | 198 | 01-02 → 12-26 | caught: 5 trade(s), stock +16%, equity +0.66%, first entry 2017-01-20 |
| 25 | DCMSHRIRAM | 198 | 01-02 → 12-19 | caught: 2 trade(s), stock -3%, equity -0.24%, first entry 2017-11-23 |
| 26 | RADICO | 190 | 04-19 → 11-22 | missed: setup passed 11 nights; refused max_chase, max_positions, stopout_cap |
| 27 | JMFINANCIL | 189 | 01-02 → 10-16 | caught: 3 trade(s), stock -1%, equity -0.02%, first entry 2017-05-18 |
| 28 | SHILPI | 189 | 06-15 → 07-14 | caught: 1 trade(s), stock -36%, equity -1.36%, first entry 2017-04-26 |
| 29 | KEC | 184 | 01-02 → 12-22 | caught: 5 trade(s), stock -1%, equity -0.11%, first entry 2017-05-04 |
| 30 | 8KMILES | 182 | 09-27 → 11-29 | missed: setup passed 1 nights; refused max_chase |

## Next: combined runs (proposed, not run)

The owner's design is nightly scanners feeding one portfolio, with backtests deciding timing, weights and
replacement. Each run below is one portfolio file on one account (shared cash, account caps), stocks only, on the
in-sample window 2016-01-01 to 2021-12-31, so 2017 is not the evidence. Each needs the not_in_universe fix first:
VCP, Darvas and pullback over six years will hit the abort again.

1. **Rotation core + VCP satellite.** p5 rotation at weight 0.7 and p2 old VCP at 0.3, each with its own settings.
   - Question: does VCP's convex tail (VAKRANGEE-type winners the rotation holds late) add return above the rotation
     alone, at a lower drawdown?
   - Baselines: p5 alone and p2 alone over the same window.
2. **Equal sleeves, equal slot sizes.** Rotation 0.5 with `rotation.top_n=10` (≈5% slots on half the account) and VCP
   0.5.
   - Question: how does a breakout scanner do when it competes for capital with rotation names at the same slot size?
     This is the closest existing knob to "replacement".
   - One change against run 1: a declared bundle of the weight and `top_n`.
3. **Run 1 + Darvas as a second breakout scanner.** Rotation 0.6, VCP 0.2, Darvas 0.2.
   - Question: does a second, broader breakout signal (Darvas had 2,099 setup-nights against VCP's 790 in 2017) raise
     deployment and catch without diluting VCP's edge?
   - The EMA pullback and RSI-2 are left out: neither showed edge here (0.17 R, ex-top-5 CAGR −16.5; −0.05 R).

Replacement proper (a scanner signal displacing the weakest rotation holding) is not a knob today, so it would need
engine work.
