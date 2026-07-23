"""Central logging foundation for LaserSim services."""

import logging


def get_logger(name: str = "lasersim"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
