# Waves — tls-termination

Each wave IS an iteration: a time-boxed, independently shippable
increment — one branch, one PR, green tests, demoable outcome.
Do not start wave N+1 until wave N merges.

## Wave 1 — iteration 1

Scenarios proven by this wave:
- Secure mode settings apply
- Deployment is documented
- Dev mode unchanged

| Item | Title | Size | Deps | Notes |
|------|-------|------|------|-------|
| US1 | As an operator, I want a documented TLS deployment path, so that JWT bearer tokens never cross the wire in cleartext | M | — | env-driven secure settings + deploy/Caddyfile + docs/DEPLOYMENT.md; opt-in flag keeps dev/test unchanged. |
