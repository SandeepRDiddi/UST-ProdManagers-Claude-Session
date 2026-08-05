"""
Ontology Schema (TBox)
=======================
This is the *conceptual* model of the retail world, expressed as an OWL-lite
ontology using rdflib. It is deliberately kept separate from the DDD domain
model in domain/entities.py:

  - The DDD layer answers "how does the software behave" (invariants,
    transactions, use cases).
  - The ontology answers "what do these concepts mean and how do they
    relate" (classes, is-a hierarchies, relationships) -- a shared,
    machine-readable vocabulary that both humans and future
    reasoning/search tools (SPARQL, embeddings, LLM agents) can query.

Namespace prefix used throughout: RETAIL: http://retail-ddd-demo.org/onto#
"""
from __future__ import annotations
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef
from rdflib.namespace import XSD

RETAIL = Namespace("http://retail-ddd-demo.org/onto#")


def build_schema_graph() -> Graph:
    """Builds the TBox (terminology box): classes + properties only,
    no individuals. This is the ontology's 'schema.'"""
    g = Graph()
    g.bind("retail", RETAIL)

    # ---- Classes -----------------------------------------------------
    classes = {
        "Product": "A sellable item in the catalog.",
        "Category": "A grouping concept that classifies products; "
                     "categories form an is-a hierarchy.",
        "Customer": "A person who places orders.",
        "Order": "A confirmed request by a Customer to purchase one or more Products.",
        "OrderLine": "A single product/quantity entry within an Order.",
        "InventoryItem": "The stock record for a Product.",
        "Brand": "The manufacturer or label a Product is sold under.",
    }
    for name, comment in classes.items():
        cls = RETAIL[name]
        g.add((cls, RDF.type, OWL.Class))
        g.add((cls, RDFS.label, Literal(name)))
        g.add((cls, RDFS.comment, Literal(comment)))

    # Category is reflexively hierarchical: subCategoryOf composes like
    # RDFS subClassOf but at the *instance* level (a Category is an
    # individual, not a class, in this simplified teaching ontology).
    g.add((RETAIL.subCategoryOf, RDF.type, OWL.ObjectProperty))
    g.add((RETAIL.subCategoryOf, RDFS.domain, RETAIL.Category))
    g.add((RETAIL.subCategoryOf, RDFS.range, RETAIL.Category))
    g.add((RETAIL.subCategoryOf, RDFS.label, Literal("subCategoryOf (is-a)")))

    # ---- Object Properties (relationships) ----------------------------
    object_properties = [
        ("belongsToCategory", "Product", "Category"),
        ("hasInventory", "Product", "InventoryItem"),
        ("hasBrand", "Product", "Brand"),
        ("placedBy", "Order", "Customer"),
        ("contains", "Order", "OrderLine"),
        ("forProduct", "OrderLine", "Product"),
    ]
    for name, domain, range_ in object_properties:
        prop = RETAIL[name]
        g.add((prop, RDF.type, OWL.ObjectProperty))
        g.add((prop, RDFS.domain, RETAIL[domain]))
        g.add((prop, RDFS.range, RETAIL[range_]))
        g.add((prop, RDFS.label, Literal(name)))

    # ---- Data Properties (literal attributes) -------------------------
    data_properties = [
        ("hasSKU", "Product", XSD.string),
        ("hasName", "Product", XSD.string),
        ("hasPrice", "Product", XSD.decimal),
        ("hasQuantityOnHand", "InventoryItem", XSD.integer),
        ("hasQuantityAvailable", "InventoryItem", XSD.integer),
        ("hasStatus", "Order", XSD.string),
        ("hasQuantity", "OrderLine", XSD.integer),
        ("hasEmail", "Customer", XSD.string),
        ("hasBrandName", "Brand", XSD.string),
    ]
    for name, domain, range_ in data_properties:
        prop = RETAIL[name]
        g.add((prop, RDF.type, OWL.DatatypeProperty))
        g.add((prop, RDFS.domain, RETAIL[domain]))
        g.add((prop, RDFS.range, range_))
        g.add((prop, RDFS.label, Literal(name)))

    return g


SCHEMA_CLASSES = ["Product", "Category", "Customer", "Order", "OrderLine", "InventoryItem", "Brand"]
SCHEMA_RELATIONSHIPS = [
    ("Category", "subCategoryOf", "Category"),
    ("Product", "belongsToCategory", "Category"),
    ("Product", "hasInventory", "InventoryItem"),
    ("Product", "hasBrand", "Brand"),
    ("Order", "placedBy", "Customer"),
    ("Order", "contains", "OrderLine"),
    ("OrderLine", "forProduct", "Product"),
]
