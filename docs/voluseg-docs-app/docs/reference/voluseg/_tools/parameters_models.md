---
sidebar_label: parameters_models
title: voluseg._tools.parameters_models
---

## ParametersModel Objects

```python
class ParametersModel(BaseModel)
```

#### convert\_array\_to\_list

```python
@model_validator(mode="before")
def convert_array_to_list(cls, values)
```

Validator to automatically convert NumPy arrays to lists.

#### model\_dump

```python
def model_dump(use_np_array: bool = True, *args, **kwargs)
```

Override the model_dump method to convert lists to NumPy arrays (if use_np_array is True)
and Enums to their values.

Parameters
----------
use_np_array : bool, optional
    Convert lists to NumPy arrays (default is True)
*args
    Positional arguments to pass to the parent class
**kwargs
    Keyword arguments to pass to the parent class

Returns
-------
dict
    A dictionary of the model&#x27;s data

