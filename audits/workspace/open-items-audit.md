# Open-items audit vs main 2c31be6 (2026-10-24)

Read-only. Scope: `open-items.md` (C) all items, (C) Unverified, (D), and the code facts behind (A).
Paths are relative to `backend/app/hat/`. hat_live was read only through SELECTs and read-only CLIs
(`lineage report`, `coverage report`, `ca_demergers` without `--apply`).
Status key: **present**, **fixed**, **partly**, **n/r** (not reproducible).

## 1. (C) Known code gaps

### Money-safety and execution

| # | Item | Status | Evidence | Smallest fix |
|---|---|---|---|---|
| C1 | Desks only for ACTIVE accounts | present | `daily/accounts.py:237` filters `status == ACCOUNT_ACTIVE`. An account goes `failed` at `execution/accounts.py:135-139`. Exits are allowed for any status at `submit.py:225-227`, but without a desk there is no fill sync, GTT upkeep, exit rules or flatten after a restart. | Build a desk for every ACTIVE account and for every account with an open real `HatPosition`. Entries stay blocked by the existing gates. One file. |
| C2 | `record_broker_status` can un-terminal an order | present | `execution/order_book.py:185-187` copies `found.status` with no terminal guard. If a stale book shows a cancelled order as `open`, reconcile and the stop logic treat it as working again. | Ignore a move from a terminal status to a non-terminal one, and log it. One file. |
| C3 | Fill-sync fills not `broker_fact` | present | `engine/live_trades.py:171` (entry) and `engine/positions.py:258` (sale) call `journal.record` without `broker_fact` (`engine/journal.py:86,141`). A late fill on a Cancelled or ExitPending trade raises `LifecycleStateError`. The sync catches it and retries every minute forever (`daily/accounts.py:~432`), so HAT never books shares the broker holds. | Pass `broker_fact=True` at both calls, so the fill is stored as a `no_step` event and `qty_open` updates. Add one URGENT `fill.off_lifecycle` alert. Needs **Q2**. |
| C4 | Snapshot ignores part-filled remainder | present | `engine/snapshot.py:83-100` counts a pending slot only in TRIGGERED, AWAITING_APPROVAL and ENTRY_PLACED. After the first fill, only `qty_open` counts. | In `_slots`, add `signal.qty − filled` while a real entry order is working (`live_trades.entry_working`). This only restricts entries. |
| C4b | Late remainder fill after /flatten rests unsold | present (narrow) | `engine/live_trades.py:288` `_fire_again_late` re-fires the last sale's rules. A flatten has `rule_ids=()` (`execution/manage.py:196,429`), so nothing fires. | Send a follow-up flatten sale when a late fill lands on a flattened position. Needs **Q13**. |
| C5 | Take or placement after a failed break not refused | present | `execution/router.py:131-149` `placement_refusal` has no EntryWatch input. `entry_timeout.py:97-125` sees only placed orders, and the closes are in memory (`:80`). The reason is only logged (`daily/accounts.py:464`), and `entry_cancel.py:46-67` writes no reason. | Add `break_failed` to `PlacementCheck` (filled in `daily/entries.py` `LiveRoute.check` from EntryWatch) and return `BREAK_FAILED`. Put `reason` in the `order.cancelled` payload. Needs **Q7**. |
| C6 | `_preflight` doesn't re-read price after reconcile | present | `router.py:449-458`: `placement_refusal` runs, then `reconciler.run` (a broker round trip on the day's first entry), then the send with the old check and `now`. | Run the reconcile first and the placement refusal last, with a fresh `now`. This only adds refusals. |
| C7 | Decision-level band compares entry with itself | present, cosmetic | `engine/live_entry.py:299` passes `ltp=plan.entry`. Invariant 4 is still enforced on the real LTP at placement (`daily/entries.py:178-193` → `data/live.py:95` `usable_price`, `router.py:145-146`). | Drop the dead check, or fix its comment. Fold into the C5/C6 PR. |
| C8 | Lost earlier-session sales | present | `execution/manage.py:643-720` `_settle_earlier` and `:174-186` `earlier_sale_verdict`. (a) A SOLD or UNKNOWN verdict closes the rows with no `HatFill`, so the result has no proceeds. (b) `own = held − other HAT qty` counts the owner's own shares, so a sold position reads NEVER_SOLD, the rules re-fire, and HAT can **sell the owner's shares**. | (b) Record the owner's per-symbol holding baseline at reconcile, net it out, and return UNKNOWN plus an alert when the baseline is unknown. (a) Add an owner `resolve-sale` admin CLI (qty and price from the contract note) that writes the fill. Needs **Q12**. |
| C9 | `request_mode_change` accepts confirm/auto for a non-Live sleeve | present, latent | `execution/mode_changes.py:24-50` checks only account gates. Routing is safe (`modes.py:236` `bot_mode` → shadow). The accepted mode stays dormant and goes live on promotion without a fresh request. | Refuse a non-shadow mode while `routes_as_shadow(lifecycle)`, with `SLEEVE_NOT_LIVE`. Needs **Q9**. |
| C10 | `hat_event` not protected from TRUNCATE | present | hat_live `pg_trigger`: `hat_event` and partitions p202610-12 have only `hat_event_no_update` (BEFORE UPDATE/DELETE). `schema.py:~337`. There is no runbook step. The drift check (`schema.py:411-416`) does not compare triggers, so adding to `PG_DDL` is drift-safe. | Add a `BEFORE TRUNCATE ... FOR EACH STATEMENT` trigger to `PG_DDL` on the parent and on each partition where partitions are created. Add a runbook DBA step `REVOKE TRUNCATE` (a trigger cannot stop DROP or DETACH). Confirm that `ops/retention` never truncates or drops partitions. |
| C11 | ca.rescale (a) not gated on last fill sync, (b) no CA lookup for names new to tomorrow's watchlist, (c) a failure never URGENT | (a) present, (b) present, (c) n/r | (a) `daily/nightly.py:510` → `engine/rescale.py:358`, no `synced_at` check. (b) `rescale.py:238` reads the day's watchlist before the scan (`nightly.py:339,409`). (c) `JOB_DEADLINES[CA_RESCALE]` (`daily/assembly.py:201`) gives `job.failed` and `job.missed` at 09:00, both URGENT. | (a) `rescale()` raises `JobError("fills_not_synced")` until every desk has synced since the previous session; the scheduler retries. Needs **Q8**. (b) Run `lookup_actions` and `store_actions` again for the post-scan watchlist. (c) None, but check that `corporate_action.pending` is in `URGENT_ALERTS`. |
| C12 | Unverified: protect/follow on an unrescaled split | partly. **Real hole when the action is not stored** | Action stored but rescale not run: `manage_only` (`rescale.py:223-228`) → no view (`daily/exits.py:82-84`), entries blocked, `gtt_upkeep.verify` UNVERIFIED. Safe. Action **not** stored (MCP missed it; only `corporate_action.unchecked` fires, `nightly.py:344,424`): `hard_stop` compares the post-split price with the pre-split stop and sells the old `qty_open` at market. The old-scale GTT can also fire. The `manage.py:413` reference is stale. | Fail-closed guard in `manage_only`: if the open over the previous raw close is split-like (e.g. ≤0.6) and no action is stored for a held name, go manage-only and send an URGENT alert. Needs **Q3**. |
| C13 | MCP split/bonus factors vs `exact_factor` (D item, a money effect) | present | `engine/rescale.py:~112` uses `limit_denominator(1000)` with tol 1e-9. hat_live: 300 split/bonus rows fail (295 bonus, 5 split), almost all `mcp` rows stored to 4 dp (0.6667 ×130, 0.3333 ×59, 0.9091 ×25, 0.8333 ×23, 0.7143 ×20); 76 have ex-dates in 2024 or later. A held name through any of these goes manage-only and needs a manual resolve. | Accept the nearest small-denominator fraction when the stored factor is within 0.5e-4 of it (4-dp rounding). Rescale then uses the exact fraction. No data rewrite needed. |

