# Waves — contact-phone-format

Each wave IS an iteration: a time-boxed, independently shippable
increment — one branch, one PR, green tests, demoable outcome.
Do not start wave N+1 until wave N merges.

## Wave 1 — iteration 1

Scenarios proven by this wave:
- Phone numbers keep leading zeros
- Formatted phone numbers are canonicalised
- Legacy integer phone payloads are accepted
- Zero and blank mean no phone
- Invalid phone numbers are rejected
- Both phone fields behave identically
- Existing numbers survive the migration
- Assistant finds clients by phone

| Item | Title | Size | Deps | Notes |
|------|-------|------|------|-------|
| US1 | As an operator, I want a customer's phone number stored exactly as I typed its digits, so that a leading zero is not silently lost | M | — | `CharField` + migration + canonical normalisation + charset/length validation; integer-era payloads and `0` stay accepted (D2). |
| US2 | As an API consumer, I want one documented phone representation, so that I can compare and search numbers without guessing their format | S | — | canonical digits with an optional leading `+`; document the field in the API docs. |
| US3 | As an operator, I want to find a customer by the phone digits I remember, so that a formatted search still matches the stored number | S | — | `/api/assistant/ask` phone search on the canonical value, replacing the `term.isdigit()` / `int(term)` special case. Ships in the same wave as US1: the column type change makes the integer cast fail. |
