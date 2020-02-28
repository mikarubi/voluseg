def align_images(parameters):
    '''register images to a single middle image'''
    
    # do not run if registration is set to none
    if not parameters['registration']:
        return
    
    import os
    import h5py
    import shutil
    import nibabel
    import numpy as np
    from scipy import io
    from copy import deepcopy
    from types import SimpleNamespace
    from voluseg._tools.nii_image import nii_image
    from voluseg._tools.ants_registration import ants_registration
    from voluseg._tools.evenly_parallelize import evenly_parallelize
    from voluseg._steps.step1 import process_images as step1_process_images

    p = SimpleNamespace(**parameters)
    
    volume_nameRDD = evenly_parallelize(p.volume_names)
    for color_i in range(p.n_colors):
        if os.path.isfile(os.path.join(p.dir_output, 'volume%d.hdf5'%(color_i))):
            continue
                            
        dir_volume = os.path.join(p.dir_output, 'volumes', str(color_i))
        fullname_reference = os.path.join(dir_volume, 'reference_original.nii.gz')
        if not os.path.isfile(fullname_reference):
            fullname_lt_2 = os.path.join(dir_volume, p.volume_names[p.lt//2]+'_original.nii.gz')
            shutil.copyfile(fullname_lt_2, fullname_reference)
            
        dir_transform = os.path.join(p.dir_output, 'transforms', str(color_i))
        os.makedirs(dir_transform, exist_ok=True)        
        def register_volume(tuple_name_volume):
            os.environ['ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS'] = '1'
            name_volume = tuple_name_volume[1]
            fullname_original = os.path.join(dir_volume, name_volume+'_original.nii.gz')
            fullname_aligned = os.path.join(dir_volume, name_volume+'_aligned.nii.gz')
            fullname_aligned_hdf = fullname_aligned.replace('.nii.gz', '.hdf5')
            if os.path.isfile(fullname_aligned):
                try:
                    volume_aligned = nibabel.load(fullname_aligned).get_data()
                    return
                except:
                    pass
            if os.path.isfile(fullname_aligned_hdf):
                try:
                    with h5py.File(fullname_aligned_hdf) as file_handle:
                        volume_aligned = file_handle['V3D'][()].T
                        return
                except:
                    pass
                
            cmd = ants_registration(
                dir_ants = p.dir_ants,
                in_nii = fullname_original,
                ref_nii = fullname_reference,
                out_nii = fullname_aligned,
                prefix_out_tform = os.path.join(dir_transform, name_volume+'_tform_'),
                typ = 'r'
            )
            if p.registration=='high':
                pass
            elif p.registration=='medium':
                cmd = cmd.replace('[1000x500x250x125]','[1000x500x250]')\
                         .replace('12x8x4x2', '12x8x4')\
                         .replace('4x3x2x1vox', '4x3x2vox')
            elif p.registration=='low':
                cmd = cmd.replace('[1000x500x250x125]','[1000x500]')\
                         .replace('12x8x4x2', '12x8')\
                         .replace('4x3x2x1vox', '4x3vox')
            else:
                raise Exception('unknown registration type.')
         
            flag = os.system(cmd)
            if flag:
                flag = os.system(cmd.replace('.nii.gz,1]', '.nii.gz,0]'))
            if flag and nibabel.load(fullname_original).shape[2]==1:
                os.system(cmd.replace('--dimensionality 3', '--dimensionality 2'))
                volume_input = nibabel.load(fullname_aligned).get_data()[:, :, None]
                nibabel.save(nii_image(volume_input, p.affine_mat), fullname_aligned)
                
            if os.path.isfile(fullname_aligned):
                try:
                    volume_aligned = nibabel.load(fullname_aligned).get_data()
                    os.remove(fullname_original)
                except:
                    pass
            else:
                raise Exception('image %s not registered: flag %d.'%(name_volume, flag))
                                
        volume_nameRDD.foreach(register_volume)
        
        while 1:
            # check for misregistered images
            def get_transform(tuple_name_volume):
                name_volume = tuple_name_volume[1]
                filename_transform = os.path.join(dir_transform, name_volume+'_tform_0GenericAffine.mat')
                return io.loadmat(filename_transform)['AffineTransform_float_3_3']
            
            # get transforms and ensure all transforms are available
            volume_transforms = np.array(volume_nameRDD.map(get_transform).collect())[:,:,0]
            assert(len(volume_transforms) == p.lt)
            
            # get normalized (z-score) differences in motin parameters
            diff_left = np.abs(np.r_[np.zeros((1, 12)), np.diff(volume_transforms, axis=0)])
            diff_right = np.abs(np.r_[np.diff(volume_transforms[::-1], axis=0)[::-1], np.zeros((1, 12))])
            diff_mean = np.maximum(diff_left / diff_left.mean(0), diff_right / diff_right.mean(0)).mean(1)
            diff_zscore = (diff_mean - diff_mean.mean()) / diff_mean.std()
            
            # if some volumes are misaligned
            idx_misaligned = diff_zscore > 10
            if np.any(idx_misaligned):
                print('misaligned', np.where(idx_misaligned))
                # copy and modify original parameters
                original_parameters = deepcopy(parameters)    
                parameters['volume_names'] = parameters['volume_names'][idx_misaligned]
                p = SimpleNamespace(**parameters)
                p.registration = 'high'
            
                def remove_aligned(tuple_name_volume):
                    name_volume = tuple_name_volume[1]
                    fullname_aligned = os.path.join(dir_volume, name_volume+'_aligned.nii.gz')
                    os.remove(fullname_aligned)
                
                volume_misaligned_nameRDD = evenly_parallelize(p.volume_names)
                volume_misaligned_nameRDD.foreach(remove_aligned)
                step1_process_images(parameters)
                volume_misaligned_nameRDD.foreach(register_volume)
                
                parameters = deepcopy(original_parameters)
                p = SimpleNamespace(**parameters)
    
