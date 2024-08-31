import os
from typing import Tuple

# disable numpy multithreading
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
import numpy as np

from scipy import stats
from scipy import linalg
from skimage import measure
from voluseg._tools.sparseness_projection import sparseness_projection


def nnmf_sparse(
    V0: np.ndarray,
    XYZ0: np.ndarray,
    W0: np.ndarray,
    B0: np.ndarray,
    S0: np.ndarray,
    tolfun: float = 1e-4,
    miniter: int = 10,
    maxiter: int = 100,
    timeseries_mean=1.0,
    timepoints: np.ndarray = None,
    verbosity: bool = True,
) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Cell detection via nonnegative matrix factorization with sparseness projection.

    Parameters
    ----------
    V0 : np.ndarray
        Voxel timeseries (voxel_timeseries_valid).
    XYZ0 : np.ndarray
        Voxel coordinates (voxel_xyz_valid).
    W0 : np.ndarray
        Initial cell weights (cell_weight_init_valid).
    B0 : np.ndarray
        Cell neighborhood (cell_neighborhood_valid).
    S0 : np.ndarray
        Cell sparseness (cell_sparseness).
    tolfun : float, optional
        Tolerance for convergence, by default 1e-4.
    miniter : int, optional
        Minimum number of iterations, by default 10.
    maxiter : int, optional
        Maximum number of iterations, by default 100.
    timeseries_mean : float, optional
        Mean timeseries value, by default 1.0.
    timepoints : np.ndarray, optional
        Timepoints to use, by default None.
    verbosity : bool, optional
        Print progress, by default True.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, float]
        Tuple containing: Spatial footprint, temporal footprint, convergence error.
    """
    # CAUTION: variable is modified in-place to save memory
    V0 *= timeseries_mean / V0.mean(1)[:, None]  # normalize voxel timeseries

    if timepoints is not None:
        V = V0[:, timepoints].astype(float)  # copy input signal
    else:
        V = V0.astype(float)  # copy input signal

    XYZ = XYZ0.astype(int)
    W = W0.astype(float)
    B = B0.astype(bool)
    S = S0.copy()

    # get dimensions
    n, t = V.shape
    n_, c = W.shape
    assert n_ == n

    H = np.zeros((c, t))  # zero timeseries array
    dnorm_prev = np.full(2, np.inf)  # last two d-norms
    for ii in range(maxiter):
        # save current states
        H_ = H.copy()

        # Alternate least squares with regularization
        H = np.maximum(linalg.lstsq(W, V)[0], 0)
        H *= timeseries_mean / H.mean(1)[:, None]  # normalize component timeseries

        W = np.maximum(linalg.lstsq(V.T, H.T)[0], 0)
        W[np.logical_not(B)] = 0  # restrict component boundaries
        for ci in range(c):
            W_ci = W[B[:, ci], ci]
            if np.any(W_ci) and (S[ci] > 0):
                # get relative dimensions of component
                XYZ_ci = XYZ[B[:, ci]] - XYZ[B[:, ci]].min(0)

                # enforce component sparseness and percentile threshold
                W_ci = sparseness_projection(W_ci, S[ci], at_least_as_sparse=True)

                # retain largest connected component (mode)
                L_ci = np.zeros(np.ptp(XYZ_ci, 0) + 1, dtype=bool)
                L_ci[tuple(zip(*XYZ_ci))] = W_ci > 0
                L_ci = measure.label(L_ci, connectivity=3)
                lci_mode = stats.mode(L_ci[L_ci > 0]).mode
                # backwards compatibility with old scipy behavior
                if not np.isscalar(lci_mode):
                    lci_mode = lci_mode[0]
                W_ci[L_ci[tuple(zip(*XYZ_ci))] != lci_mode] = 0

                W[B[:, ci], ci] = W_ci

        # Get norm of difference and check for convergence
        dnorm = np.sqrt(np.mean(np.square(V - W.dot(H)))) / timeseries_mean
        diffh = np.sqrt(np.mean(np.square(H - H_))) / timeseries_mean
        if ((dnorm_prev.max(0) - dnorm) < tolfun) & (diffh < tolfun):
            if ii >= miniter:
                break
        dnorm_prev[1] = dnorm_prev[0]
        dnorm_prev[0] = dnorm

        if verbosity:
            print((ii, dnorm, diffh))

    # Perform final regression on full input timeseries
    H = np.maximum(linalg.lstsq(W, V0)[0], 0)
    H *= timeseries_mean / H.mean(1)[:, None]  # normalize component timeseries

    return (W, H, dnorm)
