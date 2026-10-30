before: 01a1864d-1b49-7316-aba6-d2c2d19fee21 engine 160f4161 data c4bbe2d97cda 2022-01-01..2024-12-31 status complete
after:  01a18bfd-8f82-720b-9b88-65c54660f2a0 engine 8f4267d2 data 23e04fe1102a 2022-01-01..2024-12-31 status complete

| metric | before | after | change |
|---|---|---|---|
| CAGR % | 6.122 | 6.155 | 0.0339 |
| MAR | 0.2589 | 0.2614 | 0.0025 |
| max DD % | 23.65 | 23.55 | -0.0972 |
| longest DD sessions | 348 | 348 | 0 |
| trades | 154 | 154 | 0 |
| win % | 25.97 | 25.97 | 0 |
| avg R | 0.2423 | 0.2411 | -0.0012 |
| invested % | 53.31 | 53.38 | 0.0732 |
| NIFTY 500 TRI CAGR % | 15.42 | 15.42 | 0 |
| fees | 47,277 | 47,298 | 20.79 |
| final equity | 1,195,164 | 1,196,312 | 1,148 |
| CAGR over TRI, pts | -9.302 | -9.269 | 0.0339 |

trades: same 12, changed 141 (moved entry 0), only before 1, only after 1; of the changed, sizing only (qty, fees, P&L) 119
net P&L change: only_before 11,219, only_after -1,305, sizing_only -404.8, entry_or_exit -8,362, total 1,148
changed fields: fees 141, net_pnl 141, qty 68, entry_price 21, exit_date 1, exit_price 1, exit_reason 1
first divergence: 2022-01-10

config paths that differ: 4
- `asked.args.1`: /data/workspace/backtests/portfolios/p2-vcp.yaml -> /data/workspace/g3-inputs/backtests/portfolios/p2-vcp.yaml
- `fills.cost_model`: cnc-delivery-1 -> cnc-delivery-2
- `knobs.cost_model`: "cnc-delivery-1" -> "cnc-delivery-2"
- `known_gaps.11`: gap_over_fills_at_open -> gap_over_fills_0920_estimate
