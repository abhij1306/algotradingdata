# 2017 vs NIFTY: the cheat setup (Setup 2) alone — why it can't beat the index

Owner task of 2026-10-31 (with the invested-share addendum). Window 2017-01-01..2017-12-31 with the
loader's normal warm-up, NIFTY500_PIT, main `bd503e9` on m3, read-only DB,
`HAT_DATA_ROOT=/data/workspace/hat-data-isin`, criteria `s1-minervini.md`. Every run is a
**diagnostic** run, not a candidate. Data snapshot `06c21c0d…` in every run; every run's audit is
`warn` (the same data-audit warnings as the 6-year runs). Nothing after 2021 was run or read
(the post-exit moves read bars up to 2018-04-30).

Benchmark: NIFTY 500 TRI **+37.65%** for 2017 (owner figure; the runs' own `benchmark_cagr_pct`
says 37.93% on their base date). NIFTY 500 price index: 6,982.80 → 9,490.65 (+35.9%).

## Verdict

**Invested share is the whole story, and the strategy causes it, not the risk settings.**

1. **The baseline was invested 4.9% on average and held nothing on 74.6% of days** (baseline
   `01a18fe8-71e7-757d-8309-6aa9e0f15f44`). The identity:
   **0.347 average open positions × 14.1% per position = 4.9% invested.** Positions are not the
   main problem (14% each); **there are too few of them**. 3 trades × 28.7 sessions average hold
   ÷ 248 sessions = 0.347 positions on an average day.
2. **The money that was invested beat the index by a wide margin.** It returned +6.40% on 4.9%
   average deployment, about 130% a year on the capital at work. Split of the −31.25 pp gap
   (6.40 − 37.65):
   - **idle cash: −35.80 pp** ((1 − 0.049) × 37.65);
   - **selection on the invested 4.9%: +4.55 pp** (0.049 × (130.6 − 37.65)).
   More than all of the gap is exposure.
3. **Risk management can close at most about 60% of the gap, and only by concentrating.** The
   stacked "max deployment" run c9 (`01a1900a-c3a4-72f5-bd33-499a7a5cb428`: risk 3%, p_max 50%,
   10 positions, RS all_nse) returns **+25.82%** with max DD 2.52%, still 11.8 pp below the TRI,
   and invests **17.8% on average**. The identity: **0.46 positions × 38.7% per position.**
   Nothing held on 63.3% of days.
   - Bigger sizing alone is capped: at 2% or 3% risk p_max 25% binds, and c1 and c2 are
     identical (+8.51%, 7.05% invested).
   - p_max 50% alone (c3) and 10 positions alone (c4) change nothing. At 1% risk no position
     reaches 25%, at most 2 positions were ever open, and cash never fell below 61.9% of equity.
4. **Share of the gap:**
   - **risk/sizing ≈ 53%** (16.6 pp: c9 − c5, the sizing part of c9);
   - **strategy ≈ 47%** (14.6 pp: 2.8 pp of signals that RS all_nse recovers, c5 − c0, plus the
     11.8 pp c9 still misses). That 11.8 pp is no signal on 63% of days and exits that sell
     winners early.

   Sizing is the cheaper half to close, but it is concentration (48–50% per position), not
   diversification. Only the strategy side can raise the *number* of positions.
5. **The edge in 2017 is thinner than 2.07R suggests.** 2017 has only daily bars, so entries use
   the daily estimate. The best trade, BALKRISIND 2017-01-27, traded to 605 above the 589.80
   pivot but **closed at 567.33, below it**. The 5-minute `confirm: close` cannot be checked on a
   daily bar, so the estimate took it. Entering at the day's close with that day's volume (c8,
   `01a19007-5266-719f-ae80-0ab53923a820`, no look-ahead):
   - BALKRISIND drops out (no close above the pivot);
   - MANAPPURAM is refused by max_chase (closed 3.2% above the pivot);
   - the year is **1 trade at −0.38%**.

   Two of the three 2017 entries depend on the daily estimate and the full-day-volume look-ahead.
