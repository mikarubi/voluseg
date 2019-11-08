def collect_blocks(color_i, parameters, lxyz):
    '''collect cells across all blocks'''
    
    import os
    import h5py
    import numpy as np
    from types import SimpleNamespace

    p = SimpleNamespace(**parameters)
    
    dir_cell = os.path.join(p.dir_output, 'cells', str(color_i))    
    
    print('creating cells%d_raw.hdf5.'%(color_i))            
            
    with h5py.File(os.path.join(p.dir_output, 'volume%d.hdf5'%(color_i)), 'r') as file_handle:
        n_blocks = file_handle['n_blocks'][()]
        block_xyz0 = file_handle['block_xyz0'][()]

    # first generate lists
    cell_xyz = []
    cell_weights = []
    cell_timeseries = []
    for ii in range(n_blocks):
        try:
            with h5py.File(os.path.join(dir_cell, 'block%05d.hdf5'%(ii)), 'r') as file_handle:
                for ci in range(file_handle['n_cells'][()]):
                    cell_xyz.append(file_handle['/cell/%05d/xyz'%(ci)][()])
                    cell_weights.append(file_handle['/cell/%05d/weights'%(ci)][()])
                    cell_timeseries.append(file_handle['/cell/%05d/timeseries'%(ci)][()])
        except KeyError:
            print('block %d is empty.' %ii)
        except IOError:
            if block_xyz0[ii]:
                print('block %d does not exist.' %ii)

    # second convert lists to arrays
    cn = len(cell_xyz)
    cell_lengths = np.array([len(i) for i in cell_weights])
    cell_xyz_array = np.full((cn, np.max(cell_lengths), 3), -1, dtype=int)
    cell_weights_array = np.full((cn, np.max(cell_lengths)), np.nan)
    for ci, li in enumerate(cell_lengths):
        cell_xyz_array[ci, :li] = cell_xyz[ci]
        cell_weights_array[ci, :li] = cell_weights[ci]
    cell_timeseries_array = np.array(cell_timeseries)

    with h5py.File(os.path.join(p.dir_output, 'cells%d_raw.hdf5'%(color_i)), 'w') as file_handle:
        file_handle['cell_xyz'] = cell_xyz_array
        file_handle['cell_weights'] = cell_weights_array
        file_handle['cell_timeseries'] = cell_timeseries_array
        file_handle['cell_lengths'] = np.r_[cell_lengths]
        file_handle['dimensions'] = np.r_[lxyz, p.lt]
    