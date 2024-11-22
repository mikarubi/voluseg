import numpy as np
from pyspark.rdd import RDD

from voluseg.tools.spark import get_spark_context


def evenly_parallelize(input_list: list, parameters: dict) -> RDD:
    """
    Return evenly partitioned spark resilient distributed dataset (RDD).

    Parameters
    ----------
    input_list : list
        List of input elements.
    parameters : dict
        Parameters dictionary.

    Returns
    -------
    RDD
        Spark resilient distributed dataset (RDD).
    """
    sc = get_spark_context(**parameters.get("spark_config", {}))

    n_input = len(input_list)
    n_parts = sc.parallelize(input_list).getNumPartitions()
    partitions = np.floor(np.linspace(0, n_parts, n_input, endpoint=False)).astype(int)

    return sc.parallelize(zip(partitions, input_list)).partitionBy(n_parts)
