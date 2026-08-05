# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Small, deliberately simple teaching app, not production system. Pairs a **DDD** backend
(entities, aggregates, use cases) with a parallel **ontology** (RDF/OWL via rdflib) describing
the same retail domain. Both views are generated from the same in-memory data. No database,
no external services, no API keys. Optimize for clarity over scale/perf when editing.

## Commands

Backend (from `backend/`):
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Swagger UI at http://localhost:8000/docs. No test suite / linter configured.

Frontend (from `frontend/`):
```bash
npm install
npm run dev      # http://localhost:5173, talks to backend at :8000 (see src/api.js)
npm run build
npm run preview
```

## Architecture

```
backend/app/
  domain/         Entities, Value Objects, Aggregates, Repository interfaces (ports), Domain Services
  application/     Use-case orchestration: CatalogService, OrderService
  infrastructure/  In-memory repository implementations (dicts) + seed_data.py
  ontology/        RDF/OWL schema (TBox) + live knowledge-graph builder (ABox) + SPARQL-ish queries
  main.py          FastAPI routes — thin HTTP adapter, no business logic
frontend/src/
  App.jsx, components/   Catalog, Cart/Checkout, Orders, Ontology viewer
  api.js                  all backend calls
```

Data model (six concepts, seeded in `infrastructure/seed_data.py`):
`Category` (hierarchical) → `Product` → `InventoryItem`; `Customer` → `Order` → `OrderLine` → `Product`.

**Read order for the DDD side:** `domain/value_objects.py` → `entities.py` → `aggregates.py` →
`application/order_service.py`.

**Read order for the ontology side:** `ontology/schema.py` (TBox/schema) →
`ontology/knowledge_graph.py` (builds ABox from live repo state on every request).

### Why two parallel models

- **DDD** (`domain/`, `application/`) answers *how does the software behave* — invariants,
  transactions, use cases (e.g. stock reserved before a sale confirms; an Order can't have
  zero lines).
- **Ontology** (`ontology/`) answers *what do these concepts mean and how do they relate* —
  a queryable RDF vocabulary (classes/properties/is-a hierarchy) enabling declarative queries
  like "products in Electronics or any subcategory" (`products_in_category_tree` in
  `main.py`, using the `subCategoryOf*` property path).

### Key architectural rule

`domain/` and `application/` must stay persistence-agnostic. Repository interfaces live in
`domain/repositories.py`; `infrastructure/memory_repositories.py` is the only in-memory-specific
piece. A SQL backend would only add new classes in `infrastructure/` implementing those same
interfaces — never touch `domain/` or `application/` for that.

`main.py` is a thin adapter: routes translate HTTP <-> application-service calls. Business logic
does not belong in `main.py`.

The ontology's `/api/ontology/graph` endpoint rebuilds the ABox from live repository state on
every call — it always reflects whatever orders/stock exist in the current server session
(state resets on backend restart since storage is in-memory).
