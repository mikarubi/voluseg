---
sidebar_label: step4e
title: _steps.step4e
---

## os

## h5py

## np

## SimpleNamespace

## Tuple

## pyspark

## SparkSession

## hdf

## evenly\_parallelize

#### collect\_blocks

```python
def collect_blocks(
    color_i: int, parameters: dict
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
```

Collect cells across all blocks.

**Arguments**

* **color_i** (`int`): Color index.
* **parameters** (`dict`): Parameters dictionary.

**Returns**

* `Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]`: Tuple of cell block id, cell xyz, cell weights, cell timeseries, and cell lengths.

