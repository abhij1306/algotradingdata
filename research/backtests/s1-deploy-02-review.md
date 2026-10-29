# S1 deployment review and sweep s1-deploy-02 (2026-10-27)

Sources: run folders of s1-deploy-01 (deploy 01a17be7, r2 01a17bf0, r5 01a17c04, dry10 01a17c0e, vcploose 01a17c22, …), hat_live SELECT only, the features and index store. No backtest was run. Sweep: `backtests/sweeps/s1-deploy-02.yaml`.

## 1. Diagnosis: why only 35–50% is invested

**Invested share = trade rate × hold × position size.** For deploy: 161 trades × 20.5 sessions mean hold / 1,486 sessions = 2.22 positions on average × ~15% each = 35%. For dry10: 226 × 22.1 / 1,486 = 3.36 positions → 49%. Each of the three terms is low.

- **Caps were never binding after deploy.** Every refusal is `size_zero_cash` at ~100% invested (median cash 0.0%) or `max_positions`. This explains why switching the caps off moved invested share by only 3 points.
- **Signals cluster, so the book swings between full and empty.** In deploy, 38% of sessions have 0 positions (19% in dry10). By year: 2019 was 3.8% invested (9 trades), while 2021 was 77.5% invested with 43% of sessions above 95% invested. Inside the clusters there are more signals than cash: 249 of dry10's 475 signals (52%) were refused. Refused signals did no better than taken trades: 60-session forward R averaged +0.12 to +0.52 against +0.28 to +0.40 realized, and 70% hit their stop. So **"too few signals" is half right.** Signals are scarce outside bull runs and in surplus inside them.
- **Holds are short, and winners are cut.** The median hold is 12 sessions. SMA50 close exits are 52–55% of trades, with a 19–22% win rate. Checked against bars, that exit is sound: of deploy's 65 SMA50 losers, 50 would have hit the initial stop first, so it saves about 0.5R each. **The step trail is the problem.** It moves the stop to 0R at +1.5R and to +1R at +3R. Its 49 exits in dry10 peaked at a median 3.15R but realized a mean of only 1.97R. Held instead to the SMA50 or 20-day swing-low exit, the same trades make **+140R instead of 97R** (deploy: 89R instead of 46R), held 16–22 sessions longer on average.
- **Positions are mid-sized.** At 1% risk and a 6.2% median stop, a position is about 16% of equity (13–14% after cash cuts), so the book is full at about 7 positions. Higher risk alone concentrates the book: r2 averaged 1.87 open positions (deploy 2.22), r3 had a 33% DD, and r5 held one position worth 105% of equity.
- **The universe is narrow exactly when the book is idle.** The ₹10 cr turnover floor keeps 189 of 444 NIFTY 500 members in 2016 and 220 of 455 in 2019, but 377 of 459 in 2021. At ₹3 cr it keeps 300, 333 and 448 respectively: +59% and +51% in the idle years, little change in 2021.
- **The regime gate is not the lever.** 203 of dry10's 288 flat sessions are regime-off, but a NIFTY 500 SMA200 gate would open only 29 of them (+54 gate-on sessions in total). The trend template already empties the watchlist in weak markets, and the owner wants no trades in downtrends.

## 2. Suspected bugs and defects

1. **Crumb positions (sizing gap): `app/hat/risk/sizing.py:101-106`.** There is no minimum quantity or notional. When cash is about zero, the cash term floors to 1–4 shares and the trade opens anyway, e.g. NBCC qty 1 at ₹55 (dry10, 2016-09-06) and CHENNPETRO qty 1 (deploy). Positions under 2% of equity: 20 of 161 trades in deploy, 41 of 226 in dry10, 38 of 99 in r5 (so r5 had 61 real trades).
   - They inflate `trades`, which feeds the trades_min of 100.
   - They distort expectancy: dry10 is +0.33R overall but +0.51R without them. KPIT's +7.1R, which earned ₹59, is dry10's #4 trade by R.
   - They block slots: all 59 `max_positions` refusals in dry10 (207 in vcploose) happened with about 3 crumbs open.
   - Live trading would send 1-share orders.
   - Suggested fix: refuse an entry below a floor (for example under half the risk-sized quantity) as `size_zero_cash`.
