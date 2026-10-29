# Backtest protocol vs code: S1 first (2026-10-25, main @ 675af37b)

This was a read-only audit. Nothing was written to hat_live, the repo or the data root. I ran no backtest and no pipeline. The cheap reads used the strategy's own criteria code (`EvalContext`, `evaluate`, `evaluate_stage`) over the `bars_daily` view (DuckDB, `DataStore.connect(stored_adjustment)`) and the stored `features_daily`, for the 499 current nifty500 members. The scratch scripts are `funnel.py`, `funnel2.py` and `vcpdiag.py` in `/tmp/claude-1000/-data-home/1e9ac391-fb22-4717-bb4b-e2423711eb87/scratchpad/`.

The owner restated the objective: deploy S1 (Minervini) first, with no code or data bugs before backtesting starts. So S1 comes first in every section. S2 to S5 are secondary and only obvious problems are listed for them.

**DB state.** All five strategies have exactly one version: v1, `draft`, created 2026-10-25 06:53. Each stored config is identical to its seed YAML: `config_hash` is equal and the parsed dicts are equal for all five, so **no drift**. Every bot is `research`/`confirm`, with no live version and cluster `momentum-long`. Policy v1 has `base_weight` S1 0.50, S2 0.50, and **S3/S4/S5 0**. The exposure ladder is L1 = 2 positions at ×0.5, L2 = 4, L3 = 6, stepping up after 2 wins and down after 2 losses. `hat_regime_model_version` has **0 rows**. There are no stored backtest runs and the backtests dir is empty.

---

## (A) Claim check

