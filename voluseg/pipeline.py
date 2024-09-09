import os

# disable numpy multithreading
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
import numpy as np
from typing import Union
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from loguru import logger
import sys
from pathlib import Path
from datetime import datetime

from voluseg._tools.parameters_models import ParametersModel
from voluseg import (
    step0_process_parameters,
    step1_process_volumes,
    step2_align_volumes,
    step3_mask_volumes,
    step4_detect_cells,
    step5_clean_cells,
)


def create_logger(logs_dir: Union[str, None] = None) -> logger:
    # Remove any default logger configuration
    logger.remove()

    # Add logging to stdout
    logger.add(
        sys.stdout,
        format="{time} {level} {file} {message}",
    )

    # Add logging to a file (with rotation and retention options)
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if logs_dir is None:
        logs_path = Path.home() / "voluseg/logs" / f"voluseg_{current_time}.log"
    else:
        logs_path = Path(logs_dir) / f"voluseg_{current_time}.log"
    logger.add(
        logs_path,
        rotation="10 MB",
        # retention="7 days",
        format="{time} {level} {file} {message}",
    )

    # Redirect print statements by overriding sys.stdout
    class PrintToLoguru:
        def write(self, message):
            message = message.strip()  # Strip extra newlines
            if message:  # Avoid logging empty lines
                logger.info(message)

        def flush(self):
            pass  # No need for flushing when using Loguru

    original_stdout = sys.stdout  # Keep reference to the original stdout
    sys.stdout = PrintToLoguru()
    return logger


class Pipeline:
    def __init__(
        self,
        parameters: ParametersModel,
        spark_context: Union[SparkContext, None] = None,
        logs_dir: Union[str, None] = None,
    ) -> None:
        """
        Initialize the pipeline.

        Parameters
        ----------
        parameters : ParametersModel
            Parameters model.
        spark_context : Union[SparkContext, None], optional
            Spark context, if None, a new one will be created (default is None).
        logs_dir : Union[str, None], optional
            Directory to save the logs, if None, the logs will be saved in the
            default HOME directory (default is None).

        Returns
        -------
        None
        """
        # Create a logger
        self.logger = create_logger(logs_dir=logs_dir)

        # Process and save the parameters
        self.parameters = step0_process_parameters(initial_parameters=parameters)

        # Create a Spark session
        self.spark_session = SparkSession.builder.getOrCreate()
        self.spark_context = self.spark_session.sparkContext

    def run(self) -> None:
        """
        Run the pipeline.
        """
        self.logger.info("Starting Step 1 - Process volumes.")
        step1_process_volumes(
            parameters=self.parameters,
            spark_context=self.spark_context,
        )

        self.logger.info("Starting Step 2 - Align volumes.")
        step2_align_volumes(
            parameters=self.parameters,
            spark_context=self.spark_context,
        )

        self.logger.info("Starting Step 3 - Mask volumes.")
        step3_mask_volumes(
            parameters=self.parameters,
            spark_context=self.spark_context,
        )

        self.logger.info("Starting Step 4 - Detect cells.")
        step4_detect_cells(
            parameters=self.parameters,
            spark_context=self.spark_context,
        )

        self.logger.info("Starting Step 5 - Clean cells.")
        step5_clean_cells(
            parameters=self.parameters,
            spark_context=self.spark_context,
        )
