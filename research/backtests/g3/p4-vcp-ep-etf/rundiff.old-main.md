before: 01a18680-3e91-71e5-ae7c-d6733c7fcea4 engine afdff73e data a401e94d0baa 2022-01-01..2024-12-31 status complete
after:  01a18c1b-d5dc-7359-9be4-79a3e40ebbb9 engine 8f4267d2 data e7a68fc909ea 2022-01-01..2024-12-31 status complete

| metric | before | after | change |
|---|---|---|---|
| CAGR % | 1.823 | 2.489 | 0.6658 |
| MAR | 0.0817 | 0.1131 | 0.0314 |
| max DD % | 22.32 | 22.01 | -0.3024 |
| longest DD sessions | 395 | 394 | -1 |
| trades | 158 | 158 | 0 |
| win % | 27.22 | 28.48 | 1.266 |
| avg R | 0.2125 | 0.2502 | 0.0377 |
| invested % | 94.3 | 94.3 | 0.0025 |
| NIFTY 500 TRI CAGR % | 15.42 | 15.42 | 0 |
| fees | 24,693 | 24,935 | 241.5 |
| final equity | 1,055,709 | 1,076,559 | 20,850 |
| CAGR over TRI, pts | -13.6 | -12.94 | 0.6658 |

trades: same 3, changed 152 (moved entry 0), only before 3, only after 3; of the changed, sizing only (qty, fees, P&L) 15
net P&L change: only_before -18,431, only_after 22,091, sizing_only 19.73, entry_or_exit 17,843, total 21,523
changed fields: net_pnl 152, fees 143, entry_price 137, qty 90
first divergence: 2022-01-11

config paths that differ: 4
- `asked.args.1`: /data/workspace/backtests/portfolios/p4-vcp-ep-etf.yaml -> /data/workspace/g3-inputs/backtests/portfolios/p4-vcp-ep-etf.yaml
- `fills.cost_model`: cnc-delivery-1 -> cnc-delivery-2
- `knobs.cost_model`: "cnc-delivery-1" -> "cnc-delivery-2"
- `known_gaps.16`: gap_over_fills_at_open -> gap_over_fills_0920_estimate
