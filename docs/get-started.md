# Get Started

## Installation

Install pydantic-explain with pip:

```bash
pip install pydantic-explain
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add pydantic-explain
```

## Basic Usage

### Formatting Errors

The main entry point is `format_errors`, which takes a Pydantic `ValidationError`
and returns a human-readable string:

```python
from pydantic import BaseModel, ValidationError
from pydantic_explain import format_errors


class Address(BaseModel):
    street: str
    zipcode: str


class User(BaseModel):
    name: str
    addresses: list[Address]


try:
    User.model_validate({
        "name": "Alice",
        "addresses": [
            {"street": "123 Main St"},
            {"street": "456 Oak Ave", "zipcode": ["invalid"]},
        ],
    })
except ValidationError as e:
    print(format_errors(e))
```

### Structured Access

Use `explain` to get structured `ErrorDetail` objects for programmatic access:

```python
from pydantic_explain import explain

try:
    User.model_validate({"addresses": []})
except ValidationError as e:
    for detail in explain(e):
        print(f"{detail.path}: {detail.message}")
```

### Format Options

Customize output with `FormatOptions`:

```python
from pydantic_explain import format_errors, FormatOptions

options = FormatOptions(
    show_input=True,       # Show "Got: <value>" (default: True)
    show_url=True,         # Show Pydantic docs URL (default: False)
    show_error_type=True,  # Show error type tag (default: False)
    input_max_length=40,   # Truncate long values (default: 80)
)

try:
    User.model_validate({"addresses": []})
except ValidationError as e:
    print(format_errors(e, options=options))
```
