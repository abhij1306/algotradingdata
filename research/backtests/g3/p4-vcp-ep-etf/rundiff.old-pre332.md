before: 01a18680-3e91-71e5-ae7c-d6733c7fcea4 engine afdff73e data a401e94d0baa 2022-01-01..2024-12-31 status complete
after:  01a18c4c-eee9-73bf-bc56-062f72e963ce engine d6d99b6d data e7a68fc909ea 2022-01-01..2024-12-31 status complete

| metric | before | after | change |
|---|---|---|---|
| CAGR % | 1.823 | 2.487 | 0.6644 |
| MAR | 0.0817 | 0.113 | 0.0313 |
| max DD % | 22.32 | 22.01 | -0.3023 |
| longest DD sessions | 395 | 394 | -1 |
| trades | 158 | 158 | 0 |
| win % | 27.22 | 28.48 | 1.266 |
| avg R | 0.2125 | 0.2504 | 0.0379 |
| invested % | 94.3 | 94.3 | 0.0044 |
| NIFTY 500 TRI CAGR % | 15.42 | 15.42 | 0 |
| fees | 24,693 | 24,939 | 245.7 |
| final equity | 1,055,709 | 1,076,513 | 20,804 |
| CAGR over TRI, pts | -13.6 | -12.94 | 0.6644 |

trades: same 4, changed 151 (moved entry 0), only before 3, only after 3; of the changed, sizing only (qty, fees, P&L) 19
net P&L change: only_before -18,431, only_after 22,091, sizing_only 427.5, entry_or_exit 17,381, total 21,469
changed fields: net_pnl 151, fees 142, entry_price 132, qty 92
first divergence: 2022-01-11

config paths that differ: 3
- `asked.args.1`: /data/workspace/backtests/portfolios/p4-vcp-ep-etf.yaml -> /data/workspace/g3-inputs/backtests/portfolios/p4-vcp-ep-etf.yaml
- `fills.cost_model`: cnc-delivery-1 -> cnc-delivery-2
- `knobs.cost_model`: "cnc-delivery-1" -> "cnc-delivery-2"
