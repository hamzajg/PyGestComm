# Validation — document-numbering

## Traceability

| AC | Criterion | Scenarios | Wave(s) | Test evidence |
|----|-----------|-----------|---------|---------------|
| 1 | Creating a document without a code assigns the next… | Auto-number on create, Explicit codes win, Sequences are per type | 1 | (weak) tests.py |
| 2 | Explicit codes are preserved verbatim, including… | Auto-number on create, Explicit codes win, Sequences are per type | 1 | (weak) tests.py |
| 3 | Numbering is per-type and increments independently | Auto-number on create, Explicit codes win, Sequences are per type | 1 | (weak) tests.py |

## Scenario coverage

- Scenarios: 3 total, 0 with detected test evidence, 2 with weak (token-match) evidence only, 1 without
- ~ `Auto-number on create` (@w1)
- ✗ `Explicit codes win` (@w1)
- ~ `Sequences are per type` (@w1)

## Demo script (manual walkthrough)

1. **Auto-number on create** — run the app, perform the scenario, observe the outcome.
2. **Explicit codes win** — run the app, perform the scenario, observe the outcome.
3. **Sequences are per type** — run the app, perform the scenario, observe the outcome.

## Gaps

- 1 scenario(s) lack detected test evidence — verify manually or add checks

Note: 'no evidence' means neither the scenario name nor a
token match was found in test files — verify by hand before
treating it as a real gap. '~' marks weak token-match evidence.

## Outcome follow-up

Optional; this is a post-release learning record, not a finish gate.
- Status: not yet measured
- Owner and review date: (record when known)
- Signal and observed result: (record after release; do not invent)
- Learning or next action: (record after review)