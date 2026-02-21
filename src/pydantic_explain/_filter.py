"""Helpers for filtering and grouping validation errors."""

from __future__ import annotations

import re
from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic_explain._types import ErrorDetail


def filter_errors(
    errors: tuple[ErrorDetail, ...],
    *,
    error_type: str | None = None,
    path_pattern: str | None = None,
) -> tuple[ErrorDetail, ...]:
    """Filter errors by error type and/or path pattern.

    Args:
        errors: Tuple of ErrorDetail objects (from ``explain()``).
        error_type: Keep only errors matching this type, e.g. ``"missing"``.
        path_pattern: Keep only errors whose path matches this regex.

    Returns:
        A filtered tuple of ErrorDetail objects.
    """
    result = errors
    if error_type is not None:
        result = tuple(e for e in result if e.error_type == error_type)
    if path_pattern is not None:
        compiled = re.compile(path_pattern)
        result = tuple(e for e in result if compiled.search(e.path))
    return result


def group_errors(
    errors: tuple[ErrorDetail, ...],
) -> dict[str, tuple[ErrorDetail, ...]]:
    """Group errors by their top-level path prefix.

    The prefix is the portion before the first ``.`` or ``[``.
    For example, ``addresses[0].street`` and ``addresses[1].city``
    both group under ``"addresses"``.

    Args:
        errors: Tuple of ErrorDetail objects (from ``explain()``).

    Returns:
        A dict mapping path prefix to a tuple of matching errors.
    """
    groups: dict[str, list[ErrorDetail]] = {}
    for error in errors:
        prefix = re.split(r"[.\[]", error.path, maxsplit=1)[0]
        groups.setdefault(prefix, []).append(error)
    return {k: tuple(v) for k, v in groups.items()}


def count_errors(
    errors: tuple[ErrorDetail, ...],
) -> dict[str, int]:
    """Count errors per top-level path prefix.

    Args:
        errors: Tuple of ErrorDetail objects (from ``explain()``).

    Returns:
        A dict mapping path prefix to the number of errors under it.
    """
    prefix_counter: Counter[str] = Counter()
    for error in errors:
        prefix = re.split(r"[.\[]", error.path, maxsplit=1)[0]
        prefix_counter[prefix] += 1
    return dict(prefix_counter)
