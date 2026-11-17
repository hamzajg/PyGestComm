# Validation — tls-termination

## Traceability

| AC | Criterion | Scenarios | Wave(s) | Test evidence |
|----|-----------|-----------|---------|---------------|
| 1 | `DJANGO_SECURE_SSL=1` makes Django emit… | Deployment is documented, Dev mode unchanged, Secure mode settings apply | 1 | — |
| 2 | A working reverse-proxy config and deployment steps exist… | Deployment is documented, Dev mode unchanged, Secure mode settings apply | 1 | — |
| 3 | Default (flag off) behavior is unchanged — dev/LAN keeps… | Deployment is documented, Dev mode unchanged, Secure mode settings apply | 1 | — |

## Scenario coverage

- Scenarios: 3 total, 0 with detected test evidence, 3 without
- ✗ `Secure mode settings apply` (@w1)
- ✗ `Deployment is documented` (@w1)
- ✗ `Dev mode unchanged` (@w1)

## Demo script (manual walkthrough)

1. **Secure mode settings apply** — run the app, perform the scenario, observe the outcome.
2. **Deployment is documented** — run the app, perform the scenario, observe the outcome.
3. **Dev mode unchanged** — run the app, perform the scenario, observe the outcome.

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