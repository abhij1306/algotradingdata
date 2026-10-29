# architecture audit: frontend/  (2026-10-24, main @ 1a7aa75)

## Summary
The frontend is small (about 2,000 lines of source outside the generated `schema.d.ts`) and mostly well layered: one typed `openapi-fetch` client, one `unwrap` that normalises errors into `ApiError`, a query-key factory, per-domain query hooks, and single owners for IST time and Indian number formatting. CI's `api-schema` job keeps the generated types in step with the backend. The weak spots are in how the data's state is shown, not in the folder layout. The dashboard keeps showing the last good snapshot with no warning once a poll starts failing, and the broker login badge is never polled and folds "status unreadable" into "disconnected". **Fix first:** make staleness visible on the dashboard (F1). It is a read-only operator view of kill switches and positions, so a frozen "armed" with no warning is the worst way it can fail. The components restructure now in flight will not fix any finding below by itself. F4 and F8 will be carried across unchanged unless that PR fixes the classes it moves.

## Findings

### F1. Dashboard sections hide failed refetches and show stale data as current   [High] [Confirmed] [Strong]
Files: frontend/app/hat/page.tsx:62-76, frontend/app/hat/page.tsx:337-344, frontend/lib/queries/hat.ts:20, frontend/lib/queries/query-client.ts:7-12, frontend/app/hat/__tests__/page.test.tsx:238
Problem: `Section` renders `query.data` whenever it is defined and checks `query.error` only when there is no data. In TanStack Query v5, a failed refetch keeps the previous `data` and sets `error`. So after the first successful load, a stopped backend, a DB outage or a 5xx on any poll leaves every section showing its last snapshot indefinitely. Nothing on the page says so. Concretely: the account kill trips, then the backend becomes unreachable (or `/api/hat/status` starts returning 503). The Status card still shows "Account kill: armed", and Open positions still lists the old rows. The `as_of` the backend returns in `StatusResponse` is never shown, so the operator cannot tell how old the view is. The seven hooks also poll on their own, so even a healthy page mixes snapshots taken at different moments. The only test of the error path (`page.test.tsx:238`) covers a failure on first load, not a failure after a success.
Fix: Deepen `Section` (or a `useDashboardQuery` wrapper in `lib/queries/hat.ts`) so its interface takes the whole query state: `data`, `error`, `isRefetchError`/`isError`, `dataUpdatedAt`. When data exists and the latest fetch failed, show the data with a visible "stale since HH:MM:SS IST: <message>" banner. Show `status.as_of` (formatted IST) in the page header. Optionally collapse the reads into one `/api/hat/dashboard` snapshot with a single `as_of`, so all sections are consistent and there is one seam to watch. That is a backend change, so treat it as worth exploring.
Tests: A small test of the pure state function (for example `sectionState({data, error, isError}) -> "fresh" | "stale" | "error" | "loading"`): data plus error gives "stale". Optionally one page test where the second response is a 503 and the stale banner appears.
Size: S to M.

### F2. Broker login badge is never polled and collapses "status unreadable" into "disconnected"   [Medium] [Confirmed] [Strong]
Files: frontend/lib/queries/auth.ts:20-36, frontend/lib/queries/auth.ts:55-69, backend/app/hat/api/broker_auth.py:128-138, frontend/components/layout/Header.tsx:11, frontend/app/hat/page.tsx:102-106
Problem: Three separate problems:
- (a) `useBrokerStatus` has `staleTime: 30_000` and `refetchOnWindowFocus` but no `refetchInterval`. On a dashboard left open, which is how a read-only dashboard is used, the header keeps showing "Connected" after the Fyers token expires at midnight IST. It also never turns to "System Offline" when the backend dies, until someone focuses the window or remounts.
- (b) The backend's status route returns `{connected: false, error: "Could not read Fyers login status"}` when the token store cannot be read. `toBrokerStatus` ignores `error`, so the badge says "Connect Fyers" and invites a needless re-login while the real fault is elsewhere. Any non-2xx from a bug likewise reads as "System Offline" (`catch {}` at auth.ts:61).
- (c) `toBrokerStatus` takes its body as `unknown` fields and re-validates by hand, throwing away the generated `BrokerStatusResponse` type the client already gives it.

