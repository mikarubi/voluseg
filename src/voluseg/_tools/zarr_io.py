"""Zarr input support (4D arrays: time followed by three spatial dimensions)."""


def open_zarr_volume(input_path: str):
    """
    Open a 4D Zarr array from a local or remote store.

    The array must have time as its first axis; the three remaining axes
    are interpreted according to the 'dim_order' parameter, exactly like
    volumes read from individual files (OME-Zarr's t/z/y/x layout matches
    the default 'zyx'). If the store is a group, the array is looked up at
    the conventional keys '0' (OME-Zarr multiscale level 0) and 'data',
    or taken as the group's only array.

    Parameters
    ----------
    input_path : str
        Path or URL of the Zarr store.

    Returns
    -------
    zarr.Array
        The 4D array; indexing with a timepoint yields one 3D volume.
    """
    import zarr

    z = zarr.open(input_path, mode="r")
    if hasattr(z, "shape"):  # the store itself is an array
        arr = z
    else:  # a group: use conventional keys, else the group's only array
        arr = None
        for key in ("0", "data"):
            if key in z:
                arr = z[key]
                break
        if arr is None:
            arrays = list(z.arrays())
            if len(arrays) == 1:
                arr = arrays[0][1]
            else:
                raise Exception(
                    "could not identify a single array in Zarr group '%s'; "
                    "found: %s." % (input_path, sorted(k for k, _ in arrays))
                )
    if arr.ndim != 4:
        raise Exception(
            "Zarr array in '%s' must be 4-dimensional (time followed by "
            "three spatial dimensions); got shape %s." % (input_path, arr.shape)
        )
    return arr
