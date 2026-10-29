# HAT open items (2026-10-25, main 526925e7)

Run report: /data/workspace/RUN-REPORT.md. Per-PR follow-ups: /data/workspace/followups/*.md. Owner page: https://claude.ai/artifact/Nm5CEj6oGxRpGKMEKtKoWJ

**Owner DBA steps:** step 7, REVOKE TRUNCATE on hat_event, takes effect only once the backend runs as a non-superuser (`docs/runbook.md`). Step 8 done.

## (A) Owner decisions pending
- Data reviews: done 2026-10-25 (owner delegated to web research). Applied: 43 CA3 dividends, DVL/DTIL wrong-company fix (9 moved), 3 duplicate-date deletes; CA7 all 17 confirmed. CA8: 9 earlier exchange dates applied via #261 `demerger_notice announced --replace` (all 9 now exit before the demerger); 8 keep press dates; POLARIS 2014 worth a re-check if a BSE 2014-09-26 filing turns up.
- From #259 follow-ups: should S1/S2's score-mode level criteria (`vcp`, `consolidation`) become hard? (A failing one now keeps the setup off the watchlist.)

## (A2) Backtesting phase
- Plan: /data/workspace/ORCHESTRATOR-HANDOFF.md "Next session plan" (2026-10-26). hat_live seeded 2026-10-25 (policy, strategies, Fyers account, 5 research bots, nifty500 universe as of 2026-10-23, Sunday 2026-10-25 calendar row). Scratch DB hat_bt holds the backdated universe and the runs.

## (B) Parked / dated
- Fyers intraday 5m history / DB9 (PR 70/77/37), needed for the EP pre-open playbook. Daily-strategy backtests are un-parked (see handoff).
- hat_live stores 2026-11-08 as non-trading until `calendar.refresh` applies the Muhurat session at deploy.
- 2027 NSE holiday list (~December).
- Zerodha first login and live fixture check: followups/zerodha-framework.md.
- O2-day checks (first live Fyers session): GTT fields/tags/error codes, holdings vs positions on T and at settlement, sale proceeds in Available Balance, stop cancel in the book, SL-M modify, MPP fixture, onboard-account.
- NSE feeds still `[A]`: RSS layout, tick day high/low (`HAT_EXCHANGE_DAY_RANGE`).
- Shadow slippage placeholder (20 bps): revisit after 20 shadow sessions.

## (C) Watch on first real data
hat_live has no bots, positions or runs yet, so the execution, rescale/split-gap/demerger guards, sizing/drawdown and alert paths are verified by tests and dry runs only.

## (D) Data state
- Lineage 591 linked, 1 review (KAUSHALYA, kept apart by ruling).
- Left alone on purpose: 712 shared-symbol MCP rows (audits/data-review-2026-10-24.md §1); MPS public-only bonuses (INFINITE, TTML, GAMMNINFRA), live rescale through them stays manage-only.

## Backtest follow-ups (from #263, 2026-10-25)
- Reports live only on disk (`HAT_DATA_ROOT/backtests/run_id=<id>/report.json`); add them to `hat_backup.py` scope if they must survive a data-root move. Runs before #263 have no report (no backfill; re-run).
- No tool turns a winning variant's `overrides` into a new draft strategy version (promotion runs refuse overrides).
- `/api/hat/backtests/{id}/trades` is not paginated; add offset/limit if runs reach thousands of trades.
- Wide sweeps raise each family's trial count, so DSR/PBO tighten and later promotion gets harder (intended).
- (#264) Backtest jobs live in memory (lost on server restart; children still record runs); job folders under `backtests/jobs/` are never pruned; a plain run's progress shows 0/1 until done (no day-loop progress hook).
- (#264) The UI form does not offer `only_if_profit`, a breakeven's `after: partial` trigger or stop-rule swaps; use the CLI `--set`.


- Backtest window starts 2016-01-01 or later (owner 2026-10-25): the point-in-time NIFTY 500 history covers only 2016-01-01 on, because pre-2016 notices could not be fully matched. Pre-2016 bars may still warm up indicators (SMA200, 52-week, RS); no trade before 2016-01-01. Lift this only after the 2011-2015 membership is resolved (see /data/workspace/nifty500-history/coverage.md).
- Weekly timeframe for S1 (owner 2026-10-25: same rules on weekly bars, parameters converted to weeks). No timeframe support exists today; needs resampling, weekly-close exits and live parity, about 1-2 weeks. After the S1 config PR.

## Data-cleanup follow-ups (hat/data-cleanup, 2026-10-25)
- D4: refresh `reference/delisted_on` (stale delisting dates); not done in the data-cleanup PR.
- D7: done in #269 (2026-10-25): dated `cnc-delivery-1/<effective_from>.yaml` schedule from 2016. Approximations: SEBI fee ₹10/cr throughout, DP ₹14.75 today's tariff throughout, stamp duty convention pre-2020-07 per decisions.md, NSE IPF contribution not modelled.
- Nightly TRI: done by #287 (2026-10-26); full history verified against niftyindices raw files (3,636 closes, 0 mismatches).
- ADANIENT 2015-06-03 ex-day bar (open/high 573.30 single print): accepted as a known artefact (orchestrator 2026-10-25, runbook), no bar correction.
- India VIX has no source for 5 bar days (2014-12-15, 2015-03-12, 2015-07-08, 2021-02-12, 2021-03-30): left missing, never carried.

## S1 re-audit minors (2026-10-25, /data/workspace/audits/2026-10-25-s1-reaudit-fable.md)
- m1: `hat_index_member` lacks demerger placeholder intervals (JIOFIN 2023-07-20..09-07, ITCHOTELS 2025-01-06..02-10). No S1 impact.
- m2: done in #269 (DP charge once per instrument per sell day).
- m3: backtest `DailyInputs.avg50_volume` is None; must be set before `volume_pace` is ever evaluated in the loop.
- M1 gap: 5m `confirm: close` not modelled in daily-bar backtest; record on every intraday-entry run.
- 5-minute history: in `bars_5m` (#271, 2021-10-26..2026-10-23). Current members: 497 symbols, ~5% of days rejected vs raw daily bars. Former members (2026-10-26): 212 imported (14.4M bars, 195,572 days; 17,816 days rejected basis_mismatch, 110 no_daily_bar, ~8%); 21 of 272 not served by the broker; 17 corporate actions not carried by the history (adjusted per action). Gap: 213 symbols lack 15:15-15:25 bars from 2026-08-03 (Fyers days cover to 2026-10-21). Raw downloads in /data/workspace/kotak/data/raw_5m_former (445 MB) are now redundant: in the non-canonical cleanup list.

## 2026-10-27 (from #292/#293)
- bars_5m: 252 days with last 5m close >5% off daily close (214 in 2026) - check the 2026 import/basis.
- Refetch the explained gap days (`bars_basis explained-rejects --write`) - needs owner's data go.
- UI/API: entry_bars not in the job form; frontend ignores by_playbook and entries_5m/entries_daily.
