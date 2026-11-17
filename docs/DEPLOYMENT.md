# Deploying PyGestComm with TLS

JWT bearer tokens (ADR 0008) are plaintext without TLS — this guide puts
HTTPS in front of the API. TLS terminates at a reverse proxy; Django only
needs to be told it sits behind one (`DJANGO_SECURE_SSL=1`).

## 1. Run Django

```sh
cd src/GestCommProject
DJANGO_DEBUG=0 \
DJANGO_SECRET_KEY='<long random secret>' \
DJANGO_ALLOWED_HOSTS='gestcomm.example.com' \
DJANGO_SECURE_SSL=1 \
../../.venv/bin/python manage.py migrate
../../.venv/bin/python manage.py runserver 127.0.0.1:8000
```

- `DJANGO_SECRET_KEY` is **required** when `DJANGO_DEBUG=0`.
- `DJANGO_ALLOWED_HOSTS` must list the public hostname.
- `runserver` is fine for a small LAN/pilot deployment; for real
  production put a WSGI server (waitress/gunicorn) in front instead —
  same env vars apply.
- Bind Django to `127.0.0.1` only — the proxy is the single public
  entrypoint.

`DJANGO_SECURE_SSL=1` makes Django:

- trust `X-Forwarded-Proto: https` from the proxy
  (`SECURE_PROXY_SSL_HEADER`)
- redirect plain-HTTP requests to HTTPS (`SECURE_SSL_REDIRECT`)
- mark session/CSRF cookies `Secure`
- send HSTS + `X-Content-Type-Options: nosniff`

## 2. Reverse proxy

**Caddy** (automatic HTTPS — recommended): copy `deploy/Caddyfile`,
replace the domain, run `caddy run --config Caddyfile`. Caddy obtains and
renews certificates itself.

**nginx** equivalent:

```nginx
server {
    listen 443 ssl;
    server_name gestcomm.example.com;
    ssl_certificate     /etc/letsencrypt/live/gestcomm.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gestcomm.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 3. Client

In *Application → Parametre de l'application* set the server URL to
`https://gestcomm.example.com` — `ApiClient` sends
`Authorization: Bearer <jwt>` over TLS unchanged.

## Checklist before go-live

- [ ] `DJANGO_DEBUG=0`, strong `DJANGO_SECRET_KEY`
- [ ] `DJANGO_ALLOWED_HOSTS` = public hostname only
- [ ] `DJANGO_SECURE_SSL=1`
- [ ] Proxy terminates TLS and sets `X-Forwarded-Proto`
- [ ] `db.sqlite3` backed up / moved to a real DB if traffic grows
- [ ] Django user passwords strong (`createsuperuser`)
