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

## API

All resources support list/create at the collection path and
retrieve/update(partial)/delete at `/<id>`:

| Resource | Path | Notes |
|---|---|---|
| Clients | `/api/client`, `/api/client/<id>` | Legacy field names (`codeClient`, …) |
| Articles | `/api/article`, `/api/article/<id>` | Sale/purchase prices, discounts, VAT |
| Devis (quotes) | `/api/devis`, `/api/devis/<id>` | Nested `lignes`, computed HT/TVA/TTC totals |
| Factures (invoices) | `/api/facture`, `/api/facture/<id>` | Same line shape; optional `devis` link |
| Assistant | `POST /api/assistant/ask` | Deterministic copilot: count/search over all four resources |

Documents (`devis`, `facture`) accept a `lignes` array on create and on
update (update replaces the whole set). A line needs either `article`
(id — designation, price, discount and VAT default from it) or explicit
`designation` + `prixUnitaire`.

## Tests

```bash
python manage.py test
```

26 tests covering the client/article endpoints, devis/facture creation
with nested lines and totals, status updates, and the assistant intents.

## Status

The API covers the full declared domain — clients, articles, devis and
factures — with CRUD endpoints, an admin site, and a deterministic
assistant. Still no authentication on `/api/*` (see ADR 0001); that's the
main gap before any network exposure.
