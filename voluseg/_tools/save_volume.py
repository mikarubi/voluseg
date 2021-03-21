def save_volume(fullname_ext, volume, affine_mat=None):
    '''save volume in hdf5 or nifti format'''
    
    import h5py
    import nibabel
    from voluseg._tools.constants import dtype
    
    try:
        volume = volume.astype(dtype)
        ext = '.'+fullname_ext.split('.', 1)[1]
        
        if ('.h5' in ext) or ('.hdf5' in ext):
            with h5py.File(fullname_ext, 'w') as file_handle:
                file_handle.create_dataset('volume', data=volume, compression='gzip')
        elif ('.nii' in ext) or ('.nii.gz' in ext):
            nii = nibabel.Nifti1Image(volume, affine_mat)
            nii.header['qform_code'] = 2      # make codes consistent with ANTS
            nii.header['sform_code'] = 1      # 1 scanner, 2 aligned, 3 tlrc, 4 mni.
            nibabel.save(nii, fullname_ext)
        else:
            raise Exception('unknown extension.')
        
        return True
    
    except:
        return None
