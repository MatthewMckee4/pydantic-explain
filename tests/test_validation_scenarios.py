"""Comprehensive tests for diverse Pydantic validation scenarios.

Covers error types, model configurations, and edge cases not exercised by other tests.
"""

from __future__ import annotations

import re
from io import StringIO

import karva
from rich.console import Console

from pydantic_explain import (
    FormatOptions,
    count_errors,
    explain,
    filter_errors,
    format_errors,
    format_errors_rich,
)
from tests.conftest import (
    AliasModel,
    DateTimeModel,
    DictModel,
    EnumModel,
    ExtraForbid,
    Level0,
    ListConstrained,
    LiteralModel,
    MixedErrorModel,
    ModelValidated,
    MultiFieldValidated,
    NestedListModel,
    NumericConstrained,
    Outer,
    PatternConstrained,
    SetModel,
    StrictModel,
    StringConstrained,
    TupleModel,
    User,
    make_validation_error,
)

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _capture_rich(error, **kwargs) -> str:
    buf = StringIO()
    console = Console(file=buf, force_terminal=True, width=120)
    format_errors_rich(error, console=console, **kwargs)
    return _ANSI_RE.sub("", buf.getvalue())


def test_explain_extra_forbidden():
    error = make_validation_error(ExtraForbid, {"name": "Alice", "unknown": 1})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "extra_forbidden",
            "input_value": 1,
            "message": "Extra inputs are not permitted",
            "path": "unknown",
            "url": "https://errors.pydantic.dev/VERSION/v/extra_forbidden"
          }
        ]
        """,
    )


def test_format_extra_forbidden():
    error = make_validation_error(ExtraForbid, {"name": "Alice", "unknown": 1})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for ExtraForbid with 1 error

          unknown
            Extra inputs are not permitted
            Got: 1
        """,
    )


def test_explain_extra_forbidden_multiple():
    error = make_validation_error(ExtraForbid, {"name": "Alice", "a": 1, "b": 2})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "extra_forbidden",
            "input_value": 1,
            "message": "Extra inputs are not permitted",
            "path": "a",
            "url": "https://errors.pydantic.dev/VERSION/v/extra_forbidden"
          },
          {
            "error_type": "extra_forbidden",
            "input_value": 2,
            "message": "Extra inputs are not permitted",
            "path": "b",
            "url": "https://errors.pydantic.dev/VERSION/v/extra_forbidden"
          }
        ]
        """,
    )


def test_explain_pattern_mismatch():
    error = make_validation_error(PatternConstrained, {"code": "invalid"})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "pattern": "^[A-Z]{3}-\\\\d{3}$"
            },
            "error_type": "string_pattern_mismatch",
            "input_value": "invalid",
            "message": "String should match pattern '^[A-Z]{3}-\\\\d{3}$'",
            "path": "code",
            "url": "https://errors.pydantic.dev/VERSION/v/string_pattern_mismatch"
          }
        ]
        """,
    )


def test_format_pattern_mismatch():
    error = make_validation_error(PatternConstrained, {"code": "bad"})
    result = format_errors(error, options=FormatOptions(show_error_type=True))
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for PatternConstrained with 1 error

          code
            String should match pattern '^[A-Z]{3}-\\d{3}$' [string_pattern_mismatch]
            Got: 'bad'
        """,
    )


def test_explain_pattern_context():
    """Pattern constraint errors include the pattern in context."""
    error = make_validation_error(PatternConstrained, {"code": "nope"})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "pattern": "^[A-Z]{3}-\\\\d{3}$"
            },
            "error_type": "string_pattern_mismatch",
            "input_value": "nope",
            "message": "String should match pattern '^[A-Z]{3}-\\\\d{3}$'",
            "path": "code",
            "url": "https://errors.pydantic.dev/VERSION/v/string_pattern_mismatch"
          }
        ]
        """,
    )


