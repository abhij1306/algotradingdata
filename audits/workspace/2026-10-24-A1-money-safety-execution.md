# money-safety audit: backend/app/hat/execution (protect, fills, manage, submit, position_desk, fyers_*, kite_*)  (2026-10-24, main @ 1a7aa75)

## Summary

The order path is careful. Every place goes through `reserve_order` and `send_order`. A lost answer is never read as a rejection, and an unknown entry is never sent again. Reads fail closed. Money stays `Decimal` up to the SDK payload, and the GTT swap places the new GTT before it cancels the day stop. The weak spots sit in the heuristics around the order path:

- **Untagged GTT sales.** The fill sync attributes untagged sales to HAT's GTT without the shape check that trading-safety rule 3 requires (F1).
- **The 36-tag budget.** Retries spend the budget fast, and an exhausted budget breaks the sale path after it has already cancelled the stop (F2).
- **Failed stop raise.** When a stop raise fails, the broker stop stays low, and the engine's own hard stop is suppressed because "a broker stop rests" (F3).
- **The oversell backstop.** Several paths rely on the broker refusing a second CNC sell. That holds only when HAT owns every share of the symbol in the demat, and the holding baseline (Q12) exists because the owner does hold such shares (F4).

Fix F1 first: it lets the owner's own trading close HAT positions in HAT's book, and it can leave an orphan stop that sells the owner's shares.

## Findings

### F1. Untagged SELL trades on a symbol are booked as HAT's GTT fill with no shape check   [High] [Confirmed] [Strong]
Files: backend/app/hat/execution/fills.py:204-211, fills.py:397-401, fills.py:576-592, fills.py:668-678, fills.py:704-734; backend/app/hat/execution/fyers_payloads.py:403-413
Problem: `_WorkingGtts.of` maps any trade with `tag is None` and `gtt_tag is None` to the single live GTT on that symbol (fills.py:211). `_trades` then books every such SELL trade as a fill of that GTT (fills.py:398-401). This check has no product, quantity, price or order-id filter. The order-side paths do filter: `_resting_trigger` needs CNC with the GTT's quantity and limit price (fills.py:743-757). `_unfilled_trigger` needs only the quantity (fills.py:675). Trading-safety rule 3 allows an untagged child only "of the GTT's quantity at the GTT's limit price".

Concrete failure: HAT holds 50 shares of X under a live GTT. The owner also holds 100 shares of X (the case the holding baseline exists for) and sells 50 of them in the Fyers app.
- The trade arrives untagged. `_apply_gtt_trade` records it as an exit fill of HAT's position at the owner's price and marks the GTT row `filled` (fills.py:590).
- `protect` then sees the position closed. `cancel_all` reads only WORKING rows, so it does not cancel the real GTT, which keeps resting at the broker.
- HAT's 50 shares are now unmanaged: no trailing, no MA exits, P&L booked at the wrong price. Reconciliation may even balance, because the owner's sale and HAT's phantom sale net out.

Second form: the owner's untagged sale of exactly the GTT's quantity is cancelled or rejected.
- `_gtt_unfilled` ends HAT's GTT as `expired` while it still rests at the broker (fills.py:704), and the position is protected again with a second stop.
- With the owner's shares in the demat, the broker does not refuse the second sale. When both trigger, HAT sells the owner's shares.

Fix:
- Attribute an untagged trade only through its order: the trade's `order_id` must be a book order that passes the same shape test as `_resting_trigger` (SELL, CNC, the GTT's quantity, the GTT's limit price or a recorded `trigger_order_id`).
- Make `_unfilled_trigger` require the limit price as well as the quantity.
- An untagged sale that fails the test is foreign. Leave it to reconciliation.
Tests: a pure test of a new `gtt_child(order|trade, gtt, book)` predicate covering an owner's market sale on the symbol, the same quantity at another price, and an untagged CNC limit at the GTT's limit.
Size: M

