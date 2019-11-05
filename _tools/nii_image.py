def nii_image(data, affine_mat):
    '''convert array to nifti image'''
    
    import nibabel
    
    nii = nibabel.Nifti1Image(data, affine_mat)
    nii.header['qform_code'] = 2      # make codes consistent with ANTS
    nii.header['sform_code'] = 1      # 1 scanner, 2 aligned, 3 tlrc, 4 mni.
    
    return nii
