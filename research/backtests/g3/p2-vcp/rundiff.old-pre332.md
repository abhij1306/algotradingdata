before: 01a1864d-1b49-7316-aba6-d2c2d19fee21 engine 160f4161 data c4bbe2d97cda 2022-01-01..2024-12-31 status complete
after:  01a18c2f-45bf-7139-adda-ab7173463f9c engine 8f4267d2 data 23e04fe1102a 2022-01-01..2024-12-31 status complete

| metric | before | after | change |
|---|---|---|---|
| CAGR % | 6.122 | 6.076 | -0.0455 |
| MAR | 0.2589 | 0.2565 | -0.0024 |
| max DD % | 23.65 | 23.69 | 0.0465 |
| longest DD sessions | 348 | 348 | 0 |
| trades | 154 | 154 | 0 |
| win % | 25.97 | 25.97 | 0 |
| avg R | 0.2423 | 0.2415 | -0.0008 |
| invested % | 53.31 | 53.38 | 0.0725 |
| NIFTY 500 TRI CAGR % | 15.42 | 15.42 | 0 |
| fees | 47,277 | 47,287 | 9.93 |
| final equity | 1,195,164 | 1,193,627 | -1,537 |
| CAGR over TRI, pts | -9.302 | -9.348 | -0.0455 |

trades: same 13, changed 141 (moved entry 0), only before 0, only after 0; of the changed, sizing only (qty, fees, P&L) 140
net P&L change: only_before 0, only_after 0, sizing_only -533.7, entry_or_exit -1,003, total -1,537
changed fields: fees 141, net_pnl 141, qty 64, exit_date 1, exit_price 1, exit_reason 1
first divergence: 2022-01-10

config paths that differ: 3
- `asked.args.1`: /data/workspace/backtests/portfolios/p2-vcp.yaml -> /data/workspace/g3-inputs/backtests/portfolios/p2-vcp.yaml
- `fills.cost_model`: cnc-delivery-1 -> cnc-delivery-2
- `knobs.cost_model`: "cnc-delivery-1" -> "cnc-delivery-2"
