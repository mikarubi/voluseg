import dask.bag as db
from ..dask_config import get_dask_client


def evenly_parallelize(input_list: list) -> db.Bag:
    """
    Return a Dask bag from the input list using configured Dask client.

    Parameters
    ----------
    input_list : list
        List of input elements.

    Returns
    -------
    db.Bag
        Dask bag.
    """
    client = get_dask_client()
    return db.from_sequence(input_list)
