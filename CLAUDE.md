# CLAUDE.md

## Commands

- `uv sync --all-groups` — install all dependencies
- `uv run karva test` — run tests
- `uv run ruff check .` — lint
- `uv run ruff format .` — format code
- `uv run ruff format --check .` — check formatting
- `uv run ty check` — type check

## Project Conventions

- Python 3.10+ target
- Use `from __future__ import annotations` in all Python files
- Use `X | Y` union syntax, not `Optional[X]` or `Union[X, Y]`
- Google-style docstrings
- Full type annotations on all public functions
- `src/` layout with explicit `__all__` in `__init__.py`
- Immutable data structures (frozen dataclasses, tuples)
- Zero runtime dependencies beyond `pydantic>=2.0`
- karva for testing (not pytest)
- No wildcard imports
