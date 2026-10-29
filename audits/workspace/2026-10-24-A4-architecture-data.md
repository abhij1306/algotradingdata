# architecture audit: backend/app/hat/data (ca_*, lineage, features, instruments, minute_history)  (2026-10-24, main @ 1a7aa75)

## Summary
The scope is about 9,300 lines. It is correct in its parts: `ca_known`, `ca_versions` selection and `features` incremental state are deep modules with small pure seams. As a whole it has poor locality. The concept "a demerger" has no type; three different free-text predicates decide what counts as one, and the owner's correction list writes the owner's note as that text. The version ledger is a side protocol that seven write sites pair by hand with the `hat_corporate_action` projection, and only a CLI checks it. The adjusted series' input (`stored_adjustment`, the chains) lives inside the 1,309-line lineage-discovery module, and chain membership is re-derived in three other places. The importers share a hidden kernel inside `ca_import`. **Fix first: make the demerger a stored type (F1).** Today what a backtest forces out of, what `ca_demergers` estimates and what `point_in_time` dates all depend on whether the word "demerger" appears in a text field.

## Findings

### F1. A demerger is identified by free text, three ways, and the owner's note overwrites that text   [High] [Confirmed] [Strong]
Files: backend/app/hat/data/point_in_time.py:199-201, backend/app/hat/data/ca_import.py:99, backend/app/hat/data/ca_import.py:604-609, backend/app/hat/data/lineage.py:112, backend/app/hat/data/lineage.py:444, backend/app/hat/data/ca_corrections.py:183-190, backend/app/hat/data/ca_corrections.py:270-273, backend/app/hat/backtest/data.py:716-726, backend/app/hat/data/demerger_notice.py:216-225, backend/app/hat/data/ca_demergers.py:159-185
Problem: Demergers are stored as `action_type = "other"`, the same type as rights issues. Code tells them apart only by `raw_text`, and it does so three ways:
- `point_in_time.demerger_text` checks that "demerger" appears anywhere in the text. The backtest's forced demerger exits (`backtest/data.py:_demerger_rows`), `demerger_notice.announce_stored`, `ca_demergers.plan` and the CA5 `classify` all use it.
- `ca_import.Stored.kind` checks that the text *starts with* "demerger". `ca_import.decide` and `ca_research.decide_demerger` use it for same-event matching and same-day factor division.
- `lineage.RESTRUCTURING` is a regex used to review ISIN changes near a restructuring.

The owner's correction list stores `raw_text = note` (`add_action`, ca_corrections.py:187). A `move` op deletes the row and re-adds it with the note as its text (ca_corrections.py:270-273). So a demerger moved with the note "ex-date per bars, NSE file off by one":
- is no longer a demerger to the backtest, which drops its forced exit;
- is dropped by `ca_demergers` (no estimates, no disputed check) and by `announce_stored`;
- is treated as a rights-type `other` by the importers' near-match. A later file or research import of the same event is then not deduplicated as "already stored". In the best case it goes to review (`same_day_action`). If the moved date falls outside the before/on window, a second demerger factor can be stored (Plausible: the price gate usually catches it).

Conversely, a rights or bonus note that mentions a demerger becomes one. None of this fails loudly.
Fix: Make the kind data. Add a `demerger` action type, or a `kind` column. A one-time `PG_DDL` step retypes the rows `demerger_text` matches today, after the owner reviews the list. Put one predicate in `corporate_actions` (`is_demerger(row)`), and use it for the backtest, `demerger_notice`, `ca_demergers`, `point_in_time` and the importers' `Stored.kind`. `correct-actions move` should carry the stored row's type and text forward and put the note only in the journal and version text.
Tests: a pure test that `_one(move)` keeps the moved row's kind and text. A pure test of `is_demerger` over typed rows. Nothing text-based remains to test.
Size: M.

