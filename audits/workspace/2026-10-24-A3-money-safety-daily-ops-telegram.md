# money-safety audit: backend/app/hat/daily/, backend/app/hat/ops/ (scheduler, job runner), backend/app/hat/telegram/ commands  (2026-10-24, main @ 1a7aa75)

## Summary
The order paths these three packages drive mostly fail closed. Every entry path (trigger, placement, Take, resume) reads `feed_stale`, which includes `lock_lost`. A missing allocation, funds read, quality verdict or gate leaves an input `None`, and the risk check rejects it. Job runs are claimed once per (job, trade date). Approval buttons are MAC-bound, hash-bound and single-use. No `float` or wall-clock `datetime.now()` appears in the money paths in scope. The gaps are at the edges where the owner or the periodic loop act on many positions at once:
- `/flatten` leaves new exposure possible.
- A confirmed `/arm` re-arms every tripped kill, including ones the owner never saw.
- One exit view that raises silently stops the live exits of every position for the rest of the day.

Fix F3 first. It is a two-line change on the live path, and it ends a silent, day-long loss of trailing stops and exit rules.

## Findings

### F1. `/flatten` cancels no working entry and stops no new entry   [High] [Confirmed] [Strong]
Files: backend/app/hat/telegram/callbacks.py:263-287, backend/app/hat/execution/manage.py:410-442, backend/app/hat/execution/manage.py:347-358, backend/app/hat/engine/live_trades.py:363-392
Problem: A confirmed `/flatten` sells only `open_positions` (`qty_open > 0`). It trips no kill and pauses no bot. It does not cancel the account's working entry orders, and it does not end pending approval cards. Q13 rests on "the owner asked for no exposure", yet the follow-up sale (`flatten_owed`) covers only a position that already had a flatten sale.
Concrete failure: at 11:02 an auto bot's entry order is working with 0 shares filled, and a confirm card for another signal is pending. The owner taps Confirm on `/flatten` at 11:03, and every held position is sold. At 11:04 the working entry fills. The fill sync opens a position and puts a stop under it, but `flatten_owed` is False (no flatten sale on that position), so it is held. At 11:05 the next final bar fires a new auto trigger, which is placed. The owner can also tap Take on the old card. Each time the owner ends up holding positions again a few minutes after an emergency flatten.
Fix: Make a confirmed flatten first trip the account's manual kill switch in the same transaction as `flatten.executed`. That kill already makes every bot manage-only and ends pending approvals (`kill_ops.trip_kill`). Then send a cancel for each working real entry of the account through the existing `cancel_unfilled_entry` path, with the reason `flatten`. Change the confirm text so it says the account stays killed until `/arm`.
Tests: a small state test of the flatten edge: after the confirmed action, a manual account kill is tripped and the account's working entries are asked to cancel (FakeBroker records the cancel calls).
Size: M.

### F2. A confirmed `/arm` re-arms every kill tripped at confirm time, without listing them   [High] [Confirmed] [Strong]
Files: backend/app/hat/telegram/commands.py:224-255, backend/app/hat/telegram/commands.py:236-239, backend/app/hat/telegram/callbacks.py:296-300, backend/app/hat/telegram/render.py:449, backend/app/hat/telegram/confirm.py:28-36
Problem: `/arm` checks only that some drawdown or manual kill is tripped, then asks "Re-arm the tripped kill switches?" without naming any. The `Confirmation` stores no scopes. On Confirm, `rearm_all` re-reads `_tripped(session)` and re-arms all of them. A re-arm restarts the drawdown peak at the current equity (invariants, QA10).
Concrete failure: last week bot B tripped its 10% drawdown kill, and the owner left it tripped. Today the owner sends `/kill` during a scare, then `/arm` an hour later to undo it, meaning only the manual account kill. Confirm re-arms the account kill and bot B's drawdown kill. Bot B trades again from a fresh peak and can lose another 10%. A narrower variant: the account drawdown kill trips between the `/arm` question and the Confirm tap (within the 5 minutes). It is re-armed without the owner ever seeing it tripped.
Fix: At ask time, store the exact (scope, bot, reason, tripped-at) set in the `Confirmation` and list it in the confirm text. On Confirm, re-arm only that set, and only the entries still tripped at the same tripped-at. Refuse with `kill_changed` if a kill outside the set tripped in between. Optionally accept `/arm <bot>` so the owner can re-arm one kill (the arity changes from (0,0) to (0,1)).
Tests: a pure test of the confirm step: a kill tripped after the ask is not re-armed, and the set listed at ask time is exactly the set re-armed.
Size: S to M.

