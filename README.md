# pydantic-errors

Human-readable error messages for Pydantic validation errors.

## Installation

With [uv](https://docs.astral.sh/uv/):

```bash
uv add pydantic-errors
```

## Usage

```python
from pydantic import BaseModel, ValidationError
from pydantic_errors import format_errors


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

```text
Validation failed for User with 2 errors

  addresses[0].zipcode
    Field required
    Got: (missing)

  addresses[1].zipcode
    Input should be a valid string
    Got: ['invalid']
```

## Documentation

Full documentation is available at [pydantic-errors docs](https://matthewmckee4.github.io/pydantic-errors/).
