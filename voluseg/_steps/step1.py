def process_images(parameters):
    '''process original images and save into nifti format'''
    
    import os
    import copy
    import h5py
    import nibabel
    import numpy as np
    from scipy import interpolate
    from types import SimpleNamespace    
    from voluseg._tools.nii_image import nii_image
    from voluseg._tools.load_image import load_image
    from voluseg._tools.plane_name import plane_name
    from voluseg._tools.evenly_parallelize import evenly_parallelize
    
    p = SimpleNamespace(**parameters)
    
    volume_nameRDD = evenly_parallelize(p.volume_names0 if p.planes_packed else p.volume_names)
    for color_i in range(p.n_colors):
        if os.path.isfile(os.path.join(p.dir_output, 'volume%d.hdf5'%(color_i))):
            continue
                                                                        
        dir_volume = os.path.join(p.dir_output, 'volumes', str(color_i))
        os.makedirs(dir_volume, exist_ok=True)
        def initial_processing(tuple_name_volume):
            name_volume = tuple_name_volume[1]
        # try:
            # load input images
            fullname_input = os.path.join(p.dir_input, name_volume+p.ext)
            volume_input = load_image(fullname_input, p.ext)
            
            # get number of planes
            if p.planes_packed:
                name_volume0 = copy.deepcopy(name_volume)
                volume_input0 = copy.deepcopy(volume_input)
                lp = len(volume_input0)
            else:
                lp = 1
            
            for pi in range(lp):
                if p.planes_packed:
                    name_volume = plane_name(name_volume0, pi)
                    volume_input = volume_input0[pi]
                    
                fullname_original = os.path.join(dir_volume, name_volume+'_original.nii.gz')
                fullname_aligned = os.path.join(dir_volume, name_volume+'_aligned.nii.gz')
                fullname_aligned_hdf = fullname_aligned.replace('.nii.gz', '.hdf5')
                if os.path.isfile(fullname_original):
                    try:
                        nibabel.load(fullname_original).get_data()
                        continue
                    except:
                        pass
                if os.path.isfile(fullname_aligned):
                    try:
                        nibabel.load(fullname_aligned).get_data()
                        continue
                    except:
                        pass
                if os.path.isfile(fullname_aligned_hdf):
                    try:
                        with h5py.File(fullname_aligned_hdf) as file_handle:
                            file_handle['V3D'][()].T
                        continue
                    except:
                        pass
                
                if volume_input.ndim == 2:
                    volume_input = volume_input[None, :, :]
                volume_input = volume_input.transpose(2, 1, 0)
                
                # get dimensions
                lx, ly, lz = volume_input.shape
                
                # split two-color images into two halves        
                if p.n_colors == 2:
                    # ensure that two-frames have even number of y-dim voxels
                    assert(ly % 2 == 0)
                    ly //= 2
                    if color_i == 0:
                        volume_input = volume_input[:, :ly, :]
                    elif color_i == 1:
                        volume_input = volume_input[:, ly:, :]
                
                # downsample in the x-y if specified
                if p.ds > 1:
                    if (lx % p.ds) or (ly % p.ds):
                        lx -= (lx % p.ds)
                        ly -= (ly % p.ds)
                        volume_input = volume_input[:lx, :ly, :]
                    
                    # make grid for computing downsampled values
                    sx_ds = np.arange(0.5, lx, p.ds)
                    sy_ds = np.arange(0.5, ly, p.ds)
                    xy_grid_ds = np.dstack(np.meshgrid(sx_ds, sy_ds, indexing='ij'))
                    
                    # get downsampled image
                    volume_input_ds = np.zeros((len(sx_ds), len(sy_ds), lz))
                    for zi in np.arange(lz):
                        interpolation_fx = interpolate.RegularGridInterpolator(
                            (np.arange(lx), np.arange(ly)),
                            volume_input[:, :, zi],
                            method='linear'
                        )
                        volume_input_ds[:, :, zi] = interpolation_fx(xy_grid_ds)
                
                    volume_input = volume_input_ds
                    
                # pad planes as necessary
                if p.registration and p.planes_pad:
                    volume_input = np.lib.pad(
                        volume_input, ((0, 0), (0, 0), (p.planes_pad, p.planes_pad)),
                        'constant', constant_values=(np.percentile(volume_input, 1),)
                    )
                    
                # save image as a nifti file
                nibabel.save(
                    nii_image(volume_input.astype('float32'), p.affine_mat),
                    (fullname_original if p.registration else fullname_aligned)
                )
                
        # except Exception as msg:
        #     raise Exception('image %s not processed: %s.'%(name_volume, msg))
                
        volume_nameRDD.foreach(initial_processing)
