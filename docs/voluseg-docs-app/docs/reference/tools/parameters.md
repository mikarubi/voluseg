---
sidebar_label: parameters
title: tools.parameters
---

## pickle

## json

## ParametersModel

#### load\_parameters

```python
def load_parameters(filename: str) -> dict
```

Load previously saved parameters from filename.

**Arguments**

* **filename** (`str`): Filename of parameter file.

**Returns**

* `dict`: Parameters dictionary.

#### save\_parameters

```python
def save_parameters(parameters: dict, filename: str) -> None
```

Save parameters to filename.

**Arguments**

* **parameters** (`dict`): Parameters dictionary.
* **filename** (`str`): Filename of parameter file.

**Returns**

* `None`