Login state also has two sources of truth on one screen: the header reads the token file through `/auth/<broker>/status`, while the Status card's "Broker sessions" reads `hat_broker_session` rows. Nothing reconciles them, so they can disagree.
Fix: Make the broker-status module a deeper one with a state union, `connected | disconnected | unreadable(error) | offline`. Map it from the typed `BrokerStatusResponse` (use `error`, drop the `unknown` parsing), poll on the same 15 s cadence as the dashboard, and render `unreadable` as its own badge. Keep `offline` for network or 5xx errors only.
Tests: A pure test of the mapping: `{connected:false, error:"..."}` gives `unreadable`, a network error gives `offline`, `{connected:true,user_id}` gives `connected`.
Size: S.

### F3. Two error boundaries; the one that catches page crashes is a legacy leftover   [Medium] [Confirmed] [Strong]
Files: frontend/app/_shell/RootLayout.tsx:5-12, frontend/router.tsx:16-25, frontend/app/_shell/RouteError.tsx, frontend/components/ErrorBoundary.tsx:46-97
Problem: `RootLayout` wraps `AppShell` and `<Outlet/>` in the class `ErrorBoundary`, so every render error in `/hat`, and a failed lazy chunk load, is caught there rather than by the router's `errorElement`. That makes `RouteError` nearly unreachable: there are no loaders, and it only catches errors from `RootLayout` itself. `ErrorBoundary` has several problems of its own:
- It sits above `AppShell`, so a crash in one dashboard table removes the header and the login badge too.
- It is styled with tokens from an older design system that no longer exist (`bg-obsidian`, `glass*`, `text-text-*`, `bg-electric-blue`), so it renders unstyled.
- It tells the operator the error "has been logged and will be investigated", but no logging service exists (the `PROD` branch at :38-40 is empty).
- Its "Try Again" resets state and re-renders the same crash.

Fix: Delete `components/ErrorBoundary.tsx`. Put the router `errorElement` (`RouteError`) on the `hat` child route as well as the root, so a page error renders inside the shell and the header stays live. Keep one error UI.
Tests: None needed beyond the existing page tests. The proof is the deletion and the build.
Size: S.