6. **Exits leave a lot.** The 3 baseline trades realised 6.23R of 10.63R MFE. Held to the year's
   close at the baseline sizes, the same 3 positions would have made about **+30.7%** of equity:
   - BALKRISIND +102.0% × 16.1%;
   - MANAPPURAM +51.3% × 21.5%;
   - ADANIENT +19.5% × 16.5%.

   That is hindsight, not a rule, but it shows where the year's return was. The wide-exit run
   (c7, SMA50, no partial, no breakeven) held BALKRISIND to 27 July (+5.48R) and nearly tripled
   the invested share (13.8%). The return stayed the same (+6.36%): MANAPPURAM lost its 3R
   partial and ADANIENT took a full stop.

**Can the cheat alone be invested 60–90% in 2017? No.** By the identity:

| per-position size | open positions needed for 60–90% | trades a year at the current 28.7-session hold | 2017 actual |
|---|---|---|---|
| 14% (1% risk, ~6% stop) | 4.3–6.4 | 37–55 | 3 |
| 25% (p_max, risk ≥ 1.6%) | 2.4–3.6 | 21–31 | 3 |
| ~48% (c9: 3% risk, p_max 50%) | 1.25–1.9 | 11–16 (or 2 positions held ~all year) | 4 |

The cheat's geometry passed on only 21 stock-nights, in 7 stocks, in all of 2017 (funnel below).
It needs a 15–50% cup within 325 sessions and a 5–15-session pause of ≤6% range in the cup's
middle third. In a one-way bull year the leaders don't build that. Of the 30 best 2017
performers, 13 never formed a cup and 7 had a cup but no qualifying pause. Exposure of 60–90%
needs **other scanners feeding the same portfolio**: VCP, power play, primary base, EP, and
probably a trend-continuation entry for stocks already at highs. It also needs exits that hold
winners for months. A setup that fires 3–4 times a year can fill the book only at 50% sizes held
all year, which is a concentration bet, not a system.

**Next 3 changes to test across all six years** (2016–2021, in-sample):
1. **The setups together in one portfolio at a larger size**: r3's five setups (or more
   scanners) with risk 2% and p_max 25–33%. Report invested %, positions and size by year. This
   is the only lever that raises *positions*, which is the binding factor.
2. **Wide exits** (SMA50 close or a 20-day swing-low trail, no partial, no breakeven) on the
   combined portfolio. In 2017 it doubled holding time and invested share at no cost to return,
   and after their exits BALKRISIND (SMA20) ran +23% and c6's EDELWEISS (SMA20) and PEL (stop) +61% and +42% within 60 sessions.
3. **RS basis all_nse.** Its one extra 2017 trade was a winner (VGUARD +2.56R). Test it together
   with a **close-confirmed entry**, which needs code: T+1 open, or the daily estimate requiring
   close ≥ pivot. That shows how much of the edge survives without the daily-bar estimate.

## 1. Baseline run (c0)

Run **`01a18fe8-71e7-757d-8309-6aa9e0f15f44`**: the r2a variant (`01a18d6a-0a6c-7770-9b29-d51b6331041e`)
on the 2017 window, nothing else changed (sweep `y2017-cheat-base`). 3 trades (all `cheat_3c`),
66.7% win, expectancy **2.073R**, **+6.40%**, max DD 0.84%, invested **4.90%**, 0.347 average
open positions. It has the same 3 entries as r2a's 2017.

### Trades (one row per trade; partial legs joined)

Size = qty × entry ÷ equity before entry. R = net P&L ÷ (qty × risk per share). The post-exit
moves run from the last leg's exit price on adjusted closes (20/60 sessions), plus the highest
high within 60 sessions.

| # | symbol | entry | entry ₹ | exit (last leg) | exit ₹ (legs) | stop % | size % equity | R | MFE R | MAE R | exit reason | P&L % equity | +20 sess | +60 sess | max high 60 sess |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | BALKRISIND | 2017-01-27 | 591.03 | 2017-04-07 | 703.14 / 695.61 | 6.21 | 16.1 | 2.85 | 3.93 | −0.89 | partial 3R / sma20_close | +2.93 | +10.5% | +23.2% | +24.5% |
| 2 | MANAPPURAM | 2017-02-01 | 81.57 | 2017-03-07 | 93.28 / 98.05 | 4.67 | 21.5 | 3.57 | 6.11 | −0.81 | partial 3R / sma20_close | +3.69 | −3.8% | −6.4% | +8.1% |
| 3 | ADANIENT | 2017-07-12 | 84.29 | 2017-08-03 | 83.23 | 6.05 | 16.5 | −0.19 | 0.59 | −0.72 | sma20_close | −0.21 | −4.9% | −3.2% | +2.7% |