### Corporate actions and data

| # | Item | Status | Evidence | Smallest fix |
|---|---|---|---|---|
| C14 | Demerger exit day still takes entries | present | Backtest: `_entries` (`backtest/loop.py:~597-603`) skips only `pending_on`, and `_demergers` (`:857`) sells at that close (`:383`). Live: `submit_trigger` (`engine/live_entry.py:374`) checks only `awaits_rescale`, and `due_positions` (`engine/demerger_exit.py:~85`) sells positions opened on the exit day. | Add a `demerger_exit_day` skip. Backtest: `(id, day) in data.demerger_exits`. Live: an open notice whose `exit_day(...) == trade_date` (helper in `data/demerger_notice.py`). The backtest result changes. Needs **Q5**. |
| C15 | Demerger notice never retired when the record date moves | present | `data/demerger_notice.py:127-158` only inserts, keyed `(instrument, ex_date)`. A moved date adds a second notice and the old one still fires (`engine/demerger_exit.py:70-76`). hat_live `hat_demerger_notice` is empty today. | When tonight's bc file parsed, delete `source=bc` notices with `ex_date > day` that the file no longer lists. First confirm on archived bc files that a pending demerger is listed every night until its ex-date. Needs **Q6**. |
| C16 | Live position held across an ISIN change | present | No lineage use in `execution/` or `engine/`. Series change (`execution/series.py:35`) is handled. An ISIN change makes a new instrument: the old id gets no ticks, so there is no exit view, and the new id can take a fresh entry. | Nightly, after `refresh_lineage`: an open position on the old side of a `linked` row → manage-only plus a one-off URGENT `position.isin_changed`, and block entries on the chain (like `unhandled_actions`, `rescale.py:200`). Add an invariant line. Needs **Q4**. |
| C17 | Lineage `decide` sees only two sides; ca_import `no_bars` across an ISIN change | present | `data/lineage.py:524-527` passes `actions[old] + actions[new]`. `data/ca_import.py:535-580` reads bars only for `ids(symbol, isin, ex_date)`. | Build the action list and bar ids from the whole chain (existing lineage map). Data only; stored series change, keys are not rewritten. |
| C18 | Missed bc-file night needs a manual catch-up | partly | `nightly.py:149-150` alerts `dividend.unchecked`. `data/ca_dividends.py:1094-1100` reads 7 days back, which covers it only if NSE keeps listing past the ex-date (unconfirmed). | Low value. Keep the alert and the manual tool, or add a "last bc day imported" marker and read the missed archive days. Not planned. |
| C19 | History MCP CA lookup per symbol, not ISIN | present | `data/history_cli.py:~104-117` `chosen.setdefault(symbol, ...)`. | Key by (symbol, ISIN), as `ca_import.ids` does. History tool only. |
| C20 | Adjusted prices not rounded before DOUBLE | partly | Money paths are exact (`backtest/data.py:489-507` `price_e4`). Signal doubles cast the raw product at `backtest/data.py:485-488` and `data/features.py:116-121`. | `CAST(round(x,4) AS DOUBLE)`. This changes the features digest. Recommend **won't fix** (Q15). |
| C21 | H7 jump skip inert | **n/r: it is live** | `backtest/data.py:630-648` `_skipped` → `lineage.unexplained_jumps`. `lineage report` on hat_live: 2769 unexplained jumps (tick 2509, rights_entitlement 219, etf 26, other 15). | None. Close the item. |
| C22 | Alerts (one PR) | A1 partly, A2 present, A3 **fixed**, A4 present, A5 present | A1: `daily/accounts.py:186-199` alerts only if the morning reconcile never succeeded; a later outage is silent. A2: `execution/fyers_broker.py:291-308`: per-process day count, no alert, `-360` → `FyersRateLimitedError` with no pause (pause only on 429, `:599`). A3: `router.py:323-338,367` `_end_stranded` → `ALERT_ENTRY_NOT_PLACED`. A4: `protect.py:312-322,383-385` alerts on every sync, and `telegram/notifier.py:46-68` has no dedup. A5: `fyers_auth.py:344-352` uses only `is_usable()`; the adapter's `-16` flag (`fyers_adapter.py:165-175`) is not consulted by `api/fyers_auth.py:78`. | A1: alert once a day after N minutes with no reconcile success; the gate is unchanged. A2: on the first `-360` or day-cap refusal, `exhaust_day()` and one alert; stops and sales keep priority (**Q11**). A4: dedup in `StopDesk.alert` keyed by (code, position, reason, trade_date). A5: status reports `connected=False` when the last profile check was refused. |
| C23 | Evidence and backtest consistency | E1 present, E2 partly, E3 present | E1: `backtest/evidence.py:426` `gate_evidence` calls `evidence_run` without `at`, so a replayed gate can see later runs. E2: `backtest/loop.py:337-340` uses the pinned version, while live uses the newest version holding `max_chase` (`live_entry.py:157-275`). Invariant 6 holds in both. E3: `loop.py:297` uses `DEFAULT_MULTIPLIERS`, while live uses the stored table (`allocation_service.py:80-92`). | E1: pass `at`. E3: thread the stored table into `RunSpec` and the spec hash. E2: keep pinned and document it (**Q14**). |
| C24 | Smaller gaps | see right | `StrategyConfig.execution_mode` (`engine/strategy/config.py:344`): never read, and new bots start at confirm (`versions.py:395-409`). Order events use wall time (`execution/order_book.py:340-367` → `events.py:~275 utc_now()`). The dashboard has no confidence column: the API exposes it (`api/dashboard.py:183-184,382-383`) but the frontend has no signals view. `ApprovalToken.tla:11` names a deleted test, and no test covers `telegram/tokens.py:90 ApprovalSigner`. | Remove `execution_mode` and its seed key (**Q10**). Pass the clock into `order_event` (refactor). Add a signals table with confidence and basis (frontend only). Add one pure sign/verify/tamper/expiry test and fix the TLA comment. |
| C25 | Unverified: BZ series refresh path | confirmed, with a lag | `reference.weekly` (`data/reference_jobs.py:70`, `instruments.py:555`) sets the series. `gtt.check` 08:40 → `_alert_series_change` (`manage.py:949-985`) sends `position.series_changed`, which is URGENT (`telegram/render.py:76`) and repeats nightly. The lag runs up to a week: the position is protected only by the old GTT until the weekly refresh. | None now. A daily series refresh for held names is optional. |
| C26 | Unverified: lock-wait probes in DB tests | present, no hang guard | `tests/hat/db/hat_db_runtime.py:97-104,674-681,821-828` and `hat_db_rules.py:510-516` poll `pg_stat_activity` for 5 s, then proceed. There is no `lock_timeout` or pytest-timeout; the only backstop is the CI `timeout-minutes: 10`. | `SET lock_timeout='5s'` on the db-test engine (`connect_args`). Test only. |

