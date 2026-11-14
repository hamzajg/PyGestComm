# AGENTS.md — PyGestComm

Guidance for AI agents (and humans) working in this repository.

## Project

PyGestComm is a Django REST Framework API for a small business-management
domain (clients, articles, quotes, invoices). Today it exposes **one**
endpoint — `Client` list/create — and is the backend for the
`Gest_Comm_ClientFX` desktop client. Early-stage project.
Stack: Python 3.10+ (CI uses 3.13), Django 5.2 LTS, DRF 3.16, SQLite.

## Commands

Verified 2026-11-13 against CI (`.github/workflows/ci.yml`) and README.

| Task | Command |
|---|---|
| Install deps | `pip install -r requirements.txt` |
| Migrate | `cd src/GestCommProject && python manage.py migrate` |
| Run dev server | `cd src/GestCommProject && python manage.py runserver` |
| Test | `cd src/GestCommProject && python manage.py test` (5 tests) |
| Django checks | `python manage.py check` |

Requires: env vars per README — `DJANGO_SECRET_KEY` (required unless
`DJANGO_DEBUG` on), `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`. Defaults work for
local dev. DB is `src/GestCommProject/db.sqlite3` (committed dev DB).

## Architecture

Django project under `src/GestCommProject/`:

- `GestCommProject/` — `settings.py` (env-driven), `urls.py`, `wsgi.py`.
- `GestCommApp/` — the domain app: `models.py` (`Client`),
  `serializers.py` (`ClientSerializer`, `fields = '__all__'`),
  `views.py` (`ClientList` = `ListCreateAPIView`), `tests.py`,
  `migrations/`.
- `manage.py` at `src/GestCommProject/manage.py`.

### API contract (backend ↔ Gest_Comm_ClientFX)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/client` | none | List clients (ordered by `codeClient`) |
| POST | `/api/client` | none | Create client |
| * | `/admin/` | Django admin | Admin site |

Client fields (`models.py`, table `client`): `idClient` (PK), `codeClient`,
`nomPrenomClient`, `matFiscalClient`, `addresseClient1/2`,
`numTelClient1/2` (IntegerField — note: numeric, not string). No
update/delete routes yet — README states this explicitly.

## Conventions

- Standard Django/DRF layout; keep views as `generics.*APIView` classes in
  `views.py`, serializers in `serializers.py`.
- Field names are French-domain (`codeClient`, `nomPrenomClient`) and map
  to legacy table/column names (`db_table`, suffix-style field names) —
  match the existing naming, don't anglicise.
- Model changes require a migration in `GestCommApp/migrations/`.
- KISS: plain Django + DRF only; `requirements.txt` is intentionally
  minimal (Django + DRF only).

## Landmines

- **Default branch is `master`, not `main`** — branch/PR accordingly.
- Only GET/POST on `/api/client` exist; PUT/PATCH/DELETE are absent — don't
  assume REST completeness.
- `numTelClient1/2` are `IntegerField` — phone numbers as ints; legacy
  constraint, changing the type is a migration + client-coordination job.
- `DJANGO_SECRET_KEY` has no safe default in production mode — required env.
- `db.sqlite3` lives inside the project dir and is committed for dev.
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
