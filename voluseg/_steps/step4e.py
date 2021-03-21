def collect_blocks(color_i, parameters):
    '''collect cells across all blocks'''
    
    import os
    import h5py
    import numpy as np
    from types import SimpleNamespace
    from voluseg._tools.constants import hdf
    from voluseg._tools.evenly_parallelize import evenly_parallelize
    
    # set up spark
    import pyspark
    from pyspark.sql.session import SparkSession
    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    
    p = SimpleNamespace(**parameters)
    
    dir_cell = os.path.join(p.dir_output, 'cells', str(color_i))
    
    fullname_volmean = os.path.join(p.dir_output, 'volume%d'%(color_i))
    with h5py.File(fullname_volmean+hdf, 'r') as file_handle:
        block_valids = file_handle['block_valids'][()]

    class accum_data(pyspark.accumulators.AccumulatorParam):
        '''define accumulator class'''
        
        def zero(self, val0):
            return [[]] * 3
        
        def addInPlace(self, val1, val2):
            return [val1[i] + val2[i] for i in range(3)]
                        
    # cumulate collected cells
    if p.parallel_clean:
        cell_data = sc.accumulator([[]] * 3, accum_data())
    def add_data(tuple_ii):
        ii = tuple_ii[1]
        try:
            cell_xyz = []
            cell_weights = []
            cell_timeseries = []
            
            fullname_block = os.path.join(dir_cell, 'block%05d'%(ii))
            with h5py.File(fullname_block+hdf, 'r') as file_handle:
                for ci in range(file_handle['n_cells'][()]):
                    cell_xyz.append(file_handle['/cell/%05d/xyz'%(ci)][()])
                    cell_weights.append(file_handle['/cell/%05d/weights'%(ci)][()])
                    cell_timeseries.append(file_handle['/cell/%05d/timeseries'%(ci)][()])
            
            if p.parallel_clean:
                cell_data.add([cell_xyz, cell_weights, cell_timeseries])
            else:
                return [cell_xyz, cell_weights, cell_timeseries]
                
        except KeyError:
            print('block %d is empty.' %ii)
        except IOError:
            print('block %d does not exist.' %ii)
    
    if p.parallel_clean:
        evenly_parallelize(np.argwhere(block_valids).T[0]).foreach(add_data)
        cell_xyz, cell_weights, cell_timeseries = cell_data.value
    else:
        idx_block_valids = np.argwhere(block_valids).T[0]
        valids_tuple = zip([[]]*len(idx_block_valids), idx_block_valids)
        cell_xyz, cell_weights, cell_timeseries = list(zip(*map(add_data, valids_tuple)))
        cell_xyz = [xyzi for ci in cell_xyz for xyzi in ci]
        cell_weights = [wi for ci in cell_weights for wi in ci]
        cell_timeseries = [ti for ci in cell_timeseries for ti in ci]

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
    