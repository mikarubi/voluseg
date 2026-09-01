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
- Deleted stale generated API-reference folders `docs/.../reference/{tools,steps,update.md}` — superseded by `_tools`, `_steps`, `_update.md` (which CI regenerates); `sidebar.json` did not reference them; `tools/parameter_dictionary.md` documented a removed function.
- `docusaurus.config.js`: `organizationName`/`projectName` were still the template values `facebook`/`docusaurus`.
- `parameters.mdx`: `input_dirs` type updated to `List[str]` (relaxed in `53065d7`).
- `iac/aws_batch/README.md`: replaced the untouched "Welcome to your CDK Python project!" scaffold with a short description and a pointer to the docs page.

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
