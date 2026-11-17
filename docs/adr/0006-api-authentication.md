# ADR 0006 — Authentication on /api/*

Date: 2026-11-17
Status: accepted

## Context

ADR 0001 accepted open endpoints as a LAN/desktop-tooling risk and said
auth "must be revisited before any network exposure". With the domain
complete, that revisit is due — the API now serves financial documents.

## Decision

DRF defaults in `settings.py`:

- `BasicAuthentication` **first**, then `SessionAuthentication`.
  Basic gives API clients a proper `401` + `WWW-Authenticate` challenge
  (DRF only emits 401 when the *first* authenticator provides a header);
  Session keeps the browsable API and `/admin/` working — browsers send
  no `Authorization` header, so Basic returns `None` and Session takes
  over.
- `IsAuthenticated` as the default permission — every `/api/*` route,
  including `/api/assistant/ask`.

No new dependencies: Basic auth is built into DRF and Django's
`createsuperuser` manages users. Tokens (simplejwt etc.) were rejected —
a new dependency for a single-user desktop-tool context is not KISS.

## Consequences

- **Breaking change for `Gest_Comm_ClientFX`**: it has no HTTP layer or
  auth code at all; when implemented it must send
  `Authorization: Basic base64(user:pass)` on every request.
- Basic auth sends credentials on every call — acceptable on a trusted
  LAN, **requires TLS termination before any real deployment**.
- Users are Django users (same accounts as `/admin/`); no per-resource
  permissions — any authenticated user can do everything. Fine for a
  single-operator tool; revisit if multi-user roles appear.
- Tests authenticate via `force_authenticate`; `ApiAuthTest` covers the
  real 401/Basic path.
