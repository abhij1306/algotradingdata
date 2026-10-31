# Top 5 strategies, frozen 2026-10-31 for the 2021-2025 test

Chosen from 2016-2021 in-sample evidence only (plans/dd3-6y-report.md), before any 2022+ read. Owner go 2026-10-31: "backtest on 2021 to 2025 both included your top 5 strategies".

| # | Name | In-sample run | Config | IS invested / CAGR / max DD / Calmar |
|---|---|---|---|---|
| 1 | H3 | 01a1910e | rotation: vol_sessions=63, max_per_industry=4, scale_down breadth<30 smooth 5 keep 0.75 | 91.6 / 29.55 / 25.3 / 1.17 |
| 2 | G1 | 01a19104 | rotation: vol_sessions=63, max_per_industry=4 | 99.3 / 32.37 / 31.7 / 1.02 |
| 3 | H1 | 01a1910c | as H3 with keep 0.5 | 84.0 / 26.83 / 22.5 / 1.19 |
| 4 | F1 | 01a190e9 | rotation: vol_sessions=63 + breadth market_filter (all-cash; 23% zero-position days) | 76.0 / 29.40 / 24.5 / 1.20 |
| 5 | E2 | 01a190de | rotation: vol_sessions=63 (plain-rotation reference) | 99.3 / 27.98 / 34.2 / 0.82 |

All: G3 p5 momentum rotation base, stocks only (no ETF overlay), NIFTY500_PIT, ₹10L. Exposure note: G3 p5 rotation (with ETF overlay) was earlier run on 2016-2024, so 2022-2024 is not fully unseen for the base rotation; 2025 is fresh for all.
