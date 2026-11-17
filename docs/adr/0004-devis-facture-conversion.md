# ADR 0004 — Devis → facture conversion endpoint

Date: 2026-11-17
Status: accepted

## Context

ADR 0003 shipped devis and facture as independent documents with an
optional `devis` FK, but the actual business flow — quote accepted, then
invoiced — required the caller to re-create the invoice and its lines by
hand. That's error-prone and breaks the end-to-end story.

## Decision

`POST /api/devis/<id>/convertir` converts a devis into a facture:

- Only `statutDevis = valide` devis can convert; anything else → 400,
  unknown id → 404.
- The new facture is `brouillon`, linked via `devis`, with `codeFacture`
  defaulting to `F%04d` of the devis id (overridable), `dateFacture`
  defaulting to the devis date, observation copied.
- All lines are copied verbatim (article, designation, quantite,
  prixUnitaire, remise, tva) — the invoice freezes what was quoted.
- The devis becomes `statutDevis = converti`, which also prevents
  double conversion.
- Whole operation is one transaction.

## Consequences

- The domain flow is now closed: client → article → devis → valide →
  facture → payee.
- `converti` added to `Devis.STATUT_CHOICES` (migration 0003).
- Conversion is one-way and doesn't copy later edits — a converted
  facture is edited directly, like a real invoice.
- Still no auth; same accepted risk as ADR 0001.
