"""
API Layer (FastAPI)
=====================
Thin HTTP adapter: translates requests into application-service calls and
domain objects into JSON. Contains no business logic itself.

Run:  uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .infrastructure.seed_data import seed
from .infrastructure.json_file_repository import JsonFileProductRepository
from .application.catalog_service import CatalogService
from .application.order_service import OrderService, OrderPlacementError
from .domain.services import InventoryService
from .domain.value_objects import Email
from .domain.entities import Customer
from .ontology.schema import build_schema_graph
from .ontology.knowledge_graph import build_instance_graph, graph_to_vis_json, products_in_category_tree, low_stock_products

app = FastAPI(title="Retail DDD + Ontology Demo", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Composition root: wire repositories -> domain services -> application services ---
repos = seed()

# Exercise 6: swap the product repository's storage engine. Domain and
# application code only ever depend on ProductRepository (the abstract
# port) -- catalog_service/order_service below don't change at all.
json_products = JsonFileProductRepository("data/products.json")
for p in repos["products"].list_all():
    json_products.save(p)
repos["products"] = json_products

inventory_service = InventoryService(repos["inventory"])
catalog_service = CatalogService(repos["products"], repos["categories"], repos["inventory"])
order_service = OrderService(repos["products"], repos["orders"], repos["customers"], inventory_service)


# ----------------------------- Schemas (API DTOs) -----------------------------
class LineItemIn(BaseModel):
    product_id: str
    quantity: int


class PlaceOrderIn(BaseModel):
    customer_id: str
    line_items: list[LineItemIn]


class CustomerIn(BaseModel):
    name: str
    email: str


# ----------------------------- Catalog -----------------------------
@app.get("/api/products")
def list_products():
    return catalog_service.list_products()


@app.get("/api/categories")
def list_categories():
    return catalog_service.category_tree()


# ----------------------------- Customers -----------------------------
@app.get("/api/customers")
def list_customers():
    return [
        {"id": c.id, "name": c.name, "email": str(c.email)}
        for c in repos["customers"].list_all()
    ]


@app.post("/api/customers")
def create_customer(payload: CustomerIn):
    import uuid
    try:
        customer = Customer(id=f"cust-{uuid.uuid4().hex[:6]}", name=payload.name, email=Email(payload.email))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    repos["customers"].save(customer)
    return {"id": customer.id, "name": customer.name, "email": str(customer.email)}


# ----------------------------- Orders -----------------------------
@app.post("/api/orders")
def place_order(payload: PlaceOrderIn):
    try:
        result = order_service.place_order(
            payload.customer_id, [li.model_dump() for li in payload.line_items]
        )
        return result
    except OrderPlacementError as e:
        raise HTTPException(status_code=400, detail={"message": str(e), "items": e.details})


@app.get("/api/orders")
def list_orders():
    return order_service.list_orders()


@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    order = order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# ----------------------------- Ontology -----------------------------
@app.get("/api/ontology/schema")
def ontology_schema():
    """Returns the TBox (classes + relationships) as {nodes, edges} for viz,
    plus the raw Turtle serialization for people who want the RDF itself."""
    g = build_schema_graph()
    vis = graph_to_vis_json(g, scope="schema")
    return {**vis, "turtle": g.serialize(format="turtle")}


@app.get("/api/ontology/graph")
def ontology_instance_graph():
    """Returns the ABox: the live knowledge graph built from current
    repository state, as {nodes, edges} for the React viewer."""
    g = build_instance_graph(
        repos["products"], repos["categories"], repos["customers"],
        repos["inventory"], repos["orders"],
    )
    return graph_to_vis_json(g, scope="instances")


@app.get("/api/ontology/query/products-in-category/{category_id}")
def ontology_query_products_in_category(category_id: str):
    """Example SPARQL query using the subCategoryOf* property path: finds
    all products in a category OR any of its descendant subcategories.
    Try category_id='cat-electronics' to see it walk down into Laptops/Audio."""
    g = build_instance_graph(
        repos["products"], repos["categories"], repos["customers"],
        repos["inventory"], repos["orders"],
    )
    return products_in_category_tree(g, category_id)


@app.get("/api/ontology/query/low-stock/{threshold}")
def ontology_query_low_stock(threshold: int):
    """Example plain-FILTER SPARQL query: products whose available stock is
    below `threshold`. Try threshold=10 to catch the Espresso Machine (4)
    and Creator Laptop (5)."""
    g = build_instance_graph(
        repos["products"], repos["categories"], repos["customers"],
        repos["inventory"], repos["orders"],
    )
    return low_stock_products(g, threshold)


@app.get("/api/health")
def health():
    return {"status": "ok"}
