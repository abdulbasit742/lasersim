"""Structured logging foundation for LaserSim API."""

import logging

logger = logging.getLogger("lasersim_api")
logger.setLevel(logging.INFO)


def log_prediction(request_id: str, result: dict):
    logger.info("prediction request=%s result=%s", request_id, result)
