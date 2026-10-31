# 10-year in-sample (2012–2021): data check and proposal — awaiting owner go

## Data coverage 2011–2016 (checked 2026-10-31, read-only; `is10-work/coverage_1115.py`)

| Source | Starts | Gaps 2012–2016 | Note |
| --- | --- | --- | --- |
| EQ daily bars (`bars_daily_raw`) | 2011-06-22 | 0 sessions missing | 1,140–1,510 EQ stocks/day |
| `breadth_daily` | 2011-06-22 | 0 | over all EQ stocks; first ~50 sessions NaN (SMA50 warm-up) |
| NIFTY 500 + NIFTY 500 TRI | **2012-02-21** | 0 after start | benchmark from 2012-02-21 |
| **PIT NIFTY 500 membership** | **2016-01-01** | **none before 2016** | runs before 2016 fail closed (`backtest_no_index_membership`) |
| Industry (`hat_industry`) | 2010-01-02 | 135 of 501 members unknown already in mid-2016 | worse earlier; archived CNX 500 lists carry an Industry column |

**Effective window:** bars from 2011-06-22 plus a ~12-month momentum look-back → first trades ~mid-2012.
In-sample = **2012-07-01 → 2021-12-31** (9.5 years). 2022–2025 is a spent hold-out.

## The blocker: NIFTY 500 membership 2011-06 → 2015-12

The 2026-10-28 build stopped at 2016 because undoing notices back to 2011 gave 13 conflicts. We hold
archived full lists for **2010-01-02, 2014-01-22, 2014-07-09, 2015-03-25**. Checked against the notices
parsed between them (symbols, before renames are resolved):

| Span | Real changes | Not explained by a notice |
| --- | --- | --- |
| 2014-01-22 → 2014-07-09 | 19 | 5 out / 6 in — almost all symbol renames (DCB→DCBBANK, DCMSRMCONS→DCMSHRIRAM …) |
| 2014-07-09 → 2015-03-25 | 22 | 3 / 3 |
| 2010-01-02 → 2014-01-22 | 135 | 68 / 62 — notices before 2011 are not on the press page, plus renames |

So 2014–2015 is near-complete; 2011-06 → 2014-01 depends on 2011–2013 notices (27 found).

**Proposed data work (builder, m1, hat_live write with backup per the usual rule):**
1. Extend `scripts/data/nifty500_membership.py build` to **anchor segments on the archived lists**:
   undo notices backwards from each snapshot (2015-03-25, 2014-07-09, 2014-01-22) rather than from
   today only, resolve renames via symbol history, record every residual mismatch in `overrides.json`
   with the 2015 swaps (CMC, MASTEK, SHASUNPHAR) taken from the snapshot. Report residual error per year.
2. Load membership from 2011-06-22. Target: 0 conflicts 2014-01 → 2016; for 2011-06 → 2014-01 a stated
   residual (expect ≤ ~10 names of 500).
3. Industry before 2016: fill unknowns for pre-2016 members from the archived lists' Industry column
   (PIT as of each list date), flagged as a separate source.

**Robustness cross-check (no extra data needed):** run the chosen configs also on a rule-based PIT
universe — top 500 EQ stocks by trailing 6-month median traded value, re-formed each March/September from
bhavcopies (which include delisted names). If results on the two universes agree, the membership residual
does not matter.

## Proposed test design (after the leak audits land and fixes are merged)

- **Walk-forward:** rolling 3-year fit → 1-year test, test years 2015…2021 (7 out-of-sample years
  inside the in-sample span); plus per-year stability for 2012–2021.
- **Fewer knobs:** base rotation plus at most 2 levers. A config is kept only if it beats TRI in a
  majority of test years and its worst test year is no worse than the base. No lever fit to one year.
- Reports lead with invested %, positions, size, zero-position days (standard).
- **Hold-out:** 2022–2025 is spent. Proposal: the clean final check is **2026-01-01 → latest** plus
  paper trading from now; agree with the owner before touching it.
