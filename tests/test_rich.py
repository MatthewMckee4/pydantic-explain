"""Tests for Rich terminal output."""

from __future__ import annotations

import re
from io import StringIO

import karva
from rich.console import Console

from pydantic_explain import FormatOptions, format_errors_rich
from tests.conftest import Constrained, User, make_validation_error

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _capture_rich(error, **kwargs) -> str:
    """Capture Rich output with ANSI escape codes stripped."""
    buf = StringIO()
    console = Console(file=buf, force_terminal=True, width=120)
    format_errors_rich(error, console=console, **kwargs)
    return _ANSI_RE.sub("", buf.getvalue())


def test_rich_header():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="""\
    """,
    )


def test_rich_field_path():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="""\
    """,
    )


def test_rich_message():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="""\
    """,
    )


def test_rich_show_input_default():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="""\
    """,
    )


def test_rich_show_input_false():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error, options=FormatOptions(show_input=False))
    karva.assert_snapshot(
        output,
        inline="""\
    """,
    )


def test_rich_show_error_type():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error, options=FormatOptions(show_error_type=True))
    karva.assert_snapshot(
        output,
        inline="""\
    """,
    )


def test_rich_show_url():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(error, options=FormatOptions(show_url=True))
    karva.assert_snapshot(
        output,
        inline="""\
    """,
    )


def test_rich_multiple_errors():
    error = make_validation_error(User, {"addresses": []})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="""\
    """,
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
        inline="""\
    """,
    )


def test_rich_non_missing_input():
    error = make_validation_error(Constrained, {"value": -1})
    output = _capture_rich(error)
    karva.assert_snapshot(
        output,
        inline="""\
    """,
    )


def test_rich_all_options():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    output = _capture_rich(
        error,
        options=FormatOptions(show_input=True, show_url=True, show_error_type=True),
    )
    karva.assert_snapshot(
        output,
        inline="""\
    """,
    )
