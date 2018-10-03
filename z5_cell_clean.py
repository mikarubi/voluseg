for frame_i in range(imageframe_nmbr):

    thr_similarity = 0.5

    with h5py.File(output_dir + 'Cells' + str(frame_i) + '.hdf5', 'r') as file_handle:
        Cmpn_position = file_handle['Cell_position'][()]
        Cmpn_spcesers = file_handle['Cell_spcesers'][()]
        Cmpn_timesers = file_handle['Cell_timesers'][()]
        x, y, z, t = file_handle['dims'][()]
        freq = file_handle['freq'][()]
        
    with h5py.File(output_dir + 'brain_mask' + str(frame_i) + '.hdf5', 'r') as file_handle:
        brain_mask = file_handle['brain_mask'][()].T
        
    Cmpn_position[np.isnan(Cmpn_position)] = -1
    Cmpn_position = Cmpn_position.astype('int')
    Cmpn_X = Cmpn_position[:, :, 0]
    Cmpn_Y = Cmpn_position[:, :, 1]
    Cmpn_Z = Cmpn_position[:, :, 2]

    if ((t > 2e4) and (freq < 10)) or (~np.isfinite(freq)):
        while 1:
            try:
                freq = eval(input('t: %d, freq: %.3f. Enter frequency: ' %(t, freq)))
                print('Continuing with frequency: %f' %freq)
                break
            except SyntaxError:
                pass
    
    ix = np.any(np.isnan(Cmpn_timesers), 1);
    if np.any(ix):
        print('nans: %d' %np.sum(ix))
        Cmpn_timesers[ix] = np.min(Cmpn_timesers[np.where(Cmpn_timesers)]);
        
    Cell_validity = np.empty(Cmpn_timesers.shape[0], dtype=bool);
    for i in range(Cell_validity.size):
        j = np.count_nonzero(Cmpn_X[i] >= 0)
        Cell_validity[i] = np.mean(brain_mask[Cmpn_X[i, :j], Cmpn_Y[i, :j], Cmpn_Z[i, :j]]) > thr_similarity
        
    # brain mask array
    L = [[[[] for zi in range(z)] for yi in range(y)] for xi in range(x)]
    for i in range(len(Cmpn_X)):
        if Cell_validity[i]:
            for j in range(np.count_nonzero(Cmpn_X[i] >= 0)):
                xij, yij, zij = int(Cmpn_X[i, j]), int(Cmpn_Y[i, j]), int(Cmpn_Z[i, j])
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
    corr_hiolap_pairs = np.zeros((len(hiolap_pairs), 1))
    corr_hiolap_pairs = np.r_[[np.corrcoef(Cmpn_timesers[pi])[0][1] for pi in hiolap_pairs]]
            
    duplicate_pairs = hiolap_pairs[corr_hiolap_pairs > thr_similarity]
    
    Cmpn_wsum = np.nansum(Cmpn_spcesers, 1)
    for i, pi in enumerate(duplicate_pairs):
        Cell_validity[pi[np.argmin(Cmpn_wsum[pi])]] = 0
        
    n = np.count_nonzero(Cell_validity);
    
    Cell_X = Cmpn_X[Cell_validity]
    Cell_Y = Cmpn_Y[Cell_validity]
    Cell_Z = Cmpn_Z[Cell_validity]
    
    Cell_spcesers = Cmpn_spcesers[Cell_validity]
    Cell_timesers0 = Cmpn_timesers[Cell_validity]
    
    Cell_timesers1, Cell_baseline1 = \
        list(zip(*sc.parallelize(Cell_timesers0).map(detrend_dynamic_baseline).collect()))
        
    Volume = np.zeros((x, y, z))
    Labels = np.zeros((x, y, z))
    for i in range(len(Cell_X)):
        for j in range(np.count_nonzero(np.isfinite(Cell_X[i]))):
            xij, yij, zij = int(Cell_X[i, j]), int(Cell_Y[i, j]), int(Cell_Z[i, j])
            if Cell_spcesers[i, j] > Volume[xij, yij, zij]:
                Volume[xij, yij, zij] = Cell_spcesers[i, j]
                Labels[xij, yij, zij] = i;
                
    with h5py.File(output_dir + 'Cells' + str(frame_i) + '_clean' + '.hdf5', 'w-') as file_handle:
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
        file_handle['Cell_spcesers'] = Cell_spcesers
        file_handle['Cell_timesers0'] = Cell_timesers0
        file_handle['Cell_timesers1'] = Cell_timesers1
        file_handle['Cell_baseline1'] = Cell_baseline1
        