## 2. (D) Data review items

| Item | Result | Next |
|---|---|---|
| Strategy versions seeded before PRs 54-57 | **closed**: `hat_strategy_version` 0 rows, `hat_bot` 0 rows. | none |
| CCAVENUE 1:10 consolidation 2026-10-19 | **missing**. Lineage row INE483S01020→INE483S01038 is `review/prev_close_mismatch` (ratio 10.0, gap_factor 1). There is no `hat_corporate_action` row for either ISIN in 2026. AZADIND (×0.2, 2026-10-23), GOLDADD, SILVERADD and IVZINNIFTY (÷10 ETF splits) look the same. hat_live has 536 linked and 56 review (price_jump 52, long_gap 3, prev_close_mismatch 1). | Owner: `correct-action` (consolidation factor 10 on INE483S01020, 2026-10-19), then `lineage link`. Triage the 52 price_jump cases the same way. |
| Saturday sessions without index_daily | **5, not 6**. `coverage report`: index_missing 2012-03-03, 2012-04-28, 2012-09-08, 2013-05-11, 2014-03-22. 2012-01-07 is before index history starts. None is acked. | Owner: `coverage ack --note "special Saturday, index not in archive"`. |
| MCP factors vs `exact_factor` | 300 fail (see C13). | Code fix C13, in PR 6. |
| 18 disputed demergers | **confirmed**: `ca_demergers` dry run gives disputed 18. | (A) owner review |
| 6 demergers at first close | **confirmed**: `known_basis='resulting_first_close'` 6. | (A) owner |
| 35 hold-through demergers | **confirmed**: of 113 demergers, 14 have no `announced_on` and 21 have `announced_on` ≥ the last session before the ex-date. | (A) owner or research |
| Dividends with no amount | 0 stored with null cash (of 19,424). The CA3 "no_amount" rows are feed rows that were never stored, so they are absent rather than null. | (A) CA3 review stands |
| CA7 medium sources, 17 CA8 press dates, 5 unpriced ratios, pre-2011 misparses | not code; nothing to check read-only | primary-filing pass when convenient |

