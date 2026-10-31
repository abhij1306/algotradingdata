# 2017 diagnosis: VCP (Setup 1) vs NIFTY 500 TRI (2026-10-31)

All runs are **diagnostic**. They ran on m3 from main `bd503e9`, from 2017-01-01 to 2017-12-31 with the
loader's normal warm-up, against NIFTY500_PIT and the strategy version `aac4fda7-…`. The DB was read-only and
`HAT_DATA_ROOT=/data/workspace/hat-data-isin`. Nothing after 2018-06-29 was read (post-exit prices only).
The baseline is the s1-diag r1 VCP-alone variant, run on 2017 only:
**`01a18fe8-f1ca-76bc-ab46-6a3a147f8707`**. The TRI is the owner's +37.65%. The run's own
benchmark reads +37.93% (`run.json`), or +37.27% from the 2017-01-02 close.

## Verdict

**Idle capital is the failure. It comes from the strategy's signal scarcity, not from the risk settings.**

- **Baseline: +4.91% vs +37.65%, a gap of 32.7 pts.** The bot was invested **8.7%** on average. It had **0.54**
  open positions, held **16.2%** of equity per position, and had **no position on 55.2% of days**. The
  identity holds: 0.54 × 16.2% = 8.8% ≈ 8.7%.
- **Exposure explains more than the whole gap.** Cash earned nothing while the TRI made 37.65%. That
  costs 37.65 × (1 − 0.087) = **34.4 pts**. The invested capital beat the index: it returned
  4.91 / 0.087 = 56% per unit invested. So selection *added* **+1.6 pts**. The trades are not the problem;
  there are too few of them.
- **Of the two factors, the position count is the problem, not the position size.**
  - **Size.** 1% risk ÷ the 5.7% average stop = 17.5%. The actual 16.2% is already about one sixth of the
    account, which is what a 6-slot book is built for.
  - **Count.** Positions are 10 trades × 13.5 sessions held ÷ 248 sessions = 0.54. Six slots would need
    about 6.
  - **Log split of the shortfall to a full 6×16.7% book:** ln(6/0.54) = 2.41 for count against
    ln(16.7/16.2) = 0.03 for size. That is **~99% count, ~1% size**.
- **Strategy vs risk management.**
  - **Risk side.** The best risk-side change is risk 2% (c1): **+10.13%**. It closes 5.2 of the 32.7 pts
    (**~16%**). Risk 3% gives exactly the same run, because **p_max 25% caps every position from 2% risk
    upwards**. Cash and slots never bind: at most 2 of 6 slots were used, and cash averaged 91%.
  - **Strategy side.** The other **~84%** is the strategy. VCP produced 10 signals in the best year. It
    fired on **none of the 30 best 2017 stocks**, and it holds a trade for only 13.5 sessions.
- **"Even one good trade should beat NIFTY": not at these sizes.**
  - **The best trade, TATAGLOBAL.** It made +20.4% on half the position and +45.9% on the rest (still open
    at year end), about +33% on the stock. The position was 15.0% of equity, so it added **+4.93% to
    equity** (4.79R × 1.03%).
  - **What one trade would need.** To make +37.65% from one position at 16% of equity, the stock has to
    rise **+235%**. At the p_max cap of 25% it has to rise **+151%**, and the gain has to be held.
  - **Such stocks existed.** 23 of the top 30 rose more than 200% from their 2017 low to the year end (all 30 rose more than 175%). VCP saw none of
    them as a setup.
- **Max deployment (m1, the one stacked run): 55.0% invested, +0.66%, max DD 12.9%, against +37.65%.**
  - **What it stacked.** Risk 3%, p_max 50%, 10 positions, rs all_nse, breakout volume off and SMA50 exits.
  - **What happened.** With 50% positions, **cash binds** after two positions. TATAGLOBAL, TITAN (Oct),
    ESCORTS and MINDACORP were refused `size_below_min` with no cash left. That includes the year's best
    trade: TATAGLOBAL had +4.35R of forward R at 20 days. The losers took the big sizes instead, at
    0.003R expectancy.
  - **Conclusion.** Higher exposure from bigger positions on the same 11 signals is concentration, not
    diversification. It roughly triples the drawdown and earns nothing.
