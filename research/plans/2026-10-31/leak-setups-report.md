# Leak audit of the book setups (VCP, cheat, Darvas, other S1 setups), 2016–2021 (2026-10-31)

No engine backtest was run. Everything below re-prices **existing run outputs** (signals.csv,
including refused signals) on daily bars dated up to 2021-12-31. The only intraday check uses the
in-sample 5-minute bars (2021-10-26 to 2021-12-31). No data after 2021-12-31 was read for
evaluation. Post-2021 corporate-action factors were used only to put prices on the same scale as
the runs. The DB and m3 were read-only.

## Verdict

1. **The full-day-volume look-ahead is the main leak.** Three rules depend on it: `volume_pace` on
   the daily estimate in the book setups v3 (r3), in Darvas, and in EP.
   - **Per-trade effect.** It adds about **+0.2–0.4R per trade** over an honest entry with the same
     volume rule: Darvas +0.29R, book r3 +0.25R, book with volume ≥1.5× +0.43R.
   - **Stability.** For Darvas the effect is positive in 6 of 6 years.
   - **On 5-minute bars** (late 2021), live's volume pace against the full-day estimate costs
     **0.66 pp on the breakout day and 0.79 pp at 5 days** per trade.
   - **Without the leak the rule hurts.** Judged honestly, a high-volume breakout is *worse*:
     - old VCP at T+1: **0.04R** with volume ≥1.5× against **0.65R** without;
     - book setups: −0.36R against +0.81R.
2. **The daily estimate itself, a buy at pivot + tick, is not a look-ahead. It is a buy-stop order.**
   - On 5-minute bars a resting buy-stop from 09:20 fills a mean **+0.12 pp** above the estimate on
     non-gap breaks and +0.20 pp on gaps.
   - **The problem is that live does not trade a stop.** Live waits for a 5-minute *close* above the
     pivot (it fires on 83% of breaks, at a mean +0.53 pp above the pivot).
   - So the backtest measures a different order from the one live sends. For setups without a volume
     rule, the estimate and honest entries differ by only about 0.05–0.1R.
3. **After the fix, no setup shows alpha in 2016–2021.**
   - **Old VCP** (stage2 v2, no volume rule) keeps a positive R under every leak-free entry:
     **0.39–0.50R, profit factor 1.8–2.1, t ≈ 2.5**. Its excess return over NIFTY 500 TRI over the
     same holding days is only **+0.1 to +0.8% per trade (t < 0.8)**. Its R is negative in 2018–2019
     and positive mostly in 2020–2021, which is beta plus trend-exit skew.
   - **Book setups v3:**
     - with the volume rule, honest entries lose (−0.2 to −0.4R; excess −4 to −5% per trade, t −4);
     - without it the sample is small (52–72 trades, 0.34–0.74R, excess ≈ 0).
   - **Darvas: no edge** (estimate 0.28R; honest −0.01 to 0.06R).
   - **EMA pullback (2017 only): no edge** (excess ≤ 0 under every entry).
4. **Recommendation.**
   - Implement the leak-free entry below, **E1, a buy-stop at pivot + tick from 09:20, with no volume
     rule on daily bars**. Make live send the same order.
   - Ban full-day volume rules on daily-estimate sessions.
   - Then treat old VCP as a beta sleeve and compare it with rotation, not as an alpha source.
   - Re-testing the book setups is low priority.

## Leak table

Effect = R per trade (R net of a 0.5% round trip, initial stop plus a close-below-SMA50 exit capped
at 120 sessions), estimate minus honest T+1 entry under the same filter, per year 2016 / 17 / 18 /
19 / 20 / 21 → all.

