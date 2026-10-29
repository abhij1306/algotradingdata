# Accuracy plan: trustworthy data and bug-free backtests (2026-10-29)

Owner goal: before any strategy is judged or traded, be sure that (a) the data is complete and
accurate, and (b) the backtest code runs without bugs. Profitability comes later. Strategy research
is paused until the gates below are green; the research done so far stays in the record.

## Principles

- Every check compares against an independent reference (the source file, a second source, a
  hand calculation or a separate implementation), never against our own output.
- Every check is a command that can be rerun, prints pass/fail with counts, and writes a report.
  Nothing is "verified" by inspection only.
- Backtests carry the verification status of their window and refuse (or mark the run
  unverified) when a blocking check fails.
- Tests stay pure-function tests. Verification runs on real data, outside the test suite.
- Every PR: CodeAnt plus an independent high-effort review that sees the diff, not our conclusions.
- Nothing is deleted before it is snapshotted.

## W0. Safety net and version control (repo `abhij1306/algotradingdata`, private)

Today there is no backup on this machine (the backup timer in the runbook is not installed), and the
research record is in unversioned folders.

1. **Snapshot first:** pg_dump of hat_live and hat_state, and the irreplaceable stores (`raw/` NSE
   source files, `bars_5m/`, the Kotak raw files, `ca-data/`), uploaded as GitHub Release assets
   (parts under 2 GB) with a SHA-256 manifest. One restore drill into a scratch DB proves the set.
2. **Repo layout:**
   - `research/`: research log and hold-out log, strategy notes, briefs, portfolio and sweep
     files, study scripts and reports (no caches).
   - `reference/`: small source-of-truth tables exported from the DB as CSV: index membership
     history, corporate actions and corrections, board meetings, results filings, holidays,
     symbol/ISIN lineage.
   - `manifests/`: one file per store (bars_daily, bars_5m, features, index, breadth, etf),
     listing partition, rows, date range and SHA-256. They are regenerated after each daily
     update and committed, so any rewrite of past data shows up as a git diff.
   - `audits/`: dated coverage and verification reports (W1).
3. **Nightly:** the daily update ends by refreshing the manifests and reference exports and pushing
   them. A weekly snapshot release keeps the DB and stores restorable.
4. **Clean the data root:** move or remove `tmp/`, `chrome/`, dated duplicates and old worktrees
   (after the snapshot). Add a one-page data-root layout doc. Target at least 5 GB free on /data.
5. **Secret guard:** a pre-push check that refuses `.env`, tokens and keys.

## W1. Data accuracy (`python -m app.hat.data.verify`)

| Check | Reference | Passes when |
|---|---|---|
| D1 Daily bars, raw | NSE bhavcopy files in `raw/` | Every stored row equals its source row (OHLCV, series), every session 2011+ |
| D2 Adjustments | NSE corporate action files, and a second adjusted-price source on a sample | Every split, bonus, demerger, rights and dividend factor matches the ratio. Every adjusted one-day move over 20% is explained (CA, results, news) or listed as a defect. Sample of 100 stocks: total return within tolerance of the second source |
| D3 Index membership | NSE index change notices and archived constituent lists | 500 members each day (or a documented exception); every change traces to a notice; review-date lists match |
| D4 5m bars | Daily bars, Kotak raw files | The 17.6k basis_mismatch days are classified (bad source bar, our bug, real auction effect) and the rule is fixed or documented. Coverage by year and the gap-day bias are reported |
| D5 Results filings | NSE announcement timestamps | `public_at` matches the exchange timestamp; no figure is usable before it was public; pre-2020 gap and non-PIT screener figures flagged |
| D6 Calendar, suspensions, lineage | NSE holiday lists, symbol change and ISIN files | No missing or extra sessions; no broken instrument chains; suspensions reflected |
| D7 ETF and index series | NSE published index values | TRI and ETF closes match on every date |

Output: JSON and Markdown report per run, committed to `algotradingdata/audits/`. The backtest run
audit records the verification status of its window. Defects found are fixed in separate PRs.

## W2. Backtest correctness

| Check | What it proves |
|---|---|
| B1 Ledger reconciliation on every run | Each day: equity = cash + positions at the close; cash moves only by fills, costs, dividends, tax and overlay flows; trade P&L recomputes from fills. Mismatch fails the run |
| B2 No lookahead | An as-of guard in the backtest data layer raises on any read after the decision instant. A truncation check on real data: a run ending at T and a run ending at T+N make identical decisions up to T (S1, S2, rotation) |
| B3 Costs | STT, stamp, exchange, SEBI, GST and DP charges match the official schedules per period, with hand-worked examples |
| B4 Fills | Open/auction, gap, circuit-limit, suspension and halt rules audited; no fill on a locked limit day; no fill at a price outside the bar |
| B5 Config hygiene | Every criterion and exit can be switched off explicitly with no side effects (the EP neglect gate blocks everything when off today); unknown or no-op keys refused; exit labels correct (SMA20 is logged as `sma50_close` today) |
| B6 Independent parity | A separate simple implementation per strategy reproduces the engine's trades on a sample period: rotation (done, #312), S1 VCP, S2 EP (engine sees 182 gaps of 6%+ in 2022-24 vs the study's 347; explain every difference) |

## W3. Live readiness (after W1 and W2 are green; not started now)

Shadow-day replay (live signals equal backtest signals for the same days), rotation order
execution, monitoring and reporting.

## Confidence gates

| Gate | Green when |
|---|---|
| G0 Recoverable | Snapshot release exists, restore drill passed, nightly manifests pushing |
| G1 Data accurate | D1-D7 pass, or every failure is a listed, explained exception the backtest knows about |
| G2 Engine correct | B1-B6 pass on S1, S2 and rotation over 2016-2024 |
| G3 Re-run | The p1-p6 and rotation runs are rerun on the verified data and code, and differences from today's numbers are explained |

Strategy research resumes only after G3.

## Builders

| Builder | Scope | Starts |
|---|---|---|
| `data-repo` | W0 | Now |
| `data-verify` | W1 (D1-D7 command and report; fixes as follow-up PRs) | Now |
| `bt-verify` | W2 B1, B2, B3, B4, B5 | Now |
| `parity` | W2 B6 (S1 and EP) | After bt-verify's B2 lands |