- **What 60–90% invested in 2017 would take.** Invested = trades × hold ÷ 248 × size.
  - At 1% risk (size ≈ 16–18%), 3.6–5.4 positions are open on average. That needs **66–100 trades a year
    at the 13.5-session hold**, or **47–70 at the ~19-session SMA50 hold** (c6), against **10**.
  - At 2% risk (p_max-capped at ~23%), it still needs 2.6–3.9 positions, which is **48–72 trades a year**.
  - The VCP setup alone cannot get there:
    - the most permissive single rule changes give 12–13 signals in 2017 (c3, c4);
    - the 6-year leave-one-out's best single rule (RS off) gives ~27 a year (s1-diag report);
    - and, from the opportunity audit, the year's leaders **did not form VCP bases at all**.
  - So 60–90% needs **other scanners feeding the same portfolio**. Those are setups that describe a stock
    trending without a ≥10% pullback (e.g. trend continuation or pullback-to-MA). It also needs the
    liquidity floor reconsidered, **and/or an idle-cash sleeve** (the portfolio `overlay: {sleeve: regime}`
    knob already exists). Only the sleeve gets 2017 to 60–90% invested by itself.

**Next tests across all six years (in-sample, 2016–2021):**

1. **Idle-cash ETF sleeve.** S1 r3 (setups 1–5) with `overlay: {sleeve: regime}` on a portfolio file.
   It goes straight at the 91% idle cash, and the knob exists.
2. **Breakout volume off at risk 2%.** These are two single-change runs, then the pair:
   - volume off (c4) gave 13 trades at 0.67R, against 10 at 0.48R;
   - it also removes the full-day-volume look-ahead: the baseline audit warns `lookahead_hindsight` and m1 does not;
   - risk 2% is the only risk change that binds, and above it p_max 25% does.
3. **A trend-continuation / no-base setup next to VCP, and a lower turnover floor.** In the opportunity
   audit, `no_base` (price never 10% below its 325-session high) blocks 26% of the leaders' advance
   nights. The ₹10 cr turnover floor blocks 33%. Both are strategy changes that need owner approval.
   The NSE_STOCKS universe is still blocked by its data audit (s1-diag step 4).

**Caveat on the baseline's edge (c5).** Entering at the breakout day's close on that day's known volume
removes the look-ahead. It turns 10 trades at +0.48R into **4 trades at −0.77R (−3.17%)**: 5 of the 9
signals close more than 2% above the pivot and are refused `max_chase`, and the winners are among them.
The baseline's intraday-fill-at-pivot plus full-day volume therefore flatters it. A true T+1 open entry
needs code (no knob), so it was not run.

## Run table: exposure, return and the invested-share identity

"Exposure gap pts" is 37.65 × (1 − avg invested). "Selection pts" is avg invested × (return/avg invested −
37.65). The two add up to 37.65 − return. "Avg pos size %" is invested ÷ open positions on days with a
position. "pos×size %" checks the identity. Avg hold = open pos × 248 ÷ trades: 13.5 (v0), 14.5 (c4),
19.1 (c6), 25.0 (m1) sessions.

