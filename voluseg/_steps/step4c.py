def initialize_block_cells(n_voxels_cell, n_voxels_block, n_cells, 
    voxel_xyz, voxel_timeseries, peak_idx, peak_valids, voxel_similarity_peak, 
    lxyz, rxyz, ball_diam, ball_diam_xyz0):
    '''initialize cell positions in individual blocks'''

    import numpy as np
    from sklearn import cluster
    from voluseg._tools.sparseness import sparseness

    # get valid voxels of peaks
    peak_idx_valid = peak_idx[peak_valids]
    voxel_xyz_peak_valid = voxel_xyz[peak_idx_valid]
    voxel_xyz_phys_peak_valid = voxel_xyz_peak_valid * rxyz

    # cluster valid voxels of peaks by distance and similarity
    cell_clusters = \
        cluster.AgglomerativeClustering(
            n_clusters=n_cells,
            connectivity=voxel_similarity_peak[np.ix_(peak_valids,peak_valids)],
            linkage='ward')\
        .fit(voxel_xyz_phys_peak_valid)      # physical location of voxels
    cell_labels_peak_valid = cell_clusters.labels_

    # initialize weights for n_cells and background
    cell_weight_init = np.zeros((n_voxels_block, n_cells + 1))
    cell_neighborhood = np.zeros((n_voxels_block, n_cells + 1), dtype=bool)
    cell_sparseness = np.zeros(n_cells + 1)
    for cell_i in range(n_cells):
        # initialize cells with binary weights
        cell_weight_init[peak_idx_valid, cell_i] = (cell_labels_peak_valid == cell_i)

        # compute cell centroid
        cell_idx = np.argwhere(cell_labels_peak_valid == cell_i).T[0]
        cell_xyz_phys = voxel_xyz_phys_peak_valid[cell_idx]
        cell_dist = np.zeros(len(cell_xyz_phys))
        for j, voxel_xyz_phys in enumerate(cell_xyz_phys):
            cell_dist[j] = ((((voxel_xyz_phys - cell_xyz_phys)**2).sum(1))**0.5).sum()
        cell_xyz0 = voxel_xyz_peak_valid[cell_idx[np.argmin(cell_dist)]]

        # find neighborhood voxels
        for voxel_xyz_neib in (cell_xyz0 - ball_diam_xyz0 + np.argwhere(ball_diam)):
            cell_neighborhood[(voxel_xyz == voxel_xyz_neib).all(1), cell_i] = 1

        # make cell sparseness
        cell_vector = np.zeros(np.count_nonzero(cell_neighborhood[:, cell_i]))
        cell_vector[:n_voxels_cell] = 1
        cell_sparseness[cell_i] = sparseness(cell_vector)

    # get all voxels that are in neighborhood
    voxel_valids = cell_neighborhood.any(1)
    voxel_xyz_valid = voxel_xyz[voxel_valids]
    voxel_timeseries_valid = voxel_timeseries[voxel_valids]
    cell_weight_init_valid = cell_weight_init[voxel_valids]
    cell_neighborhood_valid = cell_neighborhood[voxel_valids]

    # initialize background cell
    cell_weight_init_valid[:, -1] = 1
    cell_neighborhood_valid[:, -1] = 1
    cell_sparseness[-1] = 0

    return voxel_timeseries_valid, voxel_xyz_valid, \
        cell_weight_init_valid, cell_neighborhood_valid, cell_sparseness