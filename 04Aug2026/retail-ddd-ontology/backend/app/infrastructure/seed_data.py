"""
Seed Data
=========
Populates the in-memory repositories with a small, deliberately simple
retail catalog so the app is immediately explorable after `uvicorn` starts:
no setup wizard, no empty states to click through first.
"""
from __future__ import annotations
from ..domain.entities import Category, Product, InventoryItem, Customer
from ..domain.value_objects import Money, SKU, Email
from .memory_repositories import (
    InMemoryProductRepository, InMemoryCategoryRepository,
    InMemoryCustomerRepository, InMemoryInventoryRepository,
    InMemoryOrderRepository,
)


def seed() -> dict:
    products = InMemoryProductRepository()
    categories = InMemoryCategoryRepository()
    customers = InMemoryCustomerRepository()
    inventory = InMemoryInventoryRepository()
    orders = InMemoryOrderRepository()

    # --- Category hierarchy (feeds the ontology's subCategoryOf chain) ---
    cat_defs = [
        ("cat-electronics", "Electronics", None),
        ("cat-computers", "Computers", "cat-electronics"),
        ("cat-laptops", "Laptops", "cat-computers"),
        ("cat-audio", "Audio", "cat-electronics"),
        ("cat-kitchen", "Kitchen", None),
        ("cat-appliances", "Small Appliances", "cat-kitchen"),
    ]
    for cid, name, parent in cat_defs:
        categories.save(Category(id=cid, name=name, parent_id=parent))

    # --- Products ---------------------------------------------------------
    # brand added per exercise 4 (LEARN.md): domain field first, ontology wired after
    product_defs = [
        ("prod-001", "ELEC-1001", "14-inch Ultrabook", "cat-laptops", 1099.00, "Northwind",
         "Lightweight laptop with 16GB RAM and 512GB SSD.", 12),
        ("prod-002", "ELEC-1002", "15-inch Creator Laptop", "cat-laptops", 1899.00, "Northwind",
         "High-performance laptop for design and video work.", 5),
        ("prod-003", "ELEC-2001", "Wireless Noise-Cancelling Headphones", "cat-audio", 249.00, "Aurora",
         "Over-ear headphones with 30-hour battery life.", 40),
        ("prod-004", "ELEC-2002", "Bluetooth Speaker", "cat-audio", 79.00, "Aurora",
         "Compact speaker, IPX7 water resistant.", 60),
        ("prod-005", "KTCH-3001", "Stand Mixer", "cat-appliances", 349.00, "Kestrel",
         "5-quart stand mixer with 3 attachments.", 8),
        ("prod-006", "KTCH-3002", "Espresso Machine", "cat-appliances", 599.00, "Kestrel",
         "15-bar pump espresso machine with milk frother.", 4),
    ]
    for pid, sku, name, cat_id, price, brand, desc, qty in product_defs:
        products.save(Product(
            id=pid, sku=SKU(sku), name=name, category_id=cat_id,
            price=Money(price, "USD"), brand=brand, description=desc,
        ))
        inventory.save(InventoryItem(product_id=pid, quantity_on_hand=qty))

    # GBP product — exercise 1: confirm a non-USD currency round-trips through /api/products
    products.save(Product(
        id="prod-007", sku=SKU("ELEC-1003"), name="UK Travel Adapter Laptop Charger",
        category_id="cat-laptops", price=Money(89.00, "GBP"), brand="Northwind",
        description="65W GaN charger with UK plug.",
    ))
    inventory.save(InventoryItem(product_id="prod-007", quantity_on_hand=20))

    # --- A sample customer --------------------------------------------------
    customers.save(Customer(
        id="cust-001", name="Sandeep R", email=Email("sandeep@example.com")
    ))

    return {
        "products": products,
        "categories": categories,
        "customers": customers,
        "inventory": inventory,
        "orders": orders,
    }
