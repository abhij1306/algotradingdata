# Data review, hat_live, 2026-10-24 (preparation only)

Nothing was written to hat_live. Every query ran read-only, and the lineage report and simulation ran with `default_transaction_read_only=on`. The two lists were dry-run with `admin correct-actions --list` (no `--apply`), and that dry run rolls back each line's savepoint. No network calls, no backtest, no repo change. Bars: `hat-data-isin/bars_daily_raw` (to 2026-10-23). Sources: `/data/workspace/ca-data` (NSE splits/bonus CSVs, monthly CA feed JSON, board meetings).

## Outputs (all under `/data/workspace/hat-data-isin/admin/`)

| File | Lines | Dry run |
| --- | --- | --- |
| `review-2026-10-24-c19.tsv` | 297 (295 delete, 1 delete + 1 add) | 297 would, 0 refused |
| `review-2026-10-24-lineage.tsv` | 36 add | 36 would, 0 refused |
| `review-2026-10-24-lineage-links.txt` | 24 `lineage link` commands, no unlink | (not a dry-run tool; simulated, below) |

The two lists touch no common key, so their order doesn't matter, but apply them in the order below.

## Apply order

1. `$ADMIN correct-actions --list review-2026-10-24-c19.tsv --apply`
2. `$ADMIN correct-actions --list review-2026-10-24-lineage.tsv --apply`
3. The 24 commands in `review-2026-10-24-lineage-links.txt` (from `backend`, `HAT_TELEGRAM_CHAT_ID` set).
4. `python -m app.hat.data.lineage build` (the usual symbol/name-change source), then `lineage report --limit 200`. Expect `591 linked, 1 for review` (KAUSHALYA).
5. `python -m app.hat.data.features` (no dividend or neutral change, so not `--full`).
6. Per the ca-safety follow-up: rerun `ca_import --db <file>` dry. Apply only if the `no_bars` review list shrinks for real.

**Simulation (step 4 checked in advance).** I ran the lineage rules in memory: `candidates` → `decide_all` → `apply_overrides`, on the stored actions with both lists applied and the 24 links added. Results:
- The 592 stored verdicts were reproduced, with one cosmetic difference: `INF179KC1HE2→INF179KC1JG3` comes out linked as `isin_reissue` rather than `name_change`, because the NSE name-change list could not be fetched here.
- After the change: 591 linked, 1 review (KAUSHALYA), no fork.
- Nothing outside the 51 cases changes verdict. The 295 C19 deletes move no lineage decision.

## 1. C19: 296 MCP rows on the wrong ISIN

**The 296 rows.** I reproduced the PR's 296 exactly, using its own rule: the "asked" instrument is the active one per shared symbol, then the lowest id. The row's place is the instrument `resolve_symbol` gives for (symbol, ex-date).

**295 rows are pure duplicates.** The ISIN that held the symbol on the ex-date already stores the same (ex-date, type) with the same factor, from the same MCP load.
- Fix: `delete` on the asked ISIN, not a move. A move would be refused with `action_key_taken`.
- By lineage between the two ISINs: 258 linked, 6 review, 31 no direct lineage row.
- For linked chains the delete changes no adjusted price (`chain_factors` collapses copies). For the 37 others it removes a factor stored on an instrument that did not trade the symbol that day.

**1 row is a real move: AVANTIFEED 2015-11-26 split 0.2.**
- It sits on INE871C01038. INE871C01012 traded AVANTIFEED that day (its last session) and held no copy.
- Evidence: NSE CA file lists the FV Rs10→Rs2 split under INE871C01012 (ex 26-Nov-2015, record 27-Nov-2015). Prev close 2636.50, ex open 531.00, gap 0.2014.
- Fix: delete on …038, add on …012 with `known_on` = the ex-date.

**Evidence per row** is in each line's note: prev close and ex open on the symbol, and the gap vs the stored combined factor on the holder.
- 288 rows: the gap is within 12% of the combined factor.
- 8 rows don't match on the open, but the close and NSE confirm the factor. They are all deletes of duplicates either way:

