---
sidebar_label: ants_transformation
title: voluseg._tools.ants_transformation
---

#### ants\_transformation

```python
def ants_transformation(dir_ants: str,
                        in_nii: str,
                        ref_nii: str,
                        out_nii: str,
                        in_tform: str,
                        interpolation="Linear") -> str
```

Application of ANTs transform.

Parameters
----------
dir_ants : str
    Path to ANTs binaries.
in_nii : str
    Path to input nifti file.
ref_nii : str
    Path to reference nifti file.
out_nii : str
    Path to output nifti file.
in_tform : str
    Path to input transform file (.mat).
interpolation : str
    Interpolation method.

Returns
-------
str
    ANTs transformation command string.

