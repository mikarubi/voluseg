---
sidebar_label: load_metadata
title: voluseg._tools.load_metadata
---

#### load\_metadata

```python
def load_metadata(parameters: dict, filename_channel: str,
                  filename_stack: str) -> dict
```

Fetch z-resolution, exposure time, and stack frequency.

Parameters
----------
parameters : dict
    Parameters dictionary.
filename_channel : str
    Filename XML file containing channel information.
filename_stack : str
    Filename of XML file containing stack information.

Returns
-------
dict
    Parameters dictionary.

