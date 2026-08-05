"""
JSON File Repository (Adapter) -- Exercise 6
==============================================
A second implementation of ProductRepository (domain/repositories.py),
this time persisting to a local JSON file instead of a plain dict. It
exists to prove the Ports & Adapters claim from README/CLAUDE.md: swapping
storage only requires a new class here in infrastructure/ -- domain/ and
application/ are untouched (they only ever import the abstract
ProductRepository interface, never this class).
"""
from __future__ import annotations
import json
from pathlib import Path
from ..domain.entities import Product
from ..domain.value_objects import Money, SKU
from ..domain.repositories import ProductRepository


class JsonFileProductRepository(ProductRepository):
    def __init__(self, file_path: str | Path):
        self._path = Path(file_path)
        self._store: dict[str, Product] = {}
        if self._path.exists():
            self._load()
        else:
            self._path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, product_id: str) -> Product | None:
        return self._store.get(product_id)

    def list_all(self) -> list[Product]:
        return list(self._store.values())

    def save(self, product: Product) -> None:
        self._store[product.id] = product
        self._flush()

    def _load(self) -> None:
        raw = json.loads(self._path.read_text())
        for row in raw:
            self._store[row["id"]] = Product(
                id=row["id"],
                sku=SKU(row["sku"]),
                name=row["name"],
                category_id=row["category_id"],
                price=Money(row["price"]["amount"], row["price"]["currency"]),
                brand=row.get("brand", "Generic"),
                description=row.get("description", ""),
            )

    def _flush(self) -> None:
        rows = [
            {
                "id": p.id,
                "sku": str(p.sku),
                "name": p.name,
                "category_id": p.category_id,
                "price": p.price.as_dict(),
                "brand": p.brand,
                "description": p.description,
            }
            for p in self._store.values()
        ]
        self._path.write_text(json.dumps(rows, indent=2))
