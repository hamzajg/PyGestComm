# ADR 0002 — Deterministic assistant endpoint (copilot tool surface)

## Status

Accepted — implemented on `feat/assistant-copilot`.

## Context

The queued Phase-2 candidate was a "Django admin copilot — chat endpoint
over the existing REST API". The repo has exactly one resource (Client,
list/create only) and no LLM provider, key management, or auth on the
API. A real LLM chat endpoint would add a vendor dependency, a secret,
and unbounded generation over business data — heavy machinery for a
single-table API, and the desktop client contract would be unaffected
either way.

## Decision

`POST /api/assistant/ask` returns `{intent, answer, data}` from
`GestCommApp/assistant.py` — a small deterministic intent mapper:

- `count` — "how many clients" / "combien de clients" → ORM count.
- `search` — "find client X" / "client X" / bare term → ORM `icontains`
  across code/name/tax-id/addresses, plus exact phone match for digit
  terms (phones are `IntegerField`). Capped at 20 results.
- `help` — fallback for trivially short input.

The endpoint is **read-only by design**: write intents (create/update
client) are deliberately absent until a human-confirmation flow exists —
same rule as stream-weave's agent tools.

## Consequences

- Zero new dependencies; works offline; fully unit-testable via
  `APITestCase` (7 new tests).
- The intent contract is the *stable seam*: a future LLM front-end
  translates free text → these intents, or calls `/api/client` directly.
  Swapping in a real model doesn't change this endpoint's shape.
- Honest limitation: regex intents won't understand arbitrary phrasing —
  that's the point of deferring the LLM, not a bug to patch with more
  regex.
- No auth added — consistent with the existing API (also unauthenticated);
  if auth lands, this route inherits whatever dependency is chosen.
