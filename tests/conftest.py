"""Shared test models and helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import karva

if TYPE_CHECKING:
    from collections.abc import Generator
from pydantic import BaseModel, Field, ValidationError, field_validator


@karva.fixture(auto_use=True)
def _normalise_pydantic_version() -> Generator[None]:
    """Replace the pydantic version in snapshot URLs so tests survive upgrades."""
    with karva.snapshot_settings(
        filters=[(r"errors\.pydantic\.dev/\d+\.\d+", "errors.pydantic.dev/VERSION")]
    ):
        yield


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


class OptionalFields(BaseModel):
    """Test model with optional fields."""

    name: str
    nickname: str | None = None
    age: int | None = None


class UnionFields(BaseModel):
    """Test model with union types."""

    value: int | str
    tag: str | list[str]


class Inner(BaseModel):
    """Innermost level for deep nesting tests."""

    code: str


class Middle(BaseModel):
    """Middle level for deep nesting tests."""

    inner: Inner


class Outer(BaseModel):
    """Top level for deep nesting tests (3+ level nesting)."""

    middle: Middle


class Validated(BaseModel):
    """Test model with a custom field validator."""

    username: str

    @field_validator("username")
    @classmethod
    def username_must_be_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            msg = "must be alphanumeric"
            raise ValueError(msg)
        return v


def make_validation_error(model: type[BaseModel], data: dict[str, Any]) -> ValidationError:
    """Create a ValidationError by validating bad data against a model."""
    try:
        model.model_validate(data)
    except ValidationError as e:
        return e
    msg = "Expected ValidationError"
    raise AssertionError(msg)
