# S1 book rules — Phase 5 hold-out report (2026-10-27)

s1-book-01, unchanged (sweep `sweeps/s1-book-01.yaml`, main 6cabfbd6), from 2022-01-01 to
2026-10-25. That is the last day NIFTY500_PIT membership covers: `--to 2026-10-26` was refused
`backtest_ends_after_membership@2026-10-25`.
Run `01a17dc9-e197-74c5-92c7-666997787b0b`, log `s1-book-01-holdout.log`. Daily entry bars, as in-sample.
(run.json `data.split` says `in_sample`: that is the CLI's default label; this window is the hold-out.)
In-sample reference: run `01a17d8a-f6df-7099-af99-7147629ba1ec` (`s1-book-01-report.md`).

## Summary

| metric | in-sample 2016–2021 | hold-out 2022–2026-10 |
|---|---|---|
| trades | 12 | 15 |
| win % | 33.3 | 46.7 |
| expectancy R | 0.497 | 0.931 |
| avg win / loss R | 2.74 / −0.63 | 2.78 / −0.69 |
| CAGR % (benchmark) | 0.99 (15.66) | 2.93 (8.79) |
| total return % | 6.1 | 14.9 |
| max DD % | 4.51 | 5.59 |
| MAR | 0.219 | 0.525 |
| Sharpe | 0.50 | 0.88 |
| invested % | 1.8 | 3.1 |
| avg open positions | 0.15 | 0.25 |
| longest DD sessions | 495 | 626 |
| CAGR ex top-5 trades % | −0.88 | −0.64 |
| top-5 trades P&L share % | 185.5 | 120.3 |
| max consecutive losses | 5 | 4 |
| DSR prob (trials) | 0.030 (86) | 0.732 (1; effective 5) |

## By year (by entry year)

| year | entered | exp R | return % | benchmark % |
|---|---|---|---|---|
| 2022 | 2 | 1.860 | 3.77 | 4.25 |
| 2023 | 5 | 0.123 | 0.55 | 26.91 |
| 2024 | 5 | 0.797 | 3.96 | 16.24 |
| 2025 | 2 | 2.291 | 4.80 | 7.76 |
| 2026 (to 10-25) | 1 | 1.064 | 1.09 | −9.50 |

## By exit reason (final leg)

| exit | n | win % | exp R |
|---|---|---|---|
| initial stop | 3 | 0 | −1.056 |
| close below SMA20 (labelled `sma50_close`, `standard.py:363`) | 12 | 58.3 | 1.428 |

5 of 15 took the 50% partial at +3R (SCHAEFFLER, DATAPATTNS, TATAINVEST, GICRE, MANAPPURAM).

## By base number

| base | n | win % | exp R |
|---|---|---|---|
| 1 | 12 | 42 | 0.633 |
| 2 | 3 | 67 | 2.122 |

`stage2_start_unknown`: 1 (DATAPATTNS, listed 2021).

## By Depth_1 bucket

| Depth_1 | n | win % | exp R |
|---|---|---|---|
| 10–15% | 15 | 47 | 0.931 |
| 15–35% | 0 | – | – |

Same clustering as in-sample (11.4–15.0%): rule F, per the Phase 4 audit.

## Funnel (stock-days)

Regime-off nights: 435.

| gate | in-sample | hold-out |
|---|---|---|
| evaluated | 531,500 | 378,885 |
| universe | 293,828 | 337,300 |
| trend template | 110,768 | 105,857 |
| RS ≥ 70† | 63,625 | 66,694 |
| VCP geometry | 1,299 | 1,577 |
| time compression | 1,009 | 1,289 |
| dry-up | 570 | 873 |
| relative correction | 295 | 431 |
| base count | 288 | 421 |
| close vs pivot / setup | 203 | 288 |
| watchlist | 189 | 280 |
| trigger | 59 | 77 |
| breakout volume ≥ 1.5×‡ | 12 | 15 |
| stop ≤ 10% / max chase ≤ 2% | 12 / 12 | 15 / 15 |

† RS rank is an approximation of the IBD RS rating, not a rule from the book.
‡ Full-day volume: look-ahead for an intraday entry (owner decision 7).
Not implemented: ladder size cut. Not available: earnings.

## Decision rule
**Fewer than 60 trades: too few to judge.** Hold-out: 15 trades, win 46.7%, expectancy
0.931R. Read alone, these would fall in the "≥ 40% and > 0.3R" branch. With 15 trades, though,
one trade moves win % by 6.7 points, and CAGR ex top-5 is −0.64%. In-sample plus hold-out is 27
trades in 10 years, still under 60. The capital deployed (3.1% invested, 0.25 positions on
average) gives 2.93% CAGR against a benchmark of 8.79%.