def test_explain_string_too_short():
    error = make_validation_error(StringConstrained, {"short": "a"})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "min_length": 2
            },
            "error_type": "string_too_short",
            "input_value": "a",
            "message": "String should have at least 2 characters",
            "path": "short",
            "url": "https://errors.pydantic.dev/VERSION/v/string_too_short"
          }
        ]
        """,
    )


def test_explain_string_too_long():
    error = make_validation_error(StringConstrained, {"short": "abcdef"})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "max_length": 5
            },
            "error_type": "string_too_long",
            "input_value": "abcdef",
            "message": "String should have at most 5 characters",
            "path": "short",
            "url": "https://errors.pydantic.dev/VERSION/v/string_too_long"
          }
        ]
        """,
    )


def test_format_string_constraints():
    error = make_validation_error(StringConstrained, {"short": "a"})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for StringConstrained with 1 error

          short
            String should have at least 2 characters
            Got: 'a'
        """,
    )


def test_explain_less_than_ge():
    error = make_validation_error(NumericConstrained, {"score": -1, "factor": 0.5})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "ge": 0
            },
            "error_type": "greater_than_equal",
            "input_value": -1,
            "message": "Input should be greater than or equal to 0",
            "path": "score",
            "url": "https://errors.pydantic.dev/VERSION/v/greater_than_equal"
          }
        ]
        """,
    )


def test_explain_greater_than_le():
    error = make_validation_error(NumericConstrained, {"score": 101, "factor": 0.5})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "le": 100
            },
            "error_type": "less_than_equal",
            "input_value": 101,
            "message": "Input should be less than or equal to 100",
            "path": "score",
            "url": "https://errors.pydantic.dev/VERSION/v/less_than_equal"
          }
        ]
        """,
    )


def test_explain_less_than_gt():
    error = make_validation_error(NumericConstrained, {"score": 50, "factor": 0.0})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "gt": 0.0
            },
            "error_type": "greater_than",
            "input_value": 0.0,
            "message": "Input should be greater than 0",
            "path": "factor",
            "url": "https://errors.pydantic.dev/VERSION/v/greater_than"
          }
        ]
        """,
    )


def test_explain_greater_than_lt():
    error = make_validation_error(NumericConstrained, {"score": 50, "factor": 1.0})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "lt": 1.0
            },
            "error_type": "less_than",
            "input_value": 1.0,
            "message": "Input should be less than 1",
            "path": "factor",
            "url": "https://errors.pydantic.dev/VERSION/v/less_than"
          }
        ]
        """,
    )


def test_format_numeric_constraints():
    error = make_validation_error(NumericConstrained, {"score": -5, "factor": 0.5})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for NumericConstrained with 1 error

          score
            Input should be greater than or equal to 0
            Got: -5
        """,
    )


def test_explain_numeric_multiple_errors():
    """Both fields fail simultaneously."""
    error = make_validation_error(NumericConstrained, {"score": -1, "factor": 2.0})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "ge": 0
            },
            "error_type": "greater_than_equal",
            "input_value": -1,
            "message": "Input should be greater than or equal to 0",
            "path": "score",
            "url": "https://errors.pydantic.dev/VERSION/v/greater_than_equal"
          },
          {
            "context": {
              "lt": 1.0
            },
            "error_type": "less_than",
            "input_value": 2.0,
            "message": "Input should be less than 1",
            "path": "factor",
            "url": "https://errors.pydantic.dev/VERSION/v/less_than"
          }
        ]
        """,
    )


def test_explain_list_too_short():
    error = make_validation_error(ListConstrained, {"tags": []})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "actual_length": 0,
              "field_type": "List",
              "min_length": 1
            },
            "error_type": "too_short",
            "input_value": [],
            "message": "List should have at least 1 item after validation, not 0",
            "path": "tags",
            "url": "https://errors.pydantic.dev/VERSION/v/too_short"
          }
        ]
        """,
    )


