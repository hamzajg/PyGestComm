# Gates: document-numbering

## G1 — Spec contract recorded
- Before: plan
- Type: artifact
- Owner: agent
- Resolver: agent
- Blocking: yes
- Check: file:specs/document-numbering/SPEC.md
- Why: numbering policy (prefixes, create-only, no uniqueness) must be frozen.

## G2 — Test suite green
- Before: validate
- Type: quality
- Owner: agent
- Resolver: agent
- Blocking: yes
- Check: command:cd src/GestCommProject && ../../.venv/bin/python manage.py test
- Why: migration + serializer change must not regress the suite.
