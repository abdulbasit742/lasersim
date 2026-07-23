"""
Adaptive stability manager foundation.
Used for safe autonomous beam tuning limits.
"""

class StabilityManager:
    def __init__(self, max_error=0.05):
        self.max_error = max_error

    def within_limits(self, error):
        return abs(error) <= self.max_error

    def check(self, measurement):
        return {"stable": self.within_limits(measurement)}
