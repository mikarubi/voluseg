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
    restrict: str = None,
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
    restrict : str (optional)
        Restrict transformation parameters: '1'/'0' flags separated by 'x',
        one per transform parameter (e.g. '1x1x1x1x1x0' for a 3D rigid
        transform with no z-translation). When set, the default
        center-of-mass initialization is disabled (it would violate the
        restriction), matching the behavior of the 2024-03 release.

    Returns
    -------
    None
    """
    import ants  # imported here so that workers initialize ITK independently

    settings = QUALITY_SETTINGS[quality]
    extra = dict(opts_ants or {})
    if restrict:
        extra.setdefault(
            "restrict_transformation",
            tuple(int(v) for v in restrict.split("x")),
        )
        extra.setdefault("initial_transform", "identity")
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
        **extra,
    )
    ants.image_write(output["warpedmovout"], out_nii)
