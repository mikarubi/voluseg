# Voluseg cleanup: core vs. extras, and what changed on this branch

Branch: `cleanup/mechanical-fixes` (off `master` @ `53065d7`, 2026-09-01).

**How to read this document**: section 1 says what the tool is; section 2
maps core vs. extras; section 3 lists the bugs found (each with status);
sections 4, 4b, 4c, 4d describe the four commits on this branch; section 5
records how everything was verified; section 6 lists remaining follow-ups.
`CHANGELOG.md` carries the user-facing summary of the same changes.

This document records an audit of the repository against the R03 research
strategy (Aims 1–3: streamlined dependencies / containers / CI; NWB–DANDI–
Neurosift integration; documentation and community), separates the core
pipeline from add-ons, and lists what was changed here versus what still
needs a decision.

## 1. What the tool is

Voluseg is a five-step pipeline for automatic volumetric cell segmentation of
large-scale calcium-imaging data (whole-brain zebrafish light-sheet):

| Step | Module | Purpose |
|---|---|---|
| 0 | `_steps/step0.py` | validate parameters (pydantic), enumerate volumes, write `parameters.json` |
| 1 | `_steps/step1.py` | load raw volumes (HDF5/TIFF/NIfTI/NWB), downsample, pad, save NIfTI |
| 2 | `_steps/step2.py` | rigid registration to a reference volume with ANTs (`antsRegistration`) |
| 3 | `_steps/step3.py` | brain mask via Gaussian-mixture intensity threshold; mean timeseries |
| 4 | `_steps/step4*.py` | block-wise sparse NMF cell detection (Dask-parallel) |
| 5 | `_steps/step5.py` | duplicate removal, detrending, baseline; HDF5 or NWB output |

## 2. Core vs. extras

### Core — keep

- `src/voluseg/_steps/*`
- `src/voluseg/_tools/{ants_registration,ants_transformation,load_volume,save_volume,ball,sparseness,sparseness_projection,clean_signal,parameters,parameters_models,evenly_parallelize,get_volume_name,constants}.py`
- `src/voluseg/_tools/nwb.py` (Aim 2), `src/voluseg/_tools/sample_data.py` (tests + tutorials)
- `Dockerfile`, `.github/workflows/*`, `docs/` (Aims 1 and 3)

### Extras — keep, but rough edges (Aim 1 IaC is scheduled for months 19–24)

- `src/voluseg/_tools/aws.py`, `app/app.py`, `iac/aws_batch/` — AWS Batch glue. Already
  optional via the `[aws]` extra in `pyproject.toml`.

### Extras — recommended for removal (**not done; needs sign-off**)

| Item | Reason |
|---|---|
| `src/voluseg/_update.py` (`voluseg.update()`) | `os.system("pip install --force-reinstall git+…")` from inside the library. Unsafe, conflicts with the planned semantic-versioning releases. Advertised in `README.md`. |
| `src/voluseg/_tools/load_metadata.py` (exported at top level) | Parses lab-specific rig XML (`exposure_time`, `z_step`, `Stack_frequency`). No callers anywhere in the repo. |
| KLB and PIL fallbacks in `_tools/load_volume.py` | `pyklb` is not a declared dependency; PIL path is a fallback for the TIFF reader. Suggest supporting HDF5 / TIFF / NIfTI / NWB only. |
| Pickle support in `_tools/parameters.py` | `step0` writes JSON only; pickle is a portability/security smell. One test (`test_parameters_json_pickle`) exercises it. |
| Docusaurus template filler | `docs/voluseg-docs-app/blog/` (welcome post by `author1`), `src/pages/markdown-page.md`, "Blog" navbar/footer links. |
| `iac/aws_batch/{source.bat,requirements-dev.txt}` | CDK scaffold leftovers; `requirements-dev.txt` pins pytest 6 for a directory with no tests. |

## 3. Bugs found

