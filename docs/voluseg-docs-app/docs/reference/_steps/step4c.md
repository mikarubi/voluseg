---
sidebar_label: step4c
title: _steps.step4c
---

#### initialize\_block\_cells

```python
def initialize_block_cells(
    n_voxels_cell: int, n_voxels_block: int, n_cells: int,
    voxel_xyz: np.ndarray, voxel_timeseries: np.ndarray, peak_idx: np.ndarray,
    peak_valids: np.ndarray, voxel_similarity_peak: np.ndarray,
    lxyz: Tuple[int, int, int], rxyz: Tuple[float, float, float],
    ball_diam: np.ndarray, ball_diam_xyz0: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
```

Initialize cell positions in individual blocks.

**Parameters**

* **n_voxels_cell** (`int`): Number of voxels in each cell.
* **n_voxels_block** (`int`): Number of voxels in block.
* **n_cells** (`int`): Number of cells.
* **voxel_xyz** (`np.ndarray`): Voxel coordinates.
* **voxel_timeseries** (`np.ndarray`): Voxel timeseries.
* **peak_idx** (`np.ndarray`): Peak indices.
* **peak_valids** (`np.ndarray`): Valid local-intensity maxima (used to determine number of cells).
* **voxel_similarity_peak** (`np.ndarray`): Similarity between voxels: defined by the combination of spatial proximity
and temporal similarity (the voxels are neighbors of each other and also
correlated with each other).
* **lxyz** (`Tuple[int, int, int]`): Number of voxels in x, y, and z dimensions.
* **rxyz** (`Tuple[float, float, float]`): Resolution of x, y, z dimensions.
* **ball_diam** (`np.ndarray`): Diameter of a sphere that may defines a cell boundary.
* **ball_diam_xyz0** (`np.ndarray`): Midpoint of the sphere.

**Returns**

* `Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]`: TODO - add description

