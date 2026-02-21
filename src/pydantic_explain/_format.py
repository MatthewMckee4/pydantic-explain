"""Format Pydantic validation errors as human-readable strings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_explain._explain import explain
from pydantic_explain._types import ErrorDetail, FormatOptions

if TYPE_CHECKING:
    from pydantic import ValidationError


def format_errors(error: ValidationError, *, options: FormatOptions | None = None) -> str:
    """Format a Pydantic ValidationError as a human-readable string.

    Args:
        error: A Pydantic ValidationError instance.
        options: Formatting options. Uses defaults if None.

    Returns:
        A formatted multi-line string describing all validation errors.
    """
    details = explain(error)
    opts = options or FormatOptions()

    count = len(details)
    plural = "error" if count == 1 else "errors"
    lines = [f"Validation failed for {error.title} with {count} {plural}"]

    for detail in details:
        lines.append("")
        lines.append(format_error_detail(detail, options=opts))

    return "\n".join(lines)


def format_error_detail(detail: ErrorDetail, *, options: FormatOptions | None = None) -> str:
    """Format a single ErrorDetail as a human-readable string.

    Args:
        detail: A parsed error detail.
        options: Formatting options. Uses defaults if None.

    Returns:
        A formatted multi-line string for one validation error.
    """
    opts = options or FormatOptions()
    lines = [f"  {detail.path}"]

    message = detail.message
    if opts.show_error_type:
        message = f"{message} [{detail.error_type}]"
    lines.append(f"    {message}")

    if opts.show_input:
        if detail.error_type == "missing":
            lines.append("    Got: (missing)")
        else:
            lines.append(f"    Got: {_truncate_repr(detail.input_value, opts.input_max_length)}")

    if opts.show_url and detail.url:
        lines.append(f"    See: {detail.url}")

    return "\n".join(lines)


def _truncate_repr(value: object, max_length: int) -> str:
    r = repr(value)
    if len(r) <= max_length:
        return r
    return r[: max_length - 3] + "..."
