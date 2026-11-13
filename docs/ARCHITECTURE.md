# Architecture — PyGestComm

Current-state map. Descriptive, not aspirational; see `docs/adr/` for why.

## System shape

```
Gest_Comm_ClientFX (desktop client, sibling repo)
        │  HTTP/JSON
        ▼
Django 5.2 + DRF 3.16 (runserver / WSGI)
  ├─ GestCommProject/urls.py   routes: /api/client, /admin/
  └─ GestCommApp/
       ├─ models.py        Client (db_table="client")
       ├─ serializers.py   ClientSerializer (fields='__all__')
       └─ views.py         ClientList — ListCreateAPIView
        │
        ▼
sqlite3 (src/GestCommProject/db.sqlite3)
```

## Domain

`GestCommApp` models a small-business back office: clients, articles,
quotes, invoices. **Only `Client` is implemented** — the README is explicit
that the API covers a single client endpoint and the model has no
update/delete route yet. The other domain nouns (articles, quotes,
invoices) exist in intent, not yet in code.

## Layers

Standard Django MVT/DRF: URLconf → generic class-based view → serializer →
model → SQLite. There is no service layer — business logic, when it
appears, should follow the same thin pattern unless it genuinely grows.

## Data

- Single table `client` (`GestCommApp_client` mapped via `db_table`).
- Field naming is legacy/French-domain (`codeClient`, `nomPrenomClient`,
  `matFiscalClient`, `numTelClient*`) — preserved deliberately for
  compatibility with the desktop client's expectations.
- `unique_together = (idClient, codeClient)`, default ordering by
  `codeClient`.

## Contract with the client

`Gest_Comm_ClientFX` consumes `/api/client` (GET list, POST create) with
the field set above. Any field rename, type change, or route change is a
**breaking contract change** requiring coordination across both repos —
record it as an ADR and update both AGENTS.md files.
