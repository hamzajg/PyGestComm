# Gates: contact-phone-format

## G1 — Design decisions challenged
- Before: plan
- Type: artifact
- Owner: agent
- Resolver: agent
- Blocking: yes
- Check: file:specs/contact-phone-format/DECISION-REVIEW.md
- Why: The storage type, the canonical representation and the integer-era wire
  compatibility are inherited by every wave; the challenger review must exist
  before wave planning locks them in.

## G2 — Test suite green including the client contract
- Before: validate
- Type: quality
- Owner: agent
- Resolver: agent
- Blocking: yes
- Check: command:cd src/GestCommProject && ../../.venv/bin/python manage.py test
- Why: a field-type change plus migration must not regress the 69-test suite or
  the endpoints the JavaFX client already calls.

## G3 — Migration replayed on a copy of the dev database
- Before: finish
- Type: data
- Owner: agent
- Resolver: agent
- Blocking: yes
- Check: manual
- Why: forward migrations that change a column type are the one step tests
  cannot prove on synthetic data; replay it against a copy of `db.sqlite3` and
  record what the rows became.
