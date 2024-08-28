import numpy as np


def sparseness(
    W: np.ndarray,
    dim: int = 0,
):
    """
    Vector sparseness along specified dimension.

    Parameters
    ----------
    W : np.ndarray
        Input array.
    dim : int, optional
        Dimension along which to compute sparseness, by default 0.

    Returns
    -------
    np.ndarray
        Sparseness of input array along specified dimension.
    """
    n = W.shape[dim]
    l2 = np.sqrt(np.sum(np.square(W), dim))  # l2-norm
    l1 = np.sum(np.abs(W), dim)  # l1-norm
    return (np.sqrt(n) - l1 / l2) / (np.sqrt(n) - 1)  # sparseness
