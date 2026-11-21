# Backlog: contact-phone-format

## US1 — As an operator, I want a customer's phone number stored exactly as I typed its digits, so that a leading zero is not silently lost

- Scenarios: @w1
- Size: M
- Notes: `CharField` + migration + canonical normalisation + charset/length validation; integer-era payloads and `0` stay accepted (D2).

## US2 — As an API consumer, I want one documented phone representation, so that I can compare and search numbers without guessing their format

- Scenarios: @w1
- Size: S
- Notes: canonical digits with an optional leading `+`; document the field in the API docs.

## US3 — As an operator, I want to find a customer by the phone digits I remember, so that a formatted search still matches the stored number

- Scenarios: @w1
- Size: S
- Notes: `/api/assistant/ask` phone search on the canonical value, replacing the `term.isdigit()` / `int(term)` special case. Ships in the same wave as US1: the column type change makes the integer cast fail.
