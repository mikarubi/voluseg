import os
from typing import Tuple

# disable numpy multithreading
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
import numpy as np

import h5py
import time
from scipy import interpolate
from skimage import morphology
from types import SimpleNamespace
from voluseg.tools.constants import ali, hdf, dtype


def process_block_data(
    xyz0: Tuple[int, int, int],
    xyz1: Tuple[int, int, int],
    parameters: dict,
    color_i: int,
    lxyz: Tuple[int, int, int],
    rxyz: Tuple[float, float, float],
    ball_diam: np.ndarray,
    bvolume_mean: h5py.Dataset,
    bvolume_peak: h5py.Dataset,
    timepoints: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load timeseries in individual blocks, slice-time correct, and find similar timeseries.

    Parameters
    ----------
    xyz0 : Tuple[int, int, int]
        Start coordinates of block.
    xyz1 : Tuple[int, int, int]
        End coordinates of block.
    parameters : dict
        Parameters dictionary.
    color_i : int
        Color index.
    lxyz : Tuple[int, int, int]
        Number of voxels in x, y, and z dimensions.
    rxyz : Tuple[float, float, float]
        The resolution of x, y, and z dimensions.
    ball_diam : np.ndarray
        The diameter of a cell-area sphere.
    bvolume_mean : h5py.Dataset
        Spark broadcast variable: volume mean.
    bvolume_peak : h5py.Dataset
        Spark broadcast variable: local intensity maximum volume (peak).
    timepoints : np.ndarray
        Timepoints at which segmentation will be performed.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        Tuple containing: Voxel coordinates, timeseries, peak indices, and similarity matrix of peaks.
    """
    p = SimpleNamespace(**parameters)
    lz = lxyz[2]

    # load and dilate initial voxel peak positions
    x0_, y0_, z0_ = xyz0
    x1_, y1_, z1_ = xyz1
    voxel_peak = np.zeros_like(bvolume_peak.value)
    voxel_peak[x0_:x1_, y0_:y1_, z0_:z1_] = 1
    voxel_peak = voxel_peak & bvolume_peak.value & (bvolume_mean.value > 0)
    voxel_mask = morphology.binary_dilation(voxel_peak, ball_diam) & (
        bvolume_mean.value > 0
    )

    voxel_xyz = np.argwhere(voxel_mask)
    voxel_xyz_peak = np.argwhere(voxel_peak)
    peak_idx = np.argwhere(voxel_peak[voxel_mask]).T[0]

    tic = time.time()
    dir_volume = os.path.join(p.dir_output, "volumes", str(color_i))
    x0, y0, z0 = voxel_xyz.min(0)
    x1, y1, z1 = voxel_xyz.max(0) + 1
    voxel_timeseries_block = [None] * p.lt
    for ti, name_volume in enumerate(p.volume_names):
        fullname_volume = os.path.join(dir_volume, name_volume)
        with h5py.File(fullname_volume + ali + hdf, "r") as file_handle:
            voxel_timeseries_block[ti] = file_handle["volume"][z0:z1, y0:y1, x0:x1].T

    voxel_timeseries_block = np.transpose(voxel_timeseries_block, (1, 2, 3, 0))
    voxel_timeseries = voxel_timeseries_block[voxel_mask[x0:x1, y0:y1, z0:z1]]
    voxel_timeseries = voxel_timeseries.astype(dtype)
    del voxel_timeseries_block
    print("data loading: %.1f minutes.\n" % ((time.time() - tic) / 60))

    # slice-time correct if more than one slice and t_section is positive
    if (lz > 1) and (p.t_section > 0):
        for i, zi in enumerate(voxel_xyz[:, 2]):
            # get timepoints of midpoint and zi plane for interpolation
            timepoints_zi = np.arange(p.lt) / p.f_volume + zi * p.t_section
            timepoints_zm = np.arange(p.lt) / p.f_volume + (lz / 2) * p.t_section

            # make spline interpolator and interpolate timeseries
            spline_interpolator_xyzi = interpolate.InterpolatedUnivariateSpline(
                timepoints_zi, voxel_timeseries[i]
            )
            voxel_timeseries[i] = spline_interpolator_xyzi(timepoints_zm)

    def normalize(timeseries):
        mn = timeseries.mean(1)
        sd = timeseries.std(1, ddof=1)
        return (timeseries - mn[:, None]) / (sd[:, None] * np.sqrt(p.lt - 1))

    # get voxel connectivity from proximities (distances) and similarities (correlations)
    voxel_xyz_phys_peak = voxel_xyz_peak * rxyz
    voxel_timeseries_peak_nrm = normalize(
        voxel_timeseries[np.ix_(peak_idx, timepoints)]
    )

    # compute voxel peak similarity: combination of high proximity and high correlation
    tic = time.time()
    n_peaks = len(peak_idx)
    voxel_similarity_peak = np.zeros((n_peaks, n_peaks), dtype=bool)
    for i in range(n_peaks):
        dist_i = (((voxel_xyz_phys_peak[i] - voxel_xyz_phys_peak) ** 2).sum(1)) ** 0.5
        neib_i = dist_i < p.diam_cell
        corr_i = np.dot(voxel_timeseries_peak_nrm[i], voxel_timeseries_peak_nrm.T)
        voxel_similarity_peak[i] = neib_i & (corr_i > np.median(corr_i[neib_i]))

    voxel_similarity_peak = voxel_similarity_peak | voxel_similarity_peak.T
    print("voxel similarity: %.1f minutes.\n" % ((time.time() - tic) / 60))

    return (voxel_xyz, voxel_timeseries, peak_idx, voxel_similarity_peak)
