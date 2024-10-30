---
sidebar_label: step4a
title: steps.step4a
---

## os

## Tuple

## np

#### define\_blocks

```python
def define_blocks(
        lx: int, ly: int, lz: int, n_cells_block: int, n_voxels_cell: int,
        volume_mask: np.ndarray,
        volume_peak: np.ndarray) -> Tuple[int, bool, np.ndarray, np.ndarray]
```

Get coordinates of individual blocks.

**Arguments**

* **lx** (`int`): Number of voxels in x-dimension.
* **ly** (`int`): Number of voxels in y-dimension.
* **lz** (`int`): Number of voxels in z-dimension.
* **n_cells_block** (`int`): Number of cells in each block.
* **n_voxels_cell** (`int`): Number of voxels in each cell.
* **volume_mask** (`np.ndarray`): Volume mask.
* **volume_peak** (`np.ndarray`): Volume local intensity maxima (peaks).

**Returns**

* `Tuple[int, bool, np.ndarray, np.ndarray]`: Tuple containing: Number of blocks, valid blocks, coordinates of block start,
and coordinates of block end.