| Claim | Verdict | Actual |
|---|---|---|
| Universe NIFTY 500 + EQ/BE, 20d turnover ≥ ₹10 cr, price ≥ ₹50, stocks only | true (with caveat) | Seeds: `series_in`, `min_turnover{days:20,inr_cr:10}` (`criteria/universe.py:41`, turnover in rupees, checked), `min_price{inr:50}` on the raw close. ETFs/REITs are removed by `isin.ORDINARY_EQUITY` (`data/isin.py:14`); BIRET/EMBASSY (BL) are in the nifty500 list but filtered out. Membership is today's list over the whole period (`universe_from_current_constituents`), which is out of scope here. |
| Bhavcopy daily from 2011 | partial | Bars run from **2011-06-22**. `index_daily` NIFTY 500 runs from **2012-02-21**, so S1's gate is first defined about May 2012 and S5's SMA200 gate about Dec 2012. |
| ISIN-linked | true | 591 linked lineages, all consistent (no bars outside their effective ranges). |
| Split/bonus/rights/demerger adjusted | **partial** | **ADANIENT 2015-06-03 demerger is missing** (−82.8% in the adjusted series; nifty500 member). Ex-date `prev_close` is wrong on split/bonus days (B, D2). |
| Dividends as total return for signals | true | `MarketView.window/bars_through` rescale the TR series (`backtest/data.py:404-471`). Fills and marks use the price basis. |
| Delisted names kept | false in effect | The bars are kept, but the universe is current members only, so a delisted name is never scanned. |
| Entry fill: daily level break, penetration default, touch variant, gap `trigger_is_level_break_only` | true | `fills.entry_fill` (`backtest/fills.py:65`), `--entry-fill`, `spec.KNOWN_GAPS`. |
| Close-phase exits on the official close; expiry/rebalance flagged `auction_risk` | true | `loop._close_phase`, `auction_days.py`, `report.flag_auction_risk`. |
| Costs: 20 bps slippage + versioned statutory charges | partial | `DEFAULT_SLIPPAGE_BPS=20` (`costs.py:50`). There is one `cnc-delivery-1.yaml` (all rates `[OWNER-PENDING]`), applied to every year 2011-2026. Rates are not time-varying. |
| Sizing 0.25% of sleeve equity, S1 cap 20%, 6 positions, ADV 1% | partial | Policy `risk_pct 0.0025`, `p_max` S1 0.20, `adv_cap_pct 0.01`, `max_open_positions 6`. But the **ladder starts at L1: 2 positions at half risk** (`risk/exposure.py:17`), so 6 is reached only after 4 straight wins. |
| Confidence "high" = 30+ trades and positive 90% lower bound | true | `engine/confidence.py:28,123`. |
| Promotion ≥5y, 200 trades, DSR ≥ 0.95, PBO < 0.5 over ≥2 variants, 20 shadow sessions | true | `engine/portfolio/lifecycle.py:42-53`. Ambiguous days ≤10% of held sessions is `MAX_AMBIGUOUS_SHARE` (`:49`). |
| `--regime-mult 1\|policy` | true | `__main__.py:134`. With no stored regime model, `stored_regime_table` falls back to momentum defaults (`regime_service.py:71`). |
| `--ambiguous optimistic\|pessimistic` (10% cap) | true | The CLI flag exists; the cap is a lifecycle gate, not a run option. |
| `--for-promotion` | true, but S3-S5 are refused | Policy base_weight 0 gives `backtest_no_base_weight` (`spec.py:277`). It also requires `--regime-mult policy`. |
| Entry fill touch/penetration switch | true | `--entry-fill`. |
| Slippage 20 vs 50 switch | true | `--slippage-bps N` (any value). |
| save-draft | true | `admin.py:207`. |
| `report_data.REGIME_RULE` per-regime attribution | true | `report_data.py:54`, trades grouped up/not_up by NIFTY500 > SMA200 & rising 20. This is not the strategy's own gate. |
| `LOWER_CIRCUIT_RULE` refusing entries | false | `"carry_to_next_unlocked_open"` (`spec.py:~118`) defers **stops/exits** on a locked-lower day. Entries are refused at the *upper* circuit through `max_chase` and the locked flag. |
| `episodic_pivot_not_backtested`, `single_sleeve_caps` | true | `spec.KNOWN_GAPS`. |
| Rolling 3y CAGR/maxDD at month ends | **missing** | (C) |
| Nifty 500 TRI benchmark | **missing** | The benchmark is the NIFTY 500 price index (`report_data.py:51`). No TRI exists in `index_daily`. |
| Nifty200 Momentum 30 benchmark | **missing** | Neither the index nor the code exists. |
| Cost share of gross profit, exposure | true | `report.py:211,237-242`. |
| Per-year table with best/worst trade | partial | `yearly` has the return and benchmark only. |
| Daily P&L correlation between strategies | **missing** | (C) |
| **S1** hard template (close>SMA150&200, 150>200, SMA200 rising 21, 50>150&200, close>50, ≥30% off low, ≤25% off high, RS ≥70, close ≤ pivot) | true | Seed lines 23-36; `criteria/setup.py:53-157,359`. Correct signs and windows were checked: `sma_sum` offsets, 252-bar 52w on TR highs/lows, ratios as percent. |
| S1 score 0.6, RS w1 (70→95), VCP w2 | true | Score = (1·rs + 2·vcp)/3 (`scoring.py weighted_mean`). |
| VCP 2-6 contractions, each ≤0.75× prior, final ≤10%, 120 lookback | true | `vcp.py:155-170`. The chain is truncated to the first 6 (B, S1-1). |
| VCP "5d vol ≤0.7× 50d avg" | **false** | The dry-up is the **final contraction's mean volume over the mean of the 50 sessions before the base start** (`vcp.py:200,_dryup`). |
| S1 trigger pivot break, max chase 5% | true | Seed; `volume_pace 1.5×` is ignored by the backtest (B, S1-4). |
| S1 stop 0.5% below final contraction low, skip >8% | true | `stops.final_contraction_low` (`stops.py:105`), checked against the entry price. |
| S1 exits hard stop → BE 2R → 33% at 3R → close<SMA50; time stop disabled | true | Seed lines 50-55. |
| S1 regime NIFTY 500 > SMA50, rising 10 | true | `regime_gate.py close_above_sma_and_rising`. The gate is on for 56% of sessions from 2015. |
| S4 criteria (RS ≥80, close>50, 50>200, 50 rising 10, 200 rising 21, pullback 2-10 off 11-session high, vol < 50d mean, low within 1% of rising-5 EMA10/20, close ≤2% under) | true | `criteria/pullback.py`. Note: "within 1%" is only an upper bound; any low below the EMA passes if the close holds −2%. |
| S4 trigger pullback-day high, chase 2%, stop 0.5% under pullback low, max 8%, exits | true | Seed. |
| S4 close-below-EMA exit not built | true | There is no EMA exit in the `ExitRule` union (`strategy/config.py:370`). |
| S5 (close>SMA200, RSI(2)<10, next-day break of signal close, chase 2%, 3×ATR(14), exits SMA5 / 10-session time stop, regime SMA200 rising 21) | true | `criteria/reversion.py` (Wilder RSI). The time stop is `partial_after_days{days:10, sell_fraction:1.0}`: full, fires at `days_held ≥ 10`. |
| "S5 has no stored regime row, sizes under momentum's" | true (stronger) | There is no regime row at all. Every profile falls back to `profile_table({momentum: defaults})`. |
| S2 can't be backtested on daily bars | partial | The `breakout` playbook **is** run (level = consolidation_high, low-of-day stop estimated from adr20, `volume_pace` ignored). `episodic_pivot` is skipped (`Playbook.preopen`). |
| Override paths `setup.criteria[vcp].params...`, `[rs_rank]`, `[ema_pullback]`, `[rsi_below]`, `stop.multiple` | **false** | Tested with `Overrides.apply_config`. `setup.*` gives `backtest_bad_override_path`: the canonical config is `playbooks[default].setup...` and `playbooks[default].stop...`. `criteria[vcp]` gives `backtest_override_no_item`: `_pick` matches `rule`/`name` only, never `type` (`overrides.py:85`). `rs_rank` appears twice in S1 and would be ambiguous anyway. Working forms: `playbooks[default].setup.criteria[11].params.depth_ratio_max`, `playbooks[default].stop.multiple`. |
| `exits[partial_at_r].at_r`, `exits[close_below_sma].sma`, `regime.params.sma`, `exits[trailing_swing_low].lookback_days`, `exits[close_above_sma].sma`, `exits[partial_after_days].days` | true | All parse and apply. |

