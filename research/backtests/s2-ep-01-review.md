# S2 review and first sweep s2-ep-01 (2026-10-27)

Sources: S2 seed `momentum-breakout-ep.yaml` and stored v1 `64274b85`; backtest loop, spec and
scan code at main `ac38ccde`; a read-only replay of the scan rules on the adjusted store
(2016-01-01..2026-10-22, PIT NIFTY 500, hat_live SELECT only); `bars_5m` and its rejects ledger.
No backtest was run. Parameters, windows and criteria: `strategy-notes/s2-momentum-ep.md`.
Code goals: `briefs/s2-backtest.txt`. Sweep: `backtests/sweeps/s2-ep-01.yaml`.

## 1. Can S2 be backtested today? Half of it

**The breakout playbook runs today on daily bars, approximated. The episodic pivot cannot run at all.**

| Area | State today | Consequence |
|---|---|---|
| EP in the loop | The scan skips pre-open playbooks. There is no gap-day candidate path, and the known gap `episodic_pivot_not_backtested` blocks promotion | EP makes 0 trades in any run (brief goal 2) |
| 5m bars | Stored 2021-10-26..2026-10-23 (89.8% of member-days in 2022+, none before), but `load_market` never fills `MarketData.intraday` | Every run uses daily estimates, even where 5m exists (goal 1) |
| 5m gap days | 235 of 580 member gap days ≥ 6% lack bars (198 `basis_mismatch`). The rejects are gap-and-fades: opened at the high 41% vs 14%, closed −3.2% vs −0.7% under the open | Any 5m EP run would be biased toward winners (goal 3) |
| News / catalyst | `hat_announcement` has 0 rows, and corporate actions carry no results dates | Not modellable: gap + early volume is the proxy, recorded as a known gap |
| Pre-open data | Not needed: the daily open is the auction price. But the live gap scan floor is hard-coded at 10% | A configured 8% gap could never trigger live (goal 4) |
| Regime | All three rules are supported. Live applies the gate to EP too (GateBoard) | The backtest must gate EP the same way |
| Exits | Day-3 partial (only if in profit), breakeven after the partial, SMA close exit: all supported | The SMA10 trail is active from day 1, not only after the partial (small difference) |
| Universe | `adr_min` is bot-level, so it also filters EP | Of 145 neglected 10% gappers passing ₹10 cr, ADR ≥ 4% keeps 79 (goal 4) |
| Breakout trigger | Level = consolidation high only. `volume_pace` and close-confirmation are not modelled. Gap-overs are skipped | See bias (§3). `volume_pace` switched off in the sweep |
| Sizing | Risk 1%, `p_max` 0.25. The median LOD stop is 2.6%, so the cap binds on nearly every trade | 4 positions fill the book. `risk_pct` is not a lever; `p_max` is. Needs the min-position fix first (crumbs) |

## 2. Parameters for NIFTY 500 and trade supply (signals 2016-2026; 2016-2021 in brackets)

The seed gives **4 breakout signals a year (19 in 2016-2021)** and about 3 EP signals a year. It
was written for US small caps.
- **Setup threshold 0.6 is the binding filter:** 9,674 consolidation passes → 187 setups. The
  candidates' median distance from SMA10/20 is 7.3% (the band is 5%), so `ma_surf` scores 0, and
  only a range ≤ 1.5% could pass. At 0.4: 8× more.
- **Top 2% momentum = 10 names per window** among ~500 PIT members. Top 10% (~50 names) matches
  the reference's absolute count of names. Alone: 4 → 15/yr.
- **₹10 cr turnover:** ₹5 cr adds 12% (S1 lesson: idle years). **ADR 4% with ₹10 cr:** together pass
  21% of member-days; ADR 3.5% adds ~60%. **Prior move 30%:** barely binds (−4%). **Chase 2% / ADTR 1.0×:**
  ~1% / ~10%.
- **Consolidation [5,15]** picks the tightest window: 57% of signals break a 5-session high. A
  real 2-6 week base (`days [10,30]`, range 20%, threshold 0.3) gives a similar count (107/yr):
  round 2.
