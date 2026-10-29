# Orchestrator handoff (2026-10-26, end of session)

Read first: this file, `open-items.md`, the two reviews below, the repo's `CLAUDE.md` and `docs/backtests/process.md`.

## State
- **main** = #281 `4379ac9c`. Merged 2026-10-26: #274 breadth regime, #275 results UI, #276 Result Standard v1.1, #277 audits + process doc, #278 storage split, #279 Sonar triage, #280 golden sample + audit CLI fix, #281 scripts in repo.
- **Storage (owner rule, 2026-10-26):** `hat_live` is canonical stock data, READ-ONLY except data updates (pg_dump first, delete the dump after verifying). Trading state lives in `hat_state`; configs are JSON under `HAT_DATA_ROOT/admin/config/`; backtests write only run folders `HAT_DATA_ROOT/backtests/runs/<run_id>/`. Legacy config/state tables still sit in hat_live: dropping them is the owner's call.
- **Old results deleted** (unreliable). Earlier findings are kept as leads in `/data/workspace/strategy-notes/s1-minervini.md` (Decisions), which also holds the fixed S1 promotion criteria and trial budget (30).
- **Golden sample:** `HAT_DATA_ROOT/audits/golden/2026-10-26.json` (463 items, 12 recorded mismatches). `python -m app.hat.data.golden check` passed with 0 drift on 2026-10-26; it also runs inside every data audit. Deliberate data fixes need `golden rebase --reason ... --items ...`.
- **Scripts:** reusable automation lives in the repo (owner, 2026-10-26). #281 brings in the Kotak 5m downloader, the NIFTY 500 history builder, set_secrets/fyers_login, and `scripts/agents/` merge check and builder launch/cleanup (`docs/agents/`). The out-of-repo originals were deleted (kept outside: `nifty500-history/check.py` and `ev.py` diagnostics, `corrections/review-links.sh`, `ca-research/tools`; none are reusable HAT tools).
- **No data download was started** this session (owner).

## Progress (2026-10-26, second session)
- Merged: #282 sweep discipline (e8e3774f), #283 criteria tool + trials (9dff8cb0). Follow-ups: `followups/sweep-discipline.md`, `followups/backtest-criteria.md` (open code items: budget enforcement in sweep_bot, compare criteria columns). Trials registry v2: 58 S1 trials (56 prior, count in DSR only; budget 30 counts own trials). Plateau knobs in the notes' hat-criteria block accepted as proposed (np's five paths).
- Merged #284 industry history + audit additions (d1b7c897). Industry history APPLIED to hat_live (834 rows, 820 chains; unknown member-days 2016+ 6.7%, warns >5%; policy v3 has no industry cap). Follow-ups `followups/industry-audit.md`: more dated current-taxonomy NIFTY 500 lists (2021-2025) would cut the 174 unknown names; 11 undated member demergers per the new chain-aware count (my earlier "none are members" query was per-instrument, wrong); DuckDB tmp folder must exist (create in `connect`).
- Merged #285 bars5m basis (18a4f550). APPLIED: repair (converted 4114, refiled 2152, dropped 1733), Kotak --only refills (7 + 39 days), dry run 0 off-basis, golden 0 drift. Kotak raw_5m* deleted. Hard-link backup `/data/workspace/backups/5m-2026-10-26/` to delete once the data audit is read. 1,180 dropped 5m days (mostly non-members 2025-10..2026-10) refetch via Fyers minute_history only if an intraday strategy needs them.
- 2.3 demerger announced_on APPLIED for 10 member demergers (board approval where the ratio was public; PRAKASH record-date notice 2019-04-03); COX&KINGS left null (no dated ratio). File `admin/demerger-announced-2026-10-26.tsv`. 7 undated demergers 2016+ remain (non-member chains).
- Merged #286 sweep budget + compare criteria columns + resolved knobs + DuckDB per-process tmp (ce6312a2). Follow-ups `followups/sweep-budget.md` (single runs bypass the budget; hold-out compare rows untested on real data). No builders running; main = ce6312a2.
- Data audit 2016-01-01..2026-10-23 nifty500: warn, digest 0363e347…, explained in `backtests/data_audits/0363e347….explained.md`.
- Owner 2026-10-26 "yes drop, and proceed with pending items":
  - Legacy tables DROPPED from hat_live (30 tables, schema.legacy_live_tables; CASCADE dropped FKs hat_quality_check->hat_job_run and hat_universe_version->hat_backtest_run, which the models don't declare). Checked first: state_split configs unchanged, every hat_live hat_event id in hat_state (state has +14 = today's corrections). After: schema drift none (live and state), golden 0. Docs still say the tables "stay until the owner drops them" (decisions.md:248, runbook.md:38): fix in the next PR.
  - Industry: added Nifty Total Market lists 2025-05-04 and 2026-08-02 (Wayback) to `admin/nifty500-industry/`; applied: 987 chains, unknown member-days 2016+ 4.9% (below 5% warn). Applied while the sweep ran (industry only feeds breakdowns/cap; v3 has no cap): check data-audit digests across s1-np-02 variants.
  - Sweep s1-np-02 RUNNING (log /data/workspace/backtests/s1-np-02.log). Then compare --sweep s1-np-02 --criteria, pick, plateau, review, hold-out once.
  - Merged #287 nightly TRI + verify-tri (968a00e8); fetch run: 3,636 TRI closes 2012-02-21..2026-10-23 match raw (0 mismatches). Follow-ups `followups/tri-nightly.md`: drop the legacy-table allowance from invariants.md:152 and schema.legacy_live_tables (small PR); check ingest.completed tri_stored after the first production night.
  - No builders running. Sweep s1-np-02 ~13 min/variant (started 12:19).
