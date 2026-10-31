# Exit, sizing and holding leaks, 2016-2021 in-sample (no engine runs)

2026-10-31. Counterfactual replays on recorded trades and adjusted daily bars only. No engine backtest
was run, m3 and hat_live were only read, and nothing after 2021-12-31 was read. Work files, scripts and
outputs: `/data/workspace/plans/leak-exits-work/`. Short run IDs: E2 `01a190de`, B1 `01a19039`,
H3 `01a1910e`, VCP R5 `01a1909f`, B2 `01a1903c`.

## Verdict

- **Deployment.** Every rotation variant below stays **99.6-100.2% invested at 18-20 positions × ~5%**.
  None parks cash, except the "_cash" rows, which are there for reference. The VCP exit change raises
  VCP's invested proxy from **48% to 61%**.
- **The rotation leaks through a forced sale, not through slow exits.**
  - 21% of E2's sales (69 of 322) are `rotation_not_eligible`. **58 of those 69 are names still in
    NIFTY 500 whose 20-bar mean turnover fell under ₹10 cr.**
  - These sold names then **beat their replacements by +3.8 pts over 21 sessions and +5.2 pts over
    63 sessions**. The same holds in B1 and H3.
  - Out-of-buffer sales are correct: those names **lag their replacements by 2.6 pts (21 sessions)
    and 3.9 pts (63 sessions)**.
- **Drawdowns are mostly beta.** The market leg is 60-90% of each of E2's five largest episodes
  (book beta 1.1-1.5 at the peaks outside 2020). Stops cannot fix that, and they did not:
  - All 13 intra-month stop, trailing-stop and early-failure variants lose return or have mixed signs
    by year.
  - After a holding gaps down 5% or more, its median forward return relative to the index stays positive
    (+1.8 pts at 21 sessions). A stop would sell near the low.
- **Sizing does help.** Weighting by inverse beta lowers the in-year drawdown in **23 of 24
  config-years**, with CAGR +1.3 on E2, and it stays fully invested.
- **VCP R5:** the SMA50 close exit is armed from day 1. It throws away entries that sit 1-3% above
  SMA50 (26 exits within 3 sessions, −0.62 R on average). Arming it only after +1 R lifts expectancy
  from **0.75 to 0.91 R**. Every tighter or profit-taking exit makes VCP worse.
- **Engine bugs: none found in the exit logic.** There are three design or data points to check (§4).

## Method and validation

- **Prices.** I used the engine's own adjusted store views (`DataStore.connect(stored_adjustment)`:
  total-return `bars_daily`, split-adjusted `bars_daily_cap`), with lineage mapped to chain IDs.
- **Book replay.** Each holding's value is rebuilt from `rebalances.csv`. It tracks the engine's
  `position_value` with a median error of 0.27%, which is dividends. Replaying E2's actual book gives
  CAGR 28.70 vs the engine's 27.95, with max DD 34.64 vs 34.19 and the same sign in every year.
- **Rotation simulator.** This is a mini simulator (`scripts/sim.py`), not the engine.
  - It replicates the riskadj ranking: NIFTY 500 PIT, last 20 bars' mean turnover ≥ ₹10 cr, raw close
    ≥ 50, min_bars 240, the z-score mean of 126- and 252-session return over volatility, buffer 40,
    top 20, monthly decisions, fills at the next open, 0.30% cost per side.
  - Its ranks equal the engine's on 91% of checked rows, and are within 1 on the rest. It shares 326 of
    the engine's 342 buys.
  - The baseline "base" (E2 config) gives CAGR 29.32 / max DD 34.63 vs the engine's 27.95 / 34.19.
    The vol-252 baseline gives 27.52 vs B1's 26.83.
  - **All rotation deltas below are simulator against simulator.**
