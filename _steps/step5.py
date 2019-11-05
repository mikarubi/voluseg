def clean_cells(parameters):
    
    import os
    import h5py
    import numpy as np
    import pandas as pd
    from scipy import signal
    from types import SimpleNamespace
    from itertools import combinations
    from pyspark.sql.session import SparkSession

    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    p = SimpleNamespace(**parameters)
    
    thr_similarity = 0.5
    
    for i_color in range(p.n_colors):
        if os.path.isfile(os.path.join(p.dir_output, 'cells%d_clean.hdf5'%(i_color))):
            continue
                
        with h5py.File(os.path.join(p.dir_output, 'cells%d_raw.hdf5'%(i_color)), 'r') as file_handle:
            cell_position = file_handle['cell_position'][()]
            cell_weights = file_handle['cell_weights'][()]
            cell_timeseries = file_handle['cell_timeseries'][()]
            x, y, z, t = file_handle['dims'][()]
            
        with h5py.File(os.path.join(p.dir_output, 'volume%d.hdf5'%(i_color)), 'r') as file_handle:
            volume_mask = file_handle['volume_mask'][()].T
            
        cell_x = cell_position[:, :, 0]
        cell_y = cell_position[:, :, 1]
        cell_z = cell_position[:, :, 2]
        cell_l = np.count_nonzero(cell_x >= 0, 1)
        cell_w = np.nansum(cell_weights, 1)
                
        ix = np.any(np.isnan(cell_timeseries), 1);
        if np.any(ix):
            print('nans (to be removed): %d' %np.count_nonzero(ix))
            cell_timeseries[ix] = 0
            
        cell_valids = np.zeros(len(cell_l), dtype=bool);
        for i, (li, xi, yi, zi) in enumerate(zip(cell_l, cell_x, cell_y, cell_z)):
            cell_valids[i] = np.mean(volume_mask[xi[:li], yi[:li], zi[:li]]) > p.thr_mask
            
        # brain mask array
        volume_list = [[[[] for zi in range(z)] for yi in range(y)] for xi in range(x)]
        volume_cell_n = np.zeros((x, y, z), dtype='int')
        for i, (li, vi) in enumerate(zip(cell_l, cell_valids)):
            for j in range(li if vi else 0):
                xij, yij, zij = cell_x[i, j], cell_y[i, j], cell_z[i, j]
                volume_list[xij][yij][zij].append(i)
                volume_cell_n[xij, yij, zij] += 1
                    
        pair_cells = [pi for a in volume_list for b in a for c in b for pi in combinations(c)]
        assert(len(pair_cells) == np.sum(volume_cell_n * (volume_cell_n - 1)))
        
        # remove duplicate cells
        pair_id, pair_count = np.unique(pair_cells, axis=1, return_counts=True)
        for pi, fi in zip(pair_id, pair_count):
            pair_overlap = (fi / cell_l[pi].mean(1)) > thr_similarity
            pair_correlation = np.corrcoef(cell_timeseries[pi])[0, 1] > thr_similarity
            if (pair_overlap and pair_correlation):
                cell_valids[pi[np.argmin(cell_w[pi])]] = 0
        
        ## get valid version of cells ##
        cell_weights = cell_weights[cell_valids]
        cell_timeseries = cell_timeseries[cell_valids]        
        cell_x = cell_x[cell_valids]
        cell_y = cell_y[cell_valids]
        cell_z = cell_z[cell_valids]
        cell_l = cell_l[cell_valids]
        cell_w = cell_w[cell_valids]
        ## end get valid version of cells ##
        
        def baseline(timeseries, poly_ordr=2):
            '''estimation of dynamic baseline for input timeseries'''
            
            # poly_ordr  polynomial order for detrending
            # p.t_baseline:  timescale constant for baseline estimation (in seconds)
            # p.f_hipass:   highpass cutoff frequency
            # p.f_volume:    frequency of imaging a single stack (in Hz)
            
            # timeseries mean
            timeseries_mean = timeseries.mean()
            
            # length of interval of dynamic baseline time-scales
            ltau = (np.round(p.t_baseline * p.f_volume / 2) * 2 + 1).astype(int)
            
            # detrend with a low-order polynomial
            xtime = np.arange(timeseries.shape[0])
            coefpoly = np.polyfit(xtime, timeseries, poly_ordr)
            timeseries -= np.polyval(coefpoly, xtime)
            timeseries = np.concatenate((timeseries[::-1], timeseries, timeseries[::-1]))
            
            # highpass filter
            nyquist = p.f_volume / 2
            if (p.f_hipass > 1e-10) and (p.f_hipass < nyquist - 1e-10):
                f_rng = np.array([p.f_hipass, nyquist - 1e-10])
                krnl = signal.firwin(p.lt, f_rng / nyquist, pass_zero=False)
                timeseries = signal.filtfilt(krnl, 1, timeseries, padtype=None)
                
            # restore mean
            timeseries = timeseries - timeseries.mean() + timeseries_mean
            
            # compute dynamic baseline
            timeseries_df = pd.DataFrame(timeseries)
            baseline_df = timeseries_df.rolling(ltau, min_periods=1, center=True).quantile(0.1)
            baseline_df = baseline_df.rolling(ltau, min_periods=1, center=True).mean()
            baseline = np.ravel(baseline_df)
            baseline += np.percentile(timeseries - baseline, 1)
            assert(np.allclose(np.percentile(timeseries - baseline, 1), 0))
            
            return(timeseries[p.lt:2*p.lt], baseline[p.lt:2*p.lt])
        
        try:
            cell_timeseries1, cell_baseline1 = \
                list(zip(*sc.parallelize(cell_timeseries).map(baseline).collect()))
        except:
            print('Failed parallel baseline computation. Proceeding serially.')
            cell_timeseries1, cell_baseline1 = list(zip(*map(baseline, cell_timeseries)))
                        
        n = np.count_nonzero(cell_valids)
        volume_id = np.full((x, y, z), -1)
        volume_weight = np.full((x, y, z), np.nan)
        for i, li in enumerate(cell_l):
            for j in range(li):
                xij, yij, zij = cell_x[i, j], cell_y[i, j], cell_z[i, j]
                if cell_weights[i, j] > volume_weight[xij, yij, zij]:
                    volume_id[xij, yij, zij] = i;
                    volume_weight[xij, yij, zij] = cell_weights[i, j]
                    
        with h5py.File(os.path.join(p.dir_output, 'volume%s.hdf5'%(i_color)), 'r') as file_handle:
            background = file_handle['background'][()]
                    
        with h5py.File(os.path.join(p.dir_output, 'cells%d_clean.hdf5'%(i_color)), 'w') as file_handle:
            file_handle['n'] = n
            file_handle['t'] = t
            file_handle['x'] = x
            file_handle['y'] = y
            file_handle['z'] = z
            file_handle['cell_x'] = cell_x
            file_handle['cell_y'] = cell_y
            file_handle['cell_z'] = cell_z
            file_handle['cell_l'] = cell_l
            file_handle['volume_id'] = volume_id
            file_handle['volume_weight'] = volume_weight
            file_handle['cell_weights'] = cell_weights.astype('float32')
            file_handle['cell_timeseries_raw'] = cell_timeseries.astype('float32')
            file_handle['cell_timeseries'] = cell_timeseries1.astype('float32')
            file_handle['cell_baseline'] = cell_baseline1.astype('float32')
            file_handle['background'] = background