---

## (B) Defects

### B1. Strategy code: S1 path (data → features → screen → trigger → stop → exits → sizing → ledger)

I verified these as correct, so they don't need to be re-checked. There is no lookahead: the scan uses `prev`'s bars, features and index closes; the entry uses the day's bar; the ADV/ADR/ATR inputs come from `prev`; the allocation is at `prev`'s close equity. SMA definitions, `sma_rising` offsets, 52w windows (252, TR), the rs_pct units (0-100) and RS weights 63/126/189/252 at 0.4/0.2/0.2/0.2 are correct, and turnover is in rupees. The pivot and contraction low are on the same scale as the day's bar: the TR window is rescaled to `prev`, which equals the price basis at `prev`. Entry penetration, gap-over at the open, stop width against the entry, BE/partial bisection on the way up, the close-phase SMA50 on the close, the ladder and dividends in R all behave as written. Features match a recomputation to 4 dp, and bars and features have the same id sets on every date.

| # | Sev | Where | Evidence | Fix |
|---|---|---|---|---|
| S1-1 | **major** | `engine/criteria/vcp.py:114-130` (`contraction_chain`, `len(chain) >= limit`), called with `limit = contractions[1] = 6` at `:279` | The chain is built **from the base start forward** and stops at the 6th contraction, so with more swings the latest ones are ignored. The "final" contraction (the pivot, the final low and the dry-up) can then be months old. 2019-12-31: 121 of 292 member bases have >6 swings. On the sample dates, 33-120 bases have a final contraction ending >20 sessions ago. Such a base either fails (most) or passes on a stale pivot and stop. | Build the full chain, then judge the **last** ≤6 contractions (or walk back from the date). Add a unit test with 8 swings whose last 3 tighten. |
| S1-2 | **major** (fidelity, the #1 cutter) | `vcp.py:98-112` (3-bar strict pivots), `:163` (every consecutive ratio ≤0.75) | Noise wiggles count as contractions and every pair must tighten. `depth_ratio_too_wide` hits 104-372 members per date, and only 3-13 per date would pass on their last 3 contractions alone. Examples of depths: [10.9, 3.7, 21.1, 4.3, 5.2, 12.8], [6.4, 5.0, 7.0, 5.2, 3.7, 6.5]. VCP passes about 0.9 names a day out of about 265 universe names (82 dates). Strict `>` also means flat (tied) highs/lows are never pivots. | Owner decision before tuning: a minimum contraction depth (e.g. ≥3%, or ≥0.5×ADR) or a larger pivot window, so that only significant swings count. Fix S1-1 first, because it changes these numbers. |
| S1-3 | **major** (hidden gate) | `vcp.py:142-152` (`vcp_score`), seed `threshold: 0.6` | Each VCP sub-score is 0 **at** its pass limit, so a pattern that just passes scores about 0.25. With RS at 70 the score is 0, which needs vcp ≥0.9; RS 95 needs vcp ≥0.4. This cuts 48 → 12 (75%) of the rows that pass every hard rule. The doc presents 0.6 as a light filter. | Record it as an owner decision ("parameters later"), but sweep `threshold` (0 / 0.4 / 0.6) as the first variant, not VCP sub-parameters. |
| S1-4 | **major** | `backtest/spec.py:69`; S1 seed trigger `volume_pace{vs_avg50:1.5}` | The backtest takes every pivot break. Live refuses breaks below 1.5× volume pace, so S1's evidence includes trades live won't take. `GAP_PLAYBOOKS` only blocks pre-open playbooks, so promotion is not blocked (A5 F1(b), still open). | Add a daily proxy convention `volume_proxy: breakout-day volume ≥ 1.5×adv50` as a run variant (both runs reported), or a gap that names playbooks with `volume_pace`. |
| S1-5 | minor | `engine/scan.py:247` comment; `data/features.py:248` | rs_pct is ranked across **all ordinary-equity ISINs** (EQ+BE+BZ, about 1,550-1,850, about 20% BE/BZ and many under ₹1 cr). The scan's "ranks are taken within the universe" is true for `momentum_rank` and false for `rs_rank`. Effect: mid-2021 median member rs_pct = 38.5; only 74/392 members are ≥70. | Decide: IBD-style whole-market RS (keep, fix the comment) or rank within EQ + liquid / the universe. |
| S1-6 | minor (policy) | `risk/exposure.py:17,33` | The ladder starts at L1 (2 slots, ×0.5 risk). A BE scratch exits at slightly <0R after slippage and counts as a **loss**, so two scratches step the ladder down. For a rarely trading S1 this keeps it at 2 positions for long stretches, and it is why the BE variants change the trade count (D). | Owner: start the backtest at L3 or count \|R\| < 0.1 as neutral. Report time-at-level per run. |
| S1-7 | minor | `vcp.py:200` | The dry-up baseline is the 50 sessions *before the base start*, which can be 120+ sessions before the date. That is defensible, but the doc says 5d vs 50d. | Document it. Optionally add `dryup_window: final_contraction\|last5`. |
| S1-8 | minor | S1 can't reach the gate | About 50 trades in 10y against `MIN_BACKTEST_TRADES = 200` (`lifecycle.py:43`). S1 at seed values can never be promoted, whatever its edge. | Fix S1-1/S1-2 first, then reassess. |
| OV-1 | **major** (protocol) | `backtest/overrides.py:74-90` | Criteria can't be selected by `type`, and duplicate types (S1's two `rs_rank`) can't be addressed. Index selectors (`criteria[11]`) silently change meaning if the seed order changes. Every doc sweep path on criteria is refused (loudly, not silently). | Let `_pick` match `type` (and `type#n`); fix the protocol's paths to `playbooks[default].setup.criteria[...]` / `playbooks[default].stop...`. |

