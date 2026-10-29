# S1 `stage2-contraction-breakout` re-audit (Fable, 2026-10-25)

Read-only audit of strategy version `e8cfee88-c0a4-4e52-b17d-23b2b16c7b7c` (draft, matches the seed
YAML) against `backend/app/hat` at 3569d1d0 and the store `/data/workspace/hat-data-isin`.
Method: read the scan, trigger, fill, exit, sizing, ledger, metrics, feature and store code;
re-derived features, adjustments and RS percentiles from `bars_daily_raw` + `hat_corporate_action`
+ `hat_isin_lineage` by hand (polars, read-only); SELECT-only checks on `hat_live`. Nothing was
run (no backtest, pipeline or features job) and nothing was written outside this file and the
session scratchpad.

## Blockers (result would be wrong)

None found.

## Majors

**M1. The backtest does not trade S1's trigger as live will: `volume_pace` is ignored and
`confirm: close` has no daily-bar counterpart (documented known gap, but it changes the result).**
- `backtest/spec.py:71-75,129` — `trigger_is_level_break_only` names every playbook with an
  enabled `volume_pace` trigger; `backtest/loop.py:111-113` — the loop triggers on the level break
  only. S1 enables `volume_pace {vs_avg50: 1.5}` (config `playbooks[0].trigger[1]`, seed line 42)
  and `price_breaks_level {bar: 5m, confirm: close}`.
- `backtest/fills.py:65-90` (`entry_fill`): any day whose high clears the pivot by a tick fills
  at pivot + tick (or at the open on a gap over); live (`criteria/live.py:price_breaks_level`)
  also needs the 5-minute bar to close at or above the level.
- Concrete failure: a breakout day with volume running at 0.8x the 50-day average, or a spike
  above the pivot whose 5m bar closes back below it, is a trade in the backtest and a refusal
  live. The backtest therefore measures a looser rule than the one that will trade, and
  `GAP_PLAYBOOKS` blocks promotion of this version on its evidence.
- Fix (1-2 lines): for the research version either disable `volume_pace`, or set
  `price_breaks_level: {entry_timing: daily_close, volume_vs_avg: 1.5}` (the documented
  backtestable stand-in); state in the run notes that `confirm: close` is not modelled.

## Minors

**m1. `hat_index_member` misses the demerger placeholder memberships (data, no S1 impact).**
- NSE put Jio Financial in NIFTY 500 from 2023-07-20 (dummy, listed 2023-08-21) and removed it
  on 2023-09-07; the table has JIOFIN only from 2024-03-28 (`source_notice ind_prs28022024.pdf`).
  ITC Hotels: in from 2025-01-06 (listed 2025-01-29), out 2025-02-10; table has it only from
  2025-09-30. Sources: niftyindices press releases ind_prs05092023, ind_prs06022025_1,
  ind_prs30122024 (web search 2026-10-25).
- Member counts on 2023-07-21 and 2023-08-25 are 501 without JIOFIN, so the rebuilt history
  carries a different 501st name there (unverified which).
- Concrete failure: a scan on 2023-08-25 reads a universe without JIOFIN. For S1 nothing
  changes: a stock listed 4 sessions earlier has null sma200/52w features and fails closed.
  Any strategy with short lookbacks would differ.
- Fix: add the two intervals to `nifty500-membership.csv` and reload (`load-index-membership`).

**m2. Cost model `cnc-delivery-1` is slightly light (owner-pending by its own header).**
- `cost_models/cnc-delivery-1.yaml`: no DP charge on sells (Rs 15.34 + GST per sell order at
  the usual discount brokers), NSE transaction charge fixed at 0.00297% for the whole 2016-2026
  window (it was 0.00325%-0.00345% before Oct 2024). Unverified against the owner's broker.
- Concrete effect: a Rs 50,000 round trip is under-charged by ~Rs 20-25 (DP) and ~Rs 0.3
  (txn). Negligible for the R statistics; note it before comparing to real fills.
- Fix: add `{name: dp_charge, sides: [sell], per_order: "15.34", taxable: true}` as a new
  version file.

**m3. `DailyInputs.avg50_volume` is None in the backtest (`backtest/loop.py` `_daily`).**
- Harmless today because the loop never evaluates `volume_pace` (M1). If the loop ever does,
  the criterion returns `no_data` and refuses every entry. Fix: feed `adv50` (or the
  50-session mean of basis volume from `MarketView`) when wiring volume_pace into the loop.

## What was checked and found correct