def test_explain_list_too_long():
    error = make_validation_error(ListConstrained, {"tags": ["a", "b", "c", "d", "e", "f"]})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "actual_length": 6,
              "field_type": "List",
              "max_length": 5
            },
            "error_type": "too_long",
            "input_value": [
              "a",
              "b",
              "c",
              "d",
              "e",
              "f"
            ],
            "message": "List should have at most 5 items after validation, not 6",
            "path": "tags",
            "url": "https://errors.pydantic.dev/VERSION/v/too_long"
          }
        ]
        """,
    )


def test_format_list_constraint():
    error = make_validation_error(ListConstrained, {"tags": []})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for ListConstrained with 1 error

          tags
            List should have at least 1 item after validation, not 0
            Got: []
        """,
    )


def test_explain_invalid_enum():
    error = make_validation_error(EnumModel, {"color": "yellow"})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "expected": "'red', 'green' or 'blue'"
            },
            "error_type": "enum",
            "input_value": "yellow",
            "message": "Input should be 'red', 'green' or 'blue'",
            "path": "color",
            "url": "https://errors.pydantic.dev/VERSION/v/enum"
          }
        ]
        """,
    )


def test_format_invalid_enum():
    error = make_validation_error(EnumModel, {"color": "yellow"})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for EnumModel with 1 error

          color
            Input should be 'red', 'green' or 'blue'
            Got: 'yellow'
        """,
    )


def test_explain_invalid_literal_string():
    error = make_validation_error(LiteralModel, {"status": "deleted", "priority": 1})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "expected": "'active' or 'inactive'"
            },
            "error_type": "literal_error",
            "input_value": "deleted",
            "message": "Input should be 'active' or 'inactive'",
            "path": "status",
            "url": "https://errors.pydantic.dev/VERSION/v/literal_error"
          }
        ]
        """,
    )


def test_explain_invalid_literal_int():
    error = make_validation_error(LiteralModel, {"status": "active", "priority": 99})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "expected": "1, 2 or 3"
            },
            "error_type": "literal_error",
            "input_value": 99,
            "message": "Input should be 1, 2 or 3",
            "path": "priority",
            "url": "https://errors.pydantic.dev/VERSION/v/literal_error"
          }
        ]
        """,
    )


def test_explain_multiple_literal_errors():
    error = make_validation_error(LiteralModel, {"status": "deleted", "priority": 99})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "expected": "'active' or 'inactive'"
            },
            "error_type": "literal_error",
            "input_value": "deleted",
            "message": "Input should be 'active' or 'inactive'",
            "path": "status",
            "url": "https://errors.pydantic.dev/VERSION/v/literal_error"
          },
          {
            "context": {
              "expected": "1, 2 or 3"
            },
            "error_type": "literal_error",
            "input_value": 99,
            "message": "Input should be 1, 2 or 3",
            "path": "priority",
            "url": "https://errors.pydantic.dev/VERSION/v/literal_error"
          }
        ]
        """,
    )


def test_format_literal_error():
    error = make_validation_error(LiteralModel, {"status": "deleted", "priority": 1})
    result = format_errors(error, options=FormatOptions(show_error_type=True))
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for LiteralModel with 1 error

          status
            Input should be 'active' or 'inactive' [literal_error]
            Got: 'deleted'
        """,
    )


def test_explain_dict_invalid_value_type():
    error = make_validation_error(DictModel, {"metadata": {"key": "not_an_int"}})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "int_parsing",
            "input_value": "not_an_int",
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "path": "metadata.key",
            "url": "https://errors.pydantic.dev/VERSION/v/int_parsing"
          }
        ]
        """,
    )


def test_explain_dict_missing():
    error = make_validation_error(DictModel, {})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "metadata",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_format_dict_error():
    error = make_validation_error(DictModel, {"metadata": {"a": "bad"}})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for DictModel with 1 error

          metadata.a
            Input should be a valid integer, unable to parse string as an integer
            Got: 'bad'
        """,
    )


