---
sidebar_label: parameters_models
title: _tools.parameters_models
---

## DimOrder Objects

```python
class DimOrder(str, Enum)
```

#### xyz

#### xzy

#### yxz

#### yzx

#### zxy

#### zyx

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

#### transform

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

#### input\_dirs

#### dir\_output

#### dir\_transform

#### detrending

#### registration

#### opts\_ants

#### diam\_cell

#### dim\_order

#### nwb\_output

#### ds

#### planes\_pad

#### parallel\_extra

#### save\_volume

#### type\_timepoints

#### timepoints

#### type\_mask

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

#### overwrite

#### convert\_array\_to\_list

```python
@model_validator(mode="before")
def convert_array_to_list(cls, values)
```

Validator to automatically convert NumPy arrays to lists.

