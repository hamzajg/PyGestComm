# ADR 0009 — TLS termination at a reverse proxy

Date: 2026-11-17
Status: accepted

## Context

ADR 0008 replaced Basic auth with JWT bearer tokens. Bearer tokens are
credentials: without TLS they cross the wire in cleartext on every
request. The API was explicitly LAN-only until now; real deployment
needs HTTPS.

## Decision

TLS terminates at a reverse proxy (Caddy example shipped in
`deploy/Caddyfile`); Django is not the TLS endpoint.

- `DJANGO_SECURE_SSL=1` enables proxy-awareness:
  `SECURE_PROXY_SSL_HEADER` trusts `X-Forwarded-Proto`,
  `SECURE_SSL_REDIRECT` forces HTTPS, session/CSRF cookies become
  `Secure`, HSTS + nosniff are sent.
- Off by default: dev server, tests, and LAN deployments are unchanged.
- `docs/DEPLOYMENT.md` documents proxy → Django → client configuration.

## Consequences

- Operators must run a proxy with valid certs; Django binds localhost.
- `runserver` remains dev-grade — a WSGI server is a documented
  follow-up, not part of this change.
- The JavaFX client needs no code change — `ApiConfig` accepts any
  `https://` base URL.
