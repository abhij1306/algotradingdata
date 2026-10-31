# E2 momentum rotation: years that trail NIFTY 500 TRI (diagnosis only)

Scope (owner, 2026-10-31): the test is the per-year gap to NIFTY 500 TRI. A gap worse than −10 pts
in a year is flagged, and only flagged years are explained. No backtest was run and nothing was
tuned. Runs: in-sample E2 `01a190de` (2016-2021) and hold-out E2 `01a19119` (2021-2025). Files
were copied from m3; scripts and the data pulls are in `plans/mom-fail-work/`.

## Answer

- **Two years are flagged: 2025 (−27.0 pts) and 2016 (−12.8 pts).** 2018 comes close (−9.0).
  Every other year is ahead of TRI.
- **2025: the rotation sold the year-start book at the low.** The 20 names held on 2024-12-31
  account for the whole loss: −₹7.55L, −19.2% of start equity. Names bought during 2025 made
  +₹0.48L. Held unchanged all year, that start book would have returned about −3.0%. Instead the
  rotation had sold 11 of the 20 by Feb 1 and 19 by Apr 1, and then missed the rebound from April.
  The −₹8.5L realised on `rotation_out` exits is the loss.
- **The market explains about a quarter of the 2025 gap.** Equal-weight PIT NIFTY 500 trailed TRI
  by 7.0 pts, so it was a small/mid-cap year. It was not a yearly momentum-factor crash: the top
  quintile on 12-1m return made −1.7% and the bottom quintile +0.6%. The book was the
  momentum-crowded slice: prior-12m median +123% (universe +21%), beta 1.12 (universe 1.04).
  It was not sector-concentrated, and gap-downs were not the driver.
- **2016 is a different mechanism.** The run started fully invested in a high-beta book (beta
  1.37, prior-12m median +78%) at the start of the Jan-Feb 2016 sell-off. Then the fixed ₹10 cr
  20-day turnover floor forced out 17 holdings that had fallen below it, realising −₹81k (−8.1% of
  capital).
- **This is a known property, not a bug.** Cross-sectional momentum loses sharply when a
  sell-off reverses quickly: a monthly rank rotation sells the fallen leaders near the trough and
  misses the snap-back. The in-sample years had the same exposure (2018 start book −26.9%); there
  the decline kept going, so selling helped (strategy −11.1%). Marked P&L reconciles with the
  equity curve after fees and slippage, and I found no data or engine bug (see Notes).

## Per year: E2 return minus NIFTY 500 TRI (equity.csv `benchmark_tri`)

| Year | Run | E2 % | TRI % | Gap (pts) | Invested % | Flag |
| --- | --- | --- | --- | --- | --- | --- |
| 2016 | IS | −8.08 | +4.68 | **−12.75** | 99.6 | **yes** |
| 2017 | IS | +80.78 | +37.65 | +43.12 | 99.1 | |
| 2018 | IS | −11.10 | −2.14 | −8.96 | 99.4 | near |
| 2019 | IS | +14.99 | +8.97 | +6.01 | 99.5 | |
| 2020 | IS | +37.23 | +17.89 | +19.34 | 99.3 | |
| 2021 | IS / OOS | +88.57 / +83.87 | +31.60 / +30.95 | +56.97 / +52.92 | 99.1 | |
| 2022 | OOS | +2.16 | +4.25 | −2.09 | 99.5 | |
| 2023 | OOS | +62.17 | +26.91 | +35.26 | 99.3 | |
| 2024 | OOS | +29.01 | +16.24 | +12.76 | 99.1 | |
| 2025 | OOS | −19.25 | +7.76 | **−27.01** | 98.9 | **yes** |

The first year of each run is measured from its first close: 2016 from 2016-01-01 and the OOS
2021 row from 2021-01-01. The IS 2021 row continues the in-sample run, so its TRI is +31.60.

## Market context per year (PIT NIFTY 500 members, total-return closes)

EW is the equal-weight return of the members at the year start. Q5 and Q1 are the top and bottom
quintiles by 12-1m return at the prior year-end, with returns over the next calendar year.

| Year | EW % | TRI % | EW − TRI | Q5 % | Q1 % | Q5 − Q1 |
| --- | --- | --- | --- | --- | --- | --- |
| 2016 | 4.1 | 5.1 | −1.1 | 4.5 | −4.6 | +9.1 |
| 2018 | −19.5 | −2.1 | **−17.4** | −25.9 | −25.6 | −0.3 |
| 2019 | −6.4 | 9.0 | −15.3 | 7.6 | −27.8 | +35.4 |
| 2022 | 5.2 | 4.2 | +0.9 | 1.0 | −1.6 | +2.6 |
| 2024 | 22.2 | 16.2 | +5.9 | 38.9 | 7.3 | +31.6 |
| 2025 | 0.7 | 7.8 | **−7.0** | −1.7 | 0.6 | **−2.3** |

