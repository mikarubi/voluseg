def z6():
    os.environ['MKL_NUM_THREADS'] = str(multiprocessing.cpu_count())
    
    def nmfh_lite(V, H, miniter=10, maxiter=100, tolfun=1e-3, powr=1):
        
        n, t  = V.shape
        k, t_ = H.shape
        assert(t_ == t)
        
        V = V / (np.mean(V**powr, 1)**(1.0/powr))[:, None]
        
        dnorm_prev = np.full(2, np.inf)
        for i in range(maxiter):
            H_ = H
            
            # Alternate least squares with regularization
            W = np.maximum(linalg.lstsq(V.T, H.T)[0], 0)
            
            H = np.maximum(linalg.lstsq(W, V)[0], 0)
            H = H / (np.mean(H**powr, 1)**(1.0/powr))[:, None]
            
            dnorm = np.sqrt(np.mean((V - W.dot(H))**2))
            diffh = np.sqrt(np.mean((H - H_      )**2))
            if ((np.max(dnorm_prev) - dnorm)/dnorm < tolfun) and (diffh < tolfun):
                if i > miniter:
                    break
    
            dnorm_prev[1] = dnorm_prev[0]
            dnorm_prev[0] = dnorm
            
            if np.any(np.isnan(W)) or np.any(np.isnan(H)):
                break
            
            print('%4d\t%.8f\t%.8f' %(i, dnorm, diffh))
            
        return (W, H)
    
    
    def nndsvd_econ(A):
    
        # size of input matrix
        m, n = A.shape
        
        # 1st SVD --> partial SVD rank-k to the input matrix A.
        U, S, V = linalg.svd(A, full_matrices=0)
        
        # the matrices of the factorization
        k = S.shape[0]
        W = np.zeros((m, k))
        H = np.zeros((k, n))
        
        # choose the first singular triplet to be nonnegative
        W[:, 0] = np.sqrt(S[0]) * np.abs(U[:, 0]  )
        H[0, :] = np.sqrt(S[0]) * np.abs(V[:, 0].T)
        
        # 2nd SVD for the other factors (see table 1 in our paper)
        for i in range(1, k):
            uu    =   U[:, i];              vv    =   V[:, i];
            uup   =   uu * (uu > 0);        vvp   =   vv * (vv > 0);
            uun   = - uu * (uu < 0);        vvn   = - vv * (vv < 0);
            n_uup = linalg.norm(uup);       n_vvp = linalg.norm(vvp);
            n_uun = linalg.norm(uun);       n_vvn = linalg.norm(vvn);
            
            termp = n_uup * n_vvp
            termn = n_uun * n_vvn
            if (termp >= termn):
                W[:, i] = np.sqrt(S[i] * termp) * uup   / n_uup
                H[i, :] = np.sqrt(S[i] * termp) * vvp.T / n_vvp
            else:
                W[:, i] = np.sqrt(S[i] * termn) * uun   / n_uun
                H[i, :] = np.sqrt(S[i] * termn) * vvn.T / n_vvn
        
        return (W, H)

    
    if nmf_algorithm:
        for frame_i in range(imageframe_nmbr):
            
            with h5py.File(output_dir + 'Cells' + str(frame_i) + '_clean.hdf5', 'r') as file_handle:
                Cell_timesers1 = file_handle['Cell_timesers1'][()].astype(float)
                Cell_baseline1 = file_handle['Cell_baseline1'][()].astype(float)
                background = file_handle['background'][()]
                
            T = (Cell_timesers1 - Cell_baseline1) / (Cell_baseline1 - background * 0.8)
            T = np.maximum(T, 0)
                        
            if nmf_algorithm==1:
                W0, H0 = nndsvd_econ(T)
                
            h5py.File(output_dir + 'Cells' + str(frame_i) + '_clust.hdf5', 'w')
            for i, k in enumerate(n_components):
                if nmf_algorithm==1:
                    W, H = nmfh_lite(T, H0[:k], 100, 100, 1e-4)
                elif nmf_algorithm==2:
                    model = decomposition.NMF(n_components=k, init='nndsvd', solver='cd', tol=0.0001, max_iter=100, verbose=1)
                    W = model.fit_transform(T)
                    H = model.components_
                
                with h5py.File(output_dir + 'Cells' + str(frame_i) + '_clust.hdf5', 'r+') as file_handle:
                    file_handle['W' + str(i)] = W
                    file_handle['H' + str(i)] = H

z6()
