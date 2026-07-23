"""API security helpers for LaserSim prediction service."""

import time

_REQUEST_LOG = {}


def check_rate_limit(client_id: str, limit: int = 60, window: int = 60) -> bool:
    now = time.time()
    requests = [t for t in _REQUEST_LOG.get(client_id, []) if now - t < window]
    if len(requests) >= limit:
        return False
    requests.append(now)
    _REQUEST_LOG[client_id] = requests
    return True


def validate_api_key(api_key: str, expected: str = "") -> bool:
    if not expected:
        return True
    return api_key == expected