| Row | Open gap | Confirmed by |
| --- | --- | --- |
| CUPID 2018 bonus | 0.959 | NSE bonus 1:5 = 0.8333 |
| DANGEE 2022 | 0.080 | close 0.069 vs 0.0667 |
| JMA 2019 | 0.239 | close 0.214 vs 0.2 |
| MINDACORP 2012 | — | suspended 03-19 to 06-13, no clean gap |
| PIIND 2011 | 0.565 | close 0.511 vs 0.5 |
| PRAKASHSTL 2016 | 0.116 | close 0.120 vs 0.1 |
| SHILPAMED 2013 | 0.775 | close 0.674 vs 0.6667 |

No row's right ISIN was unclear.

**Outside the 296 (for the owner, not in the list).** 712 more MCP rows of shared symbols sit on non-asked instruments:
- 295 are on the holder.
- 395 are on another ISIN whose holder already has the copy.
- 6 lack the holder copy but are directly linked to it (harmless in the chain).
- 16 have no holder in the symbol history (e.g. SHEKHAWATI's 2013 split on INE268L01046, whose old ISIN has no symbol-history row).

None of these 712 are part of C19's 296, and I left them alone.

## 2. The four refused factors (no correction proposed)

All four are 4-place MCP bonus factors that `exact_factor` refuses. That only matters to a live position's rescale (`rescale._apply`). These actions date from 2013–2017, so no live position can ever span them. The backtest and features read the stored Decimal.

| Row | Source | Ex-day gap | Verdict |
| --- | --- | --- | --- |
| INFINITE INE486J01014 2017-11-01 bonus 0.9907 | NSE "Bonus 1:26". Board 14-Sep-2017: bonus **to non-promoter shareholders only**, to reach minimum public shareholding | open 230.70 = prev close 230.70 | **Correct.** The holder ratio is 26/27 = 0.963, but the market factor is 1/(1+p/26). With public ≈ 24.1% (needed to land at 25%) that is 0.9907, which is what is stored. Keep. |
| TTML INE517B01013 2013-08-07 bonus 0.9705 | NSE "Bonus 2:15" | open 0.984, close 6.20/6.40 = 0.969 | **Correct as a market factor.** A full equity 2:15 would be 0.882, which the bars contradict. The pattern matches a public-only bonus at the June-2013 minimum public shareholding (MPS) deadline (public ≈ 22.8%). Keep. |
| GAMMNINFRA INE181G01025 2013-01-23 bonus 0.9928 | MCP "Bonus 1:34". Not in the ca-data files. | open 0.996, close 0.986 | **Likely correct**, same MPS pattern: a full 1:34 would be 0.971; 0.9928 implies public ≈ 24.6% → 25.4%. Keep, unconfirmed by an NSE file. |
| GODREJIND INE233A01035 2015-01-05 bonus 0.9992 | NSE "Bonus 1 : 1250", instrument class unknown | open 0.998 | **Owner.** 1250/1251 is the exact equity factor, but a 1:1250 ratio is typical of a bonus of preference shares. That would make it price-neutral: delete, or a dividend if worth ≥1% of the close. The bars can't tell 0.9992 from 1. |

One caveat for the owner on the MPS bonuses: one factor cannot be right for both quantity and price on a public holder's position. The quantity grows 27/26, but the price falls only by the market factor. `exact_factor` refusing them, and so holding the position manage-only with an alert, is the safe outcome. Leave it.

## 3. SETCO 2026-06-02 (no correction needed)

- NSE CA feed (`dividends/ca_2026-06.json`): **Interim Dividend Rs 13 per share**, ex and record 02-Jun-2026.
- hat_live already stores it: dividend, cash 13, `nse_ca_feed`, known_on 2026-06-02 (`ex_open`).
- The price confirms it. 28.62 − 13 = 15.62, and 15.62 × 1.02 = 15.93: the day's single print at the 2% upper band of a BE (trade-for-trade) name that had been hitting +2% every day. The rise continued afterwards (16.24, 16.56, …).
- The C12 guard counted it because `actions_between` ignores price-neutral types, and a dividend is one. For a held position, a 45% special dividend would trip the `position.split_gap` alert, which is conservative.
- Owner: decide whether a stored dividend at least as large as the gap should satisfy the guard. That is a code decision, not data.

## 4. Lineage review: 51 cases (`lineage report` prints 50 by default; use `--limit 200`)

Pattern as in `datafix-2026-10-24.tsv`: the action goes on the old ISIN, with ex_date = the new ISIN's first day and the factor from the price gap and the source. The line notes carry each case's numbers.

**A. ETF unit splits, 34 cases: add split on the old ISIN.**
- Factors: 0.1, except IVZINGOLD and LICMFGOLD at 0.01 (1:100). NSE's CA API doesn't carry ETF unit splits.
- The ratio comes from the first close net of the NIFTY 500 move, which falls in 0.095–0.104 (gold 0.0100–0.0103). First-day opens are noisy.
- After the add, 26 of them link under the rules (`face_value_change`).
- 8 still fail `OPEN_TOL` on an illiquid first-day open 15–22% high, though their closes match 0.1. They get an owner `link`: MIDSELIETF, NIF100IETF, ALPL30IETF, LOWVOLIETF, NV20IETF, HDFCPVTBAN, HDFCNIFIT, HDFCLOWVOL.
- Cross-name cases checked: KOTAKPSUBK was renamed to PSUBANK on INF373I01023 → INF174KA1A86. IDBIGOLD was renamed to LICMFGOLD on INF397L01554 → INF767K01SM1. Same symbol across the change, with continuous prices.

**B. Consolidations, 3 cases (long_gap).**

| Name | Change | Evidence | Action |
| --- | --- | --- | --- |
| VERTOZ INE188Y01023 → …031 | Re 1 → Rs 10 | NSE feed "Consolidation Re 1 to Rs 10", ex 25-Jun-2025 (listed under the stale INE188Y01015). 9.17 → open 96.28, close 87.11. | add split 10 + link |
| SHEKHAWATI INE268L01020 → …046 | Re 1 → Rs 10 | No NSE record in ca-data. Evidence: stored face value 10 (Re 1 since the 2013 split), 8.82 → 86.43 = 98.0% of 88.20, the −2% band of a BE relisting at 10× the old close. | add split 10 + link. **Owner may want an NSE confirmation first; the line can be dropped.** |
| KAUSHALYA INE234I01010 → …028 | Rs 10 → Rs 1000, i.e. **100:1** | Stored face value 1000. NSE's first prev close is 985.00 = 9.85 × 100. | **Leave.** Factor 100 is refused (`bad_factor`): the view holds cumulative factors only in [1e-9, 100) (`store.FACTOR_MAX`). Without the factor a link would put a 100× jump in the chain. Owner: a code change to the bound, or keep the two histories apart. |

**C. Factor already stored; the first open is noise. 14 cases, owner `link`, no action.**
- Rules fail only on `OPEN_TOL` (+10–20%). Every edge and close is consistent.
- ABSLNN50ET, BSLNIFTY: owner split stored 2021-11-25.
- AXISNIFTY 2020: the old last print 136.80 was a premium print. 1139.80 × 0.1 = 113.98 vs new close 118.73.
- NARMADA 0.5, GLOBAL 0.4, 360ONE 0.25 (bonus + split, stored on the new ISIN), VCL 0.5, EXCEL 0.0667.
- PTL, APOLSINHOT, SURANAT&P, SOUISPAT, RAJRAYON, NELCAST: split stored ex on the old ISIN's last day, with that day's open confirming it.
- Several are tick effects on sub-Rs 1 to Rs 6 prices.

No `unlink` is proposed: none of the 51 is two different companies.

## Left for the owner

- **KAUSHALYA 100:1** cannot be stored (FACTOR_MAX = 100). Decide: code change, or leave unlinked (current state).
- **GODREJIND 2015 bonus 1:1250**: equity (keep 0.9992) or preference shares (delete / dividend).
- **SHEKHAWATI 10:1**: confirm with NSE before applying, or drop its add and link.
- **SETCO-type guard**: whether a stored large dividend should explain a split-like gap (C12).
- **MPS public-only bonuses** (INFINITE, TTML, GAMMNINFRA): stored market factors kept. A live rescale through such an action stays manage-only by design.
- **The 8 ETF and 14 equity owner links** rest on first-day open noise. A single command each in `review-2026-10-24-lineage-links.txt`.
