"""
This module contains utility functions for setting up logging.
"""

import logging
from sys import stdout


def setup_logger(level=logging.INFO):
    """
    :param level: DEBUG|INFO
    :return: None
    """
    root = logging.getLogger()
    logging.captureWarnings(True)
    root.setLevel(level)
    stream_handler = logging.StreamHandler(stdout)
    formatter = logging.Formatter("[%(levelname)7s] %(asctime)s | %(name)-7s | %(message)s")
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)
