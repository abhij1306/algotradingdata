# EP event study: NSE NIFTY 500, 2016-2024 (in-sample only)

Date 2026-10-29. Read-only research. No data on or after 2025-01-01 was read; every forward window ends by 2024-12-31, so
events from late 2024 have truncated 60-session windows. Scripts are in `/data/workspace/research/ep-study/` (`00`-`09`,
`common.py`); results are in `cache/*.csv`. This is an event study in pandas, not an engine backtest.

**Price basis (corrected).** NSE `prev_close` is the previous **raw** close on ex-dates (RELIANCE 2017-09-07 bonus: prev
1645.4, open 823). So all prices come from HAT's adjusted view: `bars_daily` via `DataStore.connect(stored_adjustment)`, which
adjusts for splits, bonuses, rights, demergers and dividends, with ISIN chains linked. The source is the read-only export
`/data/workspace/research/momentum/data/bars_tr.parquet`. Gap = adjusted open / adjusted previous close − 1. Gap days on a
corporate-action ex-date (raw c/prev_close ≠ adjusted return by > 0.5%) are **dropped**: 34 of 4,162 liquid member gap-ups
≥ 4% (9 at ≥ 6%, 5 at ≥ 8%, 2 at ≥ 10%). In this liquid member set the raw gap made only one fake gap-up (at ≥ 10%). The
bigger effect of the fix is on forward returns, which no longer break on bonuses and splits and now include dividends.
Earlier results built on a close/prev_close chain have been discarded.

## Bottom line

1. **A gap with no earnings catalyst loses money on NIFTY 500 in every fold, at every gap size and with every entry and exit.**
   Non-earnings gaps of 4% or more (3,459 events, about 385 a year) lose 1.3% a trade with the SMA10 exit, 1.3 points worse
   than matched random days of the same stocks (t = −4.5; month-clustered t = −3.6). The bigger the gap, the worse:
   −3.1%/trade at ≥ 6% and −4.8% at ≥ 10%. The current S2 EP rules (gap, neglect, early volume, ORH, LOD stop, SMA10 trail) have no
   catalyst condition. On large and mid caps that is a gap-fade setup.
2. **Earnings gaps have a modest, positive edge.** It is post-earnings drift, and a tight exit cuts it off. With the
   current-style exit (LOD stop, SMA10 trail) an earnings gap makes +0.4 to +1.7% a trade. With a loose exit (LOD stop, then
   hold up to 60 sessions) it makes +4.7 to +6.3% (close or open entry, gap ≥ 6%). That is +2.8 to +3.4 points over matched
   baseline days, positive against the baseline in every fold for gap ≥ 6% (paired t 1.3-2.3, month-clustered t 2.5-3.0).
3. **The catalyst matters more than gap size.** Results rise with the gap (4 → 6 → 8%) but N falls fast, and ≥ 10% has too
   few events (33 earnings gaps in 9 years). **Neglect (|63d| ≤ 30%) is not robust**: it helps F2, hurts F1 and does nothing
   in F3. **A full-day volume filter (≥ 2×/3× ADV20) does not help.** Early volume ≥ 0.5× ADV20 at the 5m trigger adds
   about +0.7 to +0.9 points.
4. **The S2 regime gate does not help EP.** Gate on: +6.1%/trade; gate off: +8.3% (A close). For B close it is 5.1 vs 5.2%,
   and for A open 3.1 vs 5.8%. NIFTY 500 vs SMA200 shows no consistent split either. The gate halves the trade count without
   improving it.
5. **The edge sits in ₹5-100 cr ADV names.** Above ₹100 cr it is about zero against the baseline (−1.1 to +0.1 points).
6. **The 5m ORH entry (2022-24) beats buying at the open** (earnings gap ≥ 4%, hold60: ORH15 +4.5% vs open +2.0%) and is
   about equal to buying a green close. ORH5 is stopped out on day 0 27-30% of the time, against 14-17% for ORH15 and
   10-13% for ORH30. **The 5m numbers are biased up**: 24% of 2022-24 gap events have no 5m bars, and those are the worse
   ones. Earnings gaps with no bars made close-entry hold60 −3.7% (≥ 4%, n=32) and −1.9% (≥ 6%, n=10), against +5.9% and
   +9.2% with bars.
7. **The edge is thin and fat-tailed.** Win rate is 33-50% and the median trade is about −2 to −3%. Dropping the top 5 trades
   cuts the mean by a third to a half. 2017 and 2024 were flat or losing for every earnings definition, and 2016 is carried
   by a few big winners.

## Data and method

- **Universe**: NIFTY 500 point-in-time membership (`hat_index_member`, 501 members on every date checked), EQ/BE, gap days
  2016-01..2024-12, ADV20 traded value over the prior 20 sessions ≥ ₹10 cr (≥ ₹5 cr in T10). Days frozen at a circuit all day
  (high = low) are dropped as untradeable, along with corporate-action ex-dates (above).
- **Earnings flag `E`**: the gap day is the results day or the next session. Sources: results board meetings
  (`/data/workspace/ca-data/board_meetings_*.csv`, scheduled and public in advance, 2016+) or `hat_financial_result.public_at`
  (2020-04+, non-estimated: the first session opening after publication). They agree well in 2021-24: 301 events both, 95
  result-only, 39 meeting-only. Coverage before 2020 is about 75%.
- **Entries**: `open` = gap-day open (the pre-open auction price), stop = gap-day low. **This stop is ex-post**, so open-entry
  R and stop-hit rates are optimistic; read open entries in %. `close` = gap-day close, only if close > open; stop = gap-day
  low, known at entry. `orN` (5m, 2022-24) = close of the first 5m bar (starting before 15:00) that closes above the N-minute
  opening-range high; stop = low of day through that bar; the rest of day 0 is checked for a stop hit. 5m prices are rescaled
  to the raw daily bar (median deviation 0.04%).
- **Exits** (all with the LOD stop, filled at the stop or at the open if it gaps through): `sma10` = close < SMA10 from day 3,
  60-session cap; `sma20` = the same with SMA20; `hold60` = stop only, exit at the close of day 60; `time20` = exit at day 20;
  `partial` = 1/3 at the day-3 close, stop to breakeven, rest on SMA10.
- **Cost** 0.3% round trip. R = net return / max(stop distance, 1%).
- **Baseline**: for each event, 5 random days of the same stock within ±250 sessions with |gap| < 1%, the same membership,
  liquidity, entry and exit. "ev-base" is the paired difference. `x20` = 20-day return minus NIFTY 500.
- **Folds**: F1 2016-18, F2 2019-21, F3 2022-24. **Regimes**: NIFTY 500 vs SMA200 on the prior session, and the S2 engine gate
  (SMA10 > SMA20, both rising over 3 sessions; on for 52% of sessions).

**Variants tried, counted honestly.** About 200 event definitions × 5 exits, roughly 1,000 cell means:
- Daily grid: 96 cells (gap 4/6/8/10 × neglect × day volume none/2×/3× [close entry only] × earnings any/yes/no × entry) × 5 exits × 4 horizons.
- 24 baseline cells.
- 6 named definitions × 17 cuts.
- 18 filter cells under the wide exits.
- 5m: 72 cells × 5 exits.
- Liquidity, regime-gate and coverage checks.

With this many looks, no single cell with t ≈ 2 is strong evidence. The recommendation rests on patterns that repeat across
cells: catalyst vs no catalyst, wide vs tight exit, the monotonic gap dose-response, and the liquidity gradient. It does not
rest on the best cell.

## Key numbers (₹10 cr universe unless noted; hold60 = LOD stop + 60-session exit)

