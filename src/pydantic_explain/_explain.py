"""Explain Pydantic validation errors as structured data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_explain._types import ErrorDetail

if TYPE_CHECKING:
    from pydantic import ValidationError


def explain(error: ValidationError) -> tuple[ErrorDetail, ...]:
    """Parse a Pydantic ValidationError into structured ErrorDetail objects.

    Args:
        error: A Pydantic ValidationError instance.

    Returns:
        A tuple of ErrorDetail objects, one per validation error.
    """
    return tuple(
        ErrorDetail(
            path=_format_loc(err["loc"]),
            message=err["msg"],
            error_type=err["type"],
            input_value=err.get("input"),
            context=err.get("ctx", {}),
            url=err.get("url", ""),
        )
        for err in error.errors()
    )


def _format_loc(loc: tuple[str | int, ...]) -> str:
    if not loc:
        return "<root>"
    parts: list[str] = []
    for segment in loc:
        if isinstance(segment, int):
            parts.append(f"[{segment}]")
        elif segment == "__all__":
            parts.append("[*]")
        elif parts:
            parts.append(f".{segment}")
        else:
            parts.append(str(segment))
    return "".join(parts)
