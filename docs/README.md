# Documentation

The documentation is a [Quarto](https://quarto.org) website. Pages are plain
markdown (`.qmd`); the API reference is generated from the package docstrings
by [quartodoc](https://machow.github.io/quartodoc/) (NumPy docstring style is
supported natively).

## Building locally

```bash
pip install -e .                     # quartodoc imports the package
pip install -r docs/requirements-docs.txt
cd docs
quartodoc build                      # generates reference/ from docstrings
quarto render                        # site is written to docs/_site
quarto preview                       # or: live-reload preview
```

Install the Quarto CLI from https://quarto.org/docs/get-started/ if you do
not have it.

## Publishing

CI (`.github/workflows/build_publish_docs.yaml`) rebuilds the site on every
push and deploys to GitHub Pages from `master`. Generated files
(`docs/reference/`, `docs/_site/`) are never committed.