| definition | N | N/yr | sma10 %/trade | hold60 %/trade | hold60 R | baseline hold60 % | ev−base pts | t (paired) | ev−base F1 / F2 / F3 |
|---|---|---|---|---|---|---|---|---|---|
| D1 earnings gap ≥ 4%, close entry | 242 | 27 | +1.57 | +4.75 | 1.04 | 2.76 | +1.60 | 1.28 | +1.1 / +3.6 / +0.3 |
| D2 earnings gap ≥ 6%, close entry | 90 | 10 | +1.75 | +6.30 | 1.23 | 2.13 | +2.82 | 1.29 | +1.8 / +4.0 / +2.0 |
| D3 earnings gap ≥ 4%, open entry | 669 | 74 | +0.44 | +2.24 | (ex-post) | 1.35 | +0.89 | 1.32 | −0.1 / +3.1 / −0.5 |
| D4 earnings gap ≥ 6%, open entry | 211 | 23 | +1.44 | +4.71 | (ex-post) | 1.31 | +3.41 | 2.33 | +2.5 / +5.6 / +2.0 |
| C1 non-earnings gap ≥ 4%, open | 3,459 | 384 | −1.30 | −0.70 | — | 0.61 | −1.31 | −4.51 | −2.3 / −0.6 / −1.9 |
| C2 non-earnings gap ≥ 6%, close | 283 | 31 | −1.47 | −1.11 | — | 2.11 | −3.27 | −2.43 | −10.5 / −0.1 / −4.4 |

hold60 % by year:

| year | D1 | D2 | D4 | C1 |
|---|---|---|---|---|
| 2016 | 17.0 | 23.3 | 16.1 | −1.0 |
| 2017 | −2.5 | −6.8 | −4.7 | −1.2 |
| 2018 | 1.9 | 5.4 | −0.2 | −4.7 |
| 2019 | 0.3 | 4.8 | 4.3 | −3.3 |
| 2020 | 5.4 | 0.8 | 3.5 | 1.4 |
| 2021 | 9.5 | 7.4 | 11.4 | −0.5 |
| 2022 | 3.6 | 13.3 | 11.2 | −3.0 |
| 2023 | 8.4 | 5.5 | 4.0 | 2.8 |
| 2024 | 0.4 | 0.0 | −0.9 | −1.9 |

5m ORH vs daily entries, earnings gaps, 2022-24, events with 5m bars (biased up, see point 6):

| gap | entry | N/yr | hold60 % | hold60 R | 2022 / 2023 / 2024 % |
|---|---|---|---|---|---|
| ≥ 4% | open | 81 | +2.0 | (ex-post) | 3.0 / 5.9 / −0.4 |
| ≥ 4% | close (green) | 30 | +5.9 | 1.68 | 6.1 / 11.9 / 1.8 |
| ≥ 4% | ORH15 | 34 | +4.5 | 1.12 | 4.3 / 9.2 / 2.8 |
| ≥ 4% | ORH15 + early vol ≥ 0.5× | 31 | +5.5 | 1.36 | 6.2 / 9.2 / 3.4 |
| ≥ 6% | close (green) | 10 | +9.2 | 2.31 | 18.8 / 7.5 / −0.2 |
| ≥ 6% | ORH15 + early vol ≥ 0.5× | 11 | +8.6 | 2.09 | 17.0 / 6.8 / 2.6 |

## Recommendation

Both definitions are **earnings-only**. Thresholds come from the middle of the plateau, not the best cell.

**EP-A (primary): earnings gap ≥ 6%**
- Universe: NIFTY 500 PIT, EQ/BE, ADV20 ≥ ₹5 cr. No ADR filter, **no neglect filter**, no full-day volume filter.
- Catalyst, required: quarterly results public after the previous session's open and before this open, or the results
  board meeting falls on the previous session or today (`catalyst_type = earnings`).
- Gap: adjusted open / adjusted previous close − 1 ≥ 6%. Skip corporate-action ex-dates. Lower the live gap-scan floor from
  10% to 6%.
- Trigger: a 5m bar **closes** above the **15-minute** opening-range high, on a bar starting before 15:00, with early volume ≥ 0.5×
  ADV20 at the trigger. The daily-only proxy is the gap-day close if close > open.
- Stop: low of day at entry − 1 tick.
- Exit: **no day-3 partial, no SMA10 trail**. Hold with the LOD stop up to 60 sessions. Engine variant: close < SMA20 from
  day 3, which earns less in every fold here (+3.6% vs +6.3% for D2).
- Regime: EP not gated by the S2 SMA10/SMA20 gate. Test with and without it in the engine.
- Expected, daily close proxy at ≥ ₹5 cr, 2016-24: **12 trades/yr, +7.3% net/trade, 1.46R, win 46%, median −2.1%, +4.9%
  without the top 5; folds +8.0 / +7.6 / +6.6%**. Against the baseline (₹10 cr): +2.8 points. Open-entry analogue: 31/yr at
  +4.4%. ORH15 + early volume, 2022-24, covered days: 11/yr at +8.6%, 2.1R, biased up. Plan around +3 to +5% and about 1R
  per trade.

**EP-B (more trades, less edge per trade): earnings gap ≥ 4%**, other rules the same. At ≥ ₹5 cr: **32/yr, +5.2%/trade,
1.15R, win 34%, folds +4.0 / +7.7 / +3.5%**, but only +1.6 points over the baseline (t 1.3). Its excess over the baseline is
mostly F2. ORH15 + early volume, 2022-24: 31/yr, +5.5%, 1.36R.

**Engine config deltas** from the current S2 EP:
- gap_min 10 → 6% (EP-B: 4%)
- catalyst = earnings, required
- neglect off
- OR window 15 min
- early volume 0.5× kept
- partial off
- SMA10/20 trail → none, max hold 60 sessions (variant: SMA20)
- EP outside the S2 regime gate

Run these as engine backtests on 2016-2024 only. The hold-out stays unread until the owner gives a go.

## Caveats

- The 5m store misses about 24% of liquid gap events in 2022-24, and they are the worse ones. A 5m-only EP backtest will
  overstate the edge: fill the gaps, or use the daily close-entry proxy as the reference.
- Earnings-flag coverage before 2020 is about 75%, so some earnings gaps sit in the non-earnings group.
- Events cluster: 2020 has about a quarter of all events. Month-clustered t-stats are reported.
- The open-entry stop is ex-post. Close and ORH entries are clean.
- Cost is a flat 0.3%; gap-day slippage in ₹5-25 cr names is likely higher.
- Non-earnings gaps include news this data can't flag (orders, approvals, block deals). A separate non-earnings catalyst
  class is untested.
- The 60-session windows of late-2024 events are truncated.

## Tables (full)

