before: 01a1870a-2740-7175-9991-94ab7aafa34d engine 430c5a5f data 1d0ba47c0e0f 2016-01-01..2024-12-31 status complete
after:  01a18c4c-e180-73db-845b-23f21d48ed63 engine d6d99b6d data d5c43c659f10 2016-01-01..2024-12-31 status complete

| metric | before | after | change |
|---|---|---|---|
| CAGR % | 23.36 | 23.19 | -0.1699 |
| MAR | 0.66 | 0.6497 | -0.0103 |
| max DD % | 35.39 | 35.69 | 0.2998 |
| longest DD sessions | 501 | 501 | 0 |
| trades | 487 | 486 | -1 |
| win % | 50.72 | 50 | -0.7187 |
| avg R | 0.0945 | 0.0941 | -0.0004 |
| invested % | 99.46 | 99.48 | 0.0252 |
| NIFTY 500 TRI CAGR % | 15.58 | 15.58 | 0 |
| fees | 194,246 | 196,845 | 2,599 |
| final equity | 6,617,429 | 6,535,825 | -81,603 |
| CAGR over TRI, pts | 7.777 | 7.607 | -0.1699 |

trades: same 0, changed 1216 (moved entry 0), only before 27, only after 28; of the changed, sizing only (qty, fees, P&L) 10
net P&L change: only_before -47,625, only_after 38,001, sizing_only -160.2, entry_or_exit -89,801, total -99,585
changed fields: net_pnl 1216, fees 1211, entry_price 1164, exit_price 1139, qty 813, exit_date 2
first divergence: 2016-01-01

config paths that differ: 4
- `asked.args.1`: /data/workspace/backtests/portfolios/p5-rotation.yaml -> /data/workspace/g3-inputs/backtests/portfolios/p5-rotation.yaml
- `fills.cost_model`: cnc-delivery-1 -> cnc-delivery-2
- `knobs.cost_model`: "cnc-delivery-1" -> "cnc-delivery-2"
- `known_gaps.14`: rotation_fills_at_daily_open -> rotation_fills_0920_estimated_without_5m
