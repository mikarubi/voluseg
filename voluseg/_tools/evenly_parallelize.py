import numpy as np
from typing import Union
from pyspark.sql.session import SparkSession
from pyspark.rdd import RDD
from pyspark import SparkContext


def evenly_parallelize(
    input_list: list,
    spark_context: Union[SparkContext, None] = None,
) -> RDD:
    """
    Return evenly partitioned spark resilient distributed dataset (RDD).

    Parameters
    ----------
    input_list : list
        List of input elements.
    spark_context : Union[SparkContext, None], optional
        Spark context, if None, a new one will be created (default is None).

    Returns
    -------
    RDD
        Spark resilient distributed dataset (RDD).
    """
    if spark_context is None:
        spark = SparkSession.builder.getOrCreate()
        spark_context = spark.sparkContext

    n_input = len(input_list)
    n_parts = spark_context.parallelize(input_list).getNumPartitions()
    partitions = np.floor(np.linspace(0, n_parts, n_input, endpoint=False)).astype(int)

    return spark_context.parallelize(zip(partitions, input_list)).partitionBy(n_parts)