### T1. Daily grid, no day-volume filter (₹10 cr, 2016-24). sma10 = current-playbook-like exit; F1-F3 = sma10 mean by fold
| entry | gap>= | neglect | earn | N | N/yr | f5% | f20% | f60% | x20% | stop20% | sma10 mean% | win% | time20% | partial% | F1% | F2% | F3% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| open | 4 | - | - | 4128 | 458.67 | -1.11 | 0.51 | 5.34 | -2.13 | 81.71 | -1.02 | 22.17 | -1.14 | -1.11 | -1.8 | -0.97 | -0.73 |
| open | 4 | - | y | 669 | 74.33 | -0.51 | 2.26 | 6.56 | 0.53 | 72.2 | 0.44 | 30.94 | 0.78 | 0.07 | -1.39 | 1.2 | 0.43 |
| open | 4 | - | n | 3459 | 384.33 | -1.23 | 0.16 | 5.11 | -2.65 | 83.56 | -1.3 | 20.47 | -1.51 | -1.34 | -1.87 | -1.28 | -1.06 |
| open | 4 | y | - | 2474 | 274.89 | -1.31 | 0.03 | 3.05 | -2.22 | 80.71 | -1.3 | 21.95 | -1.12 | -1.37 | -1.81 | -1.29 | -1.11 |
| open | 4 | y | y | 491 | 54.56 | -0.19 | 2.22 | 7.06 | 0.6 | 70.88 | 0.35 | 32.18 | 0.86 | 0.04 | -1.57 | 1.67 | 0.14 |
| open | 4 | y | n | 1983 | 220.33 | -1.59 | -0.52 | 2.09 | -2.92 | 83.16 | -1.71 | 19.42 | -1.61 | -1.73 | -1.87 | -1.84 | -1.51 |
| open | 6 | - | - | 1146 | 127.33 | -2.38 | -0.84 | 4.0 | -3.77 | 79.86 | -2.25 | 21.64 | -1.99 | -2.23 | -1.9 | -2.5 | -1.97 |
| open | 6 | - | y | 211 | 23.44 | 0.1 | 2.74 | 7.43 | 1.04 | 65.4 | 1.44 | 37.91 | 1.94 | 1.14 | 0.18 | 2.41 | 1.1 |
| open | 6 | - | n | 935 | 103.89 | -2.95 | -1.65 | 3.26 | -4.86 | 83.14 | -3.08 | 17.97 | -2.88 | -2.98 | -2.35 | -3.21 | -3.22 |
| open | 6 | y | - | 668 | 74.22 | -2.23 | -1.38 | 1.36 | -3.77 | 76.84 | -1.9 | 24.25 | -1.53 | -1.87 | -1.56 | -2.51 | -1.43 |
| open | 6 | y | y | 154 | 17.11 | 0.57 | 2.35 | 6.84 | 0.7 | 62.34 | 0.81 | 40.91 | 1.67 | 0.76 | -2.41 | 1.89 | 1.11 |
| open | 6 | y | n | 514 | 57.11 | -3.07 | -2.5 | -0.19 | -5.11 | 81.21 | -2.72 | 19.26 | -2.49 | -2.66 | -1.37 | -3.43 | -2.58 |
| open | 8 | - | - | 534 | 59.33 | -2.76 | -1.33 | 3.43 | -4.32 | 77.11 | -2.5 | 22.85 | -1.86 | -2.5 | -2.54 | -2.37 | -2.74 |
| open | 8 | - | y | 91 | 10.11 | -1.1 | 2.71 | 7.07 | 1.48 | 61.54 | 1.67 | 40.66 | 2.74 | 1.06 | -1.16 | 2.35 | 1.98 |
| open | 8 | - | n | 443 | 49.22 | -3.11 | -2.16 | 2.71 | -5.51 | 80.32 | -3.35 | 19.19 | -2.8 | -3.23 | -2.75 | -2.98 | -4.83 |
| open | 8 | y | - | 312 | 34.67 | -2.64 | -1.51 | 0.79 | -4.06 | 72.67 | -2.23 | 25.64 | -1.46 | -2.1 | -1.37 | -2.57 | -2.32 |
| open | 8 | y | y | 64 | 7.11 | -0.19 | 2.22 | 6.56 | 0.77 | 56.25 | 0.93 | 45.31 | 2.32 | 0.62 | -2.44 | 1.17 | 1.64 |
| open | 8 | y | n | 248 | 27.56 | -3.27 | -2.47 | -0.65 | -5.31 | 76.92 | -3.04 | 20.56 | -2.43 | -2.8 | -1.21 | -3.18 | -4.25 |
| open | 10 | - | - | 160 | 17.78 | -4.95 | -4.09 | 0.54 | -6.75 | 83.12 | -3.89 | 19.38 | -3.48 | -3.67 | -5.83 | -4.07 | -3.01 |
| open | 10 | - | y | 33 | 3.67 | -1.98 | 1.61 | 7.47 | -0.21 | 75.76 | -0.54 | 30.3 | -0.8 | -1.05 | -4.37 | -4.6 | 1.48 |
| open | 10 | - | n | 127 | 14.11 | -5.72 | -5.57 | -1.21 | -8.45 | 85.04 | -4.76 | 16.54 | -4.17 | -4.35 | -6.0 | -4.01 | -5.54 |
| open | 10 | y | - | 105 | 11.67 | -6.18 | -5.43 | -1.63 | -8.37 | 84.76 | -4.93 | 15.24 | -4.75 | -4.64 | -6.78 | -6.36 | -3.13 |
| open | 10 | y | y | 27 | 3.0 | -2.82 | -0.66 | 4.7 | -2.45 | 77.78 | -1.43 | 29.63 | -2.11 | -2.18 | -4.37 | -5.54 | 0.5 |
| open | 10 | y | n | 78 | 8.67 | -7.34 | -7.08 | -3.75 | -10.42 | 87.18 | -6.14 | 10.26 | -5.66 | -5.49 | -7.26 | -6.51 | -5.31 |
| close | 4 | - | - | 1344 | 149.33 | 0.39 | 1.05 | 5.82 | -1.11 | 69.85 | 0.41 | 31.03 | -0.03 | 0.31 | -1.4 | 0.98 | 0.39 |
| close | 4 | - | y | 242 | 26.89 | 0.81 | 3.71 | 9.0 | 2.15 | 52.07 | 1.57 | 41.32 | 2.19 | 1.22 | 2.25 | 2.07 | 1.03 |
| close | 4 | - | n | 1102 | 122.44 | 0.3 | 0.46 | 5.15 | -1.83 | 73.77 | 0.16 | 28.77 | -0.52 | 0.11 | -2.06 | 0.81 | 0.17 |
| close | 4 | y | - | 797 | 88.56 | 0.05 | 1.04 | 4.34 | -0.87 | 66.5 | -0.03 | 30.99 | -0.08 | -0.21 | -1.49 | 0.69 | -0.12 |
| close | 4 | y | y | 184 | 20.44 | 1.03 | 3.38 | 8.77 | 2.01 | 50.0 | 1.4 | 39.67 | 2.05 | 1.2 | 1.24 | 2.67 | 0.73 |
| close | 4 | y | n | 613 | 68.11 | -0.25 | 0.33 | 3.07 | -1.73 | 71.48 | -0.45 | 28.38 | -0.72 | -0.63 | -2.09 | 0.25 | -0.48 |
| close | 6 | - | - | 373 | 41.44 | -0.63 | -0.74 | 4.02 | -2.9 | 63.71 | -0.7 | 30.56 | -0.69 | -0.93 | -1.55 | -0.69 | -0.1 |
| close | 6 | - | y | 90 | 10.0 | 1.29 | 2.8 | 10.39 | 1.35 | 43.33 | 1.75 | 42.22 | 2.46 | 1.62 | 3.68 | 0.85 | 1.87 |
| close | 6 | - | n | 283 | 31.44 | -1.24 | -1.87 | 2.1 | -4.26 | 70.21 | -1.47 | 26.86 | -1.7 | -1.74 | -2.75 | -1.04 | -1.34 |
| close | 6 | y | - | 210 | 23.33 | -0.68 | -0.37 | 3.72 | -2.31 | 54.55 | -0.4 | 33.33 | -0.03 | -0.67 | -1.37 | -0.73 | 0.4 |
| close | 6 | y | y | 64 | 7.11 | 2.39 | 3.97 | 11.22 | 2.51 | 34.38 | 2.01 | 43.75 | 3.45 | 2.07 | 0.69 | 2.23 | 2.18 |
| close | 6 | y | n | 146 | 16.22 | -2.03 | -2.29 | 0.68 | -4.43 | 63.45 | -1.45 | 28.77 | -1.55 | -1.86 | -1.84 | -1.76 | -0.82 |
| close | 8 | - | - | 172 | 19.11 | -1.14 | -1.77 | 3.29 | -3.58 | 60.47 | -1.6 | 26.74 | -1.28 | -1.61 | -3.99 | -1.58 | 0.86 |
| close | 8 | - | y | 42 | 4.67 | 0.85 | 3.42 | 12.59 | 2.75 | 40.48 | 1.22 | 40.48 | 2.77 | 1.77 | 0.16 | -1.18 | 3.17 |
| close | 8 | - | n | 130 | 14.44 | -1.78 | -3.44 | 0.41 | -5.63 | 66.92 | -2.51 | 22.31 | -2.59 | -2.71 | -4.81 | -1.66 | -1.69 |
| close | 8 | y | - | 97 | 10.78 | -0.79 | -0.02 | 3.93 | -1.88 | 45.36 | -0.86 | 30.93 | -0.09 | -0.92 | -3.3 | -1.18 | 1.43 |
| close | 8 | y | y | 27 | 3.0 | 2.88 | 5.74 | 14.82 | 4.58 | 22.22 | 2.83 | 44.44 | 5.12 | 3.27 | -0.5 | 3.37 | 3.42 |
| close | 8 | y | n | 70 | 7.78 | -2.21 | -2.24 | -0.01 | -4.37 | 54.29 | -2.29 | 25.71 | -2.1 | -2.54 | -3.83 | -1.99 | -0.83 |
| close | 10 | - | - | 40 | 4.44 | -1.24 | -0.18 | 4.41 | -1.96 | 65.0 | -1.27 | 25.0 | -1.38 | -0.37 | -2.0 | -3.56 | 2.87 |
| close | 10 | - | y | 10 | 1.11 | 3.59 | 9.01 | 24.83 | 7.08 | 50.0 | 3.59 | 30.0 | 1.77 | 4.67 |  | -5.29 | 4.58 |
| close | 10 | - | n | 30 | 3.33 | -2.85 | -3.24 | -2.4 | -4.97 | 70.0 | -2.9 | 23.33 | -2.43 | -2.05 | -2.0 | -3.47 | -0.99 |
| close | 10 | y | - | 17 | 1.89 | 1.03 | 0.19 | 8.86 | -2.36 | 58.82 | 0.73 | 29.41 | -2.09 | 1.88 | 3.33 | -3.76 | 3.94 |
| close | 10 | y | y | 6 | 0.67 | 6.43 | 7.37 | 23.36 | 5.16 | 50.0 | 5.61 | 33.33 | 1.04 | 5.77 |  |  | 5.61 |
| close | 10 | y | n | 11 | 1.22 | -1.92 | -3.72 | 0.94 | -6.45 | 63.64 | -1.93 | 27.27 | -3.8 | -0.24 | 3.33 | -3.76 | 0.6 |

