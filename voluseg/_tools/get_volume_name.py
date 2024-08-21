import os


def get_volume_name(
    fullname_volume: str,
    dir_prefix: str = None,
    plane_i: str = None,
) -> str:
    """
    Get name of volume (with directory prefix and plane suffix)

    Parameters
    ----------
    fullname_volume : str
        Full name of volume.
    dir_prefix : str
        Prefix for directory.
    plane_i : str
        Plane index.

    Returns
    -------
    str
        Name of volume.
    """
    name_volume = os.path.basename(fullname_volume)

    # add prefix (multiple input directories)
    if dir_prefix is not None:
        name_volume = dir_prefix + "_" + name_volume

    # add suffix (packed planes)
    if plane_i is not None:
        name_volume += "_PLN" + str(plane_i).zfill(3)

    return name_volume
