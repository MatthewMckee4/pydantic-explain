"""Shared test models and helpers."""

from __future__ import annotations

import datetime  # noqa: TC003 - needed at runtime for Pydantic model validation
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Any, Literal

import karva

if TYPE_CHECKING:
    from collections.abc import Generator
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator


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


class ExtraForbid(BaseModel):
    """Test model that forbids extra fields."""

    model_config = ConfigDict(extra="forbid")

    name: str


class PatternConstrained(BaseModel):
    """Test model with regex pattern constraint."""

    code: Annotated[str, Field(pattern=r"^[A-Z]{3}-\d{3}$")]


class StringConstrained(BaseModel):
    """Test model with string length constraints."""

    short: Annotated[str, Field(min_length=2, max_length=5)]


class NumericConstrained(BaseModel):
    """Test model with numeric range constraints."""

    score: Annotated[int, Field(ge=0, le=100)]
    factor: Annotated[float, Field(gt=0.0, lt=1.0)]


class ListConstrained(BaseModel):
    """Test model with list length constraints."""

    tags: Annotated[list[str], Field(min_length=1, max_length=5)]


class Color(str, Enum):
    """Test enum for validation."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class EnumModel(BaseModel):
    """Test model with enum field."""

    color: Color


class LiteralModel(BaseModel):
    """Test model with Literal type."""

    status: Literal["active", "inactive"]
    priority: Literal[1, 2, 3]


class DictModel(BaseModel):
    """Test model with dict fields."""

    metadata: dict[str, int]


class NestedListModel(BaseModel):
    """Test model with nested list of models."""

    matrix: list[list[int]]
    users: list[User]


class AliasModel(BaseModel):
    """Test model with field aliases."""

    name: str = Field(alias="full_name")
    age: int = Field(alias="user_age")


class DateTimeModel(BaseModel):
    """Test model with date/time fields."""

    created: datetime.date
    updated: datetime.datetime


class TupleModel(BaseModel):
    """Test model with tuple fields."""

    point: tuple[int, int]
    rgb: tuple[int, int, int]


class SetModel(BaseModel):
    """Test model with set and frozenset fields."""

    unique_tags: set[str]
    frozen_ids: frozenset[int]


class MultipleConstraints(BaseModel):
    """Test model with multiple constrained fields to generate diverse errors."""

    name: Annotated[str, Field(min_length=1, max_length=50)]
    age: Annotated[int, Field(ge=0, le=150)]
    email: str
    score: Annotated[float, Field(ge=0.0)]


class Level4(BaseModel):
    """Deepest level for 5-level nesting tests."""

    value: int


class Level3(BaseModel):
    """Level 3 for deep nesting."""

    level4: Level4


class Level2(BaseModel):
    """Level 2 for deep nesting."""

    level3: Level3


class Level1(BaseModel):
    """Level 1 for deep nesting."""

    level2: Level2


class Level0(BaseModel):
    """Top level for 5-level nesting tests."""

    level1: Level1


class ModelValidated(BaseModel):
    """Test model with a model-level validator."""

    password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> ModelValidated:
        if self.password != self.confirm_password:
            msg = "Passwords do not match"
            raise ValueError(msg)
        return self


class MultiFieldValidated(BaseModel):
    """Test model with validators on multiple fields."""

    username: str
    email: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            msg = "Username must be alphanumeric"
            raise ValueError(msg)
        return v

    @field_validator("email")
    @classmethod
    def email_has_at(cls, v: str) -> str:
        if "@" not in v:
            msg = "Email must contain @"
            raise ValueError(msg)
        return v


class StrictModel(BaseModel):
    """Test model with strict mode."""

    model_config = ConfigDict(strict=True)

    count: int
    name: str
    active: bool


class MixedErrorModel(BaseModel):
    """Model designed to produce many different error types at once."""

    name: str
    age: int
    score: Annotated[float, Field(gt=0)]
    code: Annotated[str, Field(pattern=r"^[A-Z]+$")]
    tags: Annotated[list[str], Field(min_length=1)]
    address: Address


def make_validation_error(model: type[BaseModel], data: dict[str, Any]) -> ValidationError:
    """Create a ValidationError by validating bad data against a model."""
    try:
        model.model_validate(data)
    except ValidationError as e:
        return e
    msg = "Expected ValidationError"
    raise AssertionError(msg)