### T2. Close entry with the day-volume filter (neglect off)

| gap>= | vol>= | earn | N | N/yr | f20% | f60% | sma10 mean% | F1% | F2% | F3% |
|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 2 | - | 829 | 92.11 | -0.06 | 4.37 | -0.71 | -1.46 | -0.36 | -0.78 |
| 4 | 2 | y | 221 | 24.56 | 3.46 | 8.72 | 1.42 | 3.13 | 1.95 | 0.65 |
| 4 | 2 | n | 608 | 67.56 | -1.34 | 2.85 | -1.49 | -2.57 | -1.02 | -1.55 |
| 4 | 3 | - | 655 | 72.78 | 0.04 | 3.87 | -0.67 | -1.67 | -0.33 | -0.58 |
| 4 | 3 | y | 202 | 22.44 | 3.22 | 8.69 | 1.21 | 2.79 | 1.34 | 0.81 |
| 4 | 3 | n | 453 | 50.33 | -1.39 | 1.81 | -1.51 | -2.74 | -0.93 | -1.51 |
| 6 | 2 | - | 294 | 32.67 | -0.99 | 2.61 | -0.97 | -1.56 | -1.34 | -0.05 |
| 6 | 2 | y | 84 | 9.33 | 3.87 | 10.94 | 1.84 | 4.51 | 0.9 | 1.72 |
| 6 | 2 | n | 210 | 23.33 | -2.95 | -0.53 | -2.1 | -3.07 | -2.03 | -1.3 |
| 6 | 3 | - | 245 | 27.22 | -0.72 | 2.1 | -0.92 | -1.22 | -1.57 | 0.04 |
| 6 | 3 | y | 75 | 8.33 | 3.64 | 12.02 | 1.64 | 5.67 | -0.25 | 1.72 |
| 6 | 3 | n | 170 | 18.89 | -2.65 | -2.0 | -2.04 | -2.84 | -2.01 | -1.32 |
| 8 | 2 | - | 138 | 15.33 | -0.93 | 3.07 | -2.15 | -4.14 | -3.03 | 1.38 |
| 8 | 2 | y | 38 | 4.22 | 5.71 | 14.67 | 1.38 | 1.36 | -2.03 | 3.17 |
| 8 | 2 | n | 100 | 11.11 | -3.45 | -1.15 | -3.49 | -5.17 | -3.24 | -0.97 |
| 8 | 3 | - | 123 | 13.67 | -1.11 | 2.03 | -1.97 | -4.08 | -2.93 | 1.51 |
| 8 | 3 | y | 38 | 4.22 | 5.71 | 14.67 | 1.38 | 1.36 | -2.03 | 3.17 |
| 8 | 3 | n | 85 | 9.44 | -4.16 | -3.38 | -3.46 | -5.17 | -3.17 | -0.81 |
| 10 | 2 | - | 36 | 4.0 | 0.26 | 6.31 | -1.12 | -3.2 | -3.4 | 2.87 |
| 10 | 2 | y | 10 | 1.11 | 9.01 | 24.83 | 3.59 |  | -5.29 | 4.58 |
| 10 | 2 | n | 26 | 2.89 | -3.11 | -0.81 | -2.94 | -3.2 | -3.3 | -0.99 |
| 10 | 3 | - | 32 | 3.56 | -0.96 | 6.76 | -1.54 | -1.58 | -4.9 | 2.87 |
| 10 | 3 | y | 10 | 1.11 | 9.01 | 24.83 | 3.59 |  | -5.29 | 4.58 |
| 10 | 3 | n | 22 | 2.44 | -5.48 | -1.46 | -3.87 | -1.58 | -4.87 | -0.99 |

### T3. Matched baseline (random |gap|<1% days, same stocks, same rules)

| entry | earn | N | f5% | f20% | f60% | stop20% | sma10 mean% | time20% |
|---|---|---|---|---|---|---|---|---|
| open | - | 20634 | -0.23 | 0.66 | 3.55 | 85.71 | -0.01 | 0.11 |
| open | y | 383 | -0.8 | 1.11 | 2.7 | 82.51 | 0.08 | 0.14 |
| open | n | 20251 | -0.22 | 0.65 | 3.56 | 85.77 | -0.01 | 0.11 |
| open | - | 20634 | -0.23 | 0.66 | 3.55 | 85.71 | -0.01 | 0.11 |
| open | y | 383 | -0.8 | 1.11 | 2.7 | 82.51 | 0.08 | 0.14 |
| open | n | 20251 | -0.22 | 0.65 | 3.56 | 85.77 | -0.01 | 0.11 |
| open | - | 20634 | -0.23 | 0.66 | 3.55 | 85.71 | -0.01 | 0.11 |
| open | y | 383 | -0.8 | 1.11 | 2.7 | 82.51 | 0.08 | 0.14 |
| open | n | 20251 | -0.22 | 0.65 | 3.56 | 85.77 | -0.01 | 0.11 |
| open | - | 20634 | -0.23 | 0.66 | 3.55 | 85.71 | -0.01 | 0.11 |
| open | y | 383 | -0.8 | 1.11 | 2.7 | 82.51 | 0.08 | 0.14 |
| open | n | 20251 | -0.22 | 0.65 | 3.56 | 85.77 | -0.01 | 0.11 |
| close | - | 8259 | 0.31 | 1.24 | 3.92 | 78.02 | 0.58 | 0.78 |
| close | y | 154 | -0.28 | 3.35 | 5.49 | 77.27 | 1.57 | 1.65 |
| close | n | 8105 | 0.32 | 1.2 | 3.89 | 78.03 | 0.56 | 0.76 |
| close | - | 8259 | 0.31 | 1.24 | 3.92 | 78.02 | 0.58 | 0.78 |
| close | y | 154 | -0.28 | 3.35 | 5.49 | 77.27 | 1.57 | 1.65 |
| close | n | 8105 | 0.32 | 1.2 | 3.89 | 78.03 | 0.56 | 0.76 |
| close | - | 8259 | 0.31 | 1.24 | 3.92 | 78.02 | 0.58 | 0.78 |
| close | y | 154 | -0.28 | 3.35 | 5.49 | 77.27 | 1.57 | 1.65 |
| close | n | 8105 | 0.32 | 1.2 | 3.89 | 78.03 | 0.56 | 0.76 |
| close | - | 8259 | 0.31 | 1.24 | 3.92 | 78.02 | 0.58 | 0.78 |
| close | y | 154 | -0.28 | 3.35 | 5.49 | 77.27 | 1.57 | 1.65 |
| close | n | 8105 | 0.32 | 1.2 | 3.89 | 78.03 | 0.56 | 0.76 |

### T4. Named definitions: folds, regime (NIFTY 500 vs SMA200), liquidity; paired vs baseline (₹10 cr)

