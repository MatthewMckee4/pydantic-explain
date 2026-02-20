# pydantic-errors

Human-readable error messages for Pydantic validation errors.

## Overview

pydantic-errors transforms Pydantic v2's verbose `ValidationError` output into clear,
structured messages that are easy to read and act on.

## Quick Example

```python
from pydantic import BaseModel, ValidationError
from pydantic_errors import format_errors


class User(BaseModel):
    name: str
    age: int


try:
    User.model_validate({"age": "not a number"})
except ValidationError as e:
    print(format_errors(e))
```

Output:

```text
Validation failed for User with 2 errors

  name
    Field required
    Got: (missing)

  age
    Input should be a valid integer, unable to parse string as an integer
    Got: 'not a number'
```