Signals 2017-01-25, 2017-01-31 and 2017-07-11. Hold 47, 23 and 16 sessions. No refusals: slots,
cash and risk gates blocked nothing. The Phase 3 audit (`s1-setups-p3-report.md`) flags 2 of
these as chart mismatches: CT04 BALKRISIND (right side 3.8% above the pivot) and CT06 ADANIENT
(spike H0). In 2017 the "mismatched" BALKRISIND was the best trade and ADANIENT the one loser,
so fixing the nearer-resistance rule would not have helped this year.

### Daily exposure, by month (c0; daily rows in the run's `equity.csv`)

| month | avg invested % | avg open positions | avg cash % | equity at month end ₹ | regime-off days |
|---|---|---|---|---|---|
| 2017-01 | 2.2 | 0.14 | 97.8 | 991,622 | 4 |
| 2017-02 | 28.9 | 2.00 | 71.1 | 1,052,069 | 0 |
| 2017-03 | 14.9 | 1.18 | 85.1 | 1,065,954 | 0 |
| 2017-04 | 1.5 | 0.17 | 98.5 | 1,066,173 | 0 |
| 2017-05 | 0.0 | 0.00 | 100.0 | 1,066,173 | 0 |
| 2017-06 | 0.0 | 0.00 | 100.0 | 1,066,173 | 3 |
| 2017-07 | 11.1 | 0.67 | 88.9 | 1,064,791 | 0 |
| 2017-08 | 1.6 | 0.10 | 98.4 | 1,064,035 | 6 |
| 2017-09 | 0.0 | 0.00 | 100.0 | 1,064,035 | 4 |
| 2017-10 | 0.0 | 0.00 | 100.0 | 1,064,035 | 4 |
| 2017-11 | 0.0 | 0.00 | 100.0 | 1,064,035 | 0 |
| 2017-12 | 0.0 | 0.00 | 100.0 | 1,064,035 | 1 |

Max invested 38.1%, max open positions 2, minimum cash 61.9%. Seven of twelve months held
nothing at all.

## 2. Return attribution against +37.65% (c0, `01a18fe8…`)

| component | arithmetic | effect |
|---|---|---|
| **Exposure** | avg invested 4.90%; position on 63 of 248 days; 74.6% of days flat. Idle cash vs TRI: (1 − 0.049) × 37.65 | **−35.80 pp** |
| **Selection on invested capital** | 6.40 ÷ 0.049 ≈ 130.6%/yr on capital at work; 0.049 × (130.6 − 37.65) | **+4.55 pp** |
| total | 6.40 − 37.65 | −31.25 pp |

The exposure decomposed (identity): **invested % = avg open positions × avg position size =
0.347 × 14.14% = 4.90%.**

- **Positions (the binding factor):** 3 trades × 28.7 average sessions held ÷ 248 sessions =
  0.347.
- **Sizing:** 1% risk ÷ stop d% = size. The stops were 6.21%, 4.67% and 6.05%, giving 16.1%,
  21.4% and 16.5% (risk 1.03–1.04% of equity: the fill sits a tick above the planned level).
  p_max 25% never bound at 1% risk; it binds once risk > ~1.6% at a 6.2% stop.
- **Number of trades:** 3. **Edge per trade:** 2.07R. 3 trades × 2.07R × ~1.03% ≈ **+6.4%**.
  Beating the TRI at 1% risk takes ~37R a year: 18 trades at this year's 2.07R, or ~104 at
  r2a's 6-year 0.363R.
- **Exits:** realised 6.23R of 10.63R MFE (59%). BALKRISIND rose a further +23.2% in the 60
  sessions after exit, and +71% from the exit to the year's close (695.61 → 1,194.15).
  MANAPPURAM and ADANIENT exits were good (−6.4% and −3.2% at 60 sessions). Held to the year's
  close at the same sizes, the three positions give 16.1% × 102.0% + 21.5% × 51.3% + 16.5% ×
  19.5% ≈ **+30.7%** of equity (hindsight bound, not a rule).