| run | run_id | change | trades | exp R | return % | max DD % | avg invested % | avg open pos | avg pos size % | zero-pos days % | pos×size % | exposure gap pts | selection pts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v0 | `01a18fe8-f1ca-76bc-ab46-6a3a147f8707` | VCP alone, 2017 only (diagnostic baseline = s1-diag r1) | 10 | 0.482 | 4.91 | 4.01 | 8.7 | 0.54 | 16.2 | 55.2 | 8.8 | 34.4 | 1.6 |
| c1 | `01a18fef-e40b-7149-9ff1-0a2bdc070e60` | risk per trade 2% (diagnostic) | 10 | 0.482 | 10.13 | 5.01 | 12.8 | 0.54 | 23.4 | 55.2 | 12.7 | 32.8 | 5.3 |
| c2 | `01a18ff4-58ee-72ba-bb4b-00210754001d` | risk per trade 3% (diagnostic) | 10 | 0.482 | 10.13 | 5.01 | 12.8 | 0.54 | 23.4 | 55.2 | 12.7 | 32.8 | 5.3 |
| c3 | `01a18ff8-3823-7084-aff5-d23d0914388b` | rs_rank basis all_nse (diagnostic) | 12 | 0.398 | 4.84 | 4.01 | 10.8 | 0.67 | 16.3 | 55.2 | 10.9 | 33.6 | 0.8 |
| c4 | `01a18ffd-1f15-7622-9a0d-e544fe19c065` | breakout volume off (diagnostic) | 13 | 0.666 | 8.96 | 3.51 | 11.2 | 0.76 | 14.9 | 48.0 | 11.3 | 33.4 | 4.7 |
| c5 | `01a19002-0647-74d4-959c-97747dc226ae` | entry at the breakout day close on its known volume (closest knob to T+1) (diagnostic) | 4 | -0.770 | -3.17 | 3.17 | 1.6 | 0.10 | 17.0 | 90.3 | 1.6 | 37.0 | -3.8 |
| c6 | `01a19007-3486-74e2-837f-dfb5938aabb5` | wide exits: SMA50 close, no partial, no breakeven (diagnostic) | 10 | 0.438 | 4.56 | 5.23 | 13.8 | 0.77 | 18.2 | 46.4 | 14.0 | 32.5 | -0.6 |
| c7 | `01a1900b-8b68-7429-a2ed-6796528f23f7` | wide exits: 20-day swing-low trail, no SMA exit, no partial, no breakeven (diagnostic) | 10 | 0.303 | 3.11 | 6.43 | 14.3 | 0.80 | 18.2 | 44.4 | 14.5 | 32.3 | -2.3 |
| m1 | `01a19011-2070-76e1-a706-361301b55f39` | MAX DEPLOYMENT (diagnostic, several changes): risk 3%, p_max 50%, 10 positions, rs all_nse, breakout volume off, SMA50 exit without partial or breakeven | 11 | 0.003 | 0.66 | 12.91 | 55.0 | 1.11 | 49.5 | 26.6 | 55.1 | 16.9 | -20.1 |

What binds, per run:

- **v0 (1% risk).** Size is risk ÷ stop. Only PEL hit p_max: its 2.8% stop gave 25.0% of equity and 0.75%
  risk. Slots peaked at 2 of 6. Cash averaged 91.3%.
- **c1/c2 (2% and 3% risk).** p_max 25% binds on every trade. The realised risk was 0.75–2.04% of equity
  in both runs (`trades.csv` `risk_pct_equity`), so 3% buys nothing over 2%. That is why the two are
  identical. Raising max positions to 10 or p_max to 50% at 1% risk was not run: slots never pass 2, and
  p_max binds on one trade. Either would be a no-op.
- **m1 (max deployment).** **Cash** binds: on 94 of 248 days cash was < 5% of equity, and 4 signals were
  refused `size_below_min`.

## Return attribution of the baseline (`01a18fe8-…`)

| component | baseline | arithmetic |
|---|---|---|
| exposure | avg invested 8.71%, max 32.8%; 111 of 248 days with a position (zero on 55.2%) | gap from idle cash: 37.65 × (1 − 0.0871) = **34.4 pts** |
| sizing | avg position 16.2% of equity; avg stop 5.7% (2.8–8.1%) | 1% ÷ 5.7% = 17.5% target size; p_max 25% binds only at stops < 4% (PEL) |
| number of trades | 10 signals, 10 taken, 0 refused | 10 × 13.5 sessions ÷ 248 = **0.54 positions** |
| edge per trade | 50% win, avg R +0.48 | **10 trades × 0.48R × 1.03% realised risk = +4.96%**; actual +4.91% after the period-end marks |
| exits | realised Σ 4.82R against Σ MFE 21.36R (23% captured); 5 of 10 trades reached MFE ≥ 1.8R | the exits leave 16.5R on the table, but wider exits *lost* money in 2017 (c6 +4.56%, c7 +3.11% vs +4.91%) because the extra hold gave the gains back; the "after exit" columns below are mixed |
| selection (residual) | 56% return per unit invested vs TRI 37.65% | 0.0871 × (56.4 − 37.65) = **+1.6 pts** |

