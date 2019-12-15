def evenly_parallelize(input_list):
    '''return evenly partitioned spark resilient distributed dataset (RDD)'''
    
    import numpy as np
    from pyspark.sql.session import SparkSession
    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    
    n_input= len(input_list)
    n_parts = sc.parallelize(input_list).getNumPartitions()
    partitions = np.floor(np.linspace(0, n_parts, n_input, endpoint=False)).astype(int)
    
    return sc.parallelize(zip(partitions, input_list)).partitionBy(n_parts)
