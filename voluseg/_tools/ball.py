import numpy as np


def ball(
    radi: float,
    affine_mat: np.ndarray,
) -> tuple:
    """
    Morphological cell balls and midpoints.

    Parameters
    ----------
    radi : float
        Radius of ball.
    affine_mat : np.ndarray
        Affine matrix.

    Returns
    -------
    tuple
        Tuple containing: Ball and midpoints.
    """
    rx, ry, rz, _ = np.diag(affine_mat)
    ball = np.ones(
        (
            np.maximum(1, np.round(radi / rx).astype(int) * 2 + 1),
            np.maximum(1, np.round(radi / ry).astype(int) * 2 + 1),
            np.maximum(1, np.round(radi / rz).astype(int) * 2 + 1),
        ),
        dtype=int,
    )
    ball_xyzm = (np.array(ball.shape) - 1) / 2
    for xi in range(ball.shape[0]):
        for yi in range(ball.shape[1]):
            for zi in range(ball.shape[2]):
                xyzi_diff = ([xi, yi, zi] - ball_xyzm) * [rx, ry, rz]
                ball[xi, yi, zi] = np.sqrt(np.sum(np.square(xyzi_diff))) <= radi
    return (ball, ball_xyzm)
