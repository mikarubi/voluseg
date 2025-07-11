---
sidebar_label: sparseness_projection
title: tools.sparseness_projection
---

#### sparseness\_projection

```python
def sparseness_projection(Si: np.ndarray,
                          s: float,
                          at_least_as_sparse: bool = False) -> np.ndarray
```

Hoyer sparseness projection.

**Arguments**

* **Si** (`np.ndarray`): Input signal.
* **s** (`float`): Sparseness parameter.
* **at_least_as_sparse** (`bool, optional`): Enforce at least as sparse, by default False.

**Returns**

* `np.ndarray`: Sparse signal.

