"""Tests for the formatting functions."""

from __future__ import annotations

import karva

from pydantic_explain import ErrorDetail, FormatOptions, format_error_detail, format_errors
from pydantic_explain._format import _truncate_repr
from tests.conftest import User, make_validation_error


def test_format_errors_header():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          name
            Field required
            Got: (missing)
        """,
    )


def test_format_errors_singular_error_count():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          name
            Field required
            Got: (missing)
        """,
    )


def test_format_errors_plural_error_count():
    error = make_validation_error(User, {"addresses": []})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 3 errors

          name
            Field required
            Got: (missing)

          age
            Field required
            Got: (missing)

          email
            Field required
            Got: (missing)
        """,
    )


def test_format_errors_single_error():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          name
            Field required
            Got: (missing)
        """,
    )


def test_format_errors_multiple_errors():
    error = make_validation_error(User, {"addresses": []})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 3 errors

          name
            Field required
            Got: (missing)

          age
            Field required
            Got: (missing)

          email
            Field required
            Got: (missing)
        """,
    )


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
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          addresses[0].zipcode
            Field required
            Got: (missing)
        """,
    )


def test_format_errors_show_input_true():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          name
            Field required
            Got: (missing)
        """,
    )


def test_format_errors_show_input_false():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error, options=FormatOptions(show_input=False))
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          name
            Field required
        """,
    )


def test_format_errors_show_url():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error, options=FormatOptions(show_url=True))
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          name
            Field required
            Got: (missing)
            See: https://errors.pydantic.dev/VERSION/v/missing
        """,
    )


def test_format_errors_show_error_type():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error, options=FormatOptions(show_error_type=True))
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          name
            Field required [missing]
            Got: (missing)
        """,
    )


def test_format_errors_missing_input_display():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          name
            Field required
            Got: (missing)
        """,
    )


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
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          name
            Field required
            Got: (missing)
        """,
    )


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
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          addresses[0].zipcode
            Input should be a valid string
            Got: ["<script>alert('xss')</script>"]
        """,
    )


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
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 1 error

          addresses[0].zipcode
            Field required
            Got: (missing)
        """,
    )


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


def test_truncate_repr_short():
    karva.assert_snapshot(_truncate_repr("hello", 80), inline="'hello'")


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
    karva.assert_snapshot(_truncate_repr(42, 80), inline="42")


def test_truncate_repr_empty_string():
    karva.assert_snapshot(_truncate_repr("", 80), inline="''")


def test_truncate_repr_unicode():
    result = _truncate_repr("cafe\u0301", 80)
    assert "caf" in result


def test_truncate_repr_custom_repr():
    class Custom:
        def __repr__(self) -> str:
            return "CustomRepr(x=1)"

    karva.assert_snapshot(_truncate_repr(Custom(), 80), inline="CustomRepr(x=1)")


def test_truncate_repr_custom_repr_over_limit():
    class Verbose:
        def __repr__(self) -> str:
            return "V" * 200

    result = _truncate_repr(Verbose(), 80)
    assert len(result) == 80
    assert result.endswith("...")


def test_format_error_detail_all_options_enabled():
    detail = ErrorDetail(
        path="age",
        message="Input should be a valid integer",
        error_type="int_parsing",
        input_value="abc",
        context={},
        url="https://errors.pydantic.dev/2/v/int_parsing",
    )
    result = format_error_detail(
        detail,
        options=FormatOptions(show_input=True, show_url=True, show_error_type=True),
    )
    assert "  age" in result
    assert "[int_parsing]" in result
    assert "Got: 'abc'" in result
    assert "See: https://errors.pydantic.dev/2/v/int_parsing" in result


def test_format_error_detail_no_options_enabled():
    detail = ErrorDetail(
        path="name",
        message="Field required",
        error_type="missing",
        input_value={"age": 30},
        context={},
        url="https://errors.pydantic.dev/2/v/missing",
    )
    result = format_error_detail(
        detail,
        options=FormatOptions(show_input=False, show_url=False, show_error_type=False),
    )
    assert "  name" in result
    assert "Field required" in result
    assert "Got:" not in result
    assert "See:" not in result
    assert "[missing]" not in result
