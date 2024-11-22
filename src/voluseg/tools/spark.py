from pyspark.sql.session import SparkSession
import psutil


def get_spark_context():
    """
    Get or create a Spark context.

    Returns
    -------
    SparkContext
        Spark context.
    """
     # Use (n_cores - 2), minimum 1 core
    total_cores = psutil.cpu_count(logical=True)
    n_cores_executors = max(total_cores - 2, 1)

    # Get available system memory in GB
    available_memory_gb = psutil.virtual_memory().available // (1024 ** 3)

    # Set memory for driver and executors
    # 25% of available memory for driver
    driver_memory = max(int(available_memory_gb * 0.2), 2)
    # 50% split among executors
    executor_memory = max(int(available_memory_gb * 0.7 / n_cores_executors), 1)

    print(f"Configuring Spark with:")
    print(f"- Total cores: {total_cores}")
    print(f"- Executor cores: {n_cores_executors}")
    print(f"- Available memory: {available_memory_gb} GB")
    print(f"- Driver memory: {driver_memory} GB")
    print(f"- Executor memory: {executor_memory} GB per executor")

    # Build Spark session with these configurations
    spark = (
        SparkSession.builder
        .appName("Voluseg")
        .config("spark.driver.memory", f"{driver_memory}g")
        .config("spark.executor.memory", f"{executor_memory}g")
        .config("spark.executor.cores", n_cores_executors)
        .config("spark.num.executors", n_cores_executors)
        .config("spark.dynamicAllocation.enabled", "true")
        .config("spark.dynamicAllocation.minExecutors", "1")
        .config("spark.dynamicAllocation.maxExecutors", n_cores_executors)
        .getOrCreate()
    )

    return spark.sparkContext
