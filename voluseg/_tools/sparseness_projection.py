def sparseness_projection(Si, s, at_least_as_sparse=False):
    """Hoyer sparseness projection"""

    import numpy as np

    assert Si.ndim == 1
    S = np.copy(Si)  # copy input signal

    if s <= 0:
        return np.maximum(S, 0)  # enforce nonnegativity

    d = S.size

    L2 = np.sqrt(np.sum(np.square(S)))  # fixed l2-norm
    L1 = L2 * (np.sqrt(d) * (1 - s) + s)  # desired l1-norm

    # quit if at_least_sparse=True and original exceeds target sparseness
    if at_least_as_sparse:
        if L1 >= np.sum(np.abs(S)):
            return S

    # initialize components with negative values
    Z = np.zeros(S.shape, dtype=bool)

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
        A = np.sum(P * P)
        B = 2 * np.sum(P * M)
        C = np.sum(M * M) - L2**2

        Alph = (-B + np.real(np.sqrt(B**2 - 4 * A * C))) / (2 * A)

        # Project within the sum-constraint hyperplane to match L2
        S = M + Alph * P

        # Check for negative values in solution
        negatives = np.any(S < 0)

    return S
