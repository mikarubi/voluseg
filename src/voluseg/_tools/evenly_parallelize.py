import dask.bag as db


def evenly_parallelize(input_list: list) -> db.Bag:
    """
    Return a Dask bag from the input list.

    Parameters
    ----------
    input_list : list
        List of input elements.

    Returns
    -------
    db.Bag
        Dask bag.
    """
    return db.from_sequence(input_list)
