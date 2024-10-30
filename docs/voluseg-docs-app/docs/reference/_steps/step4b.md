---
sidebar_label: step4b
title: _steps.step4b
---

## os

## Tuple

## np

## h5py

## time

## interpolate

## morphology

## SimpleNamespace

## ali

## hdf

## dtype

#### process\_block\_data

```python
def process_block_data(
    xyz0: Tuple[int, int, int], xyz1: Tuple[int, int, int], parameters: dict,
    color_i: int, lxyz: Tuple[int, int, int], rxyz: Tuple[float, float, float],
    ball_diam: np.ndarray, bvolume_mean: h5py.Dataset,
    bvolume_peak: h5py.Dataset, timepoints: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
```

Load timeseries in individual blocks, slice-time correct, and find similar timeseries.

**Arguments**

* **xyz0** (`Tuple[int, int, int]`): Start coordinates of block.
* **xyz1** (`Tuple[int, int, int]`): End coordinates of block.
* **parameters** (`dict`): Parameters dictionary.
* **color_i** (`int`): Color index.
* **lxyz** (`Tuple[int, int, int]`): Number of voxels in x, y, and z dimensions.
* **rxyz** (`Tuple[float, float, float]`): The resolution of x, y, and z dimensions.
* **ball_diam** (`np.ndarray`): The diameter of a cell-area sphere.
* **bvolume_mean** (`h5py.Dataset`): Spark broadcast variable: volume mean.
* **bvolume_peak** (`h5py.Dataset`): Spark broadcast variable: local intensity maximum volume (peak).
* **timepoints** (`np.ndarray`): Timepoints at which segmentation will be performed.

**Returns**

* `Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]`: Tuple containing: Voxel coordinates, timeseries, peak indices, and similarity matrix of peaks.

