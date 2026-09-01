# Voluseg cleanup: core vs. extras, and what changed on this branch

Branch: `cleanup/mechanical-fixes` (off `master` @ `53065d7`, 2026-09-01).

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

Things that still need a CI run or a real environment: the Docker image
build, the ANTs-dependent steps 2–5, and the AWS Batch path.

## 6. Larger items for later (not mechanical, from the strategy doc)

- **ANTs → ANTsPy** (Aim 1, months 1–6): replace `os.system(antsRegistration …)` in `step2.py` with `ants.registration`; removes the system-binary prerequisite and the `cmd.replace(...)` string surgery for `medium`/`low` quality.
- **Nextflow / step modularity** (Aim 1): steps are already idempotent (skip-if-output-exists), which makes wrapping them straightforward.
- **Windows CI** (Aim 1 deliverable 4): commented out in `run_tests.yaml`; blocked on ANTs.
- **NWB output metadata** (Aim 2): bug 8 above; also `nwb_output=True` skips the HDF5 output entirely — consider writing both.
- **Streaming NWB test** (`test_nwb_remote`) is skipped in CI for memory; `fsspec`/`aiohttp` are not declared dependencies for the remote path.
- **Aim 3 infra missing**: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue/PR templates, `CHANGELOG.md`, git tags / semantic versioning (`version = "0.1.0"` is static), PyPI release (docs say `pip install voluseg`, but only the git install works).
- `docs/requirements-docs.txt` pins a personal fork of `pydoc-markdown` (`luiztauffer/pydoc-markdown@develop`) — sustainability risk.
- `requirements.txt` vs `requirements-docker.txt` are two sources of truth (unpinned vs pinned); consider a lock file or `pip-compile`.
- Bare `except:` blocks (10 in `src/`) swallow real errors, e.g. `load_volume` returns `None` for any failure including a corrupt file.
