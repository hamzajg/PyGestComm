# Spec: document-numbering

> Spec-driven development artifact. This file is the contract: implementation
> is done when every acceptance criterion maps to a scenario in
> `EXAMPLES.feature` and every scenario has a passing check.

## Problem

`codeDevis`/`codeFacture`/`codeBonLiv` are required free-text fields — every
caller must invent a code, which invites duplicates and inconsistent
formats ("J-DEV-76038", "F0002", "D001" coexist in dev data). The legacy
template's *Parametre des sequences* menu hints the original app had
sequence management. Documents should get sensible auto-numbers when the
caller doesn't supply one.

## Users

- Gest_Comm_ClientFX users creating documents without thinking about codes.
- API consumers that previously had to fabricate codes.

## Outcome hypothesis

- Expected user outcome: omitting the code on create yields a sequential
  `PREFIX-NNNN` code; supplying one still works unchanged.
- Opportunity evidence: all three document serializers share the same
  create() shape — one helper covers all.
- Signal: tests show blank code → `DEV-0001`/`FAC-0001`/`BL-0001`,
  increments per type, explicit codes preserved.
- Follow-up owner/date: repo owner; revisit if multi-branch numbering or
  per-year reset is ever needed.

## Scope (in)

- `blank=True` on the three code fields + migration.
- `_next_document_code()` helper: max trailing-number suffix among codes
  with the type prefix, +1, zero-padded to 4 digits.
- Prefixes: devis `DEV-`, facture `FAC-`, bonliv `BL-`.
- Generation on **create only**, when the code is missing or blank;
  explicit codes always win.
- Client dialogs: allow blank code (auto-number hint) in the three
  document forms.

## Scope (out)

- DB-level `unique=True` on codes — existing dev data may contain
  duplicates; uniqueness is a separate policy decision.
- Gapless sequences / per-year resets / configurable prefixes
  (*Parametre des sequences* UI) — documented follow-up.
- Concurrency-safe allocation (acceptable at SQLite/LAN scale;
  `select_for_update` noted if a real DB arrives).

## Acceptance criteria

| # | Criterion | Scenario(s) |
|---|-----------|-------------|
| 1 | Creating a document without a code assigns the next sequential code for its type | Auto-number on create |
| 2 | Explicit codes are preserved verbatim, including non-standard formats | Explicit codes win |
| 3 | Numbering is per-type and increments independently | Sequences are per type |

## Decisions

- Generate in the serializer `create()`, not the model — keeps numbering a
  presentation/API concern and leaves `objects.create` usable in tests.
- Parse the **max trailing digit run** after the prefix rather than counting
  rows — survives deletions without reuse.
- 4-digit zero-padding; grows naturally past 9999.
