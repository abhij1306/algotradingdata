# S1 book rules, Phase 1 report (2026-10-27)

Sweep `s1-book-p1` (`backtests/sweeps/s1-book-p1.yaml`, log `backtests/s1-book-p1.log`), main 20fdcc73 (#294 merged), in-sample 2016-01-01..2021-12-31, entry bars daily (as ride ran).
- `ride` original: 01a17ca4-3897-75bd-8afd-24a3cb53b489 (engine fb83fe45, ambiguous optimistic)
- `ride_rerun` (control, unchanged on current main): 01a17d54-5cb3-76ba-bb8f-c54e07d9fa2d
- `ride_pess` (ambiguous pessimistic): 01a17d5e-5176-728c-8c2a-39bc88acfb16

## Result
All three runs have the same trade list (`binding.trade_list_hash` fb2e4450b2a7… in each run.json). Every trading metric is identical: 172 trades, 533 signals, win 31.40%, avg win 3.342R, avg loss -0.672R, expectancy 0.588R, CAGR 15.76%, max DD 24.12%, MAR 0.653, Sharpe 1.111, invested 51.66%, avg open 2.93, longest DD 752 sessions, CAGR ex top-5 4.62%, top-5 share 77.9%, benchmark CAGR 15.66%.
Only the trial-count statistics moved: DSR 0.3951 -> 0.3853 (n_trials 80 -> 85), PBO 0.600 -> 0.614.
Why: `ambiguous` only acts on a stop raised intraday; ride raises none (step trail and breakeven off), `ambiguous_days` = 0 in ride_pess's evidence.json. Stop-before-target in one bar was already the fill path (Phase 0 audit section 4).

## by_year after the fix (ride_pess run.json breakdowns.by_year)
| Year | Return % | Bench % | Entered | Exp R (entry yr) | Exited | Exp R (exit yr) | Realized P&L (exit yr) |
|---|---|---|---|---|---|---|---|
| 2016 | 5.36 | 5.12 | 21 | 0.295 | 21 | 0.295 | 53,627 |
| 2017 | 66.86 | 37.65 | 35 | 1.319 | 31 | 0.002 | 18,726 |
| 2018 | -11.37 | -2.14 | 16 | -0.154 | 19 | 2.306 | 487,531 |
| 2019 | -7.62 | 8.97 | 23 | -0.346 | 21 | -0.386 | -127,433 |
| 2020 | 14.07 | 17.89 | 29 | 1.001 | 27 | -0.099 | -27,825 |
| 2021 | 46.55 | 31.60 | 48 | 0.629 | 53 | 1.168 | 1,001,748 |
The 2017/2018 mismatch is VAKRANGEE (entered 2017-01-12, exited 2018-01-31, +41.5R): marked in 2017's return, realized in 2018.
