# Retail // DDD + Ontology Demo

A small, deliberately simple end-to-end retail app built to *teach*, not to
scale: it pairs a **Domain-Driven Design** backend with a parallel
**ontology** (RDF/OWL via rdflib) that describes the same retail world in
terms of classes and relationships. React frontend, Python (FastAPI)
backend, everything runs on your machine — no database, no external
services, no API keys.

```
retail-ddd-ontology/
├── backend/            FastAPI + DDD domain model + ontology
│   └── app/
│       ├── domain/         Entities, Value Objects, Aggregates, Repos (interfaces), Domain Services
│       ├── application/    Application services (use cases): CatalogService, OrderService
│       ├── infrastructure/ In-memory repository implementations + seed data
│       ├── ontology/       RDF/OWL schema (TBox) + live knowledge graph (ABox) + SPARQL
│       └── main.py         FastAPI routes (thin HTTP adapter)
└── frontend/           React (Vite) UI: Catalog, Cart/Checkout, Orders, Ontology viewer
```

## Why both DDD *and* an ontology?

They answer different questions about the same domain:

- **DDD** (`domain/`, `application/`) answers *"how does the software
  behave?"* — invariants, transactions, use cases. E.g. "an Order can't be
  placed with zero lines," "stock is reserved before a sale confirms."
- **Ontology** (`ontology/`) answers *"what do these concepts mean and how
  do they relate?"* — a shared, machine-readable vocabulary (classes,
  properties, an is-a hierarchy for categories) that can be queried with
  SPARQL. It's what lets you ask "which products are in Electronics *or any
  of its subcategories*" as a single declarative query, and it's the same
  kind of layer used in real semantic-search / knowledge-graph systems.

Both are generated from the same underlying data — the ontology's "live
data" view is built on the fly from whatever is currently in the
repositories.

## Run it

You need Python 3.10+ and Node.js 18+.

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend is now at http://localhost:8000 — try http://localhost:8000/docs
for the interactive Swagger UI (FastAPI generates this automatically).

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend is now at http://localhost:5173 and talks to the backend at
`http://localhost:8000` (see `frontend/src/api.js`).

## Where to look first

| If you want to understand&hellip; | Start at |
|---|---|
| The DDD building blocks | `backend/app/domain/` (read `value_objects.py` → `entities.py` → `aggregates.py`) |
| How a use case is orchestrated | `backend/app/application/order_service.py` |
| The ontology schema | `backend/app/ontology/schema.py` |
| How live data becomes RDF | `backend/app/ontology/knowledge_graph.py` |
| The HTTP surface | `backend/app/main.py` |
| The UI | `frontend/src/App.jsx`, then `frontend/src/components/` |

## Data model (kept intentionally small)

`Category` (hierarchical) → `Product` → `InventoryItem`, and
`Customer` → `Order` → `OrderLine` → `Product`. Six concepts total, seeded
with 6 categories, 6 products, and 1 customer in
`backend/app/infrastructure/seed_data.py`.

## Notes

- Storage is in-memory (Python dicts) and resets whenever the backend
  restarts — there's no database to install. Swapping in Postgres/SQLAlchemy
  only requires new classes in `infrastructure/` that implement the same
  repository interfaces from `domain/repositories.py`; nothing in
  `domain/` or `application/` would need to change.
- The ontology is rebuilt from live repository state on every request to
  `/api/ontology/graph`, so it always reflects the orders/stock you've
  actually created in this session.
