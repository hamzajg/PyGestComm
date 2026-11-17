# AGENTS.md — PyGestComm

Guidance for AI agents (and humans) working in this repository.

## Project

PyGestComm is a Django REST Framework API for a small business-management
domain (clients, articles, quotes, invoices). It exposes CRUD endpoints
for all four resources — `Client`, `Article`, `Devis` (quotes) and
`Facture` (invoices) — plus a deterministic assistant — and is the
backend for the `Gest_Comm_ClientFX` desktop client.
Stack: Python 3.10+ (CI uses 3.13), Django 5.2 LTS, DRF 3.16, SQLite.

## Commands

Verified 2026-11-13 against CI (`.github/workflows/ci.yml`) and README.

| Task | Command |
|---|---|
| Install deps | `pip install -r requirements.txt` |
| Migrate | `cd src/GestCommProject && python manage.py migrate` |
| Run dev server | `cd src/GestCommProject && python manage.py runserver` |
| Test | `cd src/GestCommProject && python manage.py test` (26 tests) |
| Django checks | `python manage.py check` |

Requires: env vars per README — `DJANGO_SECRET_KEY` (required unless
`DJANGO_DEBUG` on), `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`. Defaults work for
local dev. DB is `src/GestCommProject/db.sqlite3` (gitignored dev DB).

## Architecture

Django project under `src/GestCommProject/`:

- `GestCommProject/` — `settings.py` (env-driven), `urls.py`, `wsgi.py`.
- `GestCommApp/` — the domain app: `models.py` (`Client`, `Article`,
  `Devis`+`LigneDevis`, `Facture`+`LigneFacture`), `serializers.py`
  (ModelSerializers; documents nest writable `lignes` and expose
  computed `totalHT`/`totalTVA`/`totalTTC`), `assistant.py`,
  `views.py` (list/create + retrieve/update/destroy per resource),
  `admin.py` (all models; lines as tabular inlines), `tests.py`,
  `migrations/`.
- `manage.py` at `src/GestCommProject/manage.py`.

### API contract (backend ↔ Gest_Comm_ClientFX)

Every resource follows the same pattern: `GET`/`POST` on the collection
path, `GET`/`PUT`/`PATCH`/`DELETE` on `/<id>` (the PK is the `idXxx`
AutoField). Devis/facture payloads take a `lignes` array — on update it
replaces the whole set; omit it to keep existing lines.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET/POST | `/api/client` | none | List / create clients (ordered by `codeClient`) |
| GET/PUT/PATCH/DELETE | `/api/client/<id>` | none | Client detail |
| GET/POST | `/api/article` | none | List / create articles (ordered by `refArticle`) |
| GET/PUT/PATCH/DELETE | `/api/article/<id>` | none | Article detail |
| GET/POST | `/api/devis` | none | List / create quotes with nested `lignes` |
| GET/PUT/PATCH/DELETE | `/api/devis/<id>` | none | Devis detail |
| GET/POST | `/api/facture` | none | List / create invoices with nested `lignes` |
| GET/PUT/PATCH/DELETE | `/api/facture/<id>` | none | Facture detail |
| POST | `/api/assistant/ask` | none | `{question}` → `{intent, answer, data}` — deterministic read-only copilot (count/search intents over all four resources) |
| * | `/admin/` | Django admin | Admin site |

Client fields (`models.py`, table `client`): `idClient` (PK), `codeClient`,
`nomPrenomClient`, `matFiscalClient`, `addresseClient1/2`,
`numTelClient1/2` (IntegerField — note: numeric, not string).

Article fields (table `article`): `idArticle` (PK), `refArticle`,
`descArticle`, `prixAchatUnitaire`/`prixVenteUnitaire` (Decimal),
`remiseAchat`/`remiseVente`/`tvaAchat`/`tvaVente` (Float percentages),
`dernierPrixVenteUnitaire` (nullable Decimal). Mirrors the
`Gest_Comm_ClientFX` Article POJO.

Devis fields (table `devis`): `idDevis` (PK), `codeDevis`, `dateDevis`
(defaults to today), `client` (FK → `idClient`), `statutDevis`
(`brouillon`/`valide`/`refuse`), `observationDevis`, `lignes`.

Facture fields (table `facture`): same shape as devis plus `devis`
(nullable FK → `idDevis`) and `statutFacture`
(`brouillon`/`validee`/`payee`/`annulee`).

Document line fields (`ligne_devis`/`ligne_facture`): `article` (nullable
FK → `idArticle`), `designation`, `quantite`, `prixUnitaire` (nullable —
falls back to the article's `prixVenteUnitaire`), `remise`, `tva`.
Response adds read-only `totalHT`/`totalTVA` per line and
`totalHT`/`totalTVA`/`totalTTC` per document — computed, never stored.

## Conventions

- Standard Django/DRF layout; keep views as `generics.*APIView` classes in
  `views.py`, serializers in `serializers.py`.
- Field names are French-domain (`codeClient`, `nomPrenomClient`,
  `codeDevis`, `statutFacture`) and map to legacy table/column names
  (`db_table`, suffix-style field names) — match the existing naming,
  don't anglicise.
- Model changes require a migration in `GestCommApp/migrations/`.
- Money is `DecimalField`, discount/VAT rates are `FloatField` percentages
  (e.g. `tva=20` means 20%). Line/document totals are computed properties —
  don't add stored total columns.
- Document FKs (`client`, `article`, `devis`) use `on_delete=PROTECT`;
  document→lines uses `CASCADE`. Nested `lignes` writes resolve
  defaults from the linked article in `serializers.py` — keep that logic
  there, not in views.
- KISS: plain Django + DRF only; `requirements.txt` is intentionally
  minimal (Django + DRF only).

## Landmines

- **Default branch is `master`, not `main`** — branch/PR accordingly.
- Devis/facture JSON shapes are provisional — no `Gest_Comm_ClientFX`
  consumer exists yet for them; client/article shapes are the stable
  contract.
- `numTelClient1/2` are `IntegerField` — phone numbers as ints; legacy
  constraint, changing the type is a migration + client-coordination job.
- `DJANGO_SECRET_KEY` has no safe default in production mode — required env.
- `db.sqlite3` lives inside the project dir and is gitignored for dev.
- Settings/urls files carry stale Django-2.0 docstring examples — ignore
  them; they're comments only.

## Agent rules

- Branch from `master`; name branches `feat/*`, `fix/*`, `chore/*`, `docs/*`.
- Docs-only changes still go through a PR; never commit to `master` directly.
- Verify before claiming: run `python manage.py test` from
  `src/GestCommProject` and report the real result.
- Keep changes minimal and consistent with surrounding code. No drive-by
  refactors.
- Update AGENTS.md / docs/ARCHITECTURE.md when your change alters commands,
  models/fields, or API routes (coordinate with Gest_Comm_ClientFX).