### B2. Strategy code: secondary (S2-S5), obvious items only

| # | Sev | Where | Evidence | Fix |
|---|---|---|---|---|
| S4-1 | major (owner decision open) | `strategy/config.py:370` exit union | No close-below-EMA exit exists, so S4 exits only via the 10-session swing low or SMA50. | Add `close_below_ema{ema, sell_fraction}` (close phase, `view_from_bars` gives the EMA). |
| S3/S4/S5-1 | major (process) | policy `base_weight` S3-S5 = 0; `spec.py:277` | A research run sizes at 0.5. `--for-promotion` is refused `backtest_no_base_weight`. | Owner sets weights before promotion runs. Research runs are fine. |
| S2-1 | minor | adtr filter | `adtr20` is inflated for 20 sessions after each split/bonus (D2), so S2's `adtr_filter` misjudges those names. | Fixed by D2. |
| S5-1 | info | `exits.py:287`, close phase runs on the entry day | `close_above_sma 5` can exit on the entry day (days_held 0). This matches the rule as written. | Owner: confirm, or add `min_days`. |

No sign errors, percent/fraction mixups, wrong RSI/ATR/EMA definitions or silently ignored YAML keys were found in S3/S4/S5 (pydantic `ParamModel` refuses unknown keys). The `earnings_growth` criterion is disabled in every seed.

### B3. Data

