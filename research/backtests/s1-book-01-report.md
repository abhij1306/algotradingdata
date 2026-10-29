# S1 book rules — Phase 3 in-sample report (2026-10-27)

In-sample 2016-01-01..2021-12-31, NIFTY500_PIT, policy v3, daily entry bars, ambiguous pessimistic.
Hold-out (2022+) not run, not read.

- s1-book-01: run `01a17d8a-f6df-7099-af99-7147629ba1ec` (main 6cabfbd6, sweep `sweeps/s1-book-01.yaml`, log `s1-book-01.log`)
- baseline ride_pess: run `01a17d5e-5176-728c-8c2a-39bc88acfb16` (Phase 1)
- run folders: `/data/workspace/hat-data-isin/backtests/runs/<run_id>/` (run.json metrics/breakdowns/funnel, trades.csv)

## Summary

| metric | ride_pess | s1-book-01 |
|---|---|---|
| trades | 172 | 12 |
| win % | 31.4 | 33.3 |
| expectancy R | 0.588 | 0.497 |
| avg win / loss R | 3.34 / −0.67 | 2.74 / −0.63 |
| CAGR % (bench 15.66) | 15.76 | 0.99 |
| total return % | 140.6 | 6.1 |
| max DD % | 24.12 | 4.51 |
| MAR | 0.653 | 0.219 |
| Sharpe | 1.11 | 0.50 |
| invested % | 51.7 | 1.8 |
| avg open positions | 2.93 | 0.15 |
| longest DD sessions | 752 | 495 |
| CAGR ex top-5 trades % | 4.62 | −0.88 |
| top-5 trades P&L share % | 77.9 | 185.5 |
| max consecutive losses | 11 | 5 |
| DSR prob (trials) | 0.385 (85) | 0.030 (86) |
| PBO | 0.614 | 0.686 |

## By year (by entry year)

| year | ride_pess entered / exp R / return % | s1-book-01 entered / exp R / return % | benchmark % |
|---|---|---|---|
| 2016 | 21 / 0.295 / 5.36 | 0 / – / 0.00 | 5.12 |
| 2017 | 35 / 1.319 / 66.86 | 2 / 2.132 / 4.79 | 37.65 |
| 2018 | 16 / −0.154 / −11.37 | 1 / −0.551 / −0.95 | −2.14 |
| 2019 | 23 / −0.346 / −7.62 | 0 / – / 0.00 | 8.97 |
| 2020 | 29 / 1.001 / 14.07 | 1 / 2.614 / 2.70 | 17.89 |
| 2021 | 48 / 0.629 / 46.55 | 8 / −0.046 / −0.50 | 31.60 |

## By exit reason (final leg)

| exit | ride_pess n / win % / exp R | s1-book-01 n / win % / exp R |
|---|---|---|
| initial stop | 30 / 0 / −1.060 | 2 / 0 / −1.043 |
| close below SMA (50 ride, 20 book)* | 129 / 31.8 / 0.751 | 10 / 40 / 0.805 |
| trailing swing low | 12 / 100 / 2.622 | – (off) |
| demerger | 1 / 100 / 4.649 | – |

\*Labelled `sma50_close` in both runs: `backend/app/hat/backtest/standard.py:363` maps every
`close_below_sma` to that label whatever the SMA. In s1-book-01 it is the SMA20 exit (config
`exits[close_below_sma].sma=20`). 3 of the 12 trades took the 50% partial at +3R
(TATAGLOBAL, BHARTIARTL, BALAMINES). The breakeven move at +2.5R never decided an exit.

## By base number (s1-book-01; ride_pess predates the column)

| base | n | win % | exp R |
|---|---|---|---|
| 1 | 5 | 40 | 1.255 |
| 2 | 5 | 20 | −0.161 |
| 3 | 2 | 50 | 0.246 |

`stage2_start_unknown` is true for 2 trades (DMART 2018, DEEPAKNTR 2021).

## By Depth_1 bucket (s1-book-01)

| Depth_1 | n | win % | exp R |
|---|---|---|---|
| 10–15% | 12 | 33 | 0.497 |
| 15–20% | 0 | – | – |
| 20–35% | 0 | – | – |

All 12 entries have Depth_1 in 11.4–14.4%, although the allowed band is 10–35%
(`book.py:104`). Deeper first contractions never reached an entry. This is for the Phase 4
detector audit to explain. It is not a reason to change a parameter.

## Funnel (s1-book-01, stock-days passing each gate; `run.json` `funnel`)

Regime-off nights: 425.

| gate | passed | of previous |
|---|---|---|
| evaluated | 531,500 | |
| universe | 293,828 | 55% |
| trend template | 110,768 | 38% |
| RS rank ≥ 70 (eligible universe)† | 63,625 | 57% |
| VCP geometry | 1,299 | 2.0% |
| time compression | 1,009 | 78% |
| dry-up | 570 | 56% |
| relative correction | 295 | 52% |
| base count (< 4) | 288 | 98% |
| close vs pivot | 203 | 70% |
| setup / watchlist | 203 / 189 | |
| trigger (high > pivot) | 59 | |
| breakout volume ≥ 1.5× avg50‡ | 12 | 20% |
| stop ≤ 10% | 12 | 100% |
| max chase ≤ 2% | 12 | 100% |

The two big cuts are VCP geometry (98% of RS-passing stock-days fail it) and breakout volume:
47 of 59 triggers were below 1.5× the 50-day average, on full-day volume.

† RS rank is an approximation of the IBD RS rating, not a rule from the book.
‡ Breakout volume uses full-day volume (owner decision 7). That is look-ahead for an intraday
entry: it is known only at the close.

## Not implemented / not available
- Ladder size cut after losses: not implemented (flat ladder, decision 3).
- Earnings / fundamentals: no table; `earnings_growth` stays disabled.
- Health is fixed at 1 in backtests (`loop.py:458`).

## Decision rule
**Fewer than 60 trades: too few to judge, gates not loosened.** s1-book-01 made 12 trades in
6 years (win 33.3%, expectancy 0.497R). These numbers cannot place it in either the
"≥ 40% and > 0.3R" branch or the "~30%" branch: each trade moves win % by 8.3 points. DSR 0.03
and CAGR ex top-5 of −0.88% confirm there is no measurable edge at this sample size.
