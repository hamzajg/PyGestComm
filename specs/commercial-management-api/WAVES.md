# Waves — commercial-management-api

Each wave IS an iteration: a time-boxed, independently shippable
increment — one branch, one PR, green tests, demoable outcome.
Do not start wave N+1 until wave N merges.

## Wave 1 — iteration 1

Scenarios proven by this wave:
- CRUD round-trips per resource
- Document lifecycle works
- Auth lifecycle works
- Assistant covers the domain

| Item | Title | Size | Deps | Notes |
|------|-------|------|------|-------|
| US1 | As the desktop client, I want a complete authenticated commercial API, so that the full quote→invoice→delivery workflow runs end-to-end | L | — | Retroactive record — delivered across feat/* waves (full-domain-crud, devis-conversion, filters-and-guards, api-auth, bonliv, jwt-auth, token-logout, assistant-bonliv); 52 tests green. |
