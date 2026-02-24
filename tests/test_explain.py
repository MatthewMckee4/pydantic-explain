"""Tests for the explain function."""

from __future__ import annotations

import karva

from pydantic_explain import explain
from pydantic_explain._explain import _format_loc
from tests.conftest import (
    Constrained,
    Outer,
    UnionFields,
    User,
    Validated,
    make_validation_error,
)


def test_format_loc_string_only():
    karva.assert_snapshot(_format_loc(("a", "b", "c")), inline="")


def test_format_loc_int_index():
    karva.assert_snapshot(_format_loc(("a", 0)), inline="")


def test_format_loc_mixed():
    karva.assert_snapshot(_format_loc(("a", 0, "b", 1, "c")), inline="")


def test_format_loc_single_string():
    karva.assert_snapshot(_format_loc(("name",)), inline="")


def test_format_loc_single_int():
    karva.assert_snapshot(_format_loc((0,)), inline="")


def test_format_loc_empty():
    karva.assert_snapshot(_format_loc(()), inline="")


def test_format_loc_all_marker():
    karva.assert_snapshot(_format_loc(("items", "__all__", "x")), inline="")


def test_explain_returns_tuple():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = explain(error)
    assert isinstance(result, tuple)


def test_explain_single_missing_field():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
    """,
    )


def test_explain_multiple_errors():
    error = make_validation_error(User, {"addresses": []})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
    """,
    )


def test_explain_nested_path():
    error = make_validation_error(
        User,
        {
            "name": "Alice",
            "age": 30,
            "email": "a@b.com",
            "addresses": [{"street": "x", "city": "y"}],
        },
    )
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
    """,
    )


def test_explain_list_index_path():
    error = make_validation_error(
        User,
        {
            "name": "Alice",
            "age": 30,
            "email": "a@b.com",
            "addresses": [
                {"street": "x", "city": "y", "zipcode": "z"},
                {"street": "x", "city": "y", "zipcode": ["bad"]},
            ],
        },
    )
    result = explain(error)
    paths = {d.path for d in result}
    assert "addresses[1].zipcode" in paths


def test_explain_error_type_preserved():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = explain(error)
    assert result[0].error_type == "missing"


def test_explain_url_preserved():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = explain(error)
    assert result[0].url  # non-empty URL


def test_explain_context_present():
    error = make_validation_error(Constrained, {"value": -1})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
    """,
    )


def test_explain_context_absent():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = explain(error)
    assert result[0].context == {}


def test_explain_preserves_input_value():
    error = make_validation_error(
        User,
        {
            "name": "Alice",
            "age": 30,
            "email": "a@b.com",
            "addresses": [
                {"street": "x", "city": "y", "zipcode": ["bad"]},
            ],
        },
    )
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
    """,
    )


def test_explain_is_immutable():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = explain(error)
    try:
        result[0].path = "other"  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("ErrorDetail should be frozen")


def test_explain_deep_nesting():
    error = make_validation_error(Outer, {"middle": {"inner": {"code": 123}}})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
    """,
    )


def test_explain_union_type_error():
    error = make_validation_error(UnionFields, {"value": [], "tag": "ok"})
    result = explain(error)
    assert len(result) >= 1
    paths = {d.path for d in result}
    assert any(p.startswith("value") for p in paths)


def test_explain_custom_validator():
    error = make_validation_error(Validated, {"username": "bad user!"})
    result = explain(error)
    assert len(result) == 1
    assert result[0].path == "username"
    assert "alphanumeric" in result[0].message
