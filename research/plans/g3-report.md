# G3: in-sample reruns on verified data and code

The p1–p6 portfolios (p5 is the rotation) were rerun in-sample on m3 against the resynced corporate-action
tables, with all 20 owner values dated. Each was run twice:

- **pre-#332**: code 2121493, the commit before the 09:20 fill change.
- **main**: d079b11 for p1–p4 and p6; d6d99b6 for p5, which includes the #335 clamp.

#334 (correction writing and its check) and #335 (the rotation `_quote` clamp) change nothing that p1–p4 or p6
read. So for those portfolios, d079b11 equals current main.

Each run was diffed trade by trade with `python -m app.hat.backtest.rundiff` (#333) in three pairs: old → pre-#332
(data and pre-#332 code), pre-#332 → main (the 09:20 change alone) and old → main (the total). Copies of the main
runs' summaries and all three diffs are in `/data/workspace/backtests/g3/<portfolio>/`.

## Summary

CAGR % | trades | fees ₹ | max DD %:

| Run | Old | Pre-#332 | Main | Causes (see below) |
| --- | --- | --- | --- | --- |
| p1 ep-only | −0.30 · 2 · 577 · 0.90 | −0.29 · 2 · 577 · 0.85 | −0.29 · 2 · 577 · 0.85 | C2 |
| p2 vcp | 6.12 · 154 · 47,277 · 23.65 | 6.08 · 154 · 47,287 · 23.69 | 6.16 · 154 · 47,298 · 23.55 | C1, C3, C8 |
| p3 vcp-ep | 3.42 · 158 · 26,433 · 13.50 | 4.08 · 158 · 26,641 · 12.56 | 4.06 · 158 · 26,632 · 12.60 | C1, C2, C4, C8 |
| p4 vcp-ep-etf | 1.82 · 158 · 24,693 · 22.32 | 2.49 · 158 · 24,939 · 22.01 | 2.49 · 158 · 24,935 · 22.01 | C1, C2, C4, C8 |
| p5 rotation | 23.36 · 487 · 194,246 · 35.39 | 23.32 · 486 · 198,091 · 35.43 | 23.19 · 486 · 196,845 · 35.69 | C1, C5, C6, C9 |
| p6 ep-a | −1.32 · 14 · 3,717 · 7.02 | −1.64 · 16 · 4,155 · 9.68 | −1.64 · 16 · 4,155 · 9.68 | C1, C2, C3b, C7, C10 |

Every trade difference is assigned to a named cause below; the unexplained bucket is empty. The 09:20 change (C8, C9)
moves CAGR by +0.08 (p2), −0.02 (p3), +0.001 (p4), −0.135 (p5) and nothing in p1 or p6.

Three defects were found and fixed during G3:
- **#331**: run folders refused the ledger doc, so no run could publish.
- **#334**: 20 owner values were stored undated, which held those names factor-pending forever.
- **#335**: rotation 09:20 estimates were not clamped to the day's range. The ledger check caught it
  (`fill_outside_bar` ×102), so p5 failed on d079b11.

No engine code was changed in G3 itself.

## Named causes

- **C1 Cost model cnc-delivery-1 → cnc-delivery-2** (#314 B3; the default changed). The schedule dates moved too
  (2021-08-05, 2022-07-18, 2023-04-01, 2024-04-01, 2024-10-01). Recomputing the old trades' fees under v1
  reproduces the recorded fees to the paisa.
  - Effect, old → pre-#332: p2 has 76 trades with only fees changed, plus 64 resized trades. Fees changed on every
    changed trade in p2–p6.
  - The resizing (qty only) follows from the different cash path.
- **C2 5m LIMIT buy filled no worse than its limit** (#314 B4, `costs.BacktestFills.fill`). Every 5m entry is exactly
  ×0.998, the 20 bps slippage removed: p1 2, p3 132, p4 132, p6 9. p2 enters on the daily estimate and has none.
- **C3 Close-rule sale refused at a close locked at the lower band** (#314 B4, `close_lower_locked`). One trade:
  - p2 ADANITRANS closed 2022-02-14 at its 5% band (low = close = 1915.25; previous close 2016.05).
  - Its trailing-swing-low exit waited for sma50_close on 2022-02-21 (P&L −628 → −1,631).
- **C3b Exit label sma50_close → sma20_close** (#314 B5; the label follows the configured SMA). p6 TIMKEN, FINEORG,
  TEJASNET. Same exits, new label.
- **C4 A 5m LIMIT that is never reached is skipped** (#314 B4, `limit_not_reached`). The LIMIT rests at the trigger
  bar's close and fills only if a later bar trades at or below it; before #314, every trigger filled at the close
  plus slippage. The skip is a counter only: no signals or refusals row.
  - In p3 and p4, four old triggers no longer fill:

    | Name, day | Trigger close | Lowest later low |
    | --- | --- | --- |
    | VEDL 2024-06-20 | 464.90 | 464.95 |
    | CRAFTSMAN 2023-12-14 | 5235.00 | 5235.05 |
    | VIJAYA 2024-08-09 | 810.55 | 811.00 |
    | BIOCON 2024-09-04 | 365.30 | 365.80 |

  - Only VEDL was a trade; the other three were max_positions refusals in the old run.
  - VEDL re-triggers on 2024-07-01 and holds into mid-July. That fills the book: TORNTPOWER (07-09 → 07-10) and
    UNITDSPR (07-16 → 07-22) move to later entries.
  - Net: 3 trades re-timed, P&L +3,769.
- **C5 Corporate-action corrections** (196 versions added since the old runs' data, plus the 20 now dated):
  - Direct price factors in p5: PEL ×0.976143 (PIRHEALTH 2019-12-30 rights, 5 legs) and GUJGASLTD ×0.8825
    (demerger correction ex 2026-07-02, 3 legs).
- **C6 Rotation score coupling** (p5). The riskadj score is a mean of z-scores across that night's eligible names, so
  a corrected action anywhere in the lookback moves every score, flipping near-ties and crossing min_change_pct
  on small trims.
  - Checked night by night: of 108 rebalance nights, every night whose scores changed has a changed action in its
    lookback (0 changed nights without one).
  - Result: 14 old-only and 17 new-only legs (first 2016-01-01 ASHOKLEY trim; CHAMBLFERT/HINDUNILVR 2017-08-31;
    the JUBLFOOD 2017-12 cascade), 1 trim moved a month (MUTHOOTFIN 2019-09 → 2019-08) and 567 resized legs.
  - The two rerun-1 shifts without a cause (2024-10-31, 2024-11-29) are gone.
- **C7 5m volume repair** (#319 `bars5m_volume`; the import had cut volume by a later split factor). In p6 the EP
  volume test passes earlier:
  - GAEL 2022-05-30: 75 bars, volume ×2.0. The trigger moved from 12:30 (refused max_chase at 164.575) to
    11:15 (taken at 162.45; new trade, −5,312).
  - BSE 2024-08-08: 75 bars, ×3.0. The trigger moved from 12:05 to 09:40, an entry ×0.9945
    (872.53 → 869.46).
- **C8 09:20 fill on daily-estimate gap-over entries** (#332). The entry is the open moved by the measured
  OPEN_TO_0920 buy median, ×1.0002, capped at the day's high.
  - p2: 21 entries; p3 and p4: 5 each; p1 and p6: none.
  - p2 KARURVYSYA: the cash change crosses the size minimum (2024-05-28 refused size_below_min → taken; the
    2024-06-03 entry is gone).
- **C9 Rotation fills at 09:20** (#332 with #335). Every rotation order fills and is sized at 09:20:
  - 680 fills at the 09:15 bar close (where 5m data exists, 2021 on).
  - 1,630 fills at the open moved by OPEN_TO_0920 (buy +0.02%, sell −0.03%), within the day's range.
  - p5, pre-#332 → main: CAGR 23.32 → 23.19, max DD 35.43 → 35.69, fees −1,247. 486 trades both sides, of which
    17 legs are old-only and 15 new-only, from ranking and trim crossings on the new prices.
- **C10 Results filing retimed** (#317). p6 RTNINDIA Q4 FY22: public_at moved from 2022-06-04 04:43 to
  2022-05-30 14:19 UTC, giving a new EP trade (signal 05-30, entry 05-31, −7,176).
- **Cosmetic**: refusal labels size_zero_cash ↔ size_below_min (23 rows in p2), relabelled by #314's sizing order.
  No trade changes.

## Per run

- **p1**: both trades are the same; entries are ×0.998 (C2). CAGR +0.02.
- **p2**: all 154 trades are paired.
  - Old → pre-#332: 13 same, 140 fees or resizing (C1), 1 exit (ADANITRANS, C3). CAGR −0.05.
  - Pre-#332 → main: 21 entries ×1.0002 plus a KARURVYSYA swap (C8). CAGR +0.08.
- **p3**: old → pre-#332, CAGR +0.66:
  - 132 entries ×0.998 (C2), 21 resizings and 4 fee-only trades (C1).
  - 3 trades re-timed (C4): VEDL, TORNTPOWER, UNITDSPR.
  - P&L: entry/exit +17,151, sizing +298, re-timed +3,769.
- **p3, pre-#332 → main**: 5 entries ×1.0002 (C8). CAGR −0.02.
- **p4** (old engine afdff73e, post-#311): as p3. Old → pre-#332: 132 entries ×0.998 (C2), 16 resized and 3 fee-only (C1), the same 3 C4 re-timings (VEDL, TORNTPOWER, UNITDSPR); CAGR +0.66. Pre-#332 → main: 5 entries ×1.0002 (C8); CAGR +0.001.
- **p5**: old → pre-#332, CAGR −0.035:
  - Fees +3,845 (C1).
  - Legs: 642 fee-only and 567 resized (C1, C6); 5 PEL legs and 3 GUJGASLTD legs (C5).
  - 31 legs swapped and 1 trim moved (C6).
- **p5, pre-#332 → main**: C9.
- **p6**: old → pre-#332, CAGR −0.32:
  - 9 entries ×0.998 (C2).
  - 3 relabels (C3b).
  - GAEL and BSE (C7).
  - RTNINDIA (C10).
  - Resizing (C1).
- **p6, pre-#332 → main**: identical.

## Notes

- **The engine field is wrong for the pre-#332 runs.** `identity.engine_commit` records the m3 checkout's HEAD at
  write time, not the code that ran. The pre-#332 runs ran the exported tree at 2121493 but record 8f4267d2 or
  d6d99b6d-dirty.
- **Skipped LIMITs leave no row.** A `limit_not_reached` skip leaves no signals or refusals row, so a run comparison
  shows a lost 5m entry only as a missing signal.
- **DTIL has undated rows too.** Its 10 owner dividends from 2026-10-25 had the same undated pattern. #334's D2 check
  now fails any undated applied value.
- **Run folders:**
  - Old runs: `HAT_DATA_ROOT/backtests/runs/` on m1.
  - Rerun 2: the same path on m3, with copies in `/data/workspace/g3-work/rerun2/`.
  - The failed d079b11 p5 run (01a18bfd) kept its ledger.json with the 102 findings.
