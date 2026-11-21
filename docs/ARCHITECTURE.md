# Architecture — PyGestComm

Current-state map. Descriptive, not aspirational; see `docs/adr/` for why.

## System shape

```
Gest_Comm_ClientFX (desktop client, sibling repo)
        │  HTTP/JSON
        ▼
Django 5.2 + DRF 3.16 (runserver / WSGI)
  auth: JWTAuthentication + SessionAuthentication → IsAuthenticated
        on every /api/* route; token endpoints under /api/token*
        (ADR 0008, supersedes ADR 0006)
  ├─ GestCommProject/urls.py   routes: /api/{client,article,devis,facture}[/<id>],
  │                            /api/assistant/ask, /admin/
  └─ GestCommApp/
       ├─ models.py        Client, Article, Devis+LigneDevis, Facture+LigneFacture,
                 BonLiv+LigneBonLiv
       ├─ serializers.py   ModelSerializers; documents nest `lignes` and
       │                   expose computed totalHT/totalTVA/totalTTC
       ├─ phones.py        canonical phone text — one representation, validated
       ├─ assistant.py     deterministic copilot intents (count/search)
       ├─ admin.py         all models registered; lines as tabular inlines
       └─ views.py         generics.*APIView — ListCreate + RetrieveUpdateDestroy
        │
        ▼
sqlite3 (src/GestCommProject/db.sqlite3, gitignored dev DB)
```

## Domain

`GestCommApp` models a small-business back office — the full set the
README always promised:

- **Client** — legacy schema (`client` table, `codeClient`,
  `numTelClient*` canonical text: optional leading `+`, digits only, `''` =
  no phone — `phones.py`, ADR 0010). Also supports
  retrieve/update/delete at `/api/client/<id>`.
- **Article** — `article` table; field set mirrors the
  `Gest_Comm_ClientFX` Article POJO (`refArticle`, `descArticle`,
  purchase/sale price, discount and VAT for each side,
  `dernierPrixVenteUnitaire`). Money is `DecimalField`, rates `FloatField`.
- **Devis** — quote: `codeDevis`, `dateDevis` (defaults to today),
  `client` FK (PROTECT), `statutDevis` (brouillon/valide/refuse/converti),
  `observationDevis`, plus `LigneDevis` rows. A `valide` devis converts
  to a facture via `POST /api/devis/<id>/convertir`.
- **BonLiv** — delivery note: same document shape (`codeBonLiv`,
  `dateBonLiv`, `statutBonLiv` brouillon/valide/livre/annule,
  `observationBonLiv`) plus `LigneBonLiv` rows; `livre`/`annule` are
  terminal states.
- **Facture** — invoice: same shape plus `statutFacture`
  (brouillon/validee/payee/annulee) and an optional `devis` FK (PROTECT)
  recording which quote it came from, plus `LigneFacture` rows.

A document line stores `article` (nullable FK, PROTECT), a `designation`
snapshot, `quantite`, `prixUnitaire` (nullable → falls back to the
article's sale price), `remise` and `tva` percentages. Line/document
totals are computed properties (`quantite × prix × (1 − remise/100)`,
TVA on top) — never stored, so they can't go stale.

## Layers

Standard Django MVT/DRF: URLconf → generic class-based view → serializer →
model → SQLite. There is no service layer — the only business logic is
line-default resolution and total computation inside the serializers /
model properties, kept there because it's thin.

Nested writes: `lignes` is a writable nested serializer on devis/facture.
On create the lines are inserted with the document; on update (PUT/PATCH)
providing `lignes` replaces the whole set inside a transaction — omit the
key to leave lines untouched. A line must resolve a `designation` and a
unit price, either explicitly or from its linked `article`.

List endpoints filter via query params (`?search=`, plus `?statut=` and
`?client=` on documents) implemented in `get_queryset` — no django-filter
dependency. Terminal-state documents (facture `payee`/`annulee`, devis `converti`) are read-only: writes return 400 — enforced in the detail
views, not the serializer, so it applies to PUT/PATCH/DELETE alike.

Referential integrity is a first-class answer, not a crash:
`ProtectedDeleteMixin` (`views.py`) converts Django's `ProtectedError`
into **409 Conflict** with a `detail` sentence plus per-model
`protected` counts, on all five detail views. PROTECT still prevents a
document from losing its client/article (specs/protected-delete-conflict).

## Data

- Tables: `client`, `article`, `devis`, `ligne_devis`, `facture`,
  `ligne_facture`. Document FKs to Client/Article/Devis are `PROTECT` —
  a client or article referenced by a document can't be deleted;
  document→lines is `CASCADE`.
- Field naming stays legacy/French-domain camelCase (`codeClient`,
  `refArticle`, `codeDevis`, `statutFacture`) for compatibility with the
  desktop client — PyGestComm's `Client` naming is the convention the
  JavaFX models mirror.
- Ordering: clients/articles by code/ref; documents by descending date
  then code.

## Assistant endpoint

`POST /api/assistant/ask {"question": "..."}` — a deterministic,
read-only copilot (`GestCommApp/assistant.py`). Intents: `count`
("how many clients/articles/devis/factures"), `search` (resource-aware:
"find article X", "find devis X", bare terms try clients then articles),
`help` fallback. Response: `{intent, answer, data}` where `data` carries
the matched resource's plural key (`clients`, `articles`, `devis`,
`factures`). No LLM — this is the stable tool surface a future model
would map free text onto (ADR 0002). No write intents yet.

## Contract with the client

`Gest_Comm_ClientFX` consumes `/api/client` (GET list, POST create) with
the field set above; `/api/article` mirrors its Article POJO. **All
`/api/*` routes now require authentication** — JWT Bearer for API
clients (`/api/token` + `/api/token/refresh`), session auth for
browsers (ADR 0008). Clients obtain `{access, refresh}` once and send
`Authorization: Bearer <access>`; refresh tokens rotate and blacklist
on reuse. Any field
rename, type change, or route change is a **breaking contract change**
requiring coordination across both repos — record it as an ADR and
update both AGENTS.md files. The devis/facture routes have no client
consumer yet; their shape is provisional until `Gest_Comm_ClientFX`
implements `BonLivClient`/`FactureClient`.
