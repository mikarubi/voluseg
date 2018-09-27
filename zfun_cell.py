def process_blok(x0_x1_y0_y1_z0_z1_):
    
    x0_, x1_, y0_, y1_, z0_, z1_ = x0_x1_y0_y1_z0_z1_

    print(('Setting number of threads in process_blok to ' + str(nthread) + '.\n'))
    os.environ['MKL_NUM_THREADS'] = str(nthread)
    
    # load and dilate initial voxel peak positions
    voxl_peaklidx_blok = np.zeros_like(bimage_peak_fine.value)
    voxl_peaklidx_blok[x0_:x1_, y0_:y1_, z0_:z1_] = 1
    voxl_peaklidx_blok *= bimage_peak_fine.value
    voxl_valdlidx_blok = morphology.binary_dilation(voxl_peaklidx_blok, cell_ball)
    voxl_position_peak = np.argwhere(voxl_peaklidx_blok)
    voxl_position      = np.argwhere(voxl_valdlidx_blok)
    voxl_peakaidx      = np.nonzero(voxl_peaklidx_blok[voxl_valdlidx_blok])[0]

    x0, y0, z0 = voxl_position.min(0)
    x1, y1, z1 = voxl_position.max(0) + 1
    voxl_timesers_blok = [None] * lt
    
    tic = time.time()
    for ti in range(lt):        
        image_name_hdf = image_dir(image_names[ti], frame_i) + 'image_aligned.hdf5'
        with h5py.File(image_name_hdf, 'r') as file_handle:
            voxl_timesers_blok[ti] = file_handle['V3D'][z0:z1, y0:y1, x0:x1].T
    print(('Load data time:', np.around((time.time() - tic) / 60, 2), 'minutes.\n'))

    voxl_timesers_blok = np.transpose(voxl_timesers_blok, (1, 2, 3, 0))
    
    voxl_timesers = voxl_timesers_blok[voxl_valdlidx_blok[x0:x1, y0:y1, z0:z1]]
    del voxl_timesers_blok
    
    # perform slice-time correction, if there is more than one slice
    if lz > 1:
        for i in range(len(voxl_position)):
            # get timepoints of midpoint and zi plane for interpolation
            zi = voxl_position[i, 2]                  # number of plane
            timepoints_zi = np.arange(lt) * 1000.0 / freq_stack +  zi      * t_exposure
            timepoints_zm = np.arange(lt) * 1000.0 / freq_stack + (lz / 2) * t_exposure

            # make spline interpolator and interpolate timeseries
            spline_interpolator_xyzi = \
                interpolate.InterpolatedUnivariateSpline(timepoints_zi, voxl_timesers[i])
            voxl_timesers[i] = spline_interpolator_xyzi(timepoints_zm)

    def normalize_rank_timesers(timesers):
        #for i, time_i in enumerate(timesers):
        #    timesers[i] = stats.rankdata(time_i)

        mn = timesers.mean(1)
        sd = timesers.std(1, ddof=1)
        return (timesers - mn[:, None]) / (sd[:, None] * np.sqrt(lt - 1))

    # get voxel connectivity from proximities (distances) and similarities (correlations)
    voxl_position_peak_phys = voxl_position_peak * [resn_x * ds, resn_y * ds, resn_z]
    voxl_timesers_peak_rank = normalize_rank_timesers(voxl_timesers[voxl_peakaidx])

    # connectivity is given by the combination of high proximity and high similarity
    voxl_conn_peak = np.zeros((len(voxl_peakaidx), len(voxl_peakaidx)), 'bool')
    idx = np.linspace(0, len(voxl_peakaidx), 11, dtype='int')
    for i in range(len(idx) - 1):
        print(i)
        idx_i = np.r_[idx[i]:idx[i + 1]]
        voxl_dist_peak_i = np.sqrt(
            np.square(voxl_position_peak_phys[idx_i, 0:1] - voxl_position_peak_phys[:, 0:1].T) +
            np.square(voxl_position_peak_phys[idx_i, 1:2] - voxl_position_peak_phys[:, 1:2].T) +
            np.square(voxl_position_peak_phys[idx_i, 2:3] - voxl_position_peak_phys[:, 2:3].T))
        voxl_corr_peak_i = np.dot(voxl_timesers_peak_rank[idx_i], voxl_timesers_peak_rank.T)

        voxl_neib_peak_i = voxl_dist_peak_i < cell_diam
        voxl_neib_simi_i = np.r_[[corr_ij > np.median(corr_ij[neib_ij])
                                  for neib_ij, corr_ij in zip(voxl_neib_peak_i, voxl_corr_peak_i)]]
        voxl_conn_peak[idx_i] = (voxl_neib_peak_i & voxl_neib_simi_i)

    voxl_conn_peak = voxl_conn_peak | voxl_conn_peak.T
    voxl_powr_peak = np.mean(np.square(voxl_timesers[voxl_peakaidx]), 1)

    del voxl_timesers_peak_rank
    return (voxl_position, voxl_timesers, voxl_peakaidx, voxl_position_peak,
            voxl_position_peak_phys, voxl_conn_peak, voxl_powr_peak)


