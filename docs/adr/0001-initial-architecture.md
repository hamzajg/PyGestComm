# ADR 0001 — Initial architecture

Date: 2026-11-13 (baseline recorded retroactively)
Status: accepted (describes what is built)

## Context

PyGestComm is the backend half of a two-repo system: a Django REST API
serving the `Gest_Comm_ClientFX` desktop client for a small-business
domain (clients, articles, quotes, invoices).

## Decisions

1. **Django + DRF, minimal dependencies.** `requirements.txt` contains only
   Django 5.2 LTS and DRF 3.16. Rationale: KISS — no ORM plugins, no auth
   packages, no extras until needed.
2. **Single app, single endpoint so far.** `GestCommApp` exposes
   `ClientList` (list + create) at `/api/client`. The wider domain
   (articles, quotes, invoices) is planned but unimplemented — the API
   grows endpoint-by-endpoint rather than via a speculative schema.
3. **Legacy-compatible schema.** Table `client`, French-domain field names,
   `numTelClient*` as integers — matching what the desktop client already
   expects. Rationale: the DB schema predates the API; the API adapts to
   it, not vice versa.
4. **Env-driven settings with debug-mode escape hatch.** `DJANGO_SECRET_KEY`
   is mandatory unless `DJANGO_DEBUG` is on, in which case an ephemeral key
   is generated. Rationale: safe local dev, no committed secrets.
5. **SQLite committed dev database.** `db.sqlite3` ships in the project
   for zero-setup development. Rationale: matches the desktop-tooling
   context; production deployments set their own DB.
6. **No auth on the API yet.** Endpoints are open; `/admin/` is the only
   authenticated surface. Accepted risk for a LAN/desktop-tool context —
   must be revisited before any network exposure.

## Consequences

- Contract changes require synchronised updates in `Gest_Comm_ClientFX`.
- "No update/delete" means clients can't edit records — a known gap, not
  an oversight to silently fix.
- When auth is added it should cover `/api/*`, not just admin.
