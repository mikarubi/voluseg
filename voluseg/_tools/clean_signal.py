import os
from typing import Tuple

# disable numpy multithreading
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
import numpy as np

import pandas as pd
from scipy import signal
from scipy.stats.mstats import winsorize
from voluseg._tools.constants import dtype
from types import SimpleNamespace


def clean_signal(
    parameters: dict,
    timeseries: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Detrend, filter, and estimate dynamic baseline for input timeseries.

    Parameters
    ----------
    parameters : dict
        Parameters dictionary.
    timeseries : np.ndarray
        Input timeseries.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        TODO - add description
    """
    p = SimpleNamespace(**parameters)

    # p.t_baseline:  timescale constant for baseline estimation (in seconds)
    # p.f_hipass:   highpass cutoff frequency
    # p.f_volume:    frequency of imaging a single stack (in Hz)

    if p.detrending == "standard":
        robustify = lambda timeseries: timeseries
    elif p.detrending == "robust":
        robustify = lambda timeseries: winsorize(timeseries, [0.1, 0.1])

    # compute dynamic baseline
    def compute_baseline(timeseries):
        timeseries_df = pd.DataFrame(timeseries)
        baseline_df = timeseries_df.rolling(ltau, min_periods=1, center=True).quantile(
            0.1
        )
        baseline_df = baseline_df.rolling(ltau, min_periods=1, center=True).mean()
        baseline = np.ravel(baseline_df)
        baseline += np.percentile(timeseries - baseline, 1)
        assert np.allclose(np.percentile(timeseries - baseline, 1), 0)
        return baseline

    # convert to double precision
    timeseries = timeseries.astype("float64")

    # timeseries mean
    timeseries_mean = timeseries.mean()

    # length of interval of dynamic baseline time-scales
    ltau = (np.round(p.t_baseline * p.f_volume / 2) * 2 + 1).astype(int)

    # detrend with a low-order polynomial
    xtime = np.arange(timeseries.shape[0])
    coefpoly = np.polyfit(xtime, robustify(timeseries), 2)
    timeseries -= np.polyval(coefpoly, xtime)
    timeseries = np.concatenate((timeseries[::-1], timeseries, timeseries[::-1]))

    # highpass filter
    nyquist = p.f_volume / 2
    if (p.f_hipass > 1e-10) and (p.f_hipass < nyquist - 1e-10):
        f_rng = np.array([p.f_hipass, nyquist - 1e-10])
        krnl = signal.firwin(p.lt, f_rng / nyquist, pass_zero=False)
        timeseries = signal.filtfilt(krnl, 1, timeseries, padtype=None)

    # restore mean
    timeseries = timeseries - timeseries.mean() + timeseries_mean
    baseline = compute_baseline(robustify(timeseries))

    # slice and convert to single precision
    timeseries = timeseries[p.lt : 2 * p.lt].astype(dtype)
    baseline = baseline[p.lt : 2 * p.lt].astype(dtype)

    return (timeseries, baseline)