The gap is 32.7 = 34.4 (exposure) − 1.6 (selection). By month, invested % was 0 in Jan, Feb and May, and
peaked at 21.8% in Nov (`equity.csv`). Regime was off on 22 nights only (early Jan, late Jun, Aug, late Sep–early Oct, 6 Dec), so regime is not a cause.

**"One good trade".** The best trade was TATAGLOBAL: the stock rose +33% blended, at 15.0% of equity, for
+4.93% of equity. The best possible single position at the p_max cap of 25% in the year's top stock was
IBVENTURES (+1,227% from its low). Even that would have added ~300% of equity, but VCP never saw it as a
setup (`no_base` on all 20 member nights). One trade can beat the index only with a 25% position held
through a +151% move. The baseline's average 2017 winner is +1.86R ≈ +11% on the stock.

## Baseline trades (`01a18fe8-f1ca-76bc-ab46-6a3a147f8707`)

Size % eq is each leg's value over the equity at the previous close; a two-leg trade's legs add up. The
+20/+60 columns are the stock's close and its highest high 20 and 60 sessions after the exit, against the
exit price (adjusted bars, read through 2018-06-29). `period_end` legs are closed by the window, not by a
rule. Open positions, invested % and cash per day are in the run's `equity.csv`: max 2 open, max 32.8%
invested, min cash 67.2%.

| # | leg | symbol | entry | entry ₹ | exit | exit ₹ | stop % | size % eq | stock move % | P&L % eq | R | MFE R | MAE R | exit reason | hold | +20 close % | +20 max high % | +60 close % | +60 max high % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | JUBILANT | 2017-03-09 | 639.06 | 2017-04-12 | 754.47 | 6.10 | 8.4 | +18.1 | +1.50 | +1.45 | 3.15 | -0.03 | partial_target | 22 | -11.0 | -1.5 | -17.7 | -1.5 |
| 1 | 2 | JUBILANT | 2017-03-09 | 639.06 | 2017-04-19 | 703.46 | 6.10 | 8.5 | +10.1 | +0.83 | +0.81 | 3.15 | -0.03 | sma20_close | 26 | -10.3 | +3.2 | -11.6 | +3.2 |
| 2 | 1 | PEL | 2017-06-09 | 1514.09 | 2017-06-23 | 1511.06 | 3.01 | 25.0 | -0.2 | -0.11 | -0.14 | 2.80 | -0.07 | breakeven_stop | 10 | +2.8 | +7.3 | -1.2 | +7.3 |
| 3 | 1 | MUTHOOTFIN | 2017-07-26 | 469.93 | 2017-08-10 | 437.37 | 6.74 | 15.3 | -6.9 | -1.09 | -1.06 | 0.60 | -1.00 | initial_stop | 11 | +15.0 | +18.2 | +8.5 | +20.1 |
| 4 | 1 | TITAN | 2017-08-03 | 557.02 | 2017-08-29 | 599.25 | 6.33 | 16.3 | +7.6 | +1.19 | +1.16 | 2.30 | -0.03 | sma20_close | 16 | -1.2 | +9.2 | +34.5 | +38.0 |
| 5 | 1 | BALRAMCHIN | 2017-09-13 | 176.66 | 2017-09-18 | 168.46 | 4.45 | 23.5 | -4.6 | -1.15 | -1.09 | 0.74 | -1.00 | initial_stop | 3 | -5.3 | +3.8 | -13.5 | +6.5 |
| 6 | 1 | BEML | 2017-09-19 | 759.43 | 2017-09-21 | 725.85 | 4.23 | 24.8 | -4.4 | -1.15 | -1.10 | 0.48 | -1.00 | initial_stop | 2 | -5.5 | -0.0 | -17.5 | -0.0 |
| 7 | 1 | GODREJPROP | 2017-10-23 | 661.37 | 2017-11-15 | 671.30 | 6.50 | 15.8 | +1.5 | +0.20 | +0.19 | 1.83 | -0.29 | sma20_close | 17 | +4.9 | +11.6 | +25.0 | +35.8 |
| 8 | 1 | TATAGLOBAL | 2017-10-27 | 213.78 | 2017-11-20 | 257.43 | 6.86 | 7.5 | +20.4 | +1.51 | +1.47 | 6.84 | -0.45 | partial_target | 16 | +11.6 | +14.9 | +7.1 | +26.1 |
| 8 | 2 | TATAGLOBAL | 2017-10-27 | 213.78 | 2017-12-29 | 311.89 | 6.86 | 7.5 | +45.9 | +3.42 | +3.32 | 6.84 | -0.45 | period_end | 44 | -4.4 | +4.1 | -18.1 | +4.1 |
| 9 | 1 | ESCORTS | 2017-11-30 | 711.52 | 2017-12-04 | 674.75 | 4.98 | 20.9 | -5.2 | -1.13 | -1.08 | 0.76 | -1.00 | initial_stop | 2 | +14.5 | +18.2 | +31.2 | +36.8 |
| 10 | 1 | MINDACORP | 2017-12-22 | 198.86 | 2017-12-29 | 213.92 | 8.13 | 12.6 | +7.6 | +0.92 | +0.90 | 1.85 | -0.18 | period_end | 4 | -3.6 | +3.8 | -17.1 | +3.8 |

