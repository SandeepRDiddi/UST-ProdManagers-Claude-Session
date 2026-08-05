"""
Entities
========
An Entity has an identity (id) that persists across state changes.
Two Products with the same name but different ids are different products.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from .value_objects import Money, SKU, Email


@dataclass
class Category:
    """Categories form the isA hierarchy used later by the ontology layer.

    e.g. 'Laptops' isA 'Electronics' isA 'Product' (root concept)
    """
    id: str
    name: str
    parent_id: str | None = None


@dataclass
class Product:
    """A sellable item in the Catalog bounded context."""
    id: str
    sku: SKU
    name: str
    category_id: str
    price: Money
    brand: str = "Generic"
    description: str = ""

    def reprice(self, new_price: Money):
        self.price = new_price


@dataclass
class Customer:
    id: str
    name: str
    email: Email


@dataclass
class InventoryItem:
    """Aggregate root of the Inventory bounded context.

    Tracks stock on hand vs. reserved (soft-held for open orders), which is
    the classic pattern that avoids overselling without locking rows.
    """
    product_id: str
    quantity_on_hand: int
    quantity_reserved: int = 0

    @property
    def quantity_available(self) -> int:
        return self.quantity_on_hand - self.quantity_reserved

    def reserve(self, quantity: int):
        if quantity > self.quantity_available:
            raise ValueError(
                f"Cannot reserve {quantity} units; only "
                f"{self.quantity_available} available"
            )
        self.quantity_reserved += quantity

    def release(self, quantity: int):
        self.quantity_reserved = max(0, self.quantity_reserved - quantity)

    def fulfill(self, quantity: int):
        """Stock physically leaves the warehouse."""
        self.quantity_on_hand -= quantity
        self.quantity_reserved = max(0, self.quantity_reserved - quantity)