**"One good trade."** By equity the best trade was MANAPPURAM: the stock made +17.3% on the
average exit (+20.2% on the second leg) on a 21.5% position, which is **+3.69% of equity**.
BALKRISIND's stock went +102% from the entry to the year's close (its 2017 run-up was +135.6%)
but added only +2.93% of equity: a 16.1% position, sold by April. For one trade to beat +37.65%,
the stock must gain 37.65 ÷ size:

| position size | stock gain needed | 2017 PIT NIFTY 500 members (of 553) with a bigger 2017 return |
|---|---|---|
| 16% (1% risk, 6.2% stop) | +235% | 12 |
| 25% (p_max) | +151% | 35 |
| 50% | +75% | 124 |

Even one good trade beats NIFTY only at ≥ ~40–50% of equity in one stock, held for most of the
year. BALKRISIND held to the year's close at c9's 48.3% size is +49% of equity alone. The setup
found that stock but sized it at 16% and sold it in April.

## 3. Opportunity audit: the 30 best 2017 performers

Scan replay of the c0 config over 2017 with the regime gate recorded but forced on
(`y2017-cheat-work/y2017_funnel.py`). It writes every evaluated stock-night with the gate it
stopped at. Its regime-on funnel matches the runs' `run.json` funnel exactly (113,216 evaluated →
21 setups). The breaks are decided as the daily estimate decides them: high > pivot, then full-day
volume ≥ 1.5× ADV50, then a 2% chase. The move is the year's biggest advance: the highest close
÷ the lowest low before it, on adjusted bars. The "advance" nights are those from that low to that
peak. The blocker is the furthest gate the stock reached on any advance night (its closest
nights), with the reasons there. Universe = point-in-time NIFTY 500 members (553 in 2017).

