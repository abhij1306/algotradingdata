before: 01a1870a-2740-7175-9991-94ab7aafa34d engine 430c5a5f data 1d0ba47c0e0f 2016-01-01..2024-12-31 status complete
after:  01a18c2f-9fbb-727b-8233-ba3a11759af1 engine 8f4267d2 data d5c43c659f10 2016-01-01..2024-12-31 status complete

| metric | before | after | change |
|---|---|---|---|
| CAGR % | 23.36 | 23.32 | -0.0349 |
| MAR | 0.66 | 0.6582 | -0.0018 |
| max DD % | 35.39 | 35.43 | 0.042 |
| longest DD sessions | 501 | 501 | 0 |
| trades | 487 | 486 | -1 |
| win % | 50.72 | 50.41 | -0.3072 |
| avg R | 0.0945 | 0.0944 | -0.0001 |
| invested % | 99.46 | 99.46 | 0.0009 |
| NIFTY 500 TRI CAGR % | 15.58 | 15.58 | 0 |
| fees | 194,246 | 198,091 | 3,845 |
| final equity | 6,617,429 | 6,600,585 | -16,844 |
| CAGR over TRI, pts | 7.777 | 7.742 | -0.0349 |

trades: same 11, changed 1218 (moved entry 0), only before 14, only after 17; of the changed, sizing only (qty, fees, P&L) 1209
net P&L change: only_before -27,113, only_after 27,962, sizing_only -19,638, entry_or_exit -511, total -19,300
changed fields: net_pnl 1218, fees 1196, qty 573, exit_price 9, entry_price 8, exit_date 1
first divergence: 2016-01-01

config paths that differ: 3
- `asked.args.1`: /data/workspace/backtests/portfolios/p5-rotation.yaml -> /data/workspace/g3-inputs/backtests/portfolios/p5-rotation.yaml
- `fills.cost_model`: cnc-delivery-1 -> cnc-delivery-2
- `knobs.cost_model`: "cnc-delivery-1" -> "cnc-delivery-2"
