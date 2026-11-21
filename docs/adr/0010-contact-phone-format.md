# ADR 0010 — Phone numbers are stored as canonical text

Status: accepted (2026-11-21)
Supersedes: the `IntegerField` choice recorded in ADR 0001 for
`Client.numTelClient1` / `numTelClient2`

## Context

`Client.numTelClient1` and `numTelClient2` were `IntegerField`, matching the
legacy ADF template. A phone number is an identifier, not a quantity: the
integer type drops a leading zero (`0123456789` is stored as `123456789`),
cannot hold `+` or the separators users type, and makes `0` indistinguishable
from "no phone". The JavaFX client already compensated twice for the type —
`NouveauClientCtrl.parsePhone` coerces the field to `int`, and `phoneText`
renders `0` back as an empty field — so the corruption happened at write time,
before any display code could help. `/api/assistant/ask` had to branch on
`term.isdigit()` to match a phone at all.

## Decision

Store phone numbers as `CharField(max_length=32, blank=True, default='')` in a
**canonical form**: an optional leading `+` followed by digits only. Spaces,
dots, dashes, slashes and parentheses are stripped on write; `''` means "no
phone". `GestCommApp/phones.py` owns the rule (`canonical_phone` for writes,
`searchable_phone` for queries, both used by the serializer and the
assistant). The serializer field rejects anything that is not an optional `+`
plus 4–20 digits after stripping; a numeric payload is stringified so the
deployed client keeps working, and the legacy `0` maps to `''`.

## Alternatives considered

1. Keep `IntegerField` and format only on display. Smallest change and no
   migration, but it cannot recover a zero that was already lost, and `0`
   stays ambiguous. Rejected: the defect is in storage.
2. `CharField` storing the text exactly as typed. Most forgiving, but
   `06 12 34 56 78`, `0612345678` and `+33 6 12…` become three values, so
   search and equality need fuzzy matching.
3. Full E.164 validation. Correct for dialling, but rejects the local formats
   (`0612345678`) this app's users actually type.

## Consequences

Positive: leading zeros and `+` survive; one representation per number, so
`__contains` is enough to search; the assistant's integer special case is gone;
the field type now says what it means.

Negative: a client that renders the stored value shows `0612345678` rather than
`06 12 34 56 78` — display formatting is now a client concern and a tracked
follow-up in `Gest_Comm_ClientFX`. An external consumer doing arithmetic on the
old integer field breaks. The `0` → `''` compatibility rule looks like
permanent legacy and must be deleted once the client sends `""`.

## Reversibility

Schema-wise a two-way door for digit-only values: narrowing back to
`IntegerField` works. For data already written with a leading zero it is
one-way — an integer downgrade would truncate them. Revisit if a client needs
country-formatted display, or a consumer needs phone metadata (country, type,
label), at which point the field becomes a value object or its own model.

## References

- `specs/contact-phone-format/SPEC.md` (D1 canonical storage, D2 wire
  compatibility, D3 validation) and `DECISION-REVIEW.md` (verdict ACCEPT).
- `GestCommApp/phones.py`, `GestCommApp/serializers.py` (`PhoneField`),
  `GestCommApp/migrations/0006_alter_client_numtelclient1_and_more.py`.
