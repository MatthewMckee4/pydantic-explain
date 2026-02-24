"""Tests for error filtering and grouping helpers."""

from __future__ import annotations

import karva

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
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "missing",
            "input_value": {
              "city": "y",
              "street": "x"
            },
            "message": "Field required",
            "path": "addresses[0].zipcode",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          },
          {
            "error_type": "missing",
            "input_value": {
              "city": "b",
              "street": "a"
            },
            "message": "Field required",
            "path": "addresses[1].zipcode",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_filter_by_path_pattern_specific():
    errors = _get_user_errors()
    result = filter_errors(errors, path_pattern=r"addresses\[0\]")
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "missing",
            "input_value": {
              "city": "y",
              "street": "x"
            },
            "message": "Field required",
            "path": "addresses[0].zipcode",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_filter_combined():
    errors = _get_user_errors()
    result = filter_errors(errors, error_type="missing", path_pattern=r"^name$")
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "missing",
            "input_value": {
              "addresses": [
                {
                  "city": "y",
                  "street": "x"
                },
                {
                  "city": "b",
                  "street": "a"
                }
              ]
            },
            "message": "Field required",
            "path": "name",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_filter_no_criteria():
    errors = _get_user_errors()
    result = filter_errors(errors)
    assert result == errors


def test_group_errors():
    errors = _get_user_errors()
    groups = group_errors(errors)
    karva.assert_json_snapshot(
        {k: [d.to_dict() for d in v] for k, v in groups.items()},
        inline="""\
        {
          "addresses": [
            {
              "error_type": "missing",
              "input_value": {
                "city": "y",
                "street": "x"
              },
              "message": "Field required",
              "path": "addresses[0].zipcode",
              "url": "https://errors.pydantic.dev/VERSION/v/missing"
            },
            {
              "error_type": "missing",
              "input_value": {
                "city": "b",
                "street": "a"
              },
              "message": "Field required",
              "path": "addresses[1].zipcode",
              "url": "https://errors.pydantic.dev/VERSION/v/missing"
            }
          ],
          "age": [
            {
              "error_type": "missing",
              "input_value": {
                "addresses": [
                  {
                    "city": "y",
                    "street": "x"
                  },
                  {
                    "city": "b",
                    "street": "a"
                  }
                ]
              },
              "message": "Field required",
              "path": "age",
              "url": "https://errors.pydantic.dev/VERSION/v/missing"
            }
          ],
          "email": [
            {
              "error_type": "missing",
              "input_value": {
                "addresses": [
                  {
                    "city": "y",
                    "street": "x"
                  },
                  {
                    "city": "b",
                    "street": "a"
                  }
                ]
              },
              "message": "Field required",
              "path": "email",
              "url": "https://errors.pydantic.dev/VERSION/v/missing"
            }
          ],
          "name": [
            {
              "error_type": "missing",
              "input_value": {
                "addresses": [
                  {
                    "city": "y",
                    "street": "x"
                  },
                  {
                    "city": "b",
                    "street": "a"
                  }
                ]
              },
              "message": "Field required",
              "path": "name",
              "url": "https://errors.pydantic.dev/VERSION/v/missing"
            }
          ]
        }
        """,
    )


def test_group_errors_single_field():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    errors = explain(error)
    groups = group_errors(errors)
    karva.assert_json_snapshot(
        {k: [d.to_dict() for d in v] for k, v in groups.items()},
        inline="""\
        {
          "name": [
            {
              "error_type": "missing",
              "input_value": {
                "addresses": [],
                "age": 30,
                "email": "a@b.com"
              },
              "message": "Field required",
              "path": "name",
              "url": "https://errors.pydantic.dev/VERSION/v/missing"
            }
          ]
        }
        """,
    )


def test_count_errors():
    errors = _get_user_errors()
    counts = count_errors(errors)
    karva.assert_json_snapshot(
        counts,
        inline="""\
        {
          "addresses": 2,
          "age": 1,
          "email": 1,
          "name": 1
        }
        """,
    )


def test_count_errors_single():
    error = make_validation_error(User, {"age": 30, "email": "a@b.com", "addresses": []})
    errors = explain(error)
    counts = count_errors(errors)
    karva.assert_json_snapshot(
        counts,
        inline="""\
        {
          "name": 1
        }
        """,
    )


def test_group_errors_empty():
    groups = group_errors(())
    assert groups == {}


def test_count_errors_empty():
    counts = count_errors(())
    assert counts == {}


def test_filter_errors_empty():
    result = filter_errors((), error_type="missing")
    assert result == ()
