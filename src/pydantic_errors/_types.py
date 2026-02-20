"""Core types for errantic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ErrorDetail:
    """A single parsed validation error.

    Attributes:
        path: Dotted path to the field, e.g. ``"user.addresses[1].zipcode"``.
        message: Human-readable error message from Pydantic.
        error_type: Pydantic error type code, e.g. ``"missing"``.
        input_value: The actual invalid input value.
        context: Extra context dict from Pydantic.
        url: Pydantic documentation URL for this error type.
    """

    path: str
    message: str
    error_type: str
    input_value: Any
    context: dict[str, Any]
    url: str


@dataclass(frozen=True, slots=True)
class FormatOptions:
    """Configuration for error formatting.

    Attributes:
        show_input: Whether to show the ``"Got:"`` line with the input value.
        show_url: Whether to show the Pydantic docs URL.
        show_error_type: Whether to show the error type tag.
        input_max_length: Maximum length for input value repr.
    """

    show_input: bool = True
    show_url: bool = False
    show_error_type: bool = False
    input_max_length: int = 80
