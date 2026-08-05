

# Teaching Guide: DDD + Ontology with this codebase

This guide is for walking a class through this repo live. It assumes students can read Python
and JavaScript but have never built a DDD system or an RDF ontology. Total runtime: roughly a
half-day workshop (4-5 hours) split into modules, or spread across 2-3 shorter sessions.

Companion reading: `README.md` (quick overview), `CLAUDE.md` (architecture reference).

---

## 0. Setup (do this before class starts)

```bash
# Terminal 1 — backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Verify before students arrive:
- http://localhost:8000/docs — Swagger UI loads, shows all routes
- http://localhost:8000/api/health — returns `{"status": "ok"}`
- http://localhost:5173 — React app loads, Catalog tab shows 6 products

Keep three things open the whole session: the Swagger UI tab, the React app tab, and an editor
on the repo. You will bounce between "read the code" → "call the endpoint" → "see it in the UI"
constantly — that loop is the whole teaching method here.

---

## 1. Frame the problem (10 min, no code yet)

Ask the class: *"If I hand you a retail system, what are the two totally different questions
someone could ask about it?"* Steer toward:

1. **"What happens when a customer buys something?"** — behavior, rules, transactions.
2. **"What IS a Product, and how does it relate to a Category?"** — meaning, vocabulary,
   relationships.

Write both questions on the board. Tell them: question 1 is what **DDD** (Domain-Driven Design)
answers. Question 2 is what an **ontology** answers. Most systems only ever answer question 1 —
this repo deliberately builds both, side by side, over the *same* six concepts, so the contrast
is visible.

The six concepts (write on board): `Category → Product → InventoryItem`, and
`Customer → Order → OrderLine → Product`.

---

## 2. Module A — DDD building blocks (60-75 min)

Teach bottom-up: the smallest building block first, then compose upward. This mirrors the
suggested reading order in the README.

### A.1 Value Objects — `backend/app/domain/value_objects.py`

Open the file. Key teaching points on `Money`:
- `@dataclass(frozen=True)` → immutable. Ask: *"why would money need to be immutable?"*
  (Answer: so nobody can silently mutate a price that's shared/referenced elsewhere.)
- No `id` field. Two `Money(10, "USD")` are equal by *value*, not identity — that's the
  definition of a Value Object.
- `__post_init__` validates on construction (`amount < 0` raises). This is the "illegal states
  unrepresentable" idea: you cannot construct a broken `Money`.
- `SKU` and `Email` are the same pattern with regex validation — show `SKU.__post_init__`'s
  regex and ask what SKU strings would fail it (e.g. `"abc-1"` — lowercase, too few digits).

**Live demo:** open a Python REPL (`python3` inside the venv) and try:
```python
from app.domain.value_objects import Money
Money(10, "USD") == Money(10, "USD")   # True — value equality
Money(-5, "USD")                        # raises ValueError
```

### A.2 Entities — `backend/app/domain/entities.py`

Contrast with Value Objects: `Product` has an `id`. Two products named identically but with
different ids are different products — identity, not value, defines equality here.

- `Category.parent_id` — point out this is the field that will become the ontology's `isA`
  hierarchy later. Plant the seed now, pay it off in Module B.
- `InventoryItem` — this is the meatiest one. Walk through `quantity_available` (computed
  property: on_hand − reserved), then `reserve()` and its guard (`ValueError` if
  over-reserving), then `fulfill()`. Ask: *"why track `reserved` separately from `on_hand`
  instead of just decrementing on_hand immediately?"* → this is the classic "avoid overselling
  without locking rows" pattern; reserved stock is a soft hold during checkout.

### A.3 Aggregates — `backend/app/domain/aggregates.py`

Define **aggregate**: a cluster of objects treated as a single consistency boundary, entered
only through its root. Here, `Order` is the root; `OrderLine` cannot be created or modified
except through `Order.add_line()`.

- Show `add_line()`'s guard: can't add lines once status leaves `DRAFT`. This is an invariant
  enforced *inside* the domain object, not in the API layer.
- Show `place()`: requires at least one line, flips status, stamps `placed_at`. Ask: *"what
  happens if I call `place()` twice?"* → raises, second call finds status already `PLACED`.
- `_events` / `pull_events()` / `record_event()` — flag but don't dwell; full payoff comes in
  A.5.

**Exercise (5 min, pairs):** Have students try to write a test/script that constructs an `Order`
and calls `.place()` on it with zero lines, and confirm they get a `ValueError`. This makes the
"invariants live in the domain" idea concrete before moving on.

### A.4 Domain Services — `backend/app/domain/services.py`

Explain: some logic doesn't belong to one entity because it coordinates across several.
`InventoryService.check_and_reserve` doesn't live on `InventoryItem` because it also needs the
repository to look the item up and persist the reservation — coordination, not a single
object's own behavior.

- Note it returns domain **events** (`StockReserved` / `StockInsufficient`) rather than raising
  or returning booleans — show `backend/app/domain/events.py` here. Explain: events are named
  past-tense facts ("this happened"), and returning them lets the caller decide what to do
  (raise an HTTP error, log, notify) without the domain service knowing about HTTP or logging.
- `PricingService` is intentionally trivial (a bulk-discount threshold) — mention it's a second
  example of the same "logic that doesn't belong to one entity" pattern, kept simple on purpose.

### A.5 Repositories (ports) — `backend/app/domain/repositories.py`

This is the **most important architectural idea** in the whole codebase — spend real time here.

- These are abstract classes (`ABC` + `@abstractmethod`) with zero implementation. The domain
  layer declares *what* persistence it needs, never *how*.
- Ask: *"why would a domain layer want to be ignorant of whether data is stored in a dict, a
  Postgres table, or a REST API?"* → testability (swap in fakes), and so business logic doesn't
  rot when infrastructure changes.
- Now open `backend/app/infrastructure/memory_repositories.py` side by side. Show
  `InMemoryProductRepository` implementing `ProductRepository` with a plain dict. State the
  punchline explicitly: *"if we wanted Postgres tomorrow, we'd write a new
  `SqlProductRepository` implementing this exact interface. Nothing in `domain/` or
  `application/` would change — not one line."* This is the Ports & Adapters (Hexagonal
  Architecture) pattern; repositories are the ports, `memory_repositories.py` is the adapter.

### A.6 Application Services (use cases) — `backend/app/application/`

Read `catalog_service.py` first (short, simple): it just fetches from repositories and shapes
dicts for the API. State the rule: **application services contain no business rules** — those
already live in the domain layer. Application services only orchestrate.

Then read `order_service.py` — this is the payoff of everything in Module A. Walk
`place_order()` top to bottom and narrate each step against what students already learned:
1. Validate customer exists, line items non-empty (application-level guard).
2. Construct an `Order` aggregate (A.3).
3. For each line, call `InventoryService.check_and_reserve` (A.4) — collect any
   `StockInsufficient` events.
4. If any insufficient, raise `OrderPlacementError` with details — **note**: stock was already
   reserved for the lines that succeeded before hitting an insufficient one; this is a known
   simplification worth naming as a discussion point (see §6).
5. If all OK, build `OrderLine`s from `Product` + requested quantity, call `order.add_line()`
   (A.3's invariant guard fires here if misused).
6. `order.place()` (A.3) — flips status, enforces "at least one line."
7. Record an `OrderPlaced` event (A.4/A.5's event pattern), save via `OrderRepository` (A.5's
   port), return a plain dict.

Ask the class to trace, without looking, which layer each of these lives in: Value Object,
Entity, Aggregate, Domain Service, Repository, Application Service. This is the checkpoint that
confirms Module A landed.

### A.7 The HTTP layer — `backend/app/main.py`

Quick pass only — the point here is how *thin* it is. Show the composition root (lines ~32-36:
repos → domain services → application services, wired once at startup). Show `place_order()`
route: it just calls `order_service.place_order()` and translates `OrderPlacementError` into an
HTTP 400. No business logic in this file — reinforce that's a rule, not an accident.

**Live demo — trigger it for real:**
```bash
# Successful order
curl -s -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"cust-001","line_items":[{"product_id":"prod-003","quantity":2}]}' | python3 -m json.tool

