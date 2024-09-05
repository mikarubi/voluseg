# Tests

Run tests locally with `pytest` and `coverage`:

```bash
coverage run -m pytest -s -v --tb=short
```

With the plugin `pytest-cov` (this works locally, but for some reason not on Github actions):
```bash
pytest --cov=voluseg --cov-report=term-missing --cov-report=html --cov-report=xml -s -v --tb=short
```