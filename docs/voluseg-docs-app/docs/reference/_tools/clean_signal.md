---
sidebar_label: clean_signal
title: _tools.clean_signal
---

#### clean\_signal

```python
def clean_signal(parameters: dict,
                 timeseries: np.ndarray) -> Tuple[np.ndarray, np.ndarray]
```

Detrend, filter, and estimate dynamic baseline for input timeseries.

**Parameters**

* **parameters** (`dict`): Parameters dictionary.
* **timeseries** (`np.ndarray`): Input timeseries.

**Returns**

* `Tuple[np.ndarray, np.ndarray]`: TODO - add description

