def z6():
    global brain_mask, censor_tau
    os.environ['MKL_NUM_THREADS'] = str(multiprocessing.cpu_count())
        
    if nmf_algorithm:
        for frame_i in range(imageframe_nmbr):
            if os.path.isfile(output_dir + 'Cells' + str(frame_i) + '_clust.hdf5'):
                if batch_mode:
                    continue
                else:
                    try:
                        cell_reset = eval(input('Reset cell clustering? [0, no]; 1, yes. '))
                    except SyntaxError:
                        cell_reset = 0
                    
                    if not cell_reset:
                        continue
            
            with h5py.File(output_dir + 'Cells' + str(frame_i) + '_clean.hdf5', 'r') as file_handle:
                Cell_timesers1 = file_handle['Cell_timesers1'][()].astype(float)
                Cell_baseline1 = file_handle['Cell_baseline1'][()].astype(float)
                background = file_handle['background'][()]
                
            T  = np.maximum(Cell_timesers1 - Cell_baseline1, 0)
            assert(np.all(np.isfinite(T)))
            T /= np.maximum(Cell_baseline1 - background * 0.8, 0)
            T[np.isnan(T)] = 0
            assert(np.min(T)==0)
            T[np.isinf(T)] = np.max(T[np.isfinite(T)])
            
            try:
                censor_tau
            except NameError:
                censor_tau = np.zeros(2)
            
            ltau_sta, ltau_fin = np.round(censor_tau * freq_stack).astype(int)
            ltau_fin = T.shape[1] - ltau_fin
            T[:, ltau_sta:ltau_fin] /= T[:, ltau_sta:ltau_fin].mean(1)[:, None]
            T[:, :ltau_sta] = T[:, ltau_fin:] = T[:, ltau_sta:ltau_fin].mean()
            assert(np.all(np.isfinite(T)))
                                    
            h5py.File(output_dir + 'Cells' + str(frame_i) + '_clust.hdf5', 'w')
            for i, k in enumerate(n_components):
                print('Running NMF: %d components' %k)
                
                model = decomposition.NMF(n_components=k, init='nndsvd', solver='cd', tol=0.0001, max_iter=100, verbose=1)
                W = model.fit_transform(T)
                H = model.components_
                
                with h5py.File(output_dir + 'Cells' + str(frame_i) + '_clust.hdf5', 'r+') as file_handle:
                    file_handle['W' + str(i)] = W
                    file_handle['H' + str(i)] = H

z6()