## Opportunity audit: the 30 best 2017 stocks in the PIT NIFTY 500

**Method.**

- **Ranking.** Members scanned on a 2017 night (553) are ranked by the year's last close over the lowest
  low before their biggest close-to-close advance ("low→year-end").
- **Replay.** `y2017_opps.py` replays the baseline's nightly scan as `s1_setups_audit.py` does: the same
  `config.json`, market, ledger and `scan_and_publish`. It hooks `scan.evaluate_playbook` to record every
  stock-night's first failing rule. The replay evaluated **113,216 stock-nights, the same as the run's
  funnel**. It published 92 watchlist rows against the run's 96; the replay holds no positions.
- **Per stock.** "First blockers" counts the first failing rule over the nights of the stock's advance
  (low date to peak date). "Closest" is the night it got furthest in the funnel, in this order: universe <
  trend template (8 rules) < rs_rank < VCP geometry < time compression < dry-up < relative correction <
  pivot / stop / overhead.

**Result: the setup fired on 0 of 30.** None of the 30 was ever traded, and none broke a pivot from a
watchlist row.

| # | symbol | low date | peak date | drawup % | low→year-end % | advance nights | regime-off | first blockers over the advance | closest-night blocker (night) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | IBVENTURES | 2017-01-31 | 2017-11-03 | 1412 | 1227 | 20 | 17 | vcp_geometry 20 | vcp_geometry:no_base (2017-11-03) |
| 2 | RAIN | 2017-01-06 | 2017-11-13 | 640 | 592 | 194 | 17 | vcp_geometry 148; universe 32; trend_template 14 | vcp_geometry:no_base (2017-11-13) |
| 3 | BOMDYEING | 2017-01-02 | 2017-12-21 | 511 | 476 | 222 | 21 | vcp_geometry 151; universe 47; trend_template 24 | vcp_geometry:no_base (2017-12-21) |
| 4 | AVANTIFEED | 2017-01-02 | 2017-11-10 | 497 | 424 | 194 | 20 | vcp_geometry 106; universe 88 | vcp_geometry:no_base (2017-11-10) |
| 5 | DBL | 2017-01-09 | 2017-12-26 | 361 | 342 | 167 | 18 | vcp_geometry 73; trend_template 72; universe 17 | trigger: no break of pivot (2017-09-22) |
| 6 | KOLTEPATIL | 2017-01-02 | 2017-11-28 | 353 | 336 | 206 | 20 | universe 134; vcp_geometry 42; trend_template 30 | vcp_geometry:no_base (2017-11-28) |
| 7 | MINDAIND | 2017-01-02 | 2017-12-22 | 342 | 332 | 166 | 21 | universe 118; vcp_geometry 48 | vcp_geometry:no_base (2017-12-22) |
| 8 | FRETAIL | 2017-01-02 | 2017-11-24 | 411 | 316 | 137 | 20 | trend_template 112; vcp_geometry 24; rs_rank>=70 1 | vcp_geometry:depth_ratio_too_wide (2017-10-23) |
| 9 | ADANITRANS | 2017-01-02 | 2017-12-22 | 319 | 298 | 223 | 21 | vcp_geometry 105; universe 100; trend_template 15 | relative_correction:correction_too_deep_vs_index (2017-07-05) |
| 10 | SUNTECK | 2017-01-02 | 2017-12-22 | 288 | 284 | 223 | 21 | universe 171; vcp_geometry 52 | vcp_geometry:no_base (2017-11-28) |
| 11 | FVIL | 2017-01-02 | 2017-12-26 | 297 | 282 | 224 | 21 | universe 153; vcp_geometry 51; trend_template 18 | relative_correction:correction_too_deep_vs_index (2017-10-17) |
| 12 | RCOM | 2017-11-15 | 2017-12-29 | 277 | 277 | 30 | 1 | universe 30 | universe:min_price (2017-12-28) |
| 13 | GVKPIL | 2017-05-25 | 2017-10-31 | 274 | 273 | 92 | 17 | universe 92 | universe:min_turnover (2017-10-31) |
| 14 | ITI | 2017-02-27 | 2017-10-26 | 296 | 241 | 14 | 17 | vcp_geometry 14 | vcp_geometry:no_base (2017-10-26) |
| 15 | BBTC | 2017-01-02 | 2017-10-18 | 234 | 230 | 178 | 20 | vcp_geometry 99; universe 71; trend_template 8 | vcp_geometry:no_base (2017-10-18) |
| 16 | JPASSOCIAT | 2017-01-03 | 2017-07-28 | 274 | 229 | 137 | 5 | universe 137 | universe:min_price (2017-07-28) |
| 17 | JPINFRATEC | 2017-01-02 | 2017-07-26 | 230 | 222 | 57 | 6 | universe 57 | universe:min_turnover (2017-03-29) |
| 18 | VAKRANGEE | 2017-01-06 | 2017-12-26 | 218 | 212 | 223 | 18 | vcp_geometry 223 | vcp_geometry:no_base (2017-12-26) |
| 19 | EDELWEISS | 2017-01-09 | 2017-11-02 | 216 | 212 | 186 | 17 | vcp_geometry 147; trend_template 31; dry_up 8 | dry_up:no_volume_dryup (2017-08-02) |
| 20 | IBREALEST | 2017-01-02 | 2017-08-07 | 271 | 211 | 143 | 6 | trend_template 81; vcp_geometry 61; time_compression 1 | time_compression:too_soon_after_low (2017-06-06) |
| 21 | STRTECH | 2017-01-02 | 2017-12-14 | 214 | 207 | 160 | 21 | vcp_geometry 117; universe 37; relative_correction 4 | relative_correction:correction_too_deep_vs_index (2017-09-14) |
| 22 | IFBIND | 2017-01-04 | 2017-12-01 | 229 | 205 | 40 | 18 | universe 32; vcp_geometry 8 | vcp_geometry:no_base (2017-12-01) |
| 23 | VIPIND | 2017-01-02 | 2017-11-28 | 219 | 202 | 206 | 20 | universe 113; vcp_geometry 92; time_compression 1 | time_compression:too_soon_after_low (2017-05-02) |
| 24 | JINDALSTEL | 2017-01-02 | 2017-12-29 | 198 | 198 | 226 | 21 | vcp_geometry 155; trend_template 58; time_compression 13 | time_compression:time_not_compressed (2017-12-18) |
| 25 | RKFORGE | 2017-01-02 | 2017-12-29 | 195 | 195 | 226 | 21 | universe 226 | universe:min_turnover (2017-12-28) |
| 26 | MOTILALOFS | 2017-01-06 | 2017-12-21 | 205 | 192 | 221 | 18 | vcp_geometry 118; universe 65; trend_template 33 | dry_up:no_volume_dryup (2017-08-24) |
| 27 | DELTACORP | 2017-01-02 | 2017-12-26 | 195 | 184 | 224 | 21 | trend_template 120; vcp_geometry 82; rs_rank>=70 15 | relative_correction:correction_too_deep_vs_index (2017-12-05) |
| 28 | JSL | 2017-01-02 | 2017-09-18 | 231 | 180 | 0 | 12 | – | not scanned (regime off / not a member) (–) |
| 29 | KEC | 2017-01-02 | 2017-12-29 | 178 | 178 | 226 | 21 | vcp_geometry 138; universe 63; trend_template 20 | trigger: no break of pivot (2017-05-04) |

