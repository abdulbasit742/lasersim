"""
Real-time control scheduler foundation for LaserSim.
Provides deterministic control-cycle management hooks.
"""

class ControlScheduler:
    def __init__(self, cycle_ms=10):
        self.cycle_ms = cycle_ms
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def status(self):
        return {"running": self.running, "cycle_ms": self.cycle_ms}
