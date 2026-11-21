# Decision review brief — Spec: contact-phone-format

- Source: `specs/contact-phone-format/SPEC.md (## Decisions)`
- Generated: 2026-11-21T16:01:43Z
- Detected type: data, api
- Readiness: **CHALLENGE** (6/6 record elements)
- This brief is input to judgment, not a verdict. The agent fills the scorecard after reading the code.

**Reversibility:** stated

**Alternatives on record (verify they are credible, not strawmen):**
- The column is user-facing data that a person retypes or dials. - Options considered: 1.
- CharField storing a canonical value (digits, optional leading +) — one representation per number, searchable with a plain contains. - Decision & why: Option 3.
- Changing the field type must not break the deployed client before the client loop lands. - Options considered: 1.
- Accept both, then normalise 0 → '' in the serializer — tiny explicit rule that encodes the legacy convention in one place. - Decision & why: Option 3.

## Evidence signals (heuristic — verify before acting)

- `.` — 19 source file(s); not a domain path, so layering checks were skipped
- `/` — 400 source file(s); not a domain path, so layering checks were skipped

Inspected: `.`, `/`

## Design moves to test

- Which invariant spans more than one aggregate, and does the transaction span it too?
- Can the write model be separated from read shapes without splitting the database?
- What is the migration and rollback path for existing data?
- Is this a public contract or an implementation detail? Who depends on it?
- How will it version, and what is the backward-compatibility promise?
- Are errors part of the contract — consistent shape, codes, retry semantics — or an afterthought?
- Is the contract documented where consumers can find it (OpenAPI, AsyncAPI, schema registry, docs site), and is the doc generated from code or hand-maintained?
- Which fields and operations are stable vs experimental, and what is the deprecation path?
- Is authn/authz explicit per operation with least privilege, and is that visible in the docs?
- Are writes idempotent where clients can retry (idempotency keys, natural keys, upserts)?
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
- Which consistency guarantee is required, and which can be eventual?
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
| Problem & forces | 5 | `models.py:16-17` `IntegerField`; client `NouveauClientCtrl.phoneText` treats `0` as blank; `assistant.py:115-125` needs `term.isdigit()` to match a phone | none |
| Alternatives & tradeoffs | 4 | D1 lists three options including the smallest (display-only) and the most reversible; D2/D3 each list three | none |
| Domain fit (DDD) | 4 | Phone becomes a value with one canonical form on the `Client` write path; no new aggregate, no behaviour added to the model beyond representation | keep validation in one serializer method, not spread across views |
| Architecture & boundaries | 4 | Serializer + model field change only; `assistant.py` is the single read-side consumer to update in w2; no new module or port warranted at this size | update `docs/ARCHITECTURE.md` field table in w2 |
| Testable design | 5 | Every AC names a `ClientApiTest`/`ClientModelTests`/`AssistantApiTest` case; migration replay named as G3 manual check because tests use a fresh DB | record the G3 replay output as evidence |
| Craftsmanship | 4 | One `CharField` + one normaliser + one validator; legacy `0` rule is 3 lines and explicitly temporary (D2 consequences) | delete the `0` rule in the client loop |
| Decision record | 5 | D1–D3 each carry forces, ≥2 alternatives, consequences (positive and negative), reversibility and a revisit trigger | none |

## Verdict (agent fills)

```
VERDICT: ACCEPT
STEELMAN: Storing a phone as canonical text is the only option that fixes the
defect at its source (the zero is already lost before any display code runs),
and it buys two things at once: fidelity and a single representation that both
the API and the assistant can compare with a plain string contains.
SMALLEST NEXT STEP: ship w1 (field + normaliser + validator + migration) and
keep the legacy 0→'' rule explicitly temporary so the client loop can delete it.
REVISIT TRIGGER: a client that needs to show country-formatted numbers, or a
second consumer that needs phone metadata (country, type, label) — then the
field becomes a value object or its own model.
```

Run the review with `/challenge-decision` and the `decision-challenger`
subagent. It is advisory: it never blocks a gate or a merge.
