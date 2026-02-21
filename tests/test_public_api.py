"""Tests for the public API surface."""

from __future__ import annotations

import pydantic_explain


def test_all_exports():
    assert set(pydantic_explain.__all__) == {
        "ErrorDetail",
        "FormatOptions",
        "explain",
        "format_error_detail",
        "format_errors",
        "format_errors_rich",
    }


def test_importable():
    from pydantic_explain import (
        ErrorDetail,
        FormatOptions,
        explain,
        format_error_detail,
        format_errors,
        format_errors_rich,
    )

    assert ErrorDetail is not None
    assert FormatOptions is not None
    assert explain is not None
    assert format_error_detail is not None
    assert format_errors is not None
    assert format_errors_rich is not None


def test_no_private_leaks():
    public = {name for name in dir(pydantic_explain) if not name.startswith("_")}
    expected = set(pydantic_explain.__all__)
    # All __all__ exports should be in dir()
    assert expected <= public
