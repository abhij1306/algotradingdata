# Value component: data feasibility and first cheap read (2016–2021)

Scope: research only. No engine backtest was run. hat_live was only read, and nothing was tuned.
2022–2025 (the spent hold-out) was not evaluated. Scripts, exports and outputs are in
`plans/value-work/`.

## Verdict

- **No value premium shows up in 2016–2021 with the data we have, and that data cannot test it
  cleanly yet.** In the covered universe, every value top quintile returns about what the covered
  equal-weight universe returns (CAGR within ±2 pts of 19.7%). The top quintiles also have the
  worst drawdowns of any book: −58% to −68%, against −48% for covered equal weight and −38% for TRI.
  Value did well in 2016–2017 and 2021, and badly in 2018–2020.
- **The study has a survivorship hole.** The fundamentals store covers only companies in NIFTY 500
  on or after 2020-03-31. In 2016, 33% of members have no fundamentals: 124 of 168 missing names
  left the index before 2020, and the other 44 are mainly standalone-only companies. The missing
  names returned **−1.6% CAGR** against 18.3% for the covered names. They sit mostly in the
  lowest-momentum and smallest quintiles, which is where cheap stocks also sit. In 2016-01 they
  make up 51% of momentum Q1 against 27% of Q5, and 53% of the smallest traded-value quintile
  against 11% of the largest (`survbias.py`). So value results on today's data are probably
  flattered.
- **Restatement is not the problem.** For FY2020–21, screener's restated figures leave value
  ranks almost unchanged: Spearman 0.97–0.999, and 96–98% of names land in the same quintile.
  Screener history with a deadline lag is usable for research, with the caveats in section 2.
- **Momentum and value are negatively rank-correlated** (mean −0.21, range −0.43 to +0.10).
  Their excess returns over equal weight are also negatively correlated (−0.21). Even so, a
  50/50 value + momentum book did **not** cut drawdown (−51% to −54% against −46% for momentum
  alone), because value's own drawdown is larger. The lowest drawdowns came from *expensive
  quality* (VAL Q1 −33.5%, QUALITY −40%), not from cheapness.
- **Recommendation:** close the data gaps first (spec in section 4). Carry forward one
  definition: a **quality-screened value composite** (EBIT/EV, earnings yield, CFO/price;
  ROCE ≥ 15%, D/E ≤ 1, CFO > 0). Treat it as a *tilt or filter inside the momentum book*, not
  as a standalone sleeve. Re-test only on the de-biased universe.

## 1. Data

### Coverage, share of PIT NIFTY 500 members (fiscal year ending in Y; members at Dec 31 Y, 2015 at 2016-01-01)

| Item (% of members) | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|---|
| screener: equity, net profit, EPS, sales, debt, CFO, shares | 66 | 70 | 71 | 76 | 84 | 86 | 87 |
| screener: operating profit (not banks) | 59 | 63 | 63 | 68 | 75 | 77 | 78 |
| NSE PIT: net profit, sales | 0 | 0 | 0 | 0 | 0 | 93 | 91 |
| NSE PIT: CFO | 0 | 0 | 0 | 0 | 0 | 0* | 91 |
| NSE PIT: shares (paid-up / face value) | 0 | 0 | 0 | 0 | 0 | 97 | 94 |
| NSE PIT: equity, debt (non-financials) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

\*NSE CFO starts with the Sep 2020 half-year. **NSE XBRL has no balance sheet before the Sep 2022
half-year**, so before then book value and debt come from screener alone.

- Screener has one annual page row per company for each year from 2015. Before 2015 there are
  almost none, because the page shows about 12 years. Quarterly rows exist only for the last 13
  quarters.
- **Why members are missing:**
  - 2015: 168 missing, of which 124 left NIFTY 500 before 2020-04 (outside the fetch scope).
  - 2017: 147 missing, of which 77 are leavers.
  - 2021: 64 missing, all inside scope but with no screener page. These are standalone-only
    companies such as ABBOTINDIA, COLPAL, PAGEIND, PFIZER and PGHH, plus recent listings. Most
    of them (55) do have NSE figures.