| # | Sev | Where | Evidence | Fix |
|---|---|---|---|---|
| D1 | **blocker** | `hat_corporate_action`, ADANIENT INE423A01024 (nifty500 member) | 2015-06-03 close 637.00 → 109.75 (−82.8%) in the adjusted series. This is the 2015 demerger of Ports/Power/Transmission shares (raw prev_close 637, so NSE didn't adjust). Only a 2015-07-31 dividend is stored. The adjusted series shows a crash, which corrupts SMAs, 52w, RS and a held position's P&L. All other members' moves of ±40% or more with price ≥₹10 (21 cases) are real events (IGL 2012, YESBANK, DHFL-type, COVID, ZEEL, IEX, POLICYBZR 2026-09-24 on 27M volume). | Owner `correct-action`: demerger factor (≈ 109.75/637 adjusted for the day's move, from the NSE CA file) with `known_on`. Then rebuild features. |
| D2 | **major** | `data/store.py:16` docstring and `_ADJ_VIEW_SQL` (`:346-366`), `prev_close * factor-of-its-own-day` | The assumption "NSE's ex-date PREVCLOSE is already adjusted (F14)" is false. On 800 of 1,029 split/bonus ex-dates since 2011-07 (all 438 before 2020), raw prev_close = the previous raw close; only 4 are adjusted. The adjusted prev_close is therefore 1/f too high, which inflates true range, `adtr20` and `adr`-type features for 20 sessions (e.g. MOLDTKPAC adtr20 11.23 → 27.58). S1 doesn't read these. S2's `adtr_filter` and live adtr do. | Adjust the ex-date prev_close by the cumulative factor of the previous day (as for other prices), or derive it from the previous adjusted close. Then `features --full`. |
| D3 | major for promotion runs | `index_daily` NIFTY 500 | It is missing on 30 bar dates: the special sessions plus about 12 regular weekdays (2013-10-09, 2014-03-19, 2014-12-15, 2015-02-02, 2015-03-12/13, 2015-05-19, 2015-07-08, 2015-09-04, 2015-10-16, 2015-12-01, 2016-06-20, 2020-07-13). Under `--regime-mult policy` (required for promotion), `regime.compute_inputs` raises `regime_no_index_today` (`regime.py:113`), so there is no allocation and the next day's entries are all rejected. Under `1`, the SMA window silently skips the day. The 2026-10-24 open-items audit said "5 Saturdays only", which understated it. | Back-fill those index days from the NSE index archive, or ack them and carry the last close in `compute_inputs`. |
| D4 | minor | `hat_instrument` | `delisted_on` is null for all 4,422 rows. 68 ordinary-equity rows are `active=false` with bars to 2026-10-23 (AZADIND INE566M01025, ZETWERK, TONBO…; placeholder names). KALYANI is active with its last bar on 2026-08-28. | Refresh the reference job. Delisting in the backtest relies on `last_traded` only, which is fine. |
| D5 | minor | bars | 53 instruments come back after a gap of more than a year (e.g. 12 on 2026-04-20, last bar 2023-10-25). SMA200, 52w and returns count rows across the hole, so the S1 template is wrong for about a year after the return. | Treat a gap of more than N sessions as a series break in features and criteria (null windows), or `JUMP_SKIP`. |
| D6 | minor | `index_daily` | No NIFTY 500 TRI. VIX starts 2014-05-14 and SMALLCAP 250 starts 2019-01-14. | Ingest TRI for the benchmark. |
| D7 | minor | cost model | A single rate file for 2011-2026. Stamp duty, STT and exchange rates changed over that period. | A dated cost schedule (`cost_models/*` with `effective_from`). |
| D8 | info | `features.py` | high_52w etc. are on the TR basis, below the traded high (ITC 406.57 vs 426.40). S1 reads its own TR history consistently, so there is no defect for S1. | none |

Clean: duplicates 0, bad OHLC/volume 0, calendar matches `hat_trading_calendar` exactly, 2,958 bars and features rows on 2026-10-23 with identical ids. 497/499 nifty500 members have a bar on 2026-10-23; the 2 without are the BL REITs. Previous review: KAUSHALYA is still `review` (open); SHEKHAWATI is stored; GODREJIND bonus is gone; MPS bonuses are kept.

Previous audit A5: F4 (`resolve_level`) and F6 (`single_sleeve_caps`) are fixed. F1 is partly fixed: kind by `Playbook.preopen`, but `volume_pace` playbooks still pass the gate (S1-4). F3 (one identity) and F5 (one regime profile, now `profile_table` fallback) are not re-checked here.

---

## (C) Features the doc assumes that are missing

