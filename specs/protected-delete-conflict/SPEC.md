# Spec: protected-delete-conflict

> Spec-driven development artifact. This file is the contract: implementation
> is done when every acceptance criterion maps to a scenario in
> `EXAMPLES.feature` and every scenario has a passing check.

## Problem

Deleting a client, article or quote that other records still point at
returns **HTTP 500 (ProtectedError)** instead of a client-actionable
answer. The Django `on_delete=PROTECT` FKs are intentional (a document must
never be silently orphaned), but the uncaught `ProtectedError` escapes the
DRF view and produces a server error page/JSON. In
`Gest_Comm_ClientFX` this surfaces as "Erreur : HTTP 500 from
http://localhost:8000/api/client/3 — ProtectedError at /api/client/3 …",
which tells the user nothing they can act on and hides a normal business
rule behind a crash.

## Users

- Desktop operators using `Gest_Comm_ClientFX` (French UI) who delete rows
  from the Clients / Articles / Devis tabs.
- Any HTTP consumer of the API (scripts, future web client) that must
  distinguish "not allowed" from "the server broke".

## Outcome hypothesis

- Expected user outcome: a blocked delete is explained ("this client is
  used by 2 devis and 1 facture"), so the operator removes or reassigns the
  dependants instead of retrying a delete that cannot work.
- Opportunity evidence: reproduced live on 2026-11-20 against the running
  dev server — `DELETE /api/client/3` and `DELETE /api/article/4` returned
  `500 ProtectedError` while the same run's other 30 checks passed.
- Signal: 0 PROTECT-driven 5xx responses in the HTTP smoke; the smoke
  asserts 409 for all three protected resources. Baseline before the fix:
  2/2 such deletes returned 500.
- Follow-up owner/date: agent, at validation of this feature.

## Scope (in)

- A shared `ProtectedDeleteMixin` on the detail views: catch
  `django.db.models.ProtectedError` and answer **409 Conflict** with a JSON
  body `{"detail": "<human sentence>", "protected": [{"model", "count"}]}`.
- Apply it to `ClientDetail`, `ArticleDetail`, `DevisDetail`,
  `FactureDetail`, `BonLivDetail`.
- Terminal-state locks (400) keep precedence over the conflict answer.
- Tests for client, article and devis-protected-by-facture deletes, plus a
  regression test that an unreferenced delete still returns 204.
- README/AGENTS.md/ARCHITECTURE.md document the 409 contract.

## Scope (out)

- No schema or migration change: PROTECT stays.
- No cascade/soft-delete option (rejected in the Decisions block).
- No client-repo code changes (tracked in `Gest_Comm_ClientFX` /
  `delete-conflict-ux`).
- No change to the document terminal-state rules.

## Acceptance criteria

| # | Criterion | Scenario(s) |
|---|-----------|-------------|
| 1 | Deleting a client referenced by any devis/facture/bonliv answers 409 with a detail naming the blocking records, never 500 | @w1 |
| 2 | Deleting an article referenced by any document line answers 409, never 500 | @w1 |
| 3 | Deleting a devis that a facture still references answers 409 (a `converti` devis still answers 400 first) | @w1 |
| 4 | Deleting a record with no dependants still returns 204, and the resource is then gone (404 on retrieve) | @w1 |
| 5 | The full suite stays green and the live HTTP lifecycle smoke reports 0 unexpected 5xx | @w1 |

## Decisions

### D1 — Answer a blocked delete with 409 Conflict instead of 400 Bad Request

- **Context & forces:** `PROTECT` means the request is well-formed but
  conflicts with the resource's current state (referenced by other
  records). The desktop client already treats 4xx as "show the message";
  the missing piece is an answer that is neither a crash nor an ambiguous
  validation error. `Gest_Comm_ClientFX` also needs to distinguish this
  case to phrase the French message.
- **Options considered:**
  1. Leave `ProtectedError` uncaught and let `handler500` render (status quo
     — simplest, zero code, but a normal user action crashes).
  2. Catch in each `destroy()` and return `400 {"detail": ...}` like the
     terminal-state lock (smallest change, but conflates "bad payload" with
     "referenced by other data").
  3. Catch in one shared mixin and return **409 Conflict** with a
     structured `protected` list (most reversible: one mixin, no model or
     serializer change).
- **Decision & why:** Option 3. 409 is the standard "state conflict"
  signal, keeps 400 meaning "the payload/state is invalid for the write
  itself", and lets any consumer react without string-matching a message.
- **Consequences:** (+) no 5xx on a routine user action; the reason is
  machine-readable; one place to change. (−) adds a second 4xx code to the
  documented contract; older consumers that only special-case 400 now see a
  sibling code (they already display `detail` for all 4xx).
- **Reversibility:** two-way door — the mixin is local to `views.py`;
  reverting restores the previous behaviour without data impact. Revisit if
  a consumer cannot handle 409.

### D2 — Keep `PROTECT`; never cascade or soft-delete

- **Context & forces:** Deleting a client would otherwise silently delete
  or orphan quotes/invoices/delivery notes — unacceptable for accounting
  records, and the existing ADRs treat stored documents as evidence.
- **Options considered:**
  1. Keep `PROTECT` and explain the block (chosen).
  2. Switch to `CASCADE` (deletes financial history — reversible only by
     restoring a backup).
  3. Add `deletedAt` soft deletes and filter every queryset (a schema and
     contract change touching all five resources).
- **Decision & why:** Option 1. The failure is in the *response*, not the
  constraint; the constraint is a feature.
- **Consequences:** (+) data integrity and an auditable API. (−) users must
  delete dependants first, so the message must be explicit.
- **Reversibility:** one-way door for data semantics (a cascade change
  after the fact cannot resurrect deleted documents); the current decision
  is the reversible one.