| def | cut | N | stop20% | sma10% | sma20% | hold60% | hold60 R | hold60 base% | hold60 ev-base% | hold60 t(ev-base) | hold60 t(month) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 earn gap>=4 close | all | 242 | 52.07 | 1.57 | 2.77 | 4.75 | 1.04 | 2.76 | 1.6 | 1.28 | 2.92 |
| D1 earn gap>=4 close | fold=F1 16-18 | 31 | 48.39 | 2.25 | 6.34 | 4.68 | 0.76 | 1.24 | 1.09 | 0.31 | 1.26 |
| D1 earn gap>=4 close | fold=F2 19-21 | 88 | 51.14 | 2.07 | 4.02 | 6.61 | 1.17 | 3.45 | 3.56 | 1.5 | 1.93 |
| D1 earn gap>=4 close | fold=F3 22-24 | 123 | 53.66 | 1.03 | 0.97 | 3.43 | 1.02 | 2.64 | 0.27 | 0.18 | 1.89 |
| D1 earn gap>=4 close | reg=NIFTY500<SMA200 | 49 | 57.14 | 0.87 | 1.67 | 4.28 | 1.09 | 1.83 | 2.68 | 1.15 | 1.31 |
| D1 earn gap>=4 close | reg=NIFTY500>SMA200 | 193 | 50.78 | 1.74 | 3.05 | 4.86 | 1.03 | 3.01 | 1.31 | 0.9 | 2.51 |
| D1 earn gap>=4 close | liq=10-25cr | 65 | 47.69 | 3.12 | 4.79 | 6.46 | 0.84 | -0.36 | 5.29 | 2.77 | 1.7 |
| D1 earn gap>=4 close | liq=25-100cr | 85 | 48.24 | 1.5 | 2.19 | 5.28 | 1.39 | 3.19 | 1.77 | 0.74 | 1.73 |
| D1 earn gap>=4 close | liq=>100cr | 92 | 58.7 | 0.53 | 1.87 | 3.04 | 0.87 | 4.52 | -1.09 | -0.55 | 1.34 |
| D2 earn gap>=6 close | all | 90 | 43.33 | 1.75 | 3.56 | 6.3 | 1.23 | 2.13 | 2.82 | 1.29 | 2.53 |
| D2 earn gap>=6 close | fold=F1 16-18 | 14 | 35.71 | 3.68 | 13.2 | 10.44 | 1.82 | 3.17 | 1.82 | 0.27 | 1.1 |
| D2 earn gap>=6 close | fold=F2 19-21 | 36 | 52.78 | 0.85 | 2.33 | 4.54 | 0.55 | 1.08 | 4.02 | 1.38 | 1.43 |
| D2 earn gap>=6 close | fold=F3 22-24 | 40 | 37.5 | 1.87 | 1.28 | 6.44 | 1.64 | 2.76 | 2.04 | 0.59 | 1.72 |
| D2 earn gap>=6 close | reg=NIFTY500<SMA200 | 19 | 52.63 | 1.88 | 2.46 | 7.77 | 2.17 | -0.07 | 8.65 | 2.21 | 1.14 |
| D2 earn gap>=6 close | reg=NIFTY500>SMA200 | 71 | 40.85 | 1.71 | 3.85 | 5.91 | 0.98 | 2.75 | 1.18 | 0.46 | 2.12 |
| D2 earn gap>=6 close | liq=10-25cr | 35 | 40.0 | 3.73 | 5.6 | 8.57 | 1.43 | -0.33 | 5.92 | 2.39 | 1.75 |
| D2 earn gap>=6 close | liq=25-100cr | 28 | 35.71 | 1.5 | 2.99 | 7.28 | 1.64 | 3.83 | 2.85 | 0.58 | 1.76 |
| D2 earn gap>=6 close | liq=>100cr | 27 | 55.56 | -0.56 | 1.48 | 2.36 | 0.54 | 3.43 | -0.9 | -0.23 | 0.59 |
| D3 earn gap>=4 open | all | 669 | 72.2 | 0.44 | 1.0 | 2.24 | 2.54 | 1.35 | 0.89 | 1.32 | 0.99 |
| D3 earn gap>=4 open | fold=F1 16-18 | 104 | 78.85 | -1.39 | -0.18 | -0.29 | 1.5 | -0.16 | -0.13 | -0.09 | -0.76 |
| D3 earn gap>=4 open | fold=F2 19-21 | 252 | 71.83 | 1.2 | 2.24 | 4.43 | 4.17 | 1.36 | 3.07 | 2.23 | 1.31 |
| D3 earn gap>=4 open | fold=F3 22-24 | 313 | 70.29 | 0.43 | 0.39 | 1.32 | 1.57 | 1.84 | -0.53 | -0.66 | 1.22 |
| D3 earn gap>=4 open | reg=NIFTY500<SMA200 | 107 | 71.96 | 0.05 | 0.62 | 2.62 | 2.44 | 1.49 | 1.13 | 0.66 | 0.82 |
| D3 earn gap>=4 open | reg=NIFTY500>SMA200 | 562 | 72.24 | 0.51 | 1.07 | 2.17 | 2.56 | 1.32 | 0.85 | 1.15 | 0.61 |
| D3 earn gap>=4 open | liq=10-25cr | 215 | 70.23 | 0.77 | 1.39 | 2.63 | 2.73 | 0.08 | 2.54 | 2.18 | 1.06 |
| D3 earn gap>=4 open | liq=25-100cr | 249 | 74.3 | 0.42 | 0.82 | 2.39 | 2.82 | 1.51 | 0.88 | 0.72 | 1.31 |
| D3 earn gap>=4 open | liq=>100cr | 205 | 71.71 | 0.12 | 0.81 | 1.66 | 2.0 | 2.48 | -0.82 | -0.76 | 0.77 |
| D4 earn gap>=6 open | all | 211 | 65.4 | 1.44 | 2.74 | 4.71 | 3.96 | 1.31 | 3.41 | 2.33 | 3.0 |
| D4 earn gap>=6 open | fold=F1 16-18 | 33 | 72.73 | 0.18 | 4.25 | 2.98 | 4.89 | 0.51 | 2.47 | 0.7 | 0.23 |
| D4 earn gap>=6 open | fold=F2 19-21 | 78 | 66.67 | 2.41 | 4.24 | 7.12 | 5.24 | 1.5 | 5.62 | 1.89 | 2.16 |
| D4 earn gap>=6 open | fold=F3 22-24 | 100 | 62.0 | 1.1 | 1.06 | 3.42 | 2.65 | 1.42 | 1.99 | 1.21 | 2.36 |
| D4 earn gap>=6 open | reg=NIFTY500<SMA200 | 36 | 66.67 | 1.31 | 1.56 | 5.94 | 3.5 | 1.47 | 4.47 | 1.37 | 1.46 |
| D4 earn gap>=6 open | reg=NIFTY500>SMA200 | 175 | 65.14 | 1.47 | 2.98 | 4.46 | 4.05 | 1.28 | 3.19 | 1.96 | 2.65 |
| D4 earn gap>=6 open | liq=10-25cr | 73 | 58.9 | 2.02 | 3.26 | 5.14 | 4.13 | 0.58 | 4.56 | 2.09 | 1.8 |
| D4 earn gap>=6 open | liq=25-100cr | 83 | 69.88 | 0.95 | 2.38 | 5.25 | 4.78 | 0.68 | 4.57 | 1.66 | 1.93 |
| D4 earn gap>=6 open | liq=>100cr | 55 | 67.27 | 1.42 | 2.58 | 3.33 | 2.48 | 3.21 | 0.12 | 0.05 | 1.86 |
| C1 non-earn gap>=4 open | all | 3459 | 83.56 | -1.3 | -1.25 | -0.7 | 0.54 | 0.61 | -1.31 | -4.51 | -3.61 |
| C1 non-earn gap>=4 open | fold=F1 16-18 | 534 | 82.02 | -1.87 | -1.91 | -2.79 | 0.09 | -0.47 | -2.32 | -5.33 | -3.49 |
| C1 non-earn gap>=4 open | fold=F2 19-21 | 1816 | 82.87 | -1.28 | -1.19 | 0.17 | 0.72 | 0.81 | -0.64 | -1.35 | -2.23 |
| C1 non-earn gap>=4 open | fold=F3 22-24 | 1109 | 85.45 | -1.06 | -1.03 | -1.13 | 0.46 | 0.8 | -1.93 | -4.55 | -0.83 |
| C1 non-earn gap>=4 open | reg=NIFTY500<SMA200 | 1299 | 79.91 | -1.35 | -1.23 | 0.95 | 0.95 | 0.32 | 0.63 | 1.14 | -1.69 |
| C1 non-earn gap>=4 open | reg=NIFTY500>SMA200 | 2160 | 85.77 | -1.27 | -1.26 | -1.7 | 0.29 | 0.78 | -2.48 | -7.66 | -3.55 |
| C1 non-earn gap>=4 open | liq=10-25cr | 1087 | 83.04 | -1.64 | -1.73 | -1.0 | 0.36 | -0.11 | -0.88 | -1.91 | -5.59 |
| C1 non-earn gap>=4 open | liq=25-100cr | 1236 | 83.65 | -0.62 | -0.61 | -0.62 | 0.59 | 0.81 | -1.43 | -2.85 | -1.32 |
| C1 non-earn gap>=4 open | liq=>100cr | 1136 | 83.97 | -1.71 | -1.5 | -0.51 | 0.66 | 1.09 | -1.6 | -2.95 | -2.77 |
| C2 non-earn gap>=6 close | all | 283 | 70.21 | -1.47 | -2.37 | -1.11 | -0.26 | 2.11 | -3.27 | -2.43 | -2.14 |
| C2 non-earn gap>=6 close | fold=F1 16-18 | 61 | 63.93 | -2.75 | -3.41 | -5.24 | -0.39 | 4.76 | -10.53 | -3.85 | -2.64 |
| C2 non-earn gap>=6 close | fold=F2 19-21 | 158 | 70.89 | -1.04 | -2.24 | 0.61 | -0.1 | 0.85 | -0.13 | -0.07 | -1.19 |
| C2 non-earn gap>=6 close | fold=F3 22-24 | 64 | 74.6 | -1.34 | -1.71 | -1.42 | -0.54 | 2.83 | -4.39 | -2.0 | -0.24 |
| C2 non-earn gap>=6 close | reg=NIFTY500<SMA200 | 107 | 68.22 | -2.33 | -2.81 | 1.47 | 0.03 | -0.24 | 1.89 | 0.76 | -0.13 |
| C2 non-earn gap>=6 close | reg=NIFTY500>SMA200 | 176 | 71.43 | -0.95 | -2.1 | -2.69 | -0.43 | 3.53 | -6.38 | -4.28 | -1.77 |
| C2 non-earn gap>=6 close | liq=10-25cr | 68 | 70.59 | -1.18 | -2.26 | 0.33 | -0.18 | 1.21 | -1.04 | -0.42 | -0.16 |
| C2 non-earn gap>=6 close | liq=25-100cr | 98 | 65.98 | -0.6 | -1.43 | -0.69 | -0.22 | 4.32 | -5.36 | -2.93 | 0.33 |
| C2 non-earn gap>=6 close | liq=>100cr | 117 | 73.5 | -2.38 | -3.23 | -2.31 | -0.34 | 0.75 | -2.72 | -1.11 | -4.33 |

