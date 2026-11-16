# wf12: old VCP sleeve beside c1, 2016-01..2021-12 (2026-11-02)

m1, main ea757eb6. Old VCP B2 = version aac4fda7 + the 2026-10-31 b2-oldvcp overrides (contractions 2-6,
depth ratio 0.9, dry-up 1.0x, exits SMA50 close / 20-day swing low, risk 0.75%, flat ladder, open risk
uncapped, slot order rs), leak-free E1 stop_order entry. One account, shared cash. Configs
`wf12-work/configs/` (first try without the overrides, 23 trades: `wf12-work/first-try/`, invalid).
v0 (c1 under the same account settings) replays wf11 f0 exactly.

| run | mix | CAGR | max DD | Sharpe | MAR | invested | trades |
|---|---|---:|---:|---:|---:|---:|---:|
| v0 | c1 | 32.7 | 35.2 | 1.55 | 0.93 | 99.1 | 344 |
| v1 | c1 0.8 + VCP 0.2 | 28.5 | 30.1 | 1.56 | 0.95 | 89.8 | 586 |
| v2 | c1 0.7 + VCP 0.3 | 26.1 | 27.6 | 1.54 | 0.94 | 85.0 | 583 |
| v3 | VCP alone | 11.2 | 35.7 | 0.84 | 0.32 | 51.5 | 231 |

Excess vs TRI (pp) 2016..2021: v0 -8.8 +40.5 -2.5 +3.1 +30.2 +70.8 · v1 -6.8 +33.6 -5.0 -0.8 +22.6 +59.1 ·
v2 -5.8 +30.0 -7.1 -2.7 +18.3 +53.1 · v3 0.0 +16.5 -24.4 -15.7 -8.1 +24.6.
In-year DD 2016 / 2018: v0 19.7 / 19.4 · v1 15.9 / 16.9 · v2 14.0 / 18.3 · v3 7.3 / 33.4.

## Reading
- The sleeve lowers drawdown about in proportion to the cash it leaves idle (v1 10%, v2 15% idle);
  Sharpe and MAR are flat (1.55 -> 1.56, 0.93 -> 0.95). That is dilution, not diversification.
- 2018, the year to fix, gets worse vs TRI (-2.5 -> -5.0 / -7.1): VCP alone loses 24 pp that year.
- VCP alone: 11% CAGR, 51% invested, PF 1.9; trend-year beta (2017, 2021), weak elsewhere.
- Verdict: **not promotable**; breaks the deploy-capital rule for no risk-adjusted gain. c1 stays core.
  Setups as a sleeve are closed unless a new entry/exit idea appears.
