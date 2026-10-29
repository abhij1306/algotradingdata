# money-safety audit: backend/app/hat/risk + engine entries, exits, stops, approvals, shadow  (2026-10-24, main @ 1a7aa75)

## Summary
The risk authority is in good shape. `decide` is total and fails closed on every missing or inexact input. Sizing is exact Decimal with floored terms. Caps run under the bot and owner advisory locks, the exit stack only ever raises stops, and kills and pause are re-read at placement (`router._kill_refusal`). The weak spots are at the seams, where a signal routed under one set of gates is placed later under another. A confirm card or a resumed auto entry is placed without re-checking the DDPI, sleeve-Live and weights gates. A kill switch leaves working entry orders resting at the broker. The equity basis (the broker "Total Balance") probably does not include delivery holdings, which would skew both sizing and the drawdown kill. **Fix first:** make placement re-derive the bot's effective mode (F1). It is small, and it closes the one path where a real BUY can go out on an account whose stops may not be able to sell.

## Findings

### F1. A routed real entry is placed without re-checking DDPI, sleeve-Live or weights   [High] [Confirmed] [Strong]
Files: backend/app/hat/execution/router.py:471-484, backend/app/hat/execution/router.py:200-210, backend/app/hat/execution/router.py:291-316, backend/app/hat/engine/approvals.py:181-231, backend/app/hat/execution/accounts.py:210-250, backend/app/hat/execution/modes.py:249-260
Problem: `bot_mode` (gate_refusal: GTT, DDPI, weights, and sleeve Live through `routes_as_shadow`) is evaluated only when the signal is routed (`ExecutionRouter.route` -> `open_entry`). At placement, `_refusal` re-reads only the market conditions, the kill and pause state, `_gtt_refusal` (account status and GTT capability) and the broker session. `revoke_ddpi` says "every gate read sees it at once", but no gate read happens for a signal that is already routed, and revoking does not expire pending cards. A concrete case:
- 09:58: a confirm card is sent.
- 10:00: the owner runs `revoke-ddpi` because the DDPI mandate lapsed at the broker.
- 10:01: the owner presses Take. `placement_refusal`, `_kill_refusal` and `_gtt_refusal` all pass, and a real CNC BUY is sent.

Without DDPI, the GTT or SL sell that protects the position may be refused at trigger (a TPIN authorisation is needed), so the shares can sit without a working stop. The same gap applies in three other cases:
- an auto signal re-placed by `resume_entries` after a restart;
- a sleeve demoted from Live, or a policy that stops confirming weights, between the trigger and the Take.

Fix: in `_refusal`, recompute `modes.bot_mode(session, bot, now, calendar)` and refuse (`mode_gate_closed`, or the `gate_refusal` code) unless the effective mode is still the signal's mode, or confirm for an auto signal routed as confirm. Have `revoke_ddpi` expire the account's undecided approvals, as a risk-channel kill does through `cancel_pending_approvals`.
Tests: a pure test of a `placement_gate(signal_mode, effective_mode)` helper. A FakeBroker property test: card routed in confirm, DDPI revoked, Take, then assert no `place_order` call.
Size: S

### F2. Equity read from the broker funds "Total Balance" probably excludes held delivery shares, so the drawdown counts their cost twice   [High] [Plausible] [Worth exploring] (conflicts with decision Q1)
Files: backend/app/hat/daily/accounts.py:480-493, backend/app/hat/execution/fyers_payloads.py:342-357, backend/app/hat/daily/entries.py:142-165, backend/app/hat/risk/drawdown.py:299-357, backend/app/hat/risk/drawdown.py:360-386, backend/app/hat/risk/kill.py:307-335
Problem: capital is weight x `funds().total` (Fyers "Total Balance", or available + used). A broker cash ledger normally drops by the purchase cost once a CNC buy settles; the shares then sit in the demat, outside funds. Drawdown equity is capital + `_unfunded` + `open_pnl`, and `open_pnl` already subtracts each holding's full fill cost (`_holdings` cash) before adding qty x mark. If the ledger excludes holdings, every held position lowers equity by about weight x cost, and three things go wrong:
- **(a) False trip.** Example: a bot with ₹5L capital at weight 0.5 holds ₹3L of stock. From T+1 equity reads about ₹1.5L low (30%), so the 10% kill trips with no loss.
- **(b) Real losses masked.** If the owner re-arms while positions are held, the base is taken at the depressed equity. Selling those positions then lifts equity by weight x cost, which hides a real loss of up to that amount from the next 10% check.
- **(c) Under-sizing.** Sizing equity and `total_equity` (the global open-risk cap) shrink while positions are held. This direction is safe.