Data (hand recomputation, read-only):
- Adjusted series and features: for 16 (stock, date) rows across INFY, NESTLEIND (2 ISINs),
  TATASTEEL (2), RELIANCE, HDFCBANK (3 ISINs), BAJAJFINSV (2), IRCTC (2), ITC, TMPV, on dates
  straddling splits, bonuses, a rights issue and three demergers, sma50/150/200, high_52w,
  low_52w, adv20, ret63, ret252 and rs_weighted recomputed from raw bars x chain factors x
  dividend factors (1 - cash/prev raw close), divided by the date's dividend factor, match
  `features_daily` exactly (max rel diff 1e-13; adv20 1e-13).
- Continuity across 14 price actions since 2016: raw open gap vs factor, e.g. NESTLEIND
  2024-01-05 split raw gap 0.1016 vs factor 0.1 (adj gap 0.983), TATASTEEL 2022-07-28 0.1023 vs
  0.1, BAJAJFINSV 2022-09-13 split x bonus 0.1024 vs 0.2 x 0.5, RELIANCE 2023-07-20 demerger
  0.9079 vs 0.9079, ITC 2025-01-06 0.946 vs 0.9643 (`resulting_first_close` basis), TMPV
  2025-10-14 0.6054 vs 0.6054 (`known_on` 2025-10-20: the 4 sessions between are pending days
  the loop refuses to scan or enter, `chain_pending`).
- The two NESTLEIND copies of each action (old and new ISIN rows) are de-duplicated per chain
  (`data/chains.py:99-123`, nearest-to-head copy wins); no duplicate (instrument, ex_date,
  type) rows exist in `hat_corporate_action`.
- `rs_pct`: recomputed on 2016-01-04, 2019-10-15, 2022-03-31, 2024-07-08 as
  100 x average rank / count over ordinary-equity ISINs with a value (all NSE equities, not only
  NIFTY 500: 1401/1534/1616/1868 names) — equal to stored to 1e-14; no non-equity row has a
  percentile, no equity row lacks one.
- Membership: counts 500/501/501/500/499 on 2016-01-04, 2018-06-01, 2022-03-31, 2025-09-30,
  2026-10-24; ISIN changes hand over on the ex-date with contiguous intervals (NESTLEIND
  2024-01-05, TATASTEEL 2022-07-29, HDFCBANK 2019-09-20, BAJAJFINSV 2022-09-14, IRCTC
  2021-10-29) which `point_in_time_members` merges by chain; `scan_night_members` shifts each
  interval to the night before so an entrant is on its first day's watchlist and a leaver is
  not. Cover check uses `start..end` (not the night before start), so a 2016-01-01 run passes.
- Regime index: config stores `"NIFTY 500"`, present in `index_daily` (with NIFTY 50, INDIA VIX,
  NIFTY 500 TRI, NIFTY SMALLCAP 250) from 2012-02-21, so the 50-SMA gate has data from day one.

Code (definitions and mechanics):
- No lookahead: watchlist for D is built from bars and features through the previous session
  (`loop._publish`, `view.window(prev)`), regime from closes through prev, membership as of the
  night before; `min_price` reads the raw close (`criteria/universe.py:57-63`), turnover the
  traded value; levels (pivot, contraction low) are rescaled to D's dividend basis.
- Minervini template as configured: strict `sma_above`, `sma_rising` (200, 21 sessions) by
  exact sums, 52-week window of 252 bars including today, `pct_from_52w_low` 30 as
  close >= 1.30 x low, `pct_from_52w_high` 25 as close >= 0.75 x high, `rs_rank` hard 70 on the
  all-market percentile, `close_vs_pivot` 0 as close <= pivot; VCP depth ratios <= 0.75, final
  depth <= 10%, dry-up <= 0.7 x the 50 sessions before the base; candidates without a pivot are
  dropped (`needs_setup_level`); vcp is a score criterion in seed and DB alike (weight 2).
- Fills and exits: gap over fills at the open, else pivot + tick; 20 bps slippage and the cost
  model on both legs; `max_chase` 5% tested on the limit vs the level with the circuit state
  from the bar; stop = contraction low x 0.995 floored to tick, trade skipped if > 8% below
  entry; R from the actual (slipped) fill; day order is open-gap stop -> down leg (stop at
  min(open, stop)) -> up leg (bisection on R thresholds, monotone stack) -> close phase (close
  <= stop fills at the stop; `close_below_sma` on the decision price; ambiguous raised-stop days
  optimistic by convention); breakeven only raises; partial 33% floors to >= 1 share; stop
  never lowered; exposure ladder stepped per closed trade (`_sync_ladder`).
- Accounting: dividends credited to shares held at the start of the ex-date (and to the trade's
  R), never on an ex-date entry; hindsight price basis means no rescale is needed while held
  and `qty_real` is reported; CAGR on 252 sessions/year, max DD from the equity curve,
  expectancy = mean R.
