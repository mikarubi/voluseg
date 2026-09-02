# Changelog

All notable changes to Voluseg are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
the project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-09-01

### Added
- Restored two methods from the 2024-03 stable release that had been
  dropped: `planes_packed` (packed-planes single-plane imaging, `_PLN###`
  volume naming, `res_z = diam_cell`) and `registration_restrict`
  (restrict transform parameters, e.g. `1x1x1x1x1x0`), both validated,
  CLI-exposed, and tested.
- `voluseg` console script (Typer CLI) with all pipeline parameters,
  environment-variable equivalents, and a `--version` flag;
  `voluseg.__version__` is exposed.
- CLI options that were previously missing: `--dim-order`,
  `--dir-transform`, `--nwb-output`.
- Community infrastructure: contribution guide, code of conduct, issue and
  pull-request templates, and this changelog.

### Changed
- Registration now uses ANTsPy (`antspyx`) instead of the ANTs command-line
  tools: no system ANTs installation or `PATH` setup is required, and
  `opts_ants` is now a dictionary of `ants.registration` keyword arguments.
- NWB output is written *in addition to* `cells0_clean.hdf5` when
  `nwb_output=True` (previously it replaced it, which also prevented
  completion detection and intermediate cleanup).
- NWB output carries real metadata (imaging rate from `f_volume`, voxel grid
  spacing from `res_x/res_y/res_z` and `ds`) instead of placeholder values.
- Parameter files are JSON-only; pickle support removed.
- `load_volume` supports HDF5, TIFF, and NIfTI (KLB and PIL fallbacks
  removed).
- Docs: API reference is rendered directly from the generated
  `_steps`/`_tools` pages; blog and template pages removed.

### Removed
- AWS Batch integration (CDK stack under `iac/`, `voluseg._tools.aws`,
  automatic S3 export, `[aws]` extra): unexercised cloud plumbing removed
  to keep the pipeline lean; recoverable from git history when cloud
  deployment work is scheduled.
- `voluseg.update()` (self-reinstall via pip).
- `voluseg.load_metadata()` (lab-specific XML parser with no callers).
- Apache Spark / Java leftovers (pyspark, JDK) from the container, CI, and
  documentation — Dask has been the parallel backend since early 2025.
- Unused `loguru` dependency; contradictory `[dask]` extra.

### Fixed
- Container CLI failed at startup: `opts_ants` was passed as a string into a
  pydantic `dict` field; it is now a JSON option.
- Unconditional S3 upload after every pipeline run (now only inside AWS
  Batch jobs); AWS environment-variable and output-path mismatches.
- Step 3 crash with pandas >= 3 (read-only Copy-on-Write view).
- Failed segmentation blocks reported a nonzero cell count with no cell
  data, crashing step 5; they now report zero cells and step 5 raises a
  clear error when no cells were detected anywhere.
- DANDI sample download: current `dandi` client required by the server;
  staging instance renamed to `dandi-sandbox`.
- Documentation build: undeclared `remark-math`/`rehype-katex`; stale
  API-reference copies; broken links; stale `package-lock.json`.
- Documentation content: removed non-existent CLI flags and outdated API
  examples (`parameter_dictionary`, `dir_ants`, `step0_process_parameters`).

## [0.1.0]

Functional prototype used in Mu et al., Cell 2019 and Yang et al., Cell 2022.
