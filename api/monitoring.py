"""Monitoring metrics foundation for LaserSim API."""

import time

START_TIME = time.time()


def service_metrics():
    return {
        "uptime_seconds": time.time() - START_TIME,
        "service": "lasersim-beam-api"
    }
