"""Rich terminal output for Pydantic validation errors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_explain._explain import explain
from pydantic_explain._format import _truncate_repr
from pydantic_explain._types import FormatOptions

if TYPE_CHECKING:
    from pydantic import ValidationError
    from rich.console import Console


def format_errors_rich(
    error: ValidationError,
    *,
    options: FormatOptions | None = None,
    console: Console | None = None,
) -> None:
    """Print Pydantic validation errors to the terminal with Rich formatting.

    Args:
        error: A Pydantic ValidationError instance.
        options: Formatting options. Uses defaults if None.
        console: Rich Console to print to. Uses a new default console if None.
    """
    from rich.console import Console
    from rich.text import Text

    opts = options or FormatOptions()
    con = console or Console()
    details = explain(error)

    count = len(details)
    plural = "error" if count == 1 else "errors"

    header = Text()
    header.append("Validation failed", style="bold red")
    header.append(f" for {error.title} with {count} {plural}")
    con.print(header)

    for detail in details:
        con.print()

        path_text = Text(f"  {detail.path}", style="bold cyan")
        con.print(path_text)

        message = detail.message
        if opts.show_error_type:
            msg_text = Text(f"    {message} ")
            msg_text.append(f"[{detail.error_type}]", style="dim")
        else:
            msg_text = Text(f"    {message}")
        con.print(msg_text)

        if opts.show_input:
            if detail.error_type == "missing":
                input_text = Text("    Got: ", style="")
                input_text.append("(missing)", style="yellow")
            else:
                truncated = _truncate_repr(detail.input_value, opts.input_max_length)
                input_text = Text("    Got: ", style="")
                input_text.append(truncated, style="yellow")
            con.print(input_text)

        if opts.show_url and detail.url:
            url_text = Text("    See: ", style="")
            url_text.append(detail.url, style="blue underline")
            con.print(url_text)
