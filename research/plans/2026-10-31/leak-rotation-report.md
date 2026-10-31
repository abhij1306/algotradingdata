# Leak and bias audit: momentum rotation (G3 p5 base), in-sample 2016–2021

Scope: E2 (`01a190de`, vol_sessions 63), B1 (`01a19039`), G1 (`01a19104`), H3 (`01a1910e`), plus the other
in-sample variants (R1, R3, E1, E3, E4, E6, F1, H1). The run folders were copied read-only from m3 to
`plans/leak-rotation-work/runs/`. No engine backtest was run, and no data after 2021-12-31 was used.
Scripts and outputs are in `plans/leak-rotation-work/`:
- `a1`–`a9` and `sig.py`: the analysis scripts.
- `out_sig.json` and `out_eng_vs_replica.csv`: their outputs.

## Verdict

- **I found no material leak in the mechanics.** I wrote an independent replica from raw NSE bhavcopies
  (`sig.py`). It uses NSE's prev_close chain, the PIT NIFTY 500 table and the engine's own pure `scores()`.
  - It reproduces E2's monthly returns to a mean of **−0.02%/month** (71 months).
  - The engine's leg-by-leg price path matches the raw chain to a **0.000% median**. The 2 legs off by more
    than 5% are corporate actions my chain cannot see (bonus or rights issues).
  - Timing is correct: the rank uses the close at T, and the fill is at T+1 at 09:20.
  - Fills at the open are not flattering: the open-to-(H+L+C)/3 difference is −0.01% for buys and −0.01% for sells.
  - Membership coverage is complete: 500–501 members on every night, all with bars.
  - No rotation trade exited on a delisting, suspension or demerger.
- **The in-sample edge is real but much smaller and narrower than 28–32% CAGR suggests.**
  - **Concentration in time.** About 80% of E2's log growth came in 21 of 72 months (2020-04 → 2021-12).
    For 2016–2019, E2 made **14.2% CAGR vs TRI 11.3%** (+2.9/yr), with 1.5–2× TRI's drawdowns. H3 and F1 made
    10.6% and 10.9%, below TRI. CAGR excluding the best 6 months is 14.5%.
  - **Concentration in stocks.** About **34% (E2) to 45% (B1) of net P&L** came from 16–18 trades in names that
    closed at an NSE price band 5 or more times while held. These are circuit-bound names, mostly the 5%-band
    Adani group and TTML. TTML alone is about 10% of E2's P&L, bought one tick under its upper band.
  - **Parameter choice is noise.** The lever differences (G1 +4.4, E2 +1.1 CAGR) are smaller than
    rebalance-day timing luck. Moving the decision 5, 10 or 15 sessions off month-end moves CAGR by 25.1–31.0
    and per-year excess by up to ±15 pts.
- **The momentum signal itself is genuine.**
  - Top-20 vs the equal-weighted eligible universe: 26–28% vs 13% gross; excess t ≈ 2.3; 9 of 12 half-years positive.
  - The result holds across lookbacks, top_n and vol windows.
  - A random 20 of the same universe gives a 95th percentile of 19.2%.
  - A liquidity-only universe in 2012–2015 also shows it: 30.8% vs 14.7% equal-weighted, gross.
  - But the eligible equal-weighted universe lagged cap-weighted TRI (13.0 vs 15.4 over 6 years; 4.7 vs 11.3
    in 2016–2019). The excess over TRI therefore depends on small and mid-cap momentum regimes (2017-H2,
    2020-21).
  - Realistic expectation in normal regimes: **+2 to +5 pts/yr over TRI**. That matches the 2022–2025 hold-out
    (E2 +1.2).

## Findings table