- **Shares and market cap are available point in time.** On screener, shares = share capital ÷
  face value (current face value, with each later split undone). On NSE, shares = paid-up
  capital ÷ face value, in every results filing. The screener-derived count matches NSE's for
  98.1% of FY2021–22 company-years within 10% (90.6% within 2%). Screener's EPS is restated for
  later splits and bonuses (26.6% differ by >20%, at ratios of 0.5, 0.2 and 0.1), so **EPS must
  not be used for share counts**.
- **Why NSE PIT starts in 2020: partly a source limit, partly a fetch choice.** The A0 probe
  found no XBRL before 2017, partial XBRL in 2018–2019, and complete XBRL from 2020. The cached
  NSE listings (already on disk, `listing_depth.py`) for the in-scope symbols show, per year:

  | Period-end year | Symbols | XBRL | HTML results page only | Neither |
  |---|---|---|---|---|
  | 2012 | 463 | 0 | 3,885 | 0 |
  | 2014 | 477 | 0 | 4,165 | 0 |
  | 2016 | 537 | 0 | 5,900 | 400 |
  | 2017 | 549 | 215 | 4,962 | 99 |
  | 2018 | 571 | 4,488 | 0 | 938 |
  | 2019 | 593 | 5,884 | 0 | 774 |

  - The **HTML results pages (2005–2017)** are first-published and carry the quarterly P&L
    (revenue, net profit, EPS), **paid-up capital, face value** and, on annual pages, **reserves
    excluding revaluation**. That gives a PIT book value once a year. They have no debt and no CFO.
  - The XBRL for 2018–2019 (about 85% of filings) was simply not fetched.
- **BSE:** XBRL financial results were introduced in 2015 and became mandatory for all listed
  companies (insurers excepted) by circular DCS/COMP/28/2016-17 of 2017-03-30. So BSE fills
  2017–2019 holes, but not 2012–2016. Neither exchange has results XBRL before 2015–17. The full
  annual statements with CFO for earlier years sit at MCA (paid, per company), so they are not
  practical.
- **Size of a backfill** (NSE, in-scope symbols plus the roughly 125–170 pre-2020 leavers):
  - HTML pages 2012–2017: about 30k pages × 11 KB, roughly 0.33 GB raw or 0.06 GB gzipped.
  - XBRL 2018–2019: about 10.4k files × 50 KB median, roughly 0.5 GB raw or 0.13 GB gzipped.
  - With the leavers: **about 0.25 GB on disk**, roughly 45–50k requests, 12–15 h at about one
    request per second.
  - Screener pages for the leavers: about 170 pages, roughly 10 MB.

## 2. Restatement bias (screener restated vs NSE as first published, same basis)

FY2020–22, 1,499 matched company-years (`restate.py`):

