---
sidebar_label: ants_transformation
title: _tools.ants_transformation
---

#### ants\_transformation

```python
def ants_transformation(in_nii: str,
                        ref_nii: str,
                        out_nii: str,
                        in_tform: str,
                        interpolation="Linear") -> str
```

Application of ANTs transform.

**Parameters**

* **in_nii** (`str`): Path to input nifti file.
* **ref_nii** (`str`): Path to reference nifti file.
* **out_nii** (`str`): Path to output nifti file.
* **in_tform** (`str`): Path to input transform file (.mat).
* **interpolation** (`str`): Interpolation method.

**Returns**

* `str`: ANTs transformation command string.

