# volumetric segmentation pipeline #

Reference: https://doi.org/10.1016/j.cell.2019.05.050

Mu Y*, Bennett DV*, Rubinov M*, Narayan S, Yang CT, Tanimoto M, Mensh BD, Looger LL, Ahrens MB.

Glia accumulate evidence that actions are futile and suppress unsuccessful behavior.

Cell 2019 178:27-43.

# dependencies

- Apache Spark

- Advanced Normalization Tools (ANTs)

- h5py, matplotlib, nibabel, numpy, pandas, scipy, scikit-image, scikit-learn

# installation

- use pip to install: `pip install git+https://github.com/mikarubi/voluseg.git`

# example usage

- Download an example dataset folder: 

	https://www.dropbox.com/sh/psrj9lusohj7epu/AAAbj8Jbb3o__pyKTTDxPvIKa?dl=0

- Launch IPython with Spark.

- Import package and load default parameters.

- Set and save parameters (see `voluseg.parameter_dictionary??` for details).

- Execute code sequentially to perform cell detection.

- The final output is in the file `cells0_clean.hdf5` in the output directory.

# example code

```
# set up
import os
import pprint
import voluseg

# check for updates
voluseg.update()

# set and save parameters
parameters0 = voluseg.parameter_dictionary()
parameters0['dir_ants'] = '/path/to/ants/bin/'
parameters0['dir_input'] = '/path/to/input/volumes/'
parameters0['dir_output'] = '/path/to/output/directory/'
parameters0['registration'] = 'high'
parameters0['diam_cell'] = 5.0
parameters0['f_volume'] = 2.0
voluseg.step0_process_parameters(parameters0)

# load and print parameters
filename_parameters = os.path.join(parameters0['dir_output'], 'parameters.pickle')
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

# pipeline output

## parameters.pickle

- parameter dictionary.

- `parameters = voluseg.load_parameters('parameters.pickle')`

- required as input to individual pipeline steps.

## mask_plots

- directory of average volume plane images

- brain mask superimposed on brain volume

- can be used to assess goodness of brain masks

## transforms directory

- directory of affine transforms for individual volumes

- can be used to assess movement of individual volumes

- can be used to register volumes from a concurrent recording

## volume0.hdf5

- `background`: estimated background fluorescence

- `block_valids`: indices of blocks used for segmentation

- `block_xyz0/1`: min/max block xyz coordinates

- `n_blocks`: total number of blocks

- `n_voxels_cells`: approximate number of voxels in each cell

- `thr_intensity`: brain-mask intensity threshold

- `thr_probability`: brain-mask probability threshold

- `volume_mean/mask/peak`: volume mean/mask/local peak intensity

## mean_timeseries.hdf5

- `mean_baseline`: baseline of detrended volume-mean timeseries

- `mean_timeseries`: detrended volume-mean timeseries

- `mean_timeseries_raw`: raw volume-mean timeseries

- `timepoints`: indices of timepoints used for cell segmentation

## cells0_clean.hdf5

- `background`: estimated background fluorescence

- `cell_baseline`: computed cell baselines

- `cell_timeseries`: detrended [+ optionally filtered] cell timeseries

- `cell_timeseries_raw`: raw cell timeseries (direct output of segmentation)

- `cell_weights`: cell spatial footprints (spatial NMF components)

- `cell_x/y/z`: cell coordinates

- `n/t`: number of cells/timepoints

- `volume_id`: cell ids represented on a volume

- `volume_weight`: cell spatial footprints represent on a volume

- `x/y/z`: volume dimensions
