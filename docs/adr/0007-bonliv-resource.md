# ADR 0007 — BonLiv (delivery note) resource

## Status

Accepted — implemented on `feat/bonliv`.

## Context

The Gest_Comm_ClientFX UI has always had a *Bon Liv* menu (delivery
notes), but the backend domain only covered clients, articles, devis
and factures. Delivery notes complete the commercial chain: a client
order becomes a devis, optionally an invoice, and a bon de livraison
records what physically shipped.

## Decision

Add `BonLiv` + `LigneBonLiv` mirroring the `Devis`/`Facture` document
pattern exactly:

- Header: `idBonLiv`, `codeBonLiv`, `dateBonLiv`, `client` FK (PROTECT),
  `statutBonLiv`, `observationBonLiv`.
- Statuts: `brouillon` → `valide` → `livre`, plus `annule`.
  `livre`/`annule` are terminal — writes/deletes are rejected with 400,
  same lock mechanism as payee/annulee factures (ADR 0005).
- Lines: `LigneBonLiv` identical to `LigneDevis`/`LigneFacture`
  (article FK nullable, designation, quantite, prixUnitaire, remise,
  tva) with the same article-default resolution and computed
  HT/TVA/TTC totals.
- Routes: `GET/POST /api/bonliv`, `GET/PUT/PATCH/DELETE
  /api/bonliv/<id>` — same filters (`?search=`/`?statut=`/`?client=`)
  via `_document_queryset`.

No devis/facture linkage: a bon de livraison in this domain is
standalone (it can be created from scratch or from the client UI's
article picker). A future `devis`/`facture` FK can be added if the
business needs traceability.

## Consequences

- The Gest_Comm_ClientFX *Bon Liv* menu items can now be wired to real
  endpoints; `BonLivClient` model shell gets replaced by a real
  `BonLiv` POJO.
- The assistant intentionally does not cover bonliv yet — its intent
  table is kept minimal per ADR 0002; extend only when a caller needs
  it.
