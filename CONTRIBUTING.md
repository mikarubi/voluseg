# Contributing to Voluseg

Thanks for your interest in improving Voluseg! Contributions of all kinds are
welcome: bug reports, feature requests, documentation, and code.

## Reporting bugs and requesting features

Please use the [issue tracker](https://github.com/mikarubi/voluseg/issues).
Issue templates will guide you through the information we need — for bugs,
always include your Voluseg version (`voluseg --version`), Python version,
operating system, and the full error output.

## Development setup

```bash
git clone https://github.com/mikarubi/voluseg.git
cd voluseg
python -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r tests/requirements.txt
```

## Running the tests

```bash
pytest -v
```

The test suite downloads a small sample dataset on first use when
`GITHUB_ACTIONS=true`; locally, point the fixtures at existing data with the
`SAMPLE_DATA_PATH_H5` and `SAMPLE_DATA_PATH_NWB` environment variables (see
`tests/test_voluseg.py`). The remote-streaming test (`test_nwb_remote`) is
skipped in CI and can be run locally when bandwidth allows.

## Pull requests

1. Fork the repository and create a branch from `master`.
2. Keep changes focused; unrelated fixes belong in separate PRs.
3. Add or update tests for any behavior change.
4. Make sure `pytest` passes and the documentation still builds
   (`cd docs/voluseg-docs-app && yarn && yarn build`) if you touched docs.
5. Open the PR with a clear description of the problem and the solution.

CI runs the test suite on Linux and macOS across supported Python versions;
a PR must be green before review.

## Documentation

The documentation is a Docusaurus site in `docs/voluseg-docs-app`. The API
reference is generated from docstrings by `pydoc-markdown` (see
`docs/README.md`), so document new functions with NumPy-style docstrings.

## Code style

- Follow the existing style; format Python with `black` defaults.
- Prefer explicit exceptions (`raise ValueError(...)`) over bare `except`.
- Keep the public API minimal: pipeline steps and parameter I/O.

## Code of conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md); by
participating you agree to uphold it.
