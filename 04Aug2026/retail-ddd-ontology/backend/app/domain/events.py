"""
Domain Events
=============
Facts that happened in the domain, named in the past tense. Other parts of
the system (or other bounded contexts) can react to these without the
Order aggregate needing to know who's listening.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc), init=False
    )


@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: str
    customer_id: str
    total_amount: float
    currency: str


@dataclass(frozen=True)
class StockReserved(DomainEvent):
    product_id: str
    quantity: int


@dataclass(frozen=True)
class StockInsufficient(DomainEvent):
    product_id: str
    requested: int
    available: int


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    order_id: str
    customer_id: str
