---
sidebar_label: step4d
title: steps.step4d
---

#### nnmf\_sparse

```python
def nnmf_sparse(
        V0: np.ndarray,
        XYZ0: np.ndarray,
        W0: np.ndarray,
        B0: np.ndarray,
        S0: np.ndarray,
        tolfun: float = 1e-4,
        miniter: int = 10,
        maxiter: int = 100,
        timeseries_mean=1.0,
        timepoints: np.ndarray = None,
        verbosity: bool = True) -> Tuple[np.ndarray, np.ndarray, float]
```

Cell detection via nonnegative matrix factorization with sparseness projection.

**Arguments**

* **V0** (`np.ndarray`): Voxel timeseries (voxel_timeseries_valid).
* **XYZ0** (`np.ndarray`): Voxel coordinates (voxel_xyz_valid).
* **W0** (`np.ndarray`): Initial cell weights (cell_weight_init_valid).
* **B0** (`np.ndarray`): Cell neighborhood (cell_neighborhood_valid).
* **S0** (`np.ndarray`): Cell sparseness (cell_sparseness).
* **tolfun** (`float, optional`): Tolerance for convergence, by default 1e-4.
* **miniter** (`int, optional`): Minimum number of iterations, by default 10.
* **maxiter** (`int, optional`): Maximum number of iterations, by default 100.
* **timeseries_mean** (`float, optional`): Mean timeseries value, by default 1.0.
* **timepoints** (`np.ndarray, optional`): Timepoints to use, by default None.
* **verbosity** (`bool, optional`): Print progress, by default True.

**Returns**

* `Tuple[np.ndarray, np.ndarray, float]`: Tuple containing: Spatial footprint, temporal footprint, convergence error.

