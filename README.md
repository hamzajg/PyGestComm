# PyGestComm

A Django REST API for a small business-management app (clients, articles,
quotes and invoices).

## What it does

`PyGestComm` exposes the `GestCommApp` domain — clients, articles, quotes,
invoices — through Django REST Framework, so a desktop client
([Gest_Comm_ClientFX](../Gest_Comm_ClientFX)) or any HTTP client can read and
write it.

## Tech stack

- Python 3.10+ (CI uses 3.12)
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

## Tests

```bash
python manage.py test
```

## Status

The project has been moved to a supported Django and DRF line, and the
dependency list now contains only what the code imports. The API still covers
a single client endpoint, and the model has no update/delete route yet.
