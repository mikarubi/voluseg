from pyspark.sql.session import SparkSession
import psutil


def get_spark_context(
    auto: bool = True,
    driver_memory: int = 4,
    executor_memory: int = 8,
    executor_cores: int = 1,
    num_executors: int = 4,
):
    """
    Get or create a Spark context.

    Parameters:
    -----------
    auto : bool
        Automatically configure Spark resources.
    driver_memory : int
        Set driver memory.
    executor_memory : int
        Set executor memory.
    executor_cores : int
        Number of cores per executor.
    num_executors : int
        Total number of executors.

    Returns:
    --------
    SparkContext
        Spark context.
    """
    total_cores = psutil.cpu_count(logical=True)
    if auto:
        # Use (n_cores - 2), minimum 1 core
        num_executors = max((total_cores - 2) / executor_cores, 1)

        # Get available system memory in GB
        available_memory_gb = psutil.virtual_memory().available // (1024**3)

        # Set memory for driver and executors
        # 20% of available memory for driver
        driver_memory = max(int(available_memory_gb * 0.2), 2)
        # 70% split among executors
        executor_memory = max(int(available_memory_gb * 0.7 / num_executors), 1)

    print(f"Configuring Spark with:")
    print(f"- Total cores: {total_cores}")
    print(f"- Executor cores: {executor_cores}")
    print(f"- Available memory: {available_memory_gb} GB")
    print(f"- Driver memory: {driver_memory} GB")
    print(f"- Executor memory: {executor_memory} GB per executor")

    # Build Spark session with these configurations
    spark = (
        SparkSession.builder.appName("Voluseg")
        .config("spark.driver.memory", f"{driver_memory}g")
        .config("spark.executor.memory", f"{executor_memory}g")
        .config("spark.executor.cores", executor_cores)
        .config("spark.num.executors", num_executors)
        .config("spark.dynamicAllocation.enabled", "true")
        .config("spark.dynamicAllocation.minExecutors", "1")
        .config("spark.dynamicAllocation.maxExecutors", num_executors)
        .getOrCreate()
    )

    return spark.sparkContext
