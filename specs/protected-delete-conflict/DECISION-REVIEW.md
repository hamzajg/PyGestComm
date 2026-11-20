# Decision review brief — Spec: protected-delete-conflict

- Source: `specs/protected-delete-conflict/SPEC.md (## Decisions)`
- Generated: 2026-11-20T09:04:28Z
- Detected type: api, ux
- Readiness: **READY** (6/6 record elements)
- This brief is input to judgment, not a verdict. The agent fills the scorecard after reading the code.

**Reversibility:** stated

**Alternatives on record (verify they are credible, not strawmen):**
- No schema or migration change: PROTECT stays. - No cascade/soft-delete option (rejected in the Decisions block). - No client-repo code changes (tracked in Gest_
- Gest_Comm_ClientFX also needs to distinguish this case to phrase the French message. - Options considered: 1.
- Catch in one shared mixin and return 409 Conflict with a structured protected list (most reversible: one mixin, no model or serializer change). - Decision & why
- Context & forces: Deleting a client would otherwise silently delete or orphan quotes/invoices/delivery notes — unacceptable for accounting records, and the exis

## Evidence signals (heuristic — verify before acting)

- `src/GestCommProject/GestCommApp/views.py` — no test file references this code (heuristic)
- `src/GestCommProject/GestCommApp/views.py` — 1 source file(s); not a domain path, so layering checks were skipped
- `src/GestCommProject/GestCommApp/tests.py` — 1 source file(s); not a domain path, so layering checks were skipped

Inspected: `src/GestCommProject/GestCommApp/views.py`, `src/GestCommProject/GestCommApp/tests.py`

## Design moves to test

- Is this a public contract or an implementation detail? Who depends on it?
- How will it version, and what is the backward-compatibility promise?
- Are errors part of the contract — consistent shape, codes, retry semantics — or an afterthought?
- Is the contract documented where consumers can find it (OpenAPI, AsyncAPI, schema registry, docs site), and is the doc generated from code or hand-maintained?
- Which fields and operations are stable vs experimental, and what is the deprecation path?
- Is authn/authz explicit per operation with least privilege, and is that visible in the docs?
- Are writes idempotent where clients can retry (idempotency keys, natural keys, upserts)?
- Which user journey does this serve, including empty, error, and slow states?
- What is the accessibility and keyboard path?
- Where does the UI hold state that belongs to the domain?
- Invert a dependency so the unstable thing depends on the stable thing.
- Make an implicit boundary or invariant explicit before adding mechanism.
- Shrink the decision: can half of it ship independently and reversibly?

## Challenge questions

### 1. Problem & forces
- What user/business outcome does this serve, and what breaks if we do nothing?
- Which quality attributes actually drive it (correctness, latency, cost, operability, compliance, time-to-market)? Rank them.
- Which constraints are fixed (budget, deadline, team, contracts) and which are assumed?
- Who owns this decision, and who must live with the consequences?
**Good looks like:** The dominant force is named, and "do nothing" is treated as a real option.

### 2. Alternatives & tradeoffs
- What are at least two credible alternatives, including the simplest thing that could work?
- For each: what does it make easy, what does it make hard, and what does it cost to reverse?
- Is this a one-way or two-way door? If one-way, what evidence justifies it?
- What would have to be true for the chosen option to be wrong?
**Good looks like:** A tradeoff matrix names winners and losers; reversibility is explicit; no strawman options.

### 3. Domain fit (DDD)
- Which bounded context owns this concept, and is the boundary drawn around language or deployment?
- Which terms are overloaded across contexts, and where is the translation (anti-corruption layer)?
- What are the aggregates, their invariants, and the transaction boundary? Does one transaction span aggregates?
- Are domain events the right integration mechanism, or is this a synchronous dependency?
- Does the model carry behavior, or is it an anemic data bag?
**Good looks like:** Ubiquitous language is explicit, invariants are protected at the boundary, external models are translated.

### 4. Architecture & boundaries
- Which direction do dependencies point? Can the core be tested without the framework, DB, or network?
- What is the smallest boundary that isolates this change (module, port, package)?
- What happens when each external dependency is slow, down, or returns garbage?
- Where does data ownership live, and is there a second writer?
- What is the operational story: config, migrations, rollout, rollback, observability?
- Who are the consumers, and what is the deprecation policy?
**Good looks like:** Policy depends on nothing; mechanisms are adapters; failure and migration paths are named.

### 5. Testable design
- Where are the seams? Can time, randomness, IO, and external calls be injected?
- Which behaviors get fast unit tests, which need integration, which need contract tests?
- Does each acceptance criterion map to an observable check, or only to implementation details?
- Are the tests deterministic and independent (no shared state, no sleeps)?
- What is the failure signal when this decision turns out wrong in production?
**Good looks like:** Behavior-first tests, deterministic seams, scenario-to-test traceability, a named failure signal.

### 6. Craftsmanship
- Is this the smallest reversible step, or a big-bang change?
- Are names from the domain, or from the framework/table?
- Is the error model explicit (typed failures vs exceptions vs silent nulls)?
- Is there speculative abstraction (interfaces with one implementation, config nobody sets)?
- Is the migration path documented and rollback-able?
**Good looks like:** Small steps, intention-revealing names, explicit errors, no speculative generality, documented migration.

### 7. Decision record
- Are status, owner, and date recorded?
- Are consequences (positive and negative) written down?
- Is there a revisit trigger (metric, date, event)?
- Are links to evidence, code, and related ADRs present?
**Good looks like:** A future reader can tell why, what was traded, and when to revisit.

## Scorecard (agent fills; 1 = poor, 5 = strong, evidence required)

| Lens | Score | Evidence (file:line, test, benchmark) | Action |
|------|-------|----------------------------------------|--------|
| Problem & forces | 5 | Live run 2026-11-20: `DELETE /api/client/3` and `/api/article/4` both answered 500 `ProtectedError`; `views.py` had no `ProtectedError` handling and `models.py` declares `on_delete=PROTECT` on every document FK | none |
| Alternatives & tradeoffs | 4 | SPEC D1 lists status quo / 400-in-each-view / shared-mixin-409, with the simplest first; D2 rejects cascade and soft-delete with data-integrity reasoning | none |
| Domain fit (DDD) | 4 | PROTECT encodes "a document never loses its client"; the conflict is a domain rule, not a validation slip, so 409 is the honest status | none |
| Architecture & boundaries | 4 | One mixin in `views.py`, no serializer/model change; the HTTP status decision stays in the HTTP layer. Concern: `views.py` already holds all five resources — the mixin must stay ~20 lines | keep the mixin local; revisit if a service layer appears |
| Testable design | 5 | DRF test client can assert exact status + body; scenarios map 1:1 to tests (client/article/devis/204-regression); no clock or randomness | none |
| Craftsmanship | 4 | `protected` list with per-model counts is close to speculative: the known consumer reads only `detail` | build it only if a test/consumer uses it; otherwise `detail` alone |
| Decision record | 5 | D1/D2 each carry forces, options, decision, consequences and a revisit trigger (consumer cannot handle 409) | none |

## Verdict (agent fills)

```
VERDICT: ACCEPT
STEELMAN: A single 20-line mixin converts a crash into a machine-readable business answer across all five resources, without touching the schema, the serializers, or the PROTECT guarantees that keep accounting documents intact.
SMALLEST NEXT STEP: Emit `detail` for every protected delete and add the `protected` counts only where a test asserts them, so the contract carries no unused structure.
REVISIT TRIGGER: any consumer reporting it cannot handle 409, or a request for reversible/soft deletes (which would reopen D2).
```

Run the review with `/challenge-decision` and the `decision-challenger`
subagent. It is advisory: it never blocks a gate or a merge.
