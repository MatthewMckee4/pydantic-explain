"""Tests for the explain function."""

from __future__ import annotations

from pydantic_explain import explain
from pydantic_explain._explain import _format_loc
from tests.conftest import Constrained, User, make_validation_error

# --- _format_loc tests ---


def test_format_loc_string_only():
    assert _format_loc(("a", "b", "c")) == "a.b.c"


def test_format_loc_int_index():
    assert _format_loc(("a", 0)) == "a[0]"


def test_format_loc_mixed():
    assert _format_loc(("a", 0, "b", 1, "c")) == "a[0].b[1].c"


def test_format_loc_single_string():
    assert _format_loc(("name",)) == "name"


def test_format_loc_single_int():
    assert _format_loc((0,)) == "[0]"


def test_format_loc_empty():
    assert _format_loc(()) == "<root>"


def test_format_loc_all_marker():
    assert _format_loc(("items", "__all__", "x")) == "items[*].x"


# --- explain tests ---


def test_explain_returns_tuple():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = explain(error)
    assert isinstance(result, tuple)


def test_explain_single_missing_field():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = explain(error)
    assert len(result) == 1
    detail = result[0]
    assert detail.path == "name"
    assert detail.error_type == "missing"
    assert detail.message == "Field required"


def test_explain_multiple_errors():
    error = make_validation_error(User, {"addresses": []})
    result = explain(error)
    assert len(result) == 3
    paths = {d.path for d in result}
    assert paths == {"name", "age", "email"}


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
    assert len(result) == 1
    assert result[0].path == "addresses[0].zipcode"


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
    assert len(result) == 1
    assert result[0].context.get("gt") == 0


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
    assert result[0].input_value == ["bad"]


def test_explain_is_immutable():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = explain(error)
    try:
        result[0].path = "other"  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("ErrorDetail should be frozen")
