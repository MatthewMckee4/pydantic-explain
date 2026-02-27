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
    group_errors,
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
    assert len(result) == 1
    assert result[0].error_type == "extra_forbidden"
    assert result[0].path == "unknown"


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


def test_format_extra_forbidden_multiple():
    error = make_validation_error(ExtraForbid, {"name": "Alice", "a": 1, "b": 2})
    result = explain(error)
    assert len(result) == 2
    paths = {d.path for d in result}
    assert paths == {"a", "b"}


def test_explain_pattern_mismatch():
    error = make_validation_error(PatternConstrained, {"code": "invalid"})
    result = explain(error)
    assert len(result) == 1
    assert result[0].error_type == "string_pattern_mismatch"
    assert result[0].path == "code"


def test_format_pattern_mismatch():
    error = make_validation_error(PatternConstrained, {"code": "bad"})
    result = format_errors(error, options=FormatOptions(show_error_type=True))
    assert "[string_pattern_mismatch]" in result
    assert "code" in result


def test_explain_pattern_context():
    """Pattern constraint errors include the pattern in context."""
    error = make_validation_error(PatternConstrained, {"code": "nope"})
    result = explain(error)
    assert "pattern" in result[0].context


def test_explain_string_too_short():
    error = make_validation_error(StringConstrained, {"short": "a"})
    result = explain(error)
    assert len(result) == 1
    assert result[0].error_type == "string_too_short"


def test_explain_string_too_long():
    error = make_validation_error(StringConstrained, {"short": "abcdef"})
    result = explain(error)
    assert len(result) == 1
    assert result[0].error_type == "string_too_long"


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


def test_explain_string_constraint_context():
    """String length errors include min_length in context."""
    error = make_validation_error(StringConstrained, {"short": "a"})
    result = explain(error)
    assert "min_length" in result[0].context


def test_explain_less_than_ge():
    error = make_validation_error(NumericConstrained, {"score": -1, "factor": 0.5})
    result = explain(error)
    assert len(result) == 1
    assert result[0].error_type == "greater_than_equal"
    assert result[0].path == "score"


def test_explain_greater_than_le():
    error = make_validation_error(NumericConstrained, {"score": 101, "factor": 0.5})
    result = explain(error)
    assert len(result) == 1
    assert result[0].error_type == "less_than_equal"


def test_explain_less_than_gt():
    error = make_validation_error(NumericConstrained, {"score": 50, "factor": 0.0})
    result = explain(error)
    assert len(result) == 1
    assert result[0].error_type == "greater_than"
    assert result[0].path == "factor"


def test_explain_greater_than_lt():
    error = make_validation_error(NumericConstrained, {"score": 50, "factor": 1.0})
    result = explain(error)
    assert len(result) == 1
    assert result[0].error_type == "less_than"


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
    assert len(result) == 2
    error_types = {d.error_type for d in result}
    assert "greater_than_equal" in error_types
    assert "less_than" in error_types


def test_explain_list_too_short():
    error = make_validation_error(ListConstrained, {"tags": []})
    result = explain(error)
    assert len(result) == 1
    assert result[0].error_type == "too_short"
    assert result[0].path == "tags"


def test_explain_list_too_long():
    error = make_validation_error(ListConstrained, {"tags": ["a", "b", "c", "d", "e", "f"]})
    result = explain(error)
    assert len(result) == 1
    assert result[0].error_type == "too_long"


def test_format_list_constraint():
    error = make_validation_error(ListConstrained, {"tags": []})
    result = format_errors(error)
    assert "too short" in result.lower() or "at least" in result.lower()


def test_explain_invalid_enum():
    error = make_validation_error(EnumModel, {"color": "yellow"})
    result = explain(error)
    assert len(result) >= 1
    paths = {d.path for d in result}
    assert any("color" in p for p in paths)


def test_format_invalid_enum():
    error = make_validation_error(EnumModel, {"color": "yellow"})
    result = format_errors(error)
    assert "color" in result


def test_explain_invalid_literal_string():
    error = make_validation_error(LiteralModel, {"status": "deleted", "priority": 1})
    result = explain(error)
    assert len(result) == 1
    assert result[0].path == "status"
    assert result[0].error_type == "literal_error"


def test_explain_invalid_literal_int():
    error = make_validation_error(LiteralModel, {"status": "active", "priority": 99})
    result = explain(error)
    assert len(result) == 1
    assert result[0].path == "priority"
    assert result[0].error_type == "literal_error"


def test_explain_multiple_literal_errors():
    error = make_validation_error(LiteralModel, {"status": "deleted", "priority": 99})
    result = explain(error)
    assert len(result) == 2
    paths = {d.path for d in result}
    assert paths == {"status", "priority"}


def test_format_literal_error():
    error = make_validation_error(LiteralModel, {"status": "deleted", "priority": 1})
    result = format_errors(error, options=FormatOptions(show_error_type=True))
    assert "[literal_error]" in result


