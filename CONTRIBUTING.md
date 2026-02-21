# Contributing

## Setup

Clone the repo and install dependencies:

```bash
git clone https://github.com/MatthewMckee4/pydantic-explain.git
cd pydantic-explain
uv sync --all-groups
pre-commit install
```

## Development

### Run tests

```bash
uv run karva test
```

### Lint and format

```bash
uv run ruff check .
uv run ruff format .
```

### Type check

```bash
uv run ty check
```

## Pull Requests

1. Create a feature branch from `main`
2. Make your changes
3. Ensure all checks pass: tests, lint, format, type check
4. Submit a PR against `main`

## Releases

1. Update `CHANGELOG.md`
2. Bump version in `pyproject.toml`
3. Commit: `git commit -m "chore: release vX.Y.Z"`
4. Tag: `git tag vX.Y.Z`
5. Push: `git push origin vX.Y.Z`