2. **`min_depth_pct` does exist** (`engine/criteria/vcp.py:70`, since #266), and `apply_config` accepts it. The handoff's "no such VCP param" was wrong, so vcploose ran without it. `parse_variants` does not check parameter names; validate new sweeps with `Overrides.apply_config` as well.
3. **Cash accounting is clean.** Across all 10 runs (14,860 rows), equity = cash + positions, cash is never negative, and invested_pct is consistent. Backtest health is fixed at 1 (`backtest/loop.py:363`), so drawdown bands do not shrink size.

## 3. The 5 variants (all on dry10 run 01a17c0e: np sets + dry-up 1.0, flat ladder, caps off)

| # | Label (base) | Exact change | Tests | Expected invested / CAGR / max DD |
|---|---|---|---|---|
| 1 | `ride` (dry10 run) | `exits[step_trail].enabled=false` | Riding winners: the +43R step-trail giveback | 49% → ~55% / 14.4% → ~16–18% / ~24–28%; top-5 share rises |
| 2 | `ride_tv3` (ride) | `universe[min_turnover].params.inr_cr=3` | More names in the idle years (2016, 2018–20) | ~60%, trades +20–30% / flat to +2 pts / similar |
| 3 | `ride_r15` (ride, bundle) | `risk_pct: 0.015` + `policy_set p_max.stage2-contraction-breakout=0.25` | Larger positions on part-full days; p_max 0.25 guards against one-name books | ~65% / ~18–22% / ~30–35%; fewer trades |
| 4 | `ride_r15_tv3` (ride_r15) | + `inr_cr=3` | Maximum-deployment candidate | ~70%+ / ~18–22% / ~30–35% |
| 5 | `ride_r15_tv3_vol` (ride_r15_tv3) | + `regime_mult: policy` (1/0.75/0.5/0.25 × 1.5%) | Full risk in healthy markets, cut in corrections (volsize had the best MAR in deploy-01: 0.64, DD 12.9%) | ~55–60% / similar to #4 / ~22–26%; best MAR expected |

All except #3 differ from their base in exactly one knob; #3 is a declared bundle. Validated with `parse_variants`, `check_one_change`, and `apply_config`/`apply_policy` on dry10's config and policy. `ride` against the dry10 run changes only `set:exits[1].enabled`. Trials after this round: 28/30.

## 4. Structurally wrong with the strategy or the criteria

- **Longest DD below 500 sessions is out of reach for any S1 parameter.** All 10 runs share the same window, starting 2018-01-23/25 and ending 2021-01 to 2021-05 (728–815 sessions). The benchmark's own longest DD is 302 sessions, and it gained 25.4% in that window. Meanwhile S1 was idle (deploy: 57% of sessions flat, 18.6% invested) or losing (dry10: -3.8% at 31.5% invested). The 2018 peak was set by an outlier: VAKRANGEE 2017, +44.9R and ₹5.1L, 41% of dry10's P&L. The fix sits at portfolio level (an idle-cash sleeve or S2), or the criterion should be judged on the combined book.
- **CAGR vs a 100%-invested TRI with 0% yield on idle cash** (the backtest models none). At 49% invested, S1 needs about 30% on deployed capital just to tie. Model a cash yield (~6% would add ~3 pts), or judge S1 on return on deployed capital plus invested share.
- **`cagr_ex_top5 ≥ 0.5×CAGR` contradicts "ride winners".** With a 26–29% win rate, wins average 2.9–3.5R against losses of -0.7R. The right tail is the strategy, all 23 runs fail this test, and variant 1 will fail it harder. Suggested replacements: CAGR ex top-5 > 0, top-5 share < 100%, or a trade bootstrap.
- **The budget cannot fit a plateau check.** A plateau needs about 10 runs, and only 2 trials remain after this round. Also, the plateau list in the criteria block names np's knobs (`exits.2` is `partial_at_r`, not the step trail at `exits.1`). This needs an owner decision before promotion.
- **Later levers, not this round:** RS rank is disabled (criteria 9 and 10; Minervini requires RS ≥ 70). `close_vs_pivot max_above_pct 0` drops the 37% of VCP passes that complete above the pivot. `min_base_bars 15` causes 66% of VCP failures.

## 5. s1-deploy-02 results (run 2026-10-27, main fb83fe45, 2% position floor active)

| Variant | Run | Trades | Exp R | CAGR % | Max DD % | MAR | DSR | PBO | Inv % | CAGR ex5 % | Top-5 share % | Longest DD | size_below_min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ride | 01a17ca4 | 172 | 0.588 | 15.8 | 24.1 | 0.653 | 0.395 | 0.600 | 51.7 | 4.62 | 77.9 | 752 | 209 |
| ride_tv3 | 01a17cae | 214 | 0.499 | 14.7 | 25.6 | 0.574 | 0.267 | 0.629 | 58.0 | 3.72 | 80.8 | 754 | 216 |
| ride_r15 | 01a17cba | 152 | 0.610 | 14.5 | 25.7 | 0.565 | 0.248 | 0.614 | 55.6 | 1.53 | 92.4 | 752 | 255 |
| ride_r15_tv3 | 01a17cc4 | 177 | 0.500 | 14.1 | 29.2 | 0.484 | 0.197 | 0.614 | 61.1 | -0.37 | 101.8 | 754 | 249 |
| ride_r15_tv3_vol | 01a17cd0 | 228 | 0.464 | 10.8 | 27.9 | 0.388 | 0.145 | 0.614 | 50.1 | 0.42 | 97.0 | 773 | 99 |
| ref dry10 (pre-floor) | 01a17c0e | 226 | 0.334 | 14.4 | 23.8 | 0.605 | 0.363 | 0.571 | 48.9 | 2.58 | 86.7 | 751 | n/a |
| ref np (pre-floor) | 01a17833 | 144 | 0.383 | 9.23 | 16.5 | 0.559 | 0.002 | - | 33.7 | 3.29 | 69.3 | 740 | n/a |

Criteria (benchmark TRI 15.7%): `ride` passes MAR, trades, CAGR > benchmark (15.8, by 0.1 pt), ADV, binding; it fails longest DD < 500 and CAGR ex top-5 ≥ 0.5×CAGR. The other four fail MAR and CAGR vs the benchmark as well. Every run fails overall.

Audits: all 5 are `warn` with no FAIL. The warnings are top5_concentrated (all), data_audit_warn (bars_5m/industries/golden, the known data-audit warnings, also on the references), binding one_change on ride_r15 (a declared bundle, expected), and edge_in_top5 on ride_r15_tv3 (CAGR ex top-5 < 0).

Reading: turning off the step trail helped. Expectancy rose from 0.33R to 0.59R and CAGR from 14.4% to 15.8% with DD about flat (part of the R gain is the floor removing crumbs: dry10 ex-crumbs was about 0.51R). The raised_stop exits (49 in dry10) are gone, and IEX (+₹1.9L) and BALAMINES moved into the top 5. The ₹3 cr floor and the 1.5% risk raised invested share (52 → 58/56/61%) but lowered CAGR and MAR every time: the added names and the larger positions add trades of lower quality and deepen DD. Regime sizing cut both return and invested share. With 200–255 `size_below_min` refusals per run, the book is often full or nearly so. Next round: keep `ride` as the base. Test exits that ride winners further (SMA50 → SMA20/close-below-10w variants, or a wider swing-low lookback), slot and position-count levers (max_positions, min floor 2% vs 3%) instead of more risk per trade, and resolve the longest-DD and ex-top-5 criteria with the owner, since no S1 knob moves them.