### T5. By year (₹10 cr)

| def | cut | N | sma10% | hold60% | hold60 ev-base% |
|---|---|---|---|---|---|
| D2 earn gap>=6 close | year=2016 | 6 | 9.04 | 23.33 | 11.61 |
| D2 earn gap>=6 close | year=2017 | 3 | -3.59 | -6.84 | -22.91 |
| D2 earn gap>=6 close | year=2018 | 5 | 1.62 | 5.36 | 6.86 |
| D2 earn gap>=6 close | year=2019 | 4 | 5.06 | 4.76 | 8.74 |
| D2 earn gap>=6 close | year=2020 | 14 | -0.79 | 0.79 | 0.78 |
| D2 earn gap>=6 close | year=2021 | 18 | 1.2 | 7.41 | 5.38 |
| D2 earn gap>=6 close | year=2022 | 16 | 5.99 | 13.33 | 7.54 |
| D2 earn gap>=6 close | year=2023 | 8 | 1.67 | 5.46 | 8.46 |
| D2 earn gap>=6 close | year=2024 | 16 | -2.15 | 0.04 | -6.68 |
| D4 earn gap>=6 open | year=2016 | 10 | 6.91 | 16.08 | 11.85 |
| D4 earn gap>=6 open | year=2017 | 13 | -3.33 | -4.68 | -4.12 |
| D4 earn gap>=6 open | year=2018 | 10 | -2.0 | -0.17 | 1.66 |
| D4 earn gap>=6 open | year=2019 | 6 | 4.45 | 4.29 | 6.67 |
| D4 earn gap>=6 open | year=2020 | 37 | -0.33 | 3.49 | 1.48 |
| D4 earn gap>=6 open | year=2021 | 35 | 4.95 | 11.44 | 9.81 |
| D4 earn gap>=6 open | year=2022 | 26 | 7.08 | 11.15 | 9.12 |
| D4 earn gap>=6 open | year=2023 | 24 | 1.15 | 4.02 | 4.03 |
| D4 earn gap>=6 open | year=2024 | 50 | -2.03 | -0.9 | -2.69 |
| C1 non-earn gap>=4 open | year=2016 | 92 | -1.36 | -0.99 | -0.94 |
| C1 non-earn gap>=4 open | year=2017 | 199 | -0.58 | -1.25 | -1.38 |
| C1 non-earn gap>=4 open | year=2018 | 243 | -3.13 | -4.74 | -3.61 |
| C1 non-earn gap>=4 open | year=2019 | 283 | -0.76 | -3.32 | -2.05 |
| C1 non-earn gap>=4 open | year=2020 | 1061 | -1.76 | 1.39 | 0.24 |
| C1 non-earn gap>=4 open | year=2021 | 472 | -0.49 | -0.47 | -1.77 |
| C1 non-earn gap>=4 open | year=2022 | 324 | -1.14 | -2.99 | -2.97 |
| C1 non-earn gap>=4 open | year=2023 | 252 | 1.21 | 2.84 | 1.9 |
| C1 non-earn gap>=4 open | year=2024 | 533 | -2.09 | -1.87 | -3.12 |

### T6. Neglect / day-volume filters under the wide exits (earnings gaps only, ₹10 cr)

| entry | gap>= | neglect | vol>= | N | N/yr | sma20% | hold60% | hold60 R | hold60 F1% | hold60 F2% | hold60 F3% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| open | 4 | - | - | 669 | 74.33 | 1.0 | 2.24 | 2.54 | -0.29 | 4.43 | 1.32 |
| open | 4 | y | - | 491 | 54.56 | 0.87 | 2.28 | 2.36 | -0.97 | 5.88 | 1.08 |
| open | 6 | - | - | 211 | 23.44 | 2.74 | 4.71 | 3.96 | 2.98 | 7.12 | 3.42 |
| open | 6 | y | - | 154 | 17.11 | 2.06 | 3.94 | 3.61 | -1.41 | 7.43 | 3.47 |
| open | 8 | - | - | 91 | 10.11 | 3.64 | 6.55 | 4.5 | 3.37 | 8.71 | 5.82 |
| open | 8 | y | - | 64 | 7.11 | 3.39 | 5.83 | 4.77 | -0.32 | 10.22 | 5.05 |
| close | 4 | - | - | 242 | 26.89 | 2.77 | 4.75 | 1.04 | 4.68 | 6.61 | 3.43 |
| close | 4 | - | 2 | 221 | 24.56 | 2.79 | 4.62 | 0.91 | 5.92 | 6.15 | 3.24 |
| close | 4 | y | - | 184 | 20.44 | 2.2 | 4.41 | 1.06 | 1.74 | 8.38 | 2.84 |
| close | 4 | y | 2 | 173 | 19.22 | 1.98 | 3.97 | 0.91 | 2.35 | 6.67 | 2.83 |
| close | 6 | - | - | 90 | 10.0 | 3.56 | 6.3 | 1.23 | 10.44 | 4.54 | 6.44 |
| close | 6 | - | 2 | 84 | 9.33 | 3.99 | 6.84 | 1.33 | 11.79 | 4.97 | 6.73 |
| close | 6 | y | - | 64 | 7.11 | 3.24 | 7.4 | 1.54 | 4.58 | 9.44 | 6.81 |
| close | 6 | y | 2 | 62 | 6.89 | 3.2 | 7.31 | 1.53 | 4.58 | 8.65 | 7.16 |
| close | 8 | - | - | 42 | 4.67 | 2.91 | 7.26 | 1.71 | 8.38 | 1.49 | 10.73 |
| close | 8 | - | 2 | 38 | 4.22 | 3.47 | 7.98 | 1.85 | 10.95 | 1.13 | 10.73 |
| close | 8 | y | - | 27 | 3.0 | 4.44 | 10.78 | 2.51 | 4.24 | 12.92 | 11.56 |
| close | 8 | y | 2 | 26 | 2.89 | 4.2 | 10.22 | 2.44 | 4.24 | 10.43 | 11.56 |