Q1 reasons only about realised P&L in the total; it says nothing about the cost of open positions. No real trade has run yet, so this has never been observed.
Confirm: read `funds()` on the live account the evening before a small CNC buy and again on the evening after it settles. If "Total Balance" fell by roughly the cost, the finding is confirmed.
Fix (if confirmed): define equity as funds total + the holdings at cost (or at mark) of HAT's open real positions, and drop the cost from the open-P&L term so the cost is counted once. Alternatively, read the broker's holdings value and add it. Record the result as an amendment to Q1.
Tests: a pure test of `equity(funds_total, holdings)` over buy, settle, mark and sell. Equity must not move on settlement.
Size: M

### F3. A kill switch or pause leaves the bot's working entry orders resting at the broker   [Medium] [Confirmed] [Strong]
Files: backend/app/hat/risk/kill_ops.py:74-118, backend/app/hat/risk/bots.py:25-49, backend/app/hat/execution/entry_timeout.py:1-24, backend/app/hat/engine/snapshot.py:47-48
Problem: `trip_kill` (risk channel) cancels only undecided approvals, and `pause_bot` only changes the bot's status. An entry already at the broker keeps working. That can be a DAY LIMIT with nothing filled (it is cancelled only on a failed break or after `HAT_ENTRY_TIMEOUT_MINUTES`, default 60), or the remainder of a part-filled entry (kept working until the close by policy). Example: an intraday drawdown kill trips at 11:00 while an entry LIMIT placed at 10:30 is resting. It fills at 11:20, so a bot the owner was told is manage-only (URGENT `kill.drawdown`) adds exposure. The 11:20 fill is booked and protected, but the trade should not exist.
Fix: on a risk-channel trip, and on pause, cancel the scope's working real entries through `AccountDesk.manager.cancel_unfilled_entry` (unfilled) and the remainder cancel (part-filled). A cancel is never an entry, so no gate blocks it. Update `KillSwitch.tla`/rule 6 wording: "manage-only also withdraws resting entries".
Tests: a pure helper `entries_to_withdraw(orders, kill_state)`; a FakeBroker test showing that a trip with a placed entry produces one cancel call.
Size: M

### F4. A strategy version without an enabled `hard_stop` is accepted, so backtest and shadow never stop out while live does   [Medium] [Confirmed] [Worth exploring]
Files: backend/app/hat/engine/strategy/config.py:230-232, backend/app/hat/engine/strategy/config.py:340-355, backend/app/hat/engine/exits.py:234-250, backend/app/hat/backtest/loop.py:435-447, backend/app/hat/engine/shadow.py:231-258
Problem: the stop only fires through the exit stack's `hard_stop` rule (`_price_at_or_below_stop`). The backtest `_down_leg` and the shadow `evaluate_position` both depend on it. `StrategyConfig` validates nothing about the exits beyond `min_length=1`, so a draft with `{rule: hard_stop, enabled: false}`, or none at all, is valid. Its backtest and shadow trades then ride through the stop with unbounded negative R. The same version live is protected by the broker stop (`StopDesk.protect` from `current_stop`), so the evidence behind promotion, the DSR and PBO gates, the confidence labels and the risk-increase gate describes a different strategy from the one that trades. The seeds include `hard_stop`, so this needs an edited draft to bite.
Fix: add a `StrategyConfig` validator that requires exactly one enabled `hard_stop`. Alternatively, make `exits.evaluate` always treat `price <= current_stop` as a full exit, whatever the stack says (invariant 3 then lives in code).
Tests: a `parse_config` test that refuses a config without an enabled `hard_stop`.
Size: S

