before: 01a18653-8ae6-768b-91b9-fe9b479d2f9e engine 160f4161 data a401e94d0baa 2022-01-01..2024-12-31 status complete
after:  01a18c3b-1029-75db-87c7-1adcf4b72f55 engine d6d99b6d data e7a68fc909ea 2022-01-01..2024-12-31 status complete

| metric | before | after | change |
|---|---|---|---|
| CAGR % | 3.419 | 4.076 | 0.657 |
| MAR | 0.2534 | 0.3246 | 0.0712 |
| max DD % | 13.5 | 12.56 | -0.9364 |
| longest DD sessions | 348 | 348 | 0 |
| trades | 158 | 158 | 0 |
| win % | 27.22 | 28.48 | 1.266 |
| avg R | 0.2128 | 0.2507 | 0.0379 |
| invested % | 30.95 | 31.02 | 0.0691 |
| NIFTY 500 TRI CAGR % | 15.42 | 15.42 | 0 |
| fees | 26,433 | 26,641 | 208.1 |
| final equity | 1,106,149 | 1,127,368 | 21,219 |
| CAGR over TRI, pts | -12 | -11.35 | 0.657 |

trades: same 2, changed 153 (moved entry 0), only before 3, only after 3; of the changed, sizing only (qty, fees, P&L) 21
net P&L change: only_before -18,702, only_after 22,471, sizing_only 298.3, entry_or_exit 17,151, total 21,219
changed fields: net_pnl 153, fees 141, entry_price 132, qty 95
first divergence: 2022-01-11

config paths that differ: 3
- `asked.args.1`: /data/workspace/backtests/portfolios/p3-vcp-ep.yaml -> /data/workspace/g3-inputs/backtests/portfolios/p3-vcp-ep.yaml
- `fills.cost_model`: cnc-delivery-1 -> cnc-delivery-2
- `knobs.cost_model`: "cnc-delivery-1" -> "cnc-delivery-2"
