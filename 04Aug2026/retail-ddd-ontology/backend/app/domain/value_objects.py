"""
Value Objects
=============
A Value Object has no identity of its own -- two Money(10, "USD") instances
are considered equal. They are immutable (frozen dataclasses) and validate
themselves on construction, so illegal states cannot exist in the domain.
"""
from __future__ import annotations
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if self.currency not in ("USD", "EUR", "INR", "GBP"):
            raise ValueError(f"Unsupported currency: {self.currency}")

    def add(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(round(self.amount + other.amount, 2), self.currency)

    def multiply(self, factor: float) -> "Money":
        return Money(round(self.amount * factor, 2), self.currency)

    def subtract(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(round(self.amount - other.amount, 2), self.currency)

    def _assert_same_currency(self, other: "Money"):
        if self.currency != other.currency:
            raise ValueError("Cannot operate on Money with different currencies")

    def as_dict(self):
        return {"amount": self.amount, "currency": self.currency}


@dataclass(frozen=True)
class SKU:
    """Stock Keeping Unit code, e.g. 'ELEC-0001'."""
    code: str

    def __post_init__(self):
        if not re.match(r"^[A-Z]{2,6}-\d{3,6}$", self.code):
            raise ValueError(f"Invalid SKU format: {self.code}")

    def __str__(self):
        return self.code


@dataclass(frozen=True)
class Email:
    address: str

    def __post_init__(self):
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", self.address):
            raise ValueError(f"Invalid email address: {self.address}")

    def __str__(self):
        return self.address