| # | Leak | Code location | Effect size per year | Fix |
|---|---|---|---|---|
| L1 | **Full-day volume look-ahead.** On a daily-estimate session `volume_pace` is judged on the whole day's volume, but the fill is at the pivot, intraday. A volume skip does not consume the row, so the row waits for a day whose *final* volume confirms. | `backtest/loop.py:1518` (`_full_day_pace`), `:1870` (EP); `backtest/fillrules.py:156` `full_day_pace_skip`; `loop.py:330` `consumes()` (volume skips keep the row) | **Darvas:** +0.29 / +0.19 / +0.13 / +0.04 / +0.73 / +0.30 → **+0.29R**. **Book r3:** +0.06 / +0.83 / +0.04 / −0.63 / +0.23 / +0.16 → **+0.25R**. **Old VCP, vol≥1.5× subset:** +0.22 / −0.07 / +0.46 / −0.14 / +0.04 / +0.31 → **+0.18R**. **Book, vol≥1.5× subset:** +0.15 / +1.16 / +0.14 / −0.48 / +0.23 / +0.24 → **+0.43R**. **5-minute bars, 2021Q4 (1,142 breaks):** estimate with full-day ≥1.5× gives +0.30% on the day and −0.47% at 5 days; live pace gives −0.36% and −1.26%, so **+0.66 / +0.79 pp**. | On sessions without 5-minute bars, **refuse** an enabled `volume_pace` (fail the run audit, not warn). Volume may be judged only (a) through the trigger bar on 5-minute bars, or (b) at the close for a T+1 entry (E2). |
| L2 | **The trigger model differs from live.** The estimate is "high > pivot → buy pivot + tick", a stop order. Live is `price_breaks_level confirm: close` on a 5-minute bar, with the LIMIT at max(level, bar close). | `loop.py:1975` → `fills.py:65` `entry_fill`; live `engine/criteria/live.py:240`, `engine/trigger.py:466` `entry_limit`; known gap `trigger_is_level_break_only` | **Not measurable per year before 2021-10** (no 5-minute bars). **2021Q4:** live does not fire on **17%** of daily breaks, which average −1.92% on the day and −3.04% at 5 days. When it fires it enters +0.53 pp above the pivot (non-gap) and pays about 0.5 pp against the estimate. Net per break, at 5 days: estimate −1.09% vs live −1.17%. **Estimate vs honest daily entries, old VCP:** +0.31 / −0.09 / +0.25 / +0.22 / +0.19 / +0.14 → **+0.08R**. | Make **live and backtest the same order**: a broker stop-limit at pivot + tick (E1), or keep the 5-minute confirm and model it in the backtest only where 5-minute bars exist. |
| L3 | **`max_chase` never binds on the estimate**, because the fill is pivot + tick by construction. | `loop.py:1540-1544` (`_entry_filters` on the estimate price) | **Refusals:** 1 of 730 old-VCP signals and 1 of 423 Darvas. **Live, 2021Q4:** **5.1%** of fired breaks enter more than 2% above the pivot; a stop order exceeds 2% on 2.9% (gaps only). | It binds correctly once the fill is E1's gap or 09:20 price, or E2's T+1 09:20 price. |
| L4 | **09:20 rule on intraday breaks.** A break inside 09:15–09:20 fills at pivot + tick. A 09:20 order buys at the 09:15 bar's close. | `loop.py:1975` (only gaps go through `fill_0920.gap_over_fill`, `engine/fill_0920.py:114`) | **2021Q4:** 23% of non-gap breaks happen in the first five minutes, at a mean **+0.53 pp** (median +0.27 pp) above the estimate. That is +0.12 pp over all non-gap breaks, about 0.02R. | E1: when the high is reached and the open is within 1 tick of the pivot, add a calibrated `BREAK_0920` premium (refit on the 5-minute years). Use the 09:15 close wherever 5-minute bars exist. |
| L5 | **Bug: gap-over flag.** `gapped = price == bar.open` has been false for a gap-over since fills moved to open × 1.0002 (the 09:20 estimate). Consequences: (a) the day's low after a gap-over fill is tested against the stop only when it is below open × (1 − ADR20); (b) the `gap_over_no_intraday` skip for low-of-day stops never fires, so EP and other low-of-day-stop playbooks plan from an estimated pre-break low. | `loop.py:2062` (also `:2066`, `:2072-2075`) | **Book and Darvas setup events:** 0–3 per run with a gap-over and the day's low ≤ stop, so ~0R for those runs. Not measured for low-of-day-stop playbooks. | `gapped = bar.open > level`, then the existing branches. Add a unit test on `_entry_lows` at the seam. |
| L6 | **Order of the break day's stop vs break** (pre-break low from ADR20). | `fillrules.py:39` `pre_break_low`; `loop.py:2206` | **Share of setups whose stop is touched on the break day:** 1–2% for VCP and Darvas. **EMA pullback:** 65 of 885, of which 17 are assumed before the break; at most about 0.03R. | Acceptable. Keep the adverse order and refit on the 5-minute years. |
| L7 | **`entry_timing: daily_close` (c5, c8 runs) is not live.** It fills at the official close, after the auction, with the auction's volume. | `loop.py:1977-1996` `_close_fill`; known gap `daily_close_entry_not_live` | **Close vs a T+1 09:20 entry:** −0.04 to +0.1R (old VCP 0.50 vs 0.43). | Replace it with E2 (decide at the close, fill T+1 at 09:20). |
| L8 | **PIT checks: no leak found.** | — | — | — |

Details for L8:

- **RS ranking.** `rs_pct` on a 2017 date ranks 1,441 names, 276 of which no longer trade in 2025,
  so delisted names are in the population. It is read the night before (`features_on(prev)`).
- **Scan.** The scan reads the total-return series rescaled to the read date
  (`backtest/data.py:609-630`).