- **EP gap 10%:** 406 member gap days in 10.8 years. Full 5m-confirmed passes in 2022+, on the
  59% of gap days the store has: about 4/yr at 10%, 11/yr at 8%, 28/yr at 6% (40% of those in regime). EP is a complement, not the
  capital user. Refined: 8%.
- **Refined base (`s2base`):** 124 signals/yr in-sample (741). They fall on 28% of sessions and in
  53% of weeks, so S2 alone will still idle in weak stretches. The deployment levers are the regime
  (`reg50`, 1,080), the ADR floor (`adr35`, 1,197) and longer holds (`sma20`).

## 3. Window and bias

In-sample 2016-2021 runs on daily bars (no 5m exists then). The hold-out 2022-2026 runs once, on
5m bars after the brief, as live trades. These are S1's windows, so the combined book shares one
calendar. On 482 base triggers in 2022+ (signal level, no P&L):
- live's level is higher on 28% of triggers, and the entry a median 0.36% higher (~0.13R): the
  daily model is **optimistic**;
- 19% of daily triggers never fire live, and the estimated stop is slightly tight (2.63% vs
  2.86%): **mildly pessimistic**;
- gap-overs are skipped (~12% of breaks) and `volume_pace` is ignored: **pessimistic**.
Net: roughly a wash on entry quality, with entry-price optimism of ~0.1R per trade. State it next
to every in-sample result.

## 4. Sweep s2-ep-01: breakout only, policy v3, sleeve weight 1, flat ladder

| # | Label (base) | Exact change | Tests | Expected |
|---|---|---|---|---|
| 1 | `s2base` | v1 + `volume_pace` off, top 10%, ₹5 cr, threshold 0.4 | A working base | 741 signals → ~350-500 trades; invested ~35-50% |
| 2 | `sma20` (s2base) | `exits[close_below_sma].sma=20` | Ride winners | Fewer, longer trades; invested +5-10 pts; top-5 share up |
| 3 | `nobe` (s2base) | `exits[move_stop_to_breakeven].enabled=false` | S1 lesson: early ratchets cut winners | Fewer breakeven scratches, larger giveback on failures |
| 4 | `reg50` (s2base, bundle) | regime → `close_above_sma_and_rising` SMA50, `rising_days` 0 | Deployment: on 68% of sessions vs 49% | 1,080 signals; invested +10-15 pts; DD likely higher |
| 5 | `adr35` (s2base) | `universe[adr_min].params.pct=3.5` | Deployment in the thin years | 1,197 signals; invested +~10 pts |

Validated:
- `parse_variants` passes.
- `check_one_change` passes: each variant changes one knob, and `reg50` is a declared two-knob
  bundle.
- `apply_config` on the v1 config resolves every path: `exits[3].sma`, `exits[2].enabled`,
  `regime.rule` + `regime.params`, `universe[2].params.pct`.

Trials after the round: 5 of 10,000 (no prior S2 trials). Run with
`--strategy-version 64274b85-696f-4aea-944e-717a62546682 --universe nifty500 --from 2016-01-01
--to 2021-12-31 --variants backtests/sweeps/s2-ep-01.yaml --criteria strategy-notes/s2-momentum-ep.md`,
after hat/min-position merges and the owner's go. Judge on invested share and CAGR vs the TRI
first.

## 5. Decisions for the owner

1. Go for s2-ep-01 (breakout only), once the min-position fix has merged.
2. Hand `briefs/s2-backtest.txt` to a builder: 5m in the loop, EP simulation, 5m gap-day basis
   fix, gap-scan floor and per-playbook ADR. The gap-day refetch needs a data go.
3. Confirm the S2 criteria: the same bar as S1. The S1 review's open questions (longest DD on the
   combined book, `cagr_ex_top5` vs ride-winners) apply to S2 too.
4. Round 2 (not proposed now): a longer base `days [10,30]`, threshold 0.5, `p_max` 0.20/0.33,
   and EP gap 6/8/10 once EP runs.