| # | Issue | Code location | Effect size (in-sample, E2 unless noted) | Fix | Type |
|---|---|---|---|---|---|
| 1 | Rank and fill timing. The decision uses the close at T (`view.as_of(prev)`, a TR window ending `index[prev]`); members are taken on the trade date; the fill is at T+1, 09:20 | `backtest/loop.py:1068-1098`, `backtest/rotation.py:105-134`, `engine/rotation.py:194-203` | No look-ahead. The independent replica matches to −0.02%/mo | None | OK |
| 2 | The 09:20 price before 2021-10-26 is the open moved by the **median** open→09:20 (+2 bps buy, −3 bps sell) | `engine/fill_0920.py:61,73-98` | Real 09:15 fills Nov–Dec 2021 (63 buys, 54 sells) vs the open: buys mean adverse +0.085% (median +0.02%); sells were 0.22% favourable. The open itself is not favourable vs the day. ≤0.1 pt/yr | Use the mean (or sample the empirical distribution) instead of the median | Modelling |
| 3 | Flat 20 bps slippage, no size or liquidity term | `costs.py:54,257` | Orders are ≤0.33% of the day's value (p99 0.23%). Square-root impact on top: start ₹10L 0.2, ₹1 cr 0.6, ₹5 cr 1.4, ₹25 cr 3.2, ₹100 cr 6.3 pts/yr. Turnover is 5.9×/yr; the flat 20 bps costs 1.2 pts/yr | Add σ·√(Q/ADV20) impact; report capacity at ₹1/5/25 cr | Modelling |
| 4 | Upper-circuit buy refused only when the open is the high **and** at the band. A buy one tick under the band on a day that locks is filled at open+2 bps | `backtest/loop.py:1100-1133`, `fillrules.py:54` | 3 of ~720 buys (TTML 2021-11-01, HINDCOPPER 2021-03-01, SUPPETRO). TTML = ₹3.53L, about 10% of E2's P&L. Removing it statically gives E2 ~26.2% CAGR (−1.8, upper bound) | When the day's high is at the band and the open is within N ticks of it, fill at the band or refuse. Count these as `near_band_buy` | Bug-adjacent |
| 5 | Lower-circuit sale refused only when the whole day is pinned (no 5m data) | `backtest/loop.py:1141-1160` | 3–6 sales opened at ±5% and the open was the day's low or high; 1 sale was blocked (ADANIGREEN trim 2020-07-01). Negligible | None needed. Keep counting | OK |
| 6 | Circuit-band, trade-for-trade and surveillance names are tradable (EQ+BE); no band, ASM or F&O awareness | `series_in` in the seed config; `decisions.md` "Tradable series" | Trades with ≥5 upper-band closes while held: **34% (E2), 45% (B1), 35% (G1) of P&L**. Trades with BE days: 25–31%. Removing them statically gives E2 ~21.6%, B1 ~18.3% | Report the P&L share every run. Test excluding names with ≤5% bands or BE series at entry, or capping their weight | Modelling / realism |
| 7 | Delisting exit at the last close uses hindsight | `backtest/loop.py:2339-2366` | **0** rotation exits by delisting, suspension or demerger in all 12 runs | None (counted `HINDSIGHT_DELISTED_EXIT`) | OK |
| 8 | Corporate-action adjustment of the price basis | `TrCloses` (`backtest/rotation.py:105`); price basis | Leg ratios vs NSE's chain: median 0.000%, 44/806 legs >1%, all explained by bonus, rights or split days and 09:15 5m fills | None | OK |
| 9 | PIT NIFTY 500 membership | `hat_index_member`, `loop.py:1077` | 500–501 members every night, every one with a bar. History starts 2016-01-01 | Membership for 2011–2015 is needed before the 10-yr in-sample (or use a liquidity-defined universe) | Data |
| 10 | Unknown industry is survivorship-correlated (only matters with `max_per_industry`) | `engine/rotation.py:19-22,265-268`; `decisions.md:262-275` | Unknown-industry legs: 14–35 per run, net −₹12k…−₹83k of ₹2.0–4.4M (losers, kept). Matters little in 2016–21 with `free`; it will be worse in 2011–15 | Keep `free`; no industry cap in the 10-yr test until a PIT classification exists | Bias (small) |
| 11 | Series filter | `backtest/data.py:1165` (series from the bars, PIT) | The backtest is PIT. The "today's series" item applies elsewhere, not to this path | None for backtests | OK |
| 12 | Sized on decision-close equity, not 09:20 marks | `backtest/loop.py:793,1049`; known gap `rotation_sized_on_decision_close` | No look-ahead (the equity is set before the day's trades). It causes some cash scaling (14 of 72 rebalances in B1) | Optional: size on 09:20 marks as live does | Modelling |
| 13 | Benchmark mismatch: cap-weighted TRI vs an equal-weight small/mid-tilted book | reports | Size/EW beta 0.7–0.8. E2 alpha vs TRI 1.02%/mo (t 2.1); with EW−TRI as a factor 1.07%/mo (t 2.5) | Report excess vs the EW eligible universe and alpha t-stats beside TRI | Reporting |
| 14 | Selection from many in-sample variants (~20) plus rebalance-day luck | reports | Timing luck (decision 0/5/10/15 sessions after month-end): CAGR 28.5 / 31.0 / 25.1 / 29.4. 2016–19: 13.1 / 11.8 / 8.8 / 21.0. This is larger than every lever gain | Tranche the rebalance (4 staggered sub-books). Use the deflated Sharpe (`backtest/dsr.py`) for selection | Process |
| 15 | `engine_commit` wrong for exported-tree runs | G3 report | Reproducibility only | Record the exported tree's commit | Bug (minor) |

## Supporting numbers

**Concentration (engine runs, `a1`, `a6`).**

| Run | Top-5 / top-10 / top-20 trades' share of P&L | P&L by entry year 2020+2021 | CAGR ex best 3 / 6 / 12 months | Log growth from 2020-04 to 2021-12 |
|---|---|---|---|---|
| E2 | 37% / 59% / 79% | 83% | 20.8 / 14.5 / 4.2 | 80% |
| B1 | 38% / 58% / 83% | — | 19.1 / 12.7 / 1.5 | 75% |
| G1 | 34% / 54% / 74% | — | 25.0 / 18.4 / 7.3 | 78% |

Liquidity:
- Entry ADV20: median ₹46–49 cr, 10th percentile ₹13 cr.
- Position as a share of ADV: median 0.02%, maximum 0.16% at ₹10L start.
- Tiny or illiquid names do not drive the P&L. The q3–q4 ADV buckets (₹17–35 cr) carry most of it.

**Per half-year excess over TRI** (engine `equity.csv`, 2016a … 2021b, pts):
- E2: −12.7 +0.6 +9.0 +20.4 −2.5 −6.9 +2.0 +3.5 +9.8 +6.0 +22.8 +16.7 (9 of 12 positive).
- 2016–19 CAGR vs TRI 11.3: B1 15.7, E2 14.2, R1 14.2, E3 14.5, G1 14.0, E4 12.9, F1 10.9, E1 10.7, H3 10.6.
- 2020–21 CAGR: 52–79 vs TRI 24.6.

**Signal-level robustness, 2016–2021** (replica, gross, price return; `out_sig.json`).
- Top-20 with buffer 40, CAGR:
  - riskadj (vol 63): 26.4
  - vol 252: 26.0
  - vol 126: 26.6
  - short 63: 28.3
  - r6: 26.5
  - r12_1: 19.3
  - hi52: 21.5
- top 10 / 30 / 50: 29.5 / 24.3 / 23.8.
- Equal-weighted eligible universe: 13.0. Mean monthly rank IC is only +0.03 (t ≈ 1.5), so the edge sits in the extreme top tail.
- Excess over the equal-weighted universe by year (E2-like): −11.3, +30.1, +4.5, +20.0, +19.6, +31.7.

## Fixes (in order)

1. **Near-band buy rule** (#4): fill at the band or refuse when the day's high is at the upper band and the
   open is within a few ticks of it. Count these fills. This is a small code change.
2. **Fill estimate** (#2): use the mean open→09:20 move by side, not the median.
3. **Impact term** (#3): add a liquidity-scaled impact on top of the flat 20 bps, and report capacity at
   ₹1, 5 and 25 cr.
4. **Run metrics:** report every run's P&L share from circuit-band and BE names (#6), its excess vs the
   EW-eligible universe and its alpha t-stats (#13).
5. **Data before the 10-yr run:** PIT NIFTY 500 membership for 2011–2015, or switch to a liquidity-defined
   universe (#9). Note the higher unknown-industry share (#10).
6. **Minor:** correct `engine_commit` (#15).

## Rotation design changes worth testing in the 2012–2021 walk-forward

These are principled and use literature defaults. None is fitted to 2020.

1. **Tranched rebalancing.** Run 4 sub-books, each rebalanced monthly, staggered by a week. This removes
   the timing luck that is larger than any lever (#14). It needs no new parameter.
2. **Tradability filter at entry.** Exclude BE or trade-for-trade series and price bands of 5% or less at
   entry, or require F&O membership. This is realism, not alpha.
3. **Fixed literature score with a tie to stability.** Use 12-1 or the riskadj 6/12-month score with
   vol 252. Choose between them by walk-forward stability across windows (rank IC per year), never by the
   best in-sample CAGR.
4. **Residual (beta- or sector-adjusted) momentum.** Rank on returns net of the market or industry. This is
   known to cut momentum crashes and concentration (the 2016-Q4, 2018 and 2020-Q1 episodes).
5. **Volatility-managed exposure.** Scale the book by its target vol over 6-month realised vol, with a
   fixed target, and park the remainder in the least-volatile ranked names rather than cash (deployment
   rule). This replaces the breadth gates that were fit to 2020.
6. **More names with liquidity-capped weights.** Use top 30 with buffer 60, weights capped at k × ADV20.
   This trades 2–4 CAGR in-sample for less single-name and circuit risk and more capacity.
7. **Evaluation rule.** Report excess vs TRI and vs the EW-eligible universe, deflated Sharpe over all
   trials, years positive out of 10, and CAGR ex the best 6 months.

## Follow-up: the turnover floor and the missing skip

These checks reuse the replica on data already pulled (`b1_followup.py`). They are gross price returns,
top 20 with buffer 40.

**1. The fixed ₹10 cr 20-day turnover floor** (`engine/criteria/universe.py:41-50`).
- It is a nominal rupee floor, so it admits a different share of the index each year. Passers on
  decision nights: 185 of 500 in 2015-12, 214 in 2019-12, 348 in 2020-12. In 2012–15 it will admit fewer
  still.
- E2's `rotation_not_eligible` sales by year, 2016 to 2021: 17, 15, 10, 11, 10, 6. These include index
  exits.
- Replacement tested: a relative floor that keeps the top 70% of each night's members by ADV20 (312–334
  names every year). CAGR rises from 28.5 to 31.9, and 2016–19 from 13.1 to 14.9.
- **It did not fix 2016 in the replica** (−9.3% vs −9.0%). The two-thirds attribution from the 2025
  diagnosis does not reproduce here. The replica sells at the rebalance and ignores dividends, so treat
  this as indicative.
- Recommendation: use the relative floor, or a floor scaled by the median member ADV, for the 10-year run.
  It is principled because every year is treated alike, not because of the gain.

**2. `riskadj` ignores `skip_sessions`** (`engine/rotation.py:146-167`; the skip is used only in
`r12_1` and `hi52`, lines 137-142).
- Confirmed: both of riskadj's returns end at T, so the last month is in the rank.
- A 21-session skip lowers the 2016–21 CAGR from 28.5 to 24.0 (2016–19: 13.1 to 7.7). In this sample the
  last month continued rather than reversed.
- With the relative floor added as well, CAGR is 26.4.
- Recommendation: add the skip as an explicit knob (riskadj 12-1 / 6-1). Compare skip 0 and skip 21 in
  the walk-forward by stability across windows. Do not assume the textbook skip helps on NSE.
