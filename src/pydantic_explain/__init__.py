"""pydantic-explain: human-readable error messages for Pydantic validation errors."""

from __future__ import annotations

from pydantic_explain._explain import explain
from pydantic_explain._filter import count_errors, filter_errors, group_errors
from pydantic_explain._format import format_error_detail, format_errors
from pydantic_explain._rich import format_errors_rich
from pydantic_explain._types import ErrorDetail, FormatOptions

__all__ = [
    "ErrorDetail",
    "FormatOptions",
    "count_errors",
    "explain",
    "filter_errors",
    "format_error_detail",
    "format_errors",
    "format_errors_rich",
    "group_errors",
]