def test_explain_nested_list_type_error():
    error = make_validation_error(
        NestedListModel,
        {"matrix": [["not_int"]], "users": []},
    )
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "int_parsing",
            "input_value": "not_int",
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "path": "matrix[0][0]",
            "url": "https://errors.pydantic.dev/VERSION/v/int_parsing"
          }
        ]
        """,
    )


def test_explain_nested_list_of_models_error():
    """Errors inside models within a list show indexed paths."""
    error = make_validation_error(
        NestedListModel,
        {
            "matrix": [[1]],
            "users": [
                {
                    "name": "Alice",
                    "age": 30,
                    "email": "a@b.com",
                    "addresses": [{"street": "x", "city": "y"}],
                }
            ],
        },
    )
    result = explain(error)
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
            "path": "users[0].addresses[0].zipcode",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_format_nested_list_model():
    error = make_validation_error(
        NestedListModel,
        {"matrix": [["bad"]], "users": []},
    )
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for NestedListModel with 1 error

          matrix[0][0]
            Input should be a valid integer, unable to parse string as an integer
            Got: 'bad'
        """,
    )


def test_explain_alias_missing():
    error = make_validation_error(AliasModel, {})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "full_name",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          },
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "user_age",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_explain_alias_wrong_type():
    error = make_validation_error(AliasModel, {"full_name": 123, "user_age": "not_int"})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "string_type",
            "input_value": 123,
            "message": "Input should be a valid string",
            "path": "full_name",
            "url": "https://errors.pydantic.dev/VERSION/v/string_type"
          },
          {
            "error_type": "int_parsing",
            "input_value": "not_int",
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "path": "user_age",
            "url": "https://errors.pydantic.dev/VERSION/v/int_parsing"
          }
        ]
        """,
    )


def test_explain_invalid_date():
    error = make_validation_error(DateTimeModel, {"created": "not-a-date", "updated": "2024-01-01"})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "error": "invalid character in year"
            },
            "error_type": "date_from_datetime_parsing",
            "input_value": "not-a-date",
            "message": "Input should be a valid date or datetime, invalid character in year",
            "path": "created",
            "url": "https://errors.pydantic.dev/VERSION/v/date_from_datetime_parsing"
          }
        ]
        """,
    )


def test_explain_invalid_datetime():
    error = make_validation_error(
        DateTimeModel, {"created": "2024-01-01", "updated": "not-a-datetime"}
    )
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "error": "invalid character in year"
            },
            "error_type": "datetime_from_date_parsing",
            "input_value": "not-a-datetime",
            "message": "Input should be a valid datetime or date, invalid character in year",
            "path": "updated",
            "url": "https://errors.pydantic.dev/VERSION/v/datetime_from_date_parsing"
          }
        ]
        """,
    )


def test_format_datetime_errors():
    error = make_validation_error(DateTimeModel, {"created": "bad", "updated": "bad"})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for DateTimeModel with 2 errors

          created
            Input should be a valid date or datetime, input is too short
            Got: 'bad'

          updated
            Input should be a valid datetime or date, input is too short
            Got: 'bad'
        """,
    )


def test_explain_tuple_wrong_length():
    error = make_validation_error(TupleModel, {"point": [1], "rgb": [1, 2, 3]})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "missing",
            "input_value": [
              1
            ],
            "message": "Field required",
            "path": "point[1]",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_explain_tuple_wrong_type():
    error = make_validation_error(TupleModel, {"point": ["a", "b"], "rgb": [1, 2, 3]})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "int_parsing",
            "input_value": "a",
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "path": "point[0]",
            "url": "https://errors.pydantic.dev/VERSION/v/int_parsing"
          },
          {
            "error_type": "int_parsing",
            "input_value": "b",
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "path": "point[1]",
            "url": "https://errors.pydantic.dev/VERSION/v/int_parsing"
          }
        ]
        """,
    )


def test_explain_tuple_too_many():
    error = make_validation_error(TupleModel, {"point": [1, 2, 3, 4], "rgb": [1, 2, 3]})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "actual_length": 4,
              "field_type": "Tuple",
              "max_length": 2
            },
            "error_type": "too_long",
            "input_value": [
              1,
              2,
              3,
              4
            ],
            "message": "Tuple should have at most 2 items after validation, not 4",
            "path": "point",
            "url": "https://errors.pydantic.dev/VERSION/v/too_long"
          }
        ]
        """,
    )