### F5. A pending risk increase overrides a later decrease; and no production path can request a policy change   [Low] [Confirmed] [Speculative]
Files: backend/app/hat/risk/policy.py:299-312, backend/app/hat/risk/policy_service.py:79-157, backend/app/hat/risk/policy_service.py:160-186
Problem: `effective_version` picks the latest `effective_from`. Suppose an increase is requested on day 0 (effective day 7, after the cooling-off) and a decrease on day 2 (effective day 3). On day 7 the increase takes effect and supersedes the decrease, so risk rises above what the owner last asked for, and the increase's evidence was judged against the older policy. This is latent: `request_policy_change` has no caller outside `tests/hat/db/test_db_risk.py`. That also means the owner has no live lever to lower the policy, only pause and the kills.
Fix: when a decrease is requested, withdraw pending increases (mark them superseded, with an event). When a policy-change surface is added (admin CLI), route it through `request_policy_change` with the chat id.
Tests: a pure test of `effective_version` over [increase pending, later decrease].
Size: S

### F6. Feed-health kill updates are dropped on a write failure   [Low] [Confirmed] [Speculative]
Files: backend/app/hat/engine/live_entry.py:484-504
Problem: `DataHealthKill.write` sets `_written = seq` before `_write`, and `_write` swallows exceptions. A failed trip leaves no kill row; entries are still refused through `feed_stale` in `decide` and `placement_refusal`, so nothing is placed. A failed recovery leaves `feed_health` tripped, so the account takes no entries until the feed flaps again. The direction is fail-closed, but the error is silent apart from the log.
Fix: on failure, advance `_written` only after a successful write, and alert once on a failed write.
Size: S

### F7. Hygiene: a float in the Take re-check, and a stale mode comment   [Low] [Confirmed] [Speculative]
Files: backend/app/hat/engine/approvals.py:111, backend/app/hat/engine/live_entry.py:21-25
Problem: `chase_recheck` passes the exact max-chase percentage through `float(pct)` into `MaxChaseParams`. The str round trip is exact for short decimals, but it breaks trading-safety rule 8 on an order path. Separately, the `live_entry` module docstring still says the Fyers adapter has no GTT for delivery, "so every bot runs shadow". Fyers reports GTT, so confirm and auto do place real orders, and a reader could wrongly conclude no real order is possible.
Fix: give `max_chase` a Decimal entry point (or `MaxChaseParams.pct: Decimal`), and correct the docstring.
Size: S

## Checked and found sound
- `decide`: every entry input is validated and exact. Unknown actions are treated as entries, and exits are always accepted. A missing calendar row or policy version is a REJECT.
- `size_position` floors each term exactly; free cash cannot be Infinity on the risk path.
- Caps snapshot: slots include pending, awaiting and placed signals plus the working-entry remainders; veto trades are excluded. The bot lock is taken before the owner lock.
- Approvals: the Take is under the bot lock, expiry is enforced, the chase is re-checked against the percentage fixed at the trigger, and a failed break or the price at or below the stop refuses. Kills are re-read at placement.
- Stops: `raise_stop` refuses a lower stop; only the rescale moves a stop down, with its event.
- Shadow never imports a broker; virtual positions are refused on the real path and real ones on the virtual path.
- Drawdown marks: stale prices use min(last trade, stop); an unreadable equity reads as a breach.

## Suggested PRs
1. **Placement re-checks the mode gates** (F1). The router's `_refusal` re-derives `bot_mode`; `revoke-ddpi` expires pending cards.
2. **Manage-only withdraws resting entries** (F3). A risk-channel trip or a pause cancels the scope's working entry orders and remainders.
3. **Equity basis check and fix** (F2). Confirm the "Total Balance" semantics on the live account, then count holdings cost once in sizing and drawdown equity, and amend Q1.
4. **Stop is not optional, plus policy ordering** (F4, F5). Add a config validator for an enabled `hard_stop`, and have a decrease withdraw pending increases.
5. **Small hygiene** (F6, F7). Retry or alert on a failed health-kill write, use a Decimal max-chase in the Take, and correct the stale docstring.