# Insufficient stock — prod-006 (Espresso Machine) only has 4 on hand
curl -s -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"cust-001","line_items":[{"product_id":"prod-006","quantity":999}]}' | python3 -m json.tool
```
Have students predict the JSON shape *before* running each command, using only what they read
in `order_service.py`. Then switch to the React app's Cart & Checkout tab and place a real order
through the UI — same code path, now visible end to end.

---

## 3. Module B — The ontology (60-75 min)

### B.1 Why a second model at all (5 min)

Revisit the board from §1. DDD answered "how does it behave." Now: "what do these concepts
*mean*, and how do they relate?" Motivating question: *"Show me every product in Electronics —
including Laptops and Computers, which are subcategories of Electronics."* This is a recursive
"is-a" question. Ask how they'd write that in SQL against a `categories` table with a
`parent_id` column (recursive CTE — doable but awkward). Ontologies make this kind of question a
first-class, declarative query.

### B.2 RDF basics (10 min, no code yet)

Explain the triple: **subject – predicate – object**. e.g. `Product/prod-001` –
`belongsToCategory` – `Category/cat-laptops`. A graph is just a set of triples. Introduce:
- **Class** — a category of thing (`Product`, `Category`, `Order`...)
- **Object property** — a relationship between two individuals (`belongsToCategory`)
- **Data property** — a relationship from an individual to a literal value (`hasPrice`)
- **TBox vs ABox** — TBox = the *schema* (classes + properties, no data). ABox = the *instance
  data* (actual products, actual orders). Same distinction as a SQL schema vs. its rows, but
  the schema itself is queryable RDF too.

### B.3 The schema (TBox) — `backend/app/ontology/schema.py`

Walk `build_schema_graph()` top to bottom:
- Six classes declared as `OWL.Class` with `rdfs:label`/`rdfs:comment` (lines ~31-44).
- `subCategoryOf` — point out the comment explaining this is deliberately an *instance-level*
  property (Category individuals point at their parent Category individual), not `rdfs:subClassOf`
  — a simplification made explicitly to keep the teaching model easy to follow. Tie back to
  `Category.parent_id` from A.2 — same fact, expressed as a Value/Entity field there, and as an
  RDF triple here.
- Object properties (line ~55-67): each has a domain and range, same as a type signature —
  `belongsToCategory: Product → Category`.
- Data properties (line ~70-85): literal-valued, typed with XSD (`XSD.string`, `XSD.decimal`,
  `XSD.integer`).

**Live demo:**
```bash
curl -s http://localhost:8000/api/ontology/schema | python3 -m json.tool | head -40
```
Then open the Turtle serialization from that same response (`.turtle` field) — show students
what RDF actually looks like as text, so the graph API response doesn't feel like a black box.

### B.4 The live knowledge graph (ABox) — `backend/app/ontology/knowledge_graph.py`

Walk `build_instance_graph()`: it starts from `build_schema_graph()` (TBox) and adds triples for
every live `Category`, `Product`, `InventoryItem`, `Customer`, `Order`, `OrderLine` currently in
the repositories. Emphasize: **this function runs fresh on every API call** — it is not
persisted RDF, it's generated from the same in-memory dicts A.5 introduced. Same data, two
views.

Point at one instance minting line, e.g. `RETAIL[f"Product/{p.id}"]`, and connect it to the
Product entity id from A.2 — literally the same `id` string, just wrapped into a URI.

### B.5 SPARQL query — `products_in_category_tree()`

This is the payoff of B.1's motivating question. Read the SPARQL block:
```sparql
?cat retail:subCategoryOf* <...Category/cat-electronics> .
```
The `*` is a property-path operator: "zero or more hops of `subCategoryOf`." Explain this
answers "in this category OR any descendant" in one line — the recursive-CTE problem from B.1,
solved declaratively.

**Live demo:**
```bash
curl -s http://localhost:8000/api/ontology/query/products-in-category/cat-electronics | python3 -m json.tool
```
Should return laptops (`cat-laptops`, two hops down) and audio products (`cat-audio`, one hop
down) — not just direct children. Then try `cat-laptops` directly (should return just the two
laptops) and `cat-kitchen` (should return the appliances). Ask students to predict results
before each call.

### B.6 Graph → visualization JSON — `graph_to_vis_json()`

Briefly explain the `scope="schema"` vs `scope="instances"` split and why schema mode reads from
the plain Python lists (`SCHEMA_CLASSES`/`SCHEMA_RELATIONSHIPS`) instead of the RDF triples —
`rdfs:domain`/`rdfs:range` triples describe a *property*, not a class-to-class edge, so
reverse-engineering the visual graph from them would be awkward. Instances mode walks real
triples and filters out schema-only predicates (`type`, `label`, `comment`, `domain`, `range`).

**Live demo:** switch to the React app's Ontology tab. Toggle between schema and instance views
if the UI supports it (check `OntologyView.jsx`) and let students click around the graph. Place
another order in the Checkout tab, then flip back to the Ontology tab — new `Order` and
`OrderLine` nodes should appear, proving the ABox is rebuilt live.

---

## 4. Module C — Tie it together (15-20 min)

Put both diagrams on the board / screen side by side:

```
DDD (behavior)                    Ontology (meaning)
───────────────                   ──────────────────
Category (parent_id)     ←──same fact, two forms──→   Category --subCategoryOf--> Category
Product                                                Product --belongsToCategory--> Category
InventoryItem                                          Product --hasInventory--> InventoryItem
Customer, Order, OrderLine                             Customer <--placedBy-- Order --contains--> OrderLine --forProduct--> Product
```

Ask: *"If I add a new bounded context — say, Returns/Refunds — what has to change in each
model?"* Guide toward: DDD gets a new aggregate + repository + application service, following
the exact pattern from Module A. The ontology gets a new class + a couple of object/data
properties, following the exact pattern from Module B. Neither model needs to touch the other's
files — they're deliberately decoupled, generated from (or referencing) the same underlying
entity ids.

Close with the swap-in-a-database point from `README.md`/`CLAUDE.md`: because repositories are
ports (A.5), replacing in-memory dicts with Postgres touches only `infrastructure/` — everything
taught in Module A and B stays true regardless of storage engine.

---

## 5. Suggested exercises (assign after class, or as a lab)

Ordered easy → hard:

1. **Add a Money currency.** Add `"GBP"` to `Money.__post_init__`'s allowed currencies
   (`value_objects.py`). Confirm via a new product seeded in `seed_data.py` with `Money(x,
   "GBP")` that it round-trips through `/api/products`.
2. **Add an invariant.** In `aggregates.py`, make `Order.add_line()` reject a line whose
   `quantity <= 0`. Write a quick script/REPL check that it raises.
3. **Add a domain event.** Add an `OrderCancelled` event to `events.py`, and a
   `cancel()` method on `Order` in `aggregates.py` that only works from `PLACED` (not `DRAFT` or
   already `CANCELLED`), records the event, and sets status. No API route required — this
   exercise is about the domain layer only.
4. **Extend the ontology.** Add a `Brand` class to `schema.py` (with a `label`/`comment`), a
   `hasBrand: Product → Brand` object property, and mint `Brand` individuals + `hasBrand` triples
   in `knowledge_graph.py`'s `build_instance_graph()`. Products don't currently have a brand
   field in the domain model — students must decide: fake it with a lookup table in the ontology
   layer, or add `brand` to the `Product` entity first? Good discussion prompt either way.
5. **Write a new SPARQL query.** In `knowledge_graph.py`, write a function
   `low_stock_products(g, threshold)` that returns all products whose `hasQuantityAvailable` is
   below `threshold`. Wire a new route in `main.py` to expose it.
6. **New repository implementation.** Write a `JsonFileProductRepository` implementing
   `ProductRepository` (from `domain/repositories.py`) that persists to a local JSON file instead
   of a dict. Swap it into the composition root in `main.py` and confirm nothing in `domain/` or
   `application/` needed to change — this is the exercise that proves the Ports & Adapters claim
   from A.5, rather than just asserting it.

---

## 6. Discussion points / known simplifications (use to spark debate, not as "bugs" to fix)

- **Partial reservation on multi-line failure.** In `order_service.place_order()`, if line 1
  reserves successfully and line 2 fails on insufficient stock, line 1's reservation is never
  released — the whole request raises `OrderPlacementError` but stock stays reserved. Ask
  students: *"how would you fix this?"* (Answers: compensating release loop, or a two-phase
  check-then-commit pass, or a `try/finally`.) Good segue into transactions/sagas if the class is
  ready for it.
- **No persistence.** Storage resets on every backend restart. Ask what they'd need to add for
  durability, and how little of `domain/`/`application/` it would touch (ties to Exercise 6).
  Whether the `_events` list on `Order` (A.3) is actually consumed anywhere yet — check
  `main.py` — if not, that's an honest gap to name: events are recorded but nothing subscribes
  to them yet. Good prompt for "what would an event *handler* look like?"
- **Ontology has no reasoner.** This demo queries the graph with SPARQL but never runs OWL
  inference (e.g. auto-deriving that a Laptop is-a Electronics via transitive closure beyond what
  `subCategoryOf*` already gives you in the query itself). Worth mentioning reasoners
  (e.g. `owlrl`) exist for classes that want to go further.

---

## 7. Quick command reference (cheat sheet to project on screen during live demos)

```bash
# Health check
curl -s http://localhost:8000/api/health