| # | symbol | member days | run-up % | low → peak | 2017 % | advance nights (regime off) | blocker (furthest gate) | reasons at that gate | gate mix over the advance | does the cheat describe the rise? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | IBVENTURES | 63 | 1412 | 01-31 → 11-03 | 1185 | 25 (5) | cup | no_cup 18, cup_too_short 7 | cup 25 | no: straight-line trend, no base |
| 2 | RAIN | 248 | 640 | 01-06 → 11-13 | 574 | 211 (17) | pause | no_pause 5 | cup 156; universe 32; trend 18; pause 5 | no: cups formed but no tight pause |
| 3 | BOMDYEING | 248 | 511 | 01-02 → 12-21 | 470 | 243 (21) | pause | no_pause 14 | cup 131; universe 52; trend 46; pause 14 | no: loose pullbacks |
| 4 | AVANTIFEED | 248 | 497 | 01-02 → 11-10 | 417 | 214 (20) | cup | no_cup 120, too_short 2 | cup 122; universe 92 | no: at highs, no base ≥15% |
| 5 | FRETAIL | 154 | 411 | 01-02 → 11-24 | 301 | 154 (17) | cup | too_short 18, no_cup 14 | rs_rank 117; cup 32; trend 5 | no: new listing (RS no data/low), no base |
| 6 | DBL | 187 | 361 | 01-09 → 12-26 | 334 | 185 (18) | cup | no_cup 80, too_short 9 | cup 89; rs_rank 76; universe 17 | no: trend without a base |
| 7 | KOLTEPATIL | 248 | 353 | 01-02 → 11-28 | 267 | 226 (20) | cup | no_cup 70, too_short 6, too_deep 4 | universe 146; cup 80 | no; also turnover filter |
| 8 | MINDAIND | 187 | 342 | 01-02 → 12-22 | 309 | 184 (18) | cup | no_cup 47, too_short 10 | universe 127; cup 57 | no; also turnover filter |
| 9 | ADANITRANS | 248 | 319 | 01-02 → 12-22 | 293 | 244 (21) | pause | no_pause 1 | cup 118; universe 109; trend 16; pause 1 | no |
| 10 | FVIL | 248 | 297 | 01-02 → 12-26 | 278 | 245 (21) | pause | no_pause 9, low_too_recent 2 | universe 165; cup 46; trend 23; pause 11 | mostly a filter case |
| 11 | ITI | 63 | 296 | 02-27 → 10-26 | 181 | 19 (5) | cup | no_cup 16, too_short 3 | cup 19 | no |
| 12 | SUNTECK | 248 | 288 | 01-02 → 12-22 | 274 | 244 (21) | cup | no_cup 50, too_short 6 | universe 188; cup 56 | no; mostly turnover filter |
| 13 | RCOM | 248 | 277 | 11-15 → 12-29 | 4 | 31 (1) | universe | price_below_min 31 | universe 31 | no: penny squeeze |
| 14 | JPASSOCIAT | 248 | 274 | 01-03 → 07-28 | 213 | 142 (5) | universe | price_below_min 142 | universe 142 | no: penny stock |
| 15 | GVKPIL | 248 | 274 | 05-25 → 10-31 | 236 | 109 (17) | universe | turnover 66, price 43 | universe 109 | no: penny stock |
| 16 | IBREALEST | 248 | 271 | 01-02 → 08-07 | 195 | 149 (6) | cup | no_cup 53, too_short 27 | cup 80; rs_rank 53; trend 16 | no |
| 17 | ITDC | 63 | 252 | 01-02 → 04-24 | 137 | 0 | not a member during the advance | – | – | n/a |
| 18 | BBTC | 248 | 234 | 01-02 → 10-18 | 225 | 198 (20) | cup | no_cup 104 | cup 104; universe 80; trend 14 | no |
| 19 | JSL | 63 | 231 | 01-02 → 09-18 | 169 | 0 | not a member during the advance | – | – | n/a |
| 20 | JPINFRATEC | 61 | 230 | 01-02 → 07-26 | 215 | 60 (3) | universe | turnover 60 | universe 60 | n/a (filter) |
| 21 | IFBIND | 63 | 229 | 01-04 → 12-01 | 203 | 45 (5) | cup | no_cup 8 | universe 37; cup 8 | no |
| 22 | VIPIND | 248 | 219 | 01-02 → 11-28 | 197 | 226 (20) | cup | no_cup 90, too_short 12 | universe 124; cup 102 | no |
| 23 | VAKRANGEE | 248 | 218 | 01-06 → 12-26 | 206 | 241 (18) | cup | no_cup 241 | cup 241 | no: never 15% off its high |
| 24 | EDELWEISS | 248 | 216 | 01-09 → 11-02 | 201 | 203 (17) | breakout_volume | 4 breaks, vr 0.58–1.29 | cup 172; pause 20; trend 10; passed 1 | **yes**, in January; refused on volume |
| 25 | STRTECH | 187 | 214 | 01-02 → 12-14 | 204 | 178 (18) | pause | no_pause 3 | cup 129; universe 40; trend 6; pause 3 | no |
| 26 | FLFL | 124 | 213 | 01-02 → 09-11 | 158 | 60 (3) | universe | turnover 60 | universe 60 | n/a (filter) |
| 27 | MOTILALOFS | 248 | 205 | 01-06 → 12-21 | 185 | 239 (18) | pause | no_pause 26, upper_third 3 | cup 99; universe 66; trend 45; pause 29 | partly: cups formed, pauses too loose |
| 28 | HFCL | 248 | 203 | 06-30 → 09-18 | 122 | 55 (6) | universe | price 35, turnover 20 | universe 55 | no: penny stock |
| 29 | JINDALSTEL | 248 | 198 | 01-02 → 12-29 | 191 | 247 (21) | pause | no_pause 10, upper_third 3 | cup 143; trend 71; rs 20; pause 13 | partly |
| 30 | RKFORGE | 248 | 195 | 01-02 → 12-29 | 187 | 247 (21) | universe | turnover_below_min 247 | universe 247 | n/a (₹10 cr turnover floor all year) |

