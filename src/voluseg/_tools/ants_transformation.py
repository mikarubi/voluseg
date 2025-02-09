def ants_transformation(
    in_nii: str,
    ref_nii: str,
    out_nii: str,
    in_tform: str,
    interpolation="Linear",
) -> str:
    """
    Application of ANTs transform.

    Parameters
    ----------
    in_nii : str
        Path to input nifti file.
    ref_nii : str
        Path to reference nifti file.
    out_nii : str
        Path to output nifti file.
    in_tform : str
        Path to input transform file (.mat).
    interpolation : str
        Interpolation method.

    Returns
    -------
    str
        ANTs transformation command string.
    """
    antsTransformation_call = " ".join(
        [
            "antsApplyTransforms",
            "--dimensionality 3",
            "--input",
            in_nii,
            "--reference-image",
            ref_nii,
            "--output",
            out_nii,
            "--interpolation",
            interpolation,
            "--transform",
            in_tform,
            "--float",
        ]
    )
    return antsTransformation_call
