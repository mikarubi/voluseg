---
sidebar_label: save_volume
title: voluseg._tools.save_volume
---

#### save\_volume

```python
def save_volume(fullname_ext: str,
                volume: np.ndarray,
                affine_matrix: np.ndarray = None) -> Union[bool, None]
```

Save volume in output format.
Formats currently accepted are: nifti and hdf5.

Parameters
----------
fullname_ext : str
    Full name of volume with extension.
volume : np.ndarray
    Volume as numpy array.
affine_matrix : np.ndarray
    Affine matrix for nifti format.

Returns
-------
bool or None
    True if volume was saved successfully, None if volume could not be saved.

