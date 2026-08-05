"""
Repository Interfaces (Ports)
==============================
The domain layer defines *what* persistence it needs as abstract
interfaces. The infrastructure layer provides the *how* (in this demo,
simple in-memory dictionaries -- swap in a SQL implementation later
without touching a single line of domain or application code).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from .entities import Product, Customer, Category, InventoryItem
from .aggregates import Order


class ProductRepository(ABC):
    @abstractmethod
    def get(self, product_id: str) -> Product | None: ...

    @abstractmethod
    def list_all(self) -> list[Product]: ...

    @abstractmethod
    def save(self, product: Product) -> None: ...


class CategoryRepository(ABC):
    @abstractmethod
    def get(self, category_id: str) -> Category | None: ...

    @abstractmethod
    def list_all(self) -> list[Category]: ...


class CustomerRepository(ABC):
    @abstractmethod
    def get(self, customer_id: str) -> Customer | None: ...

    @abstractmethod
    def save(self, customer: Customer) -> None: ...

    @abstractmethod
    def list_all(self) -> list[Customer]: ...


class InventoryRepository(ABC):
    @abstractmethod
    def get(self, product_id: str) -> InventoryItem | None: ...

    @abstractmethod
    def save(self, item: InventoryItem) -> None: ...

    @abstractmethod
    def list_all(self) -> list[InventoryItem]: ...


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def list_all(self) -> list[Order]: ...
