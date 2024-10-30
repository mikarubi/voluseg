---
sidebar_label: parameters_models
title: _tools.parameters_models
---

## Enum

## np

## BaseModel

## Field

## model\_validator

## Optional

## Detrending Objects

```python
class Detrending(str, Enum)
```

#### standard

#### robust

#### none

## Registration Objects

```python
class Registration(str, Enum)
```

#### high

#### medium

#### low

#### none

## TypeTimepoints Objects

```python
class TypeTimepoints(str, Enum)
```

#### dff

#### periodic

#### custom

## TypeMask Objects

```python
class TypeMask(str, Enum)
```

#### mean

#### geomean

#### max

## ParametersModel Objects

```python
class ParametersModel(BaseModel)
```

#### detrending

#### registration

#### registration\_restrict

#### diam\_cell

#### dir\_ants

#### dir\_input

#### dir\_output

#### dir\_transform

#### ds

#### planes\_pad

#### planes\_packed

#### parallel\_clean

#### parallel\_volume

#### save\_volume

#### type\_timepoints

#### type\_mask

#### timepoints

#### f\_hipass

#### f\_volume

#### n\_cells\_block

#### n\_colors

#### res\_x

#### res\_y

#### res\_z

#### t\_baseline

#### t\_section

#### thr\_mask

#### volume\_fullnames\_input

#### volume\_names

#### input\_dirs

#### ext

#### lt

#### affine\_matrix

#### dim\_order

#### remote

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

**Arguments**

* **use_np_array** (`bool, optional`): Convert lists to NumPy arrays (default is True)
* ***args**: Positional arguments to pass to the parent class
* ****kwargs**: Keyword arguments to pass to the parent class

**Returns**

* `dict`: A dictionary of the model&#x27;s data