- **Universe and corporate actions.**
  - `min_price` reads the raw close (`engine/criteria/universe.py:57`).
  - Turnover is in raw rupees.
  - Factor-pending names are skipped (CA5).
  - Membership is point in time from `hat_index_member`.
- **Open caveats:**
  - **(a)** `series_in` reads the current series, not the point-in-time one (handoff, 25 BZ names).
  - **(b)** `hat_index_member` NIFTY 500 starts on **2016-01-01**, with 500 seeded rows. There is
    **no PIT membership for 2011–2015**, which blocks the planned 10-year in-sample.

## Method

- **Events.**
  - Every signal row (taken or refused) of these runs:
    - book setups 1–5: breakout volume off `01a18e52`, r3 `01a18da4`, RS off `01a18d8c`, dry-up off
      `01a18e4b`;
    - old VCP: B2 `01a1903c`, deploy-02 `01a17ca4`;
    - Darvas B3 `01a1904d`;
    - EMA pullback 2017 `01a18ffa`.
  - Each event keeps the first trigger per (run, symbol, pivot).
  - Pivot, stop and estimate price come from `price`, `stop_pct` and `entry_vs_pivot_pct`.
  - Bars come from `bars_daily_raw`, adjusted with the DB's split, bonus and other factors.
  - 1–2% of events whose run price fell outside my day's range (lineage chains) were dropped. They
    would otherwise have inflated the estimate: before the fix the old-VCP estimate read 0.77R.
- **Entry variants.**

  | variant | entry |
  |---|---|
  | `est` | the engine's estimate (pivot + tick; a gap fills at open × 1.0002) |
  | `close` | close > pivot, bought at the close |
  | `close2` | the same, with the close ≤ pivot × 1.02 |
  | `t1` | close > pivot, bought at the next open × 1.0002 |
  | `t1c5` | `t1` with the next open ≤ pivot × 1.05 |
  | `t1all` | every trigger, bought at the next open |

- **Exits, identical for all variants.** The initial stop, or the first close below SMA50 (at most
  120 sessions). A 20-session time exit was also run as a check. Paths are cut at 2021-12-31.
- **Excess** = the trade's return minus NIFTY 500 TRI over the same days.
- **Scripts and outputs.** In `plans/leak-setups-work/`:
  - scripts: `scripts/load_bars.py`, `events.py`, `agg.py`, `excess.py`, `calib5m.py`;
  - outputs: `events.parquet`, `calib5m.parquet`.

### R per trade by entry (all years; n = events)

| run | est | close | close2 | t1 | t1c5 | t1all |
|---|---|---|---|---|---|---|
| old VCP B2 (no volume rule) | 0.47 (476) | 0.43 (289) | 0.50 (215) | 0.39 (289) | 0.43 (265) | 0.37 (474) |
| old VCP deploy-02 | 0.50 (353) | 0.49 (217) | 0.66 (157) | 0.47 (217) | 0.52 (199) | 0.39 (351) |
| book setups, volume off | 0.36 (130) | 0.58 (72) | 0.74 (52) | 0.37 (72) | 0.34 (67) | 0.46 (130) |
| book r3 (full-day volume) | −0.04 (49) | −0.20 (37) | −0.44 (13) | −0.29 (37) | −0.38 (30) | 0.66 (48)¹ |
| Darvas B3 (full-day volume) | 0.28 (415) | 0.06 (244) | 0.03 (157) | −0.01 (244) | −0.10 (215) | 0.01 (415) |
| EMA pullback 2017 | 0.38 (885) | 0.17 (391) | 0.18 (265) | 0.08 (391) | 0.04 (361) | 0.41 (863)¹ |

¹ One 2017 outlier drives it (+3.4R mean in 2017, negative in every other year).

### Per year, R (n)

**Old VCP B2:**

| variant | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | all |
|---|---|---|---|---|---|---|---|
| est | 0.27 (40) | 0.26 (110) | 0.02 (24) | −0.37 (25) | 0.90 (56) | 0.65 (221) | 0.47 |
| close2 | 0.26 (15) | 0.34 (58) | −0.53 (11) | −0.53 (6) | 0.86 (27) | 0.71 (98) | 0.50 |
| t1c5 | 0.01 (19) | 0.37 (68) | −0.19 (15) | −0.59 (7) | 0.75 (34) | 0.58 (122) | 0.43 |

**Book setups, volume off:**

| variant | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | all |
|---|---|---|---|---|---|---|---|
| est | −0.04 | 1.11 | −0.80 | 0.08 | 0.81 | 0.40 | 0.36 |
| t1 | 0.17 | 0.72 | −0.72 | 0.06 | 0.16 | 0.87 | 0.37 |

**Darvas:**