### T7. 5m ORH vs open/close, 2022-24, events with 5m bars (₹10 cr)

| subset | entry | N | N/yr | risk% | f20% | sma10% | sma20% | hold60% | win% | stop day0% | 2022% | 2023% | 2024% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gap>=4 earn=- | open | 1077 | 359.0 | 3.34 | 1.0 | -1.24 | -1.23 | -0.94 | 21.45 |  | -0.42 | -0.58 | -1.92 |
| gap>=4 earn=- | close | 351 | 117.0 | 4.03 | 1.84 | -0.08 | -0.26 | 0.46 | 28.49 |  | -0.62 | 1.31 | -0.48 |
| gap>=4 earn=- | or5 | 477 | 159.0 | 2.84 | 2.83 | -0.25 | -0.28 | 0.44 | 26.42 | 29.56 | 0.02 | 0.96 | -0.83 |
| gap>=4 earn=- | or15 | 406 | 135.33 | 3.22 | 2.56 | -0.24 | -0.34 | 0.43 | 28.82 | 21.43 | -0.05 | 1.42 | -0.87 |
| gap>=4 earn=- | or30 | 346 | 115.33 | 3.59 | 2.08 | -0.3 | -0.4 | 0.46 | 28.61 | 16.47 | -0.17 | 1.18 | -0.85 |
| gap>=4 earn=y | open | 244 | 81.33 | 3.52 | 3.12 | 0.32 | 0.4 | 1.99 | 33.2 |  | 2.21 | 1.86 | -1.33 |
| gap>=4 earn=y | close | 91 | 30.33 | 4.5 | 4.95 | 2.18 | 2.27 | 5.94 | 43.96 |  | 3.48 | 3.94 | -0.04 |
| gap>=4 earn=y | or5 | 130 | 43.33 | 3.29 | 5.55 | 1.33 | 1.39 | 3.36 | 40.77 | 26.92 | 2.61 | 1.31 | 0.62 |
| gap>=4 earn=y | or15 | 103 | 34.33 | 3.86 | 6.14 | 2.15 | 2.16 | 4.54 | 49.51 | 13.59 | 3.2 | 2.52 | 1.39 |
| gap>=4 earn=y | or30 | 86 | 28.67 | 4.17 | 5.54 | 2.03 | 1.96 | 4.8 | 44.19 | 10.47 | 2.88 | 2.05 | 1.53 |
| gap>=4 earn=n | open | 833 | 277.67 | 3.31 | 0.37 | -1.69 | -1.7 | -1.8 | 18.01 |  | -1.15 | -1.38 | -2.09 |
| gap>=4 earn=n | close | 260 | 86.67 | 3.84 | 0.74 | -0.87 | -1.14 | -1.46 | 23.08 |  | -2.16 | 0.23 | -0.61 |
| gap>=4 earn=n | or5 | 347 | 115.67 | 2.7 | 1.8 | -0.85 | -0.91 | -0.66 | 21.04 | 30.55 | -0.84 | 0.78 | -1.34 |
| gap>=4 earn=n | or15 | 303 | 101.0 | 3.01 | 1.33 | -1.05 | -1.2 | -0.97 | 21.78 | 24.09 | -1.06 | 0.91 | -1.6 |
| gap>=4 earn=n | or30 | 260 | 86.67 | 3.37 | 0.92 | -1.07 | -1.18 | -0.98 | 23.46 | 18.46 | -1.14 | 0.84 | -1.61 |
| gap>=6 earn=- | open | 243 | 81.0 | 4.53 | 0.46 | -1.65 | -1.81 | -0.7 | 22.63 |  | 1.62 | 0.84 | -3.56 |
| gap>=6 earn=- | close | 66 | 22.0 | 5.84 | 2.04 | 1.3 | 0.58 | 4.2 | 34.85 |  | 5.36 | 7.03 | -3.06 |
| gap>=6 earn=- | or5 | 106 | 35.33 | 3.37 | 2.68 | 0.45 | 0.26 | 2.7 | 32.08 | 29.25 | 3.43 | 4.96 | -2.05 |
| gap>=6 earn=- | or15 | 91 | 30.33 | 3.77 | 2.65 | 0.73 | 0.5 | 3.31 | 34.07 | 19.78 | 4.28 | 5.84 | -2.05 |
| gap>=6 earn=- | or30 | 78 | 26.0 | 4.14 | 2.06 | 0.84 | 0.58 | 3.91 | 35.9 | 14.1 | 4.59 | 5.62 | -2.26 |
| gap>=6 earn=y | open | 75 | 25.0 | 4.52 | 6.42 | 2.0 | 2.19 | 4.79 | 45.33 |  | 9.42 | 3.04 | -2.06 |
| gap>=6 earn=y | close | 30 | 10.0 | 7.0 | 5.61 | 3.14 | 2.98 | 9.2 | 46.67 |  | 7.78 | 2.71 | -1.66 |
| gap>=6 earn=y | or5 | 44 | 14.67 | 3.67 | 7.57 | 2.05 | 1.98 | 5.98 | 47.73 | 29.55 | 5.32 | 2.06 | -0.57 |
| gap>=6 earn=y | or15 | 35 | 11.67 | 4.08 | 7.8 | 3.36 | 3.07 | 7.85 | 57.14 | 17.14 | 6.8 | 2.81 | 0.77 |
| gap>=6 earn=y | or30 | 31 | 10.33 | 4.66 | 7.5 | 3.44 | 3.12 | 8.65 | 54.84 | 12.9 | 6.91 | 1.97 | 0.92 |
| gap>=6 earn=n | open | 168 | 56.0 | 4.56 | -2.25 | -3.28 | -3.6 | -3.15 | 12.5 |  | -4.82 | -0.12 | -4.11 |
| gap>=6 earn=n | close | 36 | 12.0 | 5.6 | -1.02 | -0.23 | -1.41 | 0.02 | 25.0 |  | -4.31 | 10.39 | -3.71 |
| gap>=6 earn=n | or5 | 62 | 20.67 | 3.13 | -0.91 | -0.69 | -0.96 | 0.38 | 20.97 | 29.03 | -0.35 | 7.07 | -2.73 |
| gap>=6 earn=n | or15 | 56 | 18.67 | 3.46 | -0.68 | -0.91 | -1.11 | 0.48 | 19.64 | 21.43 | -0.41 | 7.66 | -3.2 |
| gap>=6 earn=n | or30 | 47 | 15.67 | 3.89 | -1.69 | -0.88 | -1.1 | 0.78 | 23.4 | 14.89 | -0.05 | 8.04 | -3.55 |

### T8. R for the 5m entries, earnings gaps, 2022-24 (covered days)