- 2.2 done: SINTEX 2017-05-25 -> 0.248319, CGPOWER 2016-03-15 -> 0.283323 (ex close gap, ADANIENT convention; no official cost ratio found); features recomputed (2 chains); golden rebased (2 CGPOWER items), check 0 drift. List: `HAT_DATA_ROOT/admin/demerger-close-2026-10-26.tsv`.
- 2.3: CCAVENUE (INFIBEAM ISIN) 2026-10-19 and AZADIND 2026-10-23 splits got known_on = ex-date (`admin/known-on-2026-10-26.tsv`); ETF rows left. The 17 undated demergers 2016+ are all outside NIFTY 500 membership periods: no backtest effect, left null (owner rule).
- Golden rebase gotcha: `--items` splits on commas and bars_daily_cap ids contain one; use `all-drifted` when the drift is exactly the intended set (fix in hat/industry-audit).

## Reviews (2026-10-26)
- Data: `/data/workspace/audits/2026-10-26-data-review-fable.md`. Daily bars trustworthy from 2016, with fixes.
- Backtest process: `/data/workspace/audits/2026-10-26-backtest-review-fable.md`. Ready with fixes; every recomputed metric matched run.json.
- First sweep under the new process, `s1-baseline-01` (policy v3, 2016–2021): base 23 trades, MAR −0.11; np 144 trades, exp +0.38R, CAGR 9.2%, max DD 16.5%, MAR 0.56. np fails 4 criteria (MAR, longest DD 740 sessions, CAGR < NIFTY 500 TRI 15.7%, CAGR ex top-5 3.3% < half). No hold-out.

## Next session plan (in order)

### 1. Fixes before any new backtest (builder PRs, ≤2 at once)
1. **Criteria tool** (backtest review H3): `python -m app.hat.backtest.review <run_id> --criteria <notes>` computes every promotion criterion from the run folder (MAR, longest DD in sessions, trades, CAGR vs TRI, CAGR ex top-5, max %ADV, no-op, plateau from a sweep, hold-out degradation via `--validates`), checks the trial budget and hashes the criteria block; pass/fail table into the run folder. Criteria machine-readable (a block in the notes or a JSON beside them).
2. **Trials honesty** (H1): `dsr_n_trials` = the N actually used (floored); PBO family keyed by window too and not reported below a minimum n. Seed trials.json for S1 with the ~54 deleted variants as prior trials (they picked np), so DSR is not flattered.
3. **One change per variant** (H2): sweep/compare warn when a variant differs from its base in more than one knob unless `bundle: true` with a reason. np is a declared bundle.
4. **Hold-out from config:** `--validates <run_id>` reuses that run's config.json; refuse a second hold-out of the same candidate; compare flags policy drift between runs of a sweep.
5. **Small:** `hold_sessions` fields are calendar days (rename or recompute); audit-warning explanation file (`audit_notes.md` in the run folder, read by review); process.md says where the strategy version id, HAT_DATA_ROOT and sweep/log paths live.
6. **Data audit additions** (data review): store-wide 5m close scan (not a 120-day sample); flag demerger factors taken from thin ex-day opens.

