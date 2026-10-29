# S2 EP A4: results-store validation (hat_live, 2026-10-28)

Plan: `docs/plans/s2-ep-refinement.md`, step A4. A0: `/data/workspace/audits/2026-10-28-s2-ep-a0-probe.md`.

**Status:** this is for owner review. No code was changed for A4, and no backtest was run.

**Evidence:** `/data/workspace/audits/2026-10-28-s2-ep-a4-evidence/` (abbreviated `E/` below). It holds:
- the scripts `a4.py`, `a4_diag.py`, `spot.py`, `render.py` and `sheet.py`;
- their outputs `a4_live.md`, `a4_diag.txt`, `spot.json`, `spot.log` and `spot_table.md`;
- the parse outcomes `filings.csv`;
- the PDF pages read visually, in `png/`.

## 0. What ran

All steps ran from main, with `DB_NAME=hat_live HAT_DATA_ROOT=/data/workspace/hat-data-isin`. Logs are under `/data/workspace/hat-data-isin/results/`.

| step | code | result | log |
| --- | --- | --- | --- |
| `fetch` (NSE), read-only DB | main fd54d6bb (#301) | crashed at member 750 of 812, 11:27 UTC: FORCEMOT's listing came back as `{"data": [], "msg": "no data found"}` | `fetch-2026-10-28-scope.log` |
| `fetch`, resumed | #305 branch e1d10b80, merged as 70358e32 | `FetchReport(members=812, listings=1754, documents=17502, documents_fetched=563, announcement_days=2402, statuses={200: 678})`, no errors | `fetch-2026-10-28-scope-resume.log` |
| `fetch-secondary`, read-only DB | fd54d6bb | `SecondaryReport(members=812, pages=901, fetched=226, statuses={404: 4, 200: 222})` | `fetch-secondary-2026-10-28-scope.log` |
| `parse` | 70358e32 | `ParseReport(members=812, stored=17381, secondary=726, outcomes={'stored': 18107, 'same_figures': 237, 'already_stored': 146, 'excluded': 141, 'insurance_skipped': 97})` | `parse-2026-10-28-scope.log` |
| `derive` | 70358e32 | `DeriveReport(instruments=810, rows=18107, unit_suspect=40, defined_sales=14167, defined_eps=12129)` | `derive-2026-10-28-scope.log` |

- **Scope:** the NIFTY 500 point-in-time members from 2021-01-01, which is 812 instruments, on a consolidated-first basis. The period ends run from 2020-03-31 to 2026-09-30.
- **hat_financial_result was empty before this parse.** Its 18,204 rows are the 18,107 stored outcomes plus 97 insurer metadata rows (`E/a4_live.md`, Counts).
- **`already_stored` (146)** means the same document content (sha256) appeared under a second listing entry in this run.
- **Rows exist for 810 instruments, 792 of them with NSE figures.**

## 1. Findings

The NSE XBRL path holds up on most of the data. Standalone net profit agrees with the secondary source for 99.1% of quarters (§5), and 17 of 20 random PDF checks match on all three fields (§3).

Three defects in our code produce wrong rows. They need a fix PR, which is the owner's call after this review.

| # | defect | rows | effect | where |
| --- | --- | --- | --- | --- |
| D1 | **Q4 derivation on a mislabelled quarter.** Some Integrated Filing documents put Q4 in a 181-day `OneD` context (2024-10-01 to 2025-03-31) next to a correct 12-month `FourD`. `_annual_only` treats any span over 100 days as "the year only", so it uses the 181-day figure as the year and subtracts nine months. | all 51 `q4_derived` rows; every one has negative revenue | wrong Q4 figures. 69 growth rows touch them, 44 with a sales_yoy defined. | `backend/app/hat/data/results/xbrl.py:359` (`return span > 100`), called at `xbrl.py:336` |
| D2 | **Period mismatch creates a false revision.** A June 2025 Integrated filing whose XBRL dates itself 2024-06-30 is stored, because the document's period wins, as version 2 of Q1 FY25. It carries the Q1 FY26 figures. | 2 (AARTIDRUGS, MMTC) | Q1 FY25 reads as Q1 FY26 from the filing time. AARTIDRUGS Q1 FY26 YoY becomes 590.51 against 590.51 cr, i.e. 0%. 3 growth rows touch them. | `backend/app/hat/data/results/ingest.py:274` (`document_period`), `ingest.py:406` |
| D3 | **Filer tag swap on owners' profit.** `ProfitOrLossAttributableToOwnersOfParent` equals total comprehensive income, with NCI 0 and the period profit different. We prefer the owners' tag, so we store the filer's error. | 188 of 15,239 consolidated quarters (1.2%) | wrong net profit and turnaround input; EPS is unaffected | `backend/app/hat/data/results/xbrl.py:243` |

One rule behaves as documented but differs from the PDF. **2,327 of 15,239 consolidated quarters (15.3%) have no owners'-profit tag**, so profit falls back to the period's total profit (`xbrl.py:240-246`, module docstring). In the GRINFRA spot row that differs by 0.18%.

### Proposed fixes (not implemented)

- **D1:** when `OneD` spans more than 100 days and `FourD` spans the year with different figures, read `OneD` as the quarter with a mislabelled start, and flag it. Derive Q4 only when `OneD` itself is the year. Evidence: 37 of the 42 D1 rows that appear on a secondary page have a `OneD` revenue within 5% of the secondary quarter. The other 5 include CGCL, a genuine half-year, and RAJESHEXPO, whose filing values are themselves garbage (`E/a4_diag.txt` D1).
- **D2:** when the document's period is exactly a year before the listing's, trust the listing (or exclude the document) instead of writing a revision.
- **D3:** when the owners' tag equals `ComprehensiveIncomeForThePeriod`, differs from `ProfitLossForPeriod`, and NCI is 0 or absent, use the period profit and flag the row.

Because the table is append-only, corrected rows would come in as new versions.

## 2. Coverage by year and format

Source: the parse outcomes `E/filings.csv` (18,728 rows), with secondary rows from the DB (`E/a4_live.md`).

- **found** = filings in scope after the basis rule.
- **already/same** = the content was already stored, or the figures are identical to the held version.
- **(unread)** = outcomes recorded before the format was read: duplicates, 404s and missing periods.

| year | format | found | stored | already/same | insurance | excluded |
| --- | --- | --- | --- | --- | --- | --- |
| 2020 | (unread) | 2 | 0 | 0 | 0 | 2 |
| 2020 | reg33_banking | 129 | 129 | 0 | 0 | 0 |
| 2020 | reg33_indas | 2048 | 2047 | 1 | 0 | 0 |
| 2020 | reg33_nbfc | 167 | 163 | 4 | 0 | 0 |
| 2021 | (unread) | 44 | 0 | 0 | 0 | 44 |
| 2021 | reg33_banking | 91 | 91 | 0 | 0 | 0 |
| 2021 | reg33_indas | 2127 | 2124 | 3 | 0 | 0 |
| 2021 | reg33_nbfc | 179 | 178 | 1 | 0 | 0 |
| 2022 | (unread) | 13 | 0 | 1 | 0 | 12 |
| 2022 | reg33_banking | 103 | 102 | 1 | 0 | 0 |
| 2022 | reg33_indas | 2144 | 2140 | 4 | 0 | 0 |
| 2022 | reg33_nbfc | 180 | 180 | 0 | 0 | 0 |
| 2023 | (unread) | 22 | 0 | 0 | 0 | 22 |
| 2023 | reg33_banking | 115 | 114 | 1 | 0 | 0 |
| 2023 | reg33_indas | 2316 | 2308 | 8 | 0 | 0 |
| 2023 | reg33_nbfc | 199 | 199 | 0 | 0 | 0 |
| 2024 | (unread) | 1 | 0 | 1 | 0 | 0 |
| 2024 | insurance_skipped | 22 | 0 | 0 | 22 | 0 |
| 2024 | integrated_indas | 3 | 2 | 0 | 0 | 1 |
| 2024 | reg33_banking | 136 | 136 | 0 | 0 | 0 |
| 2024 | reg33_indas | 2421 | 2394 | 27 | 0 | 0 |
| 2024 | reg33_nbfc | 213 | 210 | 3 | 0 | 0 |
| 2025 | (unread) | 72 | 0 | 71 | 0 | 1 |
| 2025 | insurance_skipped | 45 | 0 | 0 | 45 | 0 |
| 2025 | integrated_banking | 147 | 141 | 3 | 0 | 3 |
| 2025 | integrated_indas | 2767 | 2637 | 83 | 0 | 47 |
| 2025 | integrated_nbfc | 284 | 269 | 13 | 0 | 2 |
| 2025 | other | 7 | 7 | 0 | 0 | 0 |
| 2026 | (unread) | 73 | 0 | 73 | 0 | 0 |
| 2026 | insurance_skipped | 30 | 0 | 0 | 30 | 0 |
| 2026 | integrated_banking | 105 | 100 | 4 | 0 | 1 |
| 2026 | integrated_indas | 1605 | 1532 | 67 | 0 | 6 |
| 2026 | integrated_nbfc | 189 | 175 | 14 | 0 | 0 |
| 2026 | other | 3 | 3 | 0 | 0 | 0 |

### Excluded, by reason (141)

| reason | count | where (period, listing) |
| --- | --- | --- |
| xbrl_http_404 | 75 | Reg 33 2021-03 to 2023-09 (74), Integrated 2025-03 (1): NSE answers 404 for the XBRL |
| q4_nine_month_missing | 60 | Integrated; 48 of them 2025-09 |
| period_missing | 6 | Reg 33 2020-03 to 2021-12 |

`q4_nine_month_missing` is the same `_annual_only` rule as D1, but here it fails safe. 57 of these 60 documents have a 180–182-day `OneD` and no `FourD`. Against the secondary quarter, 39 of those `OneD` revenues are about a half-year, 5 about a quarter, 9 neither, and 7 have no secondary quarter. So they are mostly genuine half-year figures, and excluding them is correct. A later change could derive the quarter as H1 − Q1 (`E/a4_diag.txt` D5).

### Secondary-source rows backfilled (726)

These are quarters with no NSE row of the same basis; counts are from the DB (`E/a4_live.md`).

| year | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rows | 7 | 9 | 14 | 232 | 339 | 100 | 25 |

By basis: 702 consolidated, 24 standalone. The 30 rows before 2023 come from pages whose 13 quarters end early, e.g. KENNAMET 2020-03-31 and HEXT 2020-06-30 (§6).

## 3. Spot check: 20 random company-quarters against the results PDFs

- **Sample:** `E/spot.py`, seed 20261028, from 17,288 NSE (instrument, period, basis) keys at their latest version (`E/spot.json`).
- **PDF:** the results announcement's attachment, matched as in `spot.py:65`. Two announcements the matcher missed (IREDA and CARBORUNIV, "Outcome of Board Meeting" text) were found by hand in the announcement cache.
- **Automatic matching:** each stored value is searched for in the PDF text in rupees, thousands, lakhs, millions or crores (`spot.py:129`).
- **Manual reading:** 7 PDFs are scanned or carry a garbled OCR layer. Their pages were rendered and read visually; the images are in `E/png/`.

**Result:** 17 of 20 match on revenue, net profit and EPS. The 3 mismatches are listed below.

| # | symbol | period end | basis | format | v | revenue cr | net profit cr | EPS | PDF evidence | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CHENNPETRO | 2024-03-31 | consolidated | reg33_indas | 1 | 20,822.95 | 627.89 | 42.17 | p14 (₹ cr), read visually: 20,822.95 / 627.89 / 42.17 | match |
| 2 | JTEKTINDIA | 2025-03-31 | standalone | integrated_indas | 1 | 649.19 | 24.65 | 0.97 | p5 (₹ lakh), scanned, read visually: 64,918.71 / 2,464.55 / 0.97 | match |
| 3 | BRIGADE | 2023-12-31 | consolidated | reg33_indas | 1 | 1,173.77 | 73.49 | 3.18 | p6 (₹ lakh), scanned, read visually: 1,17,377 / 7,349 owners / 3.18 | match |
| 4 | IREDA | 2025-09-30 | consolidated | integrated_nbfc | 1 | 2,057.28 | 614.76 | 1.97 | p21 (₹ cr), read visually: 2,057.28 / **549.33** / 1.97 | **net profit mismatch (D3)**: 614.76 is total comprehensive income |
| 5 | KTKBANK | 2022-06-30 | consolidated | reg33_banking | 1 | 1,629.08 | 114.05 | 3.66 | text, auto: crores / crores / rupees (2dp) | match |
| 6 | CARBORUNIV | 2022-06-30 | consolidated | reg33_indas | 1 | 1,139.83 | 78.77 | 4.15 | text, auto: lakhs / lakhs / rupees (2dp) | match |
| 7 | JSWDULUX | 2020-09-30 | consolidated | reg33_indas | 1 | 606.86 | 66.28 | 14.56 | zip p8 (₹ mn), scanned, read visually: 6,068.6 / 662.8 / 14.56 | match |
| 8 | GRINFRA | 2025-03-31 | consolidated | integrated_indas | 1 | 2,275.57 | 403.16 | 41.75 | p19 (₹ lakh), read visually: 2,27,557.42 / **40,389.62** owners (40,315.95 total) / 41.75 | **net profit mismatch, 0.18%**: no owners' tag in the XBRL, so total profit is stored |
| 9 | TIMKEN | 2023-09-30 | standalone | reg33_indas | 1 | 681.98 | 93.05 | 12.37 | text, auto: millions / millions / rupees (2dp) | match |
| 10 | STAR | 2021-03-31 | consolidated | reg33_indas | 1 | 908.49 | 46.09 | 5.14 | text, auto: millions / millions / rupees (2dp) | match |
| 11 | BIRLACORPN | 2026-06-30 | consolidated | integrated_indas | 1 | 2,646.45 | 115.73 | 15.03 | text, auto: crores / crores / rupees (2dp) | match |
| 12 | AARTIDRUGS | 2024-06-30 | consolidated | integrated_indas | 2 | 590.51 | 53.91 | 5.91 | p4 (₹ lakh), read visually: **55,534 / 3,324 / 3.62** | **all three mismatch (D2)**: v2 comes from the Jun-2025 filing; v1 (555.34 cr) matches |
| 13 | SONATSOFTW | 2024-09-30 | consolidated | reg33_indas | 1 | 2,169.83 | 106.49 | 3.84 | text, auto: lakhs / lakhs / rupees (2dp) | match |
| 14 | GRINFRA | 2023-12-31 | consolidated | reg33_indas | 1 | 2,134.02 | 242.72 | 25.10 | text, ₹ lakh: revenue and EPS auto; owners' profit 24,271.95 read from the OCR text | match |
| 15 | GUJENERGY | 2023-06-30 | consolidated | reg33_indas | 1 | 3,923.70 | 215.95 | 3.14 | text, auto: crores / crores / rupees (2dp) | match |
| 16 | TCIEXP | 2021-03-31 | standalone | reg33_indas | 1 | 279.80 | 42.57 | 11.08 | p4 (₹ cr), scanned, read visually: 279.80 / 42.57 / 11.08 | match |
| 17 | SAIL | 2026-09-30 | consolidated | integrated_indas | 1 | 31,997.55 | 1,750.47 | 4.24 | text, auto: crores / crores / rupees (2dp) | match |
| 18 | SPARC | 2025-12-31 | consolidated | integrated_indas | 1 | 8.45 | -80.42 | -2.48 | text, auto: lakhs / lakhs / rupees (2dp) | match |
| 19 | CHEMPLASTS | 2025-09-30 | consolidated | integrated_indas | 1 | 1,033.20 | -51.04 | -3.21 | text, auto: crores / crores (1dp) / rupees (2dp) | match |
| 20 | OLECTRA | 2023-09-30 | consolidated | reg33_indas | 1 | 307.16 | 18.58 | 2.20 | text, auto: lakhs / lakhs / rupees (2dp) | match |

### PDF URLs

`E/spot.json` has all of them. The mismatch rows:
- IREDA: https://nsearchives.nseindia.com/corporate/IREDAEQ_14102025101433_SignedOutcomefinancials14102025.pdf
- GRINFRA 2025: https://nsearchives.nseindia.com/corporate/GRINFRA_15052025213150_GRILBMoutcome15052025.pdf
- AARTIDRUGS: https://nsearchives.nseindia.com/corporate/ADL_26072024173436.pdf

### `public_at` side finding

The two announcements the matcher missed got `public_at_source='xbrl'`:
- CARBORUNIV: 2022-08-02 07:21 UTC, against the outcome PDF at 2022-08-01 14:29 IST;
- IREDA: 2025-10-14 05:47 UTC, against 10:14 IST.

Both err late, which is safe against lookahead. Altogether 1,904 NSE rows date from the XBRL time (§4).

## 4. Counts

Source: `E/a4_live.md`, queries on hat_live.

| count | rows | query |
| --- | --- | --- |
| rows | 18,204 | `select count(*) from hat_financial_result` |
| nse rows | 17,478 | `... where source='nse'` |
| secondary rows | 726 | `... where source='secondary'` |
| insurer metadata rows | 97 | `... where format='insurance_skipped'` |
| q4_derived | 51 (all defective, D1) | `... where q4_derived` |
| period_mismatch | 2 (both defective, D2) | `... where period_mismatch` |
| revisions (version > 1) | 103 | `... where version > 1` |
| public_at_estimated | 423 | `... where public_at_estimated` |
| unit_suspect | 40 | `select count(*) from hat_financial_growth where unit_suspect` |
| growth rows / with sales_yoy / with eps_yoy | 18,107 / 14,167 / 12,129 | `hat_financial_growth` |

| source | public_at_source | estimated | rows |
| --- | --- | --- | --- |
| nse | announcement | no | 15,556 |
| nse | xbrl | no | 1,904 |
| nse | xbrl_date | yes | 18 |
| secondary | announcement | no | 321 |
| secondary | deadline | yes | 405 |

None of the 40 unit-suspect rows is a q4_derived row (D1 rows were not caught by the 20x rule).

## 5. Cross-check against the secondary source

Every NSE quarter (latest version) that the cached secondary page also shows on the same basis was compared: **8,772 pairs**.

**Mismatch** means a relative difference over 1% and an absolute difference over ₹0.5 cr, or ₹0.01 for EPS (`E/a4.py`, `crosscheck`).

| field | basis | compared | mismatched | rate |
| --- | --- | --- | --- | --- |
| revenue | consolidated | 8,427 | 534 | 6.34% |
| revenue | standalone | 345 | 21 | 6.09% |
| revenue | all | 8,772 | 555 | 6.33% |
| net profit | consolidated | 8,427 | 2,682 | 31.83% |
| net profit | standalone | 345 | 3 | 0.87% |
| net profit | all | 8,772 | 2,685 | 30.61% |
| EPS | consolidated | 8,424 | 1,730 | 20.54% |
| EPS | standalone | 345 | 30 | 8.70% |
| EPS | all | 8,769 | 1,760 | 20.07% |

What the mismatches are (`E/a4_diag.txt` D4):

- **Consolidated net profit (2,681 in the diagnostic's count) is mostly definitional.** The secondary source shows total profit including minority interest; we store owners' profit. In a seeded sample (seed 1) of 296 mismatches with a period-profit tag, 280 (94.6%) agree once NSE's `ProfitLossForPeriod` is used. The residue includes D3 rows. Standalone, where there is no minority interest, mismatches on only 0.87%.
- **Revenue (555):**
  - 297 have the secondary source 1–15% below NSE. Its "Sales" is narrower than `RevenueFromOperations`, which matches the A0 note.
  - 47 have it 1–15% above.
  - 15 are D1 rows.
  - 196 differ by more than 15%. These include filer scale errors (3 at ~100×, 1 at ~10×: PFC 2023-12-31, NAVNETEDUL 2026-03-31, METROBRAND 2025-09-30) and D1 neighbours.
  - Of the 555, 26 are banking or NBFC rows.
- **EPS (1,760):**
  - 715 have net profit differing too (consolidated).
  - 384 sit at an integer ratio, 377 consolidated and 7 standalone. This is the secondary source adjusting past EPS for splits and bonuses: NESTLEIND 2023-09-30 stores 94.18 against 4.71 on the page, 20×. NSE's figure is as reported.
  - 507 are within 15%, and 132 are otherwise unexplained.
  - 15 are D1 rows.

### Worst 20 by relative difference

From `E/a4_live.md`. Values are NSE, then the secondary source.

**Revenue.** 13 of these 20 are D1 (−ve Q4 on 2025-03-31). RAJESHEXPO 2026-06-30, PFC, NAVNETEDUL, METROBRAND and PAYTM are scale errors in the filings.

| symbol | period_end | basis | NSE | secondary | rel diff |
| --- | --- | --- | --- | --- | --- |
| RAJESHEXPO | 2026-06-30 | consolidated | 1,317.89 cr | 240,336.00 cr | 18136.4% |
| PFC | 2023-12-31 | consolidated | 235.72 cr | 23,572.00 cr | 9900.1% |
| NAVNETEDUL | 2026-03-31 | consolidated | 4.30 cr | 430.00 cr | 9900.0% |
| METROBRAND | 2025-09-30 | consolidated | 6.51 cr | 651.00 cr | 9897.8% |
| EMBDL | 2024-03-31 | consolidated | 21.02 cr | 380.00 cr | 1707.8% |
| PAYTM | 2023-09-30 | consolidated | 251.86 cr | 2,519.00 cr | 900.2% |
| ONESOURCE | 2024-09-30 | consolidated | 67.98 cr | 334.00 cr | 391.3% |
| SUDARSCHEM | 2025-03-31 | consolidated | -646.70 cr | 1,349.00 cr | 308.6% |
| SYMPHONY | 2025-03-31 | consolidated | -600.00 cr | 488.00 cr | 181.3% |
| WELCORP | 2025-03-31 | consolidated | -6,127.60 cr | 3,925.00 cr | 164.1% |
| COFORGE | 2025-03-31 | consolidated | -5,371.40 cr | 3,422.00 cr | 163.7% |
| CGPOWER | 2025-03-31 | consolidated | -4,403.12 cr | 2,753.00 cr | 162.5% |
| SHYAMMETL | 2025-03-31 | consolidated | -6,858.78 cr | 4,139.00 cr | 160.3% |
| BALKRISIND | 2025-03-31 | consolidated | -4,942.19 cr | 2,752.00 cr | 155.7% |
| ZEEL | 2025-03-31 | consolidated | -3,925.90 cr | 2,184.00 cr | 155.6% |
| PFIZER | 2025-03-31 | standalone | -1,097.53 cr | 592.00 cr | 153.9% |
| SANSERA | 2025-03-31 | consolidated | -1,453.45 cr | 782.00 cr | 153.8% |
| GVPIL | 2025-03-31 | consolidated | -514.34 cr | 266.00 cr | 151.7% |
| MANKIND | 2025-03-31 | consolidated | -6,120.56 cr | 3,079.00 cr | 150.3% |
| SYRMA | 2025-03-31 | consolidated | -1,937.47 cr | 924.00 cr | 147.7% |

**Net profit.** These are mostly NSE values that are tiny next to the page (PRAJIND, RPOWER, GLENMARK). That points to scale or tag errors in the filings, but I did not diagnose them one by one. PFC and METROBRAND repeat their revenue scale error.

| symbol | period_end | basis | NSE | secondary | rel diff |
| --- | --- | --- | --- | --- | --- |
| PRAJIND | 2025-12-31 | consolidated | -0.00 cr | -12.00 cr | 1199900.0% |
| PRAJIND | 2024-09-30 | consolidated | 0.01 cr | 54.00 cr | 650502.4% |
| RPOWER | 2024-09-30 | consolidated | -0.56 cr | 2,878.00 cr | 514028.6% |
| GLENMARK | 2026-03-31 | consolidated | -0.10 cr | 301.00 cr | 316942.1% |
| PVRINOX | 2024-06-30 | consolidated | 0.10 cr | -179.00 cr | 179100.0% |
| KAYNES | 2024-09-30 | consolidated | 0.12 cr | 60.00 cr | 51624.1% |
| PRIVISCL | 2024-06-30 | consolidated | -0.06 cr | 31.00 cr | 49463.1% |
| DEVYANI | 2024-09-30 | consolidated | 0.02 cr | -5.00 cr | 29511.8% |
| SHYAMMETL | 2025-09-30 | consolidated | -1.31 cr | 260.00 cr | 19947.3% |
| PFC | 2023-12-31 | consolidated | 47.68 cr | 6,294.00 cr | 13101.2% |
| WAAREEENER | 2025-12-31 | consolidated | 9.52 cr | 1,107.00 cr | 11528.2% |
| NAVNETEDUL | 2026-03-31 | consolidated | 0.38 cr | 39.00 cr | 10163.2% |
| METROBRAND | 2025-09-30 | consolidated | 0.68 cr | 69.00 cr | 10093.5% |
| KIRLOSBROS | 2025-06-30 | consolidated | 0.80 cr | 68.00 cr | 8400.0% |
| ADANIPORTS | 2025-06-30 | consolidated | 52.67 cr | 3,311.00 cr | 6186.3% |
| STAR | 2024-06-30 | consolidated | 70.20 cr | 3,350.00 cr | 4671.9% |
| FRETAIL | 2020-03-31 | consolidated | 11.57 cr | -478.00 cr | 4230.3% |
| SOLARINDS | 2024-09-30 | consolidated | 7.76 cr | 304.00 cr | 3817.5% |
| CARERATING | 2023-06-30 | consolidated | 0.55 cr | 18.00 cr | 3198.5% |
| JBCHEPHARM | 2024-03-31 | consolidated | -4.24 cr | 126.00 cr | 3071.7% |

**EPS.**

| symbol | period_end | basis | NSE | secondary | rel diff |
| --- | --- | --- | --- | --- | --- |
| STAR | 2024-06-30 | consolidated | 7.64 | 364.69 | 4673.4% |
| FRETAIL | 2020-03-31 | consolidated | 0.23 | -9.09 | 4052.2% |
| SWIGGY | 2024-09-30 | consolidated | -2.80 | -62.75 | 2141.1% |
| TMPV | 2025-09-30 | consolidated | -17.50 | 206.85 | 1282.0% |
| VIYASH | 2024-12-31 | consolidated | 0.14 | 1.78 | 1171.4% |
| ADANIENT | 2024-12-31 | consolidated | 0.04 | 0.45 | 1025.0% |
| SWANCORP | 2025-12-31 | consolidated | -0.04 | -0.31 | 675.0% |
| EMBDL | 2024-06-30 | consolidated | -0.49 | 1.93 | 493.9% |
| PFIZER | 2025-03-31 | standalone | -23.10 | 72.34 | 413.2% |
| ALLCARGO | 2025-09-30 | consolidated | -0.03 | 0.09 | 400.0% |
| TRIVENI | 2025-06-30 | consolidated | 0.02 | 0.10 | 400.0% |
| ALLCARGO | 2025-03-31 | consolidated | -0.12 | 0.25 | 308.3% |
| TITAGARH | 2025-03-31 | consolidated | 4.79 | -9.09 | 289.8% |
| RAJESHEXPO | 2026-06-30 | consolidated | 0.42 | 1.60 | 281.0% |
| VIYASH | 2025-09-30 | consolidated | 0.59 | 2.18 | 269.5% |
| SYRMA | 2025-03-31 | consolidated | -2.20 | 3.67 | 266.8% |
| EMBDL | 2024-09-30 | consolidated | 0.38 | -0.54 | 242.1% |
| SYMPHONY | 2025-03-31 | consolidated | -8.11 | 11.50 | 241.8% |
| WELCORP | 2025-03-31 | consolidated | -19.53 | 26.62 | 236.3% |
| RAJESHEXPO | 2024-03-31 | consolidated | 1.02 | -1.03 | 201.0% |

## 6. How far back the secondary source's public pages go

Pages were fetched 2026-10-28 04:01–05:32 UTC (`E/a4_diag.txt` D6).

- **Cache:** 1,365 entries, of which 1,327 answered 200 and 38 answered 404. 1,201 of the 200s show quarters and 126 show none.
- **Depth:** **1,149 of 1,201 pages show exactly 13 quarters.** The rest show 2–12, for recent listings.
- **Earliest quarter shown:** 2023-06-30 on 776 pages and 2023-09-30 on 327. That is 13 quarters back from each company's latest result (Jun or Sep 2026).
- **So the secondary source covers Jun 2023 onward only.** It cannot fill the 2021–2023 gaps: the 74 Reg 33 404s and the 6 missing periods (§2).
- **Odd pages:** a few pages end years earlier (e.g. KENNAMET, HEXT, RAILTEL; their 2020–2022 quarters account for the 30 pre-2023 secondary rows). One page starts at 2005-12-31.
- **Example page:** https://www.screener.in/company/RELIANCE/consolidated/ (public, no login, fetched at 1 request per 3 s per the owner's rule).

## 7. Not done or open

- **Defects D1–D3 are not fixed.** No new row versions were written. The growth table therefore includes the 69 D1-touched and 3 D2-touched growth rows.
- **Not diagnosed:** the net-profit scale outliers in §5, and the 132 unexplained EPS gaps.
- **Spot sample:** 2 PDFs had to be found by hand (§3), and 7 were read visually because they are scanned.
- No backtest was run, and no EP criterion was changed (Part B).

## 8. A4 fixes applied (2026-10-28)

**What was done**
- **Code:** PR #307 (main 66aaedfd) fixed D1–D3. Its parse guards are described in `docs/decisions.md`. A new column, `hat_financial_result.quality_flags`, records any guard that fired on a row.
- **Rebuild (owner's decision):** `hat_financial_result` and `hat_financial_growth` were rebuilt on hat_live from the raw cache, with no new download. No other table was touched, and the raw cache was only read.
  1. **Backup:** row counts (18,204 results, 18,107 growth) and a `pg_dump -Fc` of the two tables are in `/data/workspace/hat-data-isin/results/backup-2026-10-28/`, along with the old `filings-pre-rebuild.csv`.
  2. **Clear:** `TRUNCATE hat_financial_growth, hat_financial_result`. The append-only trigger fires on rows, not on a truncate.
  3. **Parse and derive** from main. Logs are `results/parse-2026-10-28-rebuild.log` and `derive-2026-10-28-rebuild.log`:
     - `ParseReport(members=812, stored=17351, secondary=725, outcomes={'stored': 18076, 'excluded': 147, 'same_figures': 263, 'already_stored': 144, 'insurance_skipped': 97})`
     - `DeriveReport(instruments=810, rows=18076, unit_suspect=40, defined_sales=14158, defined_eps=12155)`

**Verification** (read-only; `E/rebuild_check.sql` → `E/rebuild_check.txt`, `E/rebuild_secondary.py` → `E/rebuild_secondary.txt`)

| Check | Before | After |
|---|---|---|
| Rows (NSE / secondary / insurer metadata) | 18,204 (17,478 / 726 / 97) | 18,173 (17,448 / 725 / 97) |
| Growth rows | 18,107 | 18,076 |
| `q4_derived` rows / with negative revenue (D1) | 51 / 51 | **0 / 0** |
| `quarter_start_mislabelled` rows (46 documents; 3 documents are stored under two ISINs of one company) | – | 49 |
| Excluded `quarter_context_not_a_quarter` (the old half-year `q4_nine_month_missing` cases plus 3 D1 documents) | – | 62 |
| D2: rows from the AARTIDRUGS/MMTC misdated documents / 2024-06-30 versions > 1 | 2 / 2 | **0 / 0** (both excluded `period_year_before_listing`) |
| `period_mismatch` rows | 2 | 0 |
| `owners_profit_tag_swapped` rows (D3) | – | **180** |
| Duplicate (instrument, period, basis, version) keys | 0 | 0 |

**Against the secondary source**
- **D1:** 35 of the 40 flagged quarters that have a secondary quarter match on revenue within 2%. Of the other 5:
  - CGCL Mar-2025 and RAJESHEXPO Mar-2026 each have a later NSE version that does match (957 cr and 23,686 cr), and readers take the latest version, so 37 of 40 match as read.
  - DCMSHRIRAM (+5%), LTTS (+13%) and IOC Mar-2026 (+14%) differ by more than 2%. Not diagnosed: the revenue tag may differ from the secondary source's line.
- **D3:** 99 of the 101 flagged rows on a secondary page now match on net profit within 2%, up from 53 before the fix. Differing: RKFORGE Sep-2024 and RPOWER Dec-2025.

**Still open**
- The 4 negative-revenue quarters (IDFC Dec-2023, MMTC Sep-2023, HEMIPROP Sep-2022, DBREALTY Mar-2020) are the figures as filed. They were in the old table too and are not derived.
- The D4 items in §5 (net-profit scale outliers, 132 EPS gaps) are not addressed.
- §7's first bullet is superseded by this section. No backtest was run.