def test_explain_set_wrong_item_type():
    error = make_validation_error(SetModel, {"unique_tags": [1, 2], "frozen_ids": [1]})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "string_type",
            "input_value": 1,
            "message": "Input should be a valid string",
            "path": "unique_tags[0]",
            "url": "https://errors.pydantic.dev/VERSION/v/string_type"
          },
          {
            "error_type": "string_type",
            "input_value": 2,
            "message": "Input should be a valid string",
            "path": "unique_tags[1]",
            "url": "https://errors.pydantic.dev/VERSION/v/string_type"
          }
        ]
        """,
    )


def test_explain_frozenset_wrong_item_type():
    error = make_validation_error(SetModel, {"unique_tags": ["a"], "frozen_ids": ["not_int"]})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "int_parsing",
            "input_value": "not_int",
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "path": "frozen_ids[0]",
            "url": "https://errors.pydantic.dev/VERSION/v/int_parsing"
          }
        ]
        """,
    )


def test_explain_five_level_nesting():
    error = make_validation_error(
        Level0,
        {"level1": {"level2": {"level3": {"level4": {"value": "not_int"}}}}},
    )
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "int_parsing",
            "input_value": "not_int",
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "path": "level1.level2.level3.level4.value",
            "url": "https://errors.pydantic.dev/VERSION/v/int_parsing"
          }
        ]
        """,
    )


def test_format_five_level_nesting():
    error = make_validation_error(
        Level0,
        {"level1": {"level2": {"level3": {"level4": {"value": "bad"}}}}},
    )
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for Level0 with 1 error

          level1.level2.level3.level4.value
            Input should be a valid integer, unable to parse string as an integer
            Got: 'bad'
        """,
    )


def test_explain_five_level_missing_intermediate():
    """Missing an intermediate nested object."""
    error = make_validation_error(Level0, {"level1": {"level2": {"level3": {}}}})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "level1.level2.level3.level4",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_format_model_validator():
    """Model-level validator errors render at <root> path."""
    error = make_validation_error(ModelValidated, {"password": "abc", "confirm_password": "xyz"})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for ModelValidated with 1 error

          <root>
            Value error, Passwords do not match
            Got: {'password': 'abc', 'confirm_password': 'xyz'}
        """,
    )


def test_explain_multiple_field_validators():
    """Both field validators fail simultaneously."""
    error = make_validation_error(MultiFieldValidated, {"username": "bad user!", "email": "nope"})
    result = explain(error)
    paths = {d.path for d in result}
    karva.assert_json_snapshot(
        sorted(paths),
        inline="""\
        [
          "email",
          "username"
        ]
        """,
    )


def test_explain_single_field_validator_passes():
    """Only one field validator fails."""
    error = make_validation_error(MultiFieldValidated, {"username": "gooduser", "email": "nope"})
    karva.assert_snapshot(
        format_errors(error),
        inline="""\
        Validation failed for MultiFieldValidated with 1 error

          email
            Value error, Email must contain @
            Got: 'nope'
    """,
    )


def test_explain_strict_int_from_string():
    """Strict mode rejects string-to-int coercion."""
    error = make_validation_error(StrictModel, {"count": "5", "name": "Alice", "active": True})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "int_type",
            "input_value": "5",
            "message": "Input should be a valid integer",
            "path": "count",
            "url": "https://errors.pydantic.dev/VERSION/v/int_type"
          }
        ]
        """,
    )