**How often each rule was the blocker.**

| rule | stocks blocked at their closest night | advance stock-nights where it was the first block (of 4,698) |
|---|---|---|
| VCP geometry | 13 (12 `no_base`, 1 `depth_ratio_too_wide`) | 2,131 (45%): `no_base` 1,234, `base_too_short` 533, `depth_ratio_too_wide` 166, `too_few_contractions` 107, other 91 |
| universe filters | 5 (`min_turnover` 3, `min_price` 2) | 1,837 (39%): turnover < ₹10 cr 1,549, price < ₹50 288 |
| trend template | 0 | 651 (14%); most often close < SMA50 (186) |
| relative correction | 4 | 13 |
| time compression | 3 | 21 |
| dry-up | 2 | 13 |
| trigger (setup passed, no pivot break) | 2 (DBL, KEC) | 6 setup-passed nights |
| rs_rank | 0 | 26 (< 1%) |
| regime | 0 (17–21 off nights per advance; the year had 22) | – |
| not scanned (JSL: no member night in its advance) | 1 | – |
| breakout volume, chase, slots, cash | 0 | never reached |

**Does the setup describe how these stocks rose?** Mostly no.

- **`no_base` (12 stocks; 26% of all advance nights).** The stock never fell 10% below its 325-session
  high: it went up in a staircase with shallow pullbacks. RAIN, BOMDYEING, AVANTIFEED, KOLTEPATIL,
  MINDAIND, SUNTECK, VAKRANGEE, BBTC, RADICO, IFBIND, IBVENTURES and ITI passed the trend template and RS
  on most member nights, but they never formed a VCP base. **The setup does not describe this kind of
  rise.** No VCP rule change catches it; it needs a trend-continuation setup.
