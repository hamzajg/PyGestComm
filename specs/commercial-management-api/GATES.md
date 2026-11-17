# Gates: commercial-management-api

## G1 — Spec contract recorded
- Before: plan
- Type: artifact
- Owner: agent
- Resolver: agent
- Blocking: yes
- Check: file:specs/commercial-management-api/SPEC.md
- Why: the delivered contract must be frozen before the loop records it.

## G2 — Test suite green
- Before: validate
- Type: quality
- Owner: agent
- Resolver: agent
- Blocking: yes
- Check: command:cd src/GestCommProject && ../../.venv/bin/python manage.py test
- Why: validation requires mechanical evidence, not claims.
