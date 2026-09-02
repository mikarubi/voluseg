# Changelog

All notable changes to Voluseg are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
the project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

- Direct ingestion of 4D Zarr stores, mirroring the NWB input path (#90).
- Documentation migrated from Docusaurus to Quarto: plain-markdown pages,
  API reference generated from NumPy docstrings by quartodoc, and the npm
  dependency tree (source of the standing vulnerability alerts) removed.
- Registration backend moved from the ANTs command-line tools to ANTsPy:
  pip install becomes a complete installation, with the historical
  multi-resolution schedules and transform file format preserved.
- Restored two methods from the 2024-03 release that were dropped in the
  2025 refactor: planes_packed (packed-planes single-plane imaging) and
  registration_restrict (restricting transform parameters).

## [0.2.0] - 2026-10-25

Merged via #74 (fixes), #75 (removals), #78 (CI), and #80 (NWB/CLI).

### Added
- `voluseg` console script (Typer CLI) with all pipeline parameters,
  environment-variable equivalents, Dask configuration options, and a
  `--version` flag; `voluseg.__version__` is exposed.
- Dask execution layer with configurable local and cluster backends
  (`voluseg.dask_config`).
- Community infrastructure: contribution guide, code of conduct, issue
  and pull-request templates, and this changelog.

### Changed
- NWB output is written in addition to `cells0_clean.hdf5` when
  `nwb_output=True` (previously it replaced it, which also prevented
  completion detection and cleanup of intermediates).
- NWB output carries real metadata (imaging rate from `f_volume`, voxel
  grid from `res_x/res_y/res_z` and `ds`) instead of placeholder values.
- Parameter files are JSON-only; pickle support removed.
- `load_volume` supports HDF5, TIFF, and NIfTI (KLB and PIL fallbacks
  removed).
- Docker images publish to GHCR only from pushes to master; pull
  requests only verify that the image builds.

### Removed
- `voluseg.update()` (self-reinstall via pip) and
  `voluseg.load_metadata()` (lab-specific XML parser with no callers).
- Apache Spark / Java remnants (pyspark, JDK) from the container, CI,
  and documentation; Dask is the parallel backend.
- AWS Batch integration (CDK stack, Batch/S3 helpers, `[aws]` extra).
- Unused `loguru` dependency.

### Fixed
- Package import broke test collection on every CI job (dangling imports
  of removed modules after a merge); test matrix restored to Linux and
  macOS.
- Tests run on an explicitly configured Dask client; the previous
  default cluster oversubscribed CI runners and killed workers on
  memory-heavy steps.
- Step 3 crash with pandas >= 3 (read-only Copy-on-Write view).
- Documentation build: missing remark-math/rehype-katex dependencies.
- Container CLI crashed at startup (`opts_ants` passed as a bare string
  into a pydantic dict field; now a JSON option).
- DANDI sample download: current `dandi` client required by the server;
  staging instance renamed to `dandi-sandbox`.
- Remote NWB streaming works from a plain install (`fsspec` and
  `aiohttp` declared).
- Failed segmentation blocks no longer report phantom cell counts;
  collecting zero cells raises a clear error. The NMF's NaN-triggered
  retry at reduced peak fractions is intentional adaptive model-order
  selection and is documented as such in the code.

## [0.1.0]

Functional prototype used in Mu et al., Cell 2019 and Yang et al.,
Cell 2022.