- **Universe, 5 stocks.**
  - GVKPIL, JPINFRATEC and RKFORGE were under ₹10 cr turnover.
  - JPASSOCIAT and RCOM were under ₹50. Both are distressed rebounds, which a leader setup should not
    catch anyway.
  - For the 3 low-turnover stocks it is a **universe** choice, not a setup failure.
- **Near misses, 12 stocks.**
  - **Shape too deep (4).** ADANITRANS, FVIL, STRTECH and DELTACORP failed relative correction: the base
    was deeper than 2× the index's correction.
  - **Timing (3).** IBREALEST and VIPIND were too soon after the low; JINDALSTEL's time was not compressed.
  - **No volume dry-up (2).** EDELWEISS and MOTILALOFS.
  - **No break (2).** DBL and KEC passed the setup but never broke the pivot while the row was live.
  - FRETAIL also stopped at geometry (`depth_ratio_too_wide`).
  - These are the cases a VCP rule change might catch. They are 12 stocks over a whole year.

## Counterfactuals (2017 only, one change each, all diagnostic)

The base for each is the baseline run id. c6/c7 are declared bundles: the owner's single "wide exits"
change touches 3 knobs. Sweeps `y2017-vcp-cf`, `y2017-vcp-max` (m3 `/data/workspace/backtests/sweeps/`,
logs in `/data/workspace/backtests/y2017-vcp/`). The exposure columns are in the run table above.

