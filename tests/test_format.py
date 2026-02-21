"""Tests for the formatting functions."""

from __future__ import annotations

from pydantic_errors import ErrorDetail, FormatOptions, format_error_detail, format_errors
from pydantic_errors._format import _truncate_repr
from tests.conftest import User, make_validation_error

# --- format_errors tests ---


def test_format_errors_header():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error)
    assert result.startswith("Validation failed for User with 1 error")


def test_format_errors_singular_error_count():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error)
    assert "1 error" in result
    assert "1 errors" not in result


def test_format_errors_plural_error_count():
    error = make_validation_error(User, {"addresses": []})
    result = format_errors(error)
    assert "3 errors" in result


def test_format_errors_single_error():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error)
    assert "name" in result
    assert "Field required" in result


def test_format_errors_multiple_errors():
    error = make_validation_error(User, {"addresses": []})
    result = format_errors(error)
    assert "name" in result
    assert "age" in result
    assert "email" in result


def test_format_errors_nested():
    error = make_validation_error(
        User,
        {
            "name": "Alice",
            "age": 30,
            "email": "a@b.com",
            "addresses": [{"street": "x", "city": "y"}],
        },
    )
    result = format_errors(error)
    assert "addresses[0].zipcode" in result


def test_format_errors_show_input_true():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error)
    assert "Got:" in result


def test_format_errors_show_input_false():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error, options=FormatOptions(show_input=False))
    assert "Got:" not in result


def test_format_errors_show_url():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error, options=FormatOptions(show_url=True))
    assert "See:" in result


def test_format_errors_show_error_type():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error, options=FormatOptions(show_error_type=True))
    assert "[missing]" in result


def test_format_errors_missing_input_display():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error)
    assert "Got: (missing)" in result


def test_format_errors_none_input():
    detail = ErrorDetail(
        path="name",
        message="Input should be a valid string",
        error_type="string_type",
        input_value=None,
        context={},
        url="",
    )
    result = format_error_detail(detail)
    assert "Got: None" in result


def test_format_errors_default_options():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error)
    # Default: show_input=True, show_url=False, show_error_type=False
    assert "Got:" in result
    assert "See:" not in result
    assert "[missing]" not in result


def test_format_errors_special_characters_in_input():
    error = make_validation_error(
        User,
        {
            "name": "Alice",
            "age": 30,
            "email": "a@b.com",
            "addresses": [
                {"street": "x", "city": "y", "zipcode": ["<script>alert('xss')</script>"]},
            ],
        },
    )
    result = format_errors(error)
    assert "Got:" in result


def test_format_errors_very_long_path():
    error = make_validation_error(
        User,
        {
            "name": "Alice",
            "age": 30,
            "email": "a@b.com",
            "addresses": [{"street": "x", "city": "y"}],
        },
    )
    result = format_errors(error)
    assert "addresses[0].zipcode" in result


# --- format_error_detail tests ---


def test_format_error_detail_single():
    detail = ErrorDetail(
        path="name",
        message="Field required",
        error_type="missing",
        input_value={"age": 30},
        context={},
        url="https://errors.pydantic.dev/2/v/missing",
    )
    result = format_error_detail(detail)
    assert "  name" in result
    assert "    Field required" in result
    assert "    Got: (missing)" in result


def test_format_error_detail_with_url():
    detail = ErrorDetail(
        path="age",
        message="Input should be a valid integer",
        error_type="int_parsing",
        input_value="abc",
        context={},
        url="https://errors.pydantic.dev/2/v/int_parsing",
    )
    result = format_error_detail(detail, options=FormatOptions(show_url=True))
    assert "See: https://errors.pydantic.dev/2/v/int_parsing" in result


def test_format_error_detail_with_error_type():
    detail = ErrorDetail(
        path="age",
        message="Input should be a valid integer",
        error_type="int_parsing",
        input_value="abc",
        context={},
        url="",
    )
    result = format_error_detail(detail, options=FormatOptions(show_error_type=True))
    assert "[int_parsing]" in result


# --- _truncate_repr tests ---


def test_truncate_repr_short():
    assert _truncate_repr("hello", 80) == "'hello'"


def test_truncate_repr_exact_limit():
    value = "x" * 78  # repr adds quotes: 'xxx...xxx' = 80 chars
    result = _truncate_repr(value, 80)
    assert len(result) == 80


def test_truncate_repr_over_limit():
    value = "x" * 200
    result = _truncate_repr(value, 80)
    assert len(result) == 80
    assert result.endswith("...")


def test_truncate_repr_under_limit():
    result = _truncate_repr(42, 80)
    assert result == "42"
