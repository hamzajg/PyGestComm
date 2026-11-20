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

All `/api/*` endpoints require authentication (ADR 0008):

- **API clients** (e.g. Gest_Comm_ClientFX) exchange credentials once
  for JWT tokens: `POST /api/token` with `{username, password}` returns
  `{access, refresh}`; then send `Authorization: Bearer <access>` on
  every request. Access tokens live 1 h; call `/api/token/refresh`
  with the refresh token (rotated + blacklisted on use, 7 d lifetime)
  to get a new pair.
- **Browsers / admin** use the Django session — log in at `/admin/`.

Create a user with `python manage.py createsuperuser`. Unauthenticated
requests get `401`. TLS is still required before any non-LAN
deployment — bearer tokens must not cross the wire in cleartext.

## API

All resources support list/create at the collection path and
retrieve/update(partial)/delete at `/<id>`:

| Resource | Path | Auth |
|---|---|---|
| Clients | `/api/client`, `/api/client/<id>` | JWT or session |
| Articles | `/api/article`, `/api/article/<id>` | JWT or session |
| Devis (quotes) | `/api/devis`, `/api/devis/<id>` | JWT or session |
| | `POST /api/devis/<id>/convertir` | JWT or session |
| Factures (invoices) | `/api/facture`, `/api/facture/<id>` | JWT or session |
| Bon de livraison | `/api/bonliv`, `/api/bonliv/<id>` | JWT or session |
| Assistant | `POST /api/assistant/ask` | JWT or session |

List endpoints accept query params: `?search=` (code/name/reference
icontains) on all five resources, plus `?statut=` and `?client=<id>` on
devis/factures. Invoices in `payee`/`annulee` and devis in `converti`
are read-only — writes return 400.

Deleting a record that documents still reference answers **409 Conflict**
(the `PROTECT` foreign keys are deliberate), with a body naming what
blocks it:

```json
{"detail": "This client cannot be deleted: still referenced by 1 devis.",
 "protected": [{"model": "devis", "label": "devis", "count": 1}]}
```

Documents (`devis`, `facture`) accept a `lignes` array on create and on
update (update replaces the whole set). A line needs either `article`
(id — designation, price, discount and VAT default from it) or explicit
`designation` + `prixUnitaire`.

## Tests

```bash
python manage.py test
```

61 tests covering auth enforcement, the client/article endpoints,
devis/facture creation with nested lines and totals, status updates,
conversion, list filters, terminal-state locks, and the assistant
intents.

## Status

The API covers the full declared domain — clients, articles, devis and
factures — with CRUD endpoints, an authenticated assistant, admin site,
and JWT/session auth on `/api/*`. TLS deployment guide: `docs/DEPLOYMENT.md`
(+ `deploy/Caddyfile`) — set `DJANGO_SECURE_SSL=1` behind a TLS proxy.
