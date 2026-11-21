# Spec: contact-phone-format

> Spec-driven development artifact. This file is the contract: implementation
> is done when every acceptance criterion maps to a scenario in
> `EXAMPLES.feature` and every scenario has a passing check.

## Problem

`Client.numTelClient1` and `numTelClient2` are `models.IntegerField()`. A phone
number is an identifier, not a quantity: integers cannot hold a leading zero
(`0123456789` becomes `123456789`), cannot hold `+` or separators, and the
column silently truncates anything a user types as a formatted number. The
JavaFX client already works around it — `NouveauClientCtrl.parsePhone` coerces
the text field to `int` and `phoneText` renders `0` back as an empty field —
so a number entered with a leading zero is corrupted on save and no caller can
tell "no phone" apart from the number `0`.

## Users

- Gest_Comm_ClientFX operators entering and reading customer phone numbers.
- API consumers that post or read `Client` records.
- The `/api/assistant/ask` search, which currently has to special-case digits
  (`if term.isdigit(): ... int(term)`) to match a phone at all.

## Outcome hypothesis

- Expected user outcome: a phone number entered as text is stored and returned
  exactly as its digits, leading zeros included, and is findable by the digits
  the user remembers.
- Opportunity evidence: verified in code — `models.IntegerField()`
  (`models.py:16-17`), `parsePhone`/`phoneText` in the client, and the
  `term.isdigit()` branch in `assistant.py:_search_clients`.
- Signal: the suite proves round-trip fidelity for leading zeros, separators,
  legacy integer payloads and blank; the deployed dev database keeps every
  existing number after the migration. Baseline today is the opposite: a
  leading zero cannot survive at all.
- Follow-up owner/date: repo owner, at the next client-loop review — phone
  *display* formatting (spacing by country) is deliberately left to the client.

## Scope (in)

- `numTelClient1`/`numTelClient2` become `CharField(max_length=32, blank=True,
  default='')`, with the migration that carries existing rows over.
- Canonical storage: digits only, with an optional single leading `+`;
  separators (space, `.`, `-`, `(`, `)`, `/`) are stripped on write.
- Write-time validation: at most one leading `+`, 4–20 digits, otherwise a
  DRF field error; blank is valid and means "no phone".
- Wire compatibility: a JSON integer or numeric string from an older client is
  accepted and stored as its digits; a payload of `0` (the legacy "empty"
  convention) is stored as `''`.
- `/api/assistant/ask` matches phone searches on the canonical value, so both
  `0612345678` and `06 12 34 56 78` find the client.
