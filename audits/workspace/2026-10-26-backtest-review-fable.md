# Backtest process review (2026-10-26, independent, read-only)

Scope: `docs/backtests/process.md`, `result-standard.md`, `run.schema.json`, the CLI
(`app/hat/backtest/{__main__,compare,review,run_audit,folder,runs,trials,dsr,standard}.py`),
`app/hat/data/audit.py`, sweep `s1-baseline-01` (runs `01a17709` base, `01a17714` np under
`HAT_DATA_ROOT=/data/workspace/hat-data-isin`), and the promotion criteria in
`/data/workspace/strategy-notes/s1-minervini.md` (section fixed 2026-10-26). Engine commit of
both runs: `d0f2a964` (#278), tree clean. No backtest was run; `compare --sweep` and
`review <np> --criteria` were run (the latter wrote `review_request.md` into the np folder).

## Verdict: ready with fixes

The mechanics are sound: both folders are complete, every headline metric I recomputed from
`trades.csv`/`equity.csv` matches `run.json` to the last digit, the run audit catches what it
says it catches, `config.json` pins enough to replay, `--rerun` is sound, and `trials.json`
counted 1 and 2 correctly. What is not ready is the decision layer: the promotion criteria are
not computed by any tool (`review` writes a prompt, nothing more), the one-change rule and the
trial budget are unenforced and already broken by the first sweep (np bundles 5 changes and was
picked from ~54 deleted earlier variants that `dsr_n_trials` no longer counts), and the industry
dimension is dead data (every trade is `unknown`), which also makes the per-industry cap a
silent global cap. Fix H1 to H4 before the next sweep; the rest can follow.

For the record, np fails 4 of the 7 in-sample criteria (MAR 0.559 < 0.6; longest drawdown 740
sessions >= 500; CAGR 9.23% < NIFTY 500 TRI 15.66%; CAGR ex top-5 3.29% < 4.62% = half of CAGR).
It passes trades (144 >= 100), ADV (0 entries > 5%) and binding (`no_op` false, 155 trades
changed). No plateau sweep exists. The notes' decision "Hold-out 2022–2026 run next" must not
happen on this evidence.

## Findings

### HIGH

**H1. Trial accounting does not see the selection that produced `np`.**
`trials.json` holds 2 hashes (base, np); `dsr_n_trials` 1 and 2 are correct for the registry
(`trials.py:63-73`, `runs.py:623-634`). But np's `change` is "earlier best exit set", chosen
from 10 earlier sweeps under `/data/workspace/backtests/sweeps/` (`s1-sweep1..10`, 54 variants,
written 2026-10-25 18:07 to 2026-10-26 03:57) whose runs were deleted in the owner's reset
(notes, "Results log", "Decisions 2026-10-26"). A DSR at N=2 for a variant selected after ~55
trials overstates it, and nothing in the process can tell. Rule 4 ("every completed in-sample
run with new parameters is a trial") is a file anyone can delete.
Fix: (a) seed `trials.json` for S1 with the earlier distinct `resolved_hash` values (the sweep
files still name every override; a dry `--hash-only` mode, or an explicit
`prior_trials: 54` field per strategy in the registry that `family()` adds), (b) write the
trial count into the sweep log and into `review_request.md`, (c) never delete the registry on a
reset, only the folders.

**H2. The one-change rule is not enforced and the first sweep already breaks it.**
process.md rule 3 and the notes' ground rules say one change per variant. np sets 5 paths
(`config.json` `asked.variant_item.set`, 5 entries; `run.json` `config.overrides`, 5 paths:
`exits.2.enabled`, `exits.3.sma`, `exits.4.lookback_days`, `exits.5.enabled`,
`criteria.11.params.contractions.0`). `parse_variants` (`runs.py:760-808`) checks shape only;
the run audit's `binding` check only asks whether anything changed. A 5-way bundle with
`no_op: false` says nothing about which change bound.
Fix: `parse_variants` refuses a variant whose knobs differ from its base in more than one path
unless the variant carries `bundle: true` and a `change` naming each; the run audit adds a
`one_change` finding (warn) with the number of changed paths; `compare` shows it.

**H3. No tool computes the promotion criteria; `review` only writes a prompt.**
`review.py:50-125` emits a Markdown request listing `_HEADLINE` fields and the path of
`--criteria`; it checks nothing (`write_request` only tests `criteria.is_file()`,
`review.py:135`). Per criterion:
- MAR >= 0.6: `metrics.mar` (folder.py:627). Computable.
- longest drawdown < 500 sessions: `longest_dd_sessions` (standard.py:235-262, sessions after
  the peak). Computable; verified 1214 and 740 by recount.
- >= 100 trades: `metrics.trades`. Computable.
- CAGR above NIFTY 500 TRI: `benchmark_cagr_pct` (folder.py:643, close before the first session
  to the last session, same calendar days as `cagr_pct`). Computable; 15.6588 verified.
- CAGR ex top-5 >= half CAGR: `cagr_ex_top5_trades_pct` (folder.py:652). Computable.
- no entry > 5% ADV: `trades_over_5pct_adv`. Computable.
- `no_op` false: `binding.no_op`. Computable.
- Plateau (each key parameter one step either side keeps MAR >= 0.5): not computable. "Key
  parameters" and "one step" are undefined for S1; no tool reads a sweep as a neighbourhood;
  `compare` prints MAR but not which parameter a row moved.
- Hold-out (expectancy >= half in-sample, MAR >= 0.4): both numbers exist in the two
  `run.json`s (`data.validates_run_id` links them) but no tool joins them.
- Trial budget 30: counted in `trials.json`, never enforced (`sweep_bot` has no budget).
The reviewer is also handed the whole notes file, including "Decisions" written with knowledge
of the deleted results and "Hold-out 2022–2026 run next" (before any in-sample run under the
standard), and the criteria text is not pinned (no hash), so "not changed after a run has been
seen" is unverifiable.
Fix: `python -m app.hat.backtest.criteria <run_id> --criteria criteria.yaml` that prints a
pass/fail table (in-sample, plateau from `--sweep`, hold-out from `validates_run_id`) and writes
`criteria.json` into the folder; criteria as a small YAML block (thresholds, key parameters and
their step, budget) whose sha256 goes into `review_request.md` and `audit_report.md`; `compare`
adds `longest_dd`, `bench%`, `cagr_ex5%`, `>5%adv` columns; `sweep_bot` refuses a new in-sample
hash once `len(trials) >= budget` (budget read from the criteria file).

**H4. Industry is dead data: every trade is `unknown`, and the per-industry cap is a global cap.**
`hat_industry` has 497 rows, all `effective_from = 2026-10-22` (one row per currently active
symbol, e.g. TATAPOWER `01a1629b-fe9b…` Power, TORNTPOWER Power); 456 of the 953 members over
2016–2026 have no row. `load_industries(..., effective)` (`data/instruments.py:285-320`) dates a
classification at load time, and `industry_on` (`backtest/data.py:224-227`) returns the newest
classification effective on or before the trade date, so every trade before 2026-10-22 reads
`unknown` (`signals.csv`/`trades.csv` column `industry`, `by_industry: {"unknown": 144}`). This
is not a #278 join break (the query `_industries`, `data.py:770-776`, reads hat_live and finds
the rows); it is the dating. `mcap_cr`, `cap_bucket`, `index_membership` empty is by design
(result-standard v1.1, "Stock attributes").
Effect on results: `decision.py:356` counts open positions whose `industry` string equals the
entrant's, so with all `unknown` the cap `max_positions_per_industry` is a cap on total
positions. Under policy v3 it is 10 = `max_open_positions`, so nothing bound (np refusals:
`ladder_level` 142, `size_zero_cash` 42, no `industry_cap`); under v2 ("3 per industry") or the
documented knob `max_per_industry: 2` it would silently cap the book at 3 or 2 positions.
`by_industry` and `stocks.csv.industry` are useless for analysis.
Fix: on ingest, back-date the first classification of an instrument to a sentinel (its listing
date or 1900-01-01) and keep later rows as reclassifications; add a data audit check
`industries` that warns when > 5% of member-days resolve to `unknown` and fails when a run's
policy has `max_positions_per_industry < max_open_positions` while coverage is incomplete;
list the unknown share in `run.json` `data`.

### MEDIUM

**M1. The hold-out cannot reuse `config.json`.** `--rerun RUN_ID` takes nothing else
(`__main__.py:176, 283-284`); step 7 says "same overrides", so a fresh agent retypes np's five
`--set`s (or a variants file) by hand. Fix: `--rerun <id> --from --to --split hold_out
--validates <id>` (replay the config with a new window), or a variants key `from_run: <id>`.

**M2. Policy drift between sweeps is silent.** `_target` (`runs.py:236-243`) takes the policy in
force now; a plateau sweep run after a `set-policy` would differ from its base in the policy,
and `compare` has no policy column. Fix: `compare` shows `risk_policy.version`; the run audit
`binding` warns when a variant's policy version differs from its base's; or require `--policy
FILE` for research sweeps and record the path.

**M3. PBO family ignores the window and is reported at n=2.** `family_pbo` (`runs.py:560-583`)
filters by strategy, universe and split, not by period; one in-sample run on another window
leaves fewer than 16 common sessions and PBO goes null for every later run. np's `pbo: 0.0`
comes from 2 series (np vs a losing base), 70 splits, which is not evidence of anything.
Fix: filter by `period_start/end`; report null below 4 distinct variants; say so in the standard.

**M4. `dsr_n_trials` is not the N the DSR used.** `family_deflated_sharpe` floors N at 5 and the
trial variance at 0.25/252 (`dsr.py:65-66, 143-147`); the standard says `dsr_n_trials` is
"variants counted for DSR" (`result-standard.md:69`). The floor is right (it only deflates
more), the label is wrong. Fix: add `dsr_n_trials_effective` (or document the floors in the
standard and the review template).

**M5. Every "sessions" hold field is calendar days.** `trades.csv.hold_sessions` =
`(leg.day - entry_date).days` (`folder.py:539`); `avg_hold_sessions_win/loss` and
`by_exit_reason.avg_hold_sessions` read `holding_days` = calendar days (`engine/positions.py:400`).
np trade 1: 2016-04-20 to 2016-05-04 = 14, 11 sessions. `longest_dd_sessions` is real sessions.
Fix: rename to `hold_days` / `avg_hold_days` or count sessions from `equity.csv` dates.

**M6. Audit warnings have nowhere to be explained once.** Both runs are `warn/warn` because the
data audit's `corporate_actions` warns (`ex_date_jump` SINTEX 2017-05-25, 250 unexplained > 20%
moves elsewhere, JETAIRWAYS, YESBANK, CCAVENUE ...); the run audit's `data` finding lists only
the digest. Process: "not evidence until the failure is explained", but every reviewer
re-explains the same digest. Fix: `backtests/data_audits/<digest>.explained.md` (owner-signed,
one line per finding); the run audit's `data` check names the warning checks and whether an
explanation file exists.

