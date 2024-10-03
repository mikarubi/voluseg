from loguru import logger
from datetime import datetime
from pathlib import Path
import sys
from typing import Union
from contextlib import contextmanager


class DynamicFileLogger:
    def __init__(self):
        # Remove any default logger configuration
        logger.remove()

        # Add logging to stdout
        logger.add(
            sys.stdout,
            format="{time} {level} {message}",
        )
        self.file_handler_id = None

        # Redirect print statements by overriding sys.stdout
        self._redirect_prints()

    def _redirect_prints(self):
        class PrintToLoguru:
            def write(self, message):
                message = message.strip()
                if message:
                    logger.info(message)
            def flush(self):
                pass  # No need for flushing when using Loguru
        sys.stdout = PrintToLoguru()

    def change_output_file(self, file_path):
        # Remove the existing file handler if it exists
        if self.file_handler_id is not None:
            logger.remove(self.file_handler_id)

        # Add a new file handler and keep track of its ID
        self.file_handler_id = logger.add(
            file_path,
            format="{time} {level} {message}",
            rotation="10 MB",
            # retention="7 days",
        )

    # @contextmanager
    # def use_output_file(self, file_path):
    #     # Add new handler
    #     file_handler_id = logger.add(
    #         file_path,
    #         format="{time} {level} {message}",
    #     )
    #     try:
    #         yield
    #     finally:
    #         logger.remove(file_handler_id)

    def info(self, message):
        logger.info(message)

    def debug(self, message):
        logger.debug(message)

    def warning(self, message):
        logger.warning(message)

    def error(self, message):
        logger.error(message)

    def critical(self, message):
        logger.critical(message)


def create_logger(
    logs_file_path: Union[str, None] = None,
) -> logger:
    logger = DynamicFileLogger()
    return logger
