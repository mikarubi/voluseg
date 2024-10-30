---
sidebar_label: step1
title: steps.step1
---

## os

## interpolate

## SimpleNamespace

## load\_volume

## save\_volume

## get\_volume\_name

## ori

## ali

## nii

## hdf

## evenly\_parallelize

## open\_nwbfile

## get\_nwbfile\_volume

#### process\_volumes

```python
def process_volumes(parameters: dict) -> None
```

Process original volumes and save them to nifti files.
Performs downsampling and padding if specified in parameters.

**Arguments**

* **parameters** (`dict`): Parameters dictionary.

**Returns**

* `None`