**M7. process.md leaves a fresh agent short of inputs.** It does not say where `<v>` comes from
(`python -m app.hat.admin show`, runbook.md:137), which `HAT_DATA_ROOT`, where sweep files and
logs live (`/data/workspace/backtests/sweeps/`, `.log`), where the strategy notes are, that
`--criteria` takes the whole notes file, or that `--variants` paths are resolved from
`backend/`. Otherwise the steps are runnable: steps 2–4 and 6 were followed exactly by the first
sweep; `--universe nifty500` resolves (hat_universe name `nifty500`).

### LOW

**L1. Data audit CLI crash confirmed by code; in-run audits were not affected.**
`audit.py:978` runs `SET TRANSACTION READ ONLY` with no `bind_arguments`; `HatSession.get_bind`
(`storage.py:79-88`) finds no table in a TextClause and SQLAlchemy has no single bind, so the CLI
fails before loading. The runs go through `runs._load` (`runs.py:325-351`) on the session
`__main__.py:221` made read-only with `bind_arguments={"mapper": HatEvent}`; both folders hold
`data_audit.json` with 7 checks (digest `407c3623…`, scope 770 members, 1486 sessions) and the
cached copy under `data_audits/`. Fix is in flight elsewhere.

**L2. Lookahead sampling is thin:** 96 feature samples and 8 breadth samples over 744,425
member-sessions (`data_audit.json`, `lookahead.summary`). Fix: sample per year and per
liquidity quintile, at least 500 feature rows.