def test_explain_strict_bool_from_int():
    """Strict mode rejects int-to-bool coercion."""
    error = make_validation_error(StrictModel, {"count": 1, "name": "Alice", "active": 1})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "bool_type",
            "input_value": 1,
            "message": "Input should be a valid boolean",
            "path": "active",
            "url": "https://errors.pydantic.dev/VERSION/v/bool_type"
          }
        ]
        """,
    )


def test_explain_strict_multiple_coercion_failures():
    error = make_validation_error(StrictModel, {"count": "5", "name": 123, "active": 0})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "int_type",
            "input_value": "5",
            "message": "Input should be a valid integer",
            "path": "count",
            "url": "https://errors.pydantic.dev/VERSION/v/int_type"
          },
          {
            "error_type": "string_type",
            "input_value": 123,
            "message": "Input should be a valid string",
            "path": "name",
            "url": "https://errors.pydantic.dev/VERSION/v/string_type"
          },
          {
            "error_type": "bool_type",
            "input_value": 0,
            "message": "Input should be a valid boolean",
            "path": "active",
            "url": "https://errors.pydantic.dev/VERSION/v/bool_type"
          }
        ]
        """,
    )


def test_format_mixed_errors():
    error = make_validation_error(
        MixedErrorModel,
        {
            "name": 123,
            "age": "bad",
            "score": -1,
            "code": "bad",
            "tags": [],
            "address": {},
        },
    )
    result = format_errors(error, options=FormatOptions(show_error_type=True))
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for MixedErrorModel with 8 errors

          name
            Input should be a valid string [string_type]
            Got: 123

          age
            Input should be a valid integer, unable to parse string as an integer [int_parsing]
            Got: 'bad'

          score
            Input should be greater than 0 [greater_than]
            Got: -1

          code
            String should match pattern '^[A-Z]+$' [string_pattern_mismatch]
            Got: 'bad'

          tags
            List should have at least 1 item after validation, not 0 [too_short]
            Got: []

          address.street
            Field required [missing]
            Got: (missing)

          address.city
            Field required [missing]
            Got: (missing)

          address.zipcode
            Field required [missing]
            Got: (missing)
        """,
    )


def test_rich_mixed_errors():
    error = make_validation_error(
        MixedErrorModel,
        {
            "name": 123,
            "age": "bad",
            "score": -1,
            "code": "bad",
            "tags": [],
            "address": {},
        },
    )
    output = _capture_rich(error, options=FormatOptions(show_error_type=True))
    karva.assert_snapshot(
        output,
        inline="""\
        Validation failed for MixedErrorModel with 8 errors

          name
            Input should be a valid string [string_type]
            Got: 123

          age
            Input should be a valid integer, unable to parse string as an integer [int_parsing]
            Got: 'bad'

          score
            Input should be greater than 0 [greater_than]
            Got: -1

          code
            String should match pattern '^[A-Z]+$' [string_pattern_mismatch]
            Got: 'bad'

          tags
            List should have at least 1 item after validation, not 0 [too_short]
            Got: []

          address.street
            Field required [missing]
            Got: (missing)

          address.city
            Field required [missing]
            Got: (missing)

          address.zipcode
            Field required [missing]
            Got: (missing)
        """,
    )


def test_filter_mixed_errors_by_type():
    error = make_validation_error(
        MixedErrorModel,
        {
            "name": 123,
            "age": "bad",
            "score": -1,
            "code": "bad",
            "tags": [],
            "address": {},
        },
    )
    all_errors = explain(error)
    missing_only = filter_errors(all_errors, error_type="missing")
    karva.assert_json_snapshot(
        [d.to_dict() for d in missing_only],
        inline="""\
        [
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "address.street",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          },
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "address.city",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          },
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "address.zipcode",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_count_mixed_errors():
    error = make_validation_error(
        MixedErrorModel,
        {
            "name": 123,
            "age": "bad",
            "score": -1,
            "code": "bad",
            "tags": [],
            "address": {},
        },
    )
    all_errors = explain(error)
    counts = count_errors(all_errors)
    karva.assert_json_snapshot(
        counts,
        inline="""\
        {
          "address": 3,
          "age": 1,
          "code": 1,
          "name": 1,
          "score": 1,
          "tags": 1
        }
        """,
    )