def blok_cell_detection(blok_i_blok_xyz_01):
    '''Detect individual cells using the sparse NMF algorithm'''

    blok_i, blok_xyz_01 = blok_i_blok_xyz_01

    print(('Setting number of threads in blok_cell_detection to ' + str(nthread) + '.\n'))
    os.environ['MKL_NUM_THREADS'] = str(nthread)

    (voxl_position, voxl_timesers, voxl_peakaidx, voxl_position_peak,
        voxl_position_peak_phys, voxl_conn_peak, voxl_powr_peak) = process_blok(blok_xyz_01)

    blok_voxl_nmbr = len(voxl_position)                        # number of voxels in blok
    peak_valdlidx = np.arange(len(voxl_position_peak))

    voxl_fraction = 100                                        # decremented if nnmf fails
    for iter_i in range(128):                                 # 0.95**31 = 0.2
        try:
            # estimate sparseness of each component
            cmpn_nmbr = np.around(peak_valdlidx.size / (0.5 * cell_voxl_nmbr)).astype('int32')

            print((iter_i, voxl_fraction, cmpn_nmbr))

            tic = time.time()
            cmpn_clusters = \
                cluster.AgglomerativeClustering(
                    n_clusters=cmpn_nmbr,
                    connectivity=voxl_conn_peak[peak_valdlidx[:,None],peak_valdlidx[None]],
                    linkage='ward')\
                .fit(voxl_position_peak_phys[peak_valdlidx])
            cmpn_labl = cmpn_clusters.labels_
            print(('Hierarchical Clustering time:', np.around((time.time() - tic) / 60, 2), 'minutes.\n;'))

            # initialize spatial component properties
            cmpn_spceinit = np.zeros((blok_voxl_nmbr, cmpn_nmbr + 1))
            cmpn_neibhood = np.zeros((blok_voxl_nmbr, cmpn_nmbr + 1), dtype='bool')
            cmpn_sparsity = np.zeros(cmpn_nmbr + 1)
            cmpn_percentl = np.zeros(cmpn_nmbr + 1)
            for cmpn_i in range(cmpn_nmbr):
                # initialize spatial component
                cmpn_spceinit[voxl_peakaidx[peak_valdlidx], cmpn_i] = (cmpn_labl == cmpn_i)

                # get neighborhood of component
                cmpn_centroid_phys_i = \
                    np.median(voxl_position_peak_phys[peak_valdlidx][cmpn_labl == cmpn_i], 0)
                dist_from_centroid_to_peak = \
                    np.sqrt(
                        np.square((cmpn_centroid_phys_i[0] - voxl_position_peak_phys[peak_valdlidx, 0])) +
                        np.square((cmpn_centroid_phys_i[1] - voxl_position_peak_phys[peak_valdlidx, 1])) +
                        np.square((cmpn_centroid_phys_i[2] - voxl_position_peak_phys[peak_valdlidx, 2]))
                    )
                cmpn_midpoint_i = voxl_position_peak[peak_valdlidx][np.argmin(dist_from_centroid_to_peak)]

                cmpn_neibaidx_i = cmpn_midpoint_i + (np.argwhere(cell_ball) - cell_ball_midpoint)
                cmpn_neibaidx_i = cmpn_neibaidx_i[(cmpn_neibaidx_i >= 0).all(1)]
                cmpn_neibaidx_i = cmpn_neibaidx_i[(cmpn_neibaidx_i < [lx//ds, ly//ds, lz]).all(1)]

                def relative_indx(ni):
                    return np.nonzero(np.all(voxl_position == ni, 1))[0][0]
                cmpn_neibridx_i = np.array([relative_indx(ni) for ni in cmpn_neibaidx_i])
                cmpn_neibhood[cmpn_neibridx_i, cmpn_i] = 1

                cmpn_vect_i = np.zeros(len(cmpn_neibridx_i))
                cmpn_vect_i[:int(round(cell_voxl_nmbr))] = 1
                cmpn_sparsity[cmpn_i] = sparseness(cmpn_vect_i)
                cmpn_percentl[cmpn_i] = 100 * (1 - np.mean(cmpn_vect_i))

            voxl_valdlidx = cmpn_neibhood.any(1)
            voxl_position_vald = voxl_position[voxl_valdlidx]
            voxl_timesers_vald = voxl_timesers[voxl_valdlidx]
            cmpn_spceinit_vald = cmpn_spceinit[voxl_valdlidx]
            cmpn_neibhood_vald = cmpn_neibhood[voxl_valdlidx]

            # initialize background component
            cmpn_spceinit_vald[:, -1] = 1
            cmpn_neibhood_vald[:, -1] = 1
            
            tic = time.time()
            cmpn_spcesers_vald, cmpn_timesers_vald, d = nnmf_sparse(
                voxl_timesers_vald, voxl_position_vald, cmpn_spceinit_vald,
                cmpn_neibhood_vald, cmpn_sparsity, cmpn_percentl,
                miniter=10, maxiter=100, tolfun=1e-3)

            detection_success = 1
            print(('NMF time:', np.around((time.time() - tic) / 60, 2), 'minutes.\n'))
            break
        except ValueError:
            detection_success = 0

            voxl_fraction *= 0.97
            thr_powr_peak = np.percentile(voxl_powr_peak, 100 - voxl_fraction)
            peak_valdlidx = np.where(voxl_powr_peak > thr_powr_peak)[0]

    # get cell positions and timeseries, and save cell data
    with h5py.File(cell_dir + '/Block' + str(blok_i).zfill(5) + '.hdf5', 'w') as file_handle:
        if detection_success:
            cell_i = 0
            for cmpn_i in range(cmpn_nmbr):
                try:
                    cmpn_lidx_i = np.nonzero(cmpn_spcesers_vald[:, cmpn_i])[0]
                    cmpn_position_i = voxl_position_vald[cmpn_lidx_i]
                    cmpn_spcesers_i = cmpn_spcesers_vald[cmpn_lidx_i, cmpn_i]
                    mean_spcevoxl_i = bimage_mean.value[list(zip(*cmpn_position_i))]
                    mean_i = np.sum(mean_spcevoxl_i * cmpn_spcesers_i) / np.sum(cmpn_spcesers_i)
                    cmpn_timesers_i = cmpn_timesers_vald[cmpn_i]
                    cmpn_timesers_i = cmpn_timesers_i * mean_i / np.mean(cmpn_timesers_i)
                    # cmpn_polytrnd_i = nonlinear_trend(cmpn_timesers_i, poly_ordr=2)[0]
                    # cmpn_basedetr_i = dynamic_baseline(cmpn_timesers_i - cmpn_polytrnd_i)
    
                    hdf5_dir = '/cell/' + str(cell_i).zfill(5)
                    file_handle[hdf5_dir + '/cell_position'] = cmpn_position_i
                    file_handle[hdf5_dir + '/cell_spcesers'] = cmpn_spcesers_i
                    file_handle[hdf5_dir + '/cell_timesers'] = cmpn_timesers_i
                    # file_handle[hdf5_dir + '/cell_baseline'] = cmpn_polytrnd_i + cmpn_basedetr_i
                    cell_i += 1
                except ValueError:
                    print((blok_i, cmpn_i, 'not saved.'))

        file_handle['cell_nmbr'] = cmpn_nmbr
        file_handle['success'] = 1


def nnmf_sparse(V0, XYZ0, W0, B0, Sparsity0, Percentl0,
                tolfun=1e-4, miniter=10, maxiter=100, verbosity=1, time_mean=1.0):

    print(('Setting number of threads in nnmf_sparse to ' + str(nthread) + '.\n'))
    os.environ['MKL_NUM_THREADS'] = str(nthread)

    # CAUTION: Input variable is modified to save memory
    V0 *= (time_mean / V0.mean(1)[:, None])                 # normalize voxel timeseries

    V = V0[:, dt_range].astype('double')                        # copy input signal
    XYZ = XYZ0.astype('int32')
    W = W0.astype('double')
    B = B0.astype('bool')
    Sparsity = Sparsity0.copy()
    Percentl = Percentl0.copy()

    # get dimensions
    n,  t = V.shape
    n_, c = W.shape
    assert(n_ == n)

    H = np.zeros((c, t))                                      # zero timeseries array
    dnorm_prev = np.full(2, np.inf)                           # last two d-norms
    for iter_i in range(maxiter):
        # save current states
        H_ = H.copy()

        # Alternate least squares with regularization
        H = np.maximum(linalg.lstsq(W, V)[0], 0)
        H *= (time_mean / H.mean(1)[:, None])                 # normalize component timeseries

        W = np.maximum(linalg.lstsq(V.T, H.T)[0], 0)
        W[~B] = 0                                             # restrict component boundaries
        for ci in range(c):
            W_ci = W[B[:, ci], ci]
            if any(W_ci) & ((Sparsity[ci] > 0) | (Percentl[ci] > 0)):
                # get relative dimensions of component
                XYZ_ci = XYZ[B[:, ci]] - XYZ[B[:, ci]].min(0)

                # enforce component sparsity and percentile threshold
                W_ci = projection(W_ci, Sparsity[ci], at_least_as_sparse=True)
                # W_ci[W_ci <= np.percentile(W_ci, Percentl[ci])] = 0
                
                # retain component of maximal size
                L_ci = np.zeros(np.ptp(XYZ_ci, 0) + 1, dtype='bool')
                L_ci[list(zip(*XYZ_ci))] = W_ci > 0
                L_ci = measure.label(L_ci, connectivity=3)
                lci_size = np.bincount(L_ci[L_ci.nonzero()])
                W_ci[L_ci[list(zip(*XYZ_ci))] != np.argmax(lci_size)] = 0

                W[B[:, ci], ci] = W_ci

        # Get norm of difference and check for convergence
        dnorm = np.sqrt(np.mean(np.square(V - W.dot(H)))) / time_mean
        diffh = np.sqrt(np.mean(np.square(H - H_      ))) / time_mean
        if ((dnorm_prev.max(0) - dnorm) < tolfun) & (diffh < tolfun):
            if (iter_i >= miniter):
                break
        dnorm_prev[1] = dnorm_prev[0]
        dnorm_prev[0] = dnorm

        if verbosity:
            print((iter_i, dnorm, diffh))

    # Perform final regression on full input timeseries
    H = np.maximum(linalg.lstsq(W, V0)[0], 0)
    H *= (time_mean / H.mean(1)[:, None])                     # normalize component timeseries

    return (W, H, dnorm)


def projection(Si, s, at_least_as_sparse=False):
    assert(Si.ndim == 1)
    S = np.copy(Si)                                           # copy input signal

    if s <= 0:
        return np.maximum(S, 0)                               # enforce nonnegativity

    d = S.size

    L2 = np.sqrt(np.sum(np.square(S)))                        # fixed l2-norm
    L1 = L2 * (np.sqrt(d) * (1 - s) + s)                      # desired l1-norm

    # quit if at_least_sparse=True and original exceeds target sparsity
    if at_least_as_sparse:                                    
        if L1 >= np.sum(np.abs(S)):
            return S

    # initialize components with negative values
    Z = np.zeros(S.shape, 'bool')

    negatives = True
    while negatives:
        # Fix components with negative values at 0
        Z = Z | (S < 0)
        S[Z] = 0

        # Project to the sum-constraint hyperplane
        S += (L1 - np.sum(S)) / (d - np.sum(Z))
        S[Z] = 0

        # Get midpoints of hyperplane, M
        M = np.tile(L1 / (d - np.sum(Z)), d)
        M[Z] = 0
        P = S - M

        # Solve for Alph, L2 = l2[M + Alph*(S-M)] = l2[P*Alph + M],
        # where L2 is defined above, and l2 is the l2-norm operator.
        # For convenience, we square both sides and find the roots,
        # 0 = (l2[P*Alph + M])^2 - (L2)^2
        # 0 = sum((P*Alph)^2) + sum(2*P*M*Alph) + sum(M^2) - L2^2
        A =     np.sum(P * P)
        B = 2 * np.sum(P * M)
        C =     np.sum(M * M) - L2**2

        Alph = (-B + np.real(np.sqrt(B**2 - 4 * A * C))) / (2 * A)

        # Project within the sum-constraint hyperplane to match L2
        S = M + Alph * P

        # Check for negative values in solution
        negatives = np.any(S < 0)

    return S
