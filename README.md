# PyGestComm

A Django REST API for a small business-management app (clients, articles,
quotes and invoices).

## What it does

`PyGestComm` exposes the `GestCommApp` domain — clients, articles, quotes,
invoices — through Django REST Framework, so a desktop client
([Gest_Comm_ClientFX](../Gest_Comm_ClientFX)) or any HTTP client can read and
write it.

## Tech stack

- Python 3.10+ (CI uses 3.13)
- Django 5.2 (LTS) and Django REST Framework 3.16

## Project layout

```
src/
  GestCommProject/
    GestCommProject/       # settings, urls, wsgi
    GestCommApp/           # models, serializers, views, migrations
    db.sqlite3             # local development database
requirements.txt
```

## Configuration

Settings are read from the environment:

| Variable | Default | Meaning |
|---|---|---|
| `DJANGO_SECRET_KEY` | — | **Required** unless `DJANGO_DEBUG` is on. In debug mode an ephemeral random key is generated at startup. |
| `DJANGO_DEBUG` | `true` | Set to `false` (or `0`/`no`/`off`) for anything other than local development. |
| `DJANGO_ALLOWED_HOSTS` | empty | Comma-separated hostnames; required when debug is off. |

For local development, nothing needs to be set:

```bash
cd src/GestCommProject
python3 -m venv .venv && source .venv/bin/activate
pip install -r ../../requirements.txt
python manage.py migrate
python manage.py runserver
```

For a deployment:

```bash
export DJANGO_DEBUG=false
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
export DJANGO_ALLOWED_HOSTS=example.com
```

## Authentication

All `/api/*` endpoints require authentication (ADR 0006):

- **API clients** (e.g. Gest_Comm_ClientFX) send HTTP Basic auth:
  `Authorization: Basic base64(username:password)`.
- **Browsers / admin** use the Django session — log in at `/admin/`.

Create a user with `python manage.py createsuperuser`. Unauthenticated
requests get `401` with a `WWW-Authenticate` challenge. Basic auth sends
credentials on every request — only acceptable over HTTPS or a trusted
LAN; put TLS in front before any real deployment.

## API

All resources support list/create at the collection path and
retrieve/update(partial)/delete at `/<id>`:

| Resource | Path | Auth |
|---|---|---|
| Clients | `/api/client`, `/api/client/<id>` | Basic or session |
| Articles | `/api/article`, `/api/article/<id>` | Basic or session |
| Devis (quotes) | `/api/devis`, `/api/devis/<id>` | Basic or session |
| | `POST /api/devis/<id>/convertir` | Basic or session |
| Factures (invoices) | `/api/facture`, `/api/facture/<id>` | Basic or session |
| Assistant | `POST /api/assistant/ask` | Basic or session |

List endpoints accept query params: `?search=` (code/name/reference
icontains) on all four resources, plus `?statut=` and `?client=<id>` on
devis/factures. Invoices in `payee`/`annulee` and devis in `converti`
are read-only — writes return 400.

Documents (`devis`, `facture`) accept a `lignes` array on create and on
update (update replaces the whole set). A line needs either `article`
(id — designation, price, discount and VAT default from it) or explicit
`designation` + `prixUnitaire`.

## Tests

```bash
python manage.py test
```

41 tests covering auth enforcement, the client/article endpoints,
devis/facture creation with nested lines and totals, status updates,
conversion, list filters, terminal-state locks, and the assistant
intents.

## Status

The API covers the full declared domain — clients, articles, devis and
factures — with CRUD endpoints, an authenticated assistant, admin site,
and Basic/session auth on `/api/*`. Remaining gap: TLS termination for
real deployments (Basic auth is plaintext without it).