## 3. (A) code facts and what each answer implies

| Item | Fact still accurate? | Code per answer |
|---|---|---|
| Re-dated `known_on` doesn't delay pending | Yes: `data/ca_versions.py:~90 select`, `:115 pending_days`. No withdraw status (`:56-62`). | Withdraw: add a status that `select` and `pending_days` honour (`ca_versions.py`, `ca_corrections.py`). Accept: add an invariant line only. |
| Dividend and split on the same ex-date | Yes: `backtest/data.py:516`, `engine/trade_dividends.py:59` (pre-split shares). Whether the stored cash is per pre- or post-split share is unverified. | Pre: none. Post: `held_at_start` includes same-day rescale steps, and backtest cash ÷ split factor (`data.py` SQL or `loop.py:476-480`). |
| Live equity double-counts realised P&L | **Yes, and worse than listed.** `daily/entries.py:127` adds the all-time realised P&L to `allocation.capital`, which is `weight × broker funds().total` (`daily/accounts.py:345`) read at the **evening allocate** (`nightly.py:539`). The same sum feeds drawdown and health equity (`risk/drawdown.py:442,501`). decisions.md "at session start" is wrong. | Broker funds only: drop `_realised` for real bots in `entries.py` and `drawdown.py` (virtual keeps it). Config capital: change `accounts.py:345` and `allocator.py:175`. Session-start snapshot: add a 09:00 funds read on `hat_allocation_daily`. Fix decisions.md in each case. |
| Shadow fills zero fees | Yes: `engine/shadow.py:66-75`. decisions.md does not record the fees decision. | Wire: move `backtest/costs.py` charges and slippage to a shared module (`engine` may import only `backtest.spec` and `backtest.evidence`), and use a fee-bearing `FillModel` in shadow. Keep zero: add a decisions line. |
| PIT NIFTY 500 | Yes: `engine/portfolio/universe_service.py:~150-186`. `KNOWN_GAPS` (`backtest/spec.py:63-72`) has no entry. | Accept: add `universe_from_current_constituents` to `KNOWN_GAPS`. Source: a new constituents loader and a bulk path past `universe.py:57`. |
| PBO not gated | Yes: `backtest/runs.py:254`, with no consumer. | Gate: add `RunMetrics.pbo` (`evidence.py:~154`), a check in `engine/portfolio/lifecycle.py`, and a decisions line. |
| Defaults missing from decisions.md | Yes: `backtest/dsr.py:65-66` (5, 0.25/252), `lifecycle.py:47` (0.10), `risk/caps.py:21-25` (2%; stage2 5%, momentum-ep 2%). None is listed. | Confirm: add them to the "Defaults awaiting" list; change the constants if the values change. |
| Risk-increase gate reads expectancy only | Yes: `risk/policy.py:410 increase_gate_ok` ← `backtest/evidence.py:408`. A decrease **does** reset the trade window (`effective_version`, `policy.py:299`). | Add conditions: reuse the lifecycle span, gap and ambiguity predicates in `gate_evidence`. Accept: add an invariant line on the reset. |
| Rights issue GTT | Yes: `engine/rescale.py:19-26`. The position is manage-only and stays on the old GTT, with an URGENT `corporate_action.unhandled`. | Cancel: breaks "every position has a resting stop". Lower: invariant 1 change, plus `protect.py:722-731`, the stop-guard trigger, `rescale.py` and a TERP input. Keep: none. |
| Re-arm vs health peak | Yes: `risk/kill_ops.py:184` does not touch the `drawdown.py:~447-470 _snapshot_peak` that `engine/portfolio/health.py:42` reads. | Reset: `_snapshot_peak` starts at the bot's last `kill.rearmed`. No: none. |
| Smaller calls | All accurate: `position_desk.py:48` (60 s); `live_trades.py:~329` `closed_at = fill time`; `universe.py:~57-71` refuses same-day republish; `manage.py:28-37,~735` band-limit sale always on; `data/staleness.py:31` 30 s → no exit view; `risk/caps.py:82` cooldown per bot; "forbidden broker fact" is ambiguous (nearest: `protect.py:731` stop-would-move-down, ERROR only); ASM/GSM has no source (`series.py:13-14`); `data/universe.py:35-54` keeps EQ/BE ETFs; data-health kill trips only below 99% coverage (`quality.py:101`); `restate_dividends` writes no event (`nightly.py:363`). | Each is a one-constant or one-call change, apart from ASM/GSM (a new ingest) and same-day republish (in-place interval edit). See Q-A15. |

