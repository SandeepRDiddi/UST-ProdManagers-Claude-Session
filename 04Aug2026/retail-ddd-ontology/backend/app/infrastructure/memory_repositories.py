"""
In-Memory Repository Implementations (Adapters)
=================================================
Implements the abstract repository interfaces from domain/repositories.py
using plain Python dicts. This keeps the demo dependency-free (no database
to install) while proving the DDD point: the application layer only ever
talks to the abstract interfaces, so this file could be swapped for a
SQLAlchemy/Postgres implementation without changing domain or application
code at all.
"""
from __future__ import annotations
from ..domain.entities import Product, Customer, Category, InventoryItem
from ..domain.aggregates import Order
from ..domain.repositories import (
    ProductRepository, CategoryRepository, CustomerRepository,
    InventoryRepository, OrderRepository,
)


class InMemoryProductRepository(ProductRepository):
    def __init__(self):
        self._store: dict[str, Product] = {}

    def get(self, product_id: str) -> Product | None:
        return self._store.get(product_id)

    def list_all(self) -> list[Product]:
        return list(self._store.values())

    def save(self, product: Product) -> None:
        self._store[product.id] = product


class InMemoryCategoryRepository(CategoryRepository):
    def __init__(self):
        self._store: dict[str, Category] = {}

    def get(self, category_id: str) -> Category | None:
        return self._store.get(category_id)

    def list_all(self) -> list[Category]:
        return list(self._store.values())

    def save(self, category: Category) -> None:
        self._store[category.id] = category


class InMemoryCustomerRepository(CustomerRepository):
    def __init__(self):
        self._store: dict[str, Customer] = {}

    def get(self, customer_id: str) -> Customer | None:
        return self._store.get(customer_id)

    def save(self, customer: Customer) -> None:
        self._store[customer.id] = customer

    def list_all(self) -> list[Customer]:
        return list(self._store.values())


class InMemoryInventoryRepository(InventoryRepository):
    def __init__(self):
        self._store: dict[str, InventoryItem] = {}

    def get(self, product_id: str) -> InventoryItem | None:
        return self._store.get(product_id)

    def save(self, item: InventoryItem) -> None:
        self._store[item.product_id] = item

    def list_all(self) -> list[InventoryItem]:
        return list(self._store.values())


class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._store: dict[str, Order] = {}

    def get(self, order_id: str) -> Order | None:
        return self._store.get(order_id)

    def save(self, order: Order) -> None:
        self._store[order.id] = order

    def list_all(self) -> list[Order]:
        return list(self._store.values())
