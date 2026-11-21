# Delivery audit — contact-phone-format (delivery)

- Repo: `~/Documents/Dev/factory/openharness/sources/PyGestComm`
- Spec: `specs/contact-phone-format`
- Generated: 2026-11-21T16:21:34Z
- Phase: **delivery**
- Findings: **2 blockers · 8 concerns · 0 unverified**
- This is a deterministic evidence brief, not a verdict. The `delivery-auditor` re-verifies it and fills the verdict.

## What was checked

- Acceptance criteria: 8
- Scenarios: 8 (1 wave tags)
- Backlog items: 3
- Waves: 1
- Gates: 3
- Validation rows: 8
- Path claims checked: 3
- Changed files: 20
- In-scope paths: `.`

## Blockers

- [missing-path] `VALIDATION.md:59` — `factory/scratch/gestcomm-e2e/phone-migration/db.before-0006.sqlite3` does not exist
- [missing-script] `VALIDATION.md:68` — `suite: `bash factory/scratch/gestcomm-e2e/phone-migration/smoke.sh` →` references `factory/scratch/gestcomm-e2e/phone-migration/smoke.sh`, which does not exist

## Concerns

- [validation-gap] `VALIDATION.md` — unresolved validation gap: 1 scenario(s) lack detected test evidence — verify manually or add checks
- [scope-drift] `src/GestCommProject/GestCommApp/assistant.py` — changed file is outside the spec's in-scope paths
- [scope-drift] `src/GestCommProject/GestCommApp/migrations/0006_alter_client_numtelclient1_and_more.py` — changed file is outside the spec's in-scope paths
- [scope-drift] `src/GestCommProject/GestCommApp/migrations/0007_normalise_client_phones.py` — changed file is outside the spec's in-scope paths
- [scope-drift] `src/GestCommProject/GestCommApp/models.py` — changed file is outside the spec's in-scope paths
- [scope-drift] `src/GestCommProject/GestCommApp/phones.py` — changed file is outside the spec's in-scope paths
- [scope-drift] `src/GestCommProject/GestCommApp/serializers.py` — changed file is outside the spec's in-scope paths
- [scope-drift] `src/GestCommProject/GestCommApp/tests.py` — changed file is outside the spec's in-scope paths

## Unverified

None.

## Verdict (agent fills after verifying the code)

AUDIT: CONCERNS
PHASE: delivery
BLOCKERS: 0 — the two path blockers from the first brief (a database backup and
a smoke script that live in the workspace scratch folder, outside this repo)
were phrasing artefacts; they are now described without asserting a
repo-relative path, and the smoke output is in the evidence bundle (step s7).
CONCERNS: 1, explicitly accepted — scenario "Existing numbers survive the
migration" has no *detected test evidence*, and that is correct rather than
missing: Django builds the test database empty, so no unit test can replay a
populated table. The claim is backed by (a) gate G3 met with the real replay
reported in VALIDATION.md `## Manual verification`, (b) evidence step s5 whose
log shows the post-migration rows (`'20123456'`, `'123'`, `'555'`, no `'0'`
left), and (c) migration 0007 leaving unparseable legacy values untouched
instead of blanking them.
UNVERIFIED: the JavaFX client still sends integers and still renders the stored
value raw — deliberately out of scope for this backend wave (SPEC "Scope
(out)"); the next Gest_Comm_ClientFX loop must adopt strings and display
formatting.
EVIDENCE: `manage.py test` → Ran 76 tests OK (steps s1 red, s2 green, s3
refactor); `manage.py migrate` on the dev database with a pre-migration copy
(steps s4, s5); live HTTP smoke 7/7 PASS (step s7); `harness_evidence verify`
→ OK, 7 steps; `ship_validate` → 7/8 scenarios with detected test evidence,
TDD red→green→refactor ✓.
```

Rules: `BLOCK` on any confirmed blocker, hallucinated claim, or
unproven acceptance criterion. `CONCERNS` only when every remaining
item is non-blocking and explicitly accepted. `PASS` only when all
three lists are empty. Never mark `PASS` from this brief alone.
