"""Tests for Rich terminal output."""

from __future__ import annotations

from io import StringIO

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
    assert "Validation failed" in output
    assert "User" in output
    assert "1 error" in output


def test_rich_field_path():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error)
    assert "name" in output


def test_rich_message():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error)
    assert "Field required" in output


def test_rich_show_input_default():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error)
    assert "Got:" in output
    assert "(missing)" in output


def test_rich_show_input_false():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error, options=FormatOptions(show_input=False))
    assert "Got:" not in output


def test_rich_show_error_type():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error, options=FormatOptions(show_error_type=True))
    assert "[missing]" in output


def test_rich_show_url():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error, options=FormatOptions(show_url=True))
    assert "See:" in output


def test_rich_multiple_errors():
    error = make_validation_error(User, {"addresses": []})
    output = _capture_rich(error)
    assert "3 errors" in output
    assert "name" in output
    assert "age" in output
    assert "email" in output


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
    assert "addresses[0].zipcode" in output


def test_rich_non_missing_input():
    error = make_validation_error(Constrained, {"value": -1})
    output = _capture_rich(error)
    assert "Got:" in output
    assert "-1" in output


def test_rich_all_options():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(
        error,
        options=FormatOptions(show_input=True, show_url=True, show_error_type=True),
    )
    assert "Got:" in output
    assert "See:" in output
    assert "[missing]" in output
