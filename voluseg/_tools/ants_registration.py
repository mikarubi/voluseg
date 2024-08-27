def ants_registration(
    dir_ants,
    in_nii,
    ref_nii,
    out_nii,
    prefix_out_tform,
    typ,
    in_tform=None,
    restrict=None,
):
    """ants registration"""

    import os

    lin_tform_params = " ".join(
        [
            "--metric MI[%s,%s,1,32,Regular,0.25]" % (ref_nii, in_nii),
            "--convergence [1000x500x250x125]",
            "--shrink-factors 12x8x4x2",
            "--smoothing-sigmas 4x3x2x1vox",
        ]
    )
    syn_tform_params = " ".join(
        [
            "--metric CC[%s,%s,1,4]" % (ref_nii, in_nii),
            "--convergence [100x100x70x50x20]",
            "--shrink-factors 10x6x4x2x1",
            "--smoothing-sigmas 5x3x2x1x0vox",
        ]
    )

    initial_moving_transform = in_tform if in_tform else "[%s,%s,1]" % (ref_nii, in_nii)
    antsRegistration_call = " ".join(
        [
            os.path.join(dir_ants, "antsRegistration"),
            (
                "--initial-moving-transform " + initial_moving_transform
                if not restrict
                else ""
            ),
            "--output [%s,%s]" % (prefix_out_tform, out_nii),
            "--dimensionality 3",
            "--float 1",
            "--interpolation Linear",
            "--winsorize-image-intensities [0.005,0.995]",
            "--use-histogram-matching 0",
            ("--restrict-deformation " + restrict if restrict else ""),
            ("--transform Translation[0.1] " + lin_tform_params if "t" in typ else ""),
            ("--transform Rigid[0.1] " + lin_tform_params if "r" in typ else ""),
            ("--transform Similarity[0.1] " + lin_tform_params if "i" in typ else ""),
            ("--transform Affine[0.1] " + lin_tform_params if "a" in typ else ""),
            ("--transform SyN[0.1,3,0] " + syn_tform_params if "s" in typ else ""),
            (
                "--transform BSplineSyN[0.1,26,0,3]" + syn_tform_params
                if "b" in typ
                else ""
            ),
        ]
    )

    return antsRegistration_call
