# Validation — commercial-management-api

## Traceability

| AC | Criterion | Scenarios | Wave(s) | Test evidence |
|----|-----------|-----------|---------|---------------|
| 1 | Every resource supports list/create/detail/update/delete… | Assistant covers the domain, Auth lifecycle works, CRUD round-trips per resource, Document lifecycle works | 1 | (weak) tests.py |
| 2 | Documents accept nested lignes, compute totals, enforce… | Assistant covers the domain, Auth lifecycle works, CRUD round-trips per resource, Document lifecycle works | 1 | (weak) tests.py |
| 3 | All /api/* routes require JWT or session auth; token… | Assistant covers the domain, Auth lifecycle works, CRUD round-trips per resource, Document lifecycle works | 1 | (weak) tests.py |
| 4 | The assistant answers count/search questions across all… | Assistant covers the domain, Auth lifecycle works, CRUD round-trips per resource, Document lifecycle works | 1 | (weak) tests.py |

## Scenario coverage

- Scenarios: 4 total, 0 with detected test evidence, 1 with weak (token-match) evidence only, 3 without
- ✗ `CRUD round-trips per resource` (@w1)
- ✗ `Document lifecycle works` (@w1)
- ✗ `Auth lifecycle works` (@w1)
- ~ `Assistant covers the domain` (@w1)

## Demo script (manual walkthrough)

1. **CRUD round-trips per resource** — run the app, perform the scenario, observe the outcome.
2. **Document lifecycle works** — run the app, perform the scenario, observe the outcome.
3. **Auth lifecycle works** — run the app, perform the scenario, observe the outcome.
4. **Assistant covers the domain** — run the app, perform the scenario, observe the outcome.

## Gaps

- 3 scenario(s) lack detected test evidence — verify manually or add checks

Note: 'no evidence' means neither the scenario name nor a
token match was found in test files — verify by hand before
treating it as a real gap. '~' marks weak token-match evidence.

## Outcome follow-up

Optional; this is a post-release learning record, not a finish gate.
- Status: not yet measured
- Owner and review date: (record when known)
- Signal and observed result: (record after release; do not invent)
- Learning or next action: (record after review)