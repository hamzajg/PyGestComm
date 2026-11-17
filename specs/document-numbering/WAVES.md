# Waves — document-numbering

Each wave IS an iteration: a time-boxed, independently shippable
increment — one branch, one PR, green tests, demoable outcome.
Do not start wave N+1 until wave N merges.

## Wave 1 — iteration 1

Scenarios proven by this wave:
- Auto-number on create
- Explicit codes win
- Sequences are per type

| Item | Title | Size | Deps | Notes |
|------|-------|------|------|-------|
| US1 | As a user, I want documents auto-numbered when I don't supply a code, so that I never invent or duplicate codes | M | — | blank=True + migration, _next_document_code helper in serializers, client dialogs accept blank code. |