### F2. The version ledger is a side protocol that seven write sites pair by hand; the projection is checked only from a CLI   [Medium] [Confirmed] [Strong]
Files: backend/app/hat/data/ca_versions.py:163-280, backend/app/hat/data/corporate_actions.py:279-292, backend/app/hat/data/corporate_actions.py:539-585, backend/app/hat/data/ca_corrections.py:183-195, backend/app/hat/data/ca_dividends.py:974-992, backend/app/hat/data/ca_demergers.py:270-276, backend/app/hat/data/point_in_time.py:402-411, backend/app/hat/data/ca_versions.py:366-386, backend/app/hat/data/point_in_time.py:598-620
Problem: The invariant "every write of a corporate action appends a version in the same transaction" holds today because each writer does two separate things: it mutates a `HatCorporateAction` row (assigning `adjustment_factor`, `cash_amount`, `known_on` or `known_basis`, or calling `session.delete`), and it calls `Ledger.add_row` or `Ledger.delete` with the right `source`, `text` and `published_on`. Because `add_row` copies the row "as just written", the call order matters too.

There are seven sites in five modules. The proof that the two agree is `projection_mismatches`, and it runs only from `point_in_time report` and `versions` (point_in_time.py:594, 604). The nightly `ca.adjust` never runs it. The next writer that forgets the ledger call, or calls it before setting `known_on`, silently breaks what the backtest selects (`select(versions, D)`), and nothing alerts.
Fix: Deepen `Ledger` into the only writer of `hat_corporate_action`. Calls such as `ledger.accept(key, factor, cash, known, source, text)`, `ledger.vacate(key, available, note)` and `ledger.conflict(...)` would append the version and update the projection row together. Callers would never assign row fields. The seam is the `Ledger` interface, and the `hat_corporate_action` row becomes an implementation detail. Separately, run `projection_mismatches` at the end of `ca.adjust` and alert on a non-zero count. It reads two tables and is cheap.
Tests: a pure property that, for any sequence of `accept` and `vacate` calls, the projection equals `select(versions, None)`. `test_ca_versions.py` already has the comparison helper.
Size: M.

### F3. `ca_demergers --neutral` rewrites stored factors outside the owner-correction path   [Medium] [Confirmed] [Strong]
Files: backend/app/hat/data/ca_demergers.py:270-276, backend/app/hat/data/corporate_actions.py:319-337, docs/invariants.md (Owner corrections)
Problem: The invariant says "A stored factor ... changes only through the owner's `correct-action` / `correct-actions` (journalled ...) or a lineage `link` / `unlink`." `ca_demergers.apply(neutral=True)` assigns `row.adjustment_factor = factor` directly. It appends a version but records no `corporate_action.corrected` event. As a result:
- `owner_vacated` and `point_in_time.owner_keys` do not know the owner set this value;
- the CA5 `classify` would treat it as an import row;
- the audit trail of "who changed this factor and why" exists only as a version text.

This is a conflict with an invariant, and it is not yet live: `--neutral` waits for owner approval (decisions.md, Demergers). That makes now the cheap time to fix it.
Fix: Route `--neutral` through `correct_action`, one `Correction` per demerger with the note "index-neutralised gap, owner approved" and a `known_on`. Alternatively, record `EVENT_CORRECTED` in the same transaction. Either way, the cross-check versions stay as they are.
Tests: none new. `correct_action` is already the tested path.
Size: S.

### F4. The adjusted series' input lives in the lineage-discovery module, and chain membership is re-derived in four places   [Medium] [Confirmed] [Strong]
Files: backend/app/hat/data/lineage.py:511-519, backend/app/hat/data/lineage.py:584-702, backend/app/hat/data/ca_import.py:492-521, backend/app/hat/data/point_in_time.py:295-308, backend/app/hat/data/point_in_time.py:668, backend/app/hat/backtest/data.py:45, backend/app/hat/daily/market.py:24, backend/app/hat/daily/nightly.py:42, backend/app/hat/data/features.py:981
Problem: Every reader of `bars_daily` (features, backtest, live market, nightly) takes its `Adjustment` from `lineage.stored_adjustment`. That function, with `chains`, `chain_factors` and `chain_dividends`, is the definition of "what the adjusted series applies". It sits in `lineage.py`, a 1,309-line module that also holds:
- the NSE list parsers;
- the succession rules (`candidates`, `decide`);
- overrides;
- `save_decisions`;
- the jump review report, which also pulls in `ca_dividends.missing_amounts`;
- `show_chains`;
- a CLI.

So a change to the review report and a change to which copy of a split a chain applies land in the same file. Meanwhile, three other modules each re-query `HatIsinLineage` and rebuild chains themselves:
- `ca_import.load_reference` (its own union-find, `status == "linked"` as a literal);
- `point_in_time.neighbours` (adjacency only, also a literal);
- `lineage.chain_members` beside `lineage.chains`.

