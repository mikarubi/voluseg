---
sidebar_label: step4e
title: steps.step4e
---

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

