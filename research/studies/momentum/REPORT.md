# Cross-sectional momentum rotation on NIFTY 500 (research, 2016-2024)

Pandas simulation, not an engine backtest. In-sample 2016-01-01..2024-12-31; nothing from 2025 on was read. Scripts and CSVs are in this folder. Reproduce: `build_tr_panel.py` (PYTHONPATH=backend, venv, from backend/), then `momentum.py`, then `analyze.py '["riskadj",20,"monthly",true,false,true]'`.

## Verdict

Momentum rotation works in-sample and is a hard baseline to beat.
- 93 of 96 grid cells beat NIFTY 500 TRI (15.6% CAGR, −38.1% max DD). Grid median: 22.3% CAGR, −41.7% DD, MAR 0.54.
- The edge depends on the period: only 20% of cells beat the index in all three folds. 2016-18 is weak; 2019-21 carries much of the total.

## Pick: riskadj, top 20, monthly, buffer top 40, equal-weight reset, no market filter

Chosen for worst-fold excess and the median of its neighbouring cells, not for the best CAGR (the best cell was 30.6%, but its worst fold lost to the index by 2.1 pp).

| | Pre-tax | After tax (est.) | NIFTY 500 TRI | NIFTY 50 TRI |
|---|---|---|---|---|
| CAGR | 27.9% | 24.1% | 15.6% | 14.3% |
| Max DD | −35.8% | −35.8% | −38.1% | −38.3% |
| MAR | 0.78 | 0.67 | 0.41 | 0.37 |
| Sharpe | 1.02 | 0.88 | 0.71 | 0.63 |
| Folds 2016-18 / 19-21 / 22-24 | 17.5 / 39.7 / 27.5% | 15.2 / 37.8 / 20.5% | 12.3 / 19.1 / 15.4% | 12.5 / 18.3 / 12.2% |

Benchmarks are pre-tax.

| By year % | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| Pick | −5.2 | 78.7 | −4.2 | 15.5 | 31.4 | 79.8 | 9.2 | 67.0 | 13.6 |
| NIFTY 500 TRI | 5.1 | 37.7 | −2.1 | 9.0 | 17.9 | 31.6 | 4.2 | 26.9 | 16.2 |

Sensitivity:

| Variant | CAGR |
|---|---|
| 2x costs | 26.3% |
| One extra session of execution delay | 27.2% |
| SMA200 market filter | 22.2% (DD −36.7%, worst fold 12.8%) |

The pick lags the index in 2016, 2018 and 2024.

## Rules

- **Universe:** PIT NIFTY 500 members, EQ/BE only. Filters: ADV20 traded value ≥ ₹10 cr, raw close ≥ ₹50, at least 240 bars of history in the last 252.
- **Score:** 0.5·z(r6/σ) + 0.5·z(r12/σ), where r6 and r12 are 126- and 252-session total-return-adjusted returns and σ is the annualised 252-day volatility of daily log returns. The z-scores are taken across the eligible names that day.
- **Schedule:** decide on the close of the last session of each month, then trade at the next open.
- **Selection:** keep a holding while it ranks in the top 40 and is still eligible; fill up to 20 names from the top-ranked names not held.
- **Sizing:** equal weight, equity/20; changes under 2% are skipped. No stops. Idle cash goes to LIQUIDBEES.
- **Turnover:** about 3x one-way a year, roughly 1.3% a year of cost drag at 0.22% per side.

## Method notes

- **Prices:** HAT's adjusted `bars_daily`, read with DataStore.connect(stored_adjustment), checked on 6 splits and bonuses. NSE's raw prev_close is the previous raw close on ex-dates, so it cannot be used for returns.
- **Universe:** delisted names are included, 2,952 chains.
- **Costs:** 0.12% statutory plus 0.10% slippage per side.
- **Tax:** FIFO lots, STCG 20%, LTCG 12.5% above ₹1.25L, losses set off; 2024 rates applied to every year.
- **Variants:** 142 simulated in total, every one counted: a 96-cell grid, 24 cells dropped over a hi52 tie bug, 12 reweight checks and 10 sensitivities.

What the grid shows:
- Risk-adjusted ranking is the best family.
- N = 20-30 beats N = 10, with about 9 pp less DD.
- The top-2N buffer halves turnover and helps every metric.
- Fortnightly rebalancing adds turnover and nothing else.
- The SMA200 filter cuts DD by about 7 pp but costs about 4 pp of CAGR, with no gain in MAR.

## Caveats

- In-sample only.
- Membership history has days with 501 members.
- Adjustment factors are today's stored ones.
- Suspended holdings are sold at the next open within 20 sessions, which is slightly optimistic.
- Slippage is only plausible at a book of about ₹10L.

## Engine gap

None of the following exists yet:
- a calendar rebalance scheduler
- a cross-sectional rank/z-score criterion
- target-weight sizing with order diffs
- a rank-based exit with no stop, and an opt-out from the stop-based risk caps and slots
- market-on-open rebalance fills
- a capital sleeve beside S1/S2

Reused as is: the PIT universe, bars_daily, corporate actions, costs, tax.py, and the run folder.