### F2. The 36-tag budget per signal and purpose is spent by retries, and exhaustion breaks the sale path after its stop was cancelled   [High] [Confirmed] [Strong]
Files: backend/app/hat/execution/protect.py:436-452, protect.py:391-417, submit.py:170-178, submit.py:286-288, fills.py:164-192, fills.py:382-383, backend/app/hat/daily/accounts.py:560-563, backend/app/hat/execution/manage.py:536, manage.py:787-809, backend/app/hat/execution/tags.py:89-90
Problem: `StopDesk.place` reserves a tag before every check that can refuse without the broker.
- A GTT with no tick is refused in `_build_request` (submit.py:287-288) only after `reserve_order`. The same happens to a write the budget or the circuit refused (`_send` → `_release_unsent`). Each such refusal spends one sequence, because `next_sequence` counts cancelled rows too.
- A rejected stop spends two tags per call (`MAX_STOP_REJECTIONS`).
- Every fill sync re-protects any position without a live stop (`_unprotected`, fills.py:382). `watch_closely` makes that sync run at every 5 s step while any real entry of the account still works (fills.py:170-180, accounts.py:562-563). This contradicts its own docstring ("a stop the broker refused is retried once a minute, never faster", fills.py:168-169).

Concrete failure: a stop rejected for a reason that keeps repeating (a trigger outside the day's price band, an instrument the order is refused on) while an entry remainder still works. That spends 36 `stop_day` tags in about 90 s. From then on `place` catches `TagExhaustedError` and only alerts, once a day, for the rest of the position's life.

The sale path is worse. `_sell_locked` runs `make_room` first: for a full sale it cancels the broker stop (manage.py:536). Only then does `_attempt` call `reserve_order` (manage.py:799). `TagExhaustedError` is neither `OrderRefusedError` nor `BrokerUnavailableError`, so it escapes `_attempt` and `_sell_qty` uncaught. The protect at manage.py:806 never runs.

Once a signal's `exit_full` tags are gone, every exit evaluation does the same: cancel the stop, then raise. The next sync places a stop again, spending `stop_day` tags too. Exit tags go to rejections (3 a day), lost sales that expire, and, with `HAT_MPP_RESEND` on, one market-price-protection re-send per sync with no cap.

Fix:
- Run the deterministic checks (tick, limit price, unmapped symbol, budget or circuit open) before `reserve_order`.
- After a stop is rejected, retry the purpose at most once a minute per position, whatever the sync cadence.
- In the sale path, reserve the tag before `make_room`, and treat `TagError` as a refusal: alert, and protect again.
- Consider the alert at sequence 30 an early warning.
Tests: a pure test that a protect plan or `place` with no tick reserves nothing; a pure throttle predicate (`retry_due(last_rejected_at, now)`); a test that `_attempt` maps `TagExhaustedError` to a refusal.
Size: M

### F3. A failed stop raise leaves the broker stop low, and the engine's hard stop is then suppressed   [High] [Confirmed] [Strong]
Files: backend/app/hat/execution/manage.py:392-397, manage.py:488-499, backend/app/hat/execution/protect.py:716-733, protect.py:782-793, backend/app/hat/engine/exits.py:316-325, backend/app/hat/execution/fills.py:873-909
Problem: `follow` runs only on the one evaluation that raised `current_stop` (manage.py:394-395). A breakeven rule raises the stop once and is then marked fired (exits.py:316-325). If the modify fails, `_move` alerts `stop.not_moved` once a day and leaves `trigger_price` at the old value. Failure here means a timeout or 429 (`CODE_UNAVAILABLE` or rate limited) or a broker refusal. Nothing raises the stop again during the session: `_unprotected` (fills.py:887-896) compares only quantities, not triggers.

When the price then falls through the new stop, the engine fires `hard_stop`. `_sell` sees that a broker stop rests and sends nothing (manage.py:488-491). `_broker_stop_rests` checks only that some live stop has a broker id, not where its trigger sits.

Concrete failure: entry at 100 with the stop at 92, then breakeven to 100. The modify times out, and the price falls back through 100. HAT sells nothing until 92: a 1R loss where the policy said 0. The day stop is not corrected until the 15:25 swap places a GTT at `current_stop`.

Fix:
- `_broker_stop_rests` should count only a live stop whose trigger is at least `broker_trigger(current_stop, tick)`. Otherwise call `follow` again and, if it still fails, sell.
- Let the fill sync's protect phase re-follow any live stop whose trigger is below the position's broker trigger.
Tests: a pure predicate `stop_covers(row, current_stop, tick)`, and a property that `protect_plan` or a new follow plan returns a raise step when the trigger is below the goal.
Size: S

### F4. The "broker refuses the oversell" backstop fails when the owner holds the same symbol   [Medium] [Plausible] [Worth exploring]
Files: backend/app/hat/execution/stop_plans.py:202-207, backend/app/hat/execution/submit.py:252-256, backend/app/hat/execution/protect.py:23-29, protect.py:549-551, protect.py:705-707, backend/app/hat/execution/position_desk.py:48
Problem: several paths accept that a second sell order may rest beside a first one, on the grounds that "a resting CNC stop makes the broker refuse the sale, the safe way round":
- A lost day stop is sent again under its tag once a single book read 60 s later lacks it (`_ready_to_send`, `_lookup_before_retry`), although the module also says Fyers' book can lag.
- `make_room` skips a lost stop and lets the sale go (protect.py:706).
- `protect` treats only a LIVE sale as `exit_live`, so it places a new stop under a sale whose answer was lost (protect.py:550).

The broker refuses the second sell only when the demat holds no other shares of the symbol. The holding baseline (decisions Q12) exists because the owner does hold such shares. With them present, both orders are accepted, and the second one sells the owner's shares.

What would confirm it: a live record of Fyers' order-book lag after a place, and whether Fyers blocks the holdings of a resting CNC SL-M against a second SL-M when more shares are held.
Fix:
- Count UNSURE sales as `exit_live` in `protect_plan`.
- Need two good book reads, at least `settle_after` apart, before a lost stop is sent again.
- Where a reconciliation baseline shows owner shares of the symbol, never rely on the broker's refusal: wait for the settle instead of placing alongside.
Tests: `protect_plan` with an unconfirmed sale gives EXIT_WORKING; `_ready_to_send` needs two absent reads.
Size: M

### F5. `make_room` cancels the stop before the sale's own refusals, and the recovery runs under the same outage   [Medium] [Confirmed] [Worth exploring]
Files: backend/app/hat/execution/manage.py:536, manage.py:787-807, manage.py:783-784, backend/app/hat/execution/protect.py:691-712, backend/app/hat/execution/fyers_broker.py:261-264
Problem: a full sale cancels every resting stop (a confirmed write), then reserves and sends the market sale. The send can be refused with nothing sent: the budget refused the write after `WRITE_WAIT` (3 s), the circuit opened between the two calls, or the day is spent. The code then calls `protect`, which needs another write through the same budget and circuit. The window is widest at 15:20-15:25, when `close_exits` sends a burst of cancel and sale writes for every position.

Concrete failure: during that burst the sale is refused `broker_rate_limited`, and the re-protect is refused too. The position has no broker stop until a later sync gets a write through. If that is after 15:25, the swap job also finds no day stop, but its GTT write competes in the same burst.

Fix: for a full sale over a resting day stop, change the stop itself to a MARKET order with one `modify_order`, as `market_sale` already does for a triggered GTT. That is one write with no stopless window. Otherwise, check `day_budget_spent` and the breaker before `make_room`, and HOLD instead of cancelling.
Tests: a pure test of a `sale_plan(rows, keep)` choosing "modify to market" over "cancel then sell".
Size: M

### F6. One unreadable foreign row in the trade book stops the whole fill sync   [Medium] [Plausible] [Worth exploring]
Files: backend/app/hat/execution/fyers_adapter.py:302-303, backend/app/hat/execution/fyers_payloads.py:361-374, fyers_payloads.py:509-524, backend/app/hat/execution/fills.py:318-319
Problem: `orders()` skips and counts an unreadable row that is not HAT-tagged (D118). `trades()` parses every row with `parse_trade`, which raises on any unreadable field, so the whole read fails.

Concrete failure: a foreign trade row (manual, off-market or another segment) has a zero or missing `tradePrice` or an odd `side`. Every `FillSync.run` then raises before the protect phase, all day. A new entry fill is never booked, so its position never opens and gets no stop.

What would confirm it: Fyers trade-book samples of non-equity or manual rows.
Fix: give trades the same skip-and-count rule as the order book. A row with an HT or GTT tag still fails the read.
Tests: a parser test that an untagged malformed row is skipped and a tagged one raises.
Size: S

### F7. The session end rejects an earlier session's lost entry that today's book cannot show   [Medium] [Plausible] [Worth exploring]
Files: backend/app/hat/execution/manage.py:1051-1095, backend/app/hat/execution/position_desk.py:69-88
Problem: `settle_verdict` returns STALE only for a sale (`sale=True`). An entry of an earlier trade date that is still UNSURE gets EXPIRE when today's book lacks it, so `end_session` ends its signal `entry_not_found`. Today's books never show an earlier day's order or trades.

Concrete failure: an entry's answer is lost at 15:10 and Fyers reads fail until the close, so `end_session` reads nothing and returns 0. The entry fills. The next day it is ended Rejected with no position and no stop over shares the account holds. Reconciliation flags the mismatch but never adopts it.

Fix: treat an entry of an earlier trade date like a lost sale: STALE, an URGENT alert, settled from the holdings (or by the owner), never rejected on today's book.
Tests: a `settle_verdict` test that an entry `placed_at` yesterday gives STALE.
Size: S

### F8. The execution windows are fixed IST times, not the calendar's session   [Low] [Plausible] [Speculative]
Files: backend/app/hat/execution/manage.py:141-143, manage.py:364-366, backend/app/hat/execution/protect.py:121, protect.py:292-298
Problem: `EXITS_CLOSE_FROM`/`UNTIL`, `ORDERS_UNTIL` (15:30) and `SWAP_AT` (15:25) ignore a special or shortened session in `hat_trading_calendar`, which invariant 5 says has only its stored hours. On an early close, the close-phase MA exits never run. In an evening special session, the calendar says OPEN but every engine sale is refused `market_closed`. The broker stop still protects in both cases.
Fix: derive the close window, the swap and the order cut-off from the session's `close_at`.
Tests: `in_close_window(now, session)` for a short session.
Size: S

### F9. The adapter silently falls back to the `-EQ` symbol when the stored symbols cannot be read   [Low] [Confirmed] [Worth exploring]
Files: backend/app/hat/execution/fyers_adapter.py:200-208
Problem: `_fyers_symbol` swallows any failure to read `hat_broker_symbol` and converts to `NSE:<X>-EQ`. For a trade-for-trade (BE) position, every stop then goes out under a symbol that takes no order. It is rejected, and with F2 each rejection spends tags. The protect path guards an unmapped series (`StopTarget.unmapped`), but not a failed read.
Fix: on a failed read, refuse the intent before the call (`InvalidIntentError` or a not-sent code), never guess.
Tests: an adapter test with an `instruments` callable that raises.
Size: S

## Suggested PRs

1. **GTT-child attribution by shape (F1, F4):** attribute only untagged sales that match the GTT's quantity and limit (or a recorded trigger order), and stop relying on the broker's oversell refusal where the owner holds the symbol.
2. **Tag budget and the sale's stop window (F2, F5):** reserve after the deterministic checks, throttle retries of rejected stops, catch `TagError` in the sale path, and turn a resting day stop into the sale instead of cancelling it.
3. **Stop raise reconciliation (F3):** a broker stop counts as the hard stop only at or above the engine's stop, and the fill sync re-follows a low trigger.
4. **Fill-sync robustness across reads and days (F6, F7):** skip unreadable foreign trade rows, and settle an earlier session's lost entry as STALE.
5. **Calendar-driven windows and no symbol guessing (F8, F9):** close, swap and cut-off times from the session row, and a failed symbol read refuses the order.
