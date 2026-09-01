"""ANTsPy-based application of a precomputed transform."""


def ants_transformation(
    in_nii: str,
    ref_nii: str,
    out_nii: str,
    in_tform: str,
    interpolation: str = "linear",
) -> None:
    """
    Apply a precomputed affine transform with ANTsPy.

    Parameters
    ----------
    in_nii : str
        Path to input (moving) nifti file.
    ref_nii : str
        Path to reference (fixed) nifti file.
    out_nii : str
        Path to output nifti file.
    in_tform : str
        Path to input transform file (.mat).
    interpolation : str
        Interpolation method (ANTsPy name, e.g. 'linear', 'nearestNeighbor').

    Returns
    -------
    None
    """
    import ants  # imported here so that workers initialize ITK independently

    fixed = ants.image_read(ref_nii)
    moving = ants.image_read(in_nii)
    warped = ants.apply_transforms(
        fixed=fixed,
        moving=moving,
        transformlist=[in_tform],
        interpolator=interpolation,
    )
    ants.image_write(warped, out_nii)
