def collect_blocks_cells(i_color, dir_cell, parameters, lxyz):
    
    import os
    import h5py
    import numpy as np
    from types import SimpleNamespace

    p = SimpleNamespace(**parameters)
                
    print('Creating cells%d.hdf5.'%(i_color))            
            
    with h5py.File(os.path.join(p.dir_output, 'volume%d.hdf5'%(i_color), 'r')) as file_handle:
        n_blocks = file_handle['n_blocks'][()]
        block_xyz0 = file_handle['block_xyz0'][()]

    cell_position = []
    cell_weights = []
    cell_timeseries = []
    for i_block in range(n_blocks):
        try:
            with h5py.File(os.path.join(dir_cell, 'block%05d.hdf5'%(i)), 'r') as file_handle:
                for ci in file_handle['cell']:
                    cell_position.append(file_handle['cell'][ci]['position'][()])
                    cell_weights.append(file_handle['cell'][ci]['weights'][()])
                    cell_timeseries.append(file_handle['cell'][ci]['timeseries'][()])
        except KeyError:
            print('block %d is empty.' %i_block)
        except IOError:
            if block_xyz0[i_block]:
                print('block %d does not exist.' %i_block)

    cn = len(cell_position)
    ln = np.max([len(i) for i in cell_weights])
    cell_position_array = np.full((cn, ln, 3), -1, dtype=int)
    cell_weights_array = np.full((cn, ln), np.nan)
    for i in range(cn):
        j = len(cell_weights[i])
        cell_position_array[i, :j] = cell_position[i]
        cell_weights_array[i, :j] = cell_weights[i]
    cell_timeseries_array = np.array(cell_timeseries)

    with h5py.File(os.path.join(p.dir_output, 'cells%d_raw.hdf5'%(i_color)), 'w') as file_handle:
        file_handle['cell_position'] = cell_position_array
        file_handle['cell_weights'] = cell_weights_array
        file_handle['cell_timeseries'] = cell_timeseries_array
        file_handle['dimensions'] = np.r_[lxyz, p.lt]