def test_explain_dict_invalid_value_type():
    error = make_validation_error(DictModel, {"metadata": {"key": "not_an_int"}})
    result = explain(error)
    assert len(result) >= 1
    assert any("metadata" in d.path for d in result)


def test_explain_dict_missing():
    error = make_validation_error(DictModel, {})
    result = explain(error)
    assert len(result) == 1
    assert result[0].path == "metadata"
    assert result[0].error_type == "missing"


def test_format_dict_error():
    error = make_validation_error(DictModel, {"metadata": {"a": "bad"}})
    result = format_errors(error)
    assert "metadata" in result


def test_explain_nested_list_type_error():
    error = make_validation_error(
        NestedListModel,
        {"matrix": [["not_int"]], "users": []},
    )
    result = explain(error)
    assert len(result) >= 1
    assert any("matrix" in d.path for d in result)


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
    assert len(result) >= 1
    assert any("users[0].addresses[0].zipcode" in d.path for d in result)


def test_format_nested_list_model():
    error = make_validation_error(
        NestedListModel,
        {"matrix": [["bad"]], "users": []},
    )
    result = format_errors(error)
    assert "matrix[0][0]" in result


def test_explain_alias_missing():
    error = make_validation_error(AliasModel, {})
    result = explain(error)
    assert len(result) == 2
    paths = {d.path for d in result}
    assert "full_name" in paths or "name" in paths
    assert "user_age" in paths or "age" in paths


def test_explain_alias_wrong_type():
    error = make_validation_error(AliasModel, {"full_name": 123, "user_age": "not_int"})
    result = explain(error)
    assert len(result) >= 1


def test_explain_invalid_date():
    error = make_validation_error(DateTimeModel, {"created": "not-a-date", "updated": "2024-01-01"})
    result = explain(error)
    assert any(d.path == "created" for d in result)


def test_explain_invalid_datetime():
    error = make_validation_error(
        DateTimeModel, {"created": "2024-01-01", "updated": "not-a-datetime"}
    )
    result = explain(error)
    assert any(d.path == "updated" for d in result)


def test_format_datetime_errors():
    error = make_validation_error(DateTimeModel, {"created": "bad", "updated": "bad"})
    result = format_errors(error)
    assert "created" in result
    assert "updated" in result


def test_explain_tuple_wrong_length():
    error = make_validation_error(TupleModel, {"point": [1], "rgb": [1, 2, 3]})
    result = explain(error)
    assert any("point" in d.path for d in result)


def test_explain_tuple_wrong_type():
    error = make_validation_error(TupleModel, {"point": ["a", "b"], "rgb": [1, 2, 3]})
    result = explain(error)
    assert any("point" in d.path for d in result)


def test_explain_tuple_too_many():
    error = make_validation_error(TupleModel, {"point": [1, 2, 3, 4], "rgb": [1, 2, 3]})
    result = explain(error)
    assert any("point" in d.path for d in result)


def test_explain_set_wrong_item_type():
    error = make_validation_error(SetModel, {"unique_tags": [1, 2], "frozen_ids": [1]})
    result = explain(error)
    assert any("unique_tags" in d.path for d in result)


def test_explain_frozenset_wrong_item_type():
    error = make_validation_error(SetModel, {"unique_tags": ["a"], "frozen_ids": ["not_int"]})
    result = explain(error)
    assert any("frozen_ids" in d.path for d in result)


def test_explain_five_level_nesting():
    error = make_validation_error(
        Level0,
        {"level1": {"level2": {"level3": {"level4": {"value": "not_int"}}}}},
    )
    result = explain(error)
    assert len(result) == 1
    assert result[0].path == "level1.level2.level3.level4.value"


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
    assert len(result) == 1
    assert "level4" in result[0].path


def test_explain_model_validator_error():
    """Model-level validators produce errors at root or model level."""
    error = make_validation_error(ModelValidated, {"password": "abc", "confirm_password": "xyz"})
    result = explain(error)
    assert len(result) == 1
    assert "match" in result[0].message.lower()


def test_format_model_validator():
    error = make_validation_error(ModelValidated, {"password": "abc", "confirm_password": "xyz"})
    result = format_errors(error)
    assert "Passwords do not match" in result


def test_explain_multiple_field_validators():
    """Both field validators fail simultaneously."""
    error = make_validation_error(MultiFieldValidated, {"username": "bad user!", "email": "nope"})
    result = explain(error)
    assert len(result) == 2
    paths = {d.path for d in result}
    assert paths == {"username", "email"}


def test_explain_single_field_validator_passes():
    """Only one field validator fails."""
    error = make_validation_error(MultiFieldValidated, {"username": "gooduser", "email": "nope"})
    result = explain(error)
    assert len(result) == 1
    assert result[0].path == "email"


