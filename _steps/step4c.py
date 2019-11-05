def initialize_block_cells(n_voxels_cell, n_voxels_block, n_cells, 
    voxel_xyz, voxel_timeseries, peak_idx, peak_valids, voxel_similarity_peak, 
    lxyz, rxyz, ball_diam, ball_diam_midpoint):
    
    import time
    import numpy as np
    from sklearn import cluster
    from .._tools.sparseness import sparseness
    
    peak_idx_valid = peak_idx[peak_valids]
    voxel_xyz_phys = voxel_xyz * rxyz
    # voxel_xyz_phys_peak_valid = voxel_xyz_phys[peak_idx[peak_valids]]
            
    tic = time.time()
    cell_clusters = \
        cluster.AgglomerativeClustering(
            n_clusters=n_cells,
            connectivity=voxel_similarity_peak[np.ix_(peak_valids,peak_valids)],
            linkage='ward')\
        .fit(voxel_xyz_phys[peak_idx_valid])      # physical location of voxels
    cell_labels = cell_clusters.labels_
    print('Hierarchical Clustering time: %.1f minutes.\n' %((time.time() - tic) / 60))
    
    # initialize spatial component properties
    cell_weight_init = np.zeros((n_voxels_block, n_cells + 1))
    cell_neighborhood = np.zeros((n_voxels_block, n_cells + 1), dtype=bool)
    cell_sparsity = np.zeros(n_cells + 1)
    for i_cell in range(n_cells):
        # initialize spatial component
        cell_weight_init[peak_idx_valid, i_cell] = (cell_labels == i_cell)
    
        # get neighborhood of component
        cell_centroid_phys_i = \
            np.median(voxel_xyz_phys[peak_idx_valid][cell_labels == i_cell], 0)
        dist_from_centroid_to_peak = \
            np.sqrt(
                np.square((cell_centroid_phys_i[0] - voxel_xyz_phys[peak_idx_valid, 0])) +
                np.square((cell_centroid_phys_i[1] - voxel_xyz_phys[peak_idx_valid, 1])) +
                np.square((cell_centroid_phys_i[2] - voxel_xyz_phys[peak_idx_valid, 2]))
            )
        cell_midpoint_i = voxel_xyz[peak_idx_valid][np.argmin(dist_from_centroid_to_peak)]
    
        cell_neibaidx_i = cell_midpoint_i + (np.argwhere(ball_diam) - ball_diam_midpoint)
        cell_neibaidx_i = cell_neibaidx_i[(cell_neibaidx_i >= 0).all(1)]
        cell_neibaidx_i = cell_neibaidx_i[(cell_neibaidx_i < lxyz).all(1)]
    
        def relative_indx(ni):
            return np.nonzero(np.all(voxel_xyz == ni, 1))[0][0]
        cell_neibridx_i = np.array([relative_indx(ni) for ni in cell_neibaidx_i])
        cell_neighborhood[cell_neibridx_i, i_cell] = 1
    
        cell_vect_i = np.zeros(len(cell_neibridx_i))
        cell_vect_i[:n_voxels_cell] = 1
        cell_sparsity[i_cell] = sparseness(cell_vect_i)
    
    voxel_valids = cell_neighborhood.any(1)
    voxel_xyz_valid = voxel_xyz[voxel_valids]
    voxel_timeseries_valid = voxel_timeseries[voxel_valids]
    cell_weight_init_valid = cell_weight_init[voxel_valids]
    cell_neighborhood_valid = cell_neighborhood[voxel_valids]
    
    # initialize background component
    cell_weight_init_valid[:, -1] = 1
    cell_neighborhood_valid[:, -1] = 1

    return voxel_timeseries_valid, voxel_xyz_valid, \
        cell_weight_init_valid, cell_neighborhood_valid, cell_sparsity