# Idle-cash ETF overlay: Phase 0 data report (2026-10-28)

Plan: `docs/plans/idle-cash-etf-overlay.md`, Phase 0 (data, report only). No backtest was run.
No ETF row was written to `hat_live`. No call went to www.nseindia.com, nsearchives or any NSE
API; the S2 results download (`app.hat.data.results fetch`) and `hat_financial_result` were not
touched.

**Script:** `scripts/data/overlay_etf.py` (`local`, `kotak`, `indices`, `dividends`, `build`). Its pure
helpers are tested in `backend/tests/test_repo_scripts.py::test_overlay__*`.

**Data directory:** `/data/workspace/overlay-data/`, outside the repo. Raw files there are cached
and never overwritten.

| Directory | Contents |
| --- | --- |
| `local/` | Copies from `HAT_DATA_ROOT` and `hat_live`, read-only |
| `kotak/raw/<series>/<interval>/<from>_<to>.json` | One file per broker window, 228 calls in total |
| `niftyindices/<index>/<year>.json` | 36 calls |
| `dividends/raw/*.json` | 4 calls to the AMC |
| `build/` | Built series: `etf_daily_adjusted.csv`, `liquidbees_tr.csv`, `index_daily.csv` and `coverage.json`, the machine-readable version of this report |

Commands as run, from the main checkout so the `.env` loader finds the credentials:

```
PGOPTIONS="-c default_transaction_read_only=on" HAT_DATA_ROOT=/data/workspace/hat-data-isin DB_NAME=hat_live \
  venv/bin/python scripts/data/overlay_etf.py --work /data/workspace/overlay-data local
kotak/venv/bin/python -I scripts/data/overlay_etf.py --work /data/workspace/overlay-data kotak
venv/bin/python scripts/data/overlay_etf.py --work /data/workspace/overlay-data indices
venv/bin/python scripts/data/overlay_etf.py --work /data/workspace/overlay-data dividends
venv/bin/python scripts/data/overlay_etf.py --work /data/workspace/overlay-data build   # expense ratio 0.0069
```

## Sources used

1. **What `hat_live` already has.** All of it was read read-only.
   - Daily bhavcopy bars for all three ETFs, 2011-06-22 to 2026-10-23, from `HAT_DATA_ROOT/bars_daily_raw`.
   - NIFTY 50 and NIFTY 500 TRI closes from `index_daily`.
   - The ETFs' rows in `hat_corporate_action`.
   - `hat_trading_calendar`, which is the calendar for every gap check below.
   - The NIFTY 1D Rate Index rows inside the stored NSE index day files `HAT_DATA_ROOT/raw/ind_close_all_*.csv`. These were downloaded earlier; nothing was fetched now.
2. **Kotak Neo market data.** Only login, scrip_master and historical_data were called, at about one call a second.
3. **niftyindices.com**, the index publisher. It supplied the NIFTY 50 TRI, the NIFTY 500 TRI and the NIFTY 1D Rate Index.
4. **Nippon India MF**, the AMC. Its IDCW history API (`api.nipponindiaim.com/.../FetchDividendDetails?Scheme=LB`) is the API behind the dividend summary page on mf.nipponindiaim.com.

### How far back Kotak serves data (probed)

| Instrument | Daily ("D") | 5-minute |
| --- | --- | --- |
| NIFTYBEES (token 10576) | 2021-10-29 → 2026-10-27, 1,238 sessions | 2021-10-29 → 2026-10-27, 92,051 bars |
| GOLDBEES (14428) | 2021-10-29 → 2026-10-27, 1,238 | 2021-10-29 → 2026-10-27, 91,984 |
| LIQUIDBEES (11006) | 2021-10-29 → 2026-10-27, 1,238 | 2021-10-29 → 2026-10-27, 91,958 |
| NIFTY 50 (by the name "Nifty 50") | 2021-10-29 → 2026-10-27, 1,238 | not fetched |

- Both intervals reach back exactly five years from the IST date. An earlier start date gets the answer `422 fromDate cannot be older than 5 years`.
- A daily request may span at most 180 days (`422 ... must be 180 days or less`). A 5-minute request may span at most 30 days.
- Price indices are served by name: "Nifty 50" and "Nifty 500" work. The numeric index token 26000 is refused (`Invalid neosymbol`).
- Kotak serves neither TRI nor the 1D Rate Index. "Nifty 50 TRI", "Nifty 500 TRI" and "Nifty 1D Rate Index" are all refused as invalid neosymbols.

## Item 1: Daily OHLCV, 2015-01-01 to latest, split-adjusted

Output: `build/etf_daily_adjusted.csv` (date, symbol, adjusted OHLC, adjusted volume, factor applied, source).

The stored bars are read with HAT's latest-ingest rule: one row per symbol and day, the latest ingest run's. This was added after a review comment. The store currently holds one ingest run for these ETFs (11,403 rows, no repeated symbol-day). A fresh export with the rule rebuilt every output byte for byte, so none of the numbers below changed.

| Series | Span | Sessions | Missing vs calendar | Sources |
| --- | --- | --- | --- | --- |
| NIFTYBEES | 2015-01-01 → 2026-10-27 | 2,928 | 0 | bhavcopy INF732E01011 (to 2019-12-19), INF204KB14I2 (from 2019-12-20), Kotak for 2026-10-26/27 |
| GOLDBEES | 2015-01-01 → 2026-10-27 | 2,928 | 0 | bhavcopy INF732E01102 / INF204KB17I5, same split, Kotak for the last 2 days |
| LIQUIDBEES | 2015-01-01 → 2026-10-27 | 2,928 | 0 | bhavcopy INF732E01037, Kotak for the last 2 days |

**Cross-check against Kotak.** On the 1,236 sessions both sources have (2021-10-29 → 2026-10-23), there are 0 close mismatches above ₹0.01 for each of the three ETFs. The same holds for NIFTY 50: 0 mismatches above 0.05.

**Adjustments applied.** There are two, both from `hat_corporate_action`, where `source = nse_ca_file`:

| Symbol | Ex-date | Action | Factor on earlier bars | Evidence in the bars |
| --- | --- | --- | --- | --- |
| NIFTYBEES | 2019-12-19 | Unit split, face value 10 → 1 | ×0.1 on prices, ÷0.1 on volume | Close 1,292.54 (12-18) → 130.20 (12-19), ratio 0.1007. Adjusted 12-18 close is 129.254. |
| GOLDBEES | 2019-12-19 | Unit split, face value 100 → 1 | ×0.01 on prices, ÷0.01 on volume | Close 3,359.60 → 33.55, ratio 0.0100. Adjusted 12-18 close is 33.596. |

**Search for other splits.** I scanned every close-to-close move larger than 25% from 2015 on. The raw series have only the two moves above. The adjusted series have none. LIQUIDBEES has had no split or consolidation; its close stays between ₹999.51 and ₹1,000.88.

**ISIN change.** The ISIN changed on 2019-12-20 for NIFTYBEES and GOLDBEES, the day after the split. Prices are continuous across it (NIFTYBEES 130.20 → 130.34), so no adjustment is needed.

**Quirks, not adjusted:**
- NIFTYBEES 2019-12-20, the first bar under the new ISIN: open = high = 134.95 against a close of 130.34.
- GOLDBEES 2019-12-19, the split day: low 30.10, high 36.30.

The overlay prices sleeve trades at the open, so the NIFTYBEES open on 2019-12-20 is an outlier for Phase 1 to treat.

**Pending, NSE only.** I could not cross-check the corporate-action list against NSE's own corporate-action listing during the download. Exact source: `https://www.nseindia.com/api/corporates-corporateActions?index=equities&symbol=<SYMBOL>&from_date=01-01-2015&to_date=27-10-2026`, for NIFTYBEES, GOLDBEES and LIQUIDBEES. The jump scan above found nothing unexplained, so this is a confirmation only.

## Item 2: LIQUIDBEES total return

Output: `build/liquidbees_tr.csv` (date, close, dividend going ex that session, tr_index from 100 on 2015-01-01, basis).

**How it is built:**
- **Dividend basis.** Each session's growth is (close + dividends dated since the previous session) / previous close, which reinvests the dividend. Dividends declared on a holiday or weekend go ex at the next session.
- **Proxy basis.** NIFTY 1D Rate Index, session to session, less an expense ratio of 0.69% a year, accrued by calendar day.
- The two bases are chained, and each session is tagged with the basis it used.

**AMC dividend record:**
- 2,085 rows covering 1,981 dates, 2019-06-09 → 2026-10-27, all in the "DAILY IDCW PLAN".
- Ranges before 2019 return "No data found".
- Before December 2019 there are only two dates (2019-06-09 and 2019-11-27/29).
- From 2019-06-09 to 2020-03-31, 104 dates have two different amounts, about 8% apart. This is probably the dividend distribution tax regime that ended on 2020-04-01, but it is not verified.
- The dividend basis is therefore used from 2020-04-01 only (`DIVIDEND_FROM`).
- From 2020-04-01 the longest gap between dividend dates is 4 days.
- A handful of sessions a year have no dividend, all of them special sessions (Saturday sessions and Muhurat trading).

**Which basis covers which dates:**

