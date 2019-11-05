def ants_transformation(in_nii, ref_nii, out_nii, in_tform, interpolation='Linear'):
    '''application of ants transform'''

    antsTransformation_call = ' '.join([
        dir_ants + '/antsApplyTransforms',
        '--dimensionality 3',
        '--input', in_nii,
        '--reference-image', ref_nii,
        '--output', out_nii,
        '--interpolation', interpolation,
        '--transform', in_tform,
        '--float'
    ])
    os.system(antsTransformation_call)
