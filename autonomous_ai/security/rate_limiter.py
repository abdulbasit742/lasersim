"""Rate limiting foundation for LaserSim API protection."""

import time


class RateLimiter:
    def __init__(self, limit=100, window_seconds=60):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = {}

    def allow(self, client_id):
        now = time.time()
        history = self.requests.get(client_id, [])
        history = [t for t in history if now - t < self.window_seconds]
        if len(history) >= self.limit:
            return False
        history.append(now)
        self.requests[client_id] = history
        return True