### F3. One exit view that raises aborts the live exits of every position, real ones included, silently   [High] [Confirmed] [Strong]
Files: backend/app/hat/daily/periodic.py:251-270 (view at :261 outside the try; `a.shadow.run` first at :255), backend/app/hat/daily/exits.py:161-180 (view at :166 outside the try), backend/app/hat/daily/exits.py:85-106, backend/app/hat/daily/market.py:229-275 (`require_exact` raises on a null close or low), backend/app/hat/daily/periodic.py:134-141
Problem: `ShadowExits.run` and `Periodic.live_exits` call `views(session, position)` outside their per-position `try`. Only `on_price` / `evaluate_position` are guarded. `live_exits` runs `a.shadow.run(now)` before any real position. So any exception while building one view propagates out of the whole `exits` step. That covers `require_exact` on a null adjusted close or low in `sma`/`swing_low`, an unparseable pinned exit rule in `exit_rules_of`, and a DB error in `manage_only`, `series_changed` or `actions_between`. `_run_steps` only logs it. The loop still beats, so `periodic.stalled` never fires, and no alert is raised.
Concrete failure: one shadow position's instrument has a null close in its 200-session window, for example from a missing adjustment factor in the view. Every 5 s pass raises in `ShadowExits.run`. For the whole session no real position runs `TradeManager.on_price`. Trailing stops are not raised, and MA, target and time exits do not fire. Only the last resting broker stop protects each position, and no one is told. The same happens to real positions after a bad real one in the oldest-first order.
Fix: Move the `views(...)` call inside the existing per-position `try` in both loops. Run the real-position loop independently of the shadow loop: two steps, or call `shadow.run` after the real loop inside its own `try`. Raise one URGENT alert per position and day when its view keeps failing (`exits.view_failed`), so the owner sees a position whose exits are off.
Tests: a small test of `live_exits` with a view source that raises for one position. The other positions' `on_price` is still called, and the shadow failure does not stop the real ones.
Size: S.

### F4. Telegram commands and buttons are authorised by chat id only, never by sender   [Medium] [Plausible] [Worth exploring]
Files: backend/app/hat/telegram/service.py:90-108, backend/app/hat/telegram/service.py:259-260, backend/app/hat/telegram/confirm.py:64-76, backend/app/hat/telegram/callbacks.py:170-192, backend/app/hat/telegram/commands.py:99-114
Problem: `handle` checks only `chat.id == HAT_TELEGRAM_CHAT_ID`. Neither the message's nor the callback's `from.id` is read. A second confirmation is bound to the chat, not the person. The `@bot` suffix handling shows that group use is anticipated, and `telegram_settings` accepts any integer, including a group's negative id.
Concrete failure: if the allowlisted chat is a group, or later becomes one, any member can tap Take on a card, Confirm the owner's pending `/flatten`, `/arm` or `/mode … auto`, or send `/resume` or `/mode`. The class is missing sender authentication; it is not a token flaw.
Confirm by: checking the deployed `HAT_TELEGRAM_CHAT_ID`. If it is the owner's private chat (a positive id equal to the owner's user id), the risk is latent.
Fix: Add `HAT_TELEGRAM_OWNER_ID`, or require the chat id to be positive and use it as the user id. Refuse (`unknown_user`) any update whose `from.id` differs. Bind each `Confirmation` to the user id too.
Tests: a pure test of the update classifier: the right chat with the wrong sender is refused, for a text command and for a callback.
Size: S.

### F5. Prices and subscriptions are fixed at 08:45, so a position opened later on an untracked instrument is marked at yesterday's close all day   [Low] [Plausible] [Speculative]
Files: backend/app/hat/daily/intraday.py:182-209, backend/app/hat/daily/intraday.py:384-389, backend/app/hat/daily/prices.py:274-290, backend/app/hat/daily/intraday.py:147-156, backend/app/hat/data/subscriptions.py:156-171
Problem: `PriceBook.track_session` and `LiveSubscriptions.sync` run only in `live.prepare` (the watchlist plus the positions open at 08:45) and for gap-scan candidates. A position that opens or reopens later on another instrument gets no subscription and no price mapping. One example is a late entry fill of an earlier session (Q2) on a name not on today's watchlist. Its exit view is `None`, so no live exits run. Intraday drawdown marks it at the previous close (`mark` returns `prev_close` when `quote` is None), never lower.
Concrete failure: such a position falls 12% by 13:00. The intraday drawdown sees 0%, the account kill does not trip until the 23:30 snapshot, and no exit rule runs. The broker stop still rests.
Fix: When the fill sync opens or reopens a real position, add its instrument to `PriceBook` and to the `held` subscription input. A cheap alternative: re-run `load_inputs`/`track_session` from housekeeping every minute.
Tests: a pure test that the subscription inputs include every open position's symbol after a position is opened.
Size: S.

