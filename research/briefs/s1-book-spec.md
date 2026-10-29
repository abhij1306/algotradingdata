# S1 book-rules spec (owner, 2026-10-27)

Source of the rules: the owner's task (Minervini 2013, page refs provenance only). Do not infer rules beyond this file.
Phase 0 audit of the current code: /data/workspace/audits/2026-10-27-s1-book-phase0.md (read it first).
No parameter tuning. In-sample 2016-01-01..2021-12-31; never run or read 2022+.
Every value used on a signal date must be computable from data up to that date.
Each new rule is a config-driven criterion in the playbook schema (setup.criteria[...], trigger[...], exits[...]), mode hard unless stated.
One passing and one failing synthetic series per new or changed criterion (small pure functions; no backtests in tests).

## Owner decisions (2026-10-27)
1. trailing_swing_low exit off in s1-book-01; SMA20 is the only trailing exit.
2. Regime unchanged: close_above_sma_and_rising sma 50, rising_days 0.
3. No exposure ladder size cut (flat ladder); report it as not implemented. Health bands are not simulated in backtests.
4. RS rank is ranked within the run's eligible universe on that date (the bot's universe stage passing: NIFTY 500 PIT + turnover + price filters), not all NSE equities.
5. Final contraction = swing high Hi to swing low Li (inclusive) for its >=3-session length and the dry-up window.
6. Base count resets at any close below SMA200: count bases from the later of stage-2 start and that close. If no stage-2 start lies in the history, count from the first date with full trend-template history and log `stage2_start_unknown`.
7. Breakout volume: daily full-day volume everywhere in-sample (incl. 5m days), recorded as a look-ahead known gap.
8. Keep close_vs_pivot (close <= pivot on the signal date) and policy min_position_pct 0.02. Relative correction uses NIFTY 500 closes.

## A. RS rank
score = 0.4 ret63 + 0.2 ret126 + 0.2 ret189 + 0.2 ret252 (existing rs_weighted). RS rank = percentile of score within the eligible universe that date, scaled to 1..99. Hard gate >= 70. Label in reports: "approximation of the IBD RS rating, not from the book".

## B. Trend template: the 8 checks (existing criteria) + RS from A.

## C. Base and contraction geometry (signal date, data up to that date)
- H0 = highest high in the last 325 sessions, after which price fell >= 10% from it; none -> no base.
- Swings: zigzag on daily high/low, reversal threshold = max(3%, 1.5 x ATR14 / close); only swings confirmed by bars up to the signal date.
- Contraction i = swing high Hi to next confirmed swing low Li; Depth_i = (Hi - Li)/Hi. Contraction 1 starts at H0. No swing high inside the base may exceed H0.
- Count 2..6 (reject outside).
- Depth_1 in [10%, 35%].
- Depth_i <= 0.75 x Depth_(i-1) for every i >= 2.
- Final depth <= 10%, final contraction >= 3 sessions.
- Pivot = highest high of the final contraction. Stop basis = final contraction low.
- Base length (H0 date -> signal date): 15..325 sessions.
- Log shakeout (any Li below an earlier Li); do not reject.
- Log footprint "<weeks>W <Depth_1>/<Depth_final> <count>T", e.g. "8W 22/2 3T".
## D. Time compression: reject if sessions(deepest low -> signal) < 0.5 x sessions(H0 -> deepest low), or < 10. Log both.
## E. Dry-up over the final contraction: mean volume < 0.7 x avg50 as of the final contraction's first session, AND >= 1 session < 0.5 x that avg50.
## F. Relative correction: idx_depth = NIFTY 500 max peak-to-trough decline (closes) between H0 date and signal date. Reject if Depth_1 > 2.5 x idx_depth AND Depth_1 > 15%. Log ratio.
## G. Base count: stage-2 start = first day the full template (B) passes after >= 60 consecutive failing sessions. Base number = 1 + earlier bases (as C) since stage-2 start whose pivot was broken by a close above it (traded or not). Reset per decision 6. Reject base >= 4. Log base number.
## H. Earnings: disabled (no point-in-time fundamentals).

## Trigger
Break of the C pivot. volume_pace hard >= 1.5 x avg50 (decision 7). max_chase 2%: fill > 2% above pivot (incl. gap-up opens) is skipped.

## Exits
Initial stop 0.5% below final contraction low, skip if > 10% from entry. Breakeven at +2.5R. Sell 50% at +3R. Remainder exits on close below SMA20, ignored for the first 10 sessions after entry (stop only). Disabled: close_below_sma 50, time_stop, partial_at_r 0.33, step_trail, trailing_swing_low.

## Sizing
Risk 1%, max position 25% of equity, max 6 open positions, same-day surplus ranked by RS (highest first), cooldown 0, flat ladder.
