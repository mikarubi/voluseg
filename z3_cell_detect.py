def z3():
    # load plane filename
    for frame_i in range(imageframe_nmbr):
        with h5py.File(output_dir + 'brain_mask' + str(frame_i) + '.hdf5', 'r') as file_handle:
            image_mean = file_handle['image_mean'][()].T
            brain_mask = file_handle['brain_mask'][()].T
            image_peak_fine = file_handle['image_peak_fine'][()].T
        
        # broadcast image peaks (for initialization) and image_mean (for renormalization)
        bimage_peak_fine = sc.broadcast(image_peak_fine)
        bimage_mean      = sc.broadcast(image_mean)
    
        # get initial estimate for the number of blocks
        blok_nmbr0 = brain_mask.size / (blok_cell_nmbr * cell_voxl_nmbr)
        
        # get initial block boundaries
        ijk = []
        xyz = []
        if lz == 1:
            blok_part = np.sqrt(blok_nmbr0)
        else:
            blok_part = np.cbrt(blok_nmbr0)
        blok_part = np.round(blok_part).astype(int)
        x0_range = np.unique(np.round(np.linspace(0, lx//ds, blok_part+1)).astype(int))
        y0_range = np.unique(np.round(np.linspace(0, ly//ds, blok_part+1)).astype(int))
        z0_range = np.unique(np.round(np.linspace(0, lz,     blok_part+1)).astype(int))
        for i, x0 in enumerate(x0_range):
            for j, y0 in enumerate(y0_range):
                for k, z0 in enumerate(z0_range):
                    ijk.append([i, j, k])
                    xyz.append([x0, y0, z0])
    
        dim = np.max(ijk, 0)
        XYZ = np.zeros(np.r_[dim+1, 3], dtype=int)
        XYZ[list(zip(*ijk))] = xyz
        
        xyz0 = []
        xyz1 = []
        for i in range(dim[0]):
            for j in range(dim[1]):
                for k in range(dim[2]):
                    xyz0.append(XYZ[i  , j  ,   k])
                    xyz1.append(XYZ[i+1, j+1, k+1])
        
        # get number of bloks and block boudaries
        blok_nmbr = len(xyz0)
        xyz0 = np.array(xyz0)
        xyz1 = np.array(xyz1)
                    
        x0, y0, z0 = xyz0[:, 0], xyz0[:, 1], xyz0[:, 2]
        x1, y1, z1 = xyz1[:, 0], xyz1[:, 1], xyz1[:, 2]
        
        # get indices of remaining blocks to be done and run block detection
        cell_dir = output_dir + 'cell_series/' + str(frame_i)
        os.system('mkdir -p ' + cell_dir)
        blok_lidx = np.ones(blok_nmbr, dtype=bool)
        for i in range(blok_nmbr):
            blok_lidx[i] = np.any(brain_mask[x0[i]:x1[i], y0[i]:y1[i], z0[i]:z1[i]])
            
        print(('Number of blocks: total, ' + str(blok_lidx.sum()) + '.'))
            
        # save number and indices of blocks
        with h5py.File(output_dir + 'brain_mask' + str(frame_i) + '.hdf5', 'r+') as file_handle:
            try:
                file_handle['blok_nmbr'] = blok_nmbr
                file_handle['blok_lidx'] = blok_lidx
            except RuntimeError:
                assert(np.allclose(blok_nmbr, file_handle['blok_nmbr'][()]))
                assert(np.allclose(blok_lidx, file_handle['blok_lidx'][()]))
            
        for i in np.where(blok_lidx)[0]:
            filename = cell_dir + '/Block' + str(i).zfill(5) + '.hdf5'
            if os.path.isfile(filename):
                try:
                    with h5py.File(filename, 'r') as file_handle:
                        if ('success' in list(file_handle.keys())) and file_handle['success'][()]:
                            blok_lidx[i] = 0
                except OSError:
                    pass
    
        print(('Number of blocks: remaining, ' + str(blok_lidx.sum()) + '.'))
                        
        ix = np.where(blok_lidx)[0]
        blok_ixyz01 = list(zip(ix, list(zip(x0[ix], x1[ix], y0[ix], y1[ix], z0[ix], z1[ix]))))
        
        if blok_lidx.any():
            sc.parallelize(blok_ixyz01).foreach(blok_cell_detection)

z3()
