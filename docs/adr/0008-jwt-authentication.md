# ADR 0008 — JWT authentication replaces HTTP Basic

Date: 2026-11-17
Status: accepted (supersedes the auth mechanism of ADR 0006)

## Context

ADR 0006 chose HTTP Basic auth: credentials are sent on **every**
request, there is no expiry, no revocation short of a password change,
and credentials traverse the wire in cleartext without TLS. For a
financial-management product that is no longer an acceptable posture —
the community-standard answer for DRF APIs is short-lived access tokens
with a rotating refresh token (`djangorestframework-simplejwt`).

## Decision

- `djangorestframework-simplejwt` + its `token_blacklist` app.
- Token endpoints (all `AllowAny`, rate-limit candidates later):
  - `POST /api/token` — `{username, password}` → `{access, refresh}`
  - `POST /api/token/refresh` — `{refresh}` → new `access` (+ rotated
    `refresh`)
  - `POST /api/token/verify` — validate an access token
- `DEFAULT_AUTHENTICATION_CLASSES` = `JWTAuthentication` then
  `SessionAuthentication` (session keeps `/admin/` + browsable API).
  **BasicAuthentication removed** — credentials are exchanged exactly
  once at `/api/token`.
- Lifetimes: access **1 h**, refresh **7 d**; refresh tokens **rotate
  on every use** and the old one is **blacklisted** (reuse → 401).
- `IsAuthenticated` unchanged — still every `/api/*` route.

## Consequences

- Clients must implement a token flow: obtain pair → `Bearer` header →
  on 401 refresh once and retry. `Gest_Comm_ClientFX` does this in
  `ApiClient`/`ApiConfig`.
- Access tokens are bearer tokens: anyone holding one can call the API
  until expiry — TLS becomes more important, not less (ADR still
  requires it before non-LAN deployment).
- `POST /api/token/logout` (`TokenBlacklistView`, auth required)
  blacklists the presented refresh token — real logout/revocation.
- Breaking change for any Basic-auth client — only `Gest_Comm_ClientFX`
  consumes this API and is updated in the same change set.
- New dependency `djangorestframework-simplejwt` (PyJWT under the
  hood); requirements.txt updated.
