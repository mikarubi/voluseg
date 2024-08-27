def detect_cells(parameters):
    """detect cells in volumes"""

    import os
    import h5py
    import time
    import numpy as np
    from types import SimpleNamespace
    from voluseg._steps.step4a import define_blocks
    from voluseg._steps.step4b import process_block_data
    from voluseg._steps.step4c import initialize_block_cells
    from voluseg._steps.step4d import nnmf_sparse
    from voluseg._tools.ball import ball
    from voluseg._tools.constants import hdf
    from voluseg._tools.evenly_parallelize import evenly_parallelize

    # set up spark
    from pyspark.sql.session import SparkSession

    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext

    p = SimpleNamespace(**parameters)

    ball_diam, ball_diam_xyz0 = ball(1.0 * p.diam_cell, p.affine_mat)

    # load timepoints
    fullname_timemean = os.path.join(p.dir_output, "mean_timeseries")
    with h5py.File(fullname_timemean + hdf, "r") as file_handle:
        timepoints = file_handle["timepoints"][()]

    # load plane filename
    for color_i in range(p.n_colors):
        fullname_cells = os.path.join(p.dir_output, "cells%s_clean" % (color_i))
        if os.path.isfile(fullname_cells + hdf):
            continue

        dir_cell = os.path.join(p.dir_output, "cells", str(color_i))
        os.makedirs(dir_cell, exist_ok=True)

        fullname_volmean = os.path.join(p.dir_output, "volume%d" % (color_i))
        with h5py.File(fullname_volmean + hdf, "r") as file_handle:
            volume_mean = file_handle["volume_mean"][()].T
            volume_mask = file_handle["volume_mask"][()].T
            volume_peak = file_handle["volume_peak"][()].T
            if "n_blocks" in file_handle.keys():
                flag = 0
                n_voxels_cell = file_handle["n_voxels_cell"][()]
                n_blocks = file_handle["n_blocks"][()]
                block_valids = file_handle["block_valids"][()]
                xyz0 = file_handle["block_xyz0"][()]
                xyz1 = file_handle["block_xyz1"][()]
            else:
                flag = 1

        # broadcast volume peaks (for initialization) and volume_mean (for renormalization)
        bvolume_peak = sc.broadcast(volume_peak)
        bvolume_mean = sc.broadcast(volume_mean)

        # dimensions and resolution
        lxyz = volume_mean.shape
        rxyz = np.diag(p.affine_mat)[:3]

        # compute number of blocks (do only once)
        if flag:
            lx, ly, lz = lxyz
            rx, ry, rz = rxyz

            # get number of voxels in cell
            if (lz == 1) or (rz >= p.diam_cell):
                # area of a circle
                n_voxels_cell = np.pi * ((p.diam_cell / 2.0) ** 2) / (rx * ry)
            else:
                # volume of a cylinder (change to sphere later)
                n_voxels_cell = (
                    p.diam_cell * np.pi * ((p.diam_cell / 2.0) ** 2) / (rx * ry * rz)
                )

            n_voxels_cell = np.round(n_voxels_cell).astype(int)

            # get number of voxels in each cell
            n_blocks, block_valids, xyz0, xyz1 = define_blocks(
                lx, ly, lz, p.n_cells_block, n_voxels_cell, volume_mask, volume_peak
            )

            # save number and indices of blocks
            with h5py.File(fullname_volmean + hdf, "r+") as file_handle:
                file_handle["n_voxels_cell"] = n_voxels_cell
                file_handle["n_blocks"] = n_blocks
                file_handle["block_valids"] = block_valids
                file_handle["block_xyz0"] = xyz0
                file_handle["block_xyz1"] = xyz1

        print("number of blocks, total: %d." % (block_valids.sum()))

        for ii in np.where(block_valids)[0]:
            try:
                fullname_block = os.path.join(dir_cell, "block%05d" % (ii))
                with h5py.File(fullname_block + hdf, "r") as file_handle:
                    if ("completion" in file_handle.keys()) and file_handle[
                        "completion"
                    ][()]:
                        block_valids[ii] = 0
            except (NameError, OSError):
                pass

        print("number of blocks, remaining: %d." % (block_valids.sum()))
        ix = np.where(block_valids)[0]
        block_ixyz01 = list(zip(ix, xyz0[ix], xyz1[ix]))

        # detect individual cells with sparse nnmf algorithm
        def detect_cells_block(tuple_i_xyz0_xyz1):
            import os

            # disable numpy multithreading
            os.environ["OMP_NUM_THREADS"] = "1"
            os.environ["MKL_NUM_THREADS"] = "1"
            os.environ["NUMEXPR_NUM_THREADS"] = "1"
            os.environ["OPENBLAS_NUM_THREADS"] = "1"
            os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
            import numpy as np

            ii, xyz0, xyz1 = tuple_i_xyz0_xyz1[1]

            voxel_xyz, voxel_timeseries, peak_idx, voxel_similarity_peak = (
                process_block_data(
                    xyz0,
                    xyz1,
                    parameters,
                    color_i,
                    lxyz,
                    rxyz,
                    ball_diam,
                    bvolume_mean,
                    bvolume_peak,
                    timepoints,
                )
            )

            n_voxels_block = len(voxel_xyz)  # number of voxels in block

            voxel_fraction_peak = np.argsort(
                ((voxel_timeseries[peak_idx]) ** 2).mean(1)
            ) / len(peak_idx)
            for fraction in np.r_[1:0:-0.05]:
                try:
                    peak_valids = voxel_fraction_peak >= (
                        1 - fraction
                    )  # valid voxel indices

                    n_cells = np.round(
                        peak_valids.sum() / (0.5 * n_voxels_cell)
                    ).astype(int)
                    print((fraction, n_cells))

                    tic = time.time()
                    (
                        voxel_timeseries_valid,
                        voxel_xyz_valid,
                        cell_weight_init_valid,
                        cell_neighborhood_valid,
                        cell_sparseness,
                    ) = initialize_block_cells(
                        n_voxels_cell,
                        n_voxels_block,
                        n_cells,
                        voxel_xyz,
                        voxel_timeseries,
                        peak_idx,
                        peak_valids,
                        voxel_similarity_peak,
                        lxyz,
                        rxyz,
                        ball_diam,
                        ball_diam_xyz0,
                    )
                    print(
                        "cell initialization: %.1f minutes.\n"
                        % ((time.time() - tic) / 60)
                    )

                    tic = time.time()
                    cell_weights_valid, cell_timeseries_valid, d = nnmf_sparse(
                        voxel_timeseries_valid,
                        voxel_xyz_valid,
                        cell_weight_init_valid,
                        cell_neighborhood_valid,
                        cell_sparseness,
                        timepoints=timepoints,
                        miniter=10,
                        maxiter=100,
                        tolfun=1e-3,
                    )

                    success = 1
                    print(
                        "cell factorization: %.1f minutes.\n"
                        % ((time.time() - tic) / 60)
                    )
                    break
                except ValueError as msg:
                    print("retrying factorization of block %d: %s" % (ii, msg))
                    success = 0

            # get cell positions and timeseries, and save cell data
            fullname_block = os.path.join(dir_cell, "block%05d" % (ii))
            with h5py.File(fullname_block + hdf, "w") as file_handle:
                if success:
                    for ci in range(n_cells):
                        ix = cell_weights_valid[:, ci] > 0
                        xyzi = voxel_xyz_valid[ix]
                        wi = cell_weights_valid[ix, ci]
                        bi = np.sum(
                            wi * bvolume_mean.value[tuple(zip(*xyzi))]
                        ) / np.sum(wi)
                        ti = (
                            bi
                            * cell_timeseries_valid[ci]
                            / np.mean(cell_timeseries_valid[ci])
                        )

                        file_handle["/cell/%05d/xyz" % (ci)] = xyzi
                        file_handle["/cell/%05d/weights" % (ci)] = wi
                        file_handle["/cell/%05d/timeseries" % (ci)] = ti

                file_handle["n_cells"] = n_cells
                file_handle["completion"] = 1

        if block_valids.any():
            evenly_parallelize(block_ixyz01).foreach(detect_cells_block)

        # collect_blocks(color_i, parameters, lxyz)
