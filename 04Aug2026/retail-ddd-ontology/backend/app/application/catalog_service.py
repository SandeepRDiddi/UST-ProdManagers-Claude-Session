"""
Application Service: Catalog
==============================
Application services orchestrate use cases. They contain no business rules
themselves (those live in the domain layer) -- they just fetch data via
repositories and shape it for the API/UI.
"""
from __future__ import annotations
from ..domain.repositories import ProductRepository, CategoryRepository, InventoryRepository


class CatalogService:
    def __init__(self, products: ProductRepository, categories: CategoryRepository,
                 inventory: InventoryRepository):
        self._products = products
        self._categories = categories
        self._inventory = inventory

    def list_products(self) -> list[dict]:
        result = []
        for p in self._products.list_all():
            item = self._inventory.get(p.id)
            result.append({
                "id": p.id,
                "sku": str(p.sku),
                "name": p.name,
                "brand": p.brand,
                "description": p.description,
                "category_id": p.category_id,
                "price": p.price.as_dict(),
                "quantity_available": item.quantity_available if item else 0,
            })
        return result

    def category_tree(self) -> list[dict]:
        cats = self._categories.list_all()
        return [{"id": c.id, "name": c.name, "parent_id": c.parent_id} for c in cats]
