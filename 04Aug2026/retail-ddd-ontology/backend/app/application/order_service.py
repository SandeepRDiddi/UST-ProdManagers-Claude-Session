"""
Application Service: Ordering
================================
Coordinates the "place an order" use case across the Ordering and
Inventory bounded contexts: it loads Products for pricing, asks the
InventoryService to reserve stock, builds the Order aggregate, and
persists it -- then returns the domain events raised along the way so the
API layer can report exactly what happened (e.g. which lines succeeded).
"""
from __future__ import annotations
import uuid
from ..domain.aggregates import Order, OrderLine
from ..domain.events import OrderPlaced, StockInsufficient
from ..domain.repositories import ProductRepository, OrderRepository, CustomerRepository
from ..domain.services import InventoryService


class OrderPlacementError(Exception):
    def __init__(self, message: str, details: list[dict] | None = None):
        super().__init__(message)
        self.details = details or []


class OrderService:
    def __init__(self, products: ProductRepository, orders: OrderRepository,
                 customers: CustomerRepository, inventory_service: InventoryService):
        self._products = products
        self._orders = orders
        self._customers = customers
        self._inventory_service = inventory_service

    def place_order(self, customer_id: str, line_items: list[dict]) -> dict:
        if self._customers.get(customer_id) is None:
            raise OrderPlacementError(f"Unknown customer: {customer_id}")
        if not line_items:
            raise OrderPlacementError("An order must contain at least one line item")

        order = Order(id=str(uuid.uuid4())[:8], customer_id=customer_id)
        insufficient: list[dict] = []

        for item in line_items:
            product = self._products.get(item["product_id"])
            if product is None:
                raise OrderPlacementError(f"Unknown product: {item['product_id']}")

            events = self._inventory_service.check_and_reserve(product.id, item["quantity"])
            for ev in events:
                if isinstance(ev, StockInsufficient):
                    insufficient.append({
                        "product_id": ev.product_id,
                        "product_name": product.name,
                        "requested": ev.requested,
                        "available": ev.available,
                    })

        if insufficient:
            raise OrderPlacementError("Insufficient stock for one or more items", insufficient)

        for item in line_items:
            product = self._products.get(item["product_id"])
            order.add_line(OrderLine(
                product_id=product.id,
                sku=str(product.sku),
                product_name=product.name,
                quantity=item["quantity"],
                unit_price=product.price,
            ))

        order.place()
        total = order.total()
        order.record_event(OrderPlaced(order.id, customer_id, total.amount, total.currency))
        self._orders.save(order)

        return self._to_dict(order)

    def get_order(self, order_id: str) -> dict | None:
        order = self._orders.get(order_id)
        return self._to_dict(order) if order else None

    def list_orders(self) -> list[dict]:
        return [self._to_dict(o) for o in self._orders.list_all()]

    @staticmethod
    def _to_dict(order: Order) -> dict:
        return {
            "id": order.id,
            "customer_id": order.customer_id,
            "status": order.status.value,
            "placed_at": order.placed_at.isoformat() if order.placed_at else None,
            "lines": [
                {
                    "product_id": l.product_id,
                    "sku": l.sku,
                    "product_name": l.product_name,
                    "quantity": l.quantity,
                    "unit_price": l.unit_price.as_dict(),
                    "line_total": l.line_total.as_dict(),
                }
                for l in order.lines
            ],
            "total": order.total().as_dict(),
        }
