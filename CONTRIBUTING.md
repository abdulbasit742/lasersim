# Contributing

Thank you for improving this project.

## Development setup

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e .[dev]
pytest -q
python validate.py
```

## Pull request checklist

- The change has a clear purpose.
- Tests pass locally.
- Documentation is updated where needed.
- Public commands continue to work.
- Any numerical change includes a short explanation.

## Code style

Prefer small functions, explicit units in variable names, deterministic examples, and readable scientific comments.
