before: 01a18653-8ae6-768b-91b9-fe9b479d2f9e engine 160f4161 data a401e94d0baa 2022-01-01..2024-12-31 status complete
after:  01a18c06-bcbe-7718-96f4-68a842b6a652 engine 8f4267d2 data e7a68fc909ea 2022-01-01..2024-12-31 status complete

| metric | before | after | change |
|---|---|---|---|
| CAGR % | 3.419 | 4.06 | 0.6412 |
| MAR | 0.2534 | 0.3223 | 0.0689 |
| max DD % | 13.5 | 12.6 | -0.8976 |
| longest DD sessions | 348 | 348 | 0 |
| trades | 158 | 158 | 0 |
| win % | 27.22 | 28.48 | 1.266 |
| avg R | 0.2128 | 0.2505 | 0.0377 |
| invested % | 30.95 | 31 | 0.0527 |
| NIFTY 500 TRI CAGR % | 15.42 | 15.42 | 0 |
| fees | 26,433 | 26,632 | 199.1 |
| final equity | 1,106,149 | 1,126,855 | 20,706 |
| CAGR over TRI, pts | -12 | -11.36 | 0.6412 |

trades: same 2, changed 153 (moved entry 0), only before 3, only after 3; of the changed, sizing only (qty, fees, P&L) 16
net P&L change: only_before -18,702, only_after 22,471, sizing_only -125.6, entry_or_exit 17,062, total 20,706
changed fields: net_pnl 153, fees 141, entry_price 137, qty 93
first divergence: 2022-01-11

config paths that differ: 4
- `asked.args.1`: /data/workspace/backtests/portfolios/p3-vcp-ep.yaml -> /data/workspace/g3-inputs/backtests/portfolios/p3-vcp-ep.yaml
- `fills.cost_model`: cnc-delivery-1 -> cnc-delivery-2
- `knobs.cost_model`: "cnc-delivery-1" -> "cnc-delivery-2"
- `known_gaps.11`: gap_over_fills_at_open -> gap_over_fills_0920_estimate