A change to what counts as linked must be found in four places.
Fix: Create one `adjustment` module, or a `chains` module, holding `stored_links`, a `Chains` read model (`head`, `depth`, `members`, `neighbours`), `chain_factors`, `chain_dividends` and `stored_adjustment`. `lineage.py` keeps succession discovery, build and override, review and CLI. `ca_import.Reference.chain` and `point_in_time.neighbours` read `Chains`. The deletion test says this module earns its keep, because five callers outside `data/` need it.
Tests: the existing `test_lineage.py` properties for `chains` and `chain_factors` move with it unchanged.
Size: M.

### F5. `ca_import` is the hidden shared kernel of every corporate-action importer   [Medium] [Confirmed] [Worth exploring]
Files: backend/app/hat/data/ca_research.py:76-111, backend/app/hat/data/ca_dividends.py:73-91, backend/app/hat/data/point_in_time.py:46-54, backend/app/hat/data/ca_demergers.py:49, backend/app/hat/data/ca_import.py:928-966, backend/app/hat/data/ca_dividends.py:960-1021, backend/app/hat/data/ca_import.py:1031-1040, backend/app/hat/data/ca_research.py:1201-1214, backend/app/hat/data/ca_dividends.py:1168-1177
Problem: `ca_import.py` is described as "the corporate-action file import" for one NSE SQLite file. In practice it is the kernel for all the importers:
- `ca_research` imports 34 of its names, including the workflow internals `decide`, `settle`, `dedupe` and `Context`;
- `ca_dividends` imports 17;
- `point_in_time` and `ca_demergers` import the price gate, the raw-bar windows and `same_factor`.

The kernel is the price gate, the `Bar` windows over `bars_daily_raw`, the statuses, `Reference` and `CaFileError`. Changing anything about the file importer risks the others.

The shape is also duplicated. There are two `apply` functions, each running `load_actions`, then a `ca_import_raced` check, then `events.record(EVENT_IMPORTED)` with nearly the same payload. There are three copies of the "path under the cwd with a suffix" guard and two sha256 helpers.
Fix: Extract `ca_gate` (`Bar`, `read_windows`, `read_first_closes`, `around`, `gate`, `Verdict`, `same_factor`, `Reference`, `load_reference`) and a small `ca_apply` (statuses, the journalled `apply` that takes outcomes to records, `input_path`, `digest`). `ca_import`, `ca_research` and `ca_dividends` then become adapters that turn their files into proposals.
Tests: the existing gate properties move with `ca_gate`. Nothing new.
Size: M.

### F6. The live nightly dividend and `bc`-file path is buried in a 1,246-line one-off importer   [Medium] [Confirmed] [Worth exploring]
Files: backend/app/hat/data/ca_dividends.py:499-543, backend/app/hat/data/ca_dividends.py:1085-1165, backend/app/hat/daily/nightly.py:467, backend/app/hat/daily/nightly.py:496, backend/app/hat/data/lineage.py:74, backend/app/hat/data/lineage.py:1135
Problem: `ca.adjust` calls three things in `ca_dividends`:
- `ca_dividends.read_bc` to parse the night's `bc` file. The demerger notices go through this too, so demerger parsing depends on the dividends module.
- `ca_dividends.nightly_import`.
- `missing_amounts`, which `lineage.review_report` also uses.

These sit beside the monthly-feed JSON and bonus-file CLI (`read_feed`, `read_bonus_file`, `bonus_proposals`, `main`), which is operator-only. Any change to the one-off import touches the module the nightly chain depends on, and the import graph has `lineage` depending on `ca_dividends`.
Fix: Move the `bc` file (`FeedRow`, `read_bc`, `bc_subject`) into its own module, used by both `ca_dividends` and `demerger_notice`. Keep `nightly_import`, `missing_amounts` and the shared `evaluate`/`apply` beside it as the live path. Leave the feed and bonus CLI as an adapter on top.
Tests: the existing `read_bc` and `payouts` properties move unchanged.
Size: S to M.