**L3. `trials.json` is keyed by strategy only.** A run of the same config on another universe
or window is a duplicate (no trial); runs on different windows pool. Fix: key by
(strategy, universe, window) or include them in the hash.

**L4. Base is a near-dead configuration** (23 trades in 6 years, 0 in 2016, expectancy −0.20 R),
so `trades_changed: 155` for np means little; the next sweep's base should be a live config.

**L5. `review_request.md` now sits in the np folder** (written by this review's allowed
`review` call); harmless, delete or overwrite when the real request is made.

## Spot checks (all match `run.json`)

| metric | base (recomputed / run.json) | np (recomputed / run.json) |
|---|---|---|
| trades | 23 / 23 | 144 / 144 |
| net P&L vs final − start | −45,864.60 / −45,864.60 | 698,874.18 / 698,874.18 |
| CAGR % (2192 calendar days) | −0.7793 / −0.7793 | 9.2324 / 9.2324 |
| max DD % | 7.2921 / 7.2921 | 16.5062 / 16.5062 |
| longest DD (sessions, start, end, recovered) | 1214, 2017-02-06, 2021-12-31, false | 740, 2018-01-24, 2021-01-21, true |
| expectancy R / win % | −0.1971 / 26.087 | 0.3828 / 28.472 |
| top-5 share % / CAGR ex top-5 % | null / −1.5915 | 69.3499 / 3.287 |
| cost share % / fees | null / 8,958.52 | 8.0949 / 61,555.98 |
| max position % ADV / entries > 5% | 0.1784 / 0 | 0.3228 / 0 |
| Sharpe / MAR | −0.3556 / −0.1069 | 0.8913 / 0.5593 |
| benchmark CAGR % | 15.6588 (from the close before 2016-01-01) | same |
| signals = taken + refused | 23 = 23 + 0 | 328 = 144 + 184 (142 + 42) |