### 2. Data fixes (orchestrator applies to hat_live: pg_dump first, then golden rebase with a reason)
1. **Industry history** (backtest review H4): every `hat_industry` row has effective_from 2026-10-22 (load date), so point-in-time lookups before that return `unknown`. Industry breakdowns are empty and a per-industry cap would act as a global cap. Pick the rule (backdate current industry to first bar, or source history) and apply. Needed before any industry-cap or industry-breakdown test.
2. **SINTEX 2017-05-25, CROMPGREAV 2016-03-15 demerger factors** (taken at a thin ex-day open; pre-history 31% low / 20% high): value-based factor (official cost-of-acquisition ratio, or prev close vs ex-day close plus the demerged entity's value), recompute features, golden rebase.
3. **Corporate-action dates:** 25 of 124 demergers lack announced_on (hold-through); CCAVENUE 2026-10-19 consolidation lacks known_on.
4. **5m store:** 3,880 stored 5m days (14 names, mostly 2025-10-22..2026-10-21) are on Fyers' adjusted basis: rebase to raw or drop. Intraday only; daily runs are unaffected.
5. **delisted_on** null on all 4,422 instruments: refresh (open item D4).
6. **Raw Kotak downloads** (`kotak/data/raw_5m` 914M, `raw_5m_former` 445M): not canonical, the only source of the ~8% rejected 5m days. Delete once item 4 is settled.

### 3. Data downloads (only when the owner says go)
- NIFTY 500 TRI raw history (niftyindices.com) to replace the back-filled series; add TRI to the nightly job.
- Re-fetch missing Fyers 5m bars (15:15–15:25 gaps since 2026-08-03; 09:15 since 2026-07-17) only if an intraday strategy needs them.

### 4. S1 sweeps under the criteria (after 1 and 2.1/2.2; budget 30 trials incl. prior ones per 1.2)
Base = np. One change per variant, in-sample 2016–2021:
1. Concentration: np's top-5 share is 69%; entry-quality filters that cut the fat-tail dependence (setup threshold, base depth, breakout volume).
2. Breadth regime (`breadth_above` 50/55/60) vs none.
3. Flat ladder vs 6/8/10 (ladder looked wrong for a ~28% win rate); ladder step-down on drawdown.
4. Exits (the proven lever): trail lookback ±1 step; SMA close exit 50 vs tighter after +2R.
5. Plateau on the chosen variant (each key parameter one step either side; MAR ≥0.5 holds).
6. Hold-out 2022–last session once, for one candidate, only if every in-sample criterion passes and the review says promote.

### 5. Owner decisions
- Drop the legacy tables in hat_live (after hat_state has run a while).
- Industry history rule (2.1), if not obvious from a source.

## How to run things
- Python `/data/workspace/algotrading/venv/bin/python`; from `algotrading/backend` with `DB_NAME=hat_live HAT_ENABLED=false HAT_DATA_ROOT=/data/workspace/hat-data-isin`.
- Backtests: `docs/backtests/process.md` is the one entry point. S1 version `aac4fda7-86b2-421d-b7f8-1247edef7f1d`. Sweep files in `/data/workspace/backtests/sweeps/` (mapping format; the old list-format files are invalid).
- Postgres: `docker exec hatpg psql -U postgres -d hat_live` (SELECT only, except data updates).
- Builders and merge check: `docs/agents/orchestrator.md` and `python scripts/agents/merge_check.py <pr> --sha <sha>` (one verdict line, never merges) and `scripts/agents/builder.py` (launch and cleanup). Merge in a separate command after the check. CodeAnt reviews once; never ask it to re-review.
- Never read or print `.env` or credentials; credentials go through the repo's set_secrets helper.

### s1-np-02 result (2026-10-26, done ~15:00)
- 13 runs complete, 13/30 own trials used. All share data-audit digest 57434913 (warn: 252 thin 5m closes, unknown industry 11.9% pre-reapply, 9 golden 5m-volume). Mid-sweep industry apply did not reach any run.
- No variant passes the in-sample criteria. All fail longest_dd (>=625 sessions vs <500), CAGR vs benchmark (best 9.7% vs 15.7%) and cagr_ex_top5 (best ~0.40 vs 0.5). PBO 0.56-0.91, DSR <= 0.26.
- Best: thr70 (MAR 0.67, DSR 0.19), trail15 (CAGR 9.7%, DSR 0.26, PBO 0.91), ratio60 (maxDD 12.4%).
- Diagnosis: invested share ~32% (thr70). Under-exposure caps CAGR. No hold-out or plateau run until the owner gives a go; proposed next: sizing/exposure round on thr70.

### Next S1 round, parked for later testing (owner 2026-10-26: "put it in handoff for later testing")
Owner direction: risk per trade much higher (up to 5%); trade count too low; avoid trades in downtrend markets / bad stocks. Idle capital is the failure (memory deploy-capital). Do not run until the owner says go.

Signal-count diagnosis (no bug; replay of the engine's own code, scripts in the old session scratchpad, not kept):
- 744,425 member-days -> 293,828 after universe + regime -> 110,768 full trend template -> 2,255 VCP pass (2%) -> 1,430 close<=pivot (348 setups) -> 459 next-day breaks within chase.
- VCP fails: base_too_short 67% (within 15 sessions of 120d closing high), depth_ratio_too_wide 19%, too_few_contractions 9%, no_volume_dryup 2%.
- Backtest triggers on daily-bar pivot break (loop.py `_level`, trigger.daily_level); 5m bars not used.
- Sizing: at 1% risk median position ~15% equity; p_max 0.20, ladder L1 6 positions (142 refusals), cash (42 refusals) bind; global_open_risk_pct 0.10 never bound (max 5.0%).

Proposed sweep s1-deploy-01 (10 trials of 17 left; base = np):
- deploy (bundle base): policy_set global_open_risk_pct=1, p_max.stage2-contraction-breakout=1, flat_ladder, max_positions 10.
- One change each on deploy:
  - r2 / r3 / r5: risk_pct 0.02 / 0.03 / 0.05.
  - dry10: vcp dryup_vs_avg50 1.0 (replay +60% breaks).
  - ratio100: vcp depth_ratio_max 1.0 (+60%).
  - vcploose (bundle): dryup 1.0 + depth_ratio 1.0 + final_depth_max_pct 15 + min_depth_pct 3 (2.8x).
  - tv5: min_turnover inr_cr 5 (~+30% universe, estimate).
  - trend200: regime sma_fast_above_slow_both_rising fast 50 slow 200 on NIFTY 500.
  - volsize: regime_mult policy (bull_quiet 1, bull_volatile 0.75, correction 0.5, bear 0.25).
- Not in round: pivot_source base_high (3.4x breaks, but a different strategy).
- Judge on invested share and CAGR vs benchmark first; compare must show invested share (add to compare if missing).

### 2026-10-27
- Owner go: sweep s1-deploy-01 RUNNING (file backtests/sweeps/s1-deploy-01.yaml, log backtests/s1-deploy-01.log), 10 variants, base = np run 01a17833. `max_positions 10` dropped (policy already 10); vcploose has no min_depth_pct (no such VCP param).
- Builder hat/compare-invested: invested share in compare, golden rebase item ids with commas, docs legacy-table wording.
- #290 merged (ac38ccde): compare inv%/inv_max%, golden rebase --items-file, legacy-table docs. Builder cleaned up; follow-ups none.
- s1-deploy-01 done (23/30 own trials). All fail longest_dd (~730 sessions) and cagr_ex_top5; none promotable. Caps off barely moved invested share (32->35%): idle cash is signal scarcity, not caps. Higher risk: inv 45-51%, fewer trades, top-5 >100% of P&L (r5 CAGR 18.7% but DD 41.5%, ex-top5 -18.9%). Best: dry10 (226 trades, CAGR 14.4%, MAR 0.605 pass, DSR 0.36, PBO 0.57, inv 49%). trend200 worst (CAGR 6.0%).
- r5 audit fail equity_jump_without_positions 2019-10-22 = ASTRAL entered and stopped out the same day (-1.08R at 4.8% equity risk); real loss, audit false positive for same-day round trips: small run_audit fix.

### 2026-10-27 (later)
- Owner: no run cap (trial_budget 10000), fix crumbs then run 5, add 2 more strategies (S2 EP first).
- #291 min position 2% + sweep path checks + same-day audit fix. #292/#293 S2: gap days storable, gap floor from config, adr_min in setup, 5m bars in backtest, EP backtested (--entry-bars daily to force daily).
- s1-deploy-02 (review + results: backtests/s1-deploy-02-review.md): `ride` (dry10 + step trail off) best: 172 tr, 0.588R, CAGR 15.8, DD 24.1, MAR 0.653, invested 51.7%; fails only longest DD (752) and CAGR ex top-5. tv3/r15/vol raised invested share but cut CAGR/MAR.
- S2: notes strategy-notes/s2-momentum-ep.md, sweep sweeps/s2-ep-01.yaml (breakout, daily bars) awaiting owner go; gap-day refetch awaiting data go; S2 criteria = S1's pending owner confirm.

### 2026-10-27 (S1 book rules task)
- Owner task: rebuild S1 to Minervini book rules (spec /data/workspace/briefs/s1-book-spec.md, incl. owner decisions 1-8). Phase 0 audit: /data/workspace/audits/2026-10-27-s1-book-phase0.md. Owner approved defaults, "proceed".
- Builders: hat/s1-book-engine (by_year fix, SMA grace, RS slot order, daily breakout volume), hat/s1-book-detector (RS in eligible universe, C-G detector, logging, funnel, sweep file s1-book-01.yaml).
- After both merge: Phase 1 rerun of ride (01a17ca4) with --ambiguous pessimistic --entry-bars daily; Phase 3 run s1-book-01 in-sample; STOP for owner. No hold-out until owner approves (Phase 5).
- S2 EP plan saved (docs/plans/s2-ep-refinement.md, merged #296). Start only after S1 book plan and owner says "start the S2 EP plan".

## 2026-10-27 S1 book Phase 3 done — STOPPED for owner
- #295 merged (main 6cabfbd6). s1-book-01 run 01a17d8a-f6df-7099-af99-7147629ba1ec: 12 trades, win 33.3%, 0.497R, CAGR 0.99%, invested 1.8%.
- Report /data/workspace/backtests/s1-book-01-report.md. Decision branch: <60 trades, too few, don't loosen.
- Launch needs `--universe 01a171d7-c436-713e-ad13-63416dada7ec` (name NIFTY500_PIT doesn't resolve).
- Open: standard.py:363 labels every close_below_sma as sma50_close. Phase 4 (detector audit) and hold-out wait for owner.

## 2026-10-27 S1 phases 4-5 + ride variants
- #297 merged (7b75ad87): Phase 4 audit /data/workspace/audits/2026-10-27-s1-book-phase4.md; charts in algotrading/reports/s1-book-01/audit/ (gitignored).
- Phase 5 hold-out s1-book-01 run 01a17dc9 (2022-01-01..2026-10-25, membership end): 15 trades. Report backtests/s1-book-01-holdout-report.md. Hold-out now used once (s1-book-01 only).
- Owner asked for ride variants (capital/DD/trades), then EP plan. Report backtests/s1-ride-deploy-report.md. Candidate rs_r075_ratio09 run 01a17e77. Awaiting owner freeze decision.
- Run-based variants must restate the base run's `set` lines (else backtest_sweep_not_one_change).

## 2026-10-28: S1 frozen, S2 EP started
- S1 frozen as rs_r075_ratio09 (run 01a17e77-8d4c-7499-bd40-fa621ba1f550; sweep s1-ride-deploy-2.yaml; report backtests/s1-ride-deploy-report.md). No hold-out run (owner). Hold-out used once, by s1-book-01 only.
- S2 EP plan (docs/plans/s2-ep-refinement.md) started: A0 probe, brief briefs/s2-ep-a0-probe.txt, builder s2-ep-a0-probe. STOP after A0 for owner review.
- Owner 2026-10-28: once results pipeline is validated (A4), ship it as reusable repo scripts for extracting future datasets (incremental new quarters). Include in A1 brief.
- 2026-10-28: owner asked for top-3 ride on hold-out: all fail (CAGR 1.5-4.0 vs bench 8.8, exp R 0.10-0.21). Report backtests/s1-ride-holdout-report.md. S1 freeze to be reconsidered by owner.
- A0 merged #298 (da9d16e2). Waiting owner go for A1 (XBRL 2020+, no HTML parsing, table via schema.py).
- 2026-10-28: #299 merged (5e59675c) A1-A3 results store. Builder s2-ep-results keeps fetching in its worktree (NSE ETA 2026-10-29 ~10:00 UTC), then parse/derive + A4 report. Don't cleanup until A4.
- Owner 2026-10-28: results fetch cut to NIFTY500_PIT members, consolidated only (standalone fallback only if no consolidated). Builder restarting fetch via new PR.
- 2026-10-28: owner: build rest of plan while download runs. Builder s2-ep-partb (brief briefs/s2-ep-partb.txt): B1-B6 + C3 breakdowns + sweep s2-ep-01.yaml + B7/C4 scripts, no runs. Scope-cut PR #301 (results builder) in CI.
- Results fetch restarted 05:21 UTC: 812 NIFTY500 members, NSE ETA ~12:30-13:30 UTC 2026-10-28, then parse/derive + A4.
- 2026-10-28: owner asked: NSE-pasta (github abhij1306/NSE-pasta, MIT, results-data CLI like NSE-noodles) built by Claude on remote box ssh -p 2222 ibssh_uot4pxvog4d3j5oam6ckz5ahbi@ssh.instabox.sh, tmux %0; brief /data/workspace/briefs/nse-pasta-brief.md there. Remote gh NOT logged in: owner must gh auth login there to push. Ends with 'PASTA READY'.
- NSE-pasta done per owner 2026-10-28; remote machine closed.
06:46 #302 builder answered 3 CodeAnt threads, head df52f616; CI watcher bonk0l468 then merge_check
06:52 #303 merged 267f830a, but my waiter merged despite merge_check NO MERGE (3 unanswered CodeAnt threads; '&&' after tail). Replied on threads; points saved in overlay memory for Phase 0. Waiters must gate on grep 'MERGE OK'.
06:52 #302 merged (MERGE OK on rerun), s2-ep-partb cleaned up
08:00 owner: fetch overlay data from Kotak, not NSE -> started builder overlay-phase0 (brief briefs/overlay-phase0.txt), Phase 0 only, STOP after
09:20 #304 overlay Phase 0: builder READY dbde2171 but merge_check NO MERGE (2 CodeAnt threads: duplicate ingest rows at overlay_etf.py:435, tmp race :389); sent to builder turn 2 (bx057nc2b)
09:25 #304 overlay Phase 0 merged (MERGE OK 5d4d37ef), builder cleaned. Overlay STOP for owner review (proxy overstates LIQUIDBEES TR 0.1-1.5pp/yr)
11:17 machine resumed after pause; NSE fetch alive and progressing (709/812 at 11:16, eta ~0.7h)
11:26 owner: keep the LIQUIDBEES proxy as written; S1 (VCP) variant to be decided later
11:27 NSE fetch crashed at member 750/812 (nse.py:134 parse_results_listing: a listing row came back as a str); builder s2-ep-results is on it, wait bm6odgwuh
11:28 fetch crash cause: FORCEMOT listing returned {data:[],msg:'no data found'}; fix PR #305; fetch resumed from #305 branch (log fetch-2026-10-28-scope-resume.log, ~30 min); parse waits on #305 merge; watcher b39odu7na
11:31 owner: build a full screener-style fundamentals store from cached NSE XBRL + screener pages -> builder fundamentals (brief briefs/fundamentals.txt)
11:32 #305 merged 70358e32 (worktree s2-ep-results deleted by --delete-branch again; resumed fetch PID 3049676 still running, 774/812). Told builder: parse/derive/A4 from main after fetch. wait bck8jeu1i
11:40 NSE fetch done 11:39 (812 members, 17,502 docs, no errors); parse running on hat_live from main; wait b2qapyp5d
11:56 A4 READY: report audits/2026-10-28-s2-ep-a4-validation.md. 18,204 rows / 810 instr; spot check 17/20; defects D1 (51 neg q4_derived), D2 (2 false revisions), D3 (188 owners-profit tag swap). STOP for owner: fix D1-D3 then Part C go?
12:14 owner: yes fix D1-D3 then start Part C. Sent the fix to s2-ep-results (wait b4ei2eet6). After merge: re-parse/derive, verify, then the C1/C2 in-sample sweep (2022-2024, no hold-out)
12:25 D1-D3 fix PR #307 (D1: 46 re-read + 3 excluded; D2: 2; D3: 174 flagged, profit agreement with secondary 53->100/102). Decided: rebuild the results+growth tables from the raw cache after merge (backup first). Watcher beiz1uqpz
12:31 #306 fundamentals merged (MERGE OK a74c055), builder cleaned
12:39 #307 merged; rebuild sent to s2-ep-results
12:42 REBUILD DONE: q4_derived neg 51->0, D2 0, D3 180 flagged; secondary agreement D1 37/40, D3 99/101
12:43 S2 notes windows set to 2022-2024 / 2025+ (backup .bak-2026-10-28); Part C sweep s2-ep-01 started (task bs52rigck, log backtests/s2-ep-01.log)
- 2026-10-28 13:0x: s2-ep-01 running; c1 5 trades, v1 4 (37 EP candidates in 3y, 10% gap floor binds) - plan rule <40 = too few, don't loosen.
- 2026-10-28: owner wants Qullamaggie EP whole market; stopped s2-ep-01 at 5/7; cleaned s2-ep-results; started builder s2-ep-wide (pane %9, brief briefs/s2-ep-wide.txt): whole-market universe, EP-only, 5m + results downloads, no tests.
- 2026-10-28: owner objected to whole-market universe (my assumption); s2-ep-wide stopped and cleaned up before any commit or download.
- 2026-10-28: owner: infra first (strategies/mixes/ETF as config). Builder backtest-infra pane %10, brief briefs/backtest-infra.txt, includes overlay Phase 1 + data completeness. No runs.
- 2026-10-28 ~14:35 UTC: #308 merged (9543ddb5) backtest infra: portfolio files, shared capital, ETF overlay Phase 1, tax. CodeAnt 4 fixed. Downloads running (logs hat-data-isin/logs/infra-2026-10-28/): kotak 5m ETA 01:30 UTC 10-29, then import + overlay store (chains repointed to main checkout). Results rerun 10-29 14:00 IST. Membership to 10-28, rebuild after 10-30. Builder backtest-infra (%10) kept alive to report INFRA DONE; don't cleanup before downloads end.
- 2026-10-28 20:35 UTC: 5m re-download is useful: 42,633 basis_mismatch days in ledger, 20,331 opened at high/low and are now accepted by #292 rule (bars_basis.py:135-146), recovered on re-import. Rest fail on intraday high/low misses >0.5% (needs investigation, not loosening). Dry-run counts tonight.
- 2026-10-29 02:35 UTC: cancelled scheduled results rerun (results_rerun_1029.sh, pid 3106837): only a top-up for Q2 FY27 filings, not needed for backtests; rerun later as a routine data update.
- 2026-10-29: owner wants scheduled daily data update (post-market, catch-up, manual run easy). Builder data-daily pane %11, brief briefs/data-daily.txt. Waits for infra 5m import before first real run.
- 2026-10-29 ~04:00 UTC: #309 merged (daily data update, timer 19:30 IST, catch-up). CodeAnt 6 fixed. Builder data-daily installs timer + first run after the 5m import.
- 2026-10-29 03:58 UTC: 5m import done: +11,194 member days (827k bars), +5,828 former days (428k bars) = 17,022 days recovered; still rejected basis_mismatch 14,556 + 12,325. ETF store to 10-28. Waiting data-daily first run + backtest-infra INFRA DONE.
- 2026-10-29 05:10 UTC: INFRA DONE. Coverage /data/workspace/audits/2026-10-29-backtest-data-coverage.md (5m 94.9% member-days; gap-day no-5m 22-25% from 40-51%). backtest-infra cleaned up. data-daily first run on results secondary; follow-up PR: weekly secondary + abs venv path.
- 2026-10-29 ~05:35 UTC: first daily update run OK, all 11 steps through 10-28. Timer hat-data-update.timer daily 14:00 UTC (19:30 IST). #310 merged (weekly secondary). data-daily cleaned up. Infra + data done; awaiting owner go on first runs.
- 2026-10-29: owner go on first runs. Portfolio files /data/workspace/backtests/portfolios/p1-ep-only, p2-vcp, p3-vcp-ep, p4-vcp-ep-etf (2022-2024, S1 rs_r075_ratio09 settings, S2 EP-only). Running bg b4dprik9y.
- 2026-10-29 06:50: p1-p4 ran (p1 01a18646, p2 01a1864d, p3 01a18653, p4 01a1865f). p4 invalid: ETF daily opens are auction outliers (NIFTYBEES 128 days >2% gap). Builder overlay-price-fix started.
- 2026-10-29: #311 merged (afdff73e), ETF store refreshed, p4 rerun 01a18680: CAGR 1.8% after tax (pre-tax tot 7.6% vs p3 10.6%), overlay costs ~45k, tax 20.8k, 199 rebal.
- 2026-10-29 ~08:00 UTC: owner mandate: full authority, legit strategy, review ~10-31. Research log /data/workspace/strategy-notes/research-2026-10-29.md. 3 research agents running (VCP leaks -> research/vcp-leaks, EP event study -> research/ep-study, momentum rotation -> research/momentum). Hold-out 2025+ untouched.
- 2026-10-29 08:15: momentum study done (27.9% CAGR in-sample, all folds beat). Builder rotation-engine %13 started. VCP + EP agents still running.
- 2026-10-29 08:40: VCP leak report saved. Sweep s1-leaks-01 running (bg bjibmfojq, log backtests/s1-leaks-01.log). S1 criteria windows -> 2016-2024 / 2025+. Disk /data 90% (cleared pip/uv caches).
- 2026-10-29 ~09:10: #312 merged (430c5a5f) rotation engine; seed c7d55ebe. s1-leaks-01: base refused not_one_change (rerun with bundle), x_sma50_2r 300 tr 0.66R, x_chand5 252 tr 1.11R; rest running.
- 2026-10-29T09:42Z s1-leaks-01 done (S1 dropped as core; chand5 best, ≈index). Base rerun s1-leaks-01b running; p5-rotation (default costs, liquid sleeve, tax) running; EP-A engine run delegated to an agent (p6-ep-a.yaml).
- 2026-10-29T09:46Z Rotation C1 hold-out FAILED (−13.9% CAGR vs TRI −1.4%, 2025Q1 momentum crash). Logged. No re-tuning on hold-out; next = paper-trade/forward test or crash-guard designed on in-sample only.
- 2026-10-29T09:58Z EP-A run 01a1870c: 14 trades, −1.3% CAGR; not a fair test (engine earnings lookup misses historical filings, 1 pass in 2023). Logged as open item.
- 2026-10-29T10:03Z S1 base 01a1870a-1258: 13.1% CAGR, DD −23.5; sweep PBO 0.94. Logged.
- 2026-10-29T11:09Z OWNER: focus switched to accuracy (data + bug-free backtests), profit later; private repo abhij1306/algotradingdata for record/data. Plan plans/accuracy-plan.md. Builders started: data-repo (%14, W0), data-verify (%15, W1), bt-verify (%16, W2 B1-B5). parity (B6) after B2. Strategy research paused until G3.