| run | change | side | result vs v0 (+4.91%, 10 trades, 0.48R, 8.7% invested) | what it shows |
|---|---|---|---|---|
| c1 `01a18fef-…` | risk 2% | risk | **+10.13%**, DD 5.01%, 12.8% invested, avg size 23.4% | sizing works up to p_max; +5.2 pts |
| c2 `01a18ff4-…` | risk 3% | risk | identical to c1 | **p_max 25% binds** on every trade at ≥ 2% |
| c3 `01a18ff8-…` | rs_rank basis all_nse | strategy | +4.84%, 12 trades (adds CADILAHC −0.57R, DALMIABHA +0.53R), 0.40R | RS basis is not the 2017 constraint (RS is the first block on < 1% of the leaders' nights) |
| c4 `01a18ffd-…` | breakout volume off | strategy | **+8.96%**, 13 trades, **0.67R**, DD 3.51%, 11.2% invested | earlier entries on the same names (JUBILANT, TITAN twice, FEDERALBNK); better R and no full-day-volume look-ahead |
| c5 `01a19002-…` | entry at the breakout day close on its known volume (closest knob to T+1) | strategy | **−3.17%**, 4 trades, −0.77R; 5 signals refused `max_chase` | the winners close more than 2% above the pivot; the baseline's edge leans on the intraday fill at the pivot |
| c6 `01a19007-…` | wide exits: SMA50 close, no partial, no breakeven | strategy | +4.56%, 0.44R, DD 5.23%, 13.8% invested | holds longer (19 sessions) but gives gains back; TATAGLOBAL +6.64R, PEL turns −1.14R |
| c7 `01a1900b-…` | wide exits: 20-day swing-low trail | strategy | +3.11%, 0.30R, DD 6.43%, 14.3% invested | same, worse |
| m1 `01a19011-…` | **MAX DEPLOYMENT, several changes**: risk 3%, p_max 50%, 10 positions, rs all_nse, volume off, SMA50 exits | both | **+0.66%, max DD 12.91%, 55.0% invested**, 1.11 positions × 49.5%, zero-position days 26.6%, 11 trades at 0.003R, 4 refused `size_below_min` | cash binds at two positions and the best trades are refused; deployment without more signals is concentration |

T+1 open entry needs code (there is no knob), so it was skipped. c5 is the nearest existing knob. Max
positions 10 and p_max 50% alone at 1% risk were skipped as no-ops (see "What binds").

Audits: every run's audit is `warn`, with nothing failed:

- `one_change`: the declared bundles, and the base run's bundle;
- `concentration`: top-5 trades;
- `data_audit_warn`: digest 739ffb06's known warnings, s1-diag step 5;
- `lookahead_hindsight` on the baseline: the full-day volume;
- `cost_share_high` on m1.

Trials: the family is S1 / NIFTY500_PIT / 2017. It is a new window, so these runs count there and not in
the 2016–2021 family. It is shared with the cheat agent: 20 of 10,000 after m1.

## Files

- **Reusable scripts.** In `/data/workspace/plans/y2017-vcp-work/` (copies on m3 in
  `/data/workspace/backtests/y2017-vcp/`):
  - `y2017_opps.py`: a scan replay that records the first failing rule of every stock-night and every
    watchlist row's break and volume, with adjusted bars to a later date;
  - `opps_report.py`: the top-N performers audit;
  - `y2017_trades.py`: the per-trade table, the exposure identity and the attribution;
  - `summary.py`: the run table with the invested-share identity.

  The scan replay and the exposure identity are worth having in the repo, e.g. as an `opportunities`
  subcommand of `scripts/research/s1_setups_diag.py` and an exposure block in `compare`.
- **Data outputs.** `top30.csv`, `breaks.csv`, `trades_y2017.csv` (same folder).
- **Sweep generators.** `make_cf.py`, `make_max.py`. The run script is
  `/data/workspace/backtests/y2017-vcp/run.sh <sweep_id>` on m3.