- **VCP replica** (`scripts/setups.py`): hard stop (intraday, a gap fills at the open) plus close below
  SMA50, on adjusted bars. It lands within 0.1 R of the engine's gross R on 97% of the 214 trades, with
  the same mean hold (27.8 sessions).
  - "Account pts" = Σ(R_net × the trade's risk % of equity). This is simple, not compounded, and it
    ignores slot and cash interactions. R5 already has 504 cash or size refusals.

## 1. Rotation

### 1A. After a name leaves the book (E2, forward % from the sale's open)

| Sale reason | n | Sold +21d | Bought same day +21d | Kept +21d | Sold +63d | Bought +63d |
| --- | --- | --- | --- | --- | --- | --- |
| out of buffer | 253 | +0.8 | +3.4 | +2.6 | +6.2 | +10.1 |
| not eligible | 69 | **+6.5** | +2.7 | +3.4 | **+13.9** | +8.7 |

These compare stocks with stocks: sold names against the names that replaced them. NIFTY is compared per year only (§1D).

- **Out of buffer.** Sold minus bought at 21 sessions by year: −1.2, −2.8, +1.9, −2.0, −0.1, −3.0.
  Names sold at rank 40-60 had already lost 3.3% in the decision month. The book does not sell too
  early. The weekly test (sell anything ranked >100 or >150 mid-month) does not show it selling too
  late either: deep100 CAGR 30.20 vs 29.32, and with the liquidity fix it adds nothing (33.03 vs 33.05).
- **Not eligible.** Sold minus bought at 63 sessions by year: E2 +6.2, +12.9, +5.9, −1.9, +2.8, −1.2.
  B1 and H3 show the same pattern: positive in 2016-2018 and 2020, negative in 2021.
  - Composition: 58 turnover failures, 10 index exits and 1 other.
  - The excess is **skewed**. The median is +4.6 pts with 59% hits, but the top 5 of 69 events carry
    89% of the summed excess.

### 1B. The path of winners and losers (E2 whole trades)

- **At 5, 10 and 20 sessions after entry:** losers are at −1.5 / −3.3 / −4.6%, winners at +2.9 /
  +4.3 / +8.1%.
- **Ten sessions predicts the outcome.** Trades below −10% excess at day 10 (n=20) finish with 25%
  winners. Trades above +10% (n=42) finish with 88%.
- **But cutting the early laggards does not pay.** Exiting at day 10 when excess < −10% gives CAGR
  27.90 vs 29.32, and at day 20 it gives 29.61, with mixed years.
- **Give-back.** Winners peak at a median +26.6% and exit at +13.3%: a median give-back of 8.6% from
  the peak, and 65% of peak gains kept. Every trailing stop tested (20/25/30%) lowers CAGR and *raises*
  max DD (38.4-38.8 vs 34.6). The book re-buys the next leader at full weight anyway.

### 1C. Drawdown anatomy (E2's book; points of peak equity, peak to trough)

| Episode | Depth | TRI fall | Book beta at peak | Market (β×TRI) | Residual | Worst industry (residual, weight) | Gaps ≤ −5% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-02-19 → 03-24 | 34.2 | 36.0 | 0.87 | −31.3 | −2.7 | Financial Services −4.5 (40%) | −19.0 |
| 2018-08-31 → 2019-08-22 | 22.6 | 11.6 | 1.12 | −12.9 | −7.1 | IT −3.0 (35%) | −2.7 |
| 2016-01-01 → 02-26 | 20.5 | 13.3 | 1.35 | −16.2 | −4.4 | Healthcare −3.0 (30%) | −0.6 |
| 2016-11-01 → 12-26 | 20.3 | 10.3 | 1.21 | −11.7 | −8.6 | Financial Services −5.7 (34%) | −8.9 |
| 2018-01-10 → 03-23 | 15.6 | 8.3 | 1.47 | −12.3 | −3.2 | FMCG −1.4 (15%) | −7.6 |

- **Beta is the bulk of every episode.** The second-largest piece is the concentrated industry, which
  G1's cap of 4 already targets.
- **Single-name blow-ups are small.** The worst three names cost 1-2 pts each.
- **The gap column overlaps the market column.** The 2020 gaps were market gaps.

### 1D. Counterfactuals (simulator, E2 config; per year return % / in-year max DD %)

| Variant | Invested % | CAGR | Max DD | Sharpe | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NIFTY 500 TRI (per year) | — | 15.66 | — | — | +5.1/13.8 | +37.7/4.8 | −2.1/15.6 | +9.0/11.5 | +17.9/38.1 | +31.6/9.8 |
| base | 100.2 | 29.32 | 34.63 | 1.30 | −7.9/20.5 | +83.1/7.9 | −9.5/22.9 | +15.5/13.7 | +37.7/34.6 | +92.7/7.3 |
| **liq hold ≥5 cr** | 100.1 | **33.05** | 35.93 | 1.43 | −7.6/20.5 | +92.2/7.9 | −5.8/23.0 | +19.1/12.8 | +44.8/35.9 | +92.3/7.3 |
| liq hold ≥2.5 cr | 100.1 | 33.44 | 35.93 | 1.45 | −8.0/20.5 | +100.3/7.8 | −5.5/23.0 | +17.2/12.8 | +44.4/35.9 | +91.4/7.3 |
| liq hold none (index + price only) | 100.1 | 32.75 | 35.93 | 1.42 | −9.8/20.6 | +96.1/7.8 | −3.9/22.7 | +17.2/12.8 | +44.4/35.9 | +90.3/7.6 |
| entry and hold ≥5 cr | 100.2 | 31.87 | 36.33 | 1.41 | −9.1/21.0 | +87.9/7.4 | −7.3/22.1 | +18.3/13.2 | +47.7/36.3 | +90.0/7.3 |
| **inverse-beta weights** | 100.2 | 30.59 | **33.94** | 1.40 | −4.8/19.1 | +78.4/7.1 | −8.2/21.5 | +16.7/11.1 | +35.7/33.9 | +100.8/6.9 |
| inverse-vol weights | 100.2 | 28.25 | 33.71 | 1.31 | −4.9/18.9 | +74.9/7.2 | −9.8/22.1 | +14.2/13.1 | +36.4/33.7 | +90.2/7.7 |
| **liq 5 + inverse beta** | 100.1 | **34.19** | 35.07 | **1.53** | −4.9/19.1 | +86.1/7.1 | −5.1/21.5 | +20.3/10.5 | +44.3/35.1 | +100.4/6.9 |
| no reweight (R1-like) | 100.0 | 29.77 | 37.57 | 1.31 | −7.5/20.6 | +89.8/8.1 | −15.4/25.0 | +13.6/13.8 | +44.7/35.0 | +95.5/7.9 |
| stop 15% below entry, proceeds to holdings | 100.2 | 29.35 | 35.34 | 1.32 | −10.2/23.0 | +84.0/7.9 | −10.4/22.8 | +11.2/15.4 | +49.9/31.9 | +89.7/7.9 |
| stop 25% below entry, proceeds to holdings | 100.2 | 29.51 | 32.94 | 1.31 | −10.7/22.0 | +83.1/7.9 | −9.8/23.0 | +14.0/13.7 | +45.5/32.3 | +92.7/7.3 |
| stop 20% below entry, cash | 98.5 | 26.38 | 33.34 | 1.25 | −14.3/22.8 | +83.5/7.9 | −12.7/23.1 | +13.1/14.1 | +40.2/30.4 | +87.1/7.9 |
| trailing 25% from peak, to holdings | 100.2 | 27.72 | 38.76 | 1.25 | −12.1/22.5 | +81.9/7.9 | −16.6/25.0 | +13.6/15.0 | +43.0/34.6 | +100.2/7.6 |
| trailing 25%, cash | 97.7 | 26.78 | 32.32 | 1.30 | −13.5/22.8 | +81.7/7.9 | −17.0/24.2 | +13.6/14.9 | +41.0/28.4 | +98.6/7.6 |
| monthly stop 10% below the rebalance price | 99.7 | 22.30 | 35.82 | 1.11 | −9.8/23.3 | +68.4/8.4 | −16.7/22.1 | +12.0/14.7 | +29.9/33.1 | +81.7/7.9 |
| monthly trail 15% | 99.6 | 24.43 | 37.09 | 1.19 | −12.0/24.1 | +78.9/8.3 | −12.6/23.1 | +10.2/15.7 | +32.7/33.1 | +84.6/8.6 |
| early fail (day 10, excess < −10%) | 100.2 | 27.90 | 34.73 | 1.25 | −10.2/22.0 | +82.5/7.9 | −10.1/22.9 | +15.5/13.7 | +37.9/34.6 | +86.6/7.8 |
| weekly sell if rank > 100 | 100.2 | 30.20 | 35.33 | 1.34 | −5.5/19.8 | +80.6/8.2 | −8.9/22.9 | +13.5/14.3 | +42.3/34.6 | +93.9/7.3 |

**Robustness across configs** (CAGR / max DD; sign count = years better than that config's base):

| Config | Base | liq hold ≥5 cr | Inverse beta |
| --- | --- | --- | --- |
| E2 (vol 63, top 20) | 29.32 / 34.63 | 33.05 / 35.93, return better 5/6 yrs | 30.59 / 33.94, in-year DD lower 6/6 |
| B1-like (vol 252) | 27.52 / 35.89 | 31.84 / 34.37, 4/6 | 28.56 / 34.49, in-year DD lower 6/6 |
| top 30, buffer 60 | 26.07 / 36.78 | 28.76 / 36.14, 4/6 | 27.58 / 35.02, 5/6 lower, 1 tie |
| top 10, buffer 20 | 34.49 / 39.60 | 37.34 / 34.26, 4/6 | 33.43 / 39.37, 6/6 lower |

## 2. Setups (VCP R5, `01a1909f`, 214 trades; entries carry the known look-ahead, so this is exits conditional on them)

- **R distribution.**
  - Expectancy 0.58 R net, with 31% winners. Winners average 3.36 R and losers −0.66 R.
  - Bands: 41 trades at ≤ −0.9 R, 60 at −0.9…−0.5, 47 at −0.5…0, 24 at 0…1, 18 at 1…3, 19 at 3…10,
    5 above 10 R.
  - The top 5 trades carry 64% of the replica's R.
- **MFE capture and give-back.** Mean MFE is 2.75 R and capture (ΣR ÷ ΣMFE) is 0.21. Winners give
  back 3.9 R on average from their MFE. Of the losers, 66 never reached +0.5 R, 75 reached 0.5-2 R, and
  7 passed 2 R.
- **Exit reasons.** 175 trades exit on SMA50 and 37 on the initial stop.
  - **26 SMA50 exits come within 3 sessions, at −0.62 R on average.** The other 149 SMA50 exits
    average +1.18 R.
  - **4 trades exit on SMA50 on the entry day itself**, because the entry day closed below SMA50.
  - 97% of entries close above SMA50, most of them by only 1-3%.

| Exit variant (replica, R net of the mean fee) | Exp R | Invested proxy % | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | Years better | Top-5 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R5 replica (stop + SMA50 close) | 0.75 | 48.2 | 5.4 | 40.9 | 3.2 | −5.9 | 21.8 | 50.2 | — | 0.64 |
| **SMA50 armed after MFE ≥ +1 R** | **0.91** | **60.6** | 9.9 | 39.4 | 1.9 | −3.2 | 41.9 | 53.5 | 4/6 | 0.54 |
| SMA50 armed after +2 R | 0.88 | 68.8 | 8.3 | 37.6 | 0.7 | −3.3 | 39.2 | 53.6 | 4/6 | 0.56 |
| SMA50 with a 2% buffer | 0.93 | 66.8 | 9.3 | 36.0 | 0.8 | −4.1 | 40.6 | 58.5 | 4/6 | 0.56 |
| SMA50 armed after 10 sessions | 0.74 | 51.4 | 4.5 | 40.5 | 2.7 | −7.6 | 25.0 | 48.9 | 1/6 | 0.65 |
| two closes below SMA50 | 0.66 | 56.0 | 3.8 | 30.3 | 0.2 | −5.9 | 25.9 | 47.4 | 2/6 | 0.61 |
| SMA20 close | 0.29 | 22.9 | 2.8 | 6.7 | −4.6 | −3.1 | 18.0 | 23.7 | 1/6 | 0.52 |
| breakeven at +2 R | 0.70 | 46.5 | 5.7 | 40.9 | −2.5 | −6.5 | 21.8 | 49.3 | 2/6 | 0.69 |
| time stop: day 10 below +0.5 R | 0.55 | 36.8 | 2.9 | 35.8 | 0.1 | −4.2 | 12.3 | 39.0 | 1/6 | 0.84 |
| trail: give back 50% after +3 R | 0.62 | 40.9 | 7.9 | 39.3 | −1.1 | −4.8 | 17.5 | 37.7 | 2/6 | 0.63 |
| partial ⅓ at +3 R | 0.61 | 48.2 | 5.7 | 30.7 | 1.6 | −4.9 | 19.0 | 41.5 | 2/6 | 0.56 |
| 10-day low after +3 R | 0.47 | 39.3 | 4.3 | 19.8 | −0.7 | −5.2 | 25.7 | 28.2 | 2/6 | 0.54 |

The year columns are account pts: Σ R × risk %, not compounded.

- **Reading.** Every exit that takes profit earlier loses: VCP's edge is its tail. The leak is at the
  front, where the SMA50 rule acts as a stop tighter than the initial stop.
- **The three "arm later" forms agree** (+1 R, +2 R and a 2% buffer give 0.88-0.93 R). That is a
  plateau, not a single tuned point. The gain is concentrated in 2020 (+20 pts) and is slightly
  negative in 2017-2018.
- Old-VCP entries (B2 trades, run through the R5 rules) give the same ordering: 0.78 → 0.94 R.

## 3. Ranked ideas (by expected robustness)

1. **Inverse-beta position weights (rotation).**
   - **Rule:** at each rebalance, weight each target name ∝ 1 / max(β, 0.5). β is the 252-session daily
     beta to NIFTY 500 TRI on the decision close. Weights are scaled to sum to n/top_n, so the book
     stays fully invested.
   - **E2 effect:** return by year +3.1, −4.7, +1.3, +1.2, −2.0, +8.1 pts. In-year DD −1.4, −0.8, −1.4,
     −2.6, −0.7, −0.4. CAGR +1.27, max DD −0.69, Sharpe 1.40 vs 1.30.
   - In-year DD is lower in 23 of 24 config-years.
   - **Why:** drawdowns are 60-90% beta, and sizing is the only lever that keeps the money invested.
     It has no new tunable beyond the beta window and the floor.
2. **Liquidity hysteresis for holdings (rotation).**
   - **Rule:** entry still needs a 20-bar mean turnover ≥ ₹10 cr. A holding is kept while ≥ ₹5 cr,
     still in the index, at price ≥ 50 and ranked within the buffer.
   - **E2 effect:** return by year +0.3, +9.1, +3.7, +3.6, +7.1, −0.4 pts. In-year DD 0, 0, +0.1, −0.9,
     +1.3, 0. CAGR +3.73, max DD +1.30, 40 fewer buys.
   - The 2.5 cr and no-floor versions give 32.8-33.4, so this is a plateau. Return is better in 17 of
     24 config-years.
   - **Why:** quiet volume in a held leader is not a trend failure. A single threshold for entry and
     exit forces a sale of the book's consolidating names, and index rules use buffers for the same
     reason.
   - **Caveat:** the excess is skewed (top 5 of 69 events carry 89% of it), and 2021 is negative.
     Capacity: 5% of ₹10L is ~0.1% of ₹5 cr ADV.
3. **Stack 1 + 2.**
   - E2 effect: return by year **+3.0, +3.0, +4.4, +4.8, +6.6, +7.7 pts (6/6 positive)**. In-year DD
     −1.4, −0.8, −1.4, −3.2, +0.5, −0.4. CAGR 34.19 vs 29.32, max DD 35.07 vs 34.63, Sharpe 1.53,
     invested 100%.
   - Test it as one engine run after the two singles, on E2 and on H3. H3's industry cap and
     scale-down were not in the simulator.
4. **VCP: arm the SMA50 close exit only after MFE ≥ +1 R.** The hard stop alone protects before that.
   - Effect, account pts by year: +4.5, −1.5, −1.3, +2.8, +20.2, +3.3. Exp R 0.75 → 0.91. Invested
     proxy 48 → 61%. Top-5 share 0.64 → 0.54.
   - Re-test only after the entry fix, because the entry look-ahead may be what creates these
     near-SMA50 entries.
5. **Negative result: do not add per-position stops, trails, early-failure exits or weekly rank
   checks to the rotation.**
   - 13 variants: no stop/trail form beats base on both CAGR and max DD with a consistent sign.
   - The 25% entry stop helps only 2020: −2.8 / 0 / −0.3 / −1.5 / +7.8 / 0 pts by year.
   - Post-gap drift is positive.
   - Turning reweighting off adds +0.45 CAGR for +2.9 pts of max DD.

## 4. Engine flags (none is a confirmed bug)

1. **Universe filters act as hard exits.** A `rotation_not_eligible` sale (69 in E2) is a design leak
   (idea 2). It also interacts with the pending owner decision on min_turnover over bars vs sessions.
2. **VCP entry-day exits.** Four trades exit at the close on the entry day on SMA50, because the
   intraday pivot estimate fills while the day closes below SMA50. Several exit the same day on the
   initial stop, because the day's low may come before the fill on daily bars. Both come from the
   daily-estimate entry under audit, not from the exit code.
3. **Fidelity gap.** Replaying E2's own book gives +0.75 CAGR more than the engine. This is consistent
   with dividends (total-return bars) and the 09:20 fill vs the open. It is small, but every variant
   delta above is simulator against simulator for that reason.

## Files

`/data/workspace/plans/leak-exits-work/`:
- `scripts/`: `lib.py` (replay), `rank.py` (rank replica), `sim.py`, `variants.py`, `rot_dropout.py`,
  `dd_decomp.py`, `setups.py`, `summary.py`, and loaders.
- Outputs: `variants.json`, `sim-*.csv`, `dropout-*.csv`, `trades-path-*.csv`, `setups-*.csv`.
- Copied run files: `runs/<id>/`.
