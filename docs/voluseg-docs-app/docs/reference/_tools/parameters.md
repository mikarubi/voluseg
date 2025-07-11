---
sidebar_label: parameters
title: _tools.parameters
---

#### load\_parameters

```python
def load_parameters(filename: str) -> dict
```

Load previously saved parameters from filename.

**Parameters**

* **filename** (`str`): Filename of parameter file.

**Returns**

* `dict`: Parameters dictionary.

#### numpy\_converter

```python
def numpy_converter(obj)
```

Convert NumPy arrays to lists for JSON serialization.

#### save\_parameters

```python
def save_parameters(parameters: dict, filename: str) -> None
```

Save parameters to filename.

**Parameters**

* **parameters** (`dict`): Parameters dictionary.
* **filename** (`str`): Filename of parameter file.

**Returns**

* `None`

