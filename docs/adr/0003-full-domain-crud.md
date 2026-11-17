# ADR 0003 — Full domain CRUD: articles, devis, factures

Date: 2026-11-17
Status: accepted

## Context

The README and ADR 0001 always described the domain as clients, articles,
quotes and invoices, but only `Client` (list/create) existed. The product
couldn't complete a single business flow — no catalog, no quotes, no
invoices — and the desktop client's `BonLivClient`/`FactureClient` shells
had no backend shape to target. This change ships the whole domain so the
API is an end-to-end working product.

## Decisions

1. **Four resources, uniform CRUD.** `Article`, `Devis`, `Facture` join
   `Client`; every resource gets list/create at the collection path and
   retrieve/update/destroy at `/<id>` (Client gains the detail route it
   lacked).
2. **Documents carry nested lines.** `Devis`/`Facture` own `LigneDevis`/
   `LigneFacture` rows exposed as a writable `lignes` array on create and
   update (update replaces the set, transactionally). Rationale: a quote
   or invoice without lines isn't a document; a separate line endpoint
   would let clients create orphaned lines.
3. **Computed, never stored, totals.** HT/TVA/TTC are serializer/model
   properties over the lines — no `total` columns to drift out of sync.
4. **Line defaults from the article.** A line referencing an `article`
   inherits designation, unit price, discount and VAT unless overridden;
   free-text lines are allowed with explicit `designation`+`prixUnitaire`.
   `prixUnitaire` stays nullable so the fallback is visible in the data.
5. **French-domain camelCase naming continues** (`codeDevis`,
   `statutFacture`, `idLigneDevis`), matching `Client` and the JavaFX
   POJOs. Article fields mirror the client's Article model 1:1.
6. **PROTECT on document FKs.** Clients/articles/devis referenced by
   documents can't be deleted; lines cascade with their document.
7. **Assistant grows with the domain.** The deterministic intents now
   count and search all four resources (resource keywords EN+FR), still
   read-only, still the stable seam for a future LLM front-end.

## Consequences

- 26 tests cover CRUD, nested-line writes, totals and the new intents.
- The devis/facture JSON shape is **provisional** — no desktop-client
  consumer exists yet; expect adjustments when `Gest_Comm_ClientFX`
  implements `BonLivClient`/`FactureClient`. Client/article shapes remain
  the stable contract.
- No auth added — consistent with ADR 0001's accepted risk; still the
  main blocker before network exposure.
- Statuses are plain choice fields settable via PATCH; no workflow
  enforcement (e.g. "can't edit a paid facture") — deliberate KISS, to be
  added only when a real rule is needed.
