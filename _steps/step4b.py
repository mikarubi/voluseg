def process_block_data(xyz0, xyz1, parameters, i_color, lxyz, rxyz, ball_diam, bvolume_peak):
    import os
    import h5py
    import time
    import numpy as np
    from scipy import interpolate
    from skimage import morphology
    from types import SimpleNamespace
            
    os.environ['MKL_NUM_THREADS'] = '1'
        
    p = SimpleNamespace(**parameters)
    lz = lxyz[2]
        
    # load and dilate initial voxel peak positions
    x0_, y0_, z0_ = xyz0
    x1_, y1_, z1_ = xyz1
    voxel_peak = np.zeros_like(bvolume_peak.value)
    voxel_peak[x0_:x1_, y0_:y1_, z0_:z1_] = 1
    voxel_peak *= bvolume_peak.value
    voxel_mask = morphology.binary_dilation(voxel_peak, ball_diam)
    
    voxel_xyz = np.argwhere(voxel_mask)
    voxel_xyz_peak = np.argwhere(voxel_peak)
    peak_idx = np.argwhere(voxel_peak[voxel_mask]).T[0]
        
    tic = time.time()
    dir_volume = os.path.join(p.dir_output, 'volumes', str(i_color))
    x0, y0, z0 = voxel_xyz.min(0)
    x1, y1, z1 = voxel_xyz.max(0) + 1
    voxel_timeseries_block = [None] * p.lt
    for ti, name_volume in enumerate(p.volume_names):
        fullname_aligned_hdf = os.path.join(dir_volume, name_volume+'_aligned.hdf5')
        with h5py.File(fullname_aligned_hdf, 'r') as file_handle:
            voxel_timeseries_block[ti] = file_handle['V3D'][z0:z1, y0:y1, x0:x1].T

    voxel_timeseries_block = np.transpose(voxel_timeseries_block, (1, 2, 3, 0))
    voxel_timeseries = voxel_timeseries_block[voxel_mask[x0:x1, y0:y1, z0:z1]]
    del voxel_timeseries_block
    print('Load data time: %.1f minutes.\n' %((time.time() - tic) / 60))
    
    # perform slice-time correction, if there is more than one slice
    if lz > 1:
        for i in range(len(voxel_xyz)):
            # get timepoints of midpoint and zi plane for interpolation
            zi = voxel_xyz[i, 2]                  # number of plane
            timepoints_zi = np.arange(p.lt) / p.f_volume +  zi      * p.t_section
            timepoints_zm = np.arange(p.lt) / p.f_volume + (lz / 2) * p.t_section

            # make spline interpolator and interpolate timeseries
            spline_interpolator_xyzi = \
                interpolate.InterpolatedUnivariateSpline(timepoints_zi, voxel_timeseries[i])
            voxel_timeseries[i] = spline_interpolator_xyzi(timepoints_zm)

    def normalize(timeseries):
        mn = timeseries.mean(1)
        sd = timeseries.std(1, ddof=1)
        return (timeseries - mn[:, None]) / (sd[:, None] * np.sqrt(p.lt - 1))

    # get voxel connectivity from proximities (distances) and similarities (correlations)
    voxel_xyz_phys_peak = voxel_xyz_peak * rxyz
    voxel_timeseries_peak_nrm = normalize(voxel_timeseries[peak_idx])

    # compute voxel peak similarity: combination of high proximity and high correlation
    tic = time.time()
    voxel_similarity_peak = np.zeros((len(peak_idx), len(peak_idx)), dtype=bool)
    for i in range(len(peak_idx)):
        dist_i = (((voxel_xyz_phys_peak[i] - voxel_xyz_phys_peak)**2).sum(1))**0.5
        neib_i = dist_i < p.diam_cell
        corr_i = np.dot(voxel_timeseries_peak_nrm[i], voxel_timeseries_peak_nrm.T)
        voxel_similarity_peak[i] = neib_i & (corr_i > np.median(corr_i[neib_i]))
        
    del voxel_timeseries_peak_nrm
    voxel_similarity_peak = voxel_similarity_peak | voxel_similarity_peak.T
    print('Compute voxel similarity: %.1f minutes.\n' %((time.time() - tic) / 60))
    
    return (voxel_xyz, voxel_timeseries, peak_idx, voxel_similarity_peak)