def test_explain_strict_int_from_string():
    """Strict mode rejects string-to-int coercion."""
    error = make_validation_error(StrictModel, {"count": "5", "name": "Alice", "active": True})
    result = explain(error)
    assert len(result) == 1
    assert result[0].path == "count"


def test_explain_strict_bool_from_int():
    """Strict mode rejects int-to-bool coercion."""
    error = make_validation_error(StrictModel, {"count": 1, "name": "Alice", "active": 1})
    result = explain(error)
    assert len(result) == 1
    assert result[0].path == "active"


def test_explain_strict_multiple_coercion_failures():
    error = make_validation_error(StrictModel, {"count": "5", "name": 123, "active": 0})
    result = explain(error)
    assert len(result) == 3
    paths = {d.path for d in result}
    assert paths == {"count", "name", "active"}


def test_explain_mixed_errors():
    """Many different error types in a single validation."""
    error = make_validation_error(
        MixedErrorModel,
        {
            "name": 123,
            "age": "not_int",
            "score": -5,
            "code": "lowercase",
            "tags": [],
            "address": {"city": "x"},
        },
    )
    result = explain(error)
    assert len(result) >= 5
    error_types = {d.error_type for d in result}
    assert len(error_types) >= 3


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
    assert "name" in result
    assert "age" in result
    assert "score" in result
    assert "code" in result
    assert "tags" in result
    assert "address" in result


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
    assert "name" in output
    assert "age" in output
    assert "score" in output


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
    assert all(e.error_type == "missing" for e in missing_only)
    assert len(missing_only) < len(all_errors)


def test_group_mixed_errors():
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
    groups = group_errors(all_errors)
    assert "address" in groups
    assert len(groups) >= 5


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
    assert "address" in counts
    assert counts["address"] >= 1


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
    assert all("[1]" in e.path for e in filtered)


def test_group_nested_model_errors():
    """Grouped errors from nested models cluster by top-level field."""
    error = make_validation_error(
        NestedListModel,
        {
            "matrix": [["bad"]],
            "users": [{"name": 1, "age": "x", "email": 2, "addresses": []}],
        },
    )
    all_errors = explain(error)
    groups = group_errors(all_errors)
    assert "matrix" in groups
    assert "users" in groups


def test_explain_completely_empty_data():
    """All fields missing from empty dict."""
    error = make_validation_error(User, {})
    result = explain(error)
    assert len(result) == 4
    paths = {d.path for d in result}
    assert paths == {"name", "age", "email", "addresses"}


def test_explain_wrong_type_for_nested_model():
    """Passing a non-dict where a nested model is expected."""
    error = make_validation_error(Outer, {"middle": "not_a_dict"})
    result = explain(error)
    assert len(result) >= 1
    assert any("middle" in d.path for d in result)


def test_explain_none_for_required_field():
    """None passed to a non-optional required field."""
    error = make_validation_error(
        User, {"name": None, "age": 30, "email": "a@b.com", "addresses": []}
    )
    result = explain(error)
    assert len(result) == 1
    assert result[0].path == "name"


def test_explain_wrong_type_for_list_field():
    """Non-list passed where list is expected."""
    error = make_validation_error(
        User,
        {"name": "Alice", "age": 30, "email": "a@b.com", "addresses": "not_a_list"},
    )
    result = explain(error)
    assert any("addresses" in d.path for d in result)


def test_explain_wrong_type_int_field():
    """String passed where int is expected."""
    error = make_validation_error(
        User,
        {"name": "Alice", "age": "not_int", "email": "a@b.com", "addresses": []},
    )
    result = explain(error)
    assert len(result) == 1
    assert result[0].path == "age"
    assert result[0].error_type == "int_parsing"


def test_format_errors_with_non_missing_and_missing_mix():
    """Mix of missing fields and type errors in one validation."""
    error = make_validation_error(User, {"age": "not_int", "addresses": []})
    result = format_errors(error)
    assert "(missing)" in result
    assert "Got:" in result


def test_rich_output_with_url_and_error_type():
    """Rich output with all options enabled on a constraint error."""
    error = make_validation_error(NumericConstrained, {"score": -1, "factor": 0.5})
    output = _capture_rich(
        error,
        options=FormatOptions(show_input=True, show_url=True, show_error_type=True),
    )
    assert "score" in output
    assert "Got:" in output
    assert "See:" in output
    assert "[greater_than_equal]" in output


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
    paths = {d.path for d in result}
    assert "addresses[0].zipcode" in paths
    assert "addresses[1].street" in paths


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
    for detail in result:
        d = detail.to_dict()
        assert "path" in d
        assert "message" in d
        assert "error_type" in d


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
    assert all(e.error_type == "missing" for e in missing_address)
    assert all("address" in e.path for e in missing_address)


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
    assert counts["addresses"] >= 3
