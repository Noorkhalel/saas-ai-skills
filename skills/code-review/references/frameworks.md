# Framework-Specific Review Notes

The pitfalls each stack invites — read the section matching the code under review. These are *additions* to the general phases, not replacements; and framework idioms cut both ways: flag violations of the project's framework conventions, and don't flag idiomatic code just because another stack does it differently.

## Frontend

### React
- **Stale closures:** callbacks/intervals/subscriptions capturing state from the render they were created in (`setInterval(() => setCount(count + 1))` — forever increments from the captured value; fix: functional updates or refs).
- **Effect discipline:** missing/wrong dependency arrays (lint rule off?); effects that derive state from props/state (compute during render instead); fetch-in-effect without abort/ignore-stale handling → out-of-order responses and setState-after-unmount; effects used as event handlers.
- **State placement:** server data in `useState` + manual effect where the app has a data-fetching layer (React Query/SWR/RSC) — cache, dedupe, race handling all reinvented; state high in the tree re-rendering everything on keystroke; derived state stored (then desyncs) instead of computed.
- **Render correctness:** array index as `key` on reorderable/deletable lists (state sticks to the wrong item — a *correctness* bug, not style); mutation of state/props (`items.push`, `sort()` in place — sort a copy); new object/closure identities passed to memoized children every render.
- Security: `dangerouslySetInnerHTML` with anything user-influenced (sanitize with DOMPurify-class); user-controlled `href` (`javascript:` URLs).
- **Auth-component review (frequent request):** tokens in `localStorage` = readable by any XSS — weigh vs HttpOnly cookie + CSRF story; secrets/API keys in client code are public, full stop; client-side route guards are UX, not security — the API must enforce; password/token values ending up in logs, error reporters, or analytics via state dumps.

### Next.js
- **Server/client boundary:** secrets or server-only code imported into client components (`NEXT_PUBLIC_` = shipped to browser — check what's prefixed); `use client` sprinkled until the tree is a SPA; data fetched client-side that the server component could render.
- **Server actions / route handlers are public endpoints:** they need the same authn/authz/validation as any API — "it's only called from my form" is not an access control.
- Caching semantics: Next caches aggressively by default (fetch cache, route cache) — review for stale-data bugs (user-specific data cached globally = data leak) and for `revalidate`/`no-store` correctness on dynamic data.
- Middleware auth: matcher gaps (unprotected paths), and JWT verified in middleware but not re-verified in the handler that trusts it.

### Vue
- Reactivity loss: destructuring props/reactive objects (loses tracking — needs `toRefs`/computed); mutating props directly; `v-if` with `v-for` on the same node; missing `:key`.
- `v-html` with user content = XSS (same rule as React above); watchers doing what computed properties should; deep watchers on large objects (performance).

### Angular
- Subscriptions never unsubscribed (memory leak + ghost handlers — `takeUntilDestroyed`/async pipe); logic in templates re-evaluated every CD cycle; `any` proliferation defeating the type system; `bypassSecurityTrust*` on user-influenced values (XSS); services provided at wrong scope (accidental shared state or accidental duplication).

## Backend

### Node.js / Express
- **The event loop is the whole product:** any sync I/O or CPU-heavy call (`fs.*Sync`, `bcrypt.hashSync`, big `JSON.parse`, crypto) in a handler stalls *every* request.
- Error handling: async handler throws don't reach Express error middleware without a wrapper (express 4) — unhandled rejection per request; missing centralized error middleware = stack traces to clients.
- Middleware order bugs (auth after routes, body parsing after consumers); `app.use(cors())` defaults reflecting any origin *with credentials*; missing rate limiting on auth endpoints.
- Module-level mutable state shared across requests (per-user data in a module variable = cross-user leak); config read at import time before env is loaded.

### NestJS
- Guard coverage: authz via per-route `@UseGuards` opt-in — one forgotten decorator = open endpoint (prefer global guard + explicit `@Public()`); DTO validation only works where `ValidationPipe` is actually applied (global?) **and** `whitelist: true` (else mass assignment rides through); request-scoped providers injected into singletons; circular module dependencies via `forwardRef` (design smell).

### Django
- ORM: `.raw()`/`extra()`/string `.filter()` building = injection review; N+1 via lazy FK access in template loops (`select_related`/`prefetch_related`); `.values()` vs model semantics.
- `@csrf_exempt` on state-changing views; `DEBUG=True` shipped; missing `@login_required`/permission checks (or DRF permission_classes defaulting open); signals doing critical work (invisible control flow — verify ordering assumptions); `objects.get()` without `DoesNotExist` handling; transactions: `atomic` blocks around multi-write invariants.

### FastAPI
- `def` vs `async def` semantics: blocking calls (requests, sync DB drivers) inside `async def` block the event loop (sync `def` at least gets a thread) — the #1 FastAPI review finding.
- Pydantic models on *input and output* (response_model prevents ORM-object leaks of hashed passwords etc.); dependencies for auth actually applied per router (missing `Depends` = open endpoint); background tasks losing DB session/tenant context.

### Spring Boot
- `@Transactional` pitfalls: self-invocation bypasses the proxy (private/internal calls aren't transactional — the classic silent one); checked exceptions don't roll back by default; transaction spanning remote calls.
- Field injection vs constructor injection (testability); entities returned directly from controllers (lazy-loading exceptions + overexposure — use DTOs); N+1 via lazy relations in loops; `@Async` without executor config/exception handler; actuator endpoints exposed unauthenticated.

### .NET / ASP.NET Core
- `async void` (uncatchable exceptions) and `.Result`/`.Wait()` deadlock/starvation (sync-over-async); `DbContext` lifetime bugs (singleton-captured context, shared across threads); `IQueryable` composed then evaluated in memory unintentionally (client evaluation); missing `[Authorize]`/policy on controllers (prefer fallback policy globally); `dynamic`/reflection where the type system was the point.

## Databases

### PostgreSQL
- See `data.md` (core) — plus: RLS policies checked per-operation (a SELECT-only policy leaves writes open); `SECURITY DEFINER` functions as RLS bypass routes; connection pooling vs session state (`SET app.tenant_id` on a pooled connection leaks across requests unless transaction-scoped `SET LOCAL`); JSONB queries needing GIN indexes; `SERIAL` vs identity, `timestamp` vs `timestamptz` (always tz).

### MySQL
- Silent data truncation/coercion in non-strict mode (verify `sql_mode`); `utf8` ≠ `utf8mb4` (emoji breakage); isolation default REPEATABLE READ (different phantom/locking behavior than PG's READ COMMITTED — check assumptions); FK support depends on engine; case-insensitive collation surprises on unique keys.

### MongoDB
- Injection still exists: query objects built from user input (`{$where: userInput}`, operator injection via `req.body` spread into `find` — `{"$gt": ""}` bypasses equality checks); no multi-document atomicity without explicit transactions/sessions — multi-doc invariants need them; unbounded array growth in documents (16MB limit + rewrite cost); missing indexes invisible until scale; schema drift with no validation layer (recommend schema validation or ODM-level).

### Supabase
- **RLS is the entire security model when clients query directly** — review policies as the API surface: every table exposed via PostgREST needs policies for each operation; `anon` vs `authenticated` role coverage; policies using `auth.uid()` correctly (and org membership via a join, not a client-supplied claim).
- Service-role key server-side only (it bypasses RLS — grep the client bundle); storage bucket policies reviewed separately from table RLS; edge functions: validate JWT explicitly when `verify_jwt` is off; `security definer` Postgres functions as accidental RLS bypasses.