### F6. Trigger writes (auto orders), the periodic loops, the Telegram poll and the scheduler share one default thread pool   [Low] [Plausible] [Speculative]
Files: backend/app/hat/engine/live_entry.py:424-429, backend/app/hat/data/live.py:208-213, backend/app/hat/daily/periodic.py:183, backend/app/hat/telegram/service.py:240, backend/app/hat/telegram/service.py:409, backend/app/hat/ops/scheduler.py:282-294
Problem: The loop's default executor has `min(32, cpu+4)` workers. On a 2-vCPU host that is 6 workers. They are shared by the 25 s Telegram long poll, the relay, three periodic loops, the scheduler's tick reads and every trigger write, which routes a real auto entry. A slow DB step (up to the 120 s statement timeout) plus the long poll can queue a trigger write or an exits pass behind them.
Concrete failure: an auto trigger fires during a DB slowdown and waits for a free worker. It is placed late, and the placement-time re-check refuses it on max-chase, so the trade is missed rather than lost. In the same window, exits passes are delayed.
Confirm by: checking the production CPU count, and logging executor queue depth during a session.
Fix: Give the trigger writes and the exits loop their own small executors, as the scheduler already has (`hat-job`), or set a default executor sized to the known number of long-lived consumers.
Tests: none (a sizing change); verify on the live host.
Size: S.

### F7. The close-phase jobs run on fixed wall-clock times, so a session that closes before 15:20 never gets its close exits   [Low] [Plausible] [Worth exploring]
Files: backend/app/hat/ops/trade_jobs.py:333-340, backend/app/hat/ops/trade_jobs.py:367-373, backend/app/hat/execution/manage.py:141-143, backend/app/hat/execution/manage.py:862-871
Problem: `exits.close` is 15:20-15:25 IST and `ORDERS_UNTIL` is 15:30, not times relative to the calendar's stored close. On a special session that closes early, `close_exits` refuses (`outside_close_window`), the job fails and raises URGENT `job.failed`, and that day's MA close exits never run. Stops are unaffected: after 15:25 a new stop is a GTT.
Fix: Derive the close window and `ORDERS_UNTIL` from the session's `close_at` (close minus 10, minus 5 and 0 minutes). Keep 15:20/15:25/15:30 only as the default session's values.
Tests: a pure test of the window function for a default and a short session.
Size: M.

### F8. A runtime that lost its lock keeps sending stops and sales beside a possible second runtime   [Low] [Plausible] [Speculative]
Files: backend/app/hat/daily/runtime.py:196-222, backend/app/hat/daily/assembly.py:387-393
Problem: When the lock cannot be taken again, `lock_lost` blocks entries only. The fill sync, the GTT jobs, live exits and flatten keep running. If another runtime took the lock, two processes run `PositionDesk` locks that know nothing of each other, on the same account. Each can reserve its own sale or stop under the next tag sequence. The tag uniqueness of `send_order` covers one tag, not two logical orders.
Concrete failure: during a Postgres restart a second container starts and takes the lock, and both now manage position P. Both raise P's stop or both send a close sale. The second sale is refused by the broker for lack of holdings, and duplicate GTTs rest on the same shares.
Fix: When the lock is lost and cannot be retaken, stop this runtime's order-writing loops and jobs too (stop the desks), and alert. The runtime holding the lock owns exits. This narrows the current "stops and exits keep running" note on `lock_lost`, so record the change in `decisions.md`.
Tests: none beyond the existing lock tests; verify with two processes on a scratch database.
Size: S.

## Outside scope, noted
- `engine/approvals.py:111` passes `MaxChaseParams(pct=float(pct))` on the Take re-check, a float in a money comparison. It belongs to an engine-scope audit.

## Suggested PRs
1. **Live exits never die on one view (F3).** Guard each view per position, run real exits independently of shadow, and alert `exits.view_failed`.
2. **Emergency controls do exactly what the owner sees (F1, F2).** A confirmed `/flatten` trips the account manual kill and cancels working entries. `/arm` lists and re-arms only the kills shown at ask time.
3. **Telegram sender authentication (F4).** Check the owner's user id on every update, and bind confirmations to the user.
4. **Session-relative close jobs and live tracking of new positions (F7, F5).** Derive the close window from `close_at`, and track and subscribe positions opened after 08:45.
5. **Runtime isolation (F6, F8).** Give trigger writes and exits their own executors, and stop the order-writing loops when the runtime lock is lost for good.
