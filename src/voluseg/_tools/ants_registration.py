"""ANTsPy-based rigid registration (replaces the ANTs command-line tools)."""

# registration quality settings (multi-resolution schedule)
QUALITY_SETTINGS = {
    "high": {
        "iterations": (1000, 500, 250, 125),
        "shrink_factors": (12, 8, 4, 2),
        "smoothing_sigmas": (4, 3, 2, 1),
    },
    "medium": {
        "iterations": (1000, 500, 250),
        "shrink_factors": (12, 8, 4),
        "smoothing_sigmas": (4, 3, 2),
    },
    "low": {
        "iterations": (1000, 500),
        "shrink_factors": (12, 8),
        "smoothing_sigmas": (4, 3),
    },
}


def ants_registration(
    in_nii: str,
    ref_nii: str,
    out_nii: str,
    prefix_out_tform: str,
    quality: str = "medium",
    opts_ants: dict = None,
) -> None:
    """
    Rigid registration with ANTsPy.

    Registers `in_nii` to `ref_nii`, writes the aligned volume to `out_nii`
    and the affine transform to ``prefix_out_tform + "0GenericAffine.mat"``.

    Parameters
    ----------
    in_nii : str
        Input (moving) nifti file.
    ref_nii : str
        Reference (fixed) nifti file.
    out_nii : str
        Output nifti file for the aligned volume.
    prefix_out_tform : str
        Prefix for the output transform file.
    quality : str
        Registration quality: 'high', 'medium', or 'low' (multi-resolution
        schedule; matches the historical ANTs CLI settings).
    opts_ants : dict (optional)
        Extra keyword arguments passed to :func:`ants.registration`
        (e.g. ``{"aff_metric": "meansquares"}``).

    Returns
    -------
    None
    """
    import ants  # imported here so that workers initialize ITK independently

    settings = QUALITY_SETTINGS[quality]
    fixed = ants.image_read(ref_nii)
    moving = ants.image_read(in_nii)
    output = ants.registration(
        fixed=fixed,
        moving=moving,
        type_of_transform="Rigid",
        aff_metric="mattes",
        aff_sampling=32,
        aff_random_sampling_rate=0.25,
        aff_iterations=settings["iterations"],
        aff_shrink_factors=settings["shrink_factors"],
        aff_smoothing_sigmas=settings["smoothing_sigmas"],
        outprefix=prefix_out_tform,
        verbose=False,
        **(opts_ants or {}),
    )
    ants.image_write(output["warpedmovout"], out_nii)