def test_filter_by_path_pattern_with_index():
    """Filter errors by index-based path pattern."""
    error = make_validation_error(
        User,
        {
            "name": "Alice",
            "age": 30,
            "email": "a@b.com",
            "addresses": [
                {"street": "x", "city": "y"},
                {"street": "a", "city": "b"},
            ],
        },
    )
    all_errors = explain(error)
    filtered = filter_errors(all_errors, path_pattern=r"\[1\]")
    karva.assert_json_snapshot(
        [d.to_dict() for d in filtered],
        inline="""\
        [
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


def test_explain_completely_empty_data():
    """All fields missing from empty dict."""
    error = make_validation_error(User, {})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "name",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          },
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "age",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          },
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "email",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          },
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "addresses",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_explain_wrong_type_for_nested_model():
    """Passing a non-dict where a nested model is expected."""
    error = make_validation_error(Outer, {"middle": "not_a_dict"})
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "context": {
              "class_name": "Middle"
            },
            "error_type": "model_type",
            "input_value": "not_a_dict",
            "message": "Input should be a valid dictionary or instance of Middle",
            "path": "middle",
            "url": "https://errors.pydantic.dev/VERSION/v/model_type"
          }
        ]
        """,
    )


def test_explain_none_for_required_field():
    """None passed to a non-optional required field."""
    error = make_validation_error(
        User, {"name": None, "age": 30, "email": "a@b.com", "addresses": []}
    )
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "string_type",
            "message": "Input should be a valid string",
            "path": "name",
            "url": "https://errors.pydantic.dev/VERSION/v/string_type"
          }
        ]
        """,
    )


def test_explain_wrong_type_for_list_field():
    """Non-list passed where list is expected."""
    error = make_validation_error(
        User,
        {"name": "Alice", "age": 30, "email": "a@b.com", "addresses": "not_a_list"},
    )
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "list_type",
            "input_value": "not_a_list",
            "message": "Input should be a valid list",
            "path": "addresses",
            "url": "https://errors.pydantic.dev/VERSION/v/list_type"
          }
        ]
        """,
    )