| Item | n | >1% diff | >5% | >20% | sign flip |
|---|---|---|---|---|---|
| revenue | 1,498 | 9.8% | 6.2% | 2.8% | 0.1% |
| net profit (period's) | 1,494 | 9.8% | 4.4% | 2.5% | 0.7% |
| CFO | 1,022 | 18.1% | 11.5% | 6.0% | 1.1% |
| PBT | 1,499 | 29.8% | 17.3% | 8.1% | 1.5% |
| finance cost | 1,490 | 44.8% | 26.3% | 12.9% | 1.7% |
| share capital vs paid-up | 1,493 | 22.5% | 1.9% | 0.7% | 0 |
| EPS | 1,494 | 45.1% | 35.6% | 26.6% | 0.5% |

- Screener's net profit is the period's profit including minorities, not the owners' share
  (22% differ by >5% from owners' profit).
- The PBT and finance-cost differences are definitional (exceptional items, interest
  classification): the median ratio is 1.000.
- **Rank effect** (`restate_rank.py`): same market cap, screener figure vs NSE first-published
  figure, non-financials, values at 2020-07-01 and 2021-07-01.

  | Yield | Spearman | Same quintile | Top-quintile overlap |
  |---|---|---|---|
  | earnings yield | 0.99–0.999 | 98% | 98.5–100% |
  | sales yield | 0.97–0.99 | 96–98% | 97–98.5% |
  | CFO yield | 0.98 | 97% | 98.5% |

- **Older years** (`html_vs_screener.py`, 28 large-cap FY2016–17 annual pages from the probe
  cache): net profit differs by >5% in 5 of 28 cases (LT −17% and −8%, JKLAKSHMI −78%, RELIANCE
  +9%, PERSISTENT −7%). These are Ind AS transition restatements of FY2016. Revenue differs by
  >5% in 5 of 28, from excise/GST gross vs net. So the restatement rate rises to about 15–20%
  around the FY2016–17 Ind AS switch. This is a reason to prefer first-published figures for
  2015–2017.
- Lag rule used:
  - P&L and balance sheet: public at screener's `public_at`, which is NSE's filing time, else
    the 60-day deadline.
  - CFO: year end + 183 days (the annual report; half-year CF was only required from FY2020).

## 3. Cross-sectional study, 2016–2021

**Design.**
- Universe: PIT NIFTY 500 members with a price on each formation day.
- Formation: first session of January and July; the annual variant is January only.
- Books: equal-weight buy and hold, total-return closes. A name whose series ends is held flat.
- Factors:
  - Value sorts use non-financials with fundamentals.
  - Momentum: 12-1 month return.
  - EY = net profit / market cap; BP = equity / market cap; CFOP = CFO / market cap.
  - EBIT/EV = (operating profit − depreciation) / (market cap + borrowings). No cash deduction:
    screener has no cash line.
  - VAL = mean percentile of EY, BP, CFOP and EBIT/EV (at least 3 of the 4 present).
  - Quality = ROCE ≥ 15%, D/E ≤ 1, CFO > 0, profit > 0.
  - MAGIC = rank ROCE + rank EBIT/EV.
  - VM = mean of the VAL and momentum percentiles.
- Covered non-financials per formation: 289 (2016-01) rising to 370 (2021-07).
- MOM Q5 uses all members. MOMnf uses the same covered non-financial set as value.
- **The fair benchmark for value is "EW covered non-fin"**, because it carries the same
  survivorship as the value books.

### Per-year returns %, semi-annual formation (`study_semi.csv`)

| Book | n | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | CAGR | vs TRI | vs cov EW | Max DD | yrs>TRI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NIFTY 500 TRI |  | 4.7 | 37.7 | -2.1 | 9.0 | 17.9 | 31.6 | 15.6 | +0.0 | -4.1 | -38.1 | – |
| EW all members | 501 | 1.8 | 51.6 | -20.3 | -7.2 | 25.4 | 49.0 | 13.5 | -2.1 | -6.2 | -54.8 | 3 |
| EW covered non-fin | 328 | 8.0 | 58.1 | -15.2 | -2.1 | 33.3 | 55.3 | 19.7 | +4.1 | 0.0 | -47.9 | 4 |
| uncovered members | 115 | -12.5 | 38.7 | -32.0 | -26.8 | 14.6 | 30.8 | -1.6 | -17.2 | -21.3 | -70.2 | 1 |
| VAL Q1 (expensive) | 66 | -1.1 | 48.7 | -8.1 | 3.0 | 40.5 | 44.0 | 18.8 | +3.2 | -0.9 | -33.5 | 3 |
| VAL Q3 | 65 | 8.8 | 60.2 | -14.7 | 0.1 | 33.8 | 56.2 | 20.8 | +5.2 | +1.1 | -47.9 | 4 |
| VAL Q5 (cheap) | 66 | 22.7 | 73.6 | -22.2 | -9.7 | 21.7 | 60.3 | 19.5 | +3.9 | -0.2 | -60.9 | 4 |
| EY Q5 | 66 | 22.7 | 71.5 | -21.5 | -11.7 | 22.5 | 51.6 | 18.1 | +2.5 | -1.6 | -61.6 | 4 |
| BP Q5 | 66 | 16.2 | 94.5 | -26.2 | -18.7 | 29.0 | 69.4 | 19.8 | +4.2 | +0.1 | -67.9 | 4 |
| CFOP Q5 | 66 | 16.8 | 69.8 | -26.6 | -8.5 | 29.4 | 67.2 | 19.3 | +3.7 | -0.4 | -62.7 | 4 |
| EBIT/EV Q5 | 66 | 21.1 | 74.3 | -20.8 | -11.4 | 26.1 | 58.6 | 19.8 | +4.2 | +0.1 | -62.8 | 4 |
| MAGIC Q5 | 66 | 14.2 | 49.3 | -15.9 | -5.4 | 24.1 | 56.0 | 17.5 | +1.9 | -2.2 | -53.6 | 4 |
| QUALITY (all passing) | 157 | 5.3 | 46.9 | -10.2 | 0.6 | 32.3 | 51.2 | 18.7 | +3.1 | -1.0 | -40.3 | 4 |
| QV (quality & VAL Q5) | 22 | 27.8 | 65.6 | -12.8 | -8.9 | 15.1 | 53.5 | 19.9 | +4.3 | +0.2 | -57.2 | 3 |
| MOM Q5 (all members) | 98 | -1.5 | 73.3 | -25.5 | 9.9 | 28.1 | 69.3 | 20.3 | +4.7 | +0.6 | -45.8 | 4 |
| MOMnf Q1 | 65 | 2.2 | 55.1 | -7.8 | -9.6 | 37.9 | 37.0 | 16.5 | +0.9 | -3.2 | -56.6 | 3 |
| MOMnf Q5 | 65 | 1.0 | 77.3 | -22.9 | 8.2 | 38.6 | 75.0 | 24.0 | +8.4 | +4.3 | -42.9 | 3 |
| VM Q4 | 64 | 13.5 | 74.5 | -15.5 | -0.6 | 33.6 | 66.1 | 24.3 | +8.7 | +4.6 | -46.1 | 4 |
| VM Q5 | 65 | 9.3 | 70.9 | -29.3 | -2.5 | 27.9 | 81.4 | 20.0 | +4.4 | +0.3 | -57.7 | 4 |
| VAL Q5 & mom > 0 | 31 | 18.5 | 78.1 | -23.8 | 1.8 | 6.1 | 65.6 | 19.3 | +3.7 | -0.4 | -51.6 | 3 |
| 50/50 VAL Q5 + MOM Q5 |  | 10.3 | 73.5 | -23.8 | -0.1 | 25.1 | 64.9 | 20.1 | +4.5 | +0.4 | -53.5 | 4 |
| 50/50 QV + MOM Q5 |  | 13.0 | 69.4 | -19.3 | 0.4 | 21.9 | 61.3 | 20.5 | +4.9 | +0.8 | -51.0 | 4 |

**Annual (January-only) robustness** (`study_annual.csv`):

| Book | CAGR | vs cov EW | Max DD |
|---|---|---|---|
| VAL Q5 | 20.2 | +0.5 | −59.9 |
| VAL Q1 | 17.5 | −2.2 | −33.7 |
| EBIT/EV Q5 | 21.6 | +1.9 | −60.5 |
| QV | 16.5 | −3.2 | −54.1 |
| MOMnf Q5 | 20.9 | +1.2 | −47.3 |
| VAL Q5 & mom > 0 | 22.0 | +2.3 | −53.1 |
| VM Q4 | 22.0 | +2.3 | −49.0 |
| 50/50 VAL + MOM | 20.0 | +0.3 | −54.0 |

**Value vs momentum.** Spearman of the VAL and momentum ranks, per formation:

| Formation | Spearman | Formation | Spearman | Formation | Spearman |
|---|---|---|---|---|---|
| 2016-01 | −0.32 | 2018-01 | −0.20 | 2020-01 | −0.43 |
| 2016-07 | +0.10 | 2018-07 | −0.27 | 2020-07 | −0.43 |
| 2017-01 | −0.00 | 2019-01 | −0.41 | 2021-01 | −0.30 |
| 2017-07 | +0.09 | 2019-07 | −0.30 | 2021-07 | −0.07 |

- Only 3–27% of VAL Q5 names are also in the momentum top quintile.
- The daily returns of the two top books correlate at 0.90, because market and small-cap beta
  dominate both. Their excess returns over equal weight correlate at −0.21.

**Reading.**
- The value spread (Q5 − Q1) is about +0.7 pts per year on the semi-annual formation and +2.7 on
  the annual one. It changes sign by regime: +24 in 2016, −14 in 2018, −13 in 2019, −19 in 2020.
  Survivorship probably favours cheap names, so this is an upper bound.
- Momentum within the same covered set is stronger and more stable: MOMnf Q5 − Q1 is +7.5 pts
  per year.
- The best combinations (VM Q4, value with momentum > 0) beat covered equal weight by about
  2–5 pts. But they are one of several cuts tried, and their drawdowns are no lower than
  momentum alone.
- Equal-weighted books are small-cap heavy. That, more than the factor, explains the −45% to
  −60% drawdowns in the 2018–20 small-cap bear market and COVID (cap-weighted TRI: −38%).

## 4. Recommendation

**Definition to carry forward:** quality-screened value composite.
- Rank on EBIT/EV, earnings yield (owners' profit) and CFO/price.
- Screen: ROCE ≥ 15%, D/E ≤ 1, CFO > 0.
- Non-financials only.
- Fiscal-year figures, with first-published P&L and balance sheet from the filing time.

**Use it to lift and broaden the momentum book, not to cut its drawdown.**
- Keep the rotation; break ties in its candidate list by VAL; exclude the most expensive
  quintile (the glamour names that drove the 2025 crowding).
- For drawdown, the evidence points to *quality* and to size/beta control, not to cheapness.
- Re-test only on the de-biased universe.

**Data work first (outcome spec for a builder; m1 is the data writer, hat_live write with backup):**
1. **Scope:** fundamentals for every PIT NIFTY 500 member on any day from 2012-07 (not only
   members from 2020), including delisted and merged names, by chain. Done when
   member-coverage ≥ 95% per year for 2013–2021.
2. **NSE first-published history:**
   - Parse the cached-listed HTML results pages for 2012–2017: quarterly P&L, EPS, paid-up
     capital, face value, and annual reserves excluding revaluation. Store them as
     `source=nse_html`, `point_in_time=true`, `public_at` from the announcement rules.
   - Fetch the 2018–2019 XBRL with the existing fetcher (`from_date` back to 2012).
   - Fill the remaining 2017–2019 holes from BSE XBRL, if the owner approves BSE as a source.
3. **Screener pages for the pre-2020 leavers and the standalone-only companies,** standalone
   page where consolidated is absent. Keep the deadline lag: P&L and balance sheet at 60 days,
   CFO and full balance sheet at year end + 183 days for years before FY2020.
4. **Research view:** a per-(instrument, as-of) value panel that prefers first-published NSE
   figures and falls back to lagged screener figures, with a flag per figure. Shares come from
   paid-up capital ÷ face value, never from EPS. Done when the FY2016–17 restatement test
   (HTML vs screener) is reported for all members.
5. Then rerun this study (2013–2021, de-biased) with the cap/size and industry-neutral variants.
   Only then propose engine runs that combine the value tilt with momentum.
