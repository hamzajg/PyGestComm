# ADR 0005 — List filters and terminal-state write locks

Date: 2026-11-17
Status: accepted

## Context

With the full CRUD surface shipped, two gaps remained for real use:
clients had to fetch whole tables to find a record (no filtering), and
nothing stopped edits to documents that are financially final — a paid
invoice or a converted quote could be silently mutated, diverging from
reality.

## Decision

1. **Query-param filters, hand-rolled.** List endpoints accept
   `?search=` (icontains over the resource's code/name/reference fields;
   factures also match the linked `devis.codeDevis`), and devis/facture
   lists accept `?statut=` and `?client=<idClient>`. Implemented in
   `get_queryset` — no `django-filter` dependency, keeping
   `requirements.txt` minimal per ADR 0001.
2. **Terminal states are read-only.** Factures in `payee`/`annulee` and
   devis in `converti` reject PUT/PATCH/DELETE with 400
   `{detail: ...}`. Enforced in the detail views so it covers every
   write verb uniformly. Reads are unaffected.
3. **Deliberately narrow locks.** `refuse` devis stay editable
   (renegotiation is normal); `validee` factures stay editable until
   paid/cancelled. No partial transitions (e.g. payee → brouillon) are
   possible because the lock applies to the document, not the field.

## Consequences

- Filtering is additive — existing clients that send no params get the
  same unfiltered lists.
- The lock is a convention, not a DB constraint: admin and shell can
  still mutate terminal documents. Acceptable for this stage; revisit if
  audit requirements appear.
- A paid facture can't be "unpaid" via the API — correct for an invoice,
  but worth telling the desktop client before it implements statut UI.
