"""
Knowledge Graph (ABox)
========================
Turns live domain objects (from the repositories) into RDF individuals
that instantiate the schema (TBox) defined in schema.py, and offers a
couple of canned SPARQL queries as a teaching example of why an ontology
is useful: it lets you ask questions that cut across bounded contexts
(e.g. "which categories, including subcategories, does this order touch?")
without the application code needing bespoke joins for each question.
"""
from __future__ import annotations
from rdflib import Graph, Literal, RDF, RDFS
from rdflib.namespace import XSD

from .schema import RETAIL, build_schema_graph, SCHEMA_CLASSES, SCHEMA_RELATIONSHIPS
from ..domain.repositories import ProductRepository, CategoryRepository, CustomerRepository, InventoryRepository
from ..domain.repositories import OrderRepository


def build_instance_graph(
    products: ProductRepository,
    categories: CategoryRepository,
    customers: CustomerRepository,
    inventory: InventoryRepository,
    orders: OrderRepository,
) -> Graph:
    g = build_schema_graph()

    for cat in categories.list_all():
        node = RETAIL[f"Category/{cat.id}"]
        g.add((node, RDF.type, RETAIL.Category))
        g.add((node, RDFS.label, Literal(cat.name)))
        if cat.parent_id:
            g.add((node, RETAIL.subCategoryOf, RETAIL[f"Category/{cat.parent_id}"]))

    for p in products.list_all():
        node = RETAIL[f"Product/{p.id}"]
        g.add((node, RDF.type, RETAIL.Product))
        g.add((node, RDFS.label, Literal(p.name)))
        g.add((node, RETAIL.hasSKU, Literal(str(p.sku), datatype=XSD.string)))
        g.add((node, RETAIL.hasName, Literal(p.name)))
        g.add((node, RETAIL.hasPrice, Literal(p.price.amount, datatype=XSD.decimal)))
        g.add((node, RETAIL.belongsToCategory, RETAIL[f"Category/{p.category_id}"]))
        item = inventory.get(p.id)
        if item:
            inv_node = RETAIL[f"InventoryItem/{p.id}"]
            g.add((inv_node, RDF.type, RETAIL.InventoryItem))
            g.add((inv_node, RETAIL.hasQuantityOnHand, Literal(item.quantity_on_hand, datatype=XSD.integer)))
            g.add((inv_node, RETAIL.hasQuantityAvailable, Literal(item.quantity_available, datatype=XSD.integer)))
            g.add((node, RETAIL.hasInventory, inv_node))

    for c in customers.list_all():
        node = RETAIL[f"Customer/{c.id}"]
        g.add((node, RDF.type, RETAIL.Customer))
        g.add((node, RDFS.label, Literal(c.name)))
        g.add((node, RETAIL.hasEmail, Literal(str(c.email), datatype=XSD.string)))

    for o in orders.list_all():
        node = RETAIL[f"Order/{o.id}"]
        g.add((node, RDF.type, RETAIL.Order))
        g.add((node, RETAIL.hasStatus, Literal(o.status.value)))
        g.add((node, RETAIL.placedBy, RETAIL[f"Customer/{o.customer_id}"]))
        for idx, line in enumerate(o.lines):
            line_node = RETAIL[f"OrderLine/{o.id}-{idx}"]
            g.add((line_node, RDF.type, RETAIL.OrderLine))
            g.add((line_node, RETAIL.hasQuantity, Literal(line.quantity, datatype=XSD.integer)))
            g.add((line_node, RETAIL.forProduct, RETAIL[f"Product/{line.product_id}"]))
            g.add((node, RETAIL.contains, line_node))

    return g


def products_in_category_tree(g: Graph, category_id: str) -> list[dict]:
    """SPARQL property-path query: finds products in `category_id` OR any
    of its transitive subcategories (subCategoryOf*), which is exactly the
    kind of query that's awkward with plain SQL joins but natural in RDF.
    """
    query = """
    PREFIX retail: <http://retail-ddd-demo.org/onto#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?product ?label ?price WHERE {
        ?product a retail:Product ;
                 rdfs:label ?label ;
                 retail:hasPrice ?price ;
                 retail:belongsToCategory ?cat .
        ?cat retail:subCategoryOf* <http://retail-ddd-demo.org/onto#Category/%s> .
    }
    """ % category_id
    rows = g.query(query)
    return [
        {"product_uri": str(r.product), "label": str(r.label), "price": float(r.price)}
        for r in rows
    ]


def graph_to_vis_json(g: Graph, scope: str = "schema") -> dict:
    """Flattens the RDF graph into {nodes, edges} for the React ontology
    viewer. scope='schema' returns only classes+relationships (TBox);
    scope='instances' returns the live data graph (ABox)."""

    if scope == "schema":
        # The TBox is small and well-known -- read it straight from the
        # declarative lists in schema.py rather than reverse-engineering it
        # out of RDF triples (RDFS.domain/range triples describe properties,
        # they aren't the class-to-class edges we want to draw).
        nodes = [{"id": c, "label": c, "group": c} for c in SCHEMA_CLASSES]
        edges = [
            {"source": s, "target": o, "label": p}
            for s, p, o in SCHEMA_RELATIONSHIPS
        ]
        return {"nodes": nodes, "edges": edges}

    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def short(uri: str) -> str:
        return uri.split("#")[-1] if "#" in uri else uri.rsplit("/", 1)[-1]

    for s, p, o in g:
        p_name = short(str(p))
        if p_name in ("type", "label", "comment", "domain", "range"):
            continue
        s_id, o_id = str(s), str(o)
        # Instance nodes are minted as RETAIL["Product/<id>"] (contains a
        # "/" after the "#"); schema terms like RETAIL.Product do not.
        s_is_instance = "/" in s_id.split("#", 1)[-1]
        if not s_is_instance:
            continue

        for node_id in (s_id, o_id):
            if node_id not in nodes:
                nodes[node_id] = {
                    "id": node_id,
                    "label": short(node_id),
                    "group": short(node_id).split("/")[0] if "/" in short(node_id) else short(node_id),
                }
        edges.append({"source": s_id, "target": o_id, "label": p_name})

    return {"nodes": list(nodes.values()), "edges": edges}