## 4. Build plan (PRs, money-safety first)

Two lanes, so two builders never touch the same file at once. Each PR lists its decisions; it starts only once they are answered.

| PR | Lane | Items | Files | Decisions | Depends / overlaps |
|---|---|---|---|---|---|
| 1 `hat/exit-desks-terminal` | A | C1 desks for failed accounts with open positions; C2 terminal-status guard | `daily/accounts.py`, `execution/order_book.py` | none | none. Start now. |
| 2 `hat/fill-broker-fact` | B | C3 fills as broker facts plus alert; C4 remainder in snapshot | `engine/live_trades.py`, `engine/positions.py`, `engine/snapshot.py` | Q2 | none |
| 3 `hat/live-equity` | B | (A) equity double count; fix decisions.md wording | `daily/entries.py`, `risk/drawdown.py`, `docs/decisions.md` | Q1 | after PR 2 (same lane; no file overlap) |
| 4 `hat/placement-recheck` | A | C6 re-check after reconcile; C5 break-failed refusal and cancel reason; C7 drop the dead band check | `execution/router.py`, `daily/entries.py`, `execution/entry_timeout.py`, `entry_cancel.py`, `daily/accounts.py`, `engine/live_entry.py` | Q7 | after PR 1 (`accounts.py`) and PR 3 (`entries.py`) |
| 5 `hat/held-instrument-guard` | B | C12 split-like gap with no stored action → manage-only; C16 ISIN change → manage-only plus alert | `engine/rescale.py`, `daily/exits.py`, `daily/nightly.py`, `docs/invariants.md` | Q3, Q4 | after PR 3 |
| 6 `hat/rescale-gating` | B | C11a sync gate, C11b post-scan lookup; C13 4-dp `exact_factor` | `daily/nightly.py`, `engine/rescale.py`, `daily/accounts.py` (expose `synced_at`) | Q8 | after PR 5 (`rescale.py`, `nightly.py`) and PR 4 (`accounts.py`) |
| 7 `hat/demerger-entries` | A | C14 no entry on the exit day; C15 retire moved notices | `backtest/loop.py`, `engine/live_entry.py`, `data/demerger_notice.py`, `daily/nightly.py` | Q5, Q6 | after PR 4 (`live_entry.py`) and PR 6 (`nightly.py`) |
| 8 `hat/earlier-sales` | B | C8 holding baseline and `resolve-sale` CLI | `execution/manage.py`, `execution/reconcile.py`, `admin.py` | Q12 | after PR 6. C4b (flatten follow-up, Q13, `live_trades.py` + `manage.py`) folds in here if Q13 = yes. |
| 9 `hat/mode-request` | A | C9 `SLEEVE_NOT_LIVE`; C24 remove `execution_mode` | `execution/modes.py`, `mode_changes.py`, `engine/strategy/config.py`, seed YAML | Q9, Q10 | none |
| 10 `hat/event-guards` | A | C10 TRUNCATE trigger plus runbook REVOKE step; C24 order-event clock (refactor half, separate commit) | `schema.py`, `docs/runbook.md`, `execution/order_book.py`, `submit.py` | none | after PR 1 (`order_book.py`) |
| 11 `hat/alert-hygiene` | B | C22 A1, A2, A4, A5 | `daily/accounts.py`, `execution/fyers_broker.py`, `protect.py`, `fyers_auth.py`, `fyers_adapter.py`, `api/fyers_auth.py`, `telegram/render.py` | Q11 | after PRs 4 and 6 (`accounts.py`) and PR 8. No `pnpm gen:api` unless the status model changes. |
| 12 `hat/shadow-fees` | A | (A) shadow cost model | new shared costs module, `engine/shadow.py`, `backtest/costs.py` | QA4 | none |
| 13 `hat/evidence-consistency` | A | C23 E1 `at`, E3 stored regime table; (A) PBO gate and `KNOWN_GAPS` membership entry if answered | `backtest/evidence.py`, `loop.py`, `spec.py`, `engine/portfolio/lifecycle.py` | Q14, QA5, QA6 | after PR 7 (`loop.py`) |
| 14 `hat/lineage-chain` | B | C17 whole-chain decide and ca_import; C19 history CLI per ISIN | `data/lineage.py`, `data/ca_import.py`, `data/history_cli.py` | none | none (data). Re-run the `lineage report` before and after on hat-data. |
| 15 `hat/test-hygiene` | any | C24 signer test and TLA comment; C26 `lock_timeout` | `tests/hat/...`, `tests/hat/db/conftest`, `verification/tla/ApprovalToken.tla` | none | none |
| 16 `hat/dashboard-confidence` | any | C24 signals table with confidence | `frontend/app/hat/` | none | none |

