import numpy as np
from pyspark.sql.session import SparkSession
from pyspark.rdd import RDD


def evenly_parallelize(input_list: list) -> RDD:
    """
    Return evenly partitioned spark resilient distributed dataset (RDD).

    Parameters
    ----------
    input_list : list
        List of input elements.

    Returns
    -------
    RDD
        Spark resilient distributed dataset (RDD).
    """
    spark = SparkSession.builder \
        .config("spark.executorEnv.COVERAGE_PROCESS_START", "/mnt/shared_storage/Github/voluseg/.coveragerc") \
        .getOrCreate()
    sc = spark.sparkContext

    n_input = len(input_list)
    n_parts = sc.parallelize(input_list).getNumPartitions()
    partitions = np.floor(np.linspace(0, n_parts, n_input, endpoint=False)).astype(int)

    return sc.parallelize(zip(partitions, input_list)).partitionBy(n_parts)