def test_explain_wrong_type_int_field():
    """String passed where int is expected."""
    error = make_validation_error(
        User,
        {"name": "Alice", "age": "not_int", "email": "a@b.com", "addresses": []},
    )
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "int_parsing",
            "input_value": "not_int",
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "path": "age",
            "url": "https://errors.pydantic.dev/VERSION/v/int_parsing"
          }
        ]
        """,
    )


def test_format_errors_with_non_missing_and_missing_mix():
    """Mix of missing fields and type errors in one validation."""
    error = make_validation_error(User, {"age": "not_int", "addresses": []})
    result = format_errors(error)
    karva.assert_snapshot(
        result,
        inline="""\
        Validation failed for User with 3 errors

          name
            Field required
            Got: (missing)

          age
            Input should be a valid integer, unable to parse string as an integer
            Got: 'not_int'

          email
            Field required
            Got: (missing)
        """,
    )


def test_rich_output_with_url_and_error_type():
    """Rich output with all options enabled on a constraint error."""
    error = make_validation_error(NumericConstrained, {"score": -1, "factor": 0.5})
    output = _capture_rich(
        error,
        options=FormatOptions(show_input=True, show_url=True, show_error_type=True),
    )
    karva.assert_snapshot(
        output,
        inline="""\
        Validation failed for NumericConstrained with 1 error

          score
            Input should be greater than or equal to 0 [greater_than_equal]
            Got: -1
            See: https://errors.pydantic.dev/VERSION/v/greater_than_equal
        """,
    )


def test_explain_list_multiple_items_different_errors():
    """Multiple list items with different errors."""
    error = make_validation_error(
        User,
        {
            "name": "Alice",
            "age": 30,
            "email": "a@b.com",
            "addresses": [
                {"street": "x", "city": "y"},
                {"city": "b", "zipcode": "z"},
            ],
        },
    )
    result = explain(error)
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
              "zipcode": "z"
            },
            "message": "Field required",
            "path": "addresses[1].street",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_to_dict_round_trip_with_real_error():
    """to_dict() on errors from real validation produces valid dicts."""
    error = make_validation_error(
        MixedErrorModel,
        {
            "name": 123,
            "age": "bad",
            "score": -1,
            "code": "bad",
            "tags": [],
            "address": {},
        },
    )
    result = explain(error)
    karva.assert_json_snapshot(
        [d.to_dict() for d in result],
        inline="""\
        [
          {
            "error_type": "string_type",
            "input_value": 123,
            "message": "Input should be a valid string",
            "path": "name",
            "url": "https://errors.pydantic.dev/VERSION/v/string_type"
          },
          {
            "error_type": "int_parsing",
            "input_value": "bad",
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "path": "age",
            "url": "https://errors.pydantic.dev/VERSION/v/int_parsing"
          },
          {
            "context": {
              "gt": 0.0
            },
            "error_type": "greater_than",
            "input_value": -1,
            "message": "Input should be greater than 0",
            "path": "score",
            "url": "https://errors.pydantic.dev/VERSION/v/greater_than"
          },
          {
            "context": {
              "pattern": "^[A-Z]+$"
            },
            "error_type": "string_pattern_mismatch",
            "input_value": "bad",
            "message": "String should match pattern '^[A-Z]+$'",
            "path": "code",
            "url": "https://errors.pydantic.dev/VERSION/v/string_pattern_mismatch"
          },
          {
            "context": {
              "actual_length": 0,
              "field_type": "List",
              "min_length": 1
            },
            "error_type": "too_short",
            "input_value": [],
            "message": "List should have at least 1 item after validation, not 0",
            "path": "tags",
            "url": "https://errors.pydantic.dev/VERSION/v/too_short"
          },
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "address.street",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          },
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "address.city",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          },
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "address.zipcode",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
    """,
    )


def test_filter_combined_type_and_path():
    """Combined filter on error_type and path_pattern narrows results."""
    error = make_validation_error(
        MixedErrorModel,
        {
            "name": 123,
            "age": "bad",
            "score": -1,
            "code": "bad",
            "tags": [],
            "address": {},
        },
    )
    all_errors = explain(error)
    missing_address = filter_errors(all_errors, error_type="missing", path_pattern=r"^address")
    karva.assert_json_snapshot(
        [d.to_dict() for d in missing_address],
        inline="""\
        [
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "address.street",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          },
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "address.city",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          },
          {
            "error_type": "missing",
            "input_value": {},
            "message": "Field required",
            "path": "address.zipcode",
            "url": "https://errors.pydantic.dev/VERSION/v/missing"
          }
        ]
        """,
    )


def test_count_single_field_multiple_errors():
    """count_errors accumulates when one top-level field has many sub-errors."""
    error = make_validation_error(
        User,
        {
            "name": "Alice",
            "age": 30,
            "email": "a@b.com",
            "addresses": [
                {"street": "x"},
                {"city": "y"},
            ],
        },
    )
    all_errors = explain(error)
    counts = count_errors(all_errors)
    karva.assert_json_snapshot(
        counts,
        inline="""\
        {
          "addresses": 4
        }
        """,
    )