### F7. "Latest ingest run wins" is hand-written in SQL in at least six places   [Low] [Confirmed] [Strong]
Files: backend/app/hat/data/ca_import.py:533-546, backend/app/hat/data/lineage.py:709-741, backend/app/hat/data/bars_basis.py:130-134, backend/app/hat/data/history_validation.py:72, backend/app/hat/data/store.py:379-381, backend/app/hat/data/store.py:748-758
Problem: Each raw-bar reader re-implements the dedup rule, using either `arg_max(x, ingest_run_id)` or `QUALIFY row_number() ... ORDER BY ingest_run_id DESC`. The rule relies on uuid v7 byte order being time order, which is stated once, at store.py:28. `DataStore` builds latest views only for the adjusted series, not for `bars_daily_raw`. A change to the rule, such as a tie-break on source, has to be found by grep.
Fix: Have `DataStore.connect` also create a `bars_daily_raw_latest` view. The importers, `lineage.read_spans` and `bars_basis.store_daily` would then select from it.
Tests: none. The view is one SQL constant.
Size: S.

### F8. ISIN classification is spelled four ways, and the rules disagree   [Low] [Confirmed] [Worth exploring]
Files: backend/app/hat/data/features.py:100, backend/app/hat/data/features.py:208-210, backend/app/hat/data/ca_import.py:665-668, backend/app/hat/data/ca_dividends.py:314-317, backend/app/hat/data/lineage.py:1006
Problem: The four checks are:
- `features.ORDINARY_EQUITY` accepts `IN[E9]` with type `01`.
- `ca_import.equity_share_isin` accepts `INE` with type `01`, so it excludes IN9 DVR shares from being a demerger's resulting company.
- `ca_dividends.equity_row_isin` accepts `INE` or `IN9` of any type, so it also passes type `20` rights entitlements.
- `lineage.jump_kind` checks `isin[7:9] == "20"` and `INF`.

The invariant defines ordinary equity once ("ISIN `IN` + `E` or `9` + issuer + type `01`"). Whether the importers' differences are intended cannot be seen from the code.
Fix: Create one small `isin.py` with named predicates (`ordinary_equity`, `rights_entitlement`, `etf_unit`). Each caller picks the one it means, and an intended difference becomes a name.
Tests: one pure table test of the predicates.
Size: S.

### F9. `instruments.py` changes for five reasons, and `demerger_notice` re-implements its symbol lookup   [Low] [Confirmed] [Worth exploring]
Files: backend/app/hat/data/instruments.py:66-660, backend/app/hat/data/instruments.py:671-812, backend/app/hat/data/instruments.py:816-915, backend/app/hat/data/instruments.py:238-261, backend/app/hat/data/demerger_notice.py:134-162
Problem: The 915 lines hold five unrelated concerns:
- the instrument master upsert;
- symbol-history interval logic (`claim`, `repair_plan`);
- broker symbol mapping for Fyers and for Kite;
- price bands;
- industries.

Separately, `demerger_notice._instruments_of` repeats `resolve_symbol`'s symbol-history query. It has no `market_id` filter, returns every holder instead of the preferred one, and falls back to the current symbol. That makes two rules for "which instrument was SYMBOL on DAY".
Fix: Split `broker_symbols.py` (the Fyers and Kite refresh and `_replace_broker_rows`) and `symbol_history.py` out of `instruments.py`. Give `instruments` a `holders(session, market_id, symbol, day)` that both `resolve_symbol` and `demerger_notice` use. The demerger fallback to the current symbol can stay as an explicit second step.
Tests: none new.
Size: M.

### F10. Finished CA5/CA6 back-fill code is still live, and `backfill` would re-date undated owner corrections   [Low] [Plausible] [Worth exploring]
Files: backend/app/hat/data/point_in_time.py:204-246, backend/app/hat/data/point_in_time.py:365-456, backend/app/hat/data/point_in_time.py:575-596, backend/app/hat/data/ca_versions.py:391-531, docs/runbook.md:219
Problem: The back-fills of `known_on` (CA5) and of the version ledger (CA6) are migrations. The runbook lists only `point_in_time report` and `pending`. Still, about 300 lines of `classify`, `plan_backfill`, `apply_backfill`, `versions_backfill`, `journal` and `versioned_keys` stay in the module the backtest imports (`chain_pending`, `demerger_text`).

