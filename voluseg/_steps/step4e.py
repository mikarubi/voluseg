def collect_blocks(color_i, parameters):
    '''collect cells across all blocks'''
    
    import os
    import h5py
    import numpy as np
    from types import SimpleNamespace
    from voluseg._tools.evenly_parallelize import evenly_parallelize
    
    # set up spark
    import pyspark
    from pyspark.sql.session import SparkSession
    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    
    p = SimpleNamespace(**parameters)
    
    dir_cell = os.path.join(p.dir_output, 'cells', str(color_i))
    
    with h5py.File(os.path.join(p.dir_output, 'volume%d.hdf5'%(color_i)), 'r') as file_handle:
        block_valids = file_handle['block_valids'][()]

    class accum_data(pyspark.accumulators.AccumulatorParam):
        '''define accumulator class'''
        
        def zero(self, val0):
            return [[]] * 3
        
        def addInPlace(self, val1, val2):
            return [val1[i] + val2[i] for i in range(3)]
                        
    # cumulate collected cells
    cell_data = sc.accumulator([[]] * 3, accum_data())
    def add_data(tuple_ii):
        ii = tuple_ii[1]
        try:
            cell_xyz = []
            cell_weights = []
            cell_timeseries = []
            
            with h5py.File(os.path.join(dir_cell, 'block%05d.hdf5'%(ii)), 'r') as file_handle:
                for ci in range(file_handle['n_cells'][()]):
                    cell_xyz.append(file_handle['/cell/%05d/xyz'%(ci)][()])
                    cell_weights.append(file_handle['/cell/%05d/weights'%(ci)][()])
                    cell_timeseries.append(file_handle['/cell/%05d/timeseries'%(ci)][()])
                    
            cell_data.add([cell_xyz, cell_weights, cell_timeseries])
        except KeyError:
            print('block %d is empty.' %ii)
        except IOError:
            print('block %d does not exist.' %ii)
            
    evenly_parallelize(np.argwhere(block_valids).T[0]).foreach(add_data)
    cell_xyz, cell_weights, cell_timeseries = cell_data.value

    # convert lists to arrays
    cn = len(cell_xyz)
    cell_lengths = np.array([len(i) for i in cell_weights])
    cell_xyz_array = np.full((cn, np.max(cell_lengths), 3), -1, dtype=int)
    cell_weights_array = np.full((cn, np.max(cell_lengths)), np.nan)
    for ci, li in enumerate(cell_lengths):
        cell_xyz_array[ci, :li] = cell_xyz[ci]
        cell_weights_array[ci, :li] = cell_weights[ci]
    cell_timeseries_array = np.array(cell_timeseries)

    return cell_xyz_array, cell_weights_array, cell_timeseries_array, cell_lengths
    #    with h5py.File(os.path.join(p.dir_output, 'cells%d_raw.hdf5'%(color_i)), 'w') as file_handle:
    #        file_handle['cell_xyz'] = cell_xyz_array
    #        file_handle['cell_weights'] = cell_weights_array
    #        file_handle['cell_timeseries'] = cell_timeseries_array
    #        file_handle['cell_lengths'] = np.r_[cell_lengths]
    #        file_handle['dimensions'] = np.r_[lxyz, p.lt]
    