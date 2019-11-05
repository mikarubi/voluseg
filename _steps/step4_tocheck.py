def detect_cells(parameters):    
    import os
    import h5py
    import numpy as np
    from types import SimpleNamespace
    from pyspark.sql.session import SparkSession
    from .._tools.define_blocks import define_blocks
    from .._tools.process_block_data import process_block_data
    from .._tools.ball import ball
        
    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    p = SimpleNamespace(**parameters)
    
    ball_diam = ball(1.0 * p.diam_cell, p.affine_mat)[0]
        
    # load plane filename
    for i_color in range(p.n_colors):        
        if os.path.isfile(os.path.join(p.dir_output, 'cells0%s.hdf5'%(i_color))):
            continue
                                                                        
        dir_cell = os.path.join(p.dir_output, 'cells', str(i_color))
        os.makedirs(dir_cell, exist_ok=True)
        
        with h5py.File(os.path.join(p.dir_output, 'volume%s.hdf5'%(i_color)), 'r') as file_handle:
            volume_mean = file_handle['volume_mean'][()].T
            volume_mask = file_handle['volume_mask'][()].T
            volume_peak = file_handle['volume_peak'][()].T
            if 'n_blocks' in file_handle.keys():
                flag = 0
                n_blocks = file_handle['n_blocks'][()]
                block_valid = file_handle['block_valid'][()]
                xyz0 = file_handle['block_xyz0'][()]
                xyz1 = file_handle['block_xyz1'][()]
            else:
                flag = 1

        # broadcast image peaks (for initialization) and volume_mean (for renormalization)
        bvolume_peak = sc.broadcast(volume_peak)
        bvolume_mean      = sc.broadcast(volume_mean)
        lxyz = volume_mean.shape
        rxyz_ = np.diag(p.affine_mat)
        
        # compute number blocks (do only once)                 
        if flag:
            # get number of voxels in each cell
            xyz0, xyz1 = define_blocks(lxyz, rxyz_, p.diam_cell, p.n_cells_block)

            # get coordinates and number of blocks            
            x0, y0, z0 = xyz0[:, 0], xyz0[:, 1], xyz0[:, 2]
            x1, y1, z1 = xyz1[:, 0], xyz1[:, 1], xyz1[:, 2]
            n_blocks = x0.size
            
            # get indices of masked blocks
            block_valid = np.ones(n_blocks, dtype=bool)
            for i in range(n_blocks):
                block_valid[i] = np.any(volume_mask[x0[i]:x1[i], y0[i]:y1[i], z0[i]:z1[i]])

            # save number and indices of blocks
            with h5py.File(os.path.join(p.dir_output, 'volume%s.hdf5'%(i_color)), 'r+') as file_handle:
                file_handle['n_blocks'] = n_blocks
                file_handle['block_valid'] = block_valid
                file_handle['block_xyz0'] = xyz0
                file_handle['block_xyz1'] = xyz1
                            
        print('Number of blocks, total: %d.'%(block_valid.sum()))
        
        for i in np.where(block_valid)[0]:
            try:
                with h5py.File(os.path.join(dir_cell, 'block%05d.hdf5'%(i)), 'r') as file_handle:
                    if ('success' in file_handle.keys()) and file_handle['success'][()]:
                        block_valid[i] = 0
            except (NameError, OSError):
                pass
    
        print('Number of blocks, remaining: %d.'%(block_valid.sum()))
        ix = np.where(block_valid)[0]
        block_ixyz01 = list(zip(ix, xyz0[ix], xyz1[ix]))
        
        # detect individual cells with sparse nnmf algorithm
        def detect_cells_block(i_xyz0_xyz1):
            os.environ['MKL_NUM_THREADS'] = '1'
            
            i_block, xyz0, xyz1 = i_xyz0_xyz1
            
            (voxel_xyz, voxel_peak_xyz, peak_idx, voxel_timeseries, voxel_peak_similarity) = \
                process_block_data(parameters, bvolume_peak, i_color, xyz0, xyz1, lxyz, rxyz_, ball_diam)
                                
            voxel_percentiles = np.mean(np.square(voxel_timeseries[peak_idx]), 1)
            voxel_percentiles = np.argsort(voxel_percentiles) / len(peak_idx)
                                            
            n_voxels_block = len(voxel_xyz)                        # number of voxels in block
            peak_valdlidx = np.arange(len(voxel_peak_xyz))
        
            frac = 100                                        # decremented if nnmf fails
            for i_iter in range(128):                                 # 0.95**31 = 0.2
                try:
                    # estimate sparseness of each component
                    cmpn_number = np.round(peak_valdlidx.size / (0.5 * p.n_voxels_cell)).astype(int)
        
                    print((i_iter, frac, cmpn_number))
        
        
                except ValueError:
                    detection_success = 0
            
                    frac *= 0.97
                    thr_power_peak = np.percentile(voxel_peak_power, 100 - frac)
                    peak_valdlidx = np.where(voxel_peak_power > thr_power_peak)[0]
                    
                    tic = time.time()
                    cell_weights_vald, cell_timeseries_vald, d = nnmf_sparse(
                        voxel_timeseries_vald, voxel_xyz_vald, cell_spceinit_vald,
                        cell_neibhood_vald, cell_sparsity, cell_percentl,
                        miniter=10, maxiter=100, tolfun=1e-3)
                
                    detection_success = 1
                    print('NMF time: %.1f minutes.\n' %((time.time() - tic) / 60))
                
                    # get cell positions and timeseries, and save cell data
                    with h5py.File(os.path.join(dir_cell, 'block%05d.hdf5'%(i_block)), 'w') as file_handle:
                        if detection_success:
                            for cell_i in range(cell_number):
                                cell_lidx_i = np.nonzero(cell_weights_vald[:, cell_i])[0]
                                cell_position_i = voxel_xyz_vald[cell_lidx_i]
                                cell_weights_i = cell_weights_vald[cell_lidx_i, cell_i]
                                mean_spcevoxel_i = bvolume_mean.value[list(zip(*cell_position_i))]
                                mean_i = np.sum(mean_spcevoxel_i * cell_weights_i) / np.sum(cell_weights_i)
                                cell_timeseries_i = cell_timeseries_vald[cell_i]
                                cell_timeseries_i = cell_timeseries_i * mean_i / np.mean(cell_timeseries_i)
                
                                hdf5_dir = '/cell/' + str(cell_i).zfill(5)
                                file_handle[hdf5_dir + '/cell_position'] = cell_position_i
                                file_handle[hdf5_dir + '/cell_weights'] = cell_weights_i
                                file_handle[hdf5_dir + '/cell_timeseries'] = cell_timeseries_i
                
                        file_handle['cell_number'] = cell_number
                        file_handle['success'] = 1
        
        if block_valid.any():
            sc.parallelize(block_ixyz01).foreach(detect_cells_block)
