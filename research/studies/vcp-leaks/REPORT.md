# S1 VCP breakout: where the leaks are (research, 2016-2024)

Runs 01a17e77 (2016-21) and 01a1864d (2022-24); nothing after 2024-12-31 read. No engine backtests. Prices come from the engine's split/bonus-adjusted bars, because raw prev_close is not adjusted. The exit replay reproduces the engine's exit dates for 90-92% of trades; total R 160.7 vs 160.0 (2016-21) and 44.4 vs 40.5 (2022-24). Scripts and outputs are in this folder.

## Ranked leaks

| # | Leak | Size | Fix to test | Confidence |
|---|---|---|---|---|
| 1 | Exits cut winners: winners keep 51-52% of their peak gain (MFE), giving back about 3R from the peak. The swing-low-20 exit and early SMA50 exits do this. | Taken trades with "SMA50 only after a +2R peak, no swing-low": 0.67 → 0.94R per trade (2016-21), 0.25 → 0.56R (2022-24). Wider trails: 1.1-1.6R. | (a) Drop swing-low-20; SMA50 active after +2R. (b) Chandelier 5×ATR21. (c) SMA100. | Medium-high on direction; size unproven, because the replay ignores capacity. |
| 2 | Exposure follows the regime gate: average invested 53%; 65-74% with the regime on, 9-21% with it off (off 29-32% of sessions). NIFTY 500's forward 60-session return is higher after regime-off days (5.2% vs 3.6%). | About 47% of capital idle on average. | Gate loosened to NIFTY 500 > SMA200, or off. | Medium |
| 3 | Churn and tight stops: friction 0.10R per trade (fees 0.038R + slippage 0.065R). Trades held 5 sessions or less are 25-32% of trades and lose 39-46R net. | Friction takes 40% of P&L before costs (2022-24) and 14% (2016-21). | Minimum stop of about 4% or 1.5×ADR; grace on the SMA exit. | Medium |
| 4 | Capacity: refused signals have the same forward R as taken ones (r60 0.49 vs 0.58; 0.54 vs 0.53). | Spread risk only. | Fixes 1 and 2. | High |
| 5 | Ranking: RS rank barely predicts (Spearman 0.05); setup score not at all. | Bottom RS quartile: 0.21R vs 0.4-0.9R for the others. | RS floor around the 50th percentile. | Low-medium |
| 6 | Shakeouts: 31-41% of losers reach +2R within 60 sessions. Wider stops lower R. | Re-entry adds about +0.3R per re-entry, but only about +5R once the top 3 are removed. | Re-entry rule. | Low |
| 7 | Gap-up entries filled at the pivot instead of the open. | 8 trades, 0.3-0.6% each. | Fill at the open when the open is above the pivot. | High; tiny size |

## Key tables

MFE capture of winners:

| Period | Winners | Average peak gain (MFE) | Realised | Captured | Give-back |
|---|---|---|---|---|---|
| 2016-21 | 76 | 6.56R | 3.40R | 52% | 3.16R |
| 2022-24 | 40 | 6.03R | 3.10R | 51% | 2.93R |

Exit replay on the same entries (net R per trade; average hold of taken trades in sessions):

| Rule | Taken 16-21 | Taken 22-24 | Refused 16-21 | Refused 22-24 | Hold |
|---|---|---|---|---|---|
| Current: SMA50 + swing-low 20 | 0.67 | 0.25 | 0.19 | 0.07 | 27 / 21 |
| SMA50 only | 0.77 | 0.40 | 0.22 | 0.12 | 28 / 22 |
| SMA50 after +2R | 0.94 | 0.56 | 0.42 | 0.38 | 45 / 34 |
| SMA20 | 0.26 | −0.02 | 0.04 | −0.09 | 13 / 10 |
| SMA100 | 1.27 | 1.03 | 0.36 | 0.97 | 55 / 42 |
| Chandelier 5×ATR21 | 1.27 | 0.69 | 0.45 | 1.08 | 53 / 42 |
| 15% trail from peak close | 1.44 | 1.15 | 0.51 | 1.41 | 66 / 50 |
| 20% trail from peak close | 1.56 | 1.57 | 0.65 | 1.61 | 84 / 72 |

- "SMA50 after +2R" beats the current exit in 8 of 9 entry years.
- Wider trails win in 6 of 9 years. Their gain sits mostly in 2020 and 2023, and they are worse in 2018.
- 2024 is negative under every rule: the failure there is on the entry side.

Other findings:
- **Stops:** median 6.4% (about 2×ADR).
- **Breakouts:** 60-67% of all breakouts hit the stop within 60 sessions, so the edge is in the tail.
- **Exposure is bimodal:** 19-26% of sessions are under 10% invested.

No serious bug was found. Note that run CSV prices carry adjustment factors from after 2024, which confuses any comparison of raw prices.
