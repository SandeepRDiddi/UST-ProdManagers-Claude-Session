"""
Aggregates
==========
The Order aggregate is the transactional consistency boundary for placing
an order: OrderLines can only be added/changed through the Order root, and
the root enforces invariants (e.g. "an order must have at least one line",
"a placed order cannot be modified").
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from .value_objects import Money
from .events import DomainEvent, OrderCancelled


class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    PLACED = "PLACED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


@dataclass
class OrderLine:
    product_id: str
    sku: str
    product_name: str
    quantity: int
    unit_price: Money

    @property
    def line_total(self) -> Money:
        return self.unit_price.multiply(self.quantity)


@dataclass
class Order:
    """Aggregate root for the Ordering bounded context."""
    id: str
    customer_id: str
    lines: list[OrderLine] = field(default_factory=list)
    status: OrderStatus = OrderStatus.DRAFT
    placed_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    def add_line(self, line: OrderLine):
        if self.status != OrderStatus.DRAFT:
            raise ValueError("Cannot modify an order that is not in DRAFT")
        if line.quantity <= 0:
            raise ValueError("OrderLine quantity must be positive")
        self.lines.append(line)

    def total(self) -> Money:
        if not self.lines:
            return Money(0, "USD")
        currency = self.lines[0].unit_price.currency
        total = Money(0, currency)
        for line in self.lines:
            total = total.add(line.line_total)
        return total

    def place(self):
        if not self.lines:
            raise ValueError("An order must contain at least one line to be placed")
        if self.status != OrderStatus.DRAFT:
            raise ValueError("Order has already been placed")
        self.status = OrderStatus.PLACED
        self.placed_at = datetime.now(timezone.utc)

    def cancel(self):
        if self.status != OrderStatus.PLACED:
            raise ValueError("Only a PLACED order can be cancelled")
        self.status = OrderStatus.CANCELLED
        self.record_event(OrderCancelled(self.id, self.customer_id))

    def pull_events(self) -> list[DomainEvent]:
        events, self._events = self._events, []
        return events

    def record_event(self, event: DomainEvent):
        self._events.append(event)
