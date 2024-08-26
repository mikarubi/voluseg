def get_volume_name(fullname_volume, dir_prefix=None, plane_i=None):
    """get name of volume (with directory prefix and plane suffix)"""

    import os

    name_volume = os.path.basename(fullname_volume)

    # add prefix (multiple input directories)
    if dir_prefix is not None:
        name_volume = dir_prefix + "_" + name_volume

    # add suffix (packed planes)
    if plane_i is not None:
        name_volume += "_PLN" + str(plane_i).zfill(3)

    return name_volume
