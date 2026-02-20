"""Shared test models and helpers."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ValidationError


class Address(BaseModel):
    """Test address model."""

    street: str
    city: str
    zipcode: str


class User(BaseModel):
    """Test user model."""

    name: str
    age: int
    email: str
    addresses: list[Address]


class Order(BaseModel):
    """Test order model."""

    id: int
    user: User
    items: list[str]


class Constrained(BaseModel):
    """Test model with field constraints."""

    value: int = Field(gt=0)


def make_validation_error(model: type[BaseModel], data: dict[str, Any]) -> ValidationError:
    """Create a ValidationError by validating bad data against a model."""
    try:
        model.model_validate(data)
    except ValidationError as e:
        return e
    msg = "Expected ValidationError"
    raise AssertionError(msg)
