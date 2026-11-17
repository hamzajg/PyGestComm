# Gates: tls-termination

## G1 — Spec contract recorded
- Before: plan
- Type: artifact
- Owner: agent
- Resolver: agent
- Blocking: yes
- Check: file:specs/tls-termination/SPEC.md
- Why: scope and acceptance criteria must be frozen first.

## G2 — Test suite green
- Before: validate
- Type: quality
- Owner: agent
- Resolver: agent
- Blocking: yes
- Check: command:cd src/GestCommProject && ../../.venv/bin/python manage.py test
- Why: the secure-settings change must not regress the 52-test suite.