| # | Where | Problem | Status |
|---|---|---|---|
| 1 | `app/app.py` | `opts_ants` CLI option was a `str` defaulting to `""`, passed straight into the pydantic `dict` field → `ValidationError: Input should be a valid dictionary` before step 0. **Every documented Docker / Apptainer / DANDI Hub command failed.** Reproduced against pydantic 2.13. | **Fixed** — option is a JSON string (default `"{}"`), parsed before `step0_define_parameters`. |
| 2 | `app/app.py` | Unconditional S3 upload after step 5 → `boto3` credential error for every non-AWS-Batch user after a full run. | **Fixed** — upload only when `VOLUSEG_JOB_ID` is set (only `run_job_in_aws_batch` sets it); `boto3` import is now lazy. |
| 3 | `_tools/aws.py` vs `app/app.py` | Env-var mismatch: submitter set `VOLUSEG_REGISTRATION_OPTS`, container read `OPTIONS_ANTS`. Output dir `/tmp/voluseg-jobs` vs CDK mount `/tmp/voluseg_output`. | **Fixed** — both use `VOLUSEG_OPTS_ANTS`; output dir aligned with the CDK mount. *Not verified against a live AWS account.* |
| 4 | `README-docker.md`, `running_container.mdx`, `running_dandihub.mdx` | Documented flags `--no-parallel-volume` / `--no-parallel-clean` do not exist; Typer rejects them. Also referenced a non-existent `voluseg_nwb-ingestion.sif`. | **Fixed** — flags removed, image name corrected. |
| 5 | `docs/.../running.mdx` | Tutorial used the removed API (`voluseg.parameter_dictionary()`, `dir_ants`, `step0_process_parameters`, `voluseg.tools.*`). | **Fixed** — matches `README.md` and the current `step0_define_parameters` API. |
| 6 | `docs/.../iac_aws_batch.mdx` | Wrong import path (`voluseg.tools.aws`) and wrong kwarg (`job_name` vs `job_name_prefix`). | **Fixed**. |
| 7 | `tests/test_voluseg.py` | `compare_results_nwb_and_h5_dir` lacks the `test_` prefix, so pytest never collects it. Enabling it as-is would fail: the h5 fixture uses `ds=2` and the NWB fixture `ds=1`, so voxel coordinates differ. | **Not touched** — needs a decision on fixture alignment. |
| 8 | `_tools/nwb.py::write_nwbfile` | Placeholder metadata is written into real output files: `location="V1"`, `indicator="GFP"`, `unit="lumens"`, `rate=1.0`, `emission_lambda=500`, `grid_spacing=[0.01,0.01] m`. | **Not touched** — Aim 2 work; needs `f_volume`, `res_x/y/z` and user metadata plumbed through. |

## 4. Mechanical changes made on this branch

### Dead Apache Spark / Java leftovers (Spark→Dask swap landed Feb 2025)
- `Dockerfile`: removed `openjdk-17-jdk`, `JAVA_HOME`, redundant `apt-get update`; added `--no-install-recommends`.
- `requirements-docker.txt`: removed `pyspark==3.4.0`.
- `.github/workflows/run_tests.yaml`: removed `actions/setup-java`.
- `docs/.../installation.md`: removed "Java SE Development Kit 17"; Python floor now matches `pyproject.toml` (`>=3.10`).

