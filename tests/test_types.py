"""Tests for core types."""

from __future__ import annotations

import dataclasses

import karva

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
    karva.assert_snapshot(
        repr(detail),
        inline="ErrorDetail(path='x', message='m', error_type='t', input_value=1, context={}, url='')",
    )


def test_format_options_defaults():
    opts = FormatOptions()
    karva.assert_json_snapshot(
        dataclasses.asdict(opts),
        inline="""\
        {
          "input_max_length": 80,
          "show_error_type": false,
          "show_input": true,
          "show_url": false
        }
    """,
    )


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
    karva.assert_json_snapshot(
        dataclasses.asdict(opts),
        inline="""\
        {
          "input_max_length": 40,
          "show_error_type": true,
          "show_input": false,
          "show_url": true
        }
    """,
    )


def test_to_dict_all_fields():
    detail = ErrorDetail(
        path="name",
        message="Field required",
        error_type="missing",
        input_value="bad",
        context={"gt": 0},
        url="https://errors.pydantic.dev/2/v/missing",
    )
    karva.assert_json_snapshot(
        detail.to_dict(),
        inline="""\
        {
          "context": {
            "gt": 0
          },
          "error_type": "missing",
          "input_value": "bad",
          "message": "Field required",
          "path": "name",
          "url": "https://errors.pydantic.dev/2/v/missing"
        }
    """,
    )


def test_to_dict_omits_empty_fields():
    detail = ErrorDetail(
        path="age",
        message="Field required",
        error_type="missing",
        input_value=None,
        context={},
        url="",
    )
    karva.assert_json_snapshot(
        detail.to_dict(),
        inline="""\
        {
          "error_type": "missing",
          "message": "Field required",
          "path": "age"
        }
    """,
    )


def test_to_dict_keeps_falsy_input_value():
    detail = ErrorDetail(
        path="count",
        message="Value error",
        error_type="value_error",
        input_value=0,
        context={},
        url="",
    )
    karva.assert_json_snapshot(
        detail.to_dict(),
        inline="""\
        {
          "error_type": "value_error",
          "input_value": 0,
          "message": "Value error",
          "path": "count"
        }
    """,
    )


def test_to_dict_partial_empty():
    detail = ErrorDetail(
        path="x",
        message="m",
        error_type="t",
        input_value=None,
        context={"limit": 10},
        url="",
    )
    karva.assert_json_snapshot(
        detail.to_dict(),
        inline="""\
        {
          "context": {
            "limit": 10
          },
          "error_type": "t",
          "message": "m",
          "path": "x"
        }
    """,
    )