**Blocker counts (the stock's furthest gate):** cup 13, pause 7, universe filters 7 (turnover
₹10 cr: 4; min price: 3 penny stocks), not a member during the advance 2, breakout volume 1. The
cheat fired for **none** of the 30. Regime, chase, slots and cash blocked none of them. By
stock-night over the advances: cup 2,009, universe 1,979, trend template 273, RS 266, pause 96,
passed 1. In 24 of the 28 member cases the setup simply doesn't describe the rise. These stocks
went up without a 15–50% cup followed by a tight middle-third pause; most never fell 15% from a
high during the year. EDELWEISS is the one stock the cheat described (January 2017). The full
output is in `y2017-cheat-work/opp.out`.

**The whole 2017 cheat funnel** (regime-on nights, stock-nights passing each gate; the replay and
`run.json` agree):

evaluated 113,216 → universe 57,908 → trend template 36,456 → RS ≥70 (eligible) 14,790 →
**cup 1,064** → **pause 53** → dry-up 28 → close vs pivot 28 → stop cap 28 → overhead supply 21 →
watchlist 21 (7 stocks: BALKRISIND, MANAPPURAM, ADANIENT, EDELWEISS, PEL, GNFC, SWANENERGY) →
16 level breaks → 3 pass the breakout volume → 3 trades.

The cup gate removes 93% of what RS lets through, and the pause removes 95% of the rest. The
universe filters (mostly the ₹10 cr turnover floor, then min price) remove 49% of member-nights before any setup rule. 22 nights were
regime-off (4 in Jan, 3 Jun, 6 Aug, 4 Sep, 4 Oct, 1 Dec); no setup-passing night fell on one.

## 4. Counterfactuals (diagnostic; one change each against c0 except c9)

Sweep `y2017-cheat-cf` (variants `/data/workspace/backtests/sweeps/y2017-cheat-cf.yaml` on m3,
generator `y2017-cheat-work/make_cf.py`). Avg size = invested ÷ open positions (the identity),
and "flat days" = share of days with zero positions.

| run | change | run_id | return % | vs TRI pp | max DD % | trades | exp R | **avg invested %** | **avg open pos** | **avg size %** | **flat days %** | what binds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c0 | baseline | `01a18fe8-71e7-757d-8309-6aa9e0f15f44` | 6.40 | −31.25 | 0.84 | 3 | 2.073 | **4.90** | 0.347 | 14.1 | 74.6 | signal count |
| c1 | risk 2% (risk) | `01a18fed-7bd8-7794-aeac-eb1a78eea1b3` | 8.51 | −29.14 | 1.30 | 3 | 2.074 | 7.05 | 0.347 | 20.3 | 74.6 | p_max 25% (all 3 at 25.0%) |
| c2 | risk 3% (risk) | `01a18ff1-b89c-71a1-90b6-47e59bff2a8a` | 8.51 | −29.14 | 1.30 | 3 | 2.074 | 7.05 | 0.347 | 20.3 | 74.6 | p_max 25%: identical to c1 |
| c3 | p_max 50% (risk) | `01a18ff4-c6ff-7027-b7d2-ebe76f8bc304` | 6.40 | −31.25 | 0.84 | 3 | 2.073 | 4.90 | 0.347 | 14.1 | 74.6 | nothing: 1% risk never reaches 25% |
| c4 | max positions 10 (risk) | `01a18ff7-da3c-70ca-bdf8-d853fea64d04` | 6.40 | −31.25 | 0.84 | 3 | 2.073 | 4.90 | 0.347 | 14.1 | 74.6 | nothing: max 2 open |
| c5 | RS basis all_nse (strategy) | `01a18ffb-9e1b-7515-9b16-f384414e9746` | 9.21 | −28.44 | 0.84 | 4 | 2.194 | 6.46 | 0.460 | 14.1 | 63.3 | signal count (+VGUARD 2017-10-24, +2.56R) |
| c6 | breakout volume off (strategy) | `01a18fff-d581-762e-8ea5-3cbdf2063027` | 4.93 | −32.72 | 2.66 | 6 | 0.811 | 6.40 | 0.427 | 15.0 | 71.8 | +PEL −1.09R, +EDELWEISS −0.11R, +GNFC −0.15R (period end) |
| c7 | wide exits: SMA50 close, no partial, no breakeven (strategy; one exit bundle) | `01a19003-8aa8-77b0-8e14-8e97377f366e` | 6.36 | −31.29 | 2.64 | 3 | 2.088 | **13.76** | 0.710 | 19.4 | 46.8 | holds 2× longer; BALKRISIND +5.48R, MANAPPURAM 1.80R, ADANIENT −1.02R |
| c8 | entry at the daily close, breakout volume on that day (strategy; nearest knob to T+1) | `01a19007-5266-719f-ae80-0ab53923a820` | −0.38 | −38.03 | 0.43 | 1 | −0.366 | 0.84 | 0.065 | 13.0 | 93.5 | BALKRISIND closed below the pivot; MANAPPURAM refused max_chase (3.2%) |
| **c9** | **MAX DEPLOYMENT, stacked (more than one change): risk 3%, p_max 50%, 10 positions, RS all_nse** | `01a1900a-c3a4-72f5-bd33-499a7a5cb428` | **25.82** | **−11.83** | 2.52 | 4 | 2.196 | **17.78** | 0.460 | 38.7 | 63.3 | signal count; sizes 47.6–50.1% (3% ÷ ~6.2% stop; p_max 50% just binds at MANAPPURAM) |

