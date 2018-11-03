def z5():
    for frame_i in range(imageframe_nmbr):
        if os.path.isfile(output_dir + 'Cells' + str(frame_i) + '_clean.hdf5'):
            try:
                cell_reset = eval(input('Reset clean cells? [0, no]; 1, yes. '))
            except SyntaxError:
                cell_reset = 0
            
            if not cell_reset:
                continue
    
        thr_similarity = 0.5
    
        with h5py.File(output_dir + 'Cells' + str(frame_i) + '.hdf5', 'r') as file_handle:
            Cmpn_position = file_handle['Cmpn_position'][()]
            Cmpn_spcesers = file_handle['Cmpn_spcesers'][()]
            Cmpn_timesers = file_handle['Cmpn_timesers'][()]
            x, y, z, t = file_handle['dims'][()]
            freq = file_handle['freq'][()]
            
        with h5py.File(output_dir + 'brain_mask' + str(frame_i) + '.hdf5', 'r') as file_handle:
            brain_mask = file_handle['brain_mask'][()].T
            
        Cmpn_X = Cmpn_position[:, :, 0]
        Cmpn_Y = Cmpn_position[:, :, 1]
        Cmpn_Z = Cmpn_position[:, :, 2]
    
        if ((t > 2e4) and (freq < 10)) or (np.logical_not(np.isfinite(freq))):
            while 1:
                try:
                    freq = eval(input('t: %d, freq: %.3f. Enter frequency: ' %(t, freq)))
                    print('Continuing with frequency: %f' %freq)
                    break
                except SyntaxError:
                    pass
        
        ix = np.any(np.isnan(Cmpn_timesers), 1);
        if np.any(ix):
            print('nans (to be cleaned): %d' %np.count_nonzero(ix))
            Cmpn_timesers[ix] = np.nanmin(Cmpn_timesers[np.where(Cmpn_timesers)])
            
        Cell_validity = np.empty(Cmpn_timesers.shape[0], dtype=bool);
        for i in range(Cell_validity.size):
            j = np.count_nonzero(Cmpn_X[i] >= 0)
            Cell_validity[i] = np.mean(brain_mask[Cmpn_X[i, :j], Cmpn_Y[i, :j], Cmpn_Z[i, :j]]) > thr_similarity
            
        # brain mask array
        L = [[[[] for zi in range(z)] for yi in range(y)] for xi in range(x)]
        for i in range(len(Cmpn_X)):
            if Cell_validity[i]:
                for j in range(np.count_nonzero(Cmpn_X[i] >= 0)):
                    xij, yij, zij = Cmpn_X[i, j], Cmpn_Y[i, j], Cmpn_Z[i, j]
                    L[xij][yij][zij].append(i)
                    
        def get_pairs(xyz, l):
            return [[xyz[i], xyz[j]] for i in range(l) for j in range(i + 1, l)]
            
        vox_pairs = [get_pairs(xyz, len(xyz)) for X in L for Y in X for xyz in Y if len(xyz) > 1]
        all_pairs = np.sort([p for pairs in vox_pairs for p in pairs], 1)
        _, idx_uolap_pairs, size_uolap_pairs = \
                np.unique(all_pairs[:, 0] + 1j * all_pairs[:, 1], return_index=True, return_counts=True)
        
        uolap_pairs = all_pairs[idx_uolap_pairs]
        size_Cmpn = np.sum(np.isfinite(Cmpn_spcesers), 1)
        spatial_similarity_uolap_pairs = size_uolap_pairs / size_Cmpn[uolap_pairs].mean(1)
    
        hiolap_pairs = uolap_pairs[spatial_similarity_uolap_pairs > thr_similarity]
        corr_hiolap_pairs = np.array([np.corrcoef(Cmpn_timesers[pi])[0][1] for pi in hiolap_pairs])
        duplicate_pairs = hiolap_pairs[corr_hiolap_pairs > thr_similarity]
        
        Cmpn_wsum = np.nansum(Cmpn_spcesers, 1)
        for i, pi in enumerate(duplicate_pairs):
            Cell_validity[pi[np.argmin(Cmpn_wsum[pi])]] = 0
            
        Idx0 = np.where(Cell_validity)[0]
        try:
            Cmpn_timesers1_idx0, Cmpn_baseline1_idx0 = \
                list(zip(*sc.parallelize(Cmpn_timesers[Idx0]).map(detrend_dynamic_baseline).collect()))
        except:
            print('Failed parallel baseline computation. Proceeding serially.')
            Cmpn_timesers1_idx0, Cmpn_baseline1_idx0 = \
                list(zip(*map(detrend_dynamic_baseline, Cmpn_timesers[Idx0])))
                
        with h5py.File(output_dir + 'brain_mask' + str(frame_i) + '.hdf5', 'r') as file_handle:
            background = file_handle['background'][()]
            
        Cmpn_timesers1 = [None] * Cmpn_timesers.shape[0]
        Cmpn_baseline1 = [None] * Cmpn_timesers.shape[0]
        for i, h in enumerate(Idx0):
            Cmpn_timesers1[h] = Cmpn_timesers1_idx0[i]
            Cmpn_baseline1[h] = Cmpn_baseline1_idx0[i]
        
        lo_baseline = np.percentile(Cmpn_baseline1_idx0 - background, 1, 1) < 0
        print('low-baseline components (to be removed): %d' %np.count_nonzero(lo_baseline))
        Cell_validity[Idx0[lo_baseline]] = 0
        
        Idx1 = np.where(Cell_validity)[0]
        Cell_timesers1 = np.array([Cmpn_timesers1[i] for i in Idx1])
        Cell_baseline1 = np.array([Cmpn_baseline1[i] for i in Idx1])
                
        Cell_X = Cmpn_X[Cell_validity]
        Cell_Y = Cmpn_Y[Cell_validity]
        Cell_Z = Cmpn_Z[Cell_validity]
        
        Cell_spcesers = Cmpn_spcesers[Cell_validity]
        Cell_timesers0 = Cmpn_timesers[Cell_validity]
        
        n = np.count_nonzero(Cell_validity)
        Volume = np.zeros((x, y, z))
        Labels = np.zeros((x, y, z))
        for i in range(len(Cell_X)):
            for j in range(np.count_nonzero(np.isfinite(Cell_X[i]))):
                xij, yij, zij = Cell_X[i, j], Cell_Y[i, j], Cell_Z[i, j]
                if Cell_spcesers[i, j] > Volume[xij, yij, zij]:
                    Volume[xij, yij, zij] = Cell_spcesers[i, j]
                    Labels[xij, yij, zij] = i;
        
        with h5py.File(output_dir + 'Cells' + str(frame_i) + '_clean.hdf5', 'w') as file_handle:
            file_handle['n'] = n
            file_handle['x'] = x
            file_handle['y'] = y
            file_handle['z'] = z
            file_handle['freq'] = freq
            file_handle['Cell_X'] = Cell_X
            file_handle['Cell_Y'] = Cell_Y
            file_handle['Cell_Z'] = Cell_Z
            file_handle['Volume'] = Volume
            file_handle['Labels'] = Labels
            file_handle['Cell_spcesers'] = Cell_spcesers.astype('float32')
            file_handle['Cell_timesers0'] = Cell_timesers0.astype('float32')
            file_handle['Cell_timesers1'] = Cell_timesers1.astype('float32')
            file_handle['Cell_baseline1'] = Cell_baseline1.astype('float32')
            file_handle['background'] = background
        
z5()
