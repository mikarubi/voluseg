def sparseness(W, dim=0):
    '''vector sparseness along specified dimension'''

    import numpy as np
    n = W.shape[dim]
    l2 = np.sqrt(np.sum(np.square(W), dim))           # l2-norm
    l1 =         np.sum(np.abs(   W), dim)            # l1-norm
    return (np.sqrt(n) - l1 / l2) / (np.sqrt(n) - 1)  # sparseness
