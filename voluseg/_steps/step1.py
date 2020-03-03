def process_images(parameters):
    '''process original images and save into nifti format'''
    
    import os
    import h5py
    import nibabel
    import numpy as np
    from scipy import interpolate
    from types import SimpleNamespace    
    from skimage.external import tifffile
    from voluseg._tools.nii_image import nii_image
    from voluseg._tools.evenly_parallelize import evenly_parallelize
    try:
        import PIL
        import pyklb
    except:
        pass

    p = SimpleNamespace(**parameters)
    
    volume_nameRDD = evenly_parallelize(p.volume_names)
    for color_i in range(p.n_colors):
        if os.path.isfile(os.path.join(p.dir_output, 'volume%d.hdf5'%(color_i))):
            continue
                                                                        
        dir_volume = os.path.join(p.dir_output, 'volumes', str(color_i))
        os.makedirs(dir_volume, exist_ok=True)
        def initial_processing(tuple_name_volume):
            name_volume = tuple_name_volume[1]
            fullname_original = os.path.join(dir_volume, name_volume+'_original.nii.gz')
            fullname_aligned = os.path.join(dir_volume, name_volume+'_aligned.nii.gz')
            fullname_aligned_hdf = fullname_aligned.replace('.nii.gz', '.hdf5')
            if os.path.isfile(fullname_original):
                try:
                    volume_original = nibabel.load(fullname_original).get_data()
                    return
                except:
                    pass
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
            
            try:
                # load input images
                fullname_input = os.path.join(p.dir_input, name_volume+p.ext)
                if ('.tif' in p.ext) or ('.tiff' in p.ext):
                    try:
                        volume_input = tifffile.imread(fullname_input)
                    except:
                        img = PIL.Image.open(fullname_input)
                        volume_input = []
                        for i in range(img.n_frames):
                            img.seek(i)
                            volume_input.append(np.array(img).T)
                        volume_input = np.array(volume_input)
                elif ('.h5' in p.ext) or ('.hdf5' in p.ext):
                    with h5py.File(fullname_input, 'r') as file_handle:
                        volume_input = file_handle[list(file_handle.keys())[0]][()]
                elif ('.klb' in p.ext):
                    volume_input = pyklb.readfull(fullname_input)
                    volume_input = volume_input.transpose(0, 2, 1)
            
                if volume_input.ndim == 2:
                    volume_input = volume_input[None, :, :]
                volume_input = volume_input.transpose(2, 1, 0)
            
                # get dimensions
                lx, ly, lz = volume_input.shape
                                
                # split two-color images into two halves        
                if p.n_colors == 2:
                    # ensure that two-frames have even number of y-dim voxels
                    assert(ly % 2 == 0)
                    ly /= 2
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
                    
                # pad in z if specified
                if p.pad_planes:
                    volume_input = np.lib.pad(
                        volume_input, ((0, 0), (0, 0), (p.pad_planes, p.pad_planes)),
                        'constant', constant_values=(np.percentile(volume_input, 1),)
                    )
                    
                # save image as a nifti file
                nibabel.save(
                    nii_image(volume_input.astype('float32'), p.affine_mat),
                    (fullname_original if p.registration else fullname_aligned)
                )
                                
            except Exception as msg:
                raise Exception('image %s not processed: %s.'%(name_volume, msg))
                
        volume_nameRDD.foreach(initial_processing)
