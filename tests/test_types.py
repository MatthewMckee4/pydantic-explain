"""Tests for core types."""

from __future__ import annotations

from pydantic_explain import ErrorDetail, FormatOptions


def test_error_detail_frozen():
    detail = ErrorDetail(
        path="name",
        message="Field required",
        error_type="missing",
        input_value=None,
        context={},
        url="",
    )
    try:
        detail.path = "other"  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("ErrorDetail should be frozen")


def test_error_detail_slots():
    assert hasattr(ErrorDetail, "__slots__")


def test_error_detail_equality():
    d1 = ErrorDetail(path="x", message="m", error_type="t", input_value=1, context={}, url="")
    d2 = ErrorDetail(path="x", message="m", error_type="t", input_value=1, context={}, url="")
    assert d1 == d2


def test_error_detail_repr():
    detail = ErrorDetail(path="x", message="m", error_type="t", input_value=1, context={}, url="")
    r = repr(detail)
    assert "ErrorDetail" in r
    assert "path='x'" in r


def test_format_options_defaults():
    opts = FormatOptions()
    assert opts.show_input is True
    assert opts.show_url is False
    assert opts.show_error_type is False
    assert opts.input_max_length == 80


def test_format_options_frozen():
    opts = FormatOptions()
    try:
        opts.show_input = False  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("FormatOptions should be frozen")


def test_format_options_custom():
    opts = FormatOptions(show_input=False, show_url=True, show_error_type=True, input_max_length=40)
    assert opts.show_input is False
    assert opts.show_url is True
    assert opts.show_error_type is True
    assert opts.input_max_length == 40


def test_to_dict_all_fields():
    detail = ErrorDetail(
        path="name",
        message="Field required",
        error_type="missing",
        input_value="bad",
        context={"gt": 0},
        url="https://errors.pydantic.dev/2/v/missing",
    )
    d = detail.to_dict()
    assert d == {
        "path": "name",
        "message": "Field required",
        "error_type": "missing",
        "input_value": "bad",
        "context": {"gt": 0},
        "url": "https://errors.pydantic.dev/2/v/missing",
    }


def test_to_dict_omits_empty_fields():
    detail = ErrorDetail(
        path="age",
        message="Field required",
        error_type="missing",
        input_value=None,
        context={},
        url="",
    )
    d = detail.to_dict()
    assert d == {
        "path": "age",
        "message": "Field required",
        "error_type": "missing",
    }
    assert "input_value" not in d
    assert "context" not in d
    assert "url" not in d


def test_to_dict_keeps_falsy_input_value():
    detail = ErrorDetail(
        path="count",
        message="Value error",
        error_type="value_error",
        input_value=0,
        context={},
        url="",
    )
    d = detail.to_dict()
    assert d["input_value"] == 0


def test_to_dict_partial_empty():
    detail = ErrorDetail(
        path="x",
        message="m",
        error_type="t",
        input_value=None,
        context={"limit": 10},
        url="",
    )
    d = detail.to_dict()
    assert "context" in d
    assert "input_value" not in d
    assert "url" not in d