`backfill --apply` dates every row whose `known_basis` is NULL, and that includes an owner correction saved without `--known-on`. For a gate-confirmed split or bonus, `classify` gives it `ex_open`. The runbook says such a value stays undated, so the backtest skips the name. Re-running the old tool would quietly contradict that. To confirm: ask the orchestrator or owner whether `backfill` and `versions` are retired.
Fix: If they are retired, delete them per CLAUDE.md (the deletion test passes: nothing live calls them), along with `classify`'s tests in `test_ca_known.py`. If not, refuse rows with `source == owner` in `plan_backfill`.
Tests: none, or one pure test that `plan_backfill` skips owner rows.
Size: S.

### F11. Lineage verdicts are rewritten nightly with no journal, unlike the actions they adjust beside   [Low] [Confirmed] [Worth exploring]
Files: backend/app/hat/data/lineage.py:778-821, backend/app/hat/data/lineage.py:957-974, backend/app/hat/daily/nightly.py:400-421
Problem: Actions get a version for every write. The owner's lineage `link`/`unlink` is journalled (`lineage.overridden`). But the nightly `refresh_lineage` → `save_decisions` creates, updates or deletes `linked` rows silently: there is a count in the log, and an alert only for new review cases.

A link that appears or disappears changes every adjusted series of the chain, and it changes the `position.isin_changed` lock. Afterwards, nothing says when a chain gained or lost a member. This matches the decision "point in time, not full as-of rebuild", so it is not a conflict, but it is a gap in the audit trail.
Fix: In `save_decisions`, record one event per pair whose status crosses `linked`, in the same transaction. These are deltas only, a handful a year.
Tests: a pure test of the delta function (old rows, decisions) → transitions.
Size: S.

### F12. The minute-history raw basis reads a second factor list, not the adjusted views'   [Low] [Confirmed] [Speculative]
Files: backend/app/hat/data/minute_history.py:806-815, backend/app/hat/data/corporate_actions.py:421-432, backend/app/hat/data/bars_basis.py:3-10, backend/app/hat/data/bars_basis.py:110-125
Problem: The `bars_basis` docstring says the Fyers factor is "the factors `bars_daily_cap_adj` multiplies by". But `minute_history._basis` reads `corporate_actions.stored_factors`, which is per instrument, takes every copy and has no chain. The view uses `lineage.stored_adjustment`, which is chain-keyed and takes one copy per chain. Today the envelope check (`check_day`) fails closed, and pre-ISIN-change days have no raw daily bar under the new id, so no wrong bar is written. The divergence would only show as rejects. It is still a second factor reader with its own rule.
Fix: Build `RawBasis` from `stored_adjustment().factors` (chain id → current instrument), or correct the docstring to name the rule it actually uses.
Tests: none.
Size: S.

### F13. Operator advice to run `features --full` after imports appears stale against `run_features`   [Low] [Plausible] [Speculative]
Files: docs/runbook.md:221-223, backend/app/hat/data/ca_demergers.py:331-333, backend/app/hat/data/ca_research.py:1224-1225, backend/app/hat/data/features.py:318-345, backend/app/hat/data/features.py:808-818
Problem: The runbook and two CLIs tell the operator to run `features --full` after dividends, `--neutral` or research imports. But `adjustment_lines` covers factors, dividends and lineage, and `_run_locked` recomputes the affected chains, or everything once `MAX_CHAINS` is exceeded. A `--full` rebuild covers about 4,150 dates. To confirm: run `features` (incremental) after a small correction on real data and compare against `--full`.
Fix: If the incremental run matches, drop the `--full` advice.
Tests: none.
Size: S.

## Suggested PRs
1. **Demerger as a type (F1):** add the `demerger` type and a reviewed retype DDL, one `is_demerger` predicate, and make `correct-actions move` keep the row's type and text.
2. **Ledger owns the projection (F2, F3):** `Ledger.accept`/`vacate` become the only writers of `hat_corporate_action`, `ca.adjust` alerts on projection mismatches, and `--neutral` goes through `correct_action`.
3. **Adjustment and chains module (F4, F7, F12):** one `Chains` read model and `stored_adjustment` outside `lineage.py`, a `bars_daily_raw_latest` view, and the minute basis built from the same factors.
4. **Importer kernel split (F5, F6, F8):** `ca_gate` and `ca_apply` out of `ca_import`, the `bc` file and the nightly dividend path out of the feed CLI, and one `isin.py`.
5. **Reference and housekeeping (F9, F10, F11, F13):** split broker symbols and symbol history out of `instruments`, retire the CA5/CA6 back-fills, journal nightly lineage transitions, and correct the `--full` advice.
