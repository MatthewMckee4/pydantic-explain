"""Tests for the public API surface."""

from __future__ import annotations

import pydantic_errors


def test_all_exports():
    assert set(pydantic_errors.__all__) == {
        "ErrorDetail",
        "FormatOptions",
        "explain",
        "format_error_detail",
        "format_errors",
    }


def test_importable():
    from pydantic_errors import (
        ErrorDetail,
        FormatOptions,
        explain,
        format_error_detail,
        format_errors,
    )

    assert ErrorDetail is not None
    assert FormatOptions is not None
    assert explain is not None
    assert format_error_detail is not None
    assert format_errors is not None


def test_no_private_leaks():
    public = {name for name in dir(pydantic_errors) if not name.startswith("_")}
    expected = set(pydantic_errors.__all__)
    # All __all__ exports should be in dir()
    assert expected <= public
