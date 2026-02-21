"""Core types for pydantic-explain."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ErrorDetail:
    """A single parsed validation error.

    Attributes:
        path: Dotted path to the field, e.g. ``"user.addresses[1].zipcode"``.
        message: Human-readable error message from Pydantic.
        error_type: Pydantic error type code, e.g. ``"missing"``.
        input_value: The actual invalid input value.
        context: Extra context dict from Pydantic.
        url: Pydantic documentation URL for this error type.
    """

    path: str
    message: str
    error_type: str
    input_value: object
    context: dict[str, object]
    url: str

    def to_dict(self) -> dict[str, object]:
        """Convert to a JSON-friendly dictionary, omitting empty fields.

        Returns:
            A dict with ``path``, ``message``, and ``error_type`` always present.
            ``input_value``, ``context``, and ``url`` are included only when non-empty.
        """
        result: dict[str, object] = {
            "path": self.path,
            "message": self.message,
            "error_type": self.error_type,
        }
        if self.input_value is not None:
            result["input_value"] = self.input_value
        if self.context:
            result["context"] = self.context
        if self.url:
            result["url"] = self.url
        return result


@dataclass(frozen=True, slots=True)
class FormatOptions:
    """Configuration for error formatting.

    Attributes:
        show_input: Whether to show the ``"Got:"`` line with the input value.
        show_url: Whether to show the Pydantic docs URL.
        show_error_type: Whether to show the error type tag.
        input_max_length: Maximum length for input value repr.
    """

    show_input: bool = True
    show_url: bool = False
    show_error_type: bool = False
    input_max_length: int = 80