# Catalog
curl -s http://localhost:8000/api/products | python3 -m json.tool
curl -s http://localhost:8000/api/categories | python3 -m json.tool

# Place an order (success case)
curl -s -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"cust-001","line_items":[{"product_id":"prod-003","quantity":2}]}'

# Place an order (insufficient stock — triggers OrderPlacementError)
curl -s -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"cust-001","line_items":[{"product_id":"prod-006","quantity":999}]}'

# Ontology TBox (schema) + Turtle serialization
curl -s http://localhost:8000/api/ontology/schema | python3 -m json.tool

# Ontology ABox (live instance graph)
curl -s http://localhost:8000/api/ontology/graph | python3 -m json.tool

# SPARQL property-path query: products in a category tree
curl -s http://localhost:8000/api/ontology/query/products-in-category/cat-electronics
curl -s http://localhost:8000/api/ontology/query/products-in-category/cat-laptops
curl -s http://localhost:8000/api/ontology/query/products-in-category/cat-kitchen
```

Product/category ids to keep handy while demoing (`backend/app/infrastructure/seed_data.py`):

| id | name | category | stock |
|---|---|---|---|
| prod-001 | 14-inch Ultrabook | cat-laptops | 12 |
| prod-002 | 15-inch Creator Laptop | cat-laptops | 5 |
| prod-003 | Wireless Noise-Cancelling Headphones | cat-audio | 40 |
| prod-004 | Bluetooth Speaker | cat-audio | 60 |
| prod-005 | Stand Mixer | cat-appliances | 8 |
| prod-006 | Espresso Machine | cat-appliances | 4 (good "insufficient stock" demo item) |

Category tree: `cat-electronics` → `cat-computers` → `cat-laptops`; `cat-electronics` →
`cat-audio`; `cat-kitchen` → `cat-appliances`.

Customer id: `cust-001` (Sandeep R).
