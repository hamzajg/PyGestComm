# Spec: commercial-management-api

> Spec-driven development artifact. This file is the contract: implementation
> is done when every acceptance criterion maps to a scenario in
> `EXAMPLES.feature` and every scenario has a passing check.

## Problem

PyGestComm started as a single-endpoint API (`GET/POST /api/client`) for the
Gest_Comm_ClientFX desktop client. The commercial lifecycle it is meant to
serve — clients, articles, quotes, invoices, delivery notes — did not exist
in the backend, so the client could not run a real business workflow. This
spec records the delivered domain: full CRUD for five resources, nested
document lines, statut workflows with terminal-state locks, devis→facture
conversion, list filters, JWT authentication, and the deterministic
assistant.

## Users

- Gest_Comm_ClientFX (the desktop client) — consumes every route below.
- Django admin users managing the same records via `/admin/`.
- Anyone querying the business data through `/api/assistant/ask`.

## Outcome hypothesis

- Expected user outcome: the full commercial loop works end-to-end —
  client/article setup → devis → valide → facture → payee, plus bonliv →
  livre — entirely through the API the desktop client calls.
- Opportunity evidence: live smoke tests through the Java `ApiClient`
  verified creation, conversion (`F0002`), statut transitions, and the
  assistant on a running server.
- Signal: `python manage.py test` green (52 tests) covering every resource,
  auth flow, locks, and conversion.
- Follow-up owner/date: repo owner, at next domain change.

## Scope (in)

- Resources: `client`, `article`, `devis`, `facture`, `bonliv` —
  GET/POST on collections, GET/PUT/PATCH/DELETE on `/<id>`.
- Nested `lignes` writes on documents; computed `totalHT/totalTVA/totalTTC`.
- Statut workflows + terminal-state write/delete locks; `POST
  /api/devis/<id>/convertir`.
- `?search=`, `?statut=`, `?client=` list filters.
- JWT auth: `/api/token`, `/api/token/refresh` (rotating + blacklist),
  `/api/token/verify`, `/api/token/logout`; session auth for admin.
- `/api/assistant/ask` — deterministic read-only count/search copilot.

## Scope (out)

- TLS termination (deployment concern — documented in ADR 0008).
- Document code auto-numbering/uniqueness (policy decision pending).
- Assistant write intents (read-only by design, ADR 0002).
- Multi-user roles/permissions.

## Acceptance criteria

| # | Criterion | Scenario(s) |
|---|-----------|-------------|
| 1 | Every resource supports list/create/detail/update/delete with the documented JSON contract | CRUD round-trips per resource |
| 2 | Documents accept nested lignes, compute totals, enforce statut locks, and convert devis→facture | Document lifecycle works |
| 3 | All /api/* routes require JWT or session auth; token lifecycle incl. rotation, verify, logout | Auth lifecycle works |
| 4 | The assistant answers count/search questions across all five resources | Assistant covers the domain |

## Decisions

- JWT (simplejwt) replaced HTTP Basic — ADR 0008; credentials exchanged
  once, rotating refresh tokens, logout blacklists.
- Field names stay French-domain camelCase (`codeBonLiv`, `statutDevis`)
  matching the legacy schema and the Java client POJOs.
- Terminal states (`payee`/`annulee`/`converti`/`livre`/`annule`) are
  read-only — enforced server-side, surfaced as 400s.
