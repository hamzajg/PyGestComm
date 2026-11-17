# Spec: tls-termination

> Spec-driven development artifact. This file is the contract: implementation
> is done when every acceptance criterion maps to a scenario in
> `EXAMPLES.feature` and every scenario has a passing check.

## Problem

ADR 0008 moved auth to JWT bearer tokens, which are plaintext without TLS.
The API is currently only safe on a trusted LAN; any real deployment needs
TLS terminated in front of Django, plus Django configured to trust the
proxy's `X-Forwarded-Proto` and to emit secure-cookie/HSTS headers. Today
none of that configuration exists.

## Users

- The operator deploying PyGestComm beyond a LAN.
- Gest_Comm_ClientFX users whose credentials/tokens must not cross the
  wire in cleartext.

## Outcome hypothesis

- Expected user outcome: a documented, repeatable TLS deployment — reverse
  proxy terminates HTTPS, Django runs with secure-proxy awareness, and the
  desktop client works unchanged over `https://`.
- Opportunity evidence: settings.py already has env-driven config
  (`DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_SECRET_KEY`); the client
  `ApiConfig` takes any base URL.
- Signal: `DJANGO_SECURE_SSL=1 python manage.py check` clean; deployment
  doc + example proxy config in repo.
- Follow-up owner/date: repo owner, at first real deployment.

## Scope (in)

- `DJANGO_SECURE_SSL` env flag in settings.py: `SECURE_PROXY_SSL_HEADER`,
  `SECURE_SSL_REDIRECT`, secure session/CSRF cookies, HSTS, nosniff.
- `deploy/Caddyfile` — minimal working reverse-proxy config (automatic
  HTTPS) proxying to the Django port.
- `docs/DEPLOYMENT.md` — TLS deployment steps: proxy → Django env vars →
  client base URL `https://…`; notes on certs, `DJANGO_SECRET_KEY`,
  `DJANGO_ALLOWED_HOSTS`, DB backup.
- README pointer to the deployment doc.

## Scope (out)

- Running the proxy itself (operator's host decision).
- Production WSGI server selection (waitress/gunicorn) — documented as a
  follow-up, `runserver` noted as dev-only.
- Client-side certificate pinning.

## Acceptance criteria

| # | Criterion | Scenario(s) |
|---|-----------|-------------|
| 1 | `DJANGO_SECURE_SSL=1` makes Django emit secure-cookie/HSTS/redirect settings and trust `X-Forwarded-Proto` | Secure mode settings apply |
| 2 | A working reverse-proxy config and deployment steps exist in the repo | Deployment is documented |
| 3 | Default (flag off) behavior is unchanged — dev/LAN keeps working | Dev mode unchanged |

## Decisions

- TLS terminates at the reverse proxy, not in Django — standard practice;
  Django only needs proxy-awareness flags.
- Caddy chosen for the example: automatic HTTPS with two lines of config;
  nginx equivalent documented in words.
- `DJANGO_SECURE_SSL` is opt-in so `runserver` dev flows and the existing
  test suite are unaffected.
