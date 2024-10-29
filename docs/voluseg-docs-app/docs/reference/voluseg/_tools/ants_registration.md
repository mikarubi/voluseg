---
sidebar_label: ants_registration
title: voluseg._tools.ants_registration
---

#### ants\_registration

```python
def ants_registration(dir_ants: str,
                      in_nii: str,
                      ref_nii: str,
                      out_nii: str,
                      prefix_out_tform: str,
                      typ: str,
                      in_tform: str = None,
                      restrict: str = None) -> str
```

ANTs registration.

Parameters
----------
dir_ants : str
    Path to ANTs directory.
in_nii : str
    Input nifti file.
ref_nii : str
    Reference nifti file.
out_nii : str
    Output nifti file.
prefix_out_tform : str
    Prefix for output transformation files.
typ : str
    Type of transformation.
in_tform : str (optional)
    Initial transformation file. Default is None.
restrict : str (optional)
    Restrict deformation. Default is None.

Returns
-------
str
    ANTs registration command.