| Basis | Date range | Sessions |
| --- | --- | --- |
| **Proxy** (NIFTY 1D Rate Index − 0.69%) | **2015-01-02 → 2020-03-31** | 1,273 |
| Dividend (AMC record) | 2020-04-01 → 2026-10-27 | 1,630 |
| Carried flat (no rate print that session; the next session's proxy growth spans both days, so nothing is lost) | 24 single sessions, 2015-02-19 … 2018-11-21. They are the session gaps listed under the 1D Rate Index in Item 5, and `coverage.json` (`flat_days`) lists them. | 24 |

`coverage.json` lists the proxy range as 25 runs, split only by those flat days. In practice the proxy covers the whole stretch from 2015-01-02 to 2020-03-31.

Resulting CAGR from 2015-01-01 to 2026-10-27: 4.66%.

**Finding: the proxy runs above the AMC record.** On the sessions where both bases exist, the proxy's return beats the dividend-based return by the margin below:

| Year | Dividend-based | Proxy (rate − 0.69%) | Gap |
| --- | --- | --- | --- |
| 2020 (from Apr) | 1.62% | 1.76% | 0.14 pp |
| 2021 | 2.37% | 2.56% | 0.19 pp |
| 2022 | 3.90% | 4.04% | 0.14 pp |
| 2023 | 5.45% | 6.00% | 0.55 pp |
| 2024 | 4.58% | 6.04% | 1.47 pp |
| 2025 | 4.44% | 5.08% | 0.64 pp |
| 2026 (to Oct) | 3.65% | 3.68% | 0.03 pp |

For example, 2024 dividends add up to ₹44.75 a unit on a ₹1,000 price, while the rate index rose 6.73%. A third-party profile quotes a 1-year return of about 4.5% (2026), which agrees with the AMC record rather than the proxy.

So the plan's proxy probably overstates LIQUIDBEES' total return by about 0.1 to 1.5 pp a year. The proxy alone covers the S1 in-sample years 2016-2019 and Q1 2020, which flatters V1 and the RISK-OFF leg of V3 and V4.

Per the ground rules nothing was tuned: the proxy is exactly as the plan defines it. Phase 1 must decide whether to keep it, or to calibrate it on the 2020-2026 overlap, which would be a plan change.

**Expense ratio.** The 0.69% comes from a third-party fund profile ("TER 0.69% as of 31-03-2025"), applied as one rate across the whole window. The AMC's historical TER disclosures were not fetched. The rate is a build parameter: `--expense-ratio`.

**Pending.** LIQUIDBEES dividends for 2015-01 → 2020-03 would replace the proxy, but no source reachable now has them:
- NSE corporate actions: `https://www.nseindia.com/api/corporates-corporateActions?index=equities&symbol=LIQUIDBEES&from_date=01-01-2015&to_date=31-03-2020` (NSE only, after the S2 download).
- BSE corporate actions for scrip 590096 (`api.bseindia.com/BseIndiaAPI/api/CorporateAction/w?scripcode=590096`) answer "Access Denied" from this machine.
- AMFI's `/api/scheme-dividend` answers empty for this scheme.

## Item 3: Index series

Output: `build/index_daily.csv`.

| Series | Span | Sessions | Missing | Source |
| --- | --- | --- | --- | --- |
| NIFTY 50 close | 2015-01-01 → 2026-10-27 | 2,928 | 0 | `index_daily` in HAT (from 2012-02-21), plus Kotak "Nifty 50" for 2026-10-26/27. 0 mismatches on the 1,236-day overlap. |
| NIFTY 50 TRI | 2015-01-01 → 2026-10-27 | 2,928 | 0 | niftyindices `getTotalReturnIndexString` |
| NIFTY 500 TRI | 2015-01-01 → 2026-10-27 | 2,928 | 0 | niftyindices. It matches HAT's stored NIFTY 500 TRI on every shared day (0 mismatches above 0.01). |
| NIFTY 1D Rate Index | 2015-01-01 → 2026-10-27 | 2,904 | 24 | See below |

Details for the NIFTY 1D Rate Index:
- **Primary source:** niftyindices `getHistoricaldatatabletoString`, which gives the close only.
- **Hole in niftyindices:** it has none of **2020-01-28 → 2020-08-12**, plus 2016-08-17, 2020-09-28/29, 2022-02-24 → 03-03, 2022-10-03 and 2022-12-28.
- **Fill:** 145 sessions were filled from HAT's stored `ind_close_all_*.csv` day files.
- **Overlap check:** where both sources have a session, they agree on all but one row. The archive also holds a stray second row dated 2023-10-04 with value 2119.00; the niftyindices value is kept.
- **Stale archive rows:** two archive rows on non-session days (2023-06-04 and 2023-11-04, about 3.5% below the series) are stale values. They are ignored because only sessions are used.
- **Result:** no session-to-session move above 0.2%.
- **Remaining gaps:** the 24 missing sessions are special or settlement-holiday sessions with no print in either source. They are listed in `coverage.json`.

## Item 4: 5-minute bars, from 2022 (Kotak)

| Series | Span | Sessions with bars | Bars | Sessions missing vs calendar | Short sessions (<75 bars) |
| --- | --- | --- | --- | --- | --- |
| NIFTYBEES | 2021-10-29 → 2026-10-27 | 1,187 | 92,051 | 7 | 21 |
| LIQUIDBEES | 2021-10-29 → 2026-10-27 | 1,186 | 91,958 | 8 | 25 |
| GOLDBEES (extra) | 2021-10-29 → 2026-10-27 | 1,186 | 91,984 | 8 | 17 |

**Missing sessions:**
- All three ETFs lack 2022-06-16, 2022-10-24 (Muhurat), 2023-11-12 (Muhurat), 2024-01-20 (Saturday special), 2024-11-01 (Muhurat), 2025-02-01 (Budget Saturday) and 2026-02-01 (Budget Sunday).
- LIQUIDBEES and GOLDBEES also lack 2024-07-08.

**Short sessions.** Nearly all are 71-74 bars, meaning one to four bars missing. The exceptions:
- 2022-05-04 has 57 bars in all three.
- 2024-03-02 and 2024-05-18 are the Saturday disaster-recovery sessions, with about 23 bars.
- 2025-10-21 has 14-16 bars (Muhurat).

When a sleeve sale falls on a session with no 5-minute bars, it would use the daily-open fallback and be flagged `sleeve_price_estimated`. This affects Phase 1 for S2, whose 5-minute window starts in 2022.

## Item 5: Coverage, gaps and proxies, per series

| Series | Covered | Gaps | Proxy or fill |
| --- | --- | --- | --- |
| NIFTYBEES daily | 2015-01-01 → 2026-10-27 | none | none; 1 split adjusted |
| GOLDBEES daily | 2015-01-01 → 2026-10-27 | none | none; 1 split adjusted |
| LIQUIDBEES daily | 2015-01-01 → 2026-10-27 | none | none |
| LIQUIDBEES total return | 2015-01-01 → 2026-10-27 | 24 sessions carried flat (no rate print) | **proxy 2015-01-02 → 2020-03-31**; dividends from 2020-04-01 |
| NIFTY 50 close | 2015-01-01 → 2026-10-27 | none | Kotak for the last 2 days |
| NIFTY 50 TRI | 2015-01-01 → 2026-10-27 | none | none |
| NIFTY 500 TRI | 2015-01-01 → 2026-10-27 | none | none |
| NIFTY 1D Rate Index | 2015-01-01 → 2026-10-27 | 24 sessions | 145 sessions from HAT's index archive (mainly 2020-01-28 → 2020-08-12) |
| NIFTYBEES 5-min | 2021-10-29 → 2026-10-27 | 7 sessions | none |
| LIQUIDBEES 5-min | 2021-10-29 → 2026-10-27 | 8 sessions | none |
| GOLDBEES 5-min | 2021-10-29 → 2026-10-27 | 8 sessions | none |

**Pending, needs NSE after the S2 download:**
1. LIQUIDBEES dividends for 2015-01 → 2020-03 (the URL is in Item 2). If NSE has them, the proxy range shrinks to nothing.
2. Confirmation of the ETF corporate actions (the URL is in Item 1).

## Open review points from #303, for Phase 1 (noted, not acted on)

1. **The overlay hold-out is not independent of S2's in-sample.** The overlay's 2022 hold-out for S1 and the combined runs overlaps S2's 2022-2024 in-sample window.
2. **Backtest sizing.** It is per sleeve allocation, not total equity, while plan §1.3 sizes strategy risk on total equity including the sleeve.
3. **Slippage.** One slippage rate applies to every instrument, while §1.5 sets 0.05% for NIFTYBEES/GOLDBEES and 0.01% for LIQUIDBEES.

Phase 1 must resolve all three.

## Deviations

- **GOLDBEES 5-minute bars** were fetched as well. Item 4 names only NIFTYBEES and LIQUIDBEES, but V4 sells GOLDBEES to fund entries. It cost 61 calls.
- **The 5-minute span starts at 2021-10-29**, the start of the broker's window, rather than 2022-01-01.
- **The dividend basis starts on 2020-04-01, not 2019-06-09.** The earlier records are sparse and carry dual amounts.
- **The 1D Rate Index is filled** from HAT's stored NSE index day files. These were downloaded earlier; nothing was fetched from NSE now.
- **The expense ratio is one rate**, and it comes from a third-party source; see Item 2.
