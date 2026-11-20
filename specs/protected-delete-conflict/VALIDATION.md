# Validation — protected-delete-conflict

## Traceability

| AC | Criterion | Scenarios | Wave(s) | Test evidence |
|----|-----------|-----------|---------|---------------|
| 1 | Deleting a client referenced by any devis/facture/bonliv… | Deleting a client used by a document returns a conflict, Deleting a quote referenced by an invoice returns a conflict, Deleting an article used by a document line returns a conflict, Deleting an unreferenced client still succeeds | 1 | tests.py |
| 2 | Deleting an article referenced by any document line answers… | Deleting a client used by a document returns a conflict, Deleting a quote referenced by an invoice returns a conflict, Deleting an article used by a document line returns a conflict, Deleting an unreferenced client still succeeds | 1 | tests.py |
| 3 | Deleting a devis that a facture still references answers… | Deleting a client used by a document returns a conflict, Deleting a quote referenced by an invoice returns a conflict, Deleting an article used by a document line returns a conflict, Deleting an unreferenced client still succeeds | 1 | tests.py |
| 4 | Deleting a record with no dependants still returns 204, and… | Deleting a client used by a document returns a conflict, Deleting a quote referenced by an invoice returns a conflict, Deleting an article used by a document line returns a conflict, Deleting an unreferenced client still succeeds | 1 | tests.py |
| 5 | The full suite stays green and the live HTTP lifecycle… | Deleting a client used by a document returns a conflict, Deleting a quote referenced by an invoice returns a conflict, Deleting an article used by a document line returns a conflict, Deleting an unreferenced client still succeeds | 1 | tests.py |

## Scenario coverage

- Scenarios: 4 total, 4 with detected test evidence, 0 without
- ✓ `Deleting a client used by a document returns a conflict` (@w1)
- ✓ `Deleting an article used by a document line returns a conflict` (@w1)
- ✓ `Deleting a quote referenced by an invoice returns a conflict` (@w1)
- ✓ `Deleting an unreferenced client still succeeds` (@w1)

## Demo script (manual walkthrough)

1. **Deleting a client used by a document returns a conflict** — run the app, perform the scenario, observe the outcome.
2. **Deleting an unreferenced client still succeeds** — run the app, perform the scenario, observe the outcome.

## Gaps

- none — spec is fully traced

Note: 'no evidence' means neither the scenario name nor a
token match was found in test files — verify by hand before
treating it as a real gap. '~' marks weak token-match evidence.

## Outcome follow-up

Optional; this is a post-release learning record, not a finish gate.
- Status: not yet measured
- Owner and review date: (record when known)
- Signal and observed result: (record after release; do not invent)
- Learning or next action: (record after review)
## Walkthrough — live server, 2026-11-20

Backend: `manage.py runserver 127.0.0.1:8000` (dev DB, user `admin`).
Driver: `factory/scratch/gestcomm-e2e/e2e_smoke.py` (37 HTTP checks, no
Django imports), recorded as evidence step `s2`.

| Check | Command / request | Observed |
|---|---|---|
| Suite | `manage.py test` | `Ran 61 tests … OK` (56 before + 5 new) |
| Client used by documents | `DELETE /api/client/4` | `409` + `detail` "still referenced by 1 devis, 1 facture", `protected` counts |
| Article used by lines | `DELETE /api/article/5` | `409` (`lignedevis`, `lignedebonliv`) |
| Devis locked | `DELETE /api/devis/6` | `400` terminal-state lock (takes precedence) |
| Unreferenced client | `DELETE /api/client/5` | `204`, then `GET` → `404` |
| Whole lifecycle | 37 checks | 37/37 passed, no 5xx |

Not verified here: how a human reads the 409 in the desktop window — that
is `Gest_Comm_ClientFX/specs/delete-conflict-ux`.
