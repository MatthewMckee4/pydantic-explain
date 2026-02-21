"""Tests for error filtering and grouping helpers."""

from __future__ import annotations

from pydantic_explain import count_errors, explain, filter_errors, group_errors
from tests.conftest import User, make_validation_error


def _get_user_errors():
    error = make_validation_error(
        User,
        {
            "addresses": [
                {"street": "x", "city": "y"},
                {"street": "a", "city": "b"},
            ],
        },
    )
    return explain(error)


def test_filter_by_error_type():
    errors = _get_user_errors()
    result = filter_errors(errors, error_type="missing")
    assert all(e.error_type == "missing" for e in result)
    assert len(result) == len(errors)


def test_filter_by_error_type_no_match():
    errors = _get_user_errors()
    result = filter_errors(errors, error_type="int_parsing")
    assert len(result) == 0


def test_filter_by_path_pattern():
    errors = _get_user_errors()
    result = filter_errors(errors, path_pattern=r"^addresses")
    assert all(e.path.startswith("addresses") for e in result)


def test_filter_by_path_pattern_specific():
    errors = _get_user_errors()
    result = filter_errors(errors, path_pattern=r"addresses\[0\]")
    assert all("addresses[0]" in e.path for e in result)


def test_filter_combined():
    errors = _get_user_errors()
    result = filter_errors(errors, error_type="missing", path_pattern=r"^name$")
    assert len(result) == 1
    assert result[0].path == "name"


def test_filter_no_criteria():
    errors = _get_user_errors()
    result = filter_errors(errors)
    assert result == errors


def test_group_errors():
    errors = _get_user_errors()
    groups = group_errors(errors)
    assert "name" in groups
    assert "age" in groups
    assert "email" in groups
    assert "addresses" in groups
    assert len(groups["addresses"]) == 2


def test_group_errors_single_field():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    errors = explain(error)
    groups = group_errors(errors)
    assert set(groups.keys()) == {"name"}
    assert len(groups["name"]) == 1


def test_count_errors():
    errors = _get_user_errors()
    counts = count_errors(errors)
    assert counts["name"] == 1
    assert counts["age"] == 1
    assert counts["email"] == 1
    assert counts["addresses"] == 2


def test_count_errors_single():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    errors = explain(error)
    counts = count_errors(errors)
    assert counts == {"name": 1}


def test_group_errors_empty():
    groups = group_errors(())
    assert groups == {}


def test_count_errors_empty():
    counts = count_errors(())
    assert counts == {}


def test_filter_errors_empty():
    result = filter_errors((), error_type="missing")
    assert result == ()
