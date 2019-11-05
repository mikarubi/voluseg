def nnmf_sparse(V0, XYZ0, W0, B0, Sparsity0, tolfun=1e-4, miniter=10, maxiter=100, verbosity=1, time_mean=1.0):

    import os
    import numpy as np
    from scipy import linalg
    from volusegm import projection

    print('Setting number of threads in nnmf_sparse to %d.\n' %nthread)
    os.environ['MKL_NUM_THREADS'] = str(nthread)

    # CAUTION: Input variable is modified to save memory
    V0 *= (time_mean / V0.mean(1)[:, None])                 # normalize voxel timeseries

    V = V0[:, dt_range].astype(float)                        # copy input signal
    XYZ = XYZ0.astype(int)
    W = W0.astype(float)
    B = B0.astype(bool)
    Sparsity = Sparsity0.copy()

    # get dimensions
    n,  t = V.shape
    n_, c = W.shape
    assert(n_ == n)

    H = np.zeros((c, t))                                      # zero timeseries array
    dnorm_prev = np.full(2, np.inf)                           # last two d-norms
    for i_iter in range(maxiter):
        # save current states
        H_ = H.copy()

        # Alternate least squares with regularization
        H = np.maximum(linalg.lstsq(W, V)[0], 0)
        H *= (time_mean / H.mean(1)[:, None])                 # normalize component timeseries

        W = np.maximum(linalg.lstsq(V.T, H.T)[0], 0)
        W[np.logical_not(B)] = 0                              # restrict component boundaries
        for ci in range(c):
            W_ci = W[B[:, ci], ci]
            if any(W_ci) & (Sparsity[ci] > 0):
                # get relative dimensions of component
                XYZ_ci = XYZ[B[:, ci]] - XYZ[B[:, ci]].min(0)

                # enforce component sparsity and percentile threshold
                W_ci = projection(W_ci, Sparsity[ci], at_least_as_sparse=True)
                
                # retain component of maximal size
                L_ci = np.zeros(np.ptp(XYZ_ci, 0) + 1, dtype=bool)
                L_ci[list(zip(*XYZ_ci))] = W_ci > 0
                L_ci = measure.label(L_ci, connectivity=3)
                lci_size = np.bincount(L_ci[L_ci.nonzero()])
                W_ci[L_ci[list(zip(*XYZ_ci))] != np.argmax(lci_size)] = 0

                W[B[:, ci], ci] = W_ci

        # Get norm of difference and check for convergence
        dnorm = np.sqrt(np.mean(np.square(V - W.dot(H)))) / time_mean
        diffh = np.sqrt(np.mean(np.square(H - H_      ))) / time_mean
        if ((dnorm_prev.max(0) - dnorm) < tolfun) & (diffh < tolfun):
            if (i_iter >= miniter):
                break
        dnorm_prev[1] = dnorm_prev[0]
        dnorm_prev[0] = dnorm

        if verbosity:
            print((i_iter, dnorm, diffh))

    # Perform final regression on full input timeseries
    H = np.maximum(linalg.lstsq(W, V0)[0], 0)
    H *= (time_mean / H.mean(1)[:, None])                     # normalize component timeseries

    return (W, H, dnorm)
