---
sidebar_label: load_volume
title: _tools.load_volume
---

## h5py

## nibabel

## np

## Union

## dtype

#### load\_volume

```python
def load_volume(fullname_ext: str) -> Union[np.ndarray, None]
```

Load volume based on input name and extension.
Supports tiff, hdf5, klb, and nifti formats.

**Arguments**

* **fullname_ext** (`str`): Full name of volume with extension.

**Returns**

* `np.ndarray or None`: Volume as numpy array, or None if volume could not be loaded.