The other years' Q5 − Q1 spreads are 2017 +10.7, 2020 +21.1, 2021 +25.2 and 2023 +18.0.

## Flagged and near years: book profile and loss source

The book profile is at the prior year-end close. Beta is 252-session daily beta to NIFTY 500.
Size is the median rank by 60-session average traded value within PIT NIFTY 500 (0 = largest).
Traded value is the size proxy here; market cap is not in the data.

| | 2025 (OOS) | 2016 (IS) | 2018 (IS) |
| --- | --- | --- | --- |
| Book beta, median (universe) | 1.12 (1.04) | 1.37 (1.05) | 1.32 (1.07) |
| Size-rank percentile, median | 0.29 | 0.20 | 0.24 |
| Prior-12m return, median (universe) | +123% (+21%) | +78% (+6%) | +216% (+48%) |
| Most names in one industry | Capital Goods 4 | Healthcare 6 | Financial Services 10 legs |
| Start book, buy-and-hold for the year | −3.0% | n/a (started 1 Jan) | −26.9% |
| Year-start names still held Feb 1 / Apr 1 / Jul 1 | 9 / 1 / 2 of 20 | 14 / 8 / 1 | 14 / 11 / 3 |
| P&L from year-start names / from names bought in year | −₹7.55L / +₹0.48L | — / −₹0.54L | −₹1.31L / −₹0.84L |
| Realised by exit reason | out −8.55L, trim +1.58L, not-eligible −0.02L | out −1.27L, trim +0.59L, **not-eligible −0.81L (17 legs)** | out +1.05L, trim +1.39L, not-eligible −0.39L |
| Opening gaps < −5% in year-start names | 32 (worst −17.6%) | — | 40 (worst −14.7%) |
| Fees on legs exited in the year | ₹37.5k (~1.0% of equity) | ₹8.2k | ₹11.5k |

- **2025 by industry** (marked P&L, % of start equity): Consumer Durables −4.5, Capital Goods
  −3.7, IT −2.7, Consumer Services −2.6, Healthcare −2.6, Metals −2.1. The losses were broad:
  no sector stands out. The worst names lost about 1.5-2.4% of equity each, spread over about 10
  names.
- **Size alone does not explain 2025.** The book sat in the top 30% by liquidity. EW trailed TRI by
  7 pts, but the start book lost only about 11 pts against TRI if simply held. The rest of the gap
  came from selling it after the fall, as above.
- **2016:** about 2/3 of the gap is the 17 turnover-floor exits. In Jan-Feb 2016, names such as
  CHENNPETRO, NIITLTD, NATCOPHARM and HIMATSEIDE fell below ₹10 cr of 20-day value. All were still
  NIFTY 500 members. The rest is high beta in a falling Jan-Feb and Nov-Dec. 2016 was not a
  momentum-factor loss (Q5 − Q1 +9.1).
- **2018** (near flag): a small-cap crash (EW −17.4 vs TRI). The book was −26.9% on buy-and-hold,
  and the rotation cut it to −11.1%. This is the mirror image of 2025, with the same rule.

## Notes and checks (no bug found)

- **Reconciliation.** Marked P&L from trades.csv against the equity change: 2025 −₹7.07L against
  −₹7.56L, a gap within fees (₹37k) plus slippage. 2018: −₹2.15L against −₹1.84L. 2016: −₹0.54L
  against −₹0.81L. 2016 is looser: 180 entry legs at 20 bps slippage each way, plus my
  open-to-close marking approximation.
- **`riskadj` has no skip-month.** It uses the last close, so `skip_sessions=21` applies only to
  `r12_1`. This is documented in `strategy/config.py`, so it is not a bug. It does mean the score
  includes the most recent month, which adds short-term-reversal exposure.
- **The turnover floor is a fixed ₹10 cr in nominal rupees.** It forced 17 exits in 2016 and 15 in
  2017, but only 1-4 a year from 2023 on, as liquidity grew. It is design, not a bug, but its
  effect on the in-sample years differs from its effect on the hold-out years.
- **Industry labels.** The 'unknown' industry legs (2016: GEOMETRIC, MTEDUCARE, HIMATSEIDE,
  DALMIABHA) are delisted or merged names. That is the known survivorship caveat in
  `docs/decisions.md`.
