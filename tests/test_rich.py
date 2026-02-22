"""Tests for Rich terminal output."""

from __future__ import annotations

from io import StringIO

import karva
from rich.console import Console

from pydantic_explain import FormatOptions, format_errors_rich
from tests.conftest import Constrained, User, make_validation_error


def _capture_rich(error, **kwargs) -> str:
    buf = StringIO()
    console = Console(file=buf, force_terminal=True, width=120)
    format_errors_rich(error, console=console, **kwargs)
    return buf.getvalue()


def test_rich_header():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="\x1b[1;31mValidation failed\x1b[0m for User with 1 error\n\n\x1b[1;36m  name\x1b[0m\n    Field required\n    Got: \x1b[33m(missing)\x1b[0m\n",
    )


def test_rich_field_path():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="\x1b[1;31mValidation failed\x1b[0m for User with 1 error\n\n\x1b[1;36m  name\x1b[0m\n    Field required\n    Got: \x1b[33m(missing)\x1b[0m\n",
    )


def test_rich_message():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="\x1b[1;31mValidation failed\x1b[0m for User with 1 error\n\n\x1b[1;36m  name\x1b[0m\n    Field required\n    Got: \x1b[33m(missing)\x1b[0m\n",
    )


def test_rich_show_input_default():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="\x1b[1;31mValidation failed\x1b[0m for User with 1 error\n\n\x1b[1;36m  name\x1b[0m\n    Field required\n    Got: \x1b[33m(missing)\x1b[0m\n",
    )


def test_rich_show_input_false():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error, options=FormatOptions(show_input=False))
    karva.assert_snapshot(
        output,
        inline="\x1b[1;31mValidation failed\x1b[0m for User with 1 error\n\n\x1b[1;36m  name\x1b[0m\n    Field required\n",
    )


def test_rich_show_error_type():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error, options=FormatOptions(show_error_type=True))
    karva.assert_snapshot(
        output,
        inline="\x1b[1;31mValidation failed\x1b[0m for User with 1 error\n\n\x1b[1;36m  name\x1b[0m\n    Field required \x1b[2m[missing]\x1b[0m\n    Got: \x1b[33m(missing)\x1b[0m\n",
    )


def test_rich_show_url():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error, options=FormatOptions(show_url=True))
    karva.assert_snapshot(
        output,
        inline="\x1b[1;31mValidation failed\x1b[0m for User with 1 error\n\n\x1b[1;36m  name\x1b[0m\n    Field required\n    Got: \x1b[33m(missing)\x1b[0m\n    See: \x1b[4;34mhttps://errors.pydantic.dev/2.12/v/missing\x1b[0m\n",
    )


def test_rich_multiple_errors():
    error = make_validation_error(User, {"addresses": []})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="\x1b[1;31mValidation failed\x1b[0m for User with 3 errors\n\n\x1b[1;36m  name\x1b[0m\n    Field required\n    Got: \x1b[33m(missing)\x1b[0m\n\n\x1b[1;36m  age\x1b[0m\n    Field required\n    Got: \x1b[33m(missing)\x1b[0m\n\n\x1b[1;36m  email\x1b[0m\n    Field required\n    Got: \x1b[33m(missing)\x1b[0m\n",
    )


def test_rich_nested_path():
    error = make_validation_error(
        User,
        {
            "name": "Alice",
            "age": 30,
            "email": "a@b.com",
            "addresses": [{"street": "x", "city": "y"}],
        },
    )
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="\x1b[1;31mValidation failed\x1b[0m for User with 1 error\n\n\x1b[1;36m  addresses[0].zipcode\x1b[0m\n    Field required\n    Got: \x1b[33m(missing)\x1b[0m\n",
    )


def test_rich_non_missing_input():
    error = make_validation_error(Constrained, {"value": -1})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="\x1b[1;31mValidation failed\x1b[0m for Constrained with 1 error\n\n\x1b[1;36m  value\x1b[0m\n    Input should be greater than 0\n    Got: \x1b[33m-1\x1b[0m\n",
    )


def test_rich_all_options():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(
        error,
        options=FormatOptions(show_input=True, show_url=True, show_error_type=True),
    )
    karva.assert_snapshot(
        output,
        inline="\x1b[1;31mValidation failed\x1b[0m for User with 1 error\n\n\x1b[1;36m  name\x1b[0m\n    Field required \x1b[2m[missing]\x1b[0m\n    Got: \x1b[33m(missing)\x1b[0m\n    See: \x1b[4;34mhttps://errors.pydantic.dev/2.12/v/missing\x1b[0m\n",
    )