Binding: np `trade_list_hash` differs from base, `trades_changed` 155 = symmetric difference,
`no_op` false; base has `no_op: null` (no base) and the audit passes it. The one > 5% equity
move (np, 2021-05-19, +6.26%, 6 positions, ₹15.5 lakh held) is inside the 20% band. Both runs
share `data_snapshot_id 25c95979…`, policy v3 (`01a175fa…`, risk 1%, 10 positions, 10 per
industry, ladder 6/8/10 at 1.0), `cnc-delivery-1`, slippage 20, `ambiguous: optimistic`,
`entry_fill: penetration_1_tick`, `regime_mult: 1`. `config.json` holds the strategy document
after overrides, the policy document and version, universe version id, period, fills,
conventions, snapshot digest and the data-audit digest; the engine commit is in `run.json`
`identity`, not in `config.json` (a `--rerun` on a later commit is published as a new run whose
`binding` shows any difference, which is acceptable, but `--rerun` should also record the
commit it replayed from). `--rerun` refuses on a snapshot mismatch (`runs.py:1043-1044`), adds
no trial (same hash, `trials.py:94-95`), and drops the sweep labels (so `compare --sweep` will
not list it).

## Where p-hacking or silent errors can enter

1. Deleting run folders resets the trial count (H1); `trials.json` and the sweep files are the
   only memory and both are plain files.
2. Bundled variants with `no_op: false` (H2) read as "the change worked".
3. Criteria live in a free-text file with post-run commentary, unhashed (H3); `--criteria` just
   needs a file that exists.
4. The policy in force can change between a sweep and its plateau sweep (M2).
5. Defaults are optimistic (`ambiguous: optimistic`, intraday fills on a tick through the
   pivot, `close_rules_decided_on_official_close` in `known_gaps`); a sweep never has to run the
   pessimistic variant. Add it to the criteria (hold-out or final candidate under
   `--ambiguous pessimistic`).
6. Industry cap behaves as a global cap without a warning (H4).
7. The data audit's warn status is carried forever and explained nowhere (M6).

## Fixes for next session

1. Seed/offset S1's trial registry with the 54 earlier variants; log the count in every sweep
   log and review request; never delete `trials.json`. (H1)
2. `parse_variants` one-change refusal plus `one_change` audit finding. (H2)
3. `app.hat.backtest.criteria` evaluator + criteria YAML with hash; `compare` columns for the
   criteria; budget enforcement in `sweep_bot`. (H3)
4. Industry ingest back-dating, `industries` data-audit check, cap guard. (H4)
5. `--rerun` with a new window/split for the hold-out. (M1)
6. Policy version in `compare` and in the binding audit. (M2)
7. PBO family by window; null below 4 variants; `dsr_n_trials_effective`. (M3, M4)
8. Rename calendar-day hold fields. (M5)
9. Explained-warnings file keyed by data-audit digest. (M6)
10. process.md: how to find `<v>`, `HAT_DATA_ROOT`, sweep/log/notes locations. (M7)
11. Land the audit CLI bind fix (in flight). (L1)
