def process_volumes(parameters):
    '''process original volumes and save into nifti format'''
    
    import os
    import copy
    import numpy as np
    from scipy import interpolate
    from types import SimpleNamespace    
    from voluseg._tools.load_volume import load_volume
    from voluseg._tools.save_volume import save_volume
    from voluseg._tools.plane_name import plane_name
    from voluseg._tools.constants import ori, ali, nii, hdf
    from voluseg._tools.evenly_parallelize import evenly_parallelize
    
    p = SimpleNamespace(**parameters)
    
    volume_nameRDD = evenly_parallelize(p.volume_names0 if p.planes_packed else p.volume_names)
    for color_i in range(p.n_colors):
        fullname_volmean = os.path.join(p.dir_output, 'volume%d'%(color_i))
        if os.path.isfile(fullname_volmean+hdf):
            continue
        
        dir_volume = os.path.join(p.dir_output, 'volumes', str(color_i))
        os.makedirs(dir_volume, exist_ok=True)
        
        def initial_processing(tuple_name_volume):
            name_volume = tuple_name_volume[1]
        # try:
            # load input volumes
            fullname_input = os.path.join(p.dir_input, name_volume)
            volume = load_volume(fullname_input+p.ext)
            
            # get number of planes
            if p.planes_packed:
                name_volume0 = copy.deepcopy(name_volume)
                volume0 = copy.deepcopy(volume)
                lp = len(volume0)
            else:
                lp = 1
            
            for pi in range(lp):
                if p.planes_packed:
                    name_volume = plane_name(name_volume0, pi)
                    volume = volume0[pi]
                    
                fullname_volume = os.path.join(dir_volume, name_volume)
                # skip processing if volume exists
                if load_volume(fullname_volume+ori+nii) or load_volume(fullname_volume+ali+hdf):
                    continue
                
                if volume.ndim == 2:
                    volume = volume[None, :, :]
                volume = volume.transpose(2, 1, 0)
                
                # get dimensions
                lx, ly, lz = volume.shape
                
                # split two-color volumes into two halves        
                if p.n_colors == 2:
                    # ensure that two-frames have even number of y-dim voxels
                    assert(ly % 2 == 0)
                    ly //= 2
                    if color_i == 0:
                        volume = volume[:, :ly, :]
                    elif color_i == 1:
                        volume = volume[:, ly:, :]
                
                # downsample in the x-y if specified
                if p.ds > 1:
                    if (lx % p.ds) or (ly % p.ds):
                        lx -= (lx % p.ds)
                        ly -= (ly % p.ds)
                        volume = volume[:lx, :ly, :]
                    
                    # make grid for computing downsampled values
                    sx_ds = np.arange(0.5, lx, p.ds)
                    sy_ds = np.arange(0.5, ly, p.ds)
                    xy_grid_ds = np.dstack(np.meshgrid(sx_ds, sy_ds, indexing='ij'))
                    
                    # get downsampled volume
                    volume_ds = np.zeros((len(sx_ds), len(sy_ds), lz))
                    for zi in np.arange(lz):
                        interpolation_fx = interpolate.RegularGridInterpolator(
                            (np.arange(lx), np.arange(ly)),
                            volume[:, :, zi],
                            method='linear'
                        )
                        volume_ds[:, :, zi] = interpolation_fx(xy_grid_ds)
                
                    volume = volume_ds
                    
                # pad planes as necessary
                if p.registration and p.planes_pad:
                    volume = np.lib.pad(
                        volume, ((0, 0), (0, 0), (p.planes_pad, p.planes_pad)),
                        'constant', constant_values=(np.percentile(volume, 1),)
                    )
                    
                # save volume in output directory
                if p.registration:
                    save_volume(fullname_volume+ori+nii, volume, p.affine_mat)
                else:
                    volume = volume.T
                    save_volume(fullname_volume+ali+hdf, volume)
        
        volume_nameRDD.foreach(initial_processing)
        
        # except Exception as msg:
        #     raise Exception('volume %s not processed: %s.'%(name_volume, msg))
