---
sidebar_label: ants_registration
title: _tools.ants_registration
---

#### ants\_registration

```python
def ants_registration(in_nii: str,
                      ref_nii: str,
                      out_nii: str,
                      prefix_out_tform: str,
                      typ: str,
                      opts_ants: dict = {}) -> str
```

ANTs registration.

**Parameters**

* **in_nii** (`str`): Input nifti file.
* **ref_nii** (`str`): Reference nifti file.
* **out_nii** (`str`): Output nifti file.
* **prefix_out_tform** (`str`): Prefix for output transformation files.
* **typ** (`str`): Type of transformation.
* **opts_ants** (`dict (optional)`): A dictionary of ANTs registration options.

**Returns**

* `str`: ANTs registration command.

