"""API layer for browser based beam monitoring dashboard."""

class BeamDashboardAPI:
    def __init__(self):
        self.latest_state = {}

    def update_state(self, state):
        self.latest_state = state

    def get_state(self):
        return self.latest_state