| variant | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | all |
|---|---|---|---|---|---|---|---|
| est | −0.17 | 0.58 | −0.48 | −0.59 | 1.16 | 0.11 | 0.28 |
| t1 | −0.46 | 0.39 | −0.60 | −0.63 | 0.43 | −0.19 | −0.01 |

### Excess over NIFTY 500 TRI per trade (%, t-stat)

| run | est | close2 | t1 | t1all |
|---|---|---|---|---|
| old VCP B2 | +0.44 (0.65) | +0.79 (0.78) | +0.09 (0.10) | +0.48 (0.69) |
| book, volume off | −0.33 | +1.79 (0.71) | −0.07 | −0.64 |
| book r3 | −2.52 (−2.6) | −5.53 | −4.82 (−4.5) | −3.66 |
| Darvas | +0.17 | −1.75 (−2.6) | −0.59 | −0.75 |

R t-stats for old VCP: est 3.5, close2 2.5, t1 2.6. Positive R with zero excess means the stop and
the SMA50 exit cut losers in a rising market. That is beta with good skew, not stock selection.

## Leak-free entry spec (outcome spec for a builder)

**E1. Stop-order breakout. This is the default for setups (VCP, cheat, cup, primary base, power
play).**

1. **Order.** On the night T−1 the row has pivot P and stop S, as now. On day T a buy stop-limit
   rests from **09:20 to 15:05**:
   - trigger price: P + tick;
   - limit: P × (1 + max_chase).
2. **Backtest fill, in order of preference.**
   - **5-minute bars.** If the 09:15 close is > P, fill at the 09:15 close (09:20). Otherwise fill
     at max(P + tick, open of the first later bar with high > P).
   - **Daily bar, gap.** If open > P, fill at `estimated_0920(open)` ≤ high.
   - **Daily bar, intraday break.** If high ≥ P + tick, fill at P + tick plus a calibrated
     stop-slippage constant. The 2021Q4 value is +0.12 pp; refit it on the 5-minute years and
     record it as an estimate gap.
   - Apply `max_chase` to that fill.
3. **No volume condition** on any session without 5-minute bars. With 5-minute bars, a volume
   condition may use only the cumulative volume through the fill bar.
4. **Break-day stop.** The low after the fill is tested adversely. A gap fill sees the whole day's
   low; this needs the L5 fix.
5. **Live must send this same order.** A broker SL-limit order is the live equivalent; it replaces
   the 5-minute `confirm: close` trigger for these playbooks.
6. **Shadow-day replay** compares fills against the 5-minute bars.

**E2. Close-confirmed, next-morning entry, for any rule that needs the day's volume or close.**

1. **Decide at T's close:**
   - close > P;
   - close ≤ P × 1.02;
   - optional: full-day volume ≥ k × ADV50, through T. Not recommended, because it is
     anti-predictive in-sample.
2. **Fill on T+1 at 09:20:** the 09:15 close, else open × 1.0002 ≤ high.
3. **Skip** if that price is ≤ S or > P × 1.05. The stop stays S.
4. This replaces `entry_timing: daily_close`, which live cannot trade.

**Engine guards**

1. A run whose playbook has `volume_pace` enabled on a daily-estimate session fails its audit with
   `lookahead_full_day_volume`. Today it only warns.
2. The run records which entry model (E1 or E2) and which slippage constant were used, so runs are
   compared like for like.

## Code bugs to fix

1. **`loop.py:2062`.** The gap-over flag is broken since the 09:20 gap fill. Fix:
   `gapped = bar.open > level` (L5).
2. **`loop.py:1518`, `:1870`, `fillrules.py:156`.** Full-day `volume_pace` is allowed on
   daily-estimate sessions. Make it an error (L1). Then fix `consumes()` (`loop.py:330`): a volume
   skip that lets the row "wait" for a high-volume day becomes harmless only once L1 is fixed.
3. **`loop.py:1975`.** The intraday break fill ignores 09:20 and has no stop slippage (L4, part of
   E1).
4. **`loop.py:1977-1996`.** Replace the daily-close entry with E2 (L7).
5. **Data, for the 10-year plan.** NIFTY 500 PIT membership exists only from 2016-01-01.

## Caveats

- **5-minute calibration.** Only 46 sessions (2021-10-26 to 2021-12-31, a weak tape); 1,142 breaks
  of the 20-day high, as a proxy for setup pivots. Refit the constants on the 5-minute years
  before use; that is calibration of fill mechanics, not evaluation.
- **Events vs engine trades.** Events include refused signals and use one uniform exit protocol.
  They measure entry quality, not the engine's portfolio CAGR.
- **Old VCP sanity check.** My old-VCP estimate (0.47R) matches the engine's 0.51R on its 230
  taken trades.
- **Book setup samples are small** (13–130 events).
