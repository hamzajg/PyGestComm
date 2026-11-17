# AGENTS.md — PyGestComm

Guidance for AI agents (and humans) working in this repository.

## Project

PyGestComm is a Django REST Framework API for a small business-management
domain (clients, articles, quotes, invoices). It exposes CRUD endpoints
for all five resources — `Client`, `Article`, `Devis` (quotes),
`Facture` (invoices) and `BonLiv` (delivery notes) — plus a
deterministic assistant — and is the
backend for the `Gest_Comm_ClientFX` desktop client.
Stack: Python 3.10+ (CI uses 3.13), Django 5.2 LTS, DRF 3.16, SQLite.

## Commands

Verified 2026-11-13 against CI (`.github/workflows/ci.yml`) and README.

| Task | Command |
|---|---|
| Install deps | `pip install -r requirements.txt` |
| Migrate | `cd src/GestCommProject && python manage.py migrate` |
| Run dev server | `cd src/GestCommProject && python manage.py runserver` |
| Test | `cd src/GestCommProject && python manage.py test` (41 tests) |
| Django checks | `python manage.py check` |

Requires: env vars per README — `DJANGO_SECRET_KEY` (required unless
`DJANGO_DEBUG` on), `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`. Defaults work for
local dev. DB is `src/GestCommProject/db.sqlite3` (gitignored dev DB).
Create API users with `python manage.py createsuperuser`.

## Architecture

Django project under `src/GestCommProject/`:

- `GestCommProject/` — `settings.py` (env-driven), `urls.py`, `wsgi.py`.
- `GestCommApp/` — the domain app: `models.py` (`Client`, `Article`,
  `Devis`+`LigneDevis`, `Facture`+`LigneFacture`,
  `BonLiv`+`LigneBonLiv`), `serializers.py`
  (ModelSerializers; documents nest writable `lignes` and expose
  computed `totalHT`/`totalTVA`/`totalTTC`), `assistant.py`,
  `views.py` (list/create + retrieve/update/destroy per resource),
  `admin.py` (all models; lines as tabular inlines), `tests.py`,
  `migrations/`.
- `manage.py` at `src/GestCommProject/manage.py`.

### API contract (backend ↔ Gest_Comm_ClientFX)

All `/api/*` routes require auth (ADR 0006): HTTP Basic for API clients,
Django session for the browsable API/admin. Unauthenticated → 401.
**Gest_Comm_ClientFX has no auth code yet** — it must send
`Authorization: Basic ...` before it can call any endpoint.

Every resource follows the same pattern: `GET`/`POST` on the collection
path, `GET`/`PUT`/`PATCH`/`DELETE` on `/<id>` (the PK is the `idXxx`
AutoField). Devis/facture payloads take a `lignes` array — on update it
replaces the whole set; omit it to keep existing lines.

List endpoints accept `?search=` (icontains on code/name/reference —
factures also match the linked `devis.codeDevis`), and devis/facture
lists additionally accept `?statut=` and `?client=<idClient>`.
Terminal-state documents are read-only: factures `payee`/`annulee` and
devis `converti` reject PUT/PATCH/DELETE with 400.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET/POST | `/api/client` | Basic/session | List / create clients (ordered by `codeClient`) |
| GET/PUT/PATCH/DELETE | `/api/client/<id>` | Basic/session | Client detail |
| GET/POST | `/api/article` | Basic/session | List / create articles (ordered by `refArticle`) |
| GET/PUT/PATCH/DELETE | `/api/article/<id>` | Basic/session | Article detail |
| GET/POST | `/api/devis` | Basic/session | List / create quotes with nested `lignes` |
| GET/PUT/PATCH/DELETE | `/api/devis/<id>` | Basic/session | Devis detail |
| POST | `/api/devis/<id>/convertir` | Basic/session | Convert a `valide` devis → `brouillon` facture (copies client+lines, sets devis `converti`) |
| GET/POST | `/api/facture` | Basic/session | List / create invoices with nested `lignes` |
| GET/PUT/PATCH/DELETE | `/api/facture/<id>` | Basic/session | Facture detail |
| GET/POST | `/api/bonliv` | Basic/session | List / create delivery notes with nested `lignes` |
| GET/PUT/PATCH/DELETE | `/api/bonliv/<id>` | Basic/session | BonLiv detail |
| POST | `/api/assistant/ask` | Basic/session | `{question}` → `{intent, answer, data}` — deterministic read-only copilot (count/search intents over all five resources) |
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
(`brouillon`/`valide`/`refuse`/`converti`), `observationDevis`, `lignes`.

Facture fields (table `facture`): same shape as devis plus `devis`
(nullable FK → `idDevis`) and `statutFacture` (`brouillon`/`validee`/
`payee`/`annulee`).

BonLiv fields (table `bonliv`): same document shape (`idBonLiv`,
`codeBonLiv`, `dateBonLiv`, client FK, `statutBonLiv`
`brouillon`/`valide`/`livre`/`annule`, `observationBonLiv`) plus
`LigneBonLiv` rows (`idLigneBonLiv`, `bonliv` FK, article FK,
`designation`, `quantite`, `prixUnitaire`, `remise`, `tva`) — same
line mechanics and computed totals as devis/facture.
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
