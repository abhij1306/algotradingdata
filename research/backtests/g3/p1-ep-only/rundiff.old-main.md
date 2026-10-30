before: 01a18646-d715-76d5-a630-2e48bb9c61e8 engine 160f4161 data a401e94d0baa 2022-01-01..2024-12-31 status complete
after:  01a18c00-93e1-76fa-8e07-c07ff47eefc2 engine 8f4267d2 data e7a68fc909ea 2022-01-01..2024-12-31 status complete

| metric | before | after | change |
|---|---|---|---|
| CAGR % | -0.3022 | -0.2855 | 0.0167 |
| MAR | -0.3343 | -0.3342 | 0.0001 |
| max DD % | 0.9041 | 0.8542 | -0.0499 |
| longest DD sessions | 145 | 145 | 0 |
| trades | 2 | 2 | 0 |
| win % | 0 | 0 | 0 |
| avg R | -1.133 | -1.142 | -0.0088 |
| invested % | 0 | 0 | 0 |
| NIFTY 500 TRI CAGR % | 15.42 | 15.42 | 0 |
| fees | 577.1 | 577 | -0.04 |
| final equity | 990,959 | 991,458 | 498.4 |
| CAGR over TRI, pts | -15.73 | -15.71 | 0.0167 |

trades: same 0, changed 2 (moved entry 0), only before 0, only after 0; of the changed, sizing only (qty, fees, P&L) 0
net P&L change: only_before 0, only_after 0, sizing_only 0, entry_or_exit 498.4, total 498.4
changed fields: entry_price 2, fees 2, net_pnl 2
first divergence: 2024-06-03

config paths that differ: 3
- `asked.args.1`: /data/workspace/backtests/portfolios/p1-ep-only.yaml -> /data/workspace/g3-inputs/backtests/portfolios/p1-ep-only.yaml
- `fills.cost_model`: cnc-delivery-1 -> cnc-delivery-2
- `knobs.cost_model`: "cnc-delivery-1" -> "cnc-delivery-2"
