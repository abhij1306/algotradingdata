before: 01a18c2f-9fbb-727b-8233-ba3a11759af1 engine 8f4267d2 data d5c43c659f10 2016-01-01..2024-12-31 status complete
after:  01a18c4c-e180-73db-845b-23f21d48ed63 engine d6d99b6d data d5c43c659f10 2016-01-01..2024-12-31 status complete

| metric | before | after | change |
|---|---|---|---|
| CAGR % | 23.32 | 23.19 | -0.135 |
| MAR | 0.6582 | 0.6497 | -0.0085 |
| max DD % | 35.43 | 35.69 | 0.2578 |
| longest DD sessions | 501 | 501 | 0 |
| trades | 486 | 486 | 0 |
| win % | 50.41 | 50 | -0.4115 |
| avg R | 0.0944 | 0.0941 | -0.0003 |
| invested % | 99.46 | 99.48 | 0.0243 |
| NIFTY 500 TRI CAGR % | 15.58 | 15.58 | 0 |
| fees | 198,091 | 196,845 | -1,247 |
| final equity | 6,600,585 | 6,535,825 | -64,760 |
| CAGR over TRI, pts | 7.742 | 7.607 | -0.135 |

trades: same 1, changed 1228 (moved entry 0), only before 17, only after 15; of the changed, sizing only (qty, fees, P&L) 9
net P&L change: only_before -21,625, only_after 8,510, sizing_only -864.7, entry_or_exit -66,304, total -80,284
changed fields: net_pnl 1228, entry_price 1171, exit_price 1152, fees 1061, qty 750, exit_date 3
first divergence: 2016-01-01

config paths that differ: 1
- `known_gaps.14`: rotation_fills_at_daily_open -> rotation_fills_0920_estimated_without_5m
