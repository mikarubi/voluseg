# Volumetric Segmentation Pipeline

Reference: [DOI: 10.1016/j.cell.2019.05.050](https://doi.org/10.1016/j.cell.2019.05.050)

Mu Y*, Bennett DV*, Rubinov M*, Narayan S, Yang CT, Tanimoto M, Mensh BD, Looger LL, Ahrens MB.

Glia accumulate evidence that actions are futile and suppress unsuccessful behavior. Cell 2019 178:27-43.

Contact: Mika Rubinov, `mika.rubinov at vanderbilt.edu`

## Run from Docker Container

Instructions [here](https://github.com/mikarubi/voluseg/blob/master/README-docker.md).

## Dependencies

- `h5py`, `dask`, `scipy`, `scikit-image`, `scikit-learn`, `matplotlib`, `nibabel`, `requests`, `numpy`, `pandas`, `pydantic>=2.8.0`, `pynwb>=2.8.0`, `loguru==0.7.2`
- Advanced Normalization Tools (ANTs) for registration (can install via conda)

## Installation

Use pip to install:
```sh
pip install git+https://github.com/mikarubi/voluseg.git
```

## Example Usage

1. Download an example dataset folder:
	[Example Dataset](https://www.dropbox.com/sh/psrj9lusohj7epu/AAAbj8Jbb3o__pyKTTDxPvIKa?dl=0)

2. Import package and load default parameters.

3. Execute code sequentially to perform cell detection.

4. The final output is in the file `cells0_clean.hdf5` in the output directory.

## Example Code

```python
# set up
import os
import pprint
import voluseg

# check for updates
voluseg.update()

# Download sample data
voluseg._tools.download_sample_data("/path/to/input/")

# set and save parameters
filename_parameters = voluseg.step0_process_parameters(
	 dir_input='/path/to/input/downloaded_data/',
	 dir_output='/path/to/output/directory/',
	 registration='high',
	 diam_cell=5.0,
	 f_volume=2.0
)

# load and print parameters
parameters = voluseg.load_parameters(filename_parameters)
pprint.pprint(parameters)

print("process volumes.")
voluseg.step1_process_volumes(parameters)

print("align volumes.")
voluseg.step2_align_volumes(parameters)

print("mask volumes.")
voluseg.step3_mask_volumes(parameters)

print("detect cells.")
voluseg.step4_detect_cells(parameters)

print("clean cells.")
voluseg.step5_clean_cells(parameters)
```

## Pipeline Output

### parameters.json

- Parameter dictionary.
- `parameters = voluseg.load_parameters('parameters.json')`
- Required as input to individual pipeline steps.

### mask_plots

- Directory of average volume plane images.
- Brain mask superimposed on brain volume.
- Can be used to assess goodness of brain masks.

### transforms directory

- Directory of affine transforms for individual volumes.
- Can be used to assess movement of individual volumes.
- Can be used to register volumes from a concurrent recording.

### volume0.hdf5

- `background`: estimated background fluorescence.
- `block_valids`: indices of blocks used for segmentation.
- `block_xyz0/1`: min/max block xyz coordinates.
- `n_blocks`: total number of blocks.
- `n_voxels_cells`: approximate number of voxels in each cell.
- `thr_intensity`: brain-mask intensity threshold.
- `thr_probability`: brain-mask probability threshold.
- `volume_mean/mask/peak`: volume mean/mask/local peak intensity.

### mean_timeseries.hdf5

- `mean_baseline`: baseline of detrended volume-mean timeseries.
- `mean_timeseries`: detrended volume-mean timeseries.
- `mean_timeseries_raw`: raw volume-mean timeseries.
- `timepoints`: indices of timepoints used for cell segmentation.

### cells0_clean.hdf5

- `background`: estimated background fluorescence.
- `cell_baseline`: computed cell baselines.
- `cell_timeseries`: detrended [+ optionally filtered] cell timeseries.
- `cell_timeseries_raw`: raw cell timeseries (direct output of segmentation).
- `cell_weights`: cell spatial footprints (spatial NMF components).
- `cell_x/y/z`: cell coordinates.
- `n/t`: number of cells/timepoints.
- `volume_id`: cell ids represented on a volume.
- `volume_weight`: cell spatial footprints represented on a volume.
- `x/y/z`: volume dimensions.