Closed, or not planned: A3 (fixed), C11c (n/r), C21 (H7 is live), C18 and C20 (won't fix unless asked), C25 (works, weekly lag), and the D strategy-version and null-dividend checks (closed).
Owner data acts with no PR: CCAVENUE and the similar consolidations, plus `coverage ack` for the 5 Saturdays.

## 5. Owner decisions (recommended option first)

Blocking a PR:

- **Q1 Live equity (PR 3).** What is the equity for sizing and drawdown? **(a) Broker funds total only, read at the evening allocate; realised P&L added only for virtual (shadow) books; decisions.md corrected** / (b) config capital + realised / (c) a funds snapshot at 09:00.
- **Q2 A broker fill the lifecycle refuses (PR 2).** **(a) Book it as a broker fact (qty_open updates, so the stop logic covers it) plus an URGENT alert** / (b) keep refusing and only alert.
- **Q3 Split-like gap with no stored action on a held name (PR 5).** **(a) Manage-only plus URGENT until the owner resolves it (a real −40% crash then waits for the owner)** / (b) leave it; normal stops fire.
- **Q4 Held position across an ISIN change (PR 5).** **(a) Manage-only plus URGENT, and no entries on the chain** / (b) move the position to the successor instrument automatically.
- **Q5 Demerger entry block (PR 7).** **(a) Live: no entry from the exit day until the factor is stored (matches the backtest's `pending`)** / (b) exit day only.
- **Q6 Notice retire (PR 7).** **(a) Retire a bc notice the file stops listing, only after the builder shows on archived files that the file lists a demerger nightly until its ex-date; otherwise alert instead of retiring** / (b) never auto-retire; alert the owner.
- **Q7 Failed-break refusal after a restart, when the in-memory closes are gone (PR 4).** **(a) Rebuild the closes from today's `bars_5m`; fail open only if there are no bars** / (b) fail open / (c) refuse every Take after a restart until the next 5-minute close.
- **Q8 ca.rescale when an account cannot sync (PR 6).** **(a) Retry until the 09:00 deadline, then the job fails URGENT and the affected positions stay manage-only** / (b) alert and proceed.
- **Q9 Mode request for a non-Live sleeve (PR 9).** **(a) Refuse; after promotion the owner requests the mode again** / (b) accept as today (dormant).
- **Q10 `StrategyConfig.execution_mode` (PR 9).** **(a) Remove the field and its seed key** / (b) reject anything but shadow.
- **Q11 Fyers day budget spent or `-360` (PR 11).** **(a) Block new entries and reads that can wait, never stops or sales, and one alert** / (b) alert only.
- **Q12 Lost earlier-session sales (PR 8).** **(a) Reconcile holding baseline plus an owner `resolve-sale` CLI from the contract note** / (b) tradebook import / (c) owner resolve only.
- **Q13 Late fill after /flatten (PR 8).** **(a) Follow-up sale under the original flatten confirmation** / (b) alert only.
- **Q14 Backtest max-chase and regime table (PR 13).** **(a) Max-chase stays on the pinned version (document it); regime uses the stored table at run time** / (b) both follow live history.
- **Q15 Rounding before DOUBLE (C20).** **(a) Won't fix (signals only)** / (b) round to 4 dp and accept the features rebuild.

The (A) list, each answer's code in §3:

- **QA1 Re-dated known_on:** **(a) accept + invariant line** / (b) build withdraw.
- **QA2 Dividend with split, same ex-date:** **(a) owner checks TCS 2018-05-31 at the source; keep pre-split unless it says post** / (b) switch to post now.
- **QA3** = Q1.
- **QA4 Shadow fees:** **(a) wire the backtest cost model into shadow (PR 12)** / (b) keep zero and record it.
- **QA5 PIT NIFTY 500:** **(a) accept the bias now with a `KNOWN_GAPS` entry, source later** / (b) block the 5-year run until a source exists.
- **QA6 PBO gate:** **(a) gate promotion at PBO < 0.5** / (b) record only.
- **QA7 Defaults (DSR 5 and 0.25/252, ambiguous 10%, max-chase 2/5/2%):** **(a) confirm as is; list them in decisions.md** / (b) change some (say which).
- **QA8 Risk-increase gate:** **(a) add the span, gap and ambiguity conditions; a decrease resetting the window is intended** / (b) expectancy only.
- **QA9 Rights GTT:** **(a) keep as is (manage-only, old GTT, URGENT alert; owner may /flatten)** / (b) lower by TERP (invariant change) / (c) cancel.
- **QA10 Re-arm and health:** **(a) a re-arm also restarts the health peak** / (b) no.
- **QA11 18 disputed / 6 first-close demergers / CA3 85 rows / CA7 factors / 35 hold-through:** data reviews; **(a) accept hold-through for the 35 and review the rest in one correction list** / (b) a research pass on NSE filings first.
- **QA12 Muhurat and the 2027 list:** parked (B) and out of scope.
- **QA15 Smaller calls:** (a) is recommended on each:
  - 60 s lost-stop settle: **keep until measured**.
  - `closed_at`: **keep the fill time** (it is right).
  - Same-day republish: **keep refusing**.
  - Band-limit sale: **keep always on** (it is an exit).
  - Illiquid 30 s: **fall back to the last trade for exit views only, never for entries**.
  - Cooldown: **per bot**.
  - Stop-would-move-down: **add an alert**.
  - ASM/GSM: **park**.
  - ETFs and -RE in the ingest universe: **keep (unranked)**.
  - Bars gap: **keep the 99% rule**.
  - Restatement: **add a journal event**.