- API documentation (`docs/api.md` or the repo's equivalent) updated for the
  changed field type.

## Scope (out)

- Client-side changes — the Gest_Comm_ClientFX `Client` model field types,
  `parsePhone`/`phoneText` and the record forms. Those belong to a follow-up `Gest_Comm_ClientFX` loop; this
  loop must nonetheless accept what today's client sends (see AC-3, AC-4).
- Human-readable *display* formatting (`+33 6 12 34 56 78`) and country
  metadata — formatting is presentation, and a client-side concern.
- Uniqueness or deduplication of phone numbers, phone verification/SMS.
- The other `IntegerField`-as-identifier offenders (none known) and any legacy
  data outside the `client` table.

## Acceptance criteria

| # | Criterion | Scenario(s) |
|---|-----------|-------------|
| 1 | A phone number with a leading zero round-trips through create and list unchanged | Phone numbers keep leading zeros |
| 2 | Formatted input is canonicalised: separators stripped, a single leading `+` kept | Formatted phone numbers are canonicalised |
| 3 | A legacy integer payload is accepted and stored as its digits | Legacy integer phone payloads are accepted |
| 4 | A blank value and the legacy `0` both mean "no phone" and read back as an empty string | Zero and blank mean no phone |
| 5 | Invalid values (letters, two `+`, out-of-range digit counts) are rejected with a field error | Invalid phone numbers are rejected |
| 6 | Existing rows keep their digits after the migration | Existing numbers survive the migration |
| 7 | The assistant finds a client by canonical or formatted phone digits | Assistant finds clients by phone |
| 8 | Both phone fields behave identically | Both phone fields behave identically |

## Decisions

### D1 — Phone storage: text with canonical digits

- **Context & forces:** Integers cannot represent a phone number: leading zeros
  are lost, `+`/separators are impossible, and `0` is indistinguishable from
  "absent". The column is user-facing data that a person retypes or dials.
- **Options considered:**
  1. Keep `IntegerField`, format only on display in the client — smallest
     change, no migration; but it cannot fix the corruption (the zero is
     already gone at write time) and leaves `0` ambiguous. Rejected: the
     defect is in storage, not presentation.
  2. `CharField` storing the text exactly as typed — most forgiving; but
     `06 12 34 56 78`, `0612345678` and `+33 6 12...` then become three
     distinct values, so search and deduplication need fuzzy matching.
  3. `CharField` storing a canonical value (digits, optional leading `+`) —
     one representation per number, searchable with a plain `contains`.
- **Decision & why:** Option 3. Fidelity (leading zeros, `+`) is preserved,
  equality is meaningful, and search stays a simple indexed string match. The
  separator-stripping rule is the only loss, and it is unambiguous.
- **Consequences:** Positive — the API gains a real phone contract and the
  assistant stops special-casing integers. Negative — a client that renders the
  stored value shows `0612345678` rather than `06 12 34 56 78`; display
  formatting becomes a client concern (explicit follow-up). Any external
  consumer doing arithmetic on the old integer field breaks.
- **Reversibility:** Two-way door in schema terms (a `CharField` narrows back to
  `IntegerField` for digit-only values), one-way for data already written with
  leading zeros — an integer downgrade would truncate them. Revisit trigger: a
  need for i18n display or for a dedicated phone model (country, type, label).

### D2 — Wire compatibility with the integer-era client

- **Context & forces:** `Gest_Comm_ClientFX` today posts `int` phone values
  (`parsePhone`) and sends `0` for an empty field (`phoneText` treats `0` as
  blank). Changing the field type must not break the deployed client before the
  client loop lands.
- **Options considered:**
  1. Strict `CharField` — reject anything non-string; clean contract, but the
     deployed client gets a 400 on every customer save. Rejected.
  2. Accept both and let DRF coerce — smallest change; DRF's `CharField`
     already accepts `int`/`float` and stringifies. `0` would still land as
     `"0"`, keeping the ambiguity this feature exists to remove.
  3. Accept both, then normalise `0` → `''` in the serializer — tiny explicit
     rule that encodes the legacy convention in one place.
- **Decision & why:** Option 3. DRF's coercion covers the type, and one
  documented rule (`0` means absent) removes the ambiguity without breaking
  the old client.
- **Consequences:** Positive — no coordinated deploy, and the old client keeps
  working. Negative — a permanent-looking legacy quirk in the serializer that
  must be deleted once the client loop ships; and the literal number `0` can
  never be stored as a phone (acceptable: it is not a valid number).
- **Reversibility:** Two-way door — the rule is three lines in one serializer
  method, deletable when the client sends `""`.

### D3 — Validation strength at the edge

- **Context & forces:** Garbage in the phone column is costly to clean later,
  but over-strict rules reject legitimate international formats and angry
  users. The dev database holds 8-digit numbers (`11111111`).
- **Options considered:**
  1. No validation beyond the column length — simplest, but `"abc"` is stored.
  2. Full E.164 validation — correct for dialling, but rejects local formats
     (`0612345678`) that this app's users actually type. Rejected.
  3. Charset + length rule: optional single leading `+`, 4–20 digits after
     separator stripping. Small, local, and admits local and international
     formats.
- **Decision & why:** Option 3. It rejects the obviously wrong (letters, empty
  digits, double `+`) while accepting both local and `+33…` forms.
- **Consequences:** Positive — dirty data is stopped at write time. Negative —
  an extension suffix (`poste 12`) is rejected; it belongs in a separate field
  if it is ever needed.
- **Reversibility:** Two-way door — the validator is a single function; relaxing
  it needs no migration.
