# Waves — protected-delete-conflict

Each wave IS an iteration: a time-boxed, independently shippable
increment — one branch, one PR, green tests, demoable outcome.
Do not start wave N+1 until wave N merges.

## Wave 1 — iteration 1

Scenarios proven by this wave:
- Deleting a client used by a document returns a conflict
- Deleting an article used by a document line returns a conflict
- Deleting a quote referenced by an invoice returns a conflict
- Deleting an unreferenced client still succeeds

| Item | Title | Size | Deps | Notes |
|------|-------|------|------|-------|
| US1 | As a desktop operator, I want a blocked delete to explain what still references the record, so that I can fix the dependants | S | — | shared ProtectedDeleteMixin on all five detail views; 409 + detail + protected list; tests and docs. |
