# Worked review examples

Each example states the input shape, reasoning, expected finding, safe improvement, and why a tempting alternative is worse.

1. **Real SRP:** `OrderService` validates credit, writes SQL, formats HTML, sends email, and emits metrics. Independent pricing, persistence, template, and delivery changes prove SRP pressure. Extract application policy plus persistence and notification adapters; retain one transaction/outbox boundary. Do not create one-method classes.
2. **False-positive SRP:** `CsvInvoiceParser` tokenizes rows, validates columns, converts values, and reports parse errors. All methods serve one import responsibility; mark as Non-issue. Splitting parsing/validation/error reporting would obscure the cohesive flow.
3. **Real OCP:** `charge()` repeats Stripe/PayPal/bank-transfer conditionals across capture/refund/status. Provider additions modify several stable paths. Introduce a payment capability adapter per provider behind one consumer-owned contract; contract-test each. A registry without shared operations would be premature.
4. **Leave conditional:** a two-state `trial ? freeLimit : paidLimit` rule has no planned variants. Keep a named conditional/function and test it. Strategy would add indirection with no extension pressure.
5. **LSP:** `ReadOnlyFile` extends `File` but `write()` throws unsupported-operation while callers accept `File`. The base writable contract is broken. Split readable/writable capabilities or use composition; test clients against each capability.
6. **ISP:** reporting UI needs `listUsers`; admin UI needs delete/suspend/reset. A shared interface makes reporting depend on admin methods. Split read and administration capabilities and migrate one consumer at a time; do not split every method absent consumer divergence.
7. **DIP:** `BillingPolicy` constructs `new StripeClient()` and reads `Date.now()`. Provider/time details obstruct deterministic policy tests. Pass consumer-owned payment/clock dependencies or functions at composition; keep Stripe in an adapter.
8. **Accept concrete dependency:** `Price.format()` calls a local immutable currency formatter with no external volatility or test cost. Mark as Non-issue; an interface only increases surface area.
9. **PR-only review:** a diff adds `ArchiveableDocument extends Document` but implements `save()` by throwing. Block only this introduced LSP risk, cite changed symbol/callers, propose a narrower archive capability, and note unrelated legacy smells as non-blocking context.
10. **Repository review:** map modules, dependency cycles, tests, churn, and critical flows; report a repeated service-locator pattern once with locations and prioritize it over low-impact naming. State sampled coverage and preserve undisputed modules.

**Small CRUD counterexample:** a small CRUD endpoint that validates a record, calls a single repository, and maps a response can be sufficiently simple. Mark it as a pragmatic Non-issue when no recurring variation, consumer pressure, or test boundary problem exists; adding interfaces/strategies would be overengineering.
