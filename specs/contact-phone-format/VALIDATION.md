# Validation — contact-phone-format

## Traceability

| AC | Criterion | Scenarios | Wave(s) | Test evidence |
|----|-----------|-----------|---------|---------------|
| 1 | A phone number with a leading zero round-trips through… | Phone numbers keep leading zeros | 1 | tests.py |
| 2 | Formatted input is canonicalised: separators stripped, a… | Formatted phone numbers are canonicalised | 1 | tests.py |
| 3 | A legacy integer payload is accepted and stored as its… | Legacy integer phone payloads are accepted | 1 | tests.py |
| 4 | A blank value and the legacy `0` both mean "no phone" and… | Zero and blank mean no phone | 1 | tests.py |
| 5 | Invalid values (letters, two `+`, out-of-range digit… | Invalid phone numbers are rejected | 1 | tests.py |
| 6 | Existing rows keep their digits after the migration | Existing numbers survive the migration | 1 | — |
| 7 | The assistant finds a client by canonical or formatted… | Assistant finds clients by phone | 1 | tests.py |
| 8 | Both phone fields behave identically | Both phone fields behave identically | 1 | tests.py |

## Scenario coverage

- Scenarios: 8 total, 7 with detected test evidence, 1 without
- ✓ `Phone numbers keep leading zeros` (@w1)
- ✓ `Formatted phone numbers are canonicalised` (@w1)
- ✓ `Legacy integer phone payloads are accepted` (@w1)
- ✓ `Zero and blank mean no phone` (@w1)
- ✓ `Invalid phone numbers are rejected` (@w1)
- ✓ `Both phone fields behave identically` (@w1)
- ✗ `Existing numbers survive the migration` (@w1)
- ✓ `Assistant finds clients by phone` (@w1)

## TDD evidence

Ordered red → green → refactor steps recorded in the wave's
evidence bundle (`--tdd=` on `harness_evidence --action=step`).

- Wave 1: red→green→refactor ✓

## Demo script (manual walkthrough)

1. **Phone numbers keep leading zeros** — run the app, perform the scenario, observe the outcome.
2. **Formatted phone numbers are canonicalised** — run the app, perform the scenario, observe the outcome.
3. **Assistant finds clients by phone** — run the app, perform the scenario, observe the outcome.

## Gaps

- 1 scenario(s) lack detected test evidence — verify manually or add checks

Note: 'no evidence' means neither the scenario name nor a
token match was found in test files — verify by hand before
treating it as a real gap. '~' marks weak token-match evidence,
which is not proof: ship_loop finish requires strong test
evidence or a `## Manual verification` entry per AC.

## Manual verification

<!-- For ACs without strong automated evidence, one bullet per
     AC: `- AC <n> — <command/check run> → <observed result>`.
     Preserved across ship_validate reruns; the delivery auditor
     still verifies each claim. -->

- AC 6 — backed up the real dev DB to
  `factory/scratch/gestcomm-e2e/phone-migration/db.before-0006.sqlite3`, then
  ran `migrate` (0006 column type + 0007 data normalisation) against it →
  11 client rows survived: `numTelClient1` is `text` (`'20123456'`, `'123'`,
  `'555'` unchanged, no digit lost), every legacy integer `0` became `''`
  (`select count(*) ... where numTelClient1='0' or numTelClient2='0'` → 0),
  and the suite still ran 76 tests OK afterwards. Recorded as evidence step
  `s5`; a unit test cannot cover this, because the Django test database is
  created from scratch and never replays a populated table.
- AC 1/2/5/7 — additionally proven against the running API, not only in the
  suite: `bash factory/scratch/gestcomm-e2e/phone-migration/smoke.sh` →
  POST keeps `0123456789`, POST canonicalises `+33 (0)6 12 34 56 78` to
  `+330612345678`, GET returns the same value, the assistant finds the client
  from `01 23 45 67 89`, `abc` is rejected 400 naming `numTelClient1`, and the
  smoke client deletes 204 (7/7 PASS, evidence step `s7`).

## Outcome follow-up

Optional; this is a post-release learning record, not a finish gate.
- Status: not yet measured
- Owner and review date: (record when known)
- Signal and observed result: (record after release; do not invent)
- Learning or next action: (record after review)