---
sidebar_label: get_volume_name
title: tools.get_volume_name
---

#### get\_volume\_name

```python
def get_volume_name(fullname_volume: str,
                    dir_prefix: str = None,
                    plane_i: int = None) -> str
```

Get name of volume (with directory prefix and plane suffix).

**Arguments**

* **fullname_volume** (`str`): Full name of volume.
* **dir_prefix** (`str (optional)`): Prefix for directory. Default is None.
* **plane_i** (`int (optional)`): Index of plane. Default is None.

**Returns**

* `str`: Name of volume.

