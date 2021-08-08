def ants_transformation(dir_ants, in_nii, ref_nii, out_nii, in_tform, interpolation='Linear'):
    '''application of ants transform'''
    
    import os

    antsTransformation_call = ' '.join([
        os.path.join(dir_ants, 'antsApplyTransforms'),
        '--dimensionality 3',
        '--input', in_nii,
        '--reference-image', ref_nii,
        '--output', out_nii,
        '--interpolation', interpolation,
        '--transform', in_tform,
        '--float'
    ])

    return(antsTransformation_call)