### F4. Login modal and badges use colour tokens that are not defined   [Medium] [Confirmed (static)] [Strong]
Files: frontend/components/LoginButton.tsx:103,120-121,144,181,199-200,224,252,260, frontend/app/globals.css:140-170
Problem: `@theme` in globals.css defines `background*`, `surface`, `elevated`, `foreground*`, `border*`, `primary*`, `profit*`, `loss*` and `warning*`. LoginButton uses `bg-base`, `bg-void/80`, `bg-void/40`, `bg-void/50`, `to-primary-bright`, and `text-foreground-disabled`, none of which exist. Tailwind v4 generates no utility for an undefined colour, so the login modal (the UI's only write path) gets no panel background and no dimmed overlay, only a backdrop blur. The input, the "Authenticate" gradient end and the offline badge text are left without colour too. I checked this statically; I did not run a visual build. The LoginButton split in the components PR will carry these classes across unchanged unless it fixes them.
Fix: Map each class to the defined token (`bg-surface`/`bg-elevated`, `bg-background/80`, `to-primary-hover`, `text-foreground-muted`). Add a lint or conformance check that rejects colour utilities whose token is not in `@theme`. That is a structural rule, not a hand-kept list.
Tests: The structural check above, or none.
Size: S.

### F5. Enum-like API fields are typed as bare `string`, so the frontend casts and guesses   [Low] [Confirmed] [Worth exploring]
Files: backend/app/hat/api/dashboard.py:107,183-184, frontend/lib/api/schema.d.ts (BotView, SignalView, RegimeView), frontend/app/hat/page.tsx:260-276
Problem: The dashboard views declare `effective_mode`, `execution_mode`, `pending_mode`, `mode`, `state`, `confidence`, regime `state` and session `status` as `str`, and `confidence_basis` as `dict[str, Any]`. The generated types are therefore `string` and `{[key: string]: unknown}`. `ConfidenceBadge` has to test `label in CONFIDENCE_VARIANT` and cast, and `basisText` re-checks types at runtime. When the backend adds or renames a value, nothing fails at type-check time; the UI quietly falls back to an `outline` badge or "--". The interface across this seam is weaker than the backend already knows it to be. `AllocationRow.currency` is also returned and never shown next to `capital`.
Fix: Use `Literal[...]` (or the existing enum types) on the Pydantic view fields, and a small `ConfidenceBasis` model. Regenerate `schema.d.ts`, then make the frontend maps exhaustive `Record<Union, Variant>` with no cast.
Tests: `tsc` catches drift once the unions exist. No new runtime test is needed.
Size: M (backend views plus regenerated types).

### F6. `pending_from` is rendered as a raw UTC ISO string   [Low] [Confirmed] [Strong]
Files: frontend/app/hat/page.tsx:126-128, backend/app/hat/api/dashboard.py:107
Problem: `modeLabel` interpolates `bot.pending_from` (a `datetime`) directly, so the Bots table reads `...; auto from 2026-10-22T03:45:00Z`. Every other timestamp on the page goes through `formatIstDateTime`, the single owner of IST display, and the operator thinks in IST.
Fix: `formatIstDateTime(bot.pending_from)`.
Tests: Extend the existing modeLabel or page assertion so it expects "22 Oct 2026, 09:15:00".
Size: S.

### F7. Backend routes and status fields with no client   [Low] [Confirmed] [Worth exploring]
Files: backend/app/hat/api/dashboard.py:467-470,497-500,323-333, frontend/lib/api/schema.d.ts:208,268, docs/architecture.md:129-130
Problem: `GET /api/hat/bots` and `GET /api/hat/regime` have no caller in the frontend, the tests, Telegram or scripts. `/bots` duplicates `StatusResponse.bots`, which the page already uses. `StatusResponse.as_of` and `kill_switches` are computed on every 15 s poll and never read; bot kills already reach the page through `bots[].reasons`. Applying the deletion test: removing `/bots` and `/regime` adds no complexity anywhere.
Fix: Either delete both routes (and their mention in architecture.md), or use `/regime` for a regime-history strip. Use `as_of` for F1's freshness display. Show `kill_switches` (channel and state) on the Status card, or drop the field.
Tests: None.
Size: S.

### F8. Dead CSS and dead props left over from the earlier platform   [Low] [Confirmed] [Strong]
Files: frontend/app/globals.css:3-6,227-246,266-360,439-498, frontend/components/LoginButton.tsx:19-21, frontend/components/ui/card.tsx:5-14, frontend/components/ui/badge.tsx:15-47, frontend/components/ui/button.tsx:9-26, frontend/index.html:22
Problem: These are left over from the earlier platform:
- The whole `@layer components` block in globals.css (`.card*`, `.btn*`, `.badge*`, `.data-table`, `.input-base`, `.layout-container`, `.main-content`, `.page-scroll`, `.mono-num`) has no user in any `.tsx`. The same is true of `.h1`-`.h4`, `.custom-scrollbar` and the three `animate-*` classes. That is about 150 lines, still headed "ALGO TRADING DESIGN SYSTEM".
- LoginButton's `collapsed` prop is never passed, so half of each branch is dead.
- Most Card, Badge and Button variants are unused.
- index.html still describes the app as a "Professional algorithmic trading platform".

The atomic-design PR moves files but will keep all of this unless someone deletes it.
Fix: Delete the unused CSS blocks and the `collapsed` branches. Trim the variants to those in use. Fix the meta description.
Tests: None. `pnpm check` and `pnpm build` are enough.
Size: S.

## Suggested PRs
1. **Dashboard freshness and broker state** (F1, F2, F6, plus F7's `as_of`): add stale banners and an "as of" IST time to the dashboard, poll broker status with a real `unreadable` state, and format `pending_from` in IST.
2. **One error path, real tokens, dead code out** (F3, F4, F8): delete the legacy ErrorBoundary and use route `errorElement`s, map LoginButton to defined tokens with a structural check, and delete the unused CSS, props and variants. Sequence it after, or fold it into, the atomic-design restructure.
3. **Typed dashboard contract** (F5, rest of F7): use `Literal` and model types on the dashboard views, regenerate `schema.d.ts`, make the frontend maps exhaustive, and delete or use `/bots` and `/regime`.
