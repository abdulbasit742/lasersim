"""API rate limiting foundation."""

class RateLimiter:
    def __init__(self, limit=100):
        self.limit = limit
        self.requests = {}

    def allow(self, client_id):
        count = self.requests.get(client_id, 0)
        if count >= self.limit:
            return False
        self.requests[client_id] = count + 1
        return True