| gap>= | entry | early vol>= | N | N/yr | risk med% | hold60% | hold60 R | sma20% | hold60 ex top3% | hold60 2022% | hold60 2023% | hold60 2024% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.04 | open | - | 244 | 81.33 | 3.52 | 1.99 | 2.04 | 0.4 | 1.32 | 2.99 | 5.86 | -0.37 |
| 0.04 | close | - | 91 | 30.33 | 4.5 | 5.94 | 1.68 | 2.27 | 4.44 | 6.09 | 11.85 | 1.82 |
| 0.04 | or5 | - | 130 | 43.33 | 3.29 | 3.36 | 1.01 | 1.39 | 2.31 | 3.51 | 6.03 | 2.01 |
| 0.04 | or5 | 0.5 | 114 | 38.0 | 3.34 | 4.31 | 1.3 | 1.79 | 3.14 | 5.38 | 6.32 | 2.71 |
| 0.04 | or15 | - | 103 | 34.33 | 3.86 | 4.54 | 1.12 | 2.16 | 3.27 | 4.3 | 9.23 | 2.79 |
| 0.04 | or15 | 0.5 | 93 | 31.0 | 3.89 | 5.46 | 1.36 | 2.59 | 4.08 | 6.15 | 9.23 | 3.42 |
| 0.04 | or30 | - | 86 | 28.67 | 4.17 | 4.8 | 1.2 | 1.96 | 3.34 | 5.31 | 8.62 | 3.11 |
| 0.04 | or30 | 0.5 | 80 | 26.67 | 4.14 | 5.51 | 1.37 | 2.3 | 3.96 | 7.75 | 8.62 | 3.25 |
| 0.06 | open | - | 75 | 25.0 | 4.52 | 4.79 | 3.33 | 2.19 | 2.67 | 15.82 | 5.8 | -1.02 |
| 0.06 | close | - | 30 | 10.0 | 7.0 | 9.2 | 2.31 | 2.98 | 4.69 | 18.83 | 7.48 | -0.2 |
| 0.06 | or5 | - | 44 | 14.67 | 3.67 | 5.98 | 1.72 | 1.98 | 3.15 | 12.17 | 5.04 | 1.4 |
| 0.06 | or5 | 0.5 | 41 | 13.67 | 3.76 | 6.72 | 1.92 | 2.42 | 3.72 | 14.56 | 5.04 | 1.64 |
| 0.06 | or15 | - | 35 | 11.67 | 4.08 | 7.85 | 1.91 | 3.07 | 4.4 | 15.24 | 6.76 | 2.25 |
| 0.06 | or15 | 0.5 | 33 | 11.0 | 4.08 | 8.59 | 2.09 | 3.53 | 4.99 | 16.96 | 6.76 | 2.62 |
| 0.06 | or30 | - | 31 | 10.33 | 4.66 | 8.65 | 1.96 | 3.12 | 4.8 | 16.43 | 5.92 | 2.73 |
| 0.06 | or30 | 0.5 | 30 | 10.0 | 4.57 | 9.12 | 2.06 | 3.41 | 5.18 | 18.42 | 5.92 | 2.73 |

### T9. 5m coverage bias (2022-24, all gap events; daily-entry outcomes)

| gap>= | has5m | N | earn share% | gap med% | adv20 med cr | open sma10% | close sma10% | open f20% |
|---|---|---|---|---|---|---|---|---|
| 0.04 | True | 1077 | 22.66 | 4.96 | 86.4 | -1.24 | -0.08 | 1.0 |
| 0.04 | False | 345 | 20.0 | 4.99 | 51.52 | 0.85 | 1.64 | -0.64 |
| 0.06 | True | 243 | 30.86 | 7.52 | 88.78 | -1.65 | 1.3 | 0.46 |
| 0.06 | False | 104 | 24.04 | 7.68 | 57.78 | -2.73 | -2.54 | -2.7 |
| 0.08 | True | 98 | 33.67 | 9.99 | 97.84 | -2.37 | 3.69 | 0.33 |
| 0.08 | False | 45 | 24.44 | 9.77 | 56.25 | -3.53 | -3.85 | -1.02 |

### T10. Candidates at ₹5 cr: liquidity buckets, S2 regime gate, folds, outlier dependence (hold60 exit)

| def | cut | N | N/yr | hold60% | hold60 med% | hold60 R | sma20% | hold60% ex top5 | win% | avg hold |
|---|---|---|---|---|---|---|---|---|---|---|
| A earn gap>=6 close | all >=5cr | 112 | 12.44 | 7.26 | -2.08 | 1.46 | 4.6 | 4.88 | 45.54 | 34.98 |
| A earn gap>=6 close | liq 5-10cr | 22 | 2.44 | 11.15 | 10.53 | 2.4 | 8.88 | 3.28 | 54.55 | 40.09 |
| A earn gap>=6 close | liq 10-25cr | 35 | 3.89 | 8.57 | -2.0 | 1.43 | 5.6 | 1.27 | 45.71 | 36.0 |
| A earn gap>=6 close | liq 25-100cr | 28 | 3.11 | 7.28 | -3.08 | 1.64 | 2.99 | 0.0 | 46.43 | 36.04 |
| A earn gap>=6 close | liq >100cr | 27 | 3.0 | 2.36 | -2.55 | 0.54 | 1.48 | -3.26 | 37.04 | 28.41 |
| A earn gap>=6 close | gate False | 58 | 6.44 | 8.31 | -0.49 | 1.7 | 4.88 | 3.98 | 50.0 | 37.12 |
| A earn gap>=6 close | gate True | 54 | 6.0 | 6.12 | -2.13 | 1.2 | 4.3 | 2.11 | 40.74 | 32.69 |
| A earn gap>=6 close | >=5cr F1 | 16 | 1.78 | 8.02 | -3.73 | 1.46 | 12.38 | -5.11 | 37.5 | 36.5 |
| A earn gap>=6 close | >=5cr F2 | 49 | 5.44 | 7.63 | -2.05 | 1.36 | 4.88 | 3.6 | 42.86 | 32.31 |
| A earn gap>=6 close | >=5cr F3 | 47 | 5.22 | 6.6 | 0.16 | 1.56 | 1.66 | 2.03 | 51.06 | 37.26 |
| A earn gap>=6 open | all >=5cr | 279 | 31.0 | 4.41 | -3.46 | 3.95 | 2.58 | 2.77 | 28.32 | 21.32 |
| A earn gap>=6 open | liq 5-10cr | 68 | 7.56 | 3.46 | -3.71 | 3.92 | 2.09 | 0.12 | 29.41 | 21.74 |
| A earn gap>=6 open | liq 10-25cr | 73 | 8.11 | 5.14 | -2.38 | 4.13 | 3.26 | 0.83 | 32.88 | 24.92 |
| A earn gap>=6 open | liq 25-100cr | 83 | 9.22 | 5.25 | -3.99 | 4.78 | 2.38 | 0.31 | 24.1 | 18.37 |
| A earn gap>=6 open | liq >100cr | 55 | 6.11 | 3.33 | -2.82 | 2.48 | 2.58 | -0.36 | 27.27 | 20.45 |
| A earn gap>=6 open | gate False | 132 | 14.67 | 5.83 | -2.96 | 4.25 | 3.19 | 2.9 | 32.58 | 24.09 |
| A earn gap>=6 open | gate True | 147 | 16.33 | 3.14 | -3.81 | 3.68 | 2.03 | 0.83 | 24.49 | 18.82 |
| A earn gap>=6 open | >=5cr F1 | 46 | 5.11 | 1.58 | -3.22 | 3.6 | 3.24 | -3.67 | 19.57 | 17.74 |
| A earn gap>=6 open | >=5cr F2 | 115 | 12.78 | 6.79 | -3.35 | 5.42 | 4.04 | 3.3 | 28.7 | 21.37 |
| A earn gap>=6 open | >=5cr F3 | 118 | 13.11 | 3.19 | -3.77 | 2.65 | 0.89 | 1.16 | 31.36 | 22.65 |
| B earn gap>=4 close | all >=5cr | 291 | 32.33 | 5.15 | -2.81 | 1.15 | 3.01 | 3.98 | 34.36 | 29.05 |
| B earn gap>=4 close | liq 5-10cr | 49 | 5.44 | 7.18 | -2.54 | 1.65 | 4.21 | 3.45 | 40.82 | 30.92 |
| B earn gap>=4 close | liq 10-25cr | 65 | 7.22 | 6.46 | -2.1 | 0.84 | 4.79 | 2.42 | 40.0 | 32.15 |
| B earn gap>=4 close | liq 25-100cr | 85 | 9.44 | 5.28 | -3.15 | 1.39 | 2.19 | 2.13 | 35.29 | 30.06 |
| B earn gap>=4 close | liq >100cr | 92 | 10.22 | 3.04 | -3.2 | 0.87 | 1.87 | 0.05 | 26.09 | 24.95 |
| B earn gap>=4 close | gate False | 159 | 17.67 | 5.19 | -2.65 | 1.2 | 3.19 | 3.12 | 33.96 | 27.43 |
| B earn gap>=4 close | gate True | 132 | 14.67 | 5.11 | -3.24 | 1.07 | 2.79 | 3.25 | 34.85 | 31.01 |
| B earn gap>=4 close | >=5cr F1 | 44 | 4.89 | 4.01 | -3.56 | 0.88 | 4.24 | -1.67 | 27.27 | 27.52 |
| B earn gap>=4 close | >=5cr F2 | 110 | 12.22 | 7.72 | -2.55 | 1.51 | 5.03 | 4.98 | 39.09 | 31.33 |
| B earn gap>=4 close | >=5cr F3 | 137 | 15.22 | 3.47 | -2.74 | 0.93 | 0.99 | 1.8 | 32.85 | 27.72 |