| Feature | Size |
|---|---|
| Override selector by criterion `type` (and the n-th duplicate) | S (half a day, `overrides._pick` + tests) |
| Daily `volume_pace` proxy convention for S1/S3 | S-M |
| Close-below-EMA exit (S4, owner decision) | S (exit rule + view EMA), M with the live close phase |
| Rolling 3-year CAGR / maxDD at month ends | S (pure, over the equity curve, in `report_data`) |
| Per-year best/worst trade | S |
| Nifty 500 TRI benchmark | M (index ingest + backfill of history; report switch is S) |
| Nifty200 Momentum 30 benchmark | M (same as TRI) |
| Daily P&L correlation between strategies | S-M (read two runs' equity, correlate daily returns; needs runs over one period) |
| Lower-circuit entry refusal | not needed (an entry on a locked-lower day cannot break a level). The doc's claim is wrong, not the code. |
| Dated cost schedule | S-M |
| Multi-sleeve portfolio run (removes `single_sleeve_caps`) | L |

---

## (D) be-off == be-4r: verdict and trace

**Verdict: consistent with the code, not an override or exit bug** (most likely correct). There are no stored runs left to confirm it from the trades.

Trace:
1. Overrides apply. `exits[move_stop_to_breakeven].enabled=false` and `...at_r=4.0` both parse through `set_path` → `parse_config`, and the resulting configs differ (tested). Rule ids are `"{index}:{rule}"` (`exits.py rule_id`), so disabling keeps the indices and neither variant shifts the partial's id.
2. The disabled BE is dropped by `_live_rules` (`exits.py:384`, `if rule.enabled`). The at_r=4 BE is due only when `_reached_r(view, pos, 4)` (`exits.py:373`).
3. In the backtest the BE move happens only on the way up: `_up_leg` → `fillrules.first_trigger` bisects for the first price where `exits.evaluate` acts (`_acts` counts `new_stop`), and moves the stop to `avg_entry` at +4R. The partial at 3R fires first, then BE at 4R. Neither changes anything else.
4. So the two variants can differ only for a trade that reached +4R and later traded back to its entry before a close below SMA50. With about 50 trades (a few reaching 3R, fewer reaching 4R) it is plausible that none did. After a +4R run, SMA50 has usually risen to or above the entry, so the SMA50 close exit sells first. Identical results are therefore expected.
5. Why the base (BE at 2R) differs by one trade: a BE at 2R stops out trades that come back from 2R at about −0.0xR after slippage and charges. `is_win` is `R > 0` (`risk/exposure.py:33`), so these count as **losses** on the exposure ladder (`loop._sync_ladder`, `:944`). Slots free up and ladder levels change, which shifts a later entry: 50 vs 49 trades. That is a policy effect (S1-6), not a bug.

A cheap confirmation on the next real run: list the base run's trades with MFE ≥ 4R whose exit price is ≤ the entry. If there are none, the identity is proven.

---

## (E) S1 trade-count analysis

Method: S1's own `evaluate_stage` on 82 sample dates (the last session of every second month, 2013-03 to 2026-09), all 499 members, the stored features, and the TR bars from the stored adjustment. Plus a criterion-by-criterion pass on 7 dates.

| Stage (mean per sample date) | Names | Cut |
|---|---|---|
| Members with a bar | about 300 (2014) to 497 (2026) | IPOs after the date |
| Universe (turnover ≥ ₹10 cr, price ≥ 50, EQ/BE) | 265 | ₹10 cr removes 131-173 members in 2014-2019, about 15 from 2023 |
| Template + RS ≥70 (hard 0-9) | 53 | RS ≥70 is the biggest template cut. rs_pct is ranked across the whole market, so in 2021 only 74/392 members are ≥70 (S1-5). |
| VCP passes | **0.9** | **about 98% cut**. Reasons per date: `depth_ratio_too_wide` 22-372, `base_too_short` 40-247 (highest close within the last 15 bars, i.e. names at highs), `too_few_contractions` 11-56. Truncation (S1-1) feeds `depth_ratio_too_wide`. |
| All hard pass (incl. close ≤ pivot) | 0.59 | |
| Score ≥ 0.6 | **0.15** | 75% of hard passers cut (S1-3) |
| Regime gate on | 54% of sample dates | NIFTY500 > SMA50 rising 10 |

So about 0.08 publishable rows per session, or about 200 row-days over 2,500 sessions. A setup sits on the list for several days, which gives perhaps 60-100 distinct setups. These are then cut by the break of the pivot, max chase 5%, stop ≤8% (final depth + 0.5% + chase), and the L1 ladder (2 slots). That matches about 50 trades in 10 years.

**The order of the cutters:** VCP structure (S1-1 truncation + S1-2 noise swings) ≫ score threshold (S1-3) > regime gate ≈ RS ≥70 vs the whole market > ₹10 cr turnover (pre-2019) > ladder slots.

I found no sign, unit or off-by-one error in the template criteria, `close_vs_pivot`, the pivot/low levels or the stop. The bug is in the VCP chain (S1-1).

---

## (F) S1 rules as config only

Every path below was tested with `Overrides(sets=...).apply_config(seed S1)`. **OK** means the config parses and the run applies it. In the S1 canonical config, criteria index order is: 0-6 SMA rules, 7 `pct_from_52w_low`, 8 `pct_from_52w_high`, **9 `rs_rank` hard, 10 `rs_rank` score, 11 `vcp`, 12 `close_vs_pivot`**, 13 `earnings_growth`. The entry filter `max_chase` is at index 0. The triggers are 0 `price_breaks_level` and 1 `volume_pace`. Criteria and filters can be addressed by **index only**; a `type` selector is refused (OV-1). Exits can be addressed by `rule`.

| # | Rule | Config only today? | Path / key the code reads | Missing code |
|---|---|---|---|---|
| 1a | Fixed 10% stop | **yes** | `playbooks[default].stop={"rule":"pct_below_entry","pct":10}`. `StopPctBelowEntry.pct` is read by `stops.pct_below_entry` as entry×(1−pct/100), floored to the tick. | none. That rule has no `max_pct` cap, and VCP still gates the setup. |
| 1b | 10% as the max-stop cap | **yes** | `playbooks[default].stop.max_pct=10`. `StopBelowFinalContractionLow.max_pct` is read by `stops.check_width` and gives `stop_too_wide`. Also `buffer_pct`, `min_pct`. | none |
| 2 | Sell 33% at 3R | **yes (seed already)** | `exits[partial_at_r].at_r=3`, `exits[partial_at_r].sell_fraction=0.33`. `ExitPartialAtR.at_r/sell_fraction` are read by `exits._partial_r` and `fraction_qty` (floor of the fraction × the original quantity). | none |
| 3 | No BE; step trail +1R of stop per +1.5R of gain | **no** (BE off: yes) | BE off: `exits[move_stop_to_breakeven].enabled=false`. Only a move to the entry exists (`ExitBreakeven` → `avg_entry`, `exits.py:419-440`). Several BE rules all stop at 0R. | A new live-phase rule, e.g. `ratchet_r{step_r:1.5, lock_r:1.0}`: new stop = entry + (k−1)·lock_r·R at a peak of k·step_r R. It needs a model in `config.py`, a stop function beside `_breakevens`, and `_RULE_PHASE`. `fillrules.first_trigger` stays valid (it is monotone). Size S, about a day with tests; live uses the same `exits.evaluate`. |
| 4a | Close below the 21-day SMA | **yes** | `exits[close_below_sma].sma=21`. `ExitVsSma.sma` is read by `view_from_bars` using `sma` on prior closes plus the close. Optional `start_r`. | none |
| 4b | Close below the 21-day EMA | **no** | `exits[+]={"rule":"close_below_ema",...}` gives `backtest_override_invalid` | `ExitCloseBelowEma{ema}` plus an EMA in `view_from_bars`. The EMA warm-up needs more history (`history_sessions`), and the existing `pullback.ema` can be reused. Size S. This also covers the S4 owner decision. |
| 4c | Under the last swing low | **yes, as the lowest low of N sessions** | `exits[+]={"rule":"trailing_swing_low","lookback_days":N,"sell_fraction":1.0}`. `ExitTrailingSwingLow.lookback_days` gives a close below min(low of the last N sessions before today). It is not a pivot-defined swing low. | A pivot-based swing low (`vcp.pivot_points`) would be a new rule (S). |
| 5a | Max chase 2% above pivot | **yes** | `playbooks[default].entry_filters[0].params.pct=2`. `MaxChaseParams.pct` is read by `trigger.evaluate_entry_filters` and `risk/caps.effective_max_chase_pct`. Measured from the trigger level. | `entry_filters[max_chase]` is refused (OV-1). |
| 5b | Intraday break vs daily close above pivot | **no** | The backtest always fills on an intraday break (`fills.entry_fill`: high ≥ level+tick, or the open on a gap). `trigger[0].params.confirm` (`close`/`high`) parses, but **the backtest ignores it**; it is a live 5-minute-bar rule. | A run convention or param `entry_timing: intraday\|daily_close`. It would fill at the session close (or the next open) when close > pivot, with the stop and chase measured from that price. Size S-M (loop `_entries` and the close-phase ordering). |
| 6 | Breakout-day volume ≥ 1.5× the 50-day average | **no** (`volume_pace` parses but the backtest ignores it, S1-4) | `playbooks[default].trigger[1].params.vs_avg50` is read only live, as intraday pace. | The full day's volume is known only at the close, so testing it on an intraday fill is **lookahead**. The two clean options: (a) with 5b's `daily_close` entry, require `volume_day ≥ vs_avg50 × mean(volume of the 50 sessions before)` and fill at the close or the next open, since both are known at the decision time; (b) use `bars_5m` cumulative volume up to the break bar, where it exists (coverage is partial; the minute history needs checking). Reporting both is best. Size S once 5b exists. |
| 7 | VCP ≥3 contractions, final ≤10% | **yes** | `playbooks[default].setup.criteria[11].params.contractions=[3,6]`, `...params.final_depth_max_pct=10`. Read in `vcp._pattern_fault` (`contractions[0]`, `final_depth_max_pct`). | The upper bound is capped at 6 by `CONTRACTION_CAP` and also truncates the chain (S1-1). |
| 8 | RS off, both gate and score | **yes** | `playbooks[default].setup.criteria[9].enabled=false` and `playbooks[default].setup.criteria[10].enabled=false`. `scoring.evaluate_stage` skips disabled criteria, so the score becomes the VCP score alone (weighted mean over enabled score criteria). | Note: the 0.6 threshold then applies to the VCP score directly. Set `playbooks[default].setup.threshold=...` to taste. |
| 9 | No buys below NIFTY 500 SMA50 | **partial** | `regime.params.sma=50` is OK, but the rule `close_above_sma_and_rising` also needs SMA50 > its value `rising_days` ago. `rising_days=0` is refused (`ge=1`); the loosest setting, `rising_days=1`, still requires a rising SMA. | Allow `rising_days: 0` (or `null`) to mean no slope test in `CloseAboveSma` and `regime_gate.close_above_sma_and_rising`. Size XS. The gate blocks only new entries; the exits are unaffected (`regime_exit` is a separate, disabled rule). |
| 10 | Time stop after 10 sessions with no progress | **yes** | `exits[time_stop].enabled=true`, `exits[time_stop].days=10`, `exits[time_stop].min_r=X`. In `ExitTimeStop` (`exits._time_stop`), **"no progress" means** that at the close phase, with `days_held ≥ days` (sessions since the entry session, which is day 0), the close is below entry + `min_r`·R (initial R). The default `min_r` 0 means the close is below the entry. The seed has `min_r 1`. Alternative: `exits[+]={"rule":"early_failure","days":10,"min_r":0.5}`, where no progress means the **best price since entry** never reached +`min_r` R. | none |
| 11 | Weekly bars | **no** | There is no timeframe concept anywhere. Every window is in daily sessions, and `price_breaks_level.bar` is `Literal["5m"]`. Approximation today (config only): weekly lengths as daily sessions (10/30/40-week MA → `sma_above` 50/150/200, which is what the seed already is; `vcp.lookback_days` up to 252). | True weekly support needs: a `timeframe: daily\|weekly` config field; resampling weekly OHLCV in `MarketView.window` and the live `ScanInputs` (pure, S); deciding whether rs_pct and turnover stay daily features (S); weekly-close exits that run only on the week's last session in the backtest and the live close phase (M); and the trigger can stay daily or intraday. Estimate M-L, about 1-2 weeks including live parity and tests. |

**Parameters hard-coded in Python rather than config** (each changes a strategy's behaviour and is not reachable by `--set`):

- **VCP** (`criteria/vcp.py:45-48`): `PIVOT_WINDOW=3` (the swing definition, main cutter S1-2), `MIN_BASE_BARS=15`, `AVG_VOLUME_DAYS=50` (the dry-up baseline length) and `CONTRACTION_CAP=6` (also the chain truncation, S1-1). The base start rule (the first highest close) is also fixed.
- **52-week window** `WINDOW_52W=252` (`criteria/setup.py`, `pct_from_52w_low/high`).
- **RS** is precomputed in features. Its weights (`data/features.py:80`, 63/126/189/252 at 0.4/0.2/0.2/0.2) and its ranking universe (all ordinary-equity ISINs, `:248`) are code. Only `min_percentile`, `score_from` and `score_full` are config. The same holds for the `mom_rank` windows (`MOM_WINDOWS`).
- **Volume averages:** `trigger.AVG_VOLUME_DAYS=50` (`volume_pace`), `pullback.AVG_DAYS=50`. The EMA and RSI warm-ups (`EMA_WARMUP`, `RSI_WARMUP`) are numerical only.
- **Fill conventions** are run conventions on the CLI, not version config: penetration by 1 tick, the open→low→high→close path, the `pre_break_low` adr20 estimate, `SUSPENSION_SESSIONS=5` and its 5% markdown, `LOOKBACK_SESSIONS=700`, and `INITIAL_EQUITY` 1,000,000.
- **Sizing and the ladder** live in the risk policy (DB), not the version YAML. `--risk-pct` and `--max-positions` override two of them; `p_max`, `adv_cap_pct`, the ladder steps and start level, `max_entries_per_day` and `max_positions_per_industry` cannot be overridden per run. `--cooldown-sessions` and `--sleeve-weight` exist.
- **Report regime attribution** `REGIME_SMA=200` and `REGIME_RISING=20` (`report_data.py:52-53`), and the portfolio regime v1 thresholds (`engine/portfolio/regime.py`).

To make "no code change per backtest" true for S1, the minimum is OV-1 (selector by `type`), new rules for #3 and #4b, `entry_timing` plus a volume proxy for #5b and #6, `rising_days: 0` for #9, and moving the VCP constants (`PIVOT_WINDOW`, `CONTRACTION_CAP`, `MIN_BASE_BARS`, dry-up window) into `VcpParams`. All of these are S-size.