c9 by month: invested 74.3% in February (2 positions, 25.7% cash) and 37.1% in November
(VGUARD), and 0% in May, June, September and December. Its trades are c5's four, at 47.6%,
50.1%, 49.6% and 47.6% of equity. Max invested 97.3% (minimum cash 2.7%).

c7 and c9 are both above +6.40%'s exposure but by different factors: c7 lengthens the holding
period (positions 0.35 → 0.71) and c9 enlarges the size (14% → 39%). Neither adds signals beyond
c5's one.

Not run: **T+1 open entry needs code** (there is no next-open entry timing; c8's daily-close
entry is the nearest existing knob and also removes the full-day-volume look-ahead). The 20-day
swing-low trail variant of wide exits was not run separately (budget; c7 already shows the
holding-period effect). p_max off (1.0) was not run because c3 shows p_max does not bind at 1%
risk, and c9 used 50%.

## 5. What it would take to be 60–90% invested

Invested = positions × size. Positions = trades × hold ÷ 248.

- **Sizing alone cannot get there.** Even at c9's 38.7% average size, 60–90% needs 1.6–2.3 open
  positions every day, and the cheat averaged 0.46 because it was flat 63% of the year.
- **The cheat alone could only get there by holding 2 positions of ~48% each all year.** In 2017
  that was BALKRISIND and MANAPPURAM bought in late January / early February and never sold. c9
  shows 74% invested in February, when exactly that happened. No exit rule in the system holds a
  position through the year's pullbacks, and a 2-stock 100% book is not what the owner's risk
  rules describe.
- **Realistically it needs 20–50 entries a year** (at 14–25% sizes and 1–2-month holds), or ~10
  entries held 3–6 months. The cheat produced 3–4, its geometry found 7 stocks all year, and the
  30 best stocks of 2017 almost never formed a cheat base. **This setup needs the other scanners
  feeding the same portfolio**, plus exits that keep winners (c7). Raising risk to 2% fills the
  25% p_max quickly, so with more signals p_max 25–33% and 6–10 slots become the real caps to
  watch.

## Reusable pieces (scratch copies in `/data/workspace/plans/y2017-cheat-work/`)

- `y2017_funnel.py`: a per-stock-night funnel replay of a run's config over any in-sample window,
  with the regime forced on but recorded. It writes `nights.csv` (each stock-night's stopping
  gate, criterion, reason and value), `breaks.csv` (daily-estimate breaks with volume ratio and
  chase), `regime.csv` and `moves.csv` (each PIT member's year return and biggest advance). Worth
  folding into `scripts/research/s1_setups_diag.py` as a `funnel --config` command.
- `opp.py`: the top-N movers vs funnel audit (blocker = the furthest gate on the advance nights).
- `runstats.py`: a run's exposure identity (invested = positions × size, flat days) and the
  trade table with post-exit 20/60-session moves. This belongs in the result standard as
  `run.json` metrics: `avg_position_pct`, `flat_days_pct`.
- `dump_bars.py`: adjusted bars and the NIFTY 500 index to a parquet file for a window.
- `make_cf.py`: the counterfactual variants generator. Run script: `/data/workspace/backtests/y2017-cheat/run.sh` on m3.