### Dependencies
- `requirements.txt`, `requirements-docker.txt`, `README.md`: removed `loguru` (pinned, imported nowhere).
- `requirements.txt`, `README.md`: added `tifffile` explicitly (it was only reachable through scikit-image's dependency tree; `load_volume.py` imports it directly).
- `pyproject.toml`: removed the `[dask]` optional extra — `dask` is already an unconditional dependency, so the extra only pinned a stale version.

### Deprecated / removed APIs
- `_steps/step3.py`: `scipy.ndimage.filters.median_filter` → `scipy.ndimage.median_filter`.
- `_steps/step1.py`: `np.lib.pad` → `np.pad`.
- `_tools/load_volume.py`: dropped the `skimage.external.tifffile` fallback (removed from scikit-image years ago); imports `tifffile` directly.

### CI
- `run_tests.yaml`: removed `ANTS_PATH` env var (nothing reads it; `dir_ants` was removed in Feb 2025) and the redundant `pip install -r requirements.txt` (already pulled in by `pip install -e .`).

### Docs
- Deleted the hand-copied API-reference folders `docs/.../reference/{tools,steps,update.md}`. pydoc-markdown regenerates `_tools`/`_steps` in CI, but Docusaurus excludes `_*` paths by default, so those copies were what actually rendered — and they were stale (`tools/parameter_dictionary.md` documented a removed function). Phase 1 fixes this properly: `docusaurus.config.js` now overrides the docs `exclude` list so the generated `_steps`/`_tools` render directly (package `__init__` pages stay hidden).
- `docusaurus.config.js`: `organizationName`/`projectName` were still the template values `facebook`/`docusaurus`.
- `parameters.mdx`: `input_dirs` type updated to `List[str]` (relaxed in `53065d7`).
- `iac/aws_batch/README.md`: replaced the untouched "Welcome to your CDK Python project!" scaffold with a short description and a pointer to the docs page.

## 4b. Phase 1 — removals and the bugs they uncovered (second commit)

### Removed (per the approved plan)
- `src/voluseg/_update.py` and the `voluseg.update()` export; README no longer advertises it.
- `src/voluseg/_tools/load_metadata.py` and its top-level export (no callers). Public API is now exactly: `step0_define_parameters … step5_clean_cells`, `load_parameters`, `save_parameters`.
- KLB (`pyklb`) and PIL fallbacks in `_tools/load_volume.py`; the loader supports HDF5, TIFF (`tifffile`), NIfTI, and NWB via `step1`.
- Pickle support in `_tools/parameters.py`; JSON only, with a `ValueError` for other extensions. `test_parameters_json_pickle` replaced by `test_parameters_json_roundtrip` + `test_parameters_unsupported_extension`.
- Docusaurus blog (`blog/`, `blog: false`, navbar/footer links) and `src/pages/markdown-page.md`.
- CDK scaffold `iac/aws_batch/{source.bat,requirements-dev.txt}` (+ `cdk.json` watch entry).
- Stale `docs/voluseg-docs-app/package-lock.json` — CI installs with `yarn --frozen-lockfile`; the npm lock resolved Docusaurus 3.3.2 against a `^3.5.2` manifest and could not be used (`npm ci` fails).

### Pre-existing bugs found while testing Phase 1 end-to-end (all fixed here)
| # | Where | Problem | Fix |
|---|---|---|---|
| 9 | `tests/requirements.txt`, `requirements-docker.txt` | `dandi==0.63.x` is rejected by the DANDI server (`CliVersionTooOldError: requires at least 0.74.0`), so the CI NWB fixture download fails. | `dandi>=0.74.0` (the server enforces a moving minimum; an exact pin re-breaks). |
| 10 | `_tools/sample_data.py` | DANDI renamed its staging instance; `for_dandi_instance("dandi-staging")` raises `KeyError` with a current client. | Use `"dandi-sandbox"` (dandiset 215495 verified present there). |
| 11 | `_tools/clean_signal.py` | `np.ravel(DataFrame)` returns a read-only view under pandas ≥ 3 (Copy-on-Write); the following in-place `+=` raises `ValueError: output array is read-only`. **Step 3 fails on every run with current pandas.** | `baseline_df.to_numpy(copy=True).ravel()`. |
| 12 | `docs/voluseg-docs-app/package.json` | `docusaurus.config.js` imports `remark-math`/`rehype-katex` (added July 2025) but neither was a dependency → `MODULE_NOT_FOUND`; the docs site could not build. | Added `remark-math@6`, `rehype-katex@7` (yarn.lock updated). |
| 14 | `_steps/step4.py`, `_steps/step4e.py` | When every NMF attempt for a block fails, step 4 still wrote `n_cells` = last attempted count (with no cell data), and step 5 then crashed with `np.max` on an empty array. Seen on a 50-timepoint run (all 80 attempts: `array must not contain infs or NaNs`). | step 4 writes `n_cells = 0` for failed blocks; `collect_blocks` raises a clear `RuntimeError("no cells were detected …")`. Why very short recordings produce NaNs in the NMF is a science question, left open. |
| 13 | `docs/voluseg-docs-app/docusaurus.config.js` | Footer linked `/docs/category/api-reference`, which did not exist because the generated `_steps`/`_tools` were excluded (see §4 Docs); `onBrokenLinks: 'throw'` failed the build. | Render the generated reference (custom `exclude`), which recreates the category page. |

## 4c. Phase 2 — integration fixes (third commit)

- **NWB output metadata** (`_tools/nwb.py`): `write_nwbfile` now takes the parameters dictionary and writes real metadata — `RoiResponseSeries.rate = f_volume`, `grid_spacing = [res_x*ds, res_y*ds, res_z]` micrometers; unknown optical metadata uses NWB conventions (`NaN` wavelengths, `"unknown"` indicator/location) instead of fabricated values (`"V1"`, `"GFP"`, `rate=1.0`, `unit="lumens"`).
- **Dual output** (`_steps/step5.py`): `nwb_output=True` now writes the NWB file *in addition to* `cells0_clean.hdf5` instead of replacing it. This also fixes a latent bug: completion is detected via the HDF5 file, so NWB-only runs never registered as complete and their `volumes/`/`cells/` intermediates were never cleaned up.
- **Console script**: new `src/voluseg/cli.py` (Typer), installed as `voluseg` (`[project.scripts]`); `app/app.py` is now a thin shim so the container entry point is unchanged. Adds the previously missing `--dim-order`, `--dir-transform`, `--nwb-output` options, a `--version` flag, and aligns `--parallel-extra` with the model default (True). `typer` added to requirements; `voluseg.__version__` exposed.
- **Comparison test enabled** (`tests/test_voluseg.py`): the NWB fixture now uses the same `ds` as the h5 fixture (the two sample datasets were verified to be bit-identical, transposed), and `compare_results_nwb_and_h5_dir` is renamed `test_compare_…` so pytest collects it (it skips if the reduced fixture yields zero cells); `test_save_result_as_nwb` passes parameters for metadata.

## 4d. Phase 3 — ANTsPy backend, release and community infrastructure (fourth commit)

### ANTs CLI -> ANTsPy (grant Aim 1, months 1-6)
- `_tools/ants_registration.py` and `_tools/ants_transformation.py` reimplemented on ANTsPy (`ants.registration` / `ants.apply_transforms`); `_steps/step2.py` no longer builds shell commands or calls `os.system`.
- The multi-resolution schedules for `high`/`medium`/`low` reproduce the historical CLI settings (`1000x500x250x125` iterations, `12x8x4x2` shrink, `4x3x2x1` smoothing, MI/mattes 32 bins, 25% sampling); the old string-surgery `cmd.replace(...)` quality switching is gone.
- Transform files keep the same names and ITK `.mat` format, so `registration="transform"` reuse and `scipy.io.loadmat` reading are unchanged.
- **Semantic change**: `opts_ants` is now a dict of `ants.registration` keyword arguments (e.g. `{"aff_metric": "meansquares"}`) instead of raw CLI flags. Documented in `parameters.mdx`.
- Removed: ANTs binary downloads from the Dockerfile (with `wget`/`unzip`) and from both CI install steps; the "install ANTs" prerequisite from README and docs. `antspyx` added to requirements.
- Dropped with the rewrite: the unused non-rigid transform types in the old command builder ('t'/'i'/'a'/'s'/'b'; only rigid was ever called) and the CLI retry fallbacks (the "change initialization" retry was a no-op — its search string never occurred in the built command — and the dimensionality-2 fallback is obsolete: ANTsPy handles the single-plane volumes in this repo's own sample data directly).
- Validation (see section 5): transforms agree with the CLI baseline to sub-voxel precision across all 200 volume pairs (rotation identical; translation max 0.47 um, median 0.07 um), registration is ~2x faster, and on the full 1000-volume dataset the pipeline detects 904 cells vs. the CLI baseline's 609 with all 4 blocks factorized.

### "Bug 15" - reclassified as intended behavior (guard reverted)
- Initial reading: `nnmf_sparse` divides timeseries by their means without a
  zero guard; a dead component produces NaN/inf, `lstsq` raises, and the
  block attempt is scrapped. A guard was briefly added and validated
  (counts rose to ~1456-1494 and became length-consistent).
- **Maintainer verdict: this is a feature, not a defect.** The NaN-triggered
  abort plus step 4's fraction-reduction loop is an adaptive model-order
  selection: when too many components are requested, factorization fails
  and is retried with fewer, stronger peak voxels, keeping detected cells
  conservative and well-supported. The guard disabled exactly that
  mechanism (hence the count inflation).
- The guard has been reverted; the original math is restored with a
  prominent code comment marking the behavior as intentional so it is not
  "fixed" again. Consequence to note: in marginal regimes the mechanism is
  sensitive to sub-voxel input differences (ANTsPy vs CLI on the reduced
  200-timepoint sample: 15 vs 98 cells; on the full dataset: 904 vs 609,
  both healthy).
- Kept (with maintainer review welcome): the two *bookkeeping* fixes from
  bug 14 - a block whose every retry fails now records `n_cells = 0`
  instead of a phantom count, and step 5 raises a clear "no cells were
  detected" error instead of crashing on an empty array. These only fire
  after the retry mechanism is fully exhausted, so they do not alter it.

### Release and community infrastructure (grant Aim 3)
- `CHANGELOG.md` (Keep-a-Changelog format), version bumped to 0.2.0 (semantic versioning from here on).
- `CONTRIBUTING.md` (dev setup, tests, PR flow), `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), issue templates (bug report, feature request) and a PR template under `.github/`.
- PyPI publication is prepared (console script, version, metadata) but the actual upload is the maintainer's call — the docs' `pip install voluseg` remains aspirational until then.

## 4e. Stable-release audit — 2024-03 parity, descoping, CI hygiene (fifth commit)

Instruction: the `2024-03` release is the stable reference; every method in it
stays. Additions since then stay only if they solve a specific problem, are
not over-engineered, and do not make the pipeline fragile.

### 2024-03 method parity
- All step 1–5 algorithms verified intact (diffs vs. the tag are Spark→Dask
  plumbing, formatting/typing, the ANTsPy backend, and the NMF guard).
- **Restored `planes_packed`** (dropped upstream in `8993400`, Feb 2025):
  single-plane imaging with planes packed into each volume file; each plane
  becomes its own volume (`_PLN###` suffix) and `res_z` is set to
  `diam_cell`. Re-implemented in step 0/1 on Dask, exposed in the CLI, and
  covered by a new synthetic-data test. Not supported for NWB input
  (explicit error).
- **Restored `registration_restrict`** (same removal): '1'/'0' flags
  restricting transform parameters, mapped to ANTsPy's
  `restrict_transformation`; as in 2024-03, the center-of-mass
  initialization is dropped when a restriction is set. Pydantic-validated,
  CLI-exposed, unit-tested.
- Restriction verified functionally: with `1x1x1x1x1x0`, z-translation is
  exactly 0 across a 5-volume step-2 run.
- **Equivalence nuance recorded**: on a synthetic 3-voxel wrap-rolled
  volume, neither backend recovers the shift (CLI and ANTsPy produce the
  identical transform and warped correlation, 0.8862) — the historical
  registration settings barely move from their initialization on this
  single-plane sample. Not a regression (backends match exactly); flagged
  as a science-QA item for large-motion datasets.

### Descoped (failed the criteria; approved by the user)
- `iac/aws_batch/` CDK stack, `_tools/aws.py`, the S3-export branch of the
  CLI, the `[aws]` extra, `boto3` pin, and the AWS docs page. Rationale:
  ~600 lines of cloud plumbing that solves no current problem (grant
  schedules IaC for months 19–24, multi-cloud), was never exercised by
  tests, and had already yielded three configuration bugs. Recoverable from
  git history when that milestone arrives.
- `.DS_Store` (accidentally committed by the Phase 3 `git add -A`) removed
  and ignored.

### CI hygiene (approved by the user)
- Docker workflow: PRs only build the image; only pushes to `master`
  publish `:latest` — PR branches no longer create GHCR tags.
- Docs workflow: no longer auto-commits generated API-reference files back
  to the branch (that pattern created the stale-docs mess cleaned up in
  Phase 0); the reference is generated at build time.

## 4f. Fragility audit of the keep-set (sixth commit)

Question: of the things we are keeping, is anything still fragile?

### Fixed here
- **Remote NWB streaming had an undeclared dependency**: `fsspec`'s http
  backend needs `aiohttp`, which nothing in a plain `pip install voluseg`
  provided (it only arrived via test-only packages). A user calling the
  documented remote-NWB ingestion would hit ImportError. `fsspec` and
  `aiohttp` are now declared. Verified by streaming the DANDI archive
  directly: correct HDF5 signature read from the remote 394 GB NWB file,
  and the (CI-skipped) `test_nwb_remote` streamed and wrote 1001 volumes
  before aborting on local disk space (see cache note below). Two
  verification notes:
  - On macOS with python.org framework Python, aiohttp cannot find the
    system CA store and raises `SSLCertVerificationError` (surfaced by
    fsspec as a misleading `FileNotFoundError`); fix with
    `export SSL_CERT_FILE=$(python -m certifi)`. Environment quirk, not
    a voluseg issue; no code change.
  - `open_nwbfile_remote` caches remote blocks into `dir_output` with no
    size bound; against a 394 GB archive file this filled tens of GB of
    local disk during one step-1 pass. Left as-is (cache policy is a
    design decision), but flagged: large remote runs need scratch space
    comparable to the data actually read, or a bounded/blockcache
    strategy in a future revision.
- `antspyx` pinned in `requirements-docker.txt` (`==0.6.3`) like every
  other dependency there — registration numerics in the published
  container cannot drift with library releases.
- The `pydoc-markdown` fork is pinned to a commit (`4919c1b6`) instead of
  a moving `@develop` branch.

### Known-fragile, deliberately left (with reasons)
- **Bare `except:` clauses in the science path** (10, e.g. `load_volume`
  returns `None` for any failure, including a corrupt file). Changing
  error-handling changes pipeline behavior on partial data — after the
  NMF-guard lesson, that is a maintainer decision, not a cleanup.
- **Sample-data hosting**: the h5 sample is a hardcoded Google Drive link
  (no checksum) and the NWB sample lives on the wipeable DANDI *sandbox*.
  Fixing this requires the maintainer to host the data somewhere durable
  (e.g. a real DANDI dandiset); code can then point at it.
- **`requirements.txt` is unpinned** (by design — it is a library);
  the pandas-3 breakage shows the risk, but adding upper bounds is a
  maintenance-policy choice for the maintainer. The Docker image is fully
  pinned, so users have a reproducible option today.
- **`remove_small_objects(min_size=…)` deprecation** (skimage ≥ 0.26 warns;
  removal promised for 2.0): migration is NOT mechanical — empirically, the
  documented mapping (`max_size = thr - 1`) does not reproduce legacy
  behavior on test data, so the legacy call stays until the semantics are
  pinned down with the maintainer.
- `.nwb`/remote input detection is substring-based (`".nwb" in dir_input`);
  a directory whose *name* contains ".nwb" would be misrouted. Cosmetic
  risk; left for a future tightening.

## 4g. Docs migration to Quarto; CI enabled on the branch (seventh commit)

- **Why (user-directed, and it fits the fragility razor)**: the Docusaurus
  site carried a ~1,000-package npm tree — the source of GitHub's "206
  vulnerabilities" banner (all Dependabot npm alerts against
  `docs/voluseg-docs-app`; the only Actions history on `master` is failing
  npm auto-update jobs) — plus two lockfiles and a personal pydoc-markdown
  fork. Quarto is a single CLI; pages are plain markdown; quartodoc reads
  NumPy docstrings natively, so the fork dependency is retired outright.
- Pages were ported verbatim (only frontmatter keys and one absolute link
  changed); math renders via Quarto's built-in support. Generated files
  (`docs/reference/`, `docs/_site/`) are gitignored and rebuilt by CI —
  the auto-commit failure mode cannot recur.
- **Note for the grant**: Aim 3 names Docusaurus explicitly; the deliverable
  (versioned, searchable docs with generated API reference) is unchanged,
  but the maintainer should be aware of the tooling substitution.
- **CI status finding**: no workflow had ever run on this branch — all
  triggers were master/PR-only, so "is CI broken?" was unanswerable. The
  three workflows now temporarily include this branch (docs and docker in
  build-only mode; Pages deploy and image publish stay master-gated).
  Remove the temporary trigger lines at merge.

## 5. Verification performed

Local machine has no ANTs binary and system Python is 3.14, so the full
pipeline cannot run here. What was checked in a Python 3.12 venv:

- `python -m py_compile` on every `.py` in `src/`, `app/`, `tests/` — OK.
- `pyflakes src app tests` — only expected re-export notices in `__init__.py`
  and one pre-existing shadowed `np` import in `step1.py`.
- `yamllint` on workflows — only pre-existing style warnings.
- `import voluseg` and `python app/app.py --help` — OK.
- Bug 1 reproduced (`ValidationError`) with the old `opts_ants=""`, and the
  fixed path (`{}`, `""`, `'{"verbose":"1"}'`) parses correctly.
- With the h5 sample dataset downloaded via `download_sample_data`:
  `pytest -k "parameters_json_pickle or load_parameters or h5_dir_step_1"`
  → **3 passed** (step 0 and step 1 on real data; steps 2–5 need ANTs).
- `step1_process_volumes` run with `planes_pad=1`, `registration="none"` on two
  sample volumes: output z-extent 1 → 3, confirming the `np.pad` change.

### Phase 1 verification (ANTs 2.5.3 macOS-ARM64 binaries on PATH; Python 3.12; pandas 3.0.5, numpy 2.5.2, scipy 1.18.1, scikit-image 0.26.0, dask 2026.8.0)

- `py_compile`, `pyflakes`, `yamllint`, `import voluseg` — clean; public API is exactly the 6 steps + `load_parameters`/`save_parameters`.
- Repo test suite, `-k "parameters or h5_dir or save_result"` (steps 1–5 on the h5 sample + NWB export): **9 passed** in 9 min 16 s.
- Full pipeline, steps 0–5, on the first **200** example volumes (`registration="high"`, `diam_cell=5.0`, `f_volume=2.0`): 5.4 min, **98 cells**, all 18 output checks passed (file set, 200 transforms, `mean_timeseries` shape/finite, `cells0_clean.hdf5` shapes/dtypes/coordinate bounds/`volume_id`, intermediates removed). Mask plot inspected: brain mask covers the tissue, midline excluded.
- Docs site: `yarn install --frozen-lockfile && yarn build` succeeds; API Reference category and `_steps`/`_tools` pages render; no `/blog` output.
- New deprecation seen (not changed): `skimage.morphology.remove_small_objects(min_size=…)` → `max_size` in 0.26 with an off-by-one semantic change (`<=` instead of `<`); `requirements-docker.txt` still pins 0.24, so a compat shim is needed before switching.
- Full pipeline on **all 1000** example volumes: 9.0 min (step 4: 8.0 min), **609 cells**, all 18 output checks passed.
- Same 200 volumes with `nwb_output=True`: 5.1 min, `cells0_clean.nwb` written; **98 ROIs** in `PlaneSegmentation` and `RoiResponseSeries` shape (200, 98) — identical cell count to the HDF5 run, so the two writers agree. (A 50-volume attempt produced zero cells and exposed bug 14; 50 timepoints is below what the NMF needs.)
- Full pipeline with the **NWB sample file as input** (`ds=1`, 200 timepoints): all 18 checks passed, **240 cells** at full resolution; step 4 took 3.0 h (full-resolution blocks are ~4x larger — worth revisiting default `ds` guidance for NWB inputs).

### Phase 3 verification (ANTsPy 0.6.x backend; NO ANTs binaries on PATH)

- Full test suite with no system ANTs installed: **11 passed** — before the NMF guard (13 min 51 s) and again after it (38 min 20 s; slower because factorization now succeeds at the full peak fraction instead of failing down to the last fallback).
- Registration equivalence: all 200 transform pairs vs. the CLI baseline — rotation part identical, translation max 0.47 um / median 0.07 um (sub-voxel); registration ~2x faster (10 s vs 18 s for 1000 volumes).
- End-to-end, full 1000 volumes: pre-guard 904 cells (4/4 blocks, 33 retries) vs. CLI baseline 609; post-guard **1494 cells, 4/4 blocks, 0 retries**.
- *(Historical - guard since reverted per maintainer)* End-to-end, 200 volumes: post-guard **1456 cells, 0 retries** — cell count is now consistent across recording lengths (1456 vs 1494), where pre-guard it collapsed with recording length (98 vs 609), because blocks no longer degrade to tiny peak fractions.
- Footprints inspected visually: dense, uniform tiling of the brain mask (74% coverage, median 56 voxels/cell), clear calcium transients in dF/F traces.
- **Honest caveat for reviewers**: the guard changes the NMF's effective operating point (by design — the fraction-reduction loop was a workaround for the crash it fixes). The detected-cell population is much larger than the historical prototype's on this sample; scientific validation of cell quality against the published results (Mu 2019 / Yang 2022 pipelines) is a maintainer task before a release is cut.
- Docs site rebuilt cleanly after all Phase 3 doc edits.

Things that still need a CI run or a real environment: the Docker image
build, the ANTs-dependent steps 2–5, and the AWS Batch path.

## 6. Larger items for later (not mechanical, from the strategy doc)

- **ANTs → ANTsPy** (Aim 1, months 1–6): replace `os.system(antsRegistration …)` in `step2.py` with `ants.registration`; removes the system-binary prerequisite and the `cmd.replace(...)` string surgery for `medium`/`low` quality.
- **Nextflow / step modularity** (Aim 1): steps are already idempotent (skip-if-output-exists), which makes wrapping them straightforward.
- **Windows CI** (Aim 1 deliverable 4): commented out in `run_tests.yaml`; blocked on ANTs.
- **NWB output metadata** (Aim 2): bug 8 above; also `nwb_output=True` skips the HDF5 output entirely — consider writing both.
- **Streaming NWB test** (`test_nwb_remote`) is skipped in CI for memory; `fsspec`/`aiohttp` are not declared dependencies for the remote path.
- **Aim 3 infra missing**: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue/PR templates, `CHANGELOG.md`, git tags / semantic versioning (`version = "0.1.0"` is static), PyPI release (docs say `pip install voluseg`, but only the git install works).
- `docs/requirements-docs.txt` pins a personal fork of `pydoc-markdown` (`luiztauffer/pydoc-markdown@develop`) — sustainability risk. *Investigated during Phase 3: the fork exists because upstream 4.8.2 has no `numpy` docstring processor (`'numpy' is not a valid type ID`), which this project's NumPy-style docstrings need. Keeping the fork for now; the durable fix is to vendor the small numpy processor or upstream it.*
- `requirements.txt` vs `requirements-docker.txt` are two sources of truth (unpinned vs pinned); consider a lock file or `pip-compile`.
- Bare `except:` blocks (10 in `src/`) swallow real errors, e.g. `load_volume` returns `None` for any failure including a corrupt file.
