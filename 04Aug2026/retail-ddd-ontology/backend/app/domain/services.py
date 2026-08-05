"""
Domain Services
===============
Logic that doesn't naturally belong to a single Entity or Aggregate because
it coordinates across several of them.
"""
from __future__ import annotations
from .entities import InventoryItem
from .repositories import InventoryRepository
from .events import StockReserved, StockInsufficient


class InventoryService:
    """Coordinates stock checks/reservations across InventoryItems."""

    def __init__(self, inventory_repo: InventoryRepository):
        self._inventory_repo = inventory_repo

    def check_and_reserve(self, product_id: str, quantity: int) -> list:
        item = self._inventory_repo.get(product_id)
        events = []
        if item is None or item.quantity_available < quantity:
            available = item.quantity_available if item else 0
            events.append(StockInsufficient(product_id, quantity, available))
            return events
        item.reserve(quantity)
        self._inventory_repo.save(item)
        events.append(StockReserved(product_id, quantity))
        return events


class PricingService:
    """Simple category-based discount rule, kept intentionally small so the
    concept of a 'domain service' stays easy to follow."""

    BULK_DISCOUNT_THRESHOLD = 5
    BULK_DISCOUNT_RATE = 0.10

    @classmethod
    def line_discount_rate(cls, quantity: int) -> float:
        return cls.BULK_DISCOUNT_RATE if quantity >= cls.BULK_DISCOUNT_THRESHOLD else 0.0
