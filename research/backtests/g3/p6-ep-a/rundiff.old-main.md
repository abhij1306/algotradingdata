before: 01a1870c-63e6-7719-9110-46d18b0db63a engine 430c5a5f data a401e94d0baa 2022-01-01..2024-12-31 status complete
after:  01a18c09-c414-76fe-8867-9ba3b74a021f engine 8f4267d2 data e7a68fc909ea 2022-01-01..2024-12-31 status complete

| metric | before | after | change |
|---|---|---|---|
| CAGR % | -1.316 | -1.639 | -0.3234 |
| MAR | -0.1875 | -0.1693 | 0.0182 |
| max DD % | 7.02 | 9.682 | 2.662 |
| longest DD sessions | 640 | 640 | 0 |
| trades | 14 | 16 | 2 |
| win % | 21.43 | 18.75 | -2.679 |
| avg R | -0.5283 | -0.5984 | -0.0701 |
| invested % | 1.29 | 1.471 | 0.1815 |
| NIFTY 500 TRI CAGR % | 15.42 | 15.42 | 0 |
| fees | 3,717 | 4,155 | 438.6 |
| final equity | 961,025 | 951,606 | -9,419 |
| CAGR over TRI, pts | -16.74 | -17.06 | -0.3234 |

trades: same 0, changed 14 (moved entry 0), only before 0, only after 2; of the changed, sizing only (qty, fees, P&L) 3
net P&L change: only_before 0, only_after -12,488, sizing_only 104.1, entry_or_exit 2,965, total -9,419
changed fields: fees 14, net_pnl 14, entry_price 10, qty 9, exit_reason 3
first divergence: 2022-01-24

config paths that differ: 3
- `asked.args.1`: /data/workspace/backtests/portfolios/p6-ep-a.yaml -> /data/workspace/g3-inputs/backtests/portfolios/p6-ep-a.yaml
- `fills.cost_model`: cnc-delivery-1 -> cnc-delivery-2
- `knobs.cost_model`: "cnc-delivery-1" -> "cnc-delivery-2